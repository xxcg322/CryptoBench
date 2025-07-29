import logging
from typing import Optional, Dict, Any
from pathlib import Path
from .types import TaskStep, StepType, ExecutionResult
from .llm_client import LLMClient


class CodeGenerator:
    """Code generator - responsible for generating Solidity and Python code"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
        self._available_libraries = self._detect_available_libraries()
    
    def generate_code(self, step: TaskStep, context: Dict[str, Any] = None, 
                     previous_error: Optional[str] = None) -> str:
        """Generate code"""
        if context is None:
            context = {}
            
        if step.step_type == StepType.SOLIDITY:
            return self._generate_solidity_code(step, context, previous_error)
        else:
            return self._generate_python_code(step, context, previous_error)
    
    def _generate_solidity_code(self, step: TaskStep, context: Dict[str, Any], 
                               previous_error: Optional[str] = None) -> str:
        """Generate Solidity code"""
        self.logger.info(f"Generating Solidity code for step {step.id}")
        
        # Dynamically generate system prompt containing available library information
        available_libs_info = self._format_available_libraries()
        
        system_prompt = f"""You are a Solidity smart contract developer. Generate clean, secure, and well-documented smart contract code.

Requirements:
- Use Solidity version ^0.8.20
- Add comprehensive comments
- Follow best practices for security
- Make the contract deployable and functional
- For storage contracts, use appropriate data types (string for text, uint256 for numbers)
- Use simple function names like set(), get(), store(), retrieve()

{available_libs_info}

IMPORTANT OpenZeppelin v5 Breaking Changes:
- Ownable constructor requires initialOwner parameter: constructor(address initialOwner)
- Use msg.sender as the initial owner: constructor() Ownable(msg.sender) {{}}
- If using Ownable, ALWAYS include proper constructor with initial owner

Only return the Solidity code wrapped in ```solidity code blocks. Do not include deployment instructions or explanations unless specifically asked."""

        user_prompt = f"""Generate a Solidity smart contract for the following requirement:

{step.description}

Context information:
{self._format_context(context)}"""

        if previous_error:
            user_prompt += f"""

IMPORTANT: The previous code generation failed with the following error:
{previous_error}

Please fix the issues and generate corrected code."""

        response = self.llm_client.chat_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], context={
            "step_id": step.id,
            "step_type": "solidity",
            "step_description": step.description
        })
        
        # Extract Solidity code
        code_blocks = self.llm_client.extract_code_blocks(response, "solidity")
        
        if not code_blocks:
            # If no solidity code block found, try to find generic code blocks
            all_blocks = self.llm_client.extract_code_blocks(response)
            for lang, code in all_blocks:
                if "pragma solidity" in code:
                    return code
            
            raise ValueError("No valid Solidity code found in LLM response")
        
        return code_blocks[0]
    
    def _detect_available_libraries(self) -> Dict[str, str]:
        """Detect available Solidity libraries"""
        available_libs = {}
        node_modules_path = Path("node_modules")
        
        if not node_modules_path.exists():
            return available_libs
        
        # Detect OpenZeppelin Contracts
        oz_path = node_modules_path / "@openzeppelin" / "contracts"
        if oz_path.exists():
            available_libs["@openzeppelin/contracts"] = "Standard security contracts (Ownable, AccessControl, ERC20, ERC721, etc.)"
        
        # Detect OpenZeppelin Upgradeable
        oz_upgradeable_path = node_modules_path / "@openzeppelin" / "contracts-upgradeable"
        if oz_upgradeable_path.exists():
            available_libs["@openzeppelin/contracts-upgradeable"] = "Upgradeable versions of OpenZeppelin contracts"
        
        # Detect Solady
        solady_path = node_modules_path / "solady" / "src"
        if solady_path.exists():
            available_libs["solady"] = "Gas-optimized contracts (Ownable, ERC20, SafeTransferLib, etc.)"
        
        # Detect Solmate
        solmate_path = node_modules_path / "solmate" / "src"
        if solmate_path.exists():
            available_libs["solmate"] = "Gas-optimized contracts by Rari Capital (Owned, ERC20, ReentrancyGuard, etc.)"
        
        # Detect Uniswap V2
        uniswap_v2_core_path = node_modules_path / "@uniswap" / "v2-core" / "contracts"
        if uniswap_v2_core_path.exists():
            available_libs["@uniswap/v2-core"] = "Uniswap V2 core contracts (IUniswapV2Factory, IUniswapV2Pair, etc.)"
        
        uniswap_v2_periphery_path = node_modules_path / "@uniswap" / "v2-periphery" / "contracts"
        if uniswap_v2_periphery_path.exists():
            available_libs["@uniswap/v2-periphery"] = "Uniswap V2 periphery contracts (IUniswapV2Router, etc.)"
        
        # Detect Chainlink
        chainlink_path = node_modules_path / "@chainlink" / "contracts"
        if chainlink_path.exists():
            available_libs["@chainlink/contracts"] = "Chainlink oracle contracts (AggregatorV3Interface, VRFConsumerBase, etc.)"
        
        return available_libs
    
    def _format_available_libraries(self) -> str:
        """Format available library information as string"""
        if not self._available_libraries:
            return "No external libraries detected. Use pure Solidity code only."
        
        library_info = ["Available Solidity Libraries:"]
        for lib_name, description in self._available_libraries.items():
            library_info.append(f"- {lib_name}: {description}")
        
        return "\n".join(library_info)
    
    def _detect_python_libraries(self) -> Dict[str, str]:
        """Detect available Python libraries (for blockchain development)"""
        python_libs = {
            "web3": "Ethereum blockchain interaction library",
            "eth_account": "Ethereum account management and signing", 
            "eth_utils": "Ethereum utility functions",
            "requests": "HTTP library for API calls",
            "json": "JSON encoding/decoding (built-in)",
            "os": "Operating system interface (built-in)",
            "logging": "Logging facility (built-in)",
            "time": "Time-related functions (built-in)",
            "hashlib": "Cryptographic hash functions (built-in)",
            "dotenv": "Environment variable loading from .env files"
        }
        
        # Additional library detection can be implemented here
        # Check if specific packages are installed
        
        return python_libs
    
    def _format_python_libraries(self) -> str:
        """Format Python library information as string"""
        python_libs = self._detect_python_libraries()
        
        library_info = ["Available Python Libraries for Blockchain Development:"]
        for lib_name, description in python_libs.items():
            library_info.append(f"- {lib_name}: {description}")
        
        return "\n".join(library_info)
    
    def _generate_python_code(self, step: TaskStep, context: Dict[str, Any],
                             previous_error: Optional[str] = None) -> str:
        """Generate Python code"""
        self.logger.info(f"Generating Python code for step {step.id}")
        
        # Dynamically generate system prompt containing available library information
        python_libs_info = self._format_python_libraries()
        
        system_prompt = f"""You are a Python blockchain developer. Generate complete, functional Python scripts for blockchain interactions.

Requirements:
- Use web3.py for Ethereum interactions
- Include all necessary imports
- Read configuration from environment variables (RPC_URL, PRIVATE_KEY, SENDER_ADDRESS)
- Include proper error handling and logging
- Use snake_case naming convention (compatible with latest web3.py)
- Include clear output/logging to show operation results
- Make the script executable as a standalone program

{python_libs_info}

IMPORTANT: Use modern web3.py API (v6+) with snake_case naming:
- Use `signed_txn.raw_transaction` (NOT rawTransaction)
- Use `web3.is_connected()` (NOT isConnected())
- Use `Web3.to_wei()` for unit conversion
- Use `web3.eth.wait_for_transaction_receipt()` for waiting

CRITICAL: NEVER use geth_poa_middleware - it has been REMOVED in newer web3.py versions:
- Do NOT import: from web3.middleware import geth_poa_middleware
- Do NOT use: web3.middleware_onion.inject(geth_poa_middleware, layer=0)
- For PoA networks, simply omit middleware or use other methods if needed

TRANSACTION BEST PRACTICES:
- NONCE MANAGEMENT: Get nonce ONCE per step, reuse for retries within same step
- RETRY STRATEGY: For timeout errors, check if transaction is still pending before retry
- GAS OPTIMIZATION: Use web3.eth.gas_price * 1.1 for faster confirmation
- TIMEOUT HANDLING: Use timeout of at least 120 seconds for transaction confirmation
- TRANSACTION REPLACEMENT: Increase gas price by 10% when replacing pending transactions
- ERROR HANDLING: Distinguish between nonce conflicts and actual transaction failures

CRITICAL TIMEOUT AND ERROR HANDLING:
- Use timeout=120 (or longer) for web3.eth.wait_for_transaction_receipt()
- If timeout occurs, call sys.exit(1) to indicate failure, DO NOT exit with code 0
- Log the transaction hash even on timeout for debugging purposes
- Check mempool status before creating replacement transaction
- Log transaction hashes for all attempts for debugging

CRITICAL NONCE RULES:
- DO NOT get new nonce on retry if previous transaction might still be pending
- Check mempool status before creating replacement transaction
- Log transaction hashes for all attempts for debugging

Only return the Python code wrapped in ```python code blocks. The code should be complete and ready to execute."""

        user_prompt = f"""Generate a Python script for the following blockchain task:

{step.description}

Context information:
{self._format_context(context)}"""

        if previous_error:
            user_prompt += f"""

IMPORTANT: The previous code execution failed with the following error:
{previous_error}

Please analyze the error and generate corrected code that addresses these issues."""

        response = self.llm_client.chat_completion([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ], context={
            "step_id": step.id,
            "step_type": "python",
            "step_description": step.description
        })
        
        # Extract Python code
        code_blocks = self.llm_client.extract_code_blocks(response, "python")
        
        if not code_blocks:
            raise ValueError("No valid Python code found in LLM response")
        
        return code_blocks[0]
    
    def _format_context(self, context: Dict[str, Any]) -> str:
        """Format context information"""
        if not context:
            return "No additional context provided."
        
        formatted = []
        
        # Process deployed contracts
        if "deployed_contracts" in context and context["deployed_contracts"]:
            formatted.append("=== DEPLOYED CONTRACTS ===")
            for contract_name, contract_info in context["deployed_contracts"].items():
                formatted.append(f"Contract: {contract_name}")
                formatted.append(f"  Address: {contract_info.get('address', 'N/A')}")
                formatted.append(f"  Deployed in step: {contract_info.get('step_id', 'N/A')}")
                if 'abi' in contract_info:
                    # Extract function names as quick reference
                    functions = [item['name'] for item in contract_info['abi'] if item['type'] == 'function']
                    if functions:
                        formatted.append(f"  Available functions: {', '.join(functions)}")
                    formatted.append(f"  Full ABI: {contract_info['abi']}")
                formatted.append("")
        
        # Process previous step outputs
        if "previous_outputs" in context and context["previous_outputs"]:
            formatted.append("=== PREVIOUS STEP OUTPUTS ===")
            for step_id, output in context["previous_outputs"].items():
                formatted.append(f"Step {step_id} output: {str(output)[:200]}...")
            formatted.append("")
        
        # Process other context information
        for key, value in context.items():
            if key not in ["deployed_contracts", "previous_outputs"]:
                formatted.append(f"{key}: {value}")
        
        return "\n".join(formatted) if formatted else "No additional context provided."
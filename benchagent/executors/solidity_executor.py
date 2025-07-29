import os
import json
import logging
import solcx
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from web3 import Web3
from web3.contract import Contract

from core.config import BlockchainConfig


class SolidityExecutor:
    """Solidity executor - responsible for compiling and deploying smart contracts"""
    
    def __init__(self, blockchain_config: BlockchainConfig, solc_version: str = "0.8.20", task_manager=None):
        self.config = blockchain_config
        self.solc_version = solc_version
        self.task_manager = task_manager
        self.logger = logging.getLogger(__name__)
        
        # Initialize Web3
        self.web3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
        if not self.web3.is_connected():
            raise ConnectionError("Failed to connect to blockchain network")
        
        # Set default account
        self.account = self.web3.eth.account.from_key(self.config.private_key)
        self.web3.eth.default_account = self.account.address
        
        # Install and setup Solidity compiler
        self._setup_solc()
        
        # Working directory - use default directory if no task_manager
        if task_manager is None:
            self.work_dir = Path("contracts")
            self.work_dir.mkdir(exist_ok=True)
    
    def _setup_solc(self):
        """Setup Solidity compiler"""
        try:
            # Install specified version of compiler
            if self.solc_version not in solcx.get_installed_solc_versions():
                self.logger.info(f"Installing Solidity compiler version {self.solc_version}")
                solcx.install_solc(self.solc_version)
            
            # Set compiler version to use
            solcx.set_solc_version(self.solc_version)
            self.logger.info(f"Using Solidity compiler version: {solcx.get_solc_version()}")
            
        except Exception as e:
            self.logger.error(f"Failed to setup Solidity compiler: {e}")
            raise
    
    def execute(self, code: str, step_id: str, task_id: str = None, attempt: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """Execute Solidity code (compile and deploy)"""
        try:
            self.logger.info(f"Executing Solidity code for step {step_id} (attempt {attempt})")
            
            # Determine save path
            if self.task_manager and task_id:
                contract_dir = self.task_manager.get_task_contracts_dir(task_id)
            else:
                contract_dir = self.work_dir
            
            # Save code to file - include attempt number
            contract_file = contract_dir / f"{step_id}_attempt_{attempt}.sol"
            
            # Maintain latest version reference
            latest_file = contract_dir / f"{step_id}.sol"
            with open(contract_file, 'w') as f:
                f.write(code)
            
            # Maintain latest version reference
            with open(latest_file, 'w') as f:
                f.write(code)
            
            # Compile contracts
            compilation_result = self._compile_contract(code)
            if not compilation_result:
                return False, {"error": "Contract compilation failed"}
            
            # Deploy contracts
            deployment_results = {}
            all_deployments_successful = True
            for contract_name, contract_info in compilation_result.items():
                result = self._deploy_contract(contract_name, contract_info)
                deployment_results[contract_name] = result
                if not result.get("success", False):
                    all_deployments_successful = False
            
            result_data = {
                "type": "solidity_execution",
                "compiled_contracts": list(compilation_result.keys()),
                "deployed_contracts": deployment_results,
                "source_file": str(contract_file)
            }
            
            return all_deployments_successful, result_data
            
        except Exception as e:
            self.logger.error(f"Solidity execution failed: {e}")
            return False, {"error": str(e), "error_type": type(e).__name__}
    
    def _compile_contract(self, code: str) -> Optional[Dict[str, Any]]:
        """Compile smart contract"""
        try:
            self.logger.info("Compiling Solidity contract...")
            
            # Set import paths (for dependencies like OpenZeppelin)
            import_remappings = []
            
            # Check if node_modules exists
            node_modules_path = Path("node_modules")
            if node_modules_path.exists():
                # OpenZeppelin
                oz_path = node_modules_path / "@openzeppelin" / "contracts"
                if oz_path.exists():
                    import_remappings.append(f"@openzeppelin/contracts/={oz_path.absolute()}/")
                    self.logger.info(f"Added OpenZeppelin remapping: {oz_path.absolute()}")
                
                # Solady
                solady_path = node_modules_path / "solady" / "src"
                if solady_path.exists():
                    import_remappings.append(f"solady/={solady_path.absolute()}/")
                    self.logger.info(f"Added Solady remapping: {solady_path.absolute()}")
                
                # Solmate
                solmate_path = node_modules_path / "solmate" / "src"
                if solmate_path.exists():
                    import_remappings.append(f"solmate/={solmate_path.absolute()}/")
                    self.logger.info(f"Added Solmate remapping: {solmate_path.absolute()}")
                
                # OpenZeppelin Upgradeable
                oz_upgradeable_path = node_modules_path / "@openzeppelin" / "contracts-upgradeable"
                if oz_upgradeable_path.exists():
                    import_remappings.append(f"@openzeppelin/contracts-upgradeable/={oz_upgradeable_path.absolute()}/")
                    self.logger.info(f"Added OpenZeppelin Upgradeable remapping: {oz_upgradeable_path.absolute()}")
                
                # Uniswap V2
                uniswap_v2_core_path = node_modules_path / "@uniswap" / "v2-core" / "contracts"
                if uniswap_v2_core_path.exists():
                    import_remappings.append(f"@uniswap/v2-core/={uniswap_v2_core_path.absolute()}/")
                    self.logger.info(f"Added Uniswap V2 Core remapping: {uniswap_v2_core_path.absolute()}")
                
                uniswap_v2_periphery_path = node_modules_path / "@uniswap" / "v2-periphery" / "contracts"
                if uniswap_v2_periphery_path.exists():
                    import_remappings.append(f"@uniswap/v2-periphery/={uniswap_v2_periphery_path.absolute()}/")
                    self.logger.info(f"Added Uniswap V2 Periphery remapping: {uniswap_v2_periphery_path.absolute()}")
                
                # Chainlink (if installed in the future)
                chainlink_path = node_modules_path / "@chainlink" / "contracts"
                if chainlink_path.exists():
                    import_remappings.append(f"@chainlink/contracts/={chainlink_path.absolute()}/")
                    self.logger.info(f"Added Chainlink remapping: {chainlink_path.absolute()}")
            
            # Compilation parameters
            compile_kwargs = {
                "output_values": ["abi", "bin", "bin-runtime"],
                "solc_version": self.solc_version,
            }
            
            if import_remappings:
                compile_kwargs["import_remappings"] = import_remappings
                compile_kwargs["allow_paths"] = str(node_modules_path.absolute())
            
            # Execute compilation
            compiled = solcx.compile_source(code, **compile_kwargs)
            
            # Process compilation results
            contracts = {}
            for contract_id, contract_data in compiled.items():
                # contract_id format is '<stdin>:ContractName'
                contract_name = contract_id.split(':')[-1]
                contracts[contract_name] = {
                    "abi": contract_data["abi"],
                    "bytecode": contract_data["bin"],
                    "runtime_bytecode": contract_data.get("bin-runtime", "")
                }
            
            self.logger.info(f"Successfully compiled {len(contracts)} contracts: {list(contracts.keys())}")
            return contracts
            
        except Exception as e:
            self.logger.error(f"Contract compilation failed: {e}")
            if hasattr(e, 'stdout') and e.stdout:
                self.logger.error(f"Compiler stdout: {e.stdout}")
            if hasattr(e, 'stderr') and e.stderr:
                self.logger.error(f"Compiler stderr: {e.stderr}")
            return None
    
    def _deploy_contract(self, contract_name: str, contract_info: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy single contract"""
        try:
            self.logger.info(f"Deploying contract: {contract_name}")
            
            # Create contract object
            contract = self.web3.eth.contract(
                abi=contract_info["abi"],
                bytecode=contract_info["bytecode"]
            )
            
            # Estimate gas
            try:
                gas_estimate = contract.constructor().estimate_gas()
                gas_limit = int(gas_estimate * 1.2)  # Add 20% margin
            except Exception:
                gas_limit = self.config.gas_limit
                self.logger.warning(f"Failed to estimate gas, using default: {gas_limit}")
            
            # Get current gas price
            gas_price = int(self.web3.eth.gas_price * self.config.gas_price_multiplier)
            
            # Get nonce
            nonce = self.web3.eth.get_transaction_count(self.account.address)
            
            # Build deployment transaction
            deploy_txn = contract.constructor().build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
                'chainId': self.config.chain_id
            })
            
            # Sign transaction
            signed_txn = self.account.sign_transaction(deploy_txn)
            
            # Send transaction
            tx_hash = self.web3.eth.send_raw_transaction(signed_txn.raw_transaction)
            self.logger.info(f"Deployment transaction sent: {tx_hash.hex()}")
            
            # Wait for transaction confirmation
            tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)
            
            if tx_receipt.status == 1:
                contract_address = tx_receipt.contractAddress
                self.logger.info(f"Contract {contract_name} deployed successfully at: {contract_address}")
                
                return {
                    "success": True,
                    "address": contract_address,
                    "transaction_hash": tx_hash.hex(),
                    "gas_used": tx_receipt.gasUsed,
                    "abi": contract_info["abi"]
                }
            else:
                self.logger.error(f"Contract deployment failed: transaction reverted")
                return {
                    "success": False,
                    "error": "Transaction reverted",
                    "transaction_hash": tx_hash.hex()
                }
                
        except Exception as e:
            self.logger.error(f"Contract deployment failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__
            }
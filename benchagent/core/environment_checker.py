"""
Environment checker - responsible for validating runtime environment integrity
"""
import os
import sys
import importlib
import logging
from pathlib import Path
from typing import Dict, Any, List, Tuple
from web3 import Web3
import solcx


class EnvironmentChecker:
    """Environment checker, ensures all necessary components are correctly configured"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Define required environment variables
        self.required_env_vars = [
            "RPC_URL",
            "PRIVATE_KEY", 
            "SENDER_ADDRESS",
            "OPENAI_API_KEY"
        ]
        
        # Define required Python packages (pip package name -> import name)
        self.required_packages = {
            'web3': 'web3',
            'python-dotenv': 'dotenv',
            'openai': 'openai',
            'py-solc-x': 'solcx'
        }
        
        # Define recommended Solidity version
        self.solc_version = '0.8.20'
    
    def run_full_check(self) -> Tuple[bool, List[str]]:
        """Run comprehensive environment check"""
        self.logger.info("Starting comprehensive environment check...")
        
        issues = []
        
        # 1. Check Python packages
        package_issues = self._check_python_packages()
        if package_issues:
            issues.extend(package_issues)
        
        # 2. Check environment variables
        env_issues = self._check_environment_variables()
        if env_issues:
            issues.extend(env_issues)
        
        # 3. Check network connection
        network_issues = self._check_network_connection()
        if network_issues:
            issues.extend(network_issues)
        
        # 4. Check Solidity compiler
        solc_issues = self._check_solidity_compiler()
        if solc_issues:
            issues.extend(solc_issues)
        
        # 5. Check Solidity libraries
        library_issues = self._check_solidity_libraries()
        if library_issues:
            issues.extend(library_issues)
        
        # 6. Create required directories
        dir_issues = self._create_required_directories()
        if dir_issues:
            issues.extend(dir_issues)
        
        success = len(issues) == 0
        
        if success:
            self.logger.info("✅ Environment check completed successfully")
        else:
            self.logger.error(f"❌ Environment check failed with {len(issues)} issues")
            for issue in issues:
                self.logger.error(f"  - {issue}")
        
        return success, issues
    
    def _check_python_packages(self) -> List[str]:
        """Check required Python packages"""
        self.logger.info("Checking required Python packages...")
        issues = []
        
        for pip_name, import_name in self.required_packages.items():
            try:
                importlib.import_module(import_name)
                self.logger.debug(f"✓ Package {pip_name} is installed")
            except ImportError:
                issues.append(f"Missing required package: {pip_name}. Install with: pip install {pip_name}")
        
        return issues
    
    def _check_environment_variables(self) -> List[str]:
        """Check required environment variables"""
        self.logger.info("Checking environment variables...")
        issues = []
        
        for var in self.required_env_vars:
            value = os.getenv(var)
            if not value:
                issues.append(f"Missing environment variable: {var}")
            else:
                # Validate format (don't log actual values)
                if var == "SENDER_ADDRESS":
                    if not value.startswith("0x") or len(value) != 42:
                        issues.append(f"Invalid format for {var}: should be 0x followed by 40 hex characters")
                elif var == "PRIVATE_KEY":
                    if not value.startswith("0x") or len(value) != 66:
                        issues.append(f"Invalid format for {var}: should be 0x followed by 64 hex characters")
                elif var == "RPC_URL":
                    if not (value.startswith("http://") or value.startswith("https://")):
                        issues.append(f"Invalid format for {var}: should start with http:// or https://")
                
                self.logger.debug(f"✓ Environment variable {var} is set")
        
        return issues
    
    def _check_network_connection(self) -> List[str]:
        """Check blockchain network connection"""
        self.logger.info("Testing blockchain network connection...")
        issues = []
        
        rpc_url = os.getenv("RPC_URL")
        if not rpc_url:
            return ["Cannot test network connection: RPC_URL not set"]
        
        try:
            web3 = Web3(Web3.HTTPProvider(rpc_url))
            if not web3.is_connected():
                issues.append(f"Failed to connect to blockchain network at {rpc_url}")
            else:
                try:
                    block_number = web3.eth.block_number
                    chain_id = web3.eth.chain_id
                    self.logger.info(f"✓ Connected to blockchain (Chain ID: {chain_id}, Latest block: {block_number})")
                except Exception as e:
                    issues.append(f"Connected to network but failed to retrieve block info: {e}")
        
        except Exception as e:
            issues.append(f"Network connection error: {e}")
        
        return issues
    
    def _check_solidity_compiler(self) -> List[str]:
        """Check Solidity compiler"""
        self.logger.info("Checking Solidity compiler...")
        issues = []
        
        try:
            # Try to install specified version of solc
            if not solcx.get_installed_solc_versions():
                self.logger.info(f"Installing Solidity compiler version {self.solc_version}...")
                solcx.install_solc(self.solc_version)
            
            # Set version
            solcx.set_solc_version(self.solc_version)
            current_version = solcx.get_solc_version()
            
            if str(current_version) != self.solc_version:
                issues.append(f"Solidity compiler version mismatch: expected {self.solc_version}, got {current_version}")
            else:
                self.logger.info(f"✓ Solidity compiler {current_version} is ready")
            
            # Validate compiler functionality
            test_contract = """
            pragma solidity ^0.8.20;
            contract Test {
                uint256 public value = 42;
            }
            """
            
            try:
                solcx.compile_source(test_contract)
                self.logger.debug("✓ Solidity compiler test compilation successful")
            except Exception as e:
                issues.append(f"Solidity compiler test failed: {e}")
        
        except Exception as e:
            issues.append(f"Failed to setup Solidity compiler: {e}")
        
        return issues
    
    def _check_solidity_libraries(self) -> List[str]:
        """Check Solidity library installation"""
        self.logger.info("Checking Solidity libraries...")
        issues = []
        warnings = []
        
        # Check critical libraries
        critical_libraries = {
            "@openzeppelin/contracts": "node_modules/@openzeppelin/contracts"
        }
        
        # Check optional libraries
        optional_libraries = {
            "solady": "node_modules/solady",
            "solmate": "node_modules/solmate",
            "@uniswap/v2-core": "node_modules/@uniswap/v2-core",
            "@uniswap/v2-periphery": "node_modules/@uniswap/v2-periphery"
        }
        
        # Check critical libraries
        for lib_name, lib_path in critical_libraries.items():
            if not Path(lib_path).exists():
                issues.append(f"Missing critical library: {lib_name}. Install with: npm install {lib_name}")
            else:
                self.logger.info(f"✓ Critical library {lib_name} is installed")
        
        # Check optional libraries
        for lib_name, lib_path in optional_libraries.items():
            if not Path(lib_path).exists():
                warnings.append(f"Optional library {lib_name} not found")
            else:
                self.logger.debug(f"✓ Optional library {lib_name} is installed")
        
        # Log warnings but don't treat as failures
        for warning in warnings:
            self.logger.warning(warning)
        
        return issues
    
    def _create_required_directories(self) -> List[str]:
        """Create required directories"""
        self.logger.info("Creating required directories...")
        issues = []
        
        required_dirs = [
            "outputs",
            "node_modules"  # For npm packages
        ]
        
        for dir_name in required_dirs:
            try:
                Path(dir_name).mkdir(exist_ok=True)
                self.logger.debug(f"✓ Directory {dir_name} is ready")
            except Exception as e:
                issues.append(f"Failed to create directory {dir_name}: {e}")
        
        return issues
    
    def get_environment_summary(self) -> Dict[str, Any]:
        """Get environment information summary"""
        summary = {
            "python_version": sys.version,
            "platform": sys.platform,
            "working_directory": os.getcwd(),
            "environment_variables": {
                var: "SET" if os.getenv(var) else "NOT SET" 
                for var in self.required_env_vars
            },
            "installed_packages": {},
            "solidity_info": {}
        }
        
        # Check package versions
        for pip_name, import_name in self.required_packages.items():
            try:
                module = importlib.import_module(import_name)
                version = getattr(module, '__version__', 'Unknown')
                summary["installed_packages"][pip_name] = version
            except ImportError:
                summary["installed_packages"][pip_name] = "NOT INSTALLED"
        
        # Solidity information
        try:
            summary["solidity_info"]["installed_versions"] = [str(v) for v in solcx.get_installed_solc_versions()]
            summary["solidity_info"]["current_version"] = str(solcx.get_solc_version()) if solcx.get_installed_solc_versions() else None
        except Exception:
            summary["solidity_info"]["error"] = "Failed to get Solidity info"
        
        return summary
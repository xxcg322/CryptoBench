import os
import sys
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Tuple


class PythonExecutor:
    """Python executor - responsible for executing Python scripts"""
    
    def __init__(self, timeout: int = 300, task_manager=None):
        self.timeout = timeout
        self.task_manager = task_manager
        self.logger = logging.getLogger(__name__)
        
        # Working directory - use default directory if no task_manager
        if task_manager is None:
            self.work_dir = Path("scripts")
            self.work_dir.mkdir(exist_ok=True)
    
    def execute(self, code: str, step_id: str, task_id: str = None, env_vars: Dict[str, str] = None, attempt: int = 1) -> Tuple[bool, Dict[str, Any]]:
        """Execute Python code"""
        try:
            self.logger.info(f"Executing Python code for step {step_id} (attempt {attempt})")
            
            # Determine save path
            if self.task_manager and task_id:
                script_dir = self.task_manager.get_task_scripts_dir(task_id)
            else:
                script_dir = self.work_dir
            
            # Save code to file - include attempt number
            script_file = script_dir / f"{step_id}_attempt_{attempt}.py"
            
            # Maintain latest version reference for backward compatibility
            latest_file = script_dir / f"{step_id}.py"
            with open(script_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Update latest version file
            with open(latest_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Prepare environment variables
            execution_env = os.environ.copy()
            if env_vars:
                execution_env.update(env_vars)
            
            # Execute script
            self.logger.info(f"Running script: {script_file}")
            process = subprocess.Popen(
                [sys.executable, str(script_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=execution_env,
                cwd=os.getcwd(),
                text=True
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.timeout)
                exit_code = process.returncode
                
                # Record output
                if stdout:
                    self.logger.info(f"Script output:\n{stdout}")
                if stderr:
                    self.logger.warning(f"Script stderr:\n{stderr}")
                
                # Extract transaction hashes from stdout and stderr for debugging  
                tx_hashes_stderr = self._extract_transaction_hashes(stderr)
                tx_hashes_stdout = self._extract_transaction_hashes(stdout)
                all_tx_hashes = list(set(tx_hashes_stderr + tx_hashes_stdout))
                if all_tx_hashes:
                    self.logger.info(f"Transaction hashes found in this attempt: {all_tx_hashes}")
                
                # Improved success determination logic: not only check exit_code, but also check ERROR in stderr
                success = exit_code == 0 and not self._has_python_error(stderr)
                
                result = {
                    "type": "python_execution",
                    "exit_code": exit_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "script_file": str(script_file),
                    "success": success
                }
                
                # Record discovered transaction hashes
                if all_tx_hashes:
                    result["transaction_hashes"] = all_tx_hashes
                
                if not success:
                    result["error"] = f"Script exited with code {exit_code}"
                    if stderr:
                        result["error"] += f"\nStderr: {stderr}"
                
                return success, result
                    
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                self.logger.error(f"Script execution timed out after {self.timeout} seconds")
                return False, {
                    "type": "python_execution",
                    "exit_code": -1,
                    "stdout": stdout,
                    "stderr": stderr + f"\nScript execution timed out after {self.timeout} seconds",
                    "error": f"Script execution timed out after {self.timeout} seconds",
                    "success": False
                }
                
        except Exception as e:
            self.logger.error(f"Python execution failed: {e}")
            return False, {
                "type": "python_execution", 
                "error": str(e),
                "error_type": type(e).__name__,
                "success": False
            }
    
    def _extract_transaction_hashes(self, text: str) -> list:
        """Extract transaction hashes from output"""
        import re
        if not text:
            return []
        
        # Match common transaction hash formats
        patterns = [
            r'(?:TX|Tx|tx|Transaction|transaction).*?hash[:\s]+([0-9a-fA-F]{64})',
            r'([0-9a-fA-F]{64})',  # 64-bit hexadecimal string
            r'0x([0-9a-fA-F]{64})'  # Hash with 0x prefix
        ]
        
        hashes = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                hash_value = match if match.startswith('0x') else f"0x{match}"
                if len(hash_value) == 66:  # 0x + 64 chars
                    hashes.append(hash_value)
        
        return list(set(hashes))  # Remove duplicates
    
    def _has_python_error(self, stderr: str) -> bool:
        """Check if stderr contains Python errors"""
        if not stderr:
            return False
        
        # Check common Python error patterns
        error_patterns = [
            "ERROR:",
            "Exception:",
            "Traceback (most recent call last):",
            "AttributeError:",
            "ValueError:",
            "TypeError:",
            "ImportError:",
            "ConnectionError:",
            "TimeoutError:"
        ]
        
        for pattern in error_patterns:
            if pattern in stderr:
                return True
        return False
    
    def validate_code(self, code: str) -> Tuple[bool, str]:
        """Validate Python code syntax"""
        try:
            compile(code, '<string>', 'exec')
            return True, "Code syntax is valid"
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        except Exception as e:
            return False, f"Validation error: {e}"
import logging
from typing import Dict, Any, Optional
from .types import TaskStep, StepType, ExecutionResult, ExecutionStatus
from .code_generator import CodeGenerator
from executors.solidity_executor import SolidityExecutor
from executors.python_executor import PythonExecutor


class StepExecutor:
    """Step executor - responsible for executing individual task steps, including error feedback and retry mechanism"""
    
    def __init__(self, code_generator: CodeGenerator, 
                 solidity_executor: SolidityExecutor,
                 python_executor: PythonExecutor,
                 max_retries: int = 3,
                 task_manager=None):
        self.code_generator = code_generator
        self.solidity_executor = solidity_executor
        self.python_executor = python_executor
        self.max_retries = max_retries
        self.task_manager = task_manager
        self.logger = logging.getLogger(__name__)
    
    def execute_step(self, step: TaskStep, task_id: str, context: Dict[str, Any] = None) -> ExecutionResult:
        """Execute single step (including retry logic)"""
        if context is None:
            context = {}
            
        self.logger.info(f"Executing step {step.id}: {step.description}")
        
        previous_error = None
        
        for attempt in range(1, self.max_retries + 1):
            self.logger.info(f"Step {step.id} - Attempt {attempt}/{self.max_retries}")
            
            try:
                # Generate code
                code = self.code_generator.generate_code(step, context, previous_error)
                self.logger.debug(f"Generated code for step {step.id}:\n{code[:500]}...")
                
                # Execute code
                success, execution_result = self._execute_code(step, code, task_id, attempt)
                
                # Save detailed log of each attempt
                if self.task_manager:
                    self.task_manager.save_step_attempt_log(
                        task_id, step.id, attempt, success, code, execution_result
                    )
                
                if success:
                    self.logger.info(f"Step {step.id} completed successfully on attempt {attempt}")
                    return ExecutionResult(
                        success=True,
                        step_id=step.id,
                        code=code,
                        output=execution_result.get("output", ""),
                        attempt=attempt,
                        error_details=execution_result
                    )
                else:
                    # Execution failed, prepare error message for next retry
                    error_msg = self._format_error_message(execution_result)
                    
                    # Handle timeout errors with pending transactions
                    if "timeout" in error_msg.lower() or "not in the chain" in error_msg.lower():
                        self.logger.warning(f"Step {step.id} attempt {attempt}: Transaction timeout detected")
                        # For timeout errors, add special instructions
                        previous_error = f"{error_msg}\n\nTransaction timeout detected. Verify transaction status before retry to avoid nonce conflicts."
                    elif "Transaction pending" in execution_result.get("stdout", ""):
                        # If stdout contains "Transaction pending", also treat as timeout situation
                        self.logger.warning(f"Step {step.id} attempt {attempt}: Transaction pending detected in output")
                        previous_error = f"{error_msg}\n\nPending transaction detected. Verify status before retry."
                    else:
                        previous_error = error_msg
                    
                    self.logger.warning(f"Step {step.id} failed on attempt {attempt}: {error_msg}")
                    
                    if attempt == self.max_retries:
                        # Last attempt failed
                        return ExecutionResult(
                            success=False,
                            step_id=step.id,
                            code=code,
                            error=error_msg,
                            error_details=execution_result,
                            attempt=attempt
                        )
                    
            except Exception as e:
                error_msg = f"Code generation/execution error: {str(e)}"
                previous_error = error_msg
                self.logger.error(f"Step {step.id} attempt {attempt} failed with exception: {e}")
                
                if attempt == self.max_retries:
                    return ExecutionResult(
                        success=False,
                        step_id=step.id,
                        error=error_msg,
                        error_details={"error_type": type(e).__name__},
                        attempt=attempt
                    )
        
        # Fallback for unexpected execution path
        return ExecutionResult(
            success=False,
            step_id=step.id,
            error="Unexpected execution path",
            attempt=self.max_retries
        )
    
    def _execute_code(self, step: TaskStep, code: str, task_id: str, attempt: int) -> tuple[bool, Dict[str, Any]]:
        """Execute code (choose executor based on step type)"""
        if step.step_type == StepType.SOLIDITY:
            return self.solidity_executor.execute(code, step.id, task_id, attempt)
        else:
            # For Python code, pass in necessary environment variables
            env_vars = {
                "RPC_URL": self.solidity_executor.config.rpc_url,
                "PRIVATE_KEY": self.solidity_executor.config.private_key,
                "SENDER_ADDRESS": self.solidity_executor.config.sender_address,
                "CHAIN_ID": str(self.solidity_executor.config.chain_id)
            }
            return self.python_executor.execute(code, step.id, task_id, env_vars, attempt)
    
    def _format_error_message(self, execution_result: Dict[str, Any]) -> str:
        """Format error message for feedback to LLM"""
        error_parts = []
        
        # Basic error information
        if "error" in execution_result:
            error_parts.append(f"Error: {execution_result['error']}")
        
        # Execution type-specific error information
        if execution_result.get("type") == "solidity_execution":
            error_parts.append("Solidity compilation/deployment failed.")
            
        elif execution_result.get("type") == "python_execution":
            error_parts.append("Python script execution failed.")
            
            if "exit_code" in execution_result:
                error_parts.append(f"Exit code: {execution_result['exit_code']}")
            
            if "stderr" in execution_result and execution_result["stderr"]:
                error_parts.append(f"Stderr output: {execution_result['stderr']}")
            
            if "stdout" in execution_result and execution_result["stdout"]:
                # Only include last few lines of stdout to avoid being too long
                stdout_lines = execution_result["stdout"].strip().split('\n')
                if len(stdout_lines) > 10:
                    stdout_preview = "\\n".join(stdout_lines[-10:])
                    error_parts.append(f"Last 10 lines of stdout: {stdout_preview}")
                else:
                    error_parts.append(f"Stdout output: {execution_result['stdout']}")
        
        # Technical error type
        if "error_type" in execution_result:
            error_parts.append(f"Error type: {execution_result['error_type']}")
        
        return "\\n".join(error_parts)
import logging
from typing import List, Dict, Any
from pathlib import Path

from .config import BenchmarkConfig
from .types import BenchmarkTask, TaskPlan, ExecutionResult
from .task_manager import TaskManager
from .task_planner import TaskPlanner
from .step_executor import StepExecutor
from .code_generator import CodeGenerator
from .llm_client import LLMClient
from .environment_checker import EnvironmentChecker
from executors.solidity_executor import SolidityExecutor
from executors.python_executor import PythonExecutor


class BenchmarkAgent:
    """Main benchmark testing agent - coordinates all components to complete task execution"""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Validate configuration
        config.validate()
        
        # Initialize components
        self.task_manager = TaskManager(config.output_dir)
        self.llm_client = LLMClient(config.llm, self.task_manager)
        self.task_planner = TaskPlanner(self.llm_client)
        self.code_generator = CodeGenerator(self.llm_client)
        
        # Initialize executors
        self.solidity_executor = SolidityExecutor(config.blockchain, config.solc_version, self.task_manager)
        self.python_executor = PythonExecutor(config.timeout, self.task_manager)
        
        # Initialize step executor
        self.step_executor = StepExecutor(
            self.code_generator,
            self.solidity_executor,
            self.python_executor,
            config.max_retries,
            self.task_manager
        )
        
        self.logger.info("BenchmarkAgent initialized successfully")
    
    def run_benchmark(self, tasks_file: str, skip_env_check: bool = False) -> Dict[str, Any]:
        """Run benchmark test"""
        self.logger.info(f"Starting benchmark with tasks from: {tasks_file}")
        
        # Run environment check
        if not skip_env_check:
            self.logger.info("Running environment check...")
            env_checker = EnvironmentChecker()
            env_success, env_issues = env_checker.run_full_check()
            
            if not env_success:
                self.logger.error("Environment check failed. Issues found:")
                for issue in env_issues:
                    self.logger.error(f"  - {issue}")
                return {
                    "success": False,
                    "error": "Environment check failed",
                    "environment_issues": env_issues,
                    "total_tasks": 0,
                    "successful_tasks": 0,
                    "failed_tasks": 0
                }
            
            self.logger.info("Environment check passed successfully")
        else:
            self.logger.warning("Environment check skipped")
        
        # Load tasks
        tasks = self.task_manager.load_tasks(tasks_file)
        
        # Execute all tasks
        results = []
        for task in tasks:
            result = self.execute_task(task)
            results.append(result)
            
            # Save task results
            self.task_manager.save_task_result(task.id, result)
        
        # Generate summary
        summary = self.task_manager.generate_summary(results)
        
        self.logger.info(f"Benchmark completed. Success rate: {summary['success_rate']:.2f}%")
        return summary
    
    def execute_task(self, task: BenchmarkTask) -> Dict[str, Any]:
        """Execute single task"""
        self.logger.info(f"Executing task {task.id}: {task.description}")
        
        try:
            # 1. Task planning
            plan = self.task_planner.plan_task(task)
            self.logger.info(f"Task {task.id} planned with {len(plan.steps)} steps")
            
            # 2. Execute steps
            step_results = []
            context = {
                "deployed_contracts": {},
                "previous_outputs": {}
            }
            
            for step in plan.steps:
                # Check dependencies
                if not self._check_dependencies(step, step_results):
                    step_result = ExecutionResult(
                        success=False,
                        step_id=step.id,
                        error="Dependencies not satisfied"
                    )
                else:
                    # Execute step
                    step_result = self.step_executor.execute_step(step, task.id, context)
                    
                    # Update context
                    if step_result.success:
                        self._update_context(context, step, step_result)
                
                step_results.append(step_result)
                
                # Save step execution log
                self.task_manager.save_execution_log(
                    task.id, 
                    step.id, 
                    {
                        "step_description": step.description,
                        "step_type": step.step_type.value,
                        "success": step_result.success,
                        "code": step_result.code,
                        "output": step_result.output,
                        "error": step_result.error,
                        "attempt": step_result.attempt
                    }
                )
                
                # If step fails, log and continue (or decide whether to stop based on strategy)
                if not step_result.success:
                    self.logger.error(f"Step {step.id} failed: {step_result.error}")
                    # Continue executing remaining steps despite failure
                    # Execution continues with failed step marked in results
            
            # 3. Evaluate overall task success
            successful_steps = sum(1 for r in step_results if r.success)
            total_steps = len(step_results)
            task_success = successful_steps == total_steps
            
            result = {
                "task_id": task.id,
                "success": task_success,
                "total_steps": total_steps,
                "successful_steps": successful_steps,
                "failed_steps": total_steps - successful_steps,
                "steps": [
                    {
                        "step_id": r.step_id,
                        "success": r.success,
                        "error": r.error,
                        "attempts": r.attempt
                    } for r in step_results
                ],
                "context": context
            }
            
            if not task_success:
                failed_steps = [r for r in step_results if not r.success]
                result["error"] = f"Task failed: {len(failed_steps)} steps failed"
                result["failed_step_details"] = [
                    {"step_id": r.step_id, "error": r.error} for r in failed_steps
                ]
            
            return result
            
        except Exception as e:
            self.logger.error(f"Task {task.id} execution failed: {e}")
            return {
                "task_id": task.id,
                "success": False,
                "error": str(e),
                "error_type": type(e).__name__,
                "total_steps": 0,
                "successful_steps": 0,
                "failed_steps": 0
            }
    
    def _check_dependencies(self, step, completed_steps: List[ExecutionResult]) -> bool:
        """Check if step dependencies are satisfied"""
        if not step.dependencies:
            return True
        
        completed_step_ids = {r.step_id for r in completed_steps if r.success}
        return all(dep in completed_step_ids for dep in step.dependencies)
    
    def _update_context(self, context: Dict[str, Any], step, step_result: ExecutionResult):
        """Update execution context"""
        # Update outputs of completed steps
        context["previous_outputs"][step.id] = step_result.output
        
        # If it's a Solidity step, update deployed contract information
        if step.step_type.value == "solidity" and step_result.success and step_result.error_details:
            deployed_contracts = step_result.error_details.get("deployed_contracts", {})
            for contract_name, contract_info in deployed_contracts.items():
                if contract_info.get("success"):
                    context["deployed_contracts"][contract_name] = {
                        "address": contract_info["address"],
                        "abi": contract_info["abi"],
                        "step_id": step.id
                    }
                    self.logger.info(f"Added contract {contract_name} to context with address {contract_info['address']}")
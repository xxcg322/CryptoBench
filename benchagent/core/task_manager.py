import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from .types import BenchmarkTask


class TaskManager:
    """Task manager - responsible for task loading, storage and state management"""
    
    def __init__(self, output_dir: str = "outputs"):
        # Create timestamped run directory
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.run_id = f"run_{timestamp}"
        
        self.output_dir = Path(output_dir) / self.run_id
        self.current_run_dir = self.output_dir  # Add alias for LLM interaction history
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
        # Create subdirectories
        self.results_dir = self.output_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        
        self.logs_dir = self.output_dir / "logs"  
        self.logs_dir.mkdir(exist_ok=True)
        
        # Create code directories
        self.scripts_dir = self.output_dir / "scripts"
        self.scripts_dir.mkdir(exist_ok=True)
        
        self.contracts_dir = self.output_dir / "contracts"
        self.contracts_dir.mkdir(exist_ok=True)
        
    def load_tasks(self, tasks_file: str) -> List[BenchmarkTask]:
        """Load tasks from file"""
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            tasks = []
            for task_data in data.get("tasks", []):
                task = BenchmarkTask(
                    id=task_data["id"],
                    description=task_data["description"],
                    type=task_data.get("type", "general"),
                    max_retries=task_data.get("max_retries", 3),
                    timeout=task_data.get("timeout", 300),
                    metadata=task_data.get("metadata", {})
                )
                tasks.append(task)
            
            self.logger.info(f"Loaded {len(tasks)} tasks from {tasks_file}")
            return tasks
            
        except Exception as e:
            self.logger.error(f"Failed to load tasks from {tasks_file}: {e}")
            raise
    
    def save_task_result(self, task_id: str, result: Dict[str, Any]) -> None:
        """Save task execution results"""
        try:
            result_file = self.results_dir / f"task_{task_id}_result.json"
            
            # Add timestamp
            result["timestamp"] = datetime.now().isoformat()
            result["task_id"] = task_id
            
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Task {task_id} result saved to {result_file}")
            
        except Exception as e:
            self.logger.error(f"Failed to save result for task {task_id}: {e}")
            raise
    
    def save_execution_log(self, task_id: str, step_id: str, log_data: Dict[str, Any]) -> None:
        """Save execution logs"""
        try:
            log_file = self.logs_dir / f"task_{task_id}_step_{step_id}.json"
            
            # Add timestamp
            log_data["timestamp"] = datetime.now().isoformat()
            log_data["task_id"] = task_id
            log_data["step_id"] = step_id
            
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"Failed to save execution log for task {task_id}, step {step_id}: {e}")
    
    def save_step_attempt_log(self, task_id: str, step_id: str, attempt: int, 
                             success: bool, code: str, result: Dict[str, Any]) -> None:
        """Save detailed log of each attempt"""
        try:
            attempt_log_file = self.logs_dir / f"task_{task_id}_step_{step_id}_attempt_{attempt}.json"
            
            attempt_data = {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "step_id": step_id,
                "attempt": attempt,
                "success": success,
                "code": code,
                "result": result
            }
            
            with open(attempt_log_file, 'w', encoding='utf-8') as f:
                json.dump(attempt_data, f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"Saved attempt {attempt} log for task {task_id}, step {step_id}")
                
        except Exception as e:
            self.logger.error(f"Failed to save attempt log for task {task_id}, step {step_id}, attempt {attempt}: {e}")
    
    def get_task_output_dir(self, task_id: str) -> Path:
        """Get task-specific output directory"""
        task_dir = self.output_dir / f"task_{task_id}"
        task_dir.mkdir(exist_ok=True)
        return task_dir
    
    def get_task_scripts_dir(self, task_id: str) -> Path:
        """Get task-specific scripts directory"""
        task_scripts_dir = self.scripts_dir / f"task_{task_id}"
        task_scripts_dir.mkdir(exist_ok=True)
        return task_scripts_dir
    
    def get_task_contracts_dir(self, task_id: str) -> Path:
        """Get task-specific contracts directory"""
        task_contracts_dir = self.contracts_dir / f"task_{task_id}"
        task_contracts_dir.mkdir(exist_ok=True)
        return task_contracts_dir
    
    def generate_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate execution summary"""
        total_tasks = len(results)
        successful_tasks = sum(1 for r in results if r.get("success", False))
        failed_tasks = total_tasks - successful_tasks
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "failed_tasks": failed_tasks,
            "success_rate": (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            "task_details": {
                r["task_id"]: {
                    "success": r["success"],
                    "error": r.get("error") if not r["success"] else None,
                    "steps_completed": r.get("steps_completed", 0),
                    "total_steps": r.get("total_steps", 0)
                } for r in results
            }
        }
        
        # Save summary
        summary_file = self.output_dir / "summary.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Summary saved to {summary_file}")
        return summary
    
    def save_llm_interaction(self, interaction_record: Dict[str, Any]):
        """Save LLM interaction history"""
        if not self.current_run_dir:
            return
            
        try:
            # Create llm_interactions directory
            interactions_dir = self.current_run_dir / "llm_interactions"
            interactions_dir.mkdir(exist_ok=True)
            
            # Generate filename (use timestamp to ensure uniqueness)
            timestamp = interaction_record["timestamp"].replace(":", "-").replace(".", "-")
            interaction_file = interactions_dir / f"interaction_{timestamp}.json"
            
            # Save interaction record
            with open(interaction_file, 'w', encoding='utf-8') as f:
                json.dump(interaction_record, f, indent=2, ensure_ascii=False)
                
            self.logger.debug(f"LLM interaction saved to {interaction_file}")
            
        except Exception as e:
            self.logger.warning(f"Failed to save LLM interaction: {e}")
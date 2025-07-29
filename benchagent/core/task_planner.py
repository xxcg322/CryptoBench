import logging
from typing import List
from .types import BenchmarkTask, TaskPlan, TaskStep, StepType
from .llm_client import LLMClient


class TaskPlanner:
    """Task planner - responsible for decomposing complex tasks into executable steps"""
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
        self.logger = logging.getLogger(__name__)
    
    def plan_task(self, task: BenchmarkTask) -> TaskPlan:
        """Decompose task into execution steps"""
        self.logger.info(f"Planning task {task.id}: {task.description}")
        
        prompt = self._create_planning_prompt(task)
        response = self.llm_client.chat_completion([
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt}
        ])
        
        # Parse the plan returned by LLM
        steps = self._parse_plan_response(response, task.id)
        
        plan = TaskPlan(
            task_id=task.id,
            description=task.description,
            steps=steps
        )
        
        self.logger.info(f"Task {task.id} planned with {len(steps)} steps")
        return plan
    
    def _get_system_prompt(self) -> str:
        """Get system prompt"""
        return """You are a blockchain development expert. Your task is to analyze a given blockchain task and break it down into executable steps.

Each step should be either:
1. A Solidity smart contract that needs to be compiled and deployed
2. A Python script that interacts with the blockchain

For each step, provide:
- A unique step ID (step_1, step_2, etc.)
- A clear description of what this step does
- The step type (either "solidity" or "python")
- Dependencies on other steps (if any)

Return your plan in JSON format:
```json
{
  "steps": [
    {
      "id": "step_1",
      "description": "Deploy ERC20 token contract with name MyToken and symbol MTK",
      "step_type": "solidity",
      "dependencies": []
    },
    {
      "id": "step_2", 
      "description": "Transfer 1000 tokens to address 0x123...",
      "step_type": "python",
      "dependencies": ["step_1"]
    }
  ]
}
```

Keep descriptions clear and specific. Focus on what needs to be accomplished, not how to implement it."""

    def _create_planning_prompt(self, task: BenchmarkTask) -> str:
        """Create planning prompt"""
        return f"""Please analyze this blockchain task and break it down into executable steps:

Task ID: {task.id}
Task Type: {task.type}
Task Description: {task.description}

Additional context:
- Each step should be atomic and executable independently
- Solidity steps are for smart contract deployment
- Python steps are for blockchain interactions (queries, transactions, etc.)
- Consider dependencies between steps (e.g., a contract must be deployed before it can be used)
- Be specific about what each step accomplishes

Please provide a detailed execution plan."""

    def _parse_plan_response(self, response: str, task_id: str) -> List[TaskStep]:
        """Parse the plan returned by LLM"""
        try:
            # Try to extract JSON
            json_blocks = self.llm_client.extract_json_blocks(response)
            
            if not json_blocks:
                raise ValueError("No valid JSON found in response")
            
            plan_data = json_blocks[0]
            steps_data = plan_data.get("steps", [])
            
            steps = []
            for i, step_data in enumerate(steps_data):
                step_type_str = step_data.get("step_type", "python").lower()
                step_type = StepType.SOLIDITY if step_type_str == "solidity" else StepType.PYTHON
                
                step = TaskStep(
                    id=step_data.get("id", f"step_{i+1}"),
                    description=step_data.get("description", ""),
                    step_type=step_type,
                    dependencies=step_data.get("dependencies", [])
                )
                steps.append(step)
            
            return steps
            
        except Exception as e:
            self.logger.error(f"Failed to parse plan response: {e}")
            self.logger.debug(f"Response content: {response}")
            
            # Fallback: create single-step plan
            return self._create_fallback_plan(task_id, response)
    
    def _create_fallback_plan(self, task_id: str, original_response: str) -> List[TaskStep]:
        """Create fallback plan (when parsing fails)"""
        self.logger.warning(f"Creating fallback plan for task {task_id}")
        
        # Determine if contract deployment is needed based on keywords
        response_lower = original_response.lower()
        
        steps = []
        
        if any(keyword in response_lower for keyword in ["deploy", "contract", "solidity", "erc20", "erc721"]):
            steps.append(TaskStep(
                id="step_1",
                description="Deploy smart contract",
                step_type=StepType.SOLIDITY,
                dependencies=[]
            ))
            
            steps.append(TaskStep(
                id="step_2", 
                description="Interact with deployed contract",
                step_type=StepType.PYTHON,
                dependencies=["step_1"]
            ))
        else:
            steps.append(TaskStep(
                id="step_1",
                description="Execute blockchain interaction",
                step_type=StepType.PYTHON,
                dependencies=[]
            ))
        
        return steps
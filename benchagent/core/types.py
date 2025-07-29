from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum


class StepType(Enum):
    SOLIDITY = "solidity"
    PYTHON = "python"


class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"


@dataclass
class TaskStep:
    """Single task step"""
    id: str
    description: str
    step_type: StepType
    dependencies: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


@dataclass
class ExecutionResult:
    """Execution result"""
    success: bool
    step_id: str
    code: Optional[str] = None
    output: Optional[str] = None
    error: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    attempt: int = 1
    
    
@dataclass
class TaskPlan:
    """Task execution plan"""
    task_id: str
    description: str
    steps: List[TaskStep]
    
    
@dataclass
class BenchmarkTask:
    """基准测试任务"""
    id: str
    description: str
    type: str
    max_retries: int = 3
    timeout: int = 300
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
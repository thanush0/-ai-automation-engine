from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid
import asyncio
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Task:
    def __init__(self, command: str, actions: List[Dict[str, Any]]):
        self.id = str(uuid.uuid4())
        self.command = command
        self.actions = actions
        self.status = TaskStatus.PENDING
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.result: Optional[Dict[str, Any]] = None
        self.error: Optional[str] = None

class TaskManager:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.is_processing = False
    
    def create_task(self, command: str, actions: List[Dict[str, Any]]) -> Task:
        """Create new task."""
        task = Task(command, actions)
        self.tasks[task.id] = task
        return task
    
    async def add_task(self, task: Task):
        """Add task to queue."""
        await self.task_queue.put(task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get all tasks."""
        return [
            {
                "id": task.id,
                "command": task.command,
                "status": task.status.value,
                "created_at": task.created_at.isoformat(),
                "started_at": task.started_at.isoformat() if task.started_at else None,
                "completed_at": task.completed_at.isoformat() if task.completed_at else None
            }
            for task in self.tasks.values()
        ]
    
    def get_task_result(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task execution result."""
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            "id": task.id,
            "command": task.command,
            "status": task.status.value,
            "result": task.result,
            "error": task.error
        }
    
    async def process_queue(self, engine):
        """Process task queue."""
        self.is_processing = True
        
        while self.is_processing:
            try:
                task = await asyncio.wait_for(self.task_queue.get(), timeout=1.0)
                
                # Update task status
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                
                # Execute task
                try:
                    result = engine.execute_actions(task.actions)
                    task.result = result
                    task.status = TaskStatus.COMPLETED if result["success"] else TaskStatus.FAILED
                except Exception as e:
                    task.error = str(e)
                    task.status = TaskStatus.FAILED
                
                task.completed_at = datetime.now()
                
                self.task_queue.task_done()
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                print(f"Queue processing error: {e}")
    
    def stop_processing(self):
        """Stop queue processing."""
        self.is_processing = False

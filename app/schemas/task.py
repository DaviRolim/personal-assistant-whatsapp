from datetime import datetime
from typing import Optional, Literal
from .base import BaseSchema

TaskStatus = Literal['todo', 'in_progress', 'blocked', 'completed']
TaskPriority = Literal['high', 'medium', 'low']

class TaskBase(BaseSchema):
    title: str
    description: Optional[str] = None
    status: TaskStatus = 'todo'
    priority: TaskPriority = 'medium'
    estimated_duration: Optional[int] = None  # minutes
    actual_duration: Optional[int] = None  # minutes
    due_date: Optional[datetime] = None
    parent_task_id: Optional[int] = None

class TaskCreate(TaskBase):
    project_id: int

class Task(TaskBase):
    task_id: int
    project_id: int
    created_at: datetime
    completed_at: Optional[datetime] = None
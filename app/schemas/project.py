from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel
from .base import BaseSchema

ProjectStatus = Literal['planning', 'active', 'paused', 'completed', 'abandoned']
ProjectPriority = Literal['high', 'medium', 'low']

class ProjectBase(BaseSchema):
    name: str
    description: Optional[str] = None
    status: ProjectStatus = 'planning'
    priority: ProjectPriority = 'medium'
    start_date: Optional[datetime] = None
    deadline: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    user_id: int

class Project(ProjectBase):
    project_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
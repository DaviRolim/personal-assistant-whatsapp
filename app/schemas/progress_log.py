from datetime import datetime
from typing import Optional, Literal
from decimal import Decimal
from pydantic import Field
from .base import BaseSchema

LogType = Literal['task_update', 'goal_progress', 'media_upload', 'activity', 'focus_session']

class ProgressLogBase(BaseSchema):
    log_type: LogType
    related_task_id: Optional[int] = None
    related_goal_id: Optional[int] = None
    related_project_id: Optional[int] = None
    value: Optional[Decimal] = None
    description: Optional[str] = None
    media_url: Optional[str] = None
    duration: Optional[int] = None  # minutes
    energy_level: Optional[int] = Field(None, ge=1, le=5)
    mood: Optional[str] = None

class ProgressLogCreate(ProgressLogBase):
    user_id: int

class ProgressLog(ProgressLogBase):
    log_id: int
    user_id: int
    created_at: datetime
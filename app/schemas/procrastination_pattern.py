from datetime import datetime
from typing import Optional
from pydantic import Field
from .base import BaseSchema

class ProcrastinationPatternBase(BaseSchema):
    trigger_type: str
    description: Optional[str] = None
    frequency: int = 1
    impact_level: Optional[int] = Field(None, ge=1, le=5)

class ProcrastinationPatternCreate(ProcrastinationPatternBase):
    user_id: int

class ProcrastinationPattern(ProcrastinationPatternBase):
    pattern_id: int
    user_id: int
    created_at: datetime
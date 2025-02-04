from datetime import datetime
from typing import Optional, Literal
from decimal import Decimal
from pydantic import BaseModel
from .base import BaseSchema

GoalType = Literal['fitness', 'learning', 'project', 'habit', 'personal']
GoalStatus = Literal['active', 'achieved', 'abandoned']

class GoalBase(BaseSchema):
    title: str
    description: Optional[str] = None
    goal_type: GoalType
    target_value: Decimal
    current_value: Decimal = Decimal('0')
    unit: Optional[str] = None
    frequency: Optional[str] = None
    status: GoalStatus = 'active'
    deadline: Optional[datetime] = None

class GoalCreate(GoalBase):
    user_id: int

class Goal(GoalBase):
    goal_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
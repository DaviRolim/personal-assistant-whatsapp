from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

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
    pass

class Goal(GoalBase):
    goal_id: int
    created_at: datetime
    updated_at: datetime
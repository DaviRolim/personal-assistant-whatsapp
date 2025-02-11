from datetime import datetime
from typing import Dict, Optional

from pydantic import Field

from .base import BaseSchema


class AIInteractionBase(BaseSchema):
    message_text: str
    response_text: str
    intent: Optional[str] = None
    context_data: Optional[Dict] = None
    effectiveness_rating: Optional[int] = Field(None, ge=1, le=5)

class AIInteractionCreate(AIInteractionBase):
    pass

class AIInteraction(AIInteractionBase):
    interaction_id: int
    created_at: datetime
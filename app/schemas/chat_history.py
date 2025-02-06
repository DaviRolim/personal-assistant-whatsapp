from datetime import datetime
from typing import Dict
from .base import BaseSchema

class ChatHistoryBase(BaseSchema):
    session_id: str
    message: Dict

class ChatHistoryCreate(ChatHistoryBase):
    pass

class ChatHistory(ChatHistoryBase):
    id: int
    created_at: datetime
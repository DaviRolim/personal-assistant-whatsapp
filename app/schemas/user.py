from datetime import datetime
from typing import Optional, Dict
from .base import BaseSchema

class UserBase(BaseSchema):
    whatsapp_number: str
    name: Optional[str] = None
    timezone: str = "UTC"
    settings: Optional[Dict] = None

class UserCreate(UserBase):
    pass

class User(UserBase):
    user_id: int
    created_at: datetime
    last_active: Optional[datetime] = None
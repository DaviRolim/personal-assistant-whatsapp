from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.chat_history import ChatHistory
from .base_repository import BaseRepository

class ChatHistoryRepository(BaseRepository[ChatHistory]):
    def __init__(self, db: Session):
        super().__init__(ChatHistory, db)
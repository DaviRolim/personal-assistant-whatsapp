
from app.models.chat_history import ChatHistory
from .base_repository import BaseRepository
from sqlalchemy.ext.asyncio import AsyncSession

class ChatHistoryRepository(BaseRepository[ChatHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatHistory, db)

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.chat_history import ChatHistory

from .base_repository import BaseRepository


class ChatHistoryRepository(BaseRepository[ChatHistory]):
    def __init__(self, db: AsyncSession):
        super().__init__(ChatHistory, db)
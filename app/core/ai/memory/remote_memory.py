from typing import List, Dict
from sqlalchemy.orm import Session

from app.core.ai.memory.base import BaseMemory
from app.db.repository.chat_history_repository import ChatHistoryRepository
from app.models.chat_history import ChatHistory

class RemoteMemory(BaseMemory):
    def __init__(self, db: Session, session_id: str):
        self.repository = ChatHistoryRepository(db)
        self.session_id = session_id

    async def get_messages(self) -> List[Dict]:
        messages = await self.repository.get_all(where=[ChatHistory.session_id == self.session_id])
        return [message.message for message in messages]

    async def add_message(self, role: str, content: str) -> None:
        message = {"role": role, "content": content}
        await self.repository.create(
            {
                "session_id": self.session_id,
                "message": message,
            }
        )

    async def clear_messages(self) -> None:
        messages = await self.repository.get_all(where=[ChatHistory.session_id == self.session_id])
        for message in messages:
            await self.repository.delete(message.id)
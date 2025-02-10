from typing import List, Literal, Optional, cast

from openai.types.chat import ChatCompletionMessageParam
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.memory.base import BaseMemory
from app.db.repository.chat_history_repository import ChatHistoryRepository
from app.models.chat_history import ChatHistory


class RemoteMemory(BaseMemory):
    def __init__(self, db: AsyncSession, session_id: str):
        self.repository = ChatHistoryRepository(db)
        self.session_id = session_id
        self.retrieve_limit = 5

    def _to_chat_completion_message(self, message: ChatHistory) -> ChatCompletionMessageParam:
        msg_dict = message.message
        return cast(ChatCompletionMessageParam, msg_dict)

    async def get_messages(self) -> Optional[List[ChatCompletionMessageParam]]:
        messages = await self.repository.get_all(
            where=[ChatHistory.session_id == self.session_id],
            limit=self.retrieve_limit,
            order_by=[ChatHistory.id.desc()]
        )
        return [self._to_chat_completion_message(message) for message in messages]

    async def add_message(self, role: Literal["user", "assistant"], content: str) -> None:
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
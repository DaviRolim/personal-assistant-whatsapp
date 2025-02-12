from typing import List, Literal, Optional, cast

from openai.types.chat import ChatCompletionMessageParam

from app.ai.memory.base import BaseMemory


class LocalMemory(BaseMemory):
    def __init__(self):
        self._message_history: List[ChatCompletionMessageParam] = []

    async def get_messages(self) -> Optional[List[ChatCompletionMessageParam]]:
        return self._message_history

    async def add_message(self, role: Literal["user", "assistant"], content: str) -> None:
        if role == "user":
            message = cast(ChatCompletionMessageParam, {"role": "user", "content": content})
        else:
            message = cast(ChatCompletionMessageParam, {"role": "assistant", "content": content})
        self._message_history.append(message)

    async def clear_messages(self) -> None:
        self._message_history = []

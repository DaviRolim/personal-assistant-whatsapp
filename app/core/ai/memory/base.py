from abc import ABC, abstractmethod
from typing import List, Literal, Optional
from openai.types.chat import ChatCompletionMessageParam


class BaseMemory(ABC):
    @abstractmethod
    async def get_messages(self) -> Optional[List[ChatCompletionMessageParam]]:
        pass

    @abstractmethod
    async def add_message(self, role: Literal["user", "assistant"], content: str) -> None:
        pass

    @abstractmethod
    async def clear_messages(self) -> None:
        pass
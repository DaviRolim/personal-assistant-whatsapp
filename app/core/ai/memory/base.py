from abc import ABC, abstractmethod
from typing import List, Dict

class BaseMemory(ABC):
    @abstractmethod
    async def get_messages(self) -> List[Dict]:
        pass

    @abstractmethod
    async def add_message(self, role: str, content: str) -> None:
        pass

    @abstractmethod
    async def clear_messages(self) -> None:
        pass
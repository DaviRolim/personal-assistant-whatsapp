from typing import List, Dict
from app.core.ai.memory.base import BaseMemory

class LocalMemory(BaseMemory):
    def __init__(self):
        self._message_history: List[Dict] = []

    async def get_messages(self) -> List[Dict]:
        return self._message_history

    async def add_message(self, role: str, content: str) -> None:
        self._message_history.append({"role": role, "content": content})

    async def clear_messages(self) -> None:
        self._message_history = []

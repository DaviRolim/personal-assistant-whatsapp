from typing import Optional
from sqlalchemy.orm import Session

from app.core.ai.memory.base import BaseMemory
from app.core.ai.memory.local_memory import LocalMemory
from app.core.ai.memory.remote_memory import RemoteMemory

def memory_factory(memory_type: str, db: Optional[Session] = None, session_id: Optional[str] = None) -> BaseMemory:
    if memory_type == "local":
        return LocalMemory()
    elif memory_type == "remote":
        if db is None or session_id is None:
            raise ValueError("Database session and session ID are required for remote memory.")
        return RemoteMemory(db=db, session_id=session_id)
    else:
        raise ValueError(f"Invalid memory type: {memory_type}")
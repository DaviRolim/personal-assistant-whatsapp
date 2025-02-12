import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.memory.base import BaseMemory

logger = logging.getLogger(__name__)

class MemoryService:
    """Service for managing chat memory operations."""
    
    def __init__(self, memory_type: str):
        self.memory_type = memory_type
        self.memory: Optional[BaseMemory] = None

    async def setup_memory(self, db: Optional[AsyncSession] = None, session_id: str = "default_session") -> None:
        """
        Set up the initial memory instance.
        
        Args:
            db: Optional database session for remote memory
            session_id: Identifier for the memory session
            
        Raises:
            HTTPException: If memory initialization fails
        """
        try:
            from app.ai.memory import memory_factory
            logger.info(f'Setting up {self.memory_type} memory for session: {session_id}')
            
            if self.memory_type == "remote":
                if not db:
                    raise ValueError("Database session required for remote memory")
                self.memory = memory_factory(memory_type=self.memory_type, db=db, session_id=session_id)
                logger.info("Remote memory initialized successfully")
            elif self.memory_type == "local":
                self.memory = memory_factory(memory_type=self.memory_type)
                logger.info("Local memory initialized successfully")
            else:
                raise ValueError(f"Unsupported memory type: {self.memory_type}")
                
        except Exception as e:
            logger.error(f"Failed to set up memory: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to initialize AI companion memory")

    async def get_memory_instance(self, db: Optional[AsyncSession], session_id: str = "default_session") -> BaseMemory:
        """
        Get a memory instance for processing.
        
        Args:
            db: Database session for remote memory
            session_id: Identifier for the memory session
            
        Returns:
            BaseMemory: Memory instance
            
        Raises:
            ValueError: If db session is missing for remote memory
            RuntimeError: If memory initialization fails
        """
        if self.memory_type == "remote":
            from app.ai.memory import memory_factory
            logger.info("Creating fresh remote memory with new db session")
            if not db:
                raise ValueError("Database session required for remote memory")
            return memory_factory(memory_type="remote", db=db, session_id=session_id)
        
        if self.memory is None:
            logger.info("Memory not initialized, attempting initialization")
            await self.setup_memory(db)
            if self.memory is None:
                raise RuntimeError("Failed to initialize memory after attempt")
        return self.memory 
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.agents.assistant_agent_v2 import agent_response
from app.core.ai.memory.base import BaseMemory
from app.core.ai.tools.whatsapp_tool import send_message

logger = logging.getLogger(__name__)

class AICompanionService:
    def __init__(self, memory_type: str, target_number: str = "99763846"):
        logger.debug(f'[DH] memory_type: {memory_type}')
        self.memory_type = memory_type
        self.memory: Optional[BaseMemory] = None
        self.target_number = target_number  # Could be moved to config

    async def init_memory(self, db: Optional[AsyncSession] = None, session_id="default_session"):
        logger.debug(f'[DH] db: {db}')
        from app.core.ai.memory import memory_factory
        if self.memory_type == "remote":
            self.memory = memory_factory(memory_type=self.memory_type, db=db, session_id=session_id)
            print(f"[DH] Initialized memory with db: {db}")
        elif self.memory_type == "local":
            self.memory = memory_factory(memory_type=self.memory_type)

    async def handle_webhook_data(self, body: dict, db: AsyncSession) -> dict:
        data = body.get('data', {})
        key = data.get('key', {})
        logger.debug(f'[DH] key: {key}')
        logger.debug(f'[DH] data: {data}')
        
        if not self._is_valid_message(key):
            logger.debug("Message ignored")
            return {"message": "Message ignored"}

        message_sent = await self._process_message(
            key=key,
            message=data.get('message', {}),
            api_key=body.get('apikey', {}),
            db=db 
        )

        return {"message": f'message_sent: {message_sent}'}

    def _is_valid_message(self, key: dict) -> bool:
        return (
            self.target_number in key.get('remoteJid', '') 
            and key.get('fromMe', True)
        )

    async def _process_message(self, key: dict, message: dict, api_key: str, db: AsyncSession) -> bool:
        if self.memory is None:
            await self.init_memory(db)
            if self.memory is None:
                raise RuntimeError("Failed to initialize memory")
                
        quoted = {"key": key, "message": message}
        user_message = message.get('conversation', '')
        logger.debug(f'[DH] user_message: {user_message}')

        await self.memory.add_message(role="user", content=user_message)
        response = await agent_response(user_message, message_history=await self.memory.get_messages())
        logger.debug(f'[DH] response: {response}')

        if response is None:
            return False

        await self.memory.add_message(role="assistant", content=response)
        return send_message(
            number=key['remoteJid'],
            text=response,
            api_key=api_key,
            quoted=quoted
        )

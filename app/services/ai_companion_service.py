import logging
from typing import Optional

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.agents.assistant_agent_v2 import agent_response
from app.core.ai.memory.base import BaseMemory
from app.core.ai.tools.whatsapp_tool import send_message

logger = logging.getLogger(__name__)

class AICompanionService:
    def __init__(self, memory_type: str, target_number: str = "99763846"):
        logger.info(f'Initializing AICompanionService with memory_type: {memory_type}')
        self.memory_type = memory_type
        self.memory: Optional[BaseMemory] = None
        self.target_number = target_number

    async def init_memory(self, db: Optional[AsyncSession] = None, session_id="default_session"):
        try:
            from app.core.ai.memory import memory_factory
            logger.info(f'Initializing {self.memory_type} memory for session: {session_id}')
            
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
            logger.error(f"Failed to initialize memory: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to initialize AI companion memory")

    async def handle_webhook_data(self, body: dict, db: AsyncSession) -> dict:
        try:
            data = body.get('data', {})
            key = data.get('key', {})
            logger.info(f'Processing webhook data for remote JID: {key.get("remoteJid", "unknown")}')
            
            if not data or not key:
                logger.warning("Invalid webhook data received: missing required fields")
                raise HTTPException(status_code=400, detail="Invalid webhook data")

            if not self._is_valid_message(key):
                logger.info("Message ignored - not matching target criteria")
                return {"message": "Message ignored"}

            message_sent = await self._process_message(
                key=key,
                message=data.get('message', {}),
                api_key=body.get('apikey', {}),
                db=db
            )

            return {"message": f'message_sent: {message_sent}'}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process webhook data")

    def _is_valid_message(self, key: dict) -> bool:
        try:
            is_valid = (
                self.target_number in key.get('remoteJid', '') 
                and key.get('fromMe', True)
            )
            logger.debug(f'Message validation result: {is_valid}')
            return is_valid
        except Exception as e:
            logger.error(f"Error validating message: {str(e)}", exc_info=True)
            return False

    async def _process_message(self, key: dict, message: dict, api_key: str, db: AsyncSession) -> bool:
        try:
            if self.memory_type == "remote":
                from app.core.ai.memory import memory_factory
                logger.info("Creating fresh remote memory with new db session")
                memory_instance = memory_factory(memory_type="remote", db=db, session_id="default_session")
            else:
                if self.memory is None:
                    logger.info("Memory not initialized, attempting initialization")
                    await self.init_memory(db)
                    if self.memory is None:
                        raise RuntimeError("Failed to initialize memory after attempt")
                memory_instance = self.memory

            quoted = {"key": key, "message": message}
            user_message = message.get('conversation', '')
            
            if not user_message:
                logger.warning("Empty user message received")
                return False

            logger.info(f'Processing user message: {user_message[:50]}...')
            await memory_instance.add_message(role="user", content=user_message)

            response = await agent_response(user_message, message_history=await memory_instance.get_messages())
            
            if response is None:
                logger.warning("No response generated from agent")
                return False

            logger.info(f'Agent response generated: {response[:50]}...')
            await memory_instance.add_message(role="assistant", content=response)
            
            message_sent = send_message(
                number=key['remoteJid'],
                text=response,
                api_key=api_key,
                quoted=quoted
            )
            
            logger.info(f'Message sent successfully to {key["remoteJid"]}')
            return message_sent

        except RuntimeError as e:
            logger.error(f"Runtime error in message processing: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process message - runtime error")
        except Exception as e:
            logger.error(f"Unexpected error in message processing: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process message")

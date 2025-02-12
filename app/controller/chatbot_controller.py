import logging

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.agent_service import AgentService
from app.services.memory_service import MemoryService
from app.services.message_service import MessageService

logger = logging.getLogger(__name__)

class ChatbotController:
    """Controller for handling chatbot webhook interactions."""
    
    def __init__(self, memory_type: str, target_number: str = "99763846"):
        """Initialize controller with required services."""
        self.target_number = target_number
        self.memory_service = MemoryService(memory_type)
        self.message_service = MessageService()
        self.agent_service = AgentService()

    async def handle_webhook_data(self, body: dict, db: AsyncSession) -> dict:
        """
        Handle incoming webhook data and process messages.
        
        Args:
            body: Webhook request body
            db: Database session for memory operations
            
        Returns:
            dict: Response indicating message processing status
            
        Raises:
            HTTPException: For invalid data or processing errors
        """
        try:
            # Extract webhook data
            data = body.get('data', {})
            key = data.get('key', {})
            instance = body.get('instance', 'daviwpp')
            logger.info(f'Processing webhook data for remote JID: {key.get("remoteJid", "unknown")}')
            
            # Validate webhook data
            if not data or not key:
                logger.warning("Invalid webhook data received: missing required fields")
                raise HTTPException(status_code=400, detail="Invalid webhook data")

            if not self._is_valid_message(key):
                logger.info("Message ignored - not matching target criteria")
                return {"message": "Message ignored"}

            # Process message
            message_sent = await self._process_message(
                key=key,
                message=data.get('message', {}),
                api_key=body.get('apikey', {}),
                db=db,
                instance=instance
            )

            return {"message": f'message_sent: {message_sent}'}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing webhook data: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process webhook data")

    async def _process_message(self, key: dict, message: dict, api_key: str, db: AsyncSession, instance: str) -> bool:
        """Process incoming message and orchestrate response generation."""
        try:
            # Get memory instance
            memory_instance = await self.memory_service.get_memory_instance(db)
            quoted = {"key": key, "message": message}
            
            # Extract user message
            user_message = await self.message_service.extract_user_message(
                message=message,
                message_id=key['id'],
                instance=instance,
                api_key=api_key
            )
            if not user_message:
                logger.warning("Empty user message received after processing")
                return False

            # Generate response
            response = await self.agent_service.process_interaction(user_message, memory_instance)
            if not response:
                return False

            # Send response
            return await self.message_service.send_response(
                response=response,
                recipient=key['remoteJid'],
                quoted=quoted,
                api_key=api_key,
                instance=instance
            )

        except Exception as e:
            logger.error(f"Error in message processing: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process message")

    def _is_valid_message(self, key: dict) -> bool:
        """Check if the message matches target criteria."""
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

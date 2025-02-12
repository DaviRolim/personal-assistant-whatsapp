import logging
from typing import Optional

from app.integrations.evolution_api import send_message
from app.services.audio_service import AudioService

logger = logging.getLogger(__name__)

class MessageService:
    """Service for handling message processing and response sending."""
    
    def __init__(self):
        self.audio_service = AudioService()

    async def extract_user_message(self, message: dict, message_id: str, instance: str, api_key: str) -> Optional[str]:
        """
        Extract user message from different message types.
        
        Args:
            message: Raw message data
            message_id: ID of the message
            instance: Instance identifier
            api_key: API key for external services
            
        Returns:
            Optional[str]: Extracted message if successful, None otherwise
        """
        if 'conversation' in message:
            logger.info("Processing text message")
            return message.get('conversation', '')
        elif 'audioMessage' in message:
            return await self.audio_service.process_audio_message(
                message_id=message_id,
                audio_info=message['audioMessage'],
                instance=instance,
                api_key=api_key
            )
        return None

    async def send_response(self, response: str, recipient: str, quoted: dict, api_key: str, instance: str) -> bool:
        """
        Send response message to user.
        
        Args:
            response: Message to send
            recipient: Recipient identifier
            quoted: Quoted message data
            api_key: API key for external services
            instance: Instance identifier
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        message_sent = send_message(
            number=recipient,
            text=response,
            api_key=api_key,
            quoted=quoted,
            instance=instance
        )
        
        logger.info(f'Message sent successfully to {recipient}')
        return message_sent 
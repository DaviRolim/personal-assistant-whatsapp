import logging
from typing import Optional

from app.ai.transcribe import transcribe_audio
from app.core.audio_utils import cleanup_temp_file, process_base64_audio
from app.integrations.evolution_api import get_base64_from_media_message

logger = logging.getLogger(__name__)

class AudioService:
    """Service for handling audio message processing and transcription."""

    async def process_audio_message(self, message_id: str, audio_info: dict, instance: str, api_key: str) -> Optional[str]:
        """
        Process audio message and return transcription.
        
        Args:
            message_id: ID of the message containing audio
            audio_info: Audio message metadata
            instance: Instance identifier
            api_key: API key for external services
            
        Returns:
            Optional[str]: Transcribed text if successful, None otherwise
        """
        logger.info("Processing audio message")
        logger.info(f"Audio message details - Duration: {audio_info.get('seconds', 'unknown')}s, "
                   f"Mime-type: {audio_info.get('mimetype', 'unknown')}")
        
        # Get base64 from audio message
        logger.info(f"Fetching base64 audio data for message ID: {message_id}")
        base64_audio = await get_base64_from_media_message(
            instance=instance,
            message_id=message_id,
            api_key=api_key
        )
        
        if not base64_audio:
            logger.error("Failed to get base64 from audio message - base64_audio is None or empty")
            return None
        
        return await self.process_audio_data(base64_audio)

    async def process_audio_data(self, base64_audio: str) -> Optional[str]:
        """
        Process base64 audio data and return transcription.
        
        Args:
            base64_audio: Base64 encoded audio data
            
        Returns:
            Optional[str]: Transcribed text if successful, None otherwise
        """
        logger.info("Processing base64 audio data")
        result = process_base64_audio(base64_audio)
        if not result:
            logger.error("Failed to process audio data")
            return None
            
        temp_file_path, audio_size = result
        logger.info(f"Audio processed successfully. Size: {audio_size} bytes")
        
        try:
            transcription = await transcribe_audio(temp_file_path)
            if not transcription:
                logger.error("Transcription failed - received None from transcribe_audio")
                return None
            
            logger.info(f"Audio successfully transcribed. Transcription length: {len(transcription)} chars")
            logger.info(f"Transcription preview: {transcription[:100]}...")
            return transcription
        finally:
            cleanup_temp_file(temp_file_path) 
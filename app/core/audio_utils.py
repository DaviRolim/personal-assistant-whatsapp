import base64
import logging
import os
import tempfile
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

def process_base64_audio(base64_audio: str) -> Optional[Tuple[str, int]]:
    """
    Process base64 audio data and save it to a temporary file.
    
    Args:
        base64_audio: Base64 encoded audio data
        
    Returns:
        Tuple containing the temporary file path and size of decoded data, or None if processing fails
    """
    try:
        logger.info("Decoding base64 audio data")
        audio_data = base64.b64decode(base64_audio)
        data_size = len(audio_data)
        logger.info(f"Successfully decoded audio data of size: {data_size} bytes")
        
        logger.info("Creating temporary file for audio data")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
            logger.info(f"Audio data written to temporary file: {temp_file_path}")
            
        return temp_file_path, data_size
    except Exception as e:
        logger.error(f"Failed to process audio data: {str(e)}")
        return None

def cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary audio file.
    
    Args:
        file_path: Path to the temporary file to be deleted
    """
    logger.info(f"Cleaning up temporary file: {file_path}")
    try:
        os.unlink(file_path)
        logger.info("Successfully deleted temporary file")
    except Exception as e:
        logger.error(f"Failed to delete temporary file: {str(e)}") 
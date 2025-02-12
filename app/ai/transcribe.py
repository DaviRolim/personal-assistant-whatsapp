import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

logger = logging.getLogger(__name__)

async def transcribe_audio(audio_file_path: str | Path) -> Optional[str]:
    """
    Transcribe an audio file using OpenAI Whisper API.
    
    Args:
        audio_file_path: Path to the audio file to transcribe
        
    Returns:
        Transcribed text or None if transcription fails
    """
    try:
        logger.info("Initializing OpenAI client for audio transcription")
        if not os.getenv("OPENAI_API_KEY"):
            logger.error("OPENAI_API_KEY environment variable not set")
            return None
            
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        try:
            logger.info("Sending audio file to OpenAI Whisper API for transcription")
            with open(audio_file_path, 'rb') as audio_file:
                transcription = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            logger.info("Successfully received transcription from Whisper API")
            return transcription.text
        except Exception as e:
            logger.error(f"Error during OpenAI API call: {str(e)}", exc_info=True)
            return None
                
    except Exception as e:
        logger.error(f"Unexpected error in audio transcription: {str(e)}", exc_info=True)
        return None

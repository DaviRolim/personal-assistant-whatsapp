import logging
import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import HTTPException
from openai import OpenAI
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.ai.agents.assistant_agent_v2 import agent_response
from app.core.ai.memory.base import BaseMemory
from app.core.ai.tools.whatsapp_tool import (get_base64_from_media_message,
                                             send_message)

load_dotenv()
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
            instance = body.get('instance', 'daviwpp')
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
                db=db,
                instance=instance
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

    async def _transcribe_audio(self, base64_audio: str) -> Optional[str]:
        """Transcribe audio using OpenAI Whisper API."""
        try:
            logger.info("Initializing OpenAI client for audio transcription")
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            if not os.getenv("OPENAI_API_KEY"):
                logger.error("OPENAI_API_KEY environment variable not set")
                return None
            
            # Save base64 to temporary file
            import base64
            import tempfile
            
            logger.info("Decoding base64 audio data")
            try:
                audio_data = base64.b64decode(base64_audio)
                logger.info(f"Successfully decoded audio data of size: {len(audio_data)} bytes")
            except Exception as e:
                logger.error(f"Failed to decode base64 audio data: {str(e)}")
                return None
            
            logger.info("Creating temporary file for audio data")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
                logger.info(f"Audio data written to temporary file: {temp_file_path}")
            
            try:
                logger.info("Sending audio file to OpenAI Whisper API for transcription")
                with open(temp_file_path, 'rb') as audio_file:
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                logger.info("Successfully received transcription from Whisper API")
                return transcription.text
            except Exception as e:
                logger.error(f"Error during OpenAI API call: {str(e)}", exc_info=True)
                return None
            finally:
                # Clean up temp file
                logger.info(f"Cleaning up temporary file: {temp_file_path}")
                try:
                    os.unlink(temp_file_path)
                    logger.info("Successfully deleted temporary file")
                except Exception as e:
                    logger.error(f"Failed to delete temporary file: {str(e)}")
                
        except Exception as e:
            logger.error(f"Unexpected error in audio transcription: {str(e)}", exc_info=True)
            return None

    async def _process_message(self, key: dict, message: dict, api_key: str, db: AsyncSession, instance: str) -> bool:
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
            
            # Handle different message types
            user_message = ""
            if 'conversation' in message:
                logger.info("Processing text message")
                user_message = message.get('conversation', '')
            elif 'audioMessage' in message:
                logger.info("Detected audio message, starting processing pipeline")
                audio_info = message.get('audioMessage', {})
                logger.info(f"Audio message details - Duration: {audio_info.get('seconds', 'unknown')}s, "
                          f"Mime-type: {audio_info.get('mimetype', 'unknown')}")
                
                # Get base64 from audio message
                logger.info(f"Fetching base64 audio data for message ID: {key['id']}")
                base64_audio = await get_base64_from_media_message(
                    instance=instance,
                    message_id=key['id'],
                    api_key=api_key
                )
                
                if not base64_audio:
                    logger.error("Failed to get base64 from audio message - base64_audio is None or empty")
                    return False
                
                logger.info("Successfully retrieved base64 audio data, proceeding with transcription")
                # Transcribe audio
                transcription = await self._transcribe_audio(base64_audio)
                if not transcription:
                    logger.error("Transcription failed - received None from _transcribe_audio")
                    return False
                
                user_message = transcription
                logger.info(f"Audio successfully transcribed. Transcription length: {len(user_message)} chars")
                logger.info(f"Transcription preview: {user_message[:100]}...")
            
            if not user_message:
                logger.warning("Empty user message received after processing")
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
                quoted=quoted,
                instance=instance
            )
            
            logger.info(f'Message sent successfully to {key["remoteJid"]}')
            return message_sent

        except RuntimeError as e:
            logger.error(f"Runtime error in message processing: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process message - runtime error")
        except Exception as e:
            logger.error(f"Unexpected error in message processing: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail="Failed to process message")

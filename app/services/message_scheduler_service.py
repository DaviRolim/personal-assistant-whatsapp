import logging
import os

from app.db.database import get_db

logger = logging.getLogger(__name__)

async def send_scheduled_message(message: str) -> None:
    """Send a scheduled message through the webhook."""
    try:
        payload = {
            "apikey": os.getenv("EVOLUTION_APIKEY"),
            "instance": "James",
            "data": {
                "message": {
                    "conversation": message
                },
                "key": {
                    "id": os.getenv("EVOLUTION_KEY_ID"),
                    "remoteJid": "558399763846@s.whatsapp.net",
                    "fromMe": True
                }
            }
        }
        async with get_db() as db:
            from app.api.dependencies import \
                chatbot_controller  # Import here to avoid circular dependency
            await chatbot_controller.handle_webhook_data(payload, db)
    except Exception as e:
        logger.error(f"Error sending scheduled message: {str(e)}") 
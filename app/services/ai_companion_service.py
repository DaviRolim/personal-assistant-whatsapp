from app.core.ai.agents.assistant_agent_v2 import agent_response
from app.core.ai.tools.whatsapp_tool import send_message
from app.core.ai.local_memory import get_messages, add_message
import logging

class AICompanionService:
    def __init__(self):
        self.target_number = "99763846"  # Could be moved to config

    async def handle_webhook_data(self, body: dict) -> dict:
        data = body.get('data', {})
        key = data.get('key', {})
        print(f'[DH] key: {key}')
        print(f'[DH] data: {data}')
        logging.debug(f'[DH] key: {key}')
        logging.debug(f'[DH] data: {data}')
        
        if not self._is_valid_message(key):
            logging.debug("Message ignored")
            return {"message": "Message ignored"}

        message_sent = await self._process_message(
            key=key,
            message=data.get('message', {}),
            api_key=body.get('apikey')
        )

        return {"message": f'message_sent: {message_sent}'}

    def _is_valid_message(self, key: dict) -> bool:
        return (
            self.target_number in key.get('remoteJid', '') 
            and key.get('fromMe', True)
        )

    async def _process_message(self, key: dict, message: dict, api_key: str) -> bool:
        quoted = {"key": key, "message": message}
        user_message = message.get('conversation', '')
        logging.debug(f'[DH] user_message: {user_message}')
        
        add_message("user", user_message)
        response = await agent_response(user_message, message_history=get_messages())
        logging.debug(f'[DH] response: {response}')
        add_message("assistant", response)
        
        return send_message(
            number=key['remoteJid'],
            text=response,
            api_key=api_key,
            quoted=quoted
        )

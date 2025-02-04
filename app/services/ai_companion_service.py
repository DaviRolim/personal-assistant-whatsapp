from app.core.ai.agents.assistant_agent import agent_response
from app.core.ai.tools.whatsapp_tool import send_message
from app.core.ai.local_memory import get_messages, add_message

class AICompanionService:
    def __init__(self):
        self.target_number = "3846"  # Could be moved to config

    def handle_webhook_data(self, body: dict) -> dict:
        data = body.get('data', {})
        key = data.get('key', {})
        
        if not self._is_valid_message(key):
            return {"message": "Message ignored"}

        message_sent = self._process_message(
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

    def _process_message(self, key: dict, message: dict, api_key: str) -> bool:
        quoted = {"key": key, "message": message}
        user_message = message.get('conversation', '')
        
        add_message("user", user_message)
        response = agent_response(user_message, message_history=get_messages())
        add_message("assistant", response)
        
        return send_message(
            number=key['remoteJid'],
            text=response,
            api_key=api_key,
            quoted=quoted
        )

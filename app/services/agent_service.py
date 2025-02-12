import logging
from typing import Optional

from app.ai.agents.assistant_agent_v2 import agent_response
from app.ai.memory.base import BaseMemory

logger = logging.getLogger(__name__)

class AgentService:
    """Service for handling AI agent interactions."""

    async def process_interaction(self, user_message: str, memory_instance: BaseMemory) -> Optional[str]:
        """
        Process user message through AI agent and update memory.
        
        Args:
            user_message: User's input message
            memory_instance: Memory instance for context
            
        Returns:
            Optional[str]: Agent's response if successful, None otherwise
        """
        logger.info(f'Processing user message: {user_message[:50]}...')
        await memory_instance.add_message(role="user", content=user_message)

        response = await agent_response(user_message, message_history=await memory_instance.get_messages())
        if response is None:
            logger.warning("No response generated from agent")
            return None

        logger.info(f'Agent response generated: {response[:50]}...')
        await memory_instance.add_message(role="assistant", content=response)
        return response 
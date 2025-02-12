import logging
import os

from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI

logger = logging.getLogger(__name__)

load_dotenv()

async def create_task(content: str, description: str, due_string: str, priority: int):
    api = TodoistAPI(os.getenv("TODOIST_API_KEY"))  # Replace with your actual API token
    try:
        task = api.add_task(
            content=content,
            description=description,
            due_string=due_string,
            priority=priority
        )
        logger.info(f"[DH] Successfully created Todoist task: {task.content}")
        return {"success": True, "message": f"Task created: {task.content}"}
    except Exception as error:
        logger.error(f"[DH] Failed to create Todoist task: {str(error)}")
        return {"success": False, "message": f"Error creating task: {str(error)}"}
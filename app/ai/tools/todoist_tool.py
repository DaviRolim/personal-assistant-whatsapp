import os

from dotenv import load_dotenv
from todoist_api_python.api import TodoistAPI

from .tool_logging import log_tool_execution, setup_tool_logger

# Set up logger for this tool
logger = setup_tool_logger("todoist")

load_dotenv()

async def create_task(reasoning: str, content: str, description: str, due_string: str, priority: int):
    log_tool_execution(
        logger=logger,
        tool_name="todoist_create_task",
        reasoning=reasoning,
        content=content,
        description=description,
        due_string=due_string,
        priority=priority
    )
    
    api = TodoistAPI(os.getenv("TODOIST_API_KEY"))  # Replace with your actual API token
    try:
        task = api.add_task(
            content=content,
            description=description,
            due_string=due_string,
            priority=priority
        )
        log_tool_execution(
            logger=logger,
            tool_name="todoist_create_task",
            reasoning="Task creation successful",
            task_content=task.content,
            status="success"
        )
        return {"success": True, "message": f"Task created: {task.content}"}
    except Exception as error:
        logger.error(f"[DH] Failed to create Todoist task: {str(error)}")
        return {"success": False, "message": f"Error creating task: {str(error)}"}
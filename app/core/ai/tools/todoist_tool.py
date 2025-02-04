import os
from todoist_api_python.api import TodoistAPI
from dotenv import load_dotenv

load_dotenv()

def create_task(content: str, due_string: str, priority: int):
    api = TodoistAPI(os.getenv("TODOIST_API_KEY"))  # Replace with your actual API token
    try:
        task = api.add_task(
            content=content,
            due_string=due_string,
            priority=priority
        )
        return f'Task created: {task.content}'
    except Exception as error:
        print(f"Error creating task: {error}")
        return None
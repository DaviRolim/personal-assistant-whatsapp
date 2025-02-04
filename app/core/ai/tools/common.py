import asyncio
from openai import OpenAI
import os
from typing import List, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv

import json

from app.core.ai.tools.sql_tool import insert, query, update
from app.core.ai.tools.todoist_tool import create_task
from app.core.ai.tools.whatsapp_tool import send_message
load_dotenv()

function_map = {
    "create_task": create_task,
    "execute_insert": insert,
    "execute_update": update,
    "execute_query": query,
}

tools = [
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Creates a new task in Todoist with the specified content, due date, and priority.",
            "parameters": {
                "type": "object",
                "properties": {
                    "content": {
                        "type": "string",
                        "description": "The content of the task to create.",
                    },
                    "due_string": {
                        "type": "string",
                        "description": "The due date of the task in natural language (e.g., 'tomorrow at 2pm').",
                    },
                    "priority": {
                        "type": "number",
                        "description": "The priority of the task (1-4, with 1 being the highest).",
                    },
                },
                "required": ["content", "due_string", "priority"],
            },
        },
    }
]

async def handle_tool_calls(tool_calls: List[Dict], messages: List[Dict]) -> List[Dict]:
    """Handle multiple tool calls and return updated messages."""
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        try:
            if function_name in function_map:
                # Add await here since the functions are now async
                result = await function_map[function_name](**function_args)
                function_result_message = {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
                messages.append(function_result_message)
            else:
                raise ValueError(f"Function '{function_name}' not found")
        except Exception as e:
            error_message = f"Error executing {function_name}: {str(e)}"
            messages.append({
                "role": "tool",
                "content": json.dumps({"error": error_message}),
                "tool_call_id": tool_call.id,
            })
    
    return messages

async def execute_conversation_with_tools(
    client: OpenAI,
    messages: List[Dict],
    tools: List[Dict],
    model: str = "o3-mini"
) -> Dict[str, Any]:
    """Execute a conversation with tool calling capabilities."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",  # Add explicit tool choice
        # reasoning_effort='high'
    )

    choice = response.choices[0]
    messages.append(choice.message)

    if choice.message.tool_calls:
        print(f"Handling tool calls: {choice.message.tool_calls}")    
        messages = await handle_tool_calls(choice.message.tool_calls, messages)
        return await execute_conversation_with_tools(client, messages, tools, model)
    
    return response

from openai import OpenAI
from typing import List, Literal, TypedDict

from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolParam,
    ChatCompletionToolMessageParam,
    ChatCompletionAssistantMessageParam,
    ChatCompletionMessageToolCallParam,
)
from openai.types.chat.chat_completion_message_tool_call import ChatCompletionMessageToolCall
from dotenv import load_dotenv

import json

from app.core.ai.tools.sql_tool import insert, query, update
from app.core.ai.tools.todoist_tool import create_task
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

class ToolMessage(TypedDict):
    role: Literal["tool"]
    content: str
    tool_call_id: str

async def handle_tool_calls(
    tool_calls: List[ChatCompletionMessageToolCall], 
    messages: List[ChatCompletionMessageParam]
) -> List[ChatCompletionMessageParam]:
    """Handle multiple tool calls and return updated messages."""
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        try:
            if function_name in function_map:
                result = await function_map[function_name](**function_args)
                function_result_message: ChatCompletionToolMessageParam = {
                    "role": "tool",
                    "content": json.dumps(result),
                    "tool_call_id": tool_call.id,
                }
                messages.append(function_result_message)
            else:
                raise ValueError(f"Function '{function_name}' not found")
        except Exception as e:
            error_message = f"Error executing {function_name}: {str(e)}"
            error_result_message: ChatCompletionToolMessageParam = {
                "role": "tool",
                "content": json.dumps({"error": error_message}),
                "tool_call_id": tool_call.id,
            }
            messages.append(error_result_message)
    
    return messages

async def execute_conversation_with_tools(
    client: OpenAI,
    messages: List[ChatCompletionMessageParam],
    tools: List[ChatCompletionToolParam],
    model: str = "o3-mini"
) -> ChatCompletion:
    """Execute a conversation with tool calling capabilities."""
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )

    choice = response.choices[0]
    assistant_message: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "content": choice.message.content or "",
    }
    if choice.message.tool_calls:
        # Convert tool calls to the correct parameter type
        tool_calls_params: List[ChatCompletionMessageToolCallParam] = [
            {
                "id": tool_call.id,
                "type": tool_call.type,
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }
            for tool_call in choice.message.tool_calls
        ]
        assistant_message["tool_calls"] = tool_calls_params
    messages.append(assistant_message)

    if choice.message.tool_calls:
        print(f"Handling tool calls: {choice.message.tool_calls}")    
        messages = await handle_tool_calls(choice.message.tool_calls, messages)
        return await execute_conversation_with_tools(client, messages, tools, model)
    
    return response
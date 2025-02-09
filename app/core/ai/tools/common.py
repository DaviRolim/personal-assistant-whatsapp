import json
from typing import List, Literal, TypedDict

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import (ChatCompletion,
                               ChatCompletionAssistantMessageParam,
                               ChatCompletionMessageParam,
                               ChatCompletionMessageToolCallParam,
                               ChatCompletionToolMessageParam,
                               ChatCompletionToolParam)
from openai.types.chat.chat_completion_message_tool_call import \
    ChatCompletionMessageToolCall

from app.core.ai.tools.perplexity_tool import web_search
from app.core.ai.tools.sql_tool import delete, insert, query, update
from app.core.ai.tools.todoist_tool import create_task

load_dotenv()


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

    
function_map = {
    "create_task_on_todoist": create_task,
    "execute_insert": insert,
    "execute_update": update,
    "execute_query": query,
    "execute_delete": delete,
    "web_search": web_search,
}

tools: List[ChatCompletionToolParam] = [
    {
        "type": "function",
        "function": {
            "name": "execute_query",
            "description": "Execute a SQL SELECT query and return results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query_string": {
                        "type": "string",
                        "description": "The SQL query to execute"
                    }
                },
                "required": ["query_string"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_insert",
            "description": "Execute a SQL INSERT statement with parameterized values",
            "parameters": {
                "type": "object",
                "properties": {
                    "insert_statement": {
                        "type": "string",
                        "description": "The INSERT statement with named parameters (e.g., :param_name)"
                    },
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "Dictionary of parameter names and their values"
                        },
                        "description": "List containing a single dictionary of parameter names and their values"
                    }
                },
                "required": ["insert_statement", "values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_update",
            "description": "Execute a SQL UPDATE statement with parameterized values",
            "parameters": {
                "type": "object",
                "properties": {
                    "update_statement": {
                        "type": "string",
                        "description": "The UPDATE statement with named parameters (e.g., :param_name)"
                    },
                    "values": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "description": "Dictionary of parameter names and their values"
                        },
                        "description": "List containing a single dictionary of parameter names and their values"
                    }
                },
                "required": ["update_statement", "values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_delete",
            "description": "Execute a SQL DELETE statement with parameterized values",
            "parameters": {
                "type": "object",
                "properties": {
                    "delete_statement": {
                        "type": "string",
                        "description": "The DELETE statement with named parameters (e.g., :param_name)"
                    },
                    "values": {
                        "type": "object",
                        "description": "Dictionary of parameter names and their values"
                    }
                },
                "required": ["delete_statement", "values"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a web search using Perplexity AI to get up-to-date information from the internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 3)",
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_task_on_todoist",
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
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a web search using Perplexity AI to get up-to-date information from the internet",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 3)",
                        "minimum": 1,
                        "maximum": 10
                    }
                },
                "required": ["query"]
            }
        }
    }
]

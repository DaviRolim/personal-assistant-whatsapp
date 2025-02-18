import json
import logging
from typing import List, Literal, Optional, TypedDict

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
from pydantic import BaseModel, Field

from app.ai.tools.perplexity_tool import web_search
from app.ai.tools.sql_tool import delete, insert, query, update
from app.ai.tools.todoist_tool import create_task
from app.core.scheduler import schedule_interaction

load_dotenv()

logger = logging.getLogger(__name__)


class ToolMessage(TypedDict):
    role: Literal["tool"]
    content: str
    tool_call_id: str

class StructuredResponse(BaseModel):
    """Pydantic model for validating the structured response format."""
    content: str = Field(..., description="The content of the message")
    is_final: bool = Field(
        default=False, 
        description="Whether this is the final response after executing necessary tool calls"
    )

    def __str__(self) -> str:
        """String representation returns the content."""
        return self.content

    def __getitem__(self, key):
        """Support for string slicing operations."""
        return self.content[key]
    
    def __len__(self) -> int:
        """Support for len() operation."""
        return len(self.content)

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
    model: str = "o3-mini",
    max_iterations: int = 10
) -> StructuredResponse:
    """Execute a conversation with tool calling capabilities with iteration limits."""
    
    # Add system message to enforce JSON structure if not present
    if not any("JSON" in str(msg.get("content", "")) for msg in messages if msg["role"] == "system"):
        messages.insert(0, {
            "role": "system",
            "content": "You must respond with JSON that matches this structure: {\"content\": string, \"is_final\": boolean}. The content field should contain your message, and is_final should be true only when you have completed all necessary tool calls and have a final answer."
        })

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        response_format={ "type": "json_object" }
    )

    choice = response.choices[0]
    logger.info(f"[DH] Choice: \n{choice}")
    
    # Parse and validate the structured output
    try:
        if choice.message.content:
            structured_response = StructuredResponse.model_validate_json(choice.message.content)
        else:
            structured_response = StructuredResponse(content="", is_final=False)
    except Exception as e:
        logger.warning(f"Failed to parse structured response: {e}")
        # Fallback to legacy format
        structured_response = StructuredResponse(
            content=choice.message.content or "",
            is_final='Final Answer:' in (choice.message.content or "")
        )
    
    assistant_message: ChatCompletionAssistantMessageParam = {
        "role": "assistant",
        "content": str(structured_response.content),
    }
    
    if choice.message.tool_calls:
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
        messages = await handle_tool_calls(choice.message.tool_calls, messages)
        return await execute_conversation_with_tools(
            client, messages, tools, model, max_iterations - 1
        )
    
    if structured_response.is_final:
        return structured_response.content

    if max_iterations <= 0:
        return StructuredResponse(
            content=structured_response.content,
            is_final=True
        )
    
    if max_iterations == 1:
        messages.append({
            "role": "system",
            "content": "WARNING: Maximum iterations approaching. You MUST provide a Final Answer with is_final: true in your response on this turn."
        })
    return await execute_conversation_with_tools(
        client, messages, tools, model, max_iterations - 1
    )
    
function_map = {
    "create_task_on_todoist": create_task,
    "execute_insert": insert,
    "execute_update": update,
    "execute_query": query,
    "execute_delete": delete,
    "web_search": web_search,
    "schedule_interaction": schedule_interaction,
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
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Detailed explanation of why this tool was chosen and how it helps achieve the goal. Include what data/tables you're querying, any specific fields or conditions being used, and why this approach helps fulfill the user's request."
                    }
                },
                "required": ["query_string", "reasoning"]
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
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Detailed explanation of why this tool was chosen and how it helps achieve the goal. Include what data you're inserting, which table it's going into, and why this insertion is necessary for the user's request."
                    }
                },
                "required": ["insert_statement", "values", "reasoning"]
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
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Detailed explanation of why this tool was chosen and how it helps achieve the goal. Include what data you're updating, which table and fields are being modified, and why this update is necessary for the user's request."
                    }
                },
                "required": ["update_statement", "values", "reasoning"]
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
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Detailed explanation of why this tool was chosen and how it helps achieve the goal. Include what data you're deleting, from which table, and why this deletion is necessary for the user's request."
                    }
                },
                "required": ["delete_statement", "values", "reasoning"]
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
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Detailed explanation of why this tool was chosen and how it helps achieve the goal. Include what information you're searching for, why it needs to be up-to-date, and how this search will help answer the user's request."
                    }
                },
                "required": ["query", "reasoning"]
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
                    "description": {
                        "type": "string",
                        "description": "Description of the task",
                    },
                    "due_string": {
                        "type": "string",
                        "description": "The due date of the task in natural language (e.g., 'tomorrow at 2pm').",
                    },
                    "priority": {
                        "type": "number",
                        "description": "The priority of the task (1-4, with 1 being the highest).",
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Detailed explanation of why this tool was chosen and how it helps achieve the goal. Include why you're creating this task, why you chose the specific priority and due date, and how this task creation helps fulfill the user's needs."
                    }
                },
                "required": ["content", "description", "due_string", "priority", "reasoning"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "schedule_interaction",
            "description": "Schedule a message to be sent at a specific time. The message can be any interaction like a web search, task creation, or general conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "The message or interaction to schedule"
                    },
                    "day": {
                        "type": "string",
                        "description": "The day to schedule the interaction (YYYY-MM-DD format). If not provided, defaults to today",
                    },
                    "hour": {
                        "type": "integer",
                        "description": "The hour to schedule the interaction (0-23)",
                        "minimum": 0,
                        "maximum": 23
                    },
                    "minute": {
                        "type": "integer",
                        "description": "The minute to schedule the interaction (0-59)",
                        "minimum": 0,
                        "maximum": 59
                    },
                    "reasoning": {
                        "type": "string",
                        "description": "Detailed explanation of why this tool was chosen and how it helps achieve the goal. Include why this interaction needs to be scheduled, why you chose the specific time, and how this scheduling helps fulfill the user's needs."
                    }
                },
                "required": ["message", "reasoning"]
            }
        }
    }
]

import asyncio
from openai import OpenAI
import os
import json
from dotenv import load_dotenv
from app.core.ai.tools.common import execute_conversation_with_tools
from app.core.ai.tools.sql_tool import query, insert, get_schema_info, update

load_dotenv()

tools = [
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
    }
]

async def agent_response(message, message_history=None):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    schema_info = get_schema_info()
    
    example_values = json.dumps([{"name": "John", "email": "john@example.com"}])
    system_prompt = f"""
    You are a SQL expert assistant. Use these database schema details to construct queries:
    The database is a Postgres database with the following tables and columns:
    {json.dumps(schema_info, indent=2)}
    
    Important rules for SQL operations:
    - For INSERT or UPDATE operations, always use parameterized queries with named parameters
    - The values for INSERT or UPDATE must be provided as a list containing a dictionary of parameters
    - Example insert: 
      insert_statement: "INSERT INTO users (name, email) VALUES (:name, :email)"
      values: {example_values}
    - Example update: 
      update_statement: "UPDATE users SET email = :email WHERE name = :name"
      values: {example_values}
    - For SELECT operations, use the execute_query function
    - Don't need to ask to execute, always execute the statement using the appropriate tool
    - Explain query results in natural language!
    - If some value is not provided but it's required, fill it using you best guess
    """
    
    messages = [{"role": "system", "content": system_prompt}]
    if message_history:
        messages.extend(message_history)
    messages.append({"role": "user", "content": message})
    
    response = await execute_conversation_with_tools(
        client=client,
        messages=messages,
        tools=tools,
        model="gpt-4o"
    )
    return response.choices[0].message.content

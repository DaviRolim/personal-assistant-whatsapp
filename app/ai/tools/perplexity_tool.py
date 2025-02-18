import os
from typing import Any, Dict, Optional

import httpx
from dotenv import load_dotenv

from .tool_logging import log_tool_execution, setup_tool_logger

# Set up logger for this tool
logger = setup_tool_logger("perplexity")

load_dotenv()

async def web_search(reasoning: str, query: str, max_results: Optional[int] = 3) -> Dict[str, Any]:
    """
    Perform a web search using the Perplexity API.
    
    Args:
        reasoning (str): Explanation for why this web search is needed
        query (str): The search query
        max_results (Optional[int]): Maximum number of results to return (default: 3)
        
    Returns:
        Dict containing search results or error message
    """
    log_tool_execution(
        logger=logger,
        tool_name="perplexity_web_search",
        reasoning=reasoning,
        query=query,
        max_results=max_results
    )
    
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        return {
            "success": False,
            "message": "PERPLEXITY_API_KEY environment variable not found"
        }

    headers = {
        "Authorization": f"Bearer {api_key}",
        "accept": "application/json",
        "content-type": "application/json",
    }

    data = {
        "model": "sonar",  # Using the correct model name
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that performs web searches."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "max_tokens": 1024,
        "temperature": 0.7,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                log_tool_execution(
                    logger=logger,
                    tool_name="perplexity_web_search",
                    reasoning="Search completed successfully",
                    status="success",
                    content_length=len(result["choices"][0]["message"]["content"])
                )
                return {
                    "success": True,
                    "results": result["choices"][0]["message"]["content"]
                }
            else:
                log_tool_execution(
                    logger=logger,
                    tool_name="perplexity_web_search",
                    reasoning="API request failed",
                    status="error",
                    status_code=response.status_code,
                    error_message=response.text
                )
                return {
                    "success": False,
                    "message": f"API request failed with status {response.status_code}: {response.text}"
                }
                
    except Exception as e:
        log_tool_execution(
            logger=logger,
            tool_name="perplexity_web_search",
            reasoning="Exception during web search",
            status="error",
            error_message=str(e)
        )
        return {
            "success": False,
            "message": f"Error performing web search: {str(e)}"
        }
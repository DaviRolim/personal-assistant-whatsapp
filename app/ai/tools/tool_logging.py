import json
import logging
from typing import Any


def setup_tool_logger(tool_name: str) -> logging.Logger:
    """
    Set up a logger for a specific tool.
    
    Args:
        tool_name (str): Name of the tool
        
    Returns:
        logging.Logger: Configured logger for the tool
    """
    logger = logging.getLogger(f"tool.{tool_name}")
    logger.setLevel(logging.INFO)
    
    # Only add handler if the logger doesn't already have one
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def log_tool_execution(logger: logging.Logger, tool_name: str, reasoning: str, **kwargs: Any) -> None:
    """
    Log tool execution information in a consistent JSON format.
    
    Args:
        logger (logging.Logger): The logger to use
        tool_name (str): Name of the tool being executed
        reasoning (str): Reason for tool execution
        **kwargs: Additional key-value pairs to include in the log
    """
    log_data = {
        "tool": tool_name,
        "reasoning": reasoning,
        **kwargs
    }
    logger.info(f"[DH] Tool Execution: {json.dumps(log_data, default=str)}") 
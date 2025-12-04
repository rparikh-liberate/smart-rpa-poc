"""
Utility helper functions
"""
import json
from typing import Any, Dict


def format_json(data: Any, indent: int = 2) -> str:
    """
    Format data as pretty-printed JSON
    
    Args:
        data: Data to format
        indent: Number of spaces for indentation
        
    Returns:
        Formatted JSON string
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def truncate_string(text: str, max_length: int = 100) -> str:
    """
    Truncate a string to a maximum length
    
    Args:
        text: String to truncate
        max_length: Maximum length
        
    Returns:
        Truncated string with ellipsis if needed
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_error(error: Exception) -> Dict[str, Any]:
    """
    Format an exception as a dictionary
    
    Args:
        error: Exception to format
        
    Returns:
        Dictionary with error details
    """
    return {
        "type": type(error).__name__,
        "message": str(error),
        "details": getattr(error, 'args', ())
    }


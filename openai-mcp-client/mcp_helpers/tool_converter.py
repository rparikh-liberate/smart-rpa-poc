"""
Tool Converter - Converts MCP tools to OpenAI function format
"""
from typing import List, Dict, Any
from utils.logger import setup_logger

logger = setup_logger("mcp.tool_converter")


class ToolConverter:
    """
    Converts MCP tool schemas to OpenAI function calling format
    """
    
    @staticmethod
    def mcp_to_openai(mcp_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Convert MCP tools to OpenAI function format
        
        Args:
            mcp_tools: List of MCP tool definitions
            
        Returns:
            List of OpenAI-compatible function definitions
        """
        openai_tools = []
        
        for tool in mcp_tools:
            try:
                input_schema = tool.get("inputSchema", {
                    "type": "object",
                    "properties": {},
                    "required": []
                })
                
                # Fix schema: ensure all properties are in required array or have defaults
                properties = input_schema.get("properties", {})
                required = input_schema.get("required", [])
                
                # Add all properties to required if they don't have defaults
                if properties:
                    for prop_name, prop_schema in properties.items():
                        # If property doesn't have a default and isn't already required, add it
                        if "default" not in prop_schema and prop_name not in required:
                            required.append(prop_name)
                    
                    # Update the schema
                    input_schema["required"] = required
                
                openai_tool = {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"] or f"Execute {tool['name']}",
                        "parameters": input_schema
                    }
                }
                
                openai_tools.append(openai_tool)
                
            except Exception as e:
                logger.warning(f"Failed to convert tool {tool.get('name', 'unknown')}: {e}")
                continue
        
        logger.debug(f"Converted {len(openai_tools)} tools to OpenAI format")
        return openai_tools
    
    @staticmethod
    def extract_tool_call_info(tool_call: Any) -> Dict[str, Any]:
        """
        Extract tool call information from OpenAI response
        
        Args:
            tool_call: OpenAI tool call object
            
        Returns:
            Dictionary with tool call details
        """
        return {
            "id": tool_call.id,
            "name": tool_call.function.name,
            "arguments": tool_call.function.arguments
        }
    
    @staticmethod
    def format_tool_result(tool_call_id: str, result: Any) -> Dict[str, Any]:
        """
        Format tool execution result for OpenAI
        
        Args:
            tool_call_id: ID of the tool call
            result: Tool execution result
            
        Returns:
            Formatted result for OpenAI
        """
        # Extract content from MCP result
        content = ""
        
        if hasattr(result, 'content'):
            # MCP result object
            if isinstance(result.content, list):
                # Multiple content items
                content = "\n".join([
                    item.text if hasattr(item, 'text') else str(item)
                    for item in result.content
                ])
            else:
                content = str(result.content)
        else:
            # Plain result
            content = str(result)
        
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "content": content
        }


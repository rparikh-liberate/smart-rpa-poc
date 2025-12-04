"""
Tool Execution - Handles executing MCP tools via OpenAI tool calls
"""
import json
from typing import Dict, Any, List
from mcp_helpers.manager import MCPManager
from mcp_helpers.tool_converter import ToolConverter
from utils.logger import setup_logger

logger = setup_logger("openai_agent.tools")


class ToolExecutor:
    """
    Executes MCP tools based on OpenAI tool calls
    """
    
    def __init__(self, mcp_manager: MCPManager):
        """
        Initialize tool executor
        
        Args:
            mcp_manager: MCP manager instance
        """
        self.mcp_manager = mcp_manager
        self.converter = ToolConverter()
    
    async def execute_tool_call(self, tool_call: Any) -> Dict[str, Any]:
        """
        Execute a single tool call
        
        Args:
            tool_call: OpenAI tool call object
            
        Returns:
            Formatted tool result for OpenAI
        """
        # Extract tool call information
        info = self.converter.extract_tool_call_info(tool_call)
        tool_name = info["name"]
        tool_call_id = info["id"]
        
        # Parse arguments
        try:
            arguments = json.loads(info["arguments"])
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse arguments for {tool_name}: {e}")
            return self.converter.format_tool_result(
                tool_call_id,
                {"error": f"Invalid arguments: {e}"}
            )
        
        # Execute the tool via MCP
        try:
            logger.info(f"🔧 Executing tool: {tool_name}")
            logger.debug(f"Arguments: {arguments}")
            
            result = await self.mcp_manager.call_tool(tool_name, arguments)
            
            logger.info(f"✅ Tool {tool_name} executed successfully")
            
            # Format result for OpenAI
            return self.converter.format_tool_result(tool_call_id, result)
            
        except Exception as e:
            logger.error(f"❌ Tool {tool_name} failed: {e}")
            return self.converter.format_tool_result(
                tool_call_id,
                {"error": str(e)}
            )
    
    async def execute_tool_calls(self, tool_calls: List[Any]) -> List[Dict[str, Any]]:
        """
        Execute multiple tool calls
        
        Args:
            tool_calls: List of OpenAI tool call objects
            
        Returns:
            List of formatted tool results
        """
        results = []
        
        for tool_call in tool_calls:
            result = await self.execute_tool_call(tool_call)
            results.append(result)
        
        return results


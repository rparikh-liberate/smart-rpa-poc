"""
MCP Client - Connects to a single MCP server via stdio
"""
import asyncio
import json
from typing import List, Dict, Any, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from utils.logger import setup_logger

logger = setup_logger("mcp.client")


class MCPClient:
    """
    Client for connecting to a single MCP server
    """
    
    def __init__(self, name: str, command: str, args: List[str]):
        """
        Initialize MCP client
        
        Args:
            name: Name of the MCP server
            command: Command to run the server
            args: Arguments for the command
        """
        self.name = name
        self.command = command
        self.args = args
        self.session: Optional[ClientSession] = None
        self._exit_stack: Optional[AsyncExitStack] = None
        self.tools: List[Dict[str, Any]] = []
        
    async def connect(self) -> None:
        """Connect to the MCP server"""
        try:
            logger.info(f"Connecting to {self.name} MCP server...")
            
            # Create server parameters
            server_params = StdioServerParameters(
                command=self.command,
                args=self.args
            )
            
            # Use AsyncExitStack to manage context
            self._exit_stack = AsyncExitStack()
            await self._exit_stack.__aenter__()
            
            # Connect via stdio
            read, write = await self._exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            
            # Create and enter session context
            self.session = await self._exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            
            # Initialize the session
            await self.session.initialize()
            
            # List available tools
            await self.list_tools()
            
            logger.info(f"✅ Connected to {self.name} ({len(self.tools)} tools)")
            
        except Exception as e:
            logger.error(f"Failed to connect to {self.name}: {e}")
            if self._exit_stack:
                await self._exit_stack.__aexit__(None, None, None)
            raise
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from this server
        
        Returns:
            List of tool definitions
        """
        if not self.session:
            raise RuntimeError(f"{self.name} client not connected")
        
        try:
            response = await self.session.list_tools()
            self.tools = [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.inputSchema,
                    "server": self.name  # Tag with server name
                }
                for tool in response.tools
            ]
            return self.tools
            
        except Exception as e:
            logger.error(f"Failed to list tools from {self.name}: {e}")
            raise
    
    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call a tool on this server
        
        Args:
            name: Tool name
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        if not self.session:
            raise RuntimeError(f"{self.name} client not connected")
        
        try:
            logger.debug(f"Calling {name} on {self.name} with args: {arguments}")
            
            result = await self.session.call_tool(name, arguments)
            
            logger.debug(f"Tool {name} result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Failed to call tool {name} on {self.name}: {e}")
            raise
    
    async def close(self) -> None:
        """Close the connection to the MCP server"""
        if self._exit_stack:
            try:
                await self._exit_stack.__aexit__(None, None, None)
                logger.info(f"Closed connection to {self.name}")
            except Exception as e:
                logger.error(f"Error closing {self.name}: {e}")
        
        self.session = None
        self._exit_stack = None


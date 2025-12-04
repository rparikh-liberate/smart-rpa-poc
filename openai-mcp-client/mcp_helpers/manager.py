"""
MCP Manager - Manages multiple MCP clients
"""
from typing import Dict, List, Any, Optional
from mcp_helpers.client import MCPClient
from config import Config
from utils.logger import setup_logger

logger = setup_logger("mcp.manager")


class MCPManager:
    """
    Manages multiple MCP clients and routes tool calls appropriately
    """
    
    def __init__(self):
        """Initialize MCP manager"""
        self.clients: Dict[str, MCPClient] = {}
        self.all_tools: List[Dict[str, Any]] = []
        
    async def initialize(self) -> None:
        """Initialize all MCP clients"""
        server_configs = Config.get_mcp_servers()
        
        for name, config in server_configs.items():
            try:
                client = MCPClient(
                    name=name,
                    command=config["command"],
                    args=config["args"]
                )
                await client.connect()
                self.clients[name] = client
                
            except Exception as e:
                logger.error(f"Failed to initialize {name} MCP: {e}")
                raise
        
        # Collect all tools from all servers
        await self.refresh_tools()
        
        logger.info(f"✅ MCP Manager initialized with {len(self.clients)} servers")
        logger.info(f"📦 Total tools available: {len(self.all_tools)}")
    
    async def refresh_tools(self) -> List[Dict[str, Any]]:
        """
        Refresh and merge tools from all servers
        
        Returns:
            List of all available tools
        """
        self.all_tools = []
        
        for name, client in self.clients.items():
            tools = await client.list_tools()
            self.all_tools.extend(tools)
            logger.debug(f"Loaded {len(tools)} tools from {name}")
        
        return self.all_tools
    
    def get_all_tools(self) -> List[Dict[str, Any]]:
        """
        Get all available tools
        
        Returns:
            List of all tools from all servers
        """
        return self.all_tools
    
    def find_tool_server(self, tool_name: str) -> Optional[str]:
        """
        Find which server provides a specific tool
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Server name or None if not found
        """
        for tool in self.all_tools:
            if tool["name"] == tool_name:
                return tool["server"]
        return None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Route and execute a tool call to the appropriate server
        
        Args:
            tool_name: Name of the tool to call
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        # Find which server has this tool
        server_name = self.find_tool_server(tool_name)
        
        if not server_name:
            raise ValueError(f"Tool '{tool_name}' not found in any server")
        
        client = self.clients.get(server_name)
        if not client:
            raise RuntimeError(f"Server '{server_name}' not initialized")
        
        logger.info(f"Executing {tool_name} on {server_name}")
        
        # Execute the tool
        result = await client.call_tool(tool_name, arguments)
        
        return result
    
    async def close_all(self) -> None:
        """Close all MCP client connections"""
        logger.info("Closing all MCP connections...")
        
        for name, client in self.clients.items():
            try:
                await client.close()
            except Exception as e:
                logger.error(f"Error closing {name}: {e}")
        
        self.clients.clear()
        self.all_tools.clear()
        logger.info("All MCP connections closed")
    
    def get_tools_by_server(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group tools by their server
        
        Returns:
            Dictionary mapping server names to their tools
        """
        tools_by_server: Dict[str, List[Dict[str, Any]]] = {}
        
        for tool in self.all_tools:
            server = tool["server"]
            if server not in tools_by_server:
                tools_by_server[server] = []
            tools_by_server[server].append(tool)
        
        return tools_by_server


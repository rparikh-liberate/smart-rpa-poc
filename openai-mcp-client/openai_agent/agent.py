"""
OpenAI Agent - Main agent orchestrating OpenAI + MCP integration
"""
from typing import List, Dict, Any, Optional
from mcp_helpers.manager import MCPManager
from mcp_helpers.tool_converter import ToolConverter
from openai_agent.chat import ChatHandler
from openai_agent.tools import ToolExecutor
from config import Config
from utils.logger import setup_logger

logger = setup_logger("openai_agent.agent")


class OpenAIAgent:
    """
    Main agent that orchestrates OpenAI and MCP interaction
    """
    
    def __init__(self):
        """Initialize the agent"""
        self.mcp_manager: Optional[MCPManager] = None
        self.chat_handler: Optional[ChatHandler] = None
        self.tool_executor: Optional[ToolExecutor] = None
        self.converter = ToolConverter()
        self.messages: List[Dict[str, Any]] = []
        self.max_iterations = Config.MAX_ITERATIONS  # Configurable via MAX_ITERATIONS env var (default: 40)
    
    async def initialize(self) -> None:
        """Initialize MCP connections and OpenAI client"""
        logger.info("🚀 Initializing OpenAI Agent...")
        
        # Initialize MCP manager
        self.mcp_manager = MCPManager()
        await self.mcp_manager.initialize()
        
        # Convert MCP tools to OpenAI format
        mcp_tools = self.mcp_manager.get_all_tools()
        openai_tools = self.converter.mcp_to_openai(mcp_tools)
        
        # Initialize chat handler with tools
        self.chat_handler = ChatHandler(openai_tools)
        
        # Initialize tool executor
        self.tool_executor = ToolExecutor(self.mcp_manager)
        
        logger.info("✅ OpenAI Agent initialized successfully")
        logger.info(f"📊 Available tools: {len(openai_tools)}")
    
    async def run(self, user_message: str, system_prompt: Optional[str] = None) -> str:
        """
        Run the agent with a user message
        
        Args:
            user_message: User's input message
            system_prompt: Optional system prompt
            
        Returns:
            Agent's final response
        """
        # Initialize conversation
        self.messages = []
        
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        logger.info(f"💭 User: {user_message}")
        logger.info(f"🔄 Max iterations set to: {self.max_iterations}")
        
        # Agentic loop
        for iteration in range(self.max_iterations):
            logger.debug(f"🔄 Iteration {iteration + 1}/{self.max_iterations}")
            
            # Get completion from OpenAI
            response = self.chat_handler.create_completion(self.messages)
            
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            
            # Add assistant message to history
            assistant_msg = {
                "role": "assistant",
                "content": message.content
            }
            
            # Check if there are tool calls
            if message.tool_calls:
                assistant_msg["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in message.tool_calls
                ]
            
            self.messages.append(assistant_msg)
            
            # If no tool calls, we're done
            if not message.tool_calls:
                final_response = message.content or ""
                logger.info(f"🤖 Assistant: {final_response}")
                return final_response
            
            # Execute tool calls
            logger.info(f"🔧 Executing {len(message.tool_calls)} tool call(s)...")
            
            tool_results = await self.tool_executor.execute_tool_calls(message.tool_calls)
            
            # Add tool results to messages
            self.messages.extend(tool_results)
            
            # Check if we should continue
            if finish_reason == "stop":
                break
        
        # If we hit max iterations, return last message
        logger.warning(f"⚠️ Hit maximum iterations ({self.max_iterations})")
        return self.messages[-1].get("content", "Max iterations reached")
    
    async def stream_run(self, user_message: str, system_prompt: Optional[str] = None):
        """
        Run the agent with streaming output
        
        Args:
            user_message: User's input message
            system_prompt: Optional system prompt
            
        Yields:
            Response chunks
        """
        # Initialize conversation
        self.messages = []
        
        if system_prompt:
            self.messages.append({
                "role": "system",
                "content": system_prompt
            })
        
        self.messages.append({
            "role": "user",
            "content": user_message
        })
        
        yield f"💭 **User:** {user_message}\n\n"
        
        # For simplicity, streaming with tool calls is complex
        # We'll do a simple non-tool-calling stream here
        # For full implementation, you'd need to handle tool calls differently
        
        accumulated_content = ""
        
        for chunk in self.chat_handler.stream_completion(self.messages):
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                accumulated_content += content
                yield content
        
        yield "\n"
    
    async def close(self) -> None:
        """Clean up resources"""
        if self.mcp_manager:
            await self.mcp_manager.close_all()
        logger.info("👋 Agent shut down")
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history
        
        Returns:
            List of messages
        """
        return self.messages.copy()
    
    def clear_history(self) -> None:
        """Clear conversation history"""
        self.messages = []
        logger.debug("Cleared conversation history")


"""
Chat Module - Handles OpenAI chat completions
"""
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config import Config
from utils.logger import setup_logger

logger = setup_logger("openai_agent.chat")


class ChatHandler:
    """
    Handles OpenAI chat completions with function calling
    """
    
    def __init__(self, tools: List[Dict[str, Any]]):
        """
        Initialize chat handler
        
        Args:
            tools: List of OpenAI-formatted tools
        """
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.tools = tools
        
        logger.info(f"Initialized OpenAI client with model: {self.model}")
        logger.info(f"Loaded {len(self.tools)} tools for function calling")
    
    def create_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Any:
        """
        Create a chat completion
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Chat completion response
        """
        try:
            logger.debug(f"Creating completion with {len(messages)} messages")
            
            # Build request parameters
            request_params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
            }
            
            # Add tools if available
            if self.tools:
                request_params["tools"] = self.tools
                request_params["tool_choice"] = "auto"
            
            # Only add max_tokens if explicitly set (some models don't accept None)
            if max_tokens is not None:
                request_params["max_tokens"] = max_tokens
            
            response = self.client.chat.completions.create(**request_params)
            
            logger.debug(f"Completion created: {response.id}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to create completion: {e}")
            raise
    
    def stream_completion(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.7
    ):
        """
        Stream a chat completion
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            
        Yields:
            Completion chunks
        """
        try:
            logger.debug(f"Streaming completion with {len(messages)} messages")
            
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools if self.tools else None,
                tool_choice="auto" if self.tools else None,
                temperature=temperature,
                stream=True
            )
            
            for chunk in stream:
                yield chunk
                
        except Exception as e:
            logger.error(f"Failed to stream completion: {e}")
            raise
    
    def update_tools(self, tools: List[Dict[str, Any]]) -> None:
        """
        Update available tools
        
        Args:
            tools: New list of OpenAI-formatted tools
        """
        self.tools = tools
        logger.info(f"Updated tools: {len(self.tools)} tools available")


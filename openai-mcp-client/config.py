"""
Configuration management for OpenAI MCP Client
"""
import os
import json
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Application configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    # Options: gpt-4o (best), gpt-4o-mini (cheaper), gpt-4o-2024-11-20 (pinned version)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # MCP Server Configurations
    PLAYWRIGHT_MCP_CMD: str = os.getenv("PLAYWRIGHT_MCP_CMD", "npx")
    PLAYWRIGHT_MCP_ARGS: List[str] = json.loads(
        os.getenv("PLAYWRIGHT_MCP_ARGS", '["@playwright/mcp@latest"]')
    )
    
    WORKFLOWS_MCP_CMD: str = os.getenv("WORKFLOWS_MCP_CMD", "node")
    WORKFLOWS_MCP_ARGS: List[str] = json.loads(
        os.getenv(
            "WORKFLOWS_MCP_ARGS", 
            '["/Users/rparikh/codebases/mcp-browser-use/custom-mcp-server/server.js"]'
        )
    )
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Agent Configuration
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "40"))
    
    # Playwright Configuration
    PLAYWRIGHT_HEADLESS: bool = os.getenv("PLAYWRIGHT_HEADLESS", "false").lower() == "true"
    PLAYWRIGHT_ISOLATED: bool = os.getenv("PLAYWRIGHT_ISOLATED", "true").lower() == "true"  # Fresh session each time (Lambda-like)
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required. Please set it in .env file")
    
    @classmethod
    def get_mcp_servers(cls) -> Dict[str, Dict[str, Any]]:
        """Get MCP server configurations"""
        playwright_args = cls.PLAYWRIGHT_MCP_ARGS.copy()
        if cls.PLAYWRIGHT_HEADLESS:
            playwright_args.append("--headless")
        if cls.PLAYWRIGHT_ISOLATED:
            playwright_args.append("--isolated")
        
        return {
            "playwright": {
                "command": cls.PLAYWRIGHT_MCP_CMD,
                "args": playwright_args
            },
            "workflows": {
                "command": cls.WORKFLOWS_MCP_CMD,
                "args": cls.WORKFLOWS_MCP_ARGS
            }
        }


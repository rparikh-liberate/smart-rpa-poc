#!/usr/bin/env python3
"""
Main CLI - Entry point for OpenAI MCP Client
"""
import asyncio
import argparse
import sys
from typing import Optional
from config import Config
from openai_agent.agent import OpenAIAgent
from prompts import get_default_system_prompt, get_workflow_system_prompt
from utils.logger import setup_logger, logger as default_logger

logger = setup_logger("main")


async def run_single_query(query: str, system_prompt: Optional[str] = None) -> None:
    """
    Run a single query and exit
    
    Args:
        query: User's query
        system_prompt: Optional system prompt (defaults to standard prompt with knowledge base)
    """
    agent = OpenAIAgent()
    
    try:
        await agent.initialize()
        
        # Use default system prompt with knowledge base if none provided
        if system_prompt is None:
            system_prompt = get_default_system_prompt()
        
        response = await agent.run(query, system_prompt)
        
        print("\n" + "=" * 80)
        print("RESPONSE:")
        print("=" * 80)
        print(response)
        print("=" * 80 + "\n")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise
    finally:
        await agent.close()


async def run_interactive() -> None:
    """Run in interactive mode"""
    agent = OpenAIAgent()
    system_prompt = get_default_system_prompt()
    
    try:
        await agent.initialize()
        
        print("\n" + "=" * 80)
        print(" 🤖 OpenAI MCP Client - Interactive Mode")
        print("=" * 80)
        print("\nCommands:")
        print("  - Type your message and press Enter")
        print("  - 'clear' - Clear conversation history")
        print("  - 'history' - Show conversation history")
        print("  - 'tools' - List available tools")
        print("  - 'quit' or 'exit' - Exit the program")
        print("\n" + "=" * 80 + "\n")
        
        while True:
            try:
                user_input = input("\n💭 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                elif user_input.lower() == 'clear':
                    agent.clear_history()
                    print("✅ Conversation history cleared")
                    continue
                
                elif user_input.lower() == 'history':
                    history = agent.get_conversation_history()
                    print("\n📜 Conversation History:")
                    for i, msg in enumerate(history, 1):
                        role = msg.get('role', 'unknown')
                        content = msg.get('content', '')
                        print(f"\n{i}. [{role.upper()}]: {content[:200]}...")
                    continue
                
                elif user_input.lower() == 'tools':
                    tools_by_server = agent.mcp_manager.get_tools_by_server()
                    print("\n🛠️  Available Tools:")
                    for server, tools in tools_by_server.items():
                        print(f"\n  {server.upper()} ({len(tools)} tools):")
                        for tool in tools[:5]:  # Show first 5
                            print(f"    - {tool['name']}: {tool['description'][:60]}...")
                        if len(tools) > 5:
                            print(f"    ... and {len(tools) - 5} more")
                    continue
                
                # Process user query
                print("\n🤖 Assistant: ", end="", flush=True)
                
                response = await agent.run(user_input, system_prompt)
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 EOF. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"\n❌ Error: {e}")
    
    finally:
        await agent.close()


async def list_tools() -> None:
    """List all available tools"""
    agent = OpenAIAgent()
    
    try:
        await agent.initialize()
        
        tools_by_server = agent.mcp_manager.get_tools_by_server()
        
        print("\n" + "=" * 80)
        print(" 🛠️  AVAILABLE TOOLS")
        print("=" * 80 + "\n")
        
        for server, tools in tools_by_server.items():
            print(f"\n{server.upper()} Server ({len(tools)} tools):")
            print("-" * 80)
            
            for tool in tools:
                print(f"\n  📦 {tool['name']}")
                print(f"     {tool['description']}")
        
        print("\n" + "=" * 80 + "\n")
        
    finally:
        await agent.close()


async def run_example() -> None:
    """Run an example workflow"""
    print("\n" + "=" * 80)
    print(" 📋 EXAMPLE: Fetch and Execute REI Hiking Shoes Workflow")
    print("=" * 80 + "\n")
    
    query = "Execute the rei-hiking-shoes-v2 workflow"
    
    await run_single_query(
        query,
        system_prompt=get_workflow_system_prompt()
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="OpenAI MCP Client - AI-powered browser automation",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "query",
        nargs="?",
        help="Query to execute (omit for interactive mode)"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "-l", "--list-tools",
        action="store_true",
        help="List all available tools"
    )
    
    parser.add_argument(
        "-e", "--example",
        action="store_true",
        help="Run example workflow"
    )
    
    parser.add_argument(
        "-s", "--system-prompt",
        help="System prompt for the AI"
    )
    
    args = parser.parse_args()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Run appropriate mode
    try:
        if args.list_tools:
            asyncio.run(list_tools())
        
        elif args.example:
            asyncio.run(run_example())
        
        elif args.interactive or not args.query:
            asyncio.run(run_interactive())
        
        else:
            asyncio.run(run_single_query(args.query, args.system_prompt))
    
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


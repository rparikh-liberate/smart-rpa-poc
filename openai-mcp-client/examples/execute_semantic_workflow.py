"""
Example: Execute a semantic workflow
Demonstrates how to run deterministic browser automation without hardcoded refs
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp_helpers.manager import MCPManager
from workflow_executor import WorkflowExecutor
from config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    """Execute the REI hiking shoes workflow using semantic selectors."""
    
    # Initialize MCP connections
    mcp_manager = MCPManager()
    await mcp_manager.initialize()
    
    # Create workflow executor
    executor = WorkflowExecutor(mcp_manager)
    
    try:
        # Option 1: Load workflow from file
        logger.info("📁 Loading semantic workflow from file...")
        with open('../custom-mcp-server/workflows/rei-hiking-shoes-v2.json', 'r') as f:
            import json
            workflow = json.load(f)
        
        # Option 2: Load workflow from MCP server (if you add rei-hiking-shoes-v2.json to workflows/)
        # workflow = await executor.load_workflow("rei-hiking-shoes-v2")
        
        logger.info(f"🚀 Executing workflow: {workflow['name']}")
        logger.info(f"   Description: {workflow['description']}")
        logger.info(f"   Steps: {len(workflow['steps'])}")
        
        # Execute the workflow
        result = await executor.execute_workflow(workflow)
        
        # Print results
        logger.info("\n" + "="*80)
        logger.info("✅ WORKFLOW EXECUTION COMPLETE")
        logger.info("="*80)
        logger.info(f"Workflow: {result['workflow']}")
        logger.info(f"Total steps: {result['total_steps']}")
        logger.info(f"Completed: {result['completed_steps']}")
        
        logger.info("\n📋 Execution Log:")
        for log_entry in result['log']:
            status_icon = "✅" if log_entry['status'] == 'success' else "❌"
            logger.info(f"  {status_icon} Step {log_entry['step']}: {log_entry['description']}")
            if log_entry['status'] == 'failed':
                logger.error(f"     Error: {log_entry['error']}")
        
        return result
        
    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {e}", exc_info=True)
        raise
    finally:
        await mcp_manager.close()


if __name__ == "__main__":
    asyncio.run(main())


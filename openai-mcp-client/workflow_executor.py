"""
Workflow Executor for Semantic Browser Automation
Translates high-level semantic workflows into Playwright MCP tool calls
"""

import json
import re
from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowExecutor:
    """
    Executes semantic workflows by translating them into MCP tool calls.
    
    Workflows describe WHAT to do (semantic) instead of WHERE to click (refs).
    The executor handles finding the right elements at runtime.
    """
    
    def __init__(self, mcp_manager):
        self.mcp_manager = mcp_manager
        self.current_snapshot = None
        self.execution_log = []
    
    async def load_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Load a workflow from the Workflows MCP server."""
        logger.info(f"Loading workflow: {workflow_name}")
        result = await self.mcp_manager.call_tool("workflow_fetch", {"workflowName": workflow_name})
        
        # Parse the workflow from the result
        # Note: The actual workflow JSON is embedded in the markdown response
        content = result.get("content", [{}])[0].get("text", "")
        
        # Extract JSON from markdown code block
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            workflow = json.loads(json_match.group(1))
            logger.info(f"Loaded workflow with {len(workflow.get('steps', []))} steps")
            return workflow
        else:
            raise ValueError(f"Could not parse workflow from result: {content[:200]}")
    
    async def execute_workflow(self, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a complete workflow.
        
        Returns execution summary with success/failure status.
        """
        logger.info(f"Executing workflow: {workflow['name']}")
        self.execution_log = []
        
        steps = workflow.get("steps", [])
        for step_data in steps:
            try:
                result = await self.execute_step(step_data)
                self.execution_log.append({
                    "step": step_data.get("step"),
                    "status": "success",
                    "description": step_data.get("description"),
                    "result": result
                })
                logger.info(f"Step {step_data.get('step')} completed: {step_data.get('description')}")
            except Exception as e:
                logger.error(f"Step {step_data.get('step')} failed: {e}")
                self.execution_log.append({
                    "step": step_data.get("step"),
                    "status": "failed",
                    "description": step_data.get("description"),
                    "error": str(e)
                })
                # Optionally continue or stop on error
                raise
        
        return {
            "workflow": workflow["name"],
            "total_steps": len(steps),
            "completed_steps": len([log for log in self.execution_log if log["status"] == "success"]),
            "log": self.execution_log
        }
    
    async def execute_step(self, step: Dict[str, Any]) -> Any:
        """
        Execute a single workflow step.
        
        Translates semantic descriptions into actual MCP tool calls.
        """
        action = step.get("action")
        
        if action == "navigate":
            return await self._navigate(step)
        elif action == "type":
            return await self._type(step)
        elif action == "click":
            return await self._click(step)
        elif action == "select":
            return await self._select(step)
        elif action == "select_option":
            return await self._select_option(step)
        elif action == "wait_for":
            return await self._wait_for(step)
        elif action == "verify":
            return await self._verify(step)
        elif action == "snapshot":
            return await self._snapshot()
        else:
            raise ValueError(f"Unknown action: {action}")
    
    async def _navigate(self, step: Dict[str, Any]) -> Any:
        """Navigate to a URL."""
        url = step["url"]
        logger.info(f"Navigating to {url}")
        result = await self.mcp_manager.call_tool("browser_navigate", {"url": url})
        
        # Update snapshot from navigation result
        await self._update_snapshot_from_result(result)
        return result
    
    async def _snapshot(self) -> Any:
        """Take a fresh snapshot."""
        logger.info("Taking page snapshot")
        result = await self.mcp_manager.call_tool("browser_snapshot", {})
        await self._update_snapshot_from_result(result)
        return result
    
    async def _type(self, step: Dict[str, Any]) -> Any:
        """Type text into an element."""
        target = step["target"]
        value = step["value"]
        submit = step.get("submit", False)
        
        # Find the element ref
        ref = await self._find_element_ref(target)
        
        logger.info(f"Typing '{value}' into {target['description']} [ref={ref}]")
        result = await self.mcp_manager.call_tool("browser_type", {
            "element": target["description"],
            "ref": ref,
            "text": value,
            "submit": submit
        })
        
        await self._update_snapshot_from_result(result)
        return result
    
    async def _click(self, step: Dict[str, Any]) -> Any:
        """Click an element."""
        target = step["target"]
        
        # Find the element ref
        ref = await self._find_element_ref(target)
        
        logger.info(f"Clicking {target['description']} [ref={ref}]")
        result = await self.mcp_manager.call_tool("browser_click", {
            "element": target["description"],
            "ref": ref
        })
        
        await self._update_snapshot_from_result(result)
        return result
    
    async def _select(self, step: Dict[str, Any]) -> Any:
        """Select/check an element (checkbox, radio)."""
        target = step["target"]
        
        # Find the element ref
        ref = await self._find_element_ref(target)
        
        logger.info(f"Selecting {target['description']} [ref={ref}]")
        result = await self.mcp_manager.call_tool("browser_click", {
            "element": target["description"],
            "ref": ref
        })
        
        await self._update_snapshot_from_result(result)
        return result
    
    async def _select_option(self, step: Dict[str, Any]) -> Any:
        """Select an option from a dropdown."""
        target = step["target"]
        option = step["option"]
        
        # Find the element ref
        ref = await self._find_element_ref(target)
        
        logger.info(f"Selecting option '{option}' in {target['description']} [ref={ref}]")
        result = await self.mcp_manager.call_tool("browser_select_option", {
            "element": target["description"],
            "ref": ref,
            "values": [option]
        })
        
        await self._update_snapshot_from_result(result)
        return result
    
    async def _wait_for(self, step: Dict[str, Any]) -> Any:
        """Wait for an element to appear."""
        target = step["target"]
        
        # Take snapshots until element appears (with retry logic)
        max_retries = 10
        for i in range(max_retries):
            await self._snapshot()
            try:
                ref = await self._find_element_ref(target)
                logger.info(f"Element {target['description']} appeared [ref={ref}]")
                return {"found": True, "ref": ref}
            except ValueError:
                if i < max_retries - 1:
                    logger.info(f"Waiting for {target['description']} (attempt {i+1}/{max_retries})")
                    await self.mcp_manager.call_tool("browser_wait_for", {"time": 1})
                else:
                    raise ValueError(f"Element {target['description']} did not appear after {max_retries} attempts")
    
    async def _verify(self, step: Dict[str, Any]) -> Any:
        """Verify an element exists."""
        target = step["target"]
        
        await self._snapshot()
        ref = await self._find_element_ref(target)
        logger.info(f"Verified {target['description']} exists [ref={ref}]")
        return {"verified": True, "ref": ref}
    
    async def _find_element_ref(self, target: Dict[str, Any]) -> str:
        """
        Find an element's ref based on semantic description.
        
        Target can contain:
        - role: ARIA role (button, link, checkbox, etc.)
        - name: Exact accessible name
        - name_contains: Name contains this string (case-insensitive)
        - name_pattern: Regex pattern for name
        - position: "first", "last", or index number
        - description: Human-readable description (for logging)
        """
        if not self.current_snapshot:
            await self._snapshot()
        
        # Parse the snapshot to find matching elements
        role = target.get("role")
        name = target.get("name")
        name_contains = target.get("name_contains")
        name_pattern = target.get("name_pattern")
        position = target.get("position")
        
        # Simple line-by-line parser
        # Format: "- role \"name\" [ref=eXXX] [other attrs]"
        matches = []
        
        for line in self.current_snapshot.split('\n'):
            line = line.strip()
            if not line.startswith('-'):
                continue
            
            # Extract role, name, and ref from the line
            # Example: - button "Search" [ref=e47] [cursor=pointer]
            match = re.match(r'-\s+(\w+)(?:\s+"([^"]*)")?\s+\[ref=([^\]]+)\]', line)
            if not match:
                continue
            
            line_role = match.group(1)
            line_name = match.group(2) or ""
            line_ref = match.group(3)
            
            # Check if role matches
            if role and line_role != role:
                continue
            
            # Check if name matches
            if name and line_name != name:
                continue
            
            if name_contains and name_contains.lower() not in line_name.lower():
                continue
            
            if name_pattern and not re.search(name_pattern, line_name, re.IGNORECASE):
                continue
            
            matches.append({
                "role": line_role,
                "name": line_name,
                "ref": line_ref,
                "line": line
            })
        
        if not matches:
            raise ValueError(
                f"Could not find element matching {target}. "
                f"Snapshot has {len(self.current_snapshot.split(chr(10)))} lines."
            )
        
        # Handle position
        if position == "first":
            return matches[0]["ref"]
        elif position == "last":
            return matches[-1]["ref"]
        elif isinstance(position, int):
            return matches[position]["ref"]
        else:
            # Default to first match
            return matches[0]["ref"]
    
    async def _update_snapshot_from_result(self, result: Any):
        """Extract and store the snapshot from an MCP tool result."""
        if isinstance(result, dict):
            content = result.get("content", [])
            for item in content:
                if item.get("type") == "text":
                    text = item.get("text", "")
                    # Look for snapshot in the text
                    # MCP returns snapshot in a specific format
                    if "- " in text and "[ref=" in text:
                        self.current_snapshot = text
                        logger.debug(f"Updated snapshot ({len(text)} chars)")
                        return




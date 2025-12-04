# Cursor Configuration Setup

## Overview

This Workflow MCP server works **alongside** Playwright MCP. You need BOTH:
1. **Playwright MCP** - For browser automation (navigate, click, type, etc.)
2. **Workflow MCP** - For saved workflows (workflow_fetch, workflow_list)

## Step 1: Open Cursor Settings

1. Open Cursor
2. Go to **Settings** (⌘+, on Mac, Ctrl+, on Windows/Linux)
3. Search for "MCP" in settings
4. Or navigate to: **Features** → **Model Context Protocol**

## Step 2: Configure BOTH MCP Servers

### Option A: UI Configuration

Add two servers:

**Server 1: Playwright**
- **Name:** `playwright`
- **Command:** `npx`
- **Args:** `@playwright/mcp@latest`

**Server 2: Workflows**
- **Name:** `workflows`
- **Command:** `node`
- **Args:** `/Users/rparikh/codebases/mcp-browser-use/custom-mcp-server/server.js`

### Option B: JSON Configuration

If editing the JSON directly (`~/.cursor/mcp.json`):

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp@latest"]
    },
    "workflows": {
      "command": "node",
      "args": ["/Users/rparikh/codebases/mcp-browser-use/custom-mcp-server/server.js"]
    }
  }
}
```

## Step 3: Keep Both Servers

**Important:** Do NOT remove Playwright MCP! You need both:
- Playwright provides browser control
- Workflows provides saved automation scripts

## Step 4: Restart Cursor

**Important:** You MUST restart Cursor completely for MCP changes to take effect.

1. Close all Cursor windows
2. Quit Cursor (⌘+Q on Mac, or File → Exit)
3. Reopen Cursor

## Step 5: Verify Both Servers Work

1. Open Cursor AI chat
2. Ask: "List available MCP tools"
3. You should see tools from BOTH servers:
   - **From Playwright MCP:** browser_navigate, browser_click, browser_type, browser_snapshot, etc.
   - **From Workflow MCP:** workflow_fetch, workflow_list

## Step 6: Test the Workflow Tools

### Test 1: List Workflows

Ask:
```
"List all available workflows"
```

Should call `workflow_list()` and show available workflows.

### Test 2: Fetch a Workflow

Ask:
```
"Fetch the rei-hiking-shoes workflow"
```

Should call `workflow_fetch("rei-hiking-shoes")` and display the steps.

### Test 3: Execute a Workflow

Ask:
```
"Use the REI hiking shoes workflow to buy shoes"
```

The AI should:
1. Call `workflow_fetch("rei-hiking-shoes")`
2. Get the workflow steps
3. Execute them using Playwright tools (browser_navigate, browser_click, etc.)

## Troubleshooting

### "MCP Server Failed to Start"

**Check:**
1. Is Node.js installed? Run `node --version` in terminal
2. Are dependencies installed? Check `custom-mcp-server/node_modules` exists
3. Is server.js executable? Run `ls -la server.js` - should show `-rwxr-xr-x`

**Fix:**
```bash
cd /Users/rparikh/codebases/mcp-browser-use/custom-mcp-server
npm install
chmod +x server.js
```

### "Tool Not Found"

1. Restart Cursor completely
2. Check MCP output panel in Cursor for errors
3. Verify the server path is absolute (not relative)

### "Browser Already in Use"

You can only run one Playwright MCP instance at a time.

1. Close all Cursor windows
2. Kill any existing node processes: `pkill -f "server.js"`
3. Restart Cursor

## Success Indicators

When working correctly, you'll see in Cursor's MCP output panel:

**For Workflow MCP:**
```
✅ Workflow MCP Server ready!
📦 Tools available:
   - workflow_fetch(workflowName)
   - workflow_list()

💡 Try: workflow_fetch("rei-hiking-shoes")
```

**For Playwright MCP:**
```
✅ Playwright MCP connected
📦 Browser tools available (21 tools)
```

Both servers should show as "Connected" in Cursor's MCP settings.

## Next Steps

Once configured:
1. Try the REI workflow
2. Create your own workflows in `workflows/` directory
3. Use `workflow_fetch` to replay saved automations

Enjoy your custom MCP server! 🎉


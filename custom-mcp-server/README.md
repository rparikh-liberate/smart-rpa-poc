# Workflow MCP Server

A standalone MCP server that provides workflow management tools. Use alongside Playwright MCP for full browser automation capabilities.

## Features

- `workflow_fetch` - Retrieve saved automation workflows
- `workflow_list` - List all available workflows
- `login_to_site` - Helper for login flows with credentials
- `workflow_record_start/stop` - Record new workflows
- Works alongside Playwright MCP

## Installation

Already installed! Dependencies are in place.

## Configuration

### For Cursor

You need to configure **BOTH** servers - Playwright MCP for browser automation AND this Workflow server for workflow management.

**File:** `~/.cursor/mcp.json` or Cursor Settings → MCP

**Configuration:**
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

### Restart Cursor

After updating the configuration, restart Cursor completely for changes to take effect.

## Usage

### Available Workflows

- `rei-hiking-shoes` - Automates finding and adding highest-rated men's hiking shoes (size 10) to REI cart

### Example

```
You: "Use the rei-hiking-shoes workflow to buy shoes"

AI will:
1. Call workflow_fetch("rei-hiking-shoes")
2. Get the step-by-step instructions
3. Execute each step using Playwright tools
4. Adapt to current page structure dynamically
```

### Adding New Workflows

Create a new JSON file in `workflows/` directory:

```json
{
  "name": "my-workflow",
  "description": "Description of what this does",
  "steps": [
    {
      "step": 1,
      "tool": "browser_navigate",
      "description": "Navigate somewhere",
      "arguments": {"url": "https://example.com"}
    }
  ]
}
```

Then use it: `workflow_fetch("my-workflow")`

## Tools

### workflow_fetch

Fetches a saved automation workflow.

**Parameters:**
- `workflowName` (string) - Name of the workflow file (without .json)

**Returns:**
- Formatted workflow with steps, descriptions, and notes
- Full JSON data for the LLM to execute

**Example:**
```javascript
workflow_fetch("rei-hiking-shoes")
```

### workflow_list

Lists all available saved workflows.

### login_to_site

Get complete login instructions with credentials for a specific website. Returns step-by-step guide to navigate, enter credentials, and verify login success.

**Parameters:**
- `site` (string) - Name of the site (e.g., "rei", "amazon")

### get_login_credentials

Retrieve stored login credentials for a specific website.

**Parameters:**
- `site` (string) - Name of the site

### workflow_record_start

Start recording a new workflow. All subsequent browser actions will be captured.

**Parameters:**
- `name` (string) - Name for the workflow
- `description` (string, optional) - Description of what the workflow does

### workflow_record_stop

Stop recording and save the workflow.

## Architecture

This server:
1. Runs alongside the official `@playwright/mcp` package
2. Adds custom tools (workflow_fetch, login helpers, recording)
3. Uses stdio transport for communication with Cursor

## Development

```bash
# Start server manually (for testing)
npm start

# Or with auto-reload
npm run dev
```

## Troubleshooting

### "Browser already in use" error

If you see this error, close Cursor completely and restart it. Only one MCP instance can control the browser at a time.

### Workflow not found

Make sure the workflow file exists in `workflows/` directory with the exact name (case-sensitive).

### Tool not showing up

1. Check Cursor MCP configuration
2. Restart Cursor completely
3. Check server logs in Cursor's MCP output panel


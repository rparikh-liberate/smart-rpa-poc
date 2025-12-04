# Quick Start Guide

## 🎯 What You Have

A custom MCP server that provides workflow management tools for browser automation.

## ⚡ Setup (2 minutes)

### 1. Open Cursor Settings

```
Settings → Model Context Protocol
```

### 2. Add These Two Servers

**Playwright MCP** (browser automation):
- Command: `npx`
- Args: `@playwright/mcp@latest`

**Workflow MCP** (this server):
- Command: `node`
- Args: `/Users/rparikh/codebases/mcp-browser-use/custom-mcp-server/server.js`

### 3. Restart Cursor

Completely quit and reopen Cursor.

### 4. Test It

In Cursor chat, ask:
```
"List workflows"
```

Should show `rei-hiking-shoes` workflow.

## 🚀 Use the REI Workflow

Ask Cursor:
```
"Use the REI hiking shoes workflow to buy size 10 men's hiking shoes"
```

Cursor will:
1. Fetch the workflow using `workflow_fetch("rei-hiking-shoes")`
2. Execute each step using Playwright tools
3. Add the highest-rated shoes to your REI cart

## 📁 File Structure

```
custom-mcp-server/
├── server.js                    ← MCP server (run this)
├── package.json                 ← Dependencies
├── workflows/                   ← Workflow storage
│   └── rei-hiking-shoes.json   ← REI automation
├── README.md                    ← Full documentation
├── CURSOR_SETUP.md              ← Detailed setup guide
└── IMPLEMENTATION_SUMMARY.md    ← Architecture & decisions
```

## 🛠️ Troubleshooting

### Server won't start?

```bash
cd custom-mcp-server
npm install
chmod +x server.js
node server.js  # Test manually
```

### Tools not showing?

1. Restart Cursor completely (Quit → Reopen)
2. Check MCP panel in Cursor for errors
3. Verify both servers are configured

### Workflow fails?

- REI's website may have changed
- The LLM adapts to current page structure
- If needed, the LLM will find new element refs

## 📚 Next Steps

### Add Your Own Workflow

1. Create `workflows/my-workflow.json`:
   ```json
   {
     "name": "my-workflow",
     "description": "What it does",
     "steps": [
       {
         "step": 1,
         "tool": "browser_navigate",
         "description": "Go somewhere",
         "arguments": {"url": "https://example.com"}
       }
     ]
   }
   ```

2. Use it:
   ```
   "Fetch and execute my-workflow"
   ```

### Extend the Server

See `IMPLEMENTATION_SUMMARY.md` for ideas:
- Add workflow_save tool
- Integrate with S3
- Add credential management

## 🎉 You're Done!

You now have:
- ✅ Workflow MCP server running
- ✅ REI hiking shoes workflow saved
- ✅ Custom tools available in Cursor
- ✅ Full browser automation + workflow management

For more details, see:
- **CURSOR_SETUP.md** - Detailed configuration
- **README.md** - Full usage guide
- **IMPLEMENTATION_SUMMARY.md** - Technical deep dive


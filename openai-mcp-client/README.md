# OpenAI MCP Client

A modular Python application that integrates OpenAI's GPT-4o with multiple MCP servers for AI-powered browser automation and workflow management.

## 🎯 Features

- ✅ **GPT-4o Integration** - Latest and most capable OpenAI model
- ✅ **Multi-MCP Support** - Connect to multiple MCP servers simultaneously
- ✅ **Browser Automation** - Full Playwright MCP integration
- ✅ **Workflow Management** - Save and replay automation workflows
- ✅ **Modular Architecture** - Clean, extensible codebase
- ✅ **Interactive CLI** - Chat interface with conversation history
- ✅ **Tool Chaining** - Automatic multi-step execution

## 🏗️ Architecture

```
┌────────────────────────────────────┐
│     OpenAI GPT-4o                  │
│     (AI Decision Making)           │
└─────────────┬──────────────────────┘
              │
    ┌─────────▼────────┐
    │   OpenAI Agent   │
    │   (main.py)      │
    └─────────┬────────┘
              │
    ┌─────────▼────────────┐
    │    MCP Manager       │
    │  (Multi-Server)      │
    └────┬─────────────┬───┘
         │             │
   ┌─────▼───┐   ┌────▼────────┐
   │Playwright│   │  Workflows  │
   │   MCP   │   │     MCP     │
   └─────┬───┘   └────┬────────┘
         │            │
    ┌────▼───┐   ┌───▼────────┐
    │Browser │   │ workflows/ │
    └────────┘   └────────────┘
```

## 📦 Project Structure

```
openai-mcp-client/
├── main.py                    # CLI entry point
├── config.py                  # Configuration management
├── requirements.txt           # Dependencies
├── mcp_helpers/
│   ├── __init__.py
│   ├── client.py             # Single MCP client
│   ├── manager.py            # Multi-server manager
│   └── tool_converter.py     # MCP→OpenAI format converter
├── openai_agent/
│   ├── __init__.py
│   ├── agent.py              # Main agent logic
│   ├── chat.py               # Chat completions
│   └── tools.py              # Tool execution
└── utils/
    ├── __init__.py
    ├── logger.py             # Logging setup
    └── helpers.py            # Utility functions
```

## 🚀 Setup

### 1. Prerequisites

- Python 3.9+
- OpenAI API key
- Node.js (for MCP servers)

### 2. Install Dependencies

```bash
cd openai-mcp-client

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the project directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL=gpt-4o

# MCP Paths (update paths as needed)
PLAYWRIGHT_MCP_CMD=npx
PLAYWRIGHT_MCP_ARGS=["@playwright/mcp@latest"]
WORKFLOWS_MCP_CMD=node
WORKFLOWS_MCP_ARGS=["/Users/rparikh/codebases/mcp-browser-use/custom-mcp-server/server.js"]

# Playwright Configuration
PLAYWRIGHT_HEADLESS=false  # Set to 'true' for headless mode (no visible browser UI)
PLAYWRIGHT_ISOLATED=true   # Set to 'true' for fresh sessions (no persistent cookies/cache)

# Agent Configuration
MAX_ITERATIONS=40  # Maximum iterations for the agentic loop

# Logging
LOG_LEVEL=INFO
```

**⚠️ Important:** Replace `/Users/rparikh/...` with your actual path!

**💡 Headless Mode:** Set `PLAYWRIGHT_HEADLESS=true` to run browser automation without a visible UI. This is useful for:
- Faster execution (no rendering overhead)
- Running in CI/CD environments
- Background automation tasks
- When visual feedback is not needed

**🔄 Session Management:** Control how browser sessions are handled:

**Isolated Mode (`PLAYWRIGHT_ISOLATED=true`, default):**
- ✅ Fresh session every time (Lambda-like behavior)
- ✅ No persistent cookies or sessions
- ✅ Browser profile stored in memory only
- ✅ Ideal for: Serverless/Lambda, CI/CD, testing
- ✅ Use when: You don't need to stay logged in

**Persistent Mode (`PLAYWRIGHT_ISOLATED=false`):**
- ✅ Saves session data to disk
- ✅ Preserves cookies and login state
- ✅ "Remember this device" works for MFA
- ✅ Ideal for: Authenticated workflows, avoiding repeated MFA
- ✅ Use when: You need to stay logged in across runs

**Profile Location (Persistent Mode):**
- macOS: `~/Library/Caches/ms-playwright/mcp-chromium-profile`
- Linux: `~/.cache/ms-playwright/mcp-chromium-profile`  
- Windows: `%USERPROFILE%\AppData\Local\ms-playwright\mcp-chromium-profile`

**🔐 Example Use Case: Progressive Insurance**
See custom-mcp-server documentation for progressive workflow examples.

### 4. Verify Setup

List available tools:

```bash
python main.py --list-tools
```

You should see tools from both Playwright and Workflows MCP servers.

## 💻 Usage

### Interactive Mode (Recommended)

```bash
python main.py --interactive
```

Commands:
- Type your message and press Enter
- `clear` - Clear conversation history
- `history` - Show conversation history
- `tools` - List available tools
- `quit` or `exit` - Exit the program

### Single Query Mode

```bash
python main.py "Navigate to google.com and search for hiking shoes"
```

### With System Prompt

```bash
python main.py "Execute the REI workflow" --system-prompt "You are a shopping assistant."
```

### List Tools

```bash
python main.py --list-tools
```

### Run Example

```bash
python main.py --example
```

## 📋 Example Workflows

### Example 1: List and Execute Workflow

**Interactive Mode:**

```
You: List available workflows
Assistant: (calls workflow_list tool and shows available workflows)

You: Execute the rei-hiking-shoes workflow
Assistant: (fetches workflow, then executes each step using browser tools)
```

### Example 2: Direct Browser Automation

```bash
python main.py "Navigate to google.com, search for 'python automation', and take a screenshot"
```

### Example 3: Multi-Step Task

```bash
python main.py "Go to rei.com, find hiking boots size 10, and add the top-rated one to cart"
```

### Example 4: Progressive Insurance (Persistent Sessions with MFA)

**First-time setup (manual MFA required):**
```bash
# Set persistent sessions in .env first:
# PLAYWRIGHT_ISOLATED=false
# PLAYWRIGHT_HEADLESS=false

python main.py "Execute the progressive-login workflow"
# ⚠️ Manually enter MFA code and check "Remember this device"
```

**Subsequent runs (no MFA needed):**
```bash
python main.py "Execute the progressive-id-card workflow"
# ✅ Uses saved session, downloads ID card PDF automatically
```

**Complete workflow:**
```bash
python main.py "Execute the progressive-full workflow"
# Login (if needed) → Get ID card → Save PDF
```

📚 See [custom-mcp-server/README.md](../custom-mcp-server/README.md) for more details.

## 🛠️ Available Tools

### From Playwright MCP (21 tools)

- `browser_navigate` - Navigate to URL
- `browser_click` - Click elements
- `browser_type` - Type text
- `browser_snapshot` - Get page accessibility tree
- `browser_select_option` - Select dropdown options
- `browser_take_screenshot` - Screenshot pages
- `browser_wait_for` - Wait for conditions
- And 14 more...

### From Workflows MCP (6 tools)

- `workflow_fetch` - Retrieve saved workflows
- `workflow_list` - List available workflows
- `login_to_site` - Helper for login flows
- `get_login_credentials` - Retrieve credentials
- `workflow_record_start` - Start recording
- `workflow_record_stop` - Stop recording

## 🔧 How It Works

### 1. Initialization

```python
agent = OpenAIAgent()
await agent.initialize()
# - Connects to both MCP servers
# - Lists all available tools
# - Converts MCP format to OpenAI format
# - Initializes GPT-4o client
```

### 2. Query Processing

```python
response = await agent.run("Your query here")
# - Sends query to GPT-4o with tool definitions
# - GPT-4o decides which tools to use
# - Tools are executed via MCP
# - Results are sent back to GPT-4o
# - Process repeats until task complete
```

### 3. Tool Execution Flow

```
User Query → GPT-4o → Tool Decision → MCP Client → Tool Execution → Result → GPT-4o → Response
```

## 📝 Configuration Details

### MCP Server Configuration

The `config.py` file manages MCP server configurations. To add a new MCP server:

1. Add environment variables:
```bash
MY_MCP_CMD=node
MY_MCP_ARGS=["/path/to/my-mcp-server.js"]
```

2. Update `Config.get_mcp_servers()` in `config.py`:
```python
"my_server": {
    "command": cls.MY_MCP_CMD,
    "args": cls.MY_MCP_ARGS
}
```

### GPT Model Configuration

Currently using **GPT-4o** (GPT-4 Omni):
- 128K context window
- Best function calling support
- Fastest response times
- Multimodal capabilities

To change model, update `.env`:
```bash
OPENAI_MODEL=gpt-4-turbo  # Alternative model
```

## 🐛 Troubleshooting

### Error: "OPENAI_API_KEY is required"

**Solution:** Create `.env` file with your API key:
```bash
OPENAI_API_KEY=sk-your-key-here
```

### Error: "Failed to connect to MCP server"

**Possible causes:**
1. MCP server path is incorrect
2. Node.js not installed
3. Dependencies not installed

**Solutions:**
```bash
# Check Node.js
node --version

# Update paths in .env file
# Ensure MCP servers are accessible
```

### Error: "Browser is already in use"

**Solution:** Close any existing Playwright browser sessions:
```bash
pkill -f "chrome.*playwright"
# Or restart your terminal
```

### Tool calls timing out

**Solution:** Increase max iterations in `agent.py`:
```python
self.max_iterations = 20  # Default is 10
```

## 📊 Performance

- **Initialization:** ~2-3 seconds (connects to both MCP servers)
- **Query Processing:** Variable (depends on GPT-4o and tool execution)
- **Tool Execution:** Near-instant for most operations
- **Browser Actions:** 1-5 seconds per action

## 🔐 Security

- API keys stored in `.env` file (git-ignored)
- MCP servers run as child processes
- Browser automation uses isolated profiles
- No data persistence between sessions

## 🚧 Limitations

1. **Max Iterations:** Limited to 10 by default (prevents infinite loops)
2. **Streaming:** Limited streaming support with tool calls
3. **Error Handling:** Tools may fail on dynamic websites
4. **Cost:** GPT-4o API calls cost money (monitor usage)

## 🤝 Contributing

This is a modular codebase. To extend:

1. **Add new MCP servers:** Update `config.py`
2. **Add new tools:** They auto-register via MCP
3. **Customize agent:** Modify `openai_agent/agent.py`
4. **Add CLI commands:** Update `main.py`

## 📚 Additional Resources

- [OpenAI API Docs](https://platform.openai.com/docs)
- [MCP Protocol](https://modelcontextprotocol.io)
- [Playwright MCP](https://github.com/microsoft/playwright-mcp)

## 📄 License

See parent project license.

## 🎉 Quick Start

```bash
# 1. Setup
cd openai-mcp-client
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure (create .env with your API key)
echo 'OPENAI_API_KEY=sk-your-key' > .env

# 3. Run
python main.py --interactive

# 4. Try it!
You: List available workflows
You: Execute the rei-hiking-shoes workflow
```

---

**Built with ❤️ using GPT-4o, MCP, and Python**

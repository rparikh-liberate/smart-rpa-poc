#!/usr/bin/env node

/**
 * Workflow MCP Server
 * Provides workflow_fetch tool to retrieve saved automation workflows
 * Use alongside Playwright MCP for full functionality
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  ListToolsRequestSchema, 
  CallToolRequestSchema 
} from '@modelcontextprotocol/sdk/types.js';
import { readFile, readdir, writeFile } from 'fs/promises';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { recorder } from './tools/workflow-recorder.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const WORKFLOWS_DIR = join(__dirname, 'workflows');
const CREDENTIALS_FILE = join(__dirname, 'credentials.json');

// ============================================================
// Credentials Management
// ============================================================

async function getLoginCredentials(site) {
  try {
    const data = await readFile(CREDENTIALS_FILE, 'utf-8');
    const credentials = JSON.parse(data);
    
    if (!credentials[site]) {
      const availableSites = Object.keys(credentials);
      throw new Error(
        `No credentials found for: ${site}\n\n` +
        `Available sites:\n${availableSites.map(s => `  - ${s}`).join('\n')}`
      );
    }
    
    console.error(`✅ Retrieved credentials for: ${site}`);
    
    // Support both "username" and "email" fields
    const username = credentials[site].username || credentials[site].email;
    const fieldLabel = credentials[site].username ? 'Username' : 'Email';
    
    return {
      content: [{
        type: 'text',
        text: `# Login Credentials: ${site}\n\n` +
              `**${fieldLabel}:** ${username}\n` +
              `**Password:** ${credentials[site].password}\n` +
              `**Notes:** ${credentials[site].notes || 'N/A'}\n\n` +
              `**Usage:**\n` +
              `1. Navigate to login page\n` +
              `2. Use browser_type to enter username/email: ${username}\n` +
              `3. Use browser_type to enter password\n` +
              `4. Click submit/login button\n\n` +
              `**Security Note:** Keep credentials.json private and never commit to git!`
      }]
    };
  } catch (error) {
    if (error.code === 'ENOENT') {
      throw new Error(
        `Credentials file not found at: ${CREDENTIALS_FILE}\n\n` +
        `Create credentials.json with format:\n` +
        `{\n` +
        `  "site-name": {\n` +
        `    "username": "user@example.com",  // or "email": "user@example.com"\n` +
        `    "password": "password",\n` +
        `    "loginUrl": "https://example.com/login",\n` +
        `    "notes": "Optional notes"\n` +
        `  }\n` +
        `}`
      );
    }
    throw new Error(`Failed to get credentials: ${error.message}`);
  }
}

async function loginToSite(site) {
  try {
    // Read credentials
    const data = await readFile(CREDENTIALS_FILE, 'utf-8');
    const credentials = JSON.parse(data);
    
    if (!credentials[site]) {
      const availableSites = Object.keys(credentials);
      throw new Error(
        `No credentials found for: ${site}\n\n` +
        `Available sites:\n${availableSites.map(s => `  - ${s}`).join('\n')}`
      );
    }
    
    // Support both "username" and "email" fields
    const username = credentials[site].username || credentials[site].email;
    const password = credentials[site].password;
    const loginUrl = credentials[site].loginUrl;
    
    if (!username) {
      throw new Error(
        `No username/email found in credentials for ${site}.\n\n` +
        `Please add "username" or "email" to credentials.json:\n` +
        `{\n` +
        `  "${site}": {\n` +
        `    "username": "...",  // or "email": "..."\n` +
        `    "password": "...",\n` +
        `    "loginUrl": "https://www.${site}.com/login"\n` +
        `  }\n` +
        `}`
      );
    }
    
    if (!loginUrl) {
      throw new Error(
        `No loginUrl configured for ${site}.\n\n` +
        `Please add "loginUrl" to credentials.json:\n` +
        `{\n` +
        `  "${site}": {\n` +
        `    "username": "...",\n` +
        `    "password": "...",\n` +
        `    "loginUrl": "https://www.${site}.com/login"\n` +
        `  }\n` +
        `}`
      );
    }
    
    console.error(`🔐 Preparing login instructions for: ${site}`);
    
    return {
      content: [{
        type: 'text',
        text: `# Login to ${site.toUpperCase()}\n\n` +
              `## Credentials Retrieved:\n` +
              `- Username/Email: ${username}\n` +
              `- Password: [REDACTED]\n` +
              `- Login URL: ${loginUrl}\n\n` +
              `## Login Instructions:\n` +
              `Follow these steps to complete login:\n\n` +
              `**Important:** Look for fields labeled "username", "email", "user", or "login" in the snapshot.\n` +
              `Use the provided credentials regardless of the field label.\n\n` +
              `### Step 1: Navigate to Login Page\n` +
              `\`\`\`json\n` +
              `{\n` +
              `  "tool": "browser_navigate",\n` +
              `  "arguments": {\n` +
              `    "url": "${loginUrl}"\n` +
              `  }\n` +
              `}\n` +
              `\`\`\`\n\n` +
              `### Step 2: Take Snapshot\n` +
              `\`\`\`json\n` +
              `{\n` +
              `  "tool": "browser_snapshot",\n` +
              `  "arguments": {}\n` +
              `}\n` +
              `\`\`\`\n` +
              `Find refs for username/email textbox, password textbox, and login/signin button.\n\n` +
              `### Step 3: Enter Username/Email\n` +
              `Use the username: ${username}\n` +
              `\`\`\`json\n` +
              `{\n` +
              `  "tool": "browser_type",\n` +
              `  "arguments": {\n` +
              `    "element": "Username/Email textbox",\n` +
              `    "ref": "{{USERNAME_EMAIL_REF}}",\n` +
              `    "text": "${username}",\n` +
              `    "submit": false\n` +
              `  }\n` +
              `}\n` +
              `\`\`\`\n` +
              `Note: The field might be labeled as "username", "email", "user", or "login" - use whichever appears in the snapshot.\n\n` +
              `### Step 4: Enter Password\n` +
              `\`\`\`json\n` +
              `{\n` +
              `  "tool": "browser_type",\n` +
              `  "arguments": {\n` +
              `    "element": "Password textbox",\n` +
              `    "ref": "{{PASSWORD_REF}}",\n` +
              `    "text": "${password}",\n` +
              `    "submit": false\n` +
              `  }\n` +
              `}\n` +
              `\`\`\`\n\n` +
              `### Step 5: Click Login Button\n` +
              `\`\`\`json\n` +
              `{\n` +
              `  "tool": "browser_click",\n` +
              `  "arguments": {\n` +
              `    "element": "Sign in button",\n` +
              `    "ref": "{{LOGIN_BUTTON_REF}}"\n` +
              `  }\n` +
              `}\n` +
              `\`\`\`\n\n` +
              `### Step 6: Verify Login Success\n` +
              `\`\`\`json\n` +
              `{\n` +
              `  "tool": "browser_snapshot",\n` +
              `  "arguments": {}\n` +
              `}\n` +
              `\`\`\`\n` +
              `Check the snapshot to confirm you're logged in (look for user name, account menu, or "Sign Out" link).\n\n` +
              `---\n\n` +
              `**Note:** Replace {{EMAIL_REF}}, {{PASSWORD_REF}}, and {{LOGIN_BUTTON_REF}} with actual refs from Step 2 snapshot.\n\n` +
              `**Security:** Credentials are retrieved from secure storage. Never log passwords.`
      }]
    };
  } catch (error) {
    throw new Error(`Failed to prepare login: ${error.message}`);
  }
}

// ============================================================
// Workflow Tools
// ============================================================

async function workflowFetch(workflowName) {
  const workflowPath = join(WORKFLOWS_DIR, `${workflowName}.json`);
  
  try {
    const data = await readFile(workflowPath, 'utf-8');
    const workflow = JSON.parse(data);
    
    console.error(`✅ Fetched workflow: ${workflow.name}`);
    
    return {
      content: [{
        type: 'text',
        text: `# Workflow: ${workflow.name}\n\n` +
              `**Description:** ${workflow.description}\n\n` +
              `**Steps:** ${workflow.steps.length}\n\n` +
              `## Workflow Steps\n\n` +
              workflow.steps.map(step => 
                `### Step ${step.step}: ${step.description}\n` +
                `- **Tool:** \`${step.tool}\`\n` +
                `- **Arguments:** \`\`\`json\n${JSON.stringify(step.arguments || {}, null, 2)}\n\`\`\`\n` +
                (step.note ? `- **Note:** ${step.note}\n` : '') +
                `\n`
              ).join('') +
              `\n## Success Criteria\n\n` +
              (workflow.successCriteria || []).map(c => `- ${c}`).join('\n') +
              `\n\n## Implementation Notes\n\n` +
              (workflow.notes || []).map(n => `- ${n}`).join('\n') +
              `\n\n---\n\n` +
              `**To execute this workflow:**\n` +
              `1. Take snapshots to find current element refs\n` +
              `2. Execute each step using the Playwright browser tools\n` +
              `3. Adapt refs (like {{SEARCH_INPUT_REF}}) based on current page\n` +
              `4. Verify success criteria at the end\n\n` +
              `**Full workflow JSON:**\n\`\`\`json\n${JSON.stringify(workflow, null, 2)}\n\`\`\``
      }]
    };
  } catch (error) {
    if (error.code === 'ENOENT') {
      // List available workflows
      try {
        const files = await readdir(join(__dirname, 'workflows'));
        const workflows = files.filter(f => f.endsWith('.json')).map(f => f.replace('.json', ''));
        throw new Error(
          `Workflow not found: ${workflowName}\n\n` +
          `Available workflows:\n${workflows.map(w => `  - ${w}`).join('\n')}`
        );
      } catch {
        throw new Error(`Workflow not found: ${workflowName}`);
      }
    }
    throw new Error(`Failed to fetch workflow: ${error.message}`);
  }
}

// ============================================================
// List available workflows
// ============================================================

async function workflowList() {
  try {
    const workflowsDir = join(__dirname, 'workflows');
    const files = await readdir(workflowsDir);
    const workflowFiles = files.filter(f => f.endsWith('.json'));
    
    const workflows = await Promise.all(
      workflowFiles.map(async (file) => {
        try {
          const data = await readFile(join(workflowsDir, file), 'utf-8');
          const workflow = JSON.parse(data);
          return {
            name: workflow.name,
            description: workflow.description,
            steps: workflow.steps.length,
            file: file
          };
        } catch (error) {
          return {
            name: file.replace('.json', ''),
            description: 'Error loading workflow',
            steps: 0,
            file: file
          };
        }
      })
    );
    
    return {
      content: [{
        type: 'text',
        text: `# Available Workflows\n\n` +
              `Found ${workflows.length} workflow(s):\n\n` +
              workflows.map((w, i) => 
                `## ${i + 1}. ${w.name}\n` +
                `- **Description:** ${w.description}\n` +
                `- **Steps:** ${w.steps}\n` +
                `- **File:** \`${w.file}\`\n` +
                `\nTo use: \`workflow_fetch("${w.name.replace('rei-hiking-shoes-purchase', 'rei-hiking-shoes')}")\`\n`
              ).join('\n')
      }]
    };
  } catch (error) {
    throw new Error(`Failed to list workflows: ${error.message}`);
  }
}

async function workflowRecordStart(name, description) {
  recorder.startRecording(name);
  return {
    content: [{
      type: 'text',
      text: `📹 **Recording Started**\n\n` +
            `Workflow: ${name}\n` +
            `Description: ${description || 'Auto-generated workflow'}\n\n` +
            `**What happens now:**\n` +
            `- All browser actions will be recorded\n` +
            `- Refs will be converted to semantic selectors automatically\n` +
            `- Use \`workflow_record_stop()\` when done\n\n` +
            `**Tip:** Perform the actions you want to automate now!`
    }]
  };
}

async function workflowRecordStop() {
  if (!recorder.isRecording()) {
    return {
      content: [{
        type: 'text',
        text: `❌ **Not Recording**\n\nNo workflow recording in progress. Use \`workflow_record_start(name)\` to start.`
      }]
    };
  }

  const filePath = await recorder.saveWorkflow(WORKFLOWS_DIR);
  const workflow = recorder.generateWorkflow();
  
  return {
    content: [{
      type: 'text',
      text: `⏹️  **Recording Stopped**\n\n` +
            `Workflow: ${workflow.name}\n` +
            `Steps recorded: ${workflow.steps.length}\n` +
            `Saved to: ${filePath}\n\n` +
            `**Steps:**\n` +
            workflow.steps.map(s => `${s.step}. ${s.description}`).join('\n') +
            `\n\n**To use this workflow:**\n` +
            `\`workflow_fetch("${workflow.name}")\`\n\n` +
            `**Workflow JSON:**\n\`\`\`json\n${JSON.stringify(workflow, null, 2)}\n\`\`\``
    }]
  };
}

async function workflowRecordAction(action, params) {
  if (!recorder.isRecording()) return;

  // Record different action types
  if (action === 'navigate') {
    recorder.recordNavigate(params.url);
  } else if (action === 'click') {
    recorder.recordClick(params.element, params.ref);
  } else if (action === 'type') {
    recorder.recordType(params.element, params.ref, params.text, params.submit);
  } else if (action === 'select_option') {
    recorder.recordSelectOption(params.element, params.ref, params.values);
  } else if (action === 'snapshot') {
    recorder.recordSnapshot(params.snapshot);
  }
}

// ============================================================
// Create MCP Server
// ============================================================

async function main() {
  console.error('🚀 Starting Workflow MCP Server...');
  
  const server = new Server(
    {
      name: 'workflow-mcp',
      version: '1.0.0'
    },
    {
      capabilities: {
        tools: {}
      }
    }
  );

  // ============================================================
  // Handle: tools/list
  // ============================================================
  
  server.setRequestHandler(ListToolsRequestSchema, async () => {
    return {
      tools: [
        {
          name: 'login_to_site',
          description: 'Get complete login instructions with credentials for a specific website. Returns step-by-step guide to navigate, enter credentials, and verify login success. This is a modular login helper that workflows can call instead of implementing login steps manually.',
          inputSchema: {
            type: 'object',
            properties: {
              site: {
                type: 'string',
                description: 'Name of the site to login to (e.g., "rei", "amazon")'
              }
            },
            required: ['site']
          }
        },
        {
          name: 'get_login_credentials',
          description: 'Retrieve stored login credentials for a specific website. Returns email and password that can be used with browser automation tools.',
          inputSchema: {
            type: 'object',
            properties: {
              site: {
                type: 'string',
                description: 'Name of the site to get credentials for (e.g., "rei", "amazon")'
              }
            },
            required: ['site']
          }
        },
        {
          name: 'workflow_fetch',
          description: 'Fetch a saved automation workflow with detailed step-by-step instructions. Returns the workflow definition that can be executed using Playwright MCP tools.',
          inputSchema: {
            type: 'object',
            properties: {
              workflowName: {
                type: 'string',
                description: 'Name of the workflow to fetch (e.g., "rei-hiking-shoes")'
              }
            },
            required: ['workflowName']
          }
        },
        {
          name: 'workflow_list',
          description: 'List all available saved workflows',
          inputSchema: {
            type: 'object',
            properties: {},
            required: []
          }
        },
        {
          name: 'workflow_record_start',
          description: 'Start recording a new workflow. All subsequent browser actions will be captured and converted to semantic selectors automatically.',
          inputSchema: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'Name for the workflow (e.g., "amazon-add-to-cart")'
              },
              description: {
                type: 'string',
                description: 'Optional description of what this workflow does'
              }
            },
            required: ['name']
          }
        },
        {
          name: 'workflow_record_stop',
          description: 'Stop recording the current workflow and save it. Returns the generated workflow with semantic selectors.',
          inputSchema: {
            type: 'object',
            properties: {},
            required: []
          }
        }
      ]
    };
  });

  // ============================================================
  // Handle: tools/call
  // ============================================================
  
  server.setRequestHandler(CallToolRequestSchema, async (request) => {
    const { name, arguments: args } = request.params;
    
    if (name === 'login_to_site') {
      return await loginToSite(args.site);
    }
    
    if (name === 'get_login_credentials') {
      return await getLoginCredentials(args.site);
    }
    
    if (name === 'workflow_fetch') {
      return await workflowFetch(args.workflowName);
    }
    
    if (name === 'workflow_list') {
      return await workflowList();
    }
    
    if (name === 'workflow_record_start') {
      return await workflowRecordStart(args.name, args.description);
    }
    
    if (name === 'workflow_record_stop') {
      return await workflowRecordStop();
    }
    
    throw new Error(`Unknown tool: ${name}`);
  });

  // ============================================================
  // Start Server
  // ============================================================
  
  const transport = new StdioServerTransport();
  await server.connect(transport);
  
  console.error('✅ Workflow MCP Server ready!');
  console.error('📦 Tools available:');
  console.error('   - login_to_site(site) - Modular login helper (recommended)');
  console.error('   - get_login_credentials(site) - Get credentials only');
  console.error('   - workflow_fetch(workflowName)');
  console.error('   - workflow_list()');
  console.error('');
  console.error('💡 Use alongside Playwright MCP for full automation');
  console.error('💡 Try: login_to_site("rei")');
  console.error('💡 Try: workflow_fetch("rei-hiking-shoes-modular")');
}

// ============================================================
// Start
// ============================================================

main().catch((error) => {
  console.error('❌ Error starting server:', error);
  process.exit(1);
});

import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';

const CONNECT_TIMEOUT = 30_000;

const SERVER_CONFIGS = {
  ga4: {
    command: '/Users/user/.local/bin/analytics-mcp',
    args: [],
    env: {}
  },
  'meta-ads': {
    command: '/Users/user/projects/genactiv-klaviyo/venv/bin/python',
    args: ['-m', 'meta_ads_mcp'],
    env: {
      META_ACCESS_TOKEN: process.env.META_ACCESS_TOKEN || ''
    }
  },
  'google-ads': {
    command: '/Users/user/projects/genactiv-klaviyo/google-ads-mcp/google-ads-mcp-server/venv/bin/fastmcp',
    args: ['run', '/Users/user/projects/genactiv-klaviyo/google-ads-mcp/google-ads-mcp-server/server.py'],
    cwd: '/Users/user/projects/genactiv-klaviyo/google-ads-mcp/google-ads-mcp-server',
    env: {
      GOOGLE_ADS_DEVELOPER_TOKEN: process.env.GOOGLE_ADS_DEVELOPER_TOKEN || '',
      GOOGLE_ADS_OAUTH_CONFIG_PATH: process.env.GOOGLE_ADS_OAUTH_CONFIG_PATH || '',
      GOOGLE_ADS_LOGIN_CUSTOMER_ID: process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID || ''
    }
  },
  klaviyo: {
    command: 'uvx',
    args: ['--with', 'fastmcp>=2.8.0,<3.0.0', 'klaviyo-mcp-server@0.4.0'],
    env: {
      PRIVATE_API_KEY: process.env.KLAVIYO_API_KEY || '',
      READ_ONLY: 'false',
      ALLOW_USER_GENERATED_CONTENT: 'true'
    }
  }
};

// Cached connections: serverName → { client, transport }
const connections = new Map();

async function getConnection(serverName) {
  if (connections.has(serverName)) {
    return connections.get(serverName);
  }

  const config = SERVER_CONFIGS[serverName];
  if (!config) {
    throw new Error(`Unknown MCP server: ${serverName}`);
  }

  console.log(`[MCP] Connecting to ${serverName}...`);

  const transport = new StdioClientTransport({
    command: config.command,
    args: config.args,
    cwd: config.cwd,
    env: { ...process.env, ...config.env }
  });

  const client = new Client({
    name: `dashboard-${serverName}`,
    version: '1.0.0'
  });

  // Connect with timeout
  const connectPromise = client.connect(transport);
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Connection to ${serverName} timed out (${CONNECT_TIMEOUT}ms)`)), CONNECT_TIMEOUT)
  );

  await Promise.race([connectPromise, timeoutPromise]);
  console.log(`[MCP] Connected to ${serverName}`);

  connections.set(serverName, { client, transport });
  return { client, transport };
}

export async function callTool(serverName, toolName, args) {
  const { client } = await getConnection(serverName);

  const result = await client.callTool({ name: toolName, arguments: args });

  // Parse JSON from content[].text
  if (result.content && result.content.length > 0) {
    const text = result.content.map(c => c.text || '').join('');
    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }
  return result;
}

export async function shutdownAll() {
  for (const [name, { client, transport }] of connections) {
    try {
      console.log(`[MCP] Shutting down ${name}...`);
      await client.close();
    } catch (err) {
      console.error(`[MCP] Error closing ${name}:`, err.message);
    }
  }
  connections.clear();
  console.log('[MCP] All connections closed');
}

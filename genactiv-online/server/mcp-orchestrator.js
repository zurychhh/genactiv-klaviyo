import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { mcpServers, CONNECT_TIMEOUT, TOOL_CACHE_TTL, TOOL_RESULT_MAX_CHARS, TOOL_DESCRIPTION_MAX_CHARS } from './config.js';

const connections = new Map();
let toolCache = null;

async function connectServer(serverConfig) {
  const { name, command, args, env, cwd } = serverConfig;
  console.log(`[MCP] Connecting to ${name}...`);

  const transport = new StdioClientTransport({
    command, args, cwd,
    env: { ...process.env, ...env }
  });

  const client = new Client({ name: `genactiv-online-${name}`, version: '1.0.0' });

  const connectPromise = client.connect(transport);
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Connection to ${name} timed out`)), CONNECT_TIMEOUT)
  );

  await Promise.race([connectPromise, timeoutPromise]);
  console.log(`[MCP] Connected to ${name}`);
  connections.set(name, { client, transport });
  return { client, transport };
}

export async function connectAll() {
  const results = await Promise.allSettled(
    mcpServers.map(config => connectServer(config))
  );
  results.forEach((result, i) => {
    if (result.status === 'rejected') {
      console.error(`[MCP] Failed to connect to ${mcpServers[i].name}:`, result.reason.message);
    }
  });
  const connected = results.filter(r => r.status === 'fulfilled').length;
  console.log(`[MCP] ${connected}/${mcpServers.length} servers connected`);
  return connected;
}

/**
 * Strip bloat from input_schema: remove examples, defaults, deep descriptions.
 */
function compressSchema(schema) {
  if (!schema || typeof schema !== 'object') return schema;

  const result = {};
  for (const [key, value] of Object.entries(schema)) {
    if (key === 'examples' || key === 'default' || key === '$schema') continue;
    if (key === 'description' && typeof value === 'string' && value.length > 80) {
      result[key] = value.slice(0, 80);
      continue;
    }
    if (key === 'properties' && typeof value === 'object') {
      result[key] = {};
      for (const [propName, propValue] of Object.entries(value)) {
        result[key][propName] = compressSchema(propValue);
      }
      continue;
    }
    if (key === 'items' && typeof value === 'object') {
      result[key] = compressSchema(value);
      continue;
    }
    result[key] = value;
  }
  return result;
}

export async function getAllTools() {
  if (toolCache && Date.now() - toolCache.timestamp < TOOL_CACHE_TTL) {
    return toolCache;
  }

  const tools = [];
  const serverMap = new Map();

  for (const [serverName, { client }] of connections) {
    try {
      const result = await client.listTools();
      for (const tool of result.tools) {
        const prefixedName = `mcp__${serverName}__${tool.name}`;

        let desc = tool.description || '';
        if (desc.length > TOOL_DESCRIPTION_MAX_CHARS) {
          desc = desc.slice(0, TOOL_DESCRIPTION_MAX_CHARS);
        }

        const schema = compressSchema(tool.inputSchema) || { type: 'object', properties: {} };

        tools.push({
          name: prefixedName,
          description: desc,
          input_schema: schema
        });

        serverMap.set(prefixedName, { serverName, originalName: tool.name });
      }
    } catch (err) {
      console.error(`[MCP] Error listing tools from ${serverName}:`, err.message);
    }
  }

  toolCache = { tools, serverMap, timestamp: Date.now() };
  console.log(`[MCP] Cached ${tools.length} tools from ${connections.size} servers`);
  return toolCache;
}

export function getToolsForServer(serverName) {
  if (!toolCache) return { tools: [], serverMap: new Map() };
  const filtered = toolCache.tools.filter(t => {
    const mapping = toolCache.serverMap.get(t.name);
    return mapping && mapping.serverName === serverName;
  });
  return { tools: filtered, serverMap: toolCache.serverMap };
}

/**
 * Strip nulls and empty strings from JSON results. Keep structure intact.
 */
function compressResult(obj) {
  if (obj === null || obj === undefined || obj === '') return undefined;
  if (typeof obj !== 'object') return obj;

  if (Array.isArray(obj)) {
    return obj.map(item => compressResult(item)).filter(v => v !== undefined);
  }

  const result = {};
  for (const [key, value] of Object.entries(obj)) {
    const compressed = compressResult(value);
    if (compressed !== undefined) {
      result[key] = compressed;
    }
  }
  return Object.keys(result).length > 0 ? result : undefined;
}

export async function callTool(prefixedToolName, args) {
  const { serverMap } = await getAllTools();
  const mapping = serverMap.get(prefixedToolName);

  if (!mapping) throw new Error(`Unknown tool: ${prefixedToolName}`);

  const { serverName, originalName } = mapping;
  const connection = connections.get(serverName);
  if (!connection) throw new Error(`Server ${serverName} not connected`);

  console.log(`[MCP] Calling ${serverName}.${originalName}`);
  const result = await connection.client.callTool({
    name: originalName,
    arguments: args
  });

  if (result.content && result.content.length > 0) {
    let text = result.content.map(c => c.text || '').join('');

    // Try to compress JSON results
    try {
      const parsed = JSON.parse(text);
      const compressed = compressResult(parsed);
      text = JSON.stringify(compressed);
    } catch {
      // not JSON, keep as-is
    }

    if (text.length > TOOL_RESULT_MAX_CHARS) {
      console.log(`[MCP] Truncating ${serverName}.${originalName}: ${text.length} → ${TOOL_RESULT_MAX_CHARS}`);
      text = text.slice(0, TOOL_RESULT_MAX_CHARS) + '\n[Wynik skrócony]';
    }

    try {
      return JSON.parse(text);
    } catch {
      return text;
    }
  }
  return result;
}

export async function shutdownAll() {
  for (const [name, { client }] of connections) {
    try {
      console.log(`[MCP] Shutting down ${name}...`);
      await client.close();
    } catch (err) {
      console.error(`[MCP] Error closing ${name}:`, err.message);
    }
  }
  connections.clear();
  toolCache = null;
  console.log('[MCP] All connections closed');
}

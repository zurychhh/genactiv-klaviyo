import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { mcpServers, CONNECT_TIMEOUT, TOOL_CACHE_TTL, TOOL_RESULT_MAX_CHARS, TOOL_DESCRIPTION_MAX_CHARS, TOOL_CALL_TIMEOUT } from './config.js';

const connections = new Map();
let toolCache = null;
let staleCache = null; // Fix 8: fallback cache
const connectionErrors = new Map(); // Fix 11: error tracking
const reconnecting = new Set(); // Fix 7: prevent race conditions

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
  connections.set(name, { client, transport, config: serverConfig });
  connectionErrors.delete(name);
  return { client, transport };
}

// Fix 7: Reconnection with exponential backoff
async function reconnectServer(serverConfig) {
  const { name } = serverConfig;
  if (reconnecting.has(name)) return false;
  reconnecting.add(name);

  const delays = [2000, 4000, 8000, 16000, 32000];

  for (let attempt = 0; attempt < delays.length; attempt++) {
    try {
      console.log(`[MCP] Reconnecting to ${name} (attempt ${attempt + 1}/${delays.length})...`);

      // Clean up old connection
      const old = connections.get(name);
      if (old) {
        try { await old.client.close(); } catch {}
        connections.delete(name);
      }

      await connectServer(serverConfig);
      console.log(`[MCP] Reconnected to ${name}`);
      reconnecting.delete(name);
      // Invalidate tool cache to pick up reconnected server
      toolCache = null;
      return true;
    } catch (err) {
      console.error(`[MCP] Reconnect attempt ${attempt + 1} for ${name} failed: ${err.message}`);
      connectionErrors.set(name, err.message);
      if (attempt < delays.length - 1) {
        await new Promise(r => setTimeout(r, delays[attempt]));
      }
    }
  }

  reconnecting.delete(name);
  console.error(`[MCP] All reconnect attempts for ${name} exhausted`);
  return false;
}

export async function connectAll() {
  const results = await Promise.allSettled(
    mcpServers.map(config => connectServer(config))
  );
  results.forEach((result, i) => {
    if (result.status === 'rejected') {
      console.error(`[MCP] Failed to connect to ${mcpServers[i].name}:`, result.reason.message);
      connectionErrors.set(mcpServers[i].name, result.reason.message);
    }
  });
  const connected = results.filter(r => r.status === 'fulfilled').length;
  console.log(`[MCP] ${connected}/${mcpServers.length} servers connected`);
  return connected;
}

// Fix 4: Connection status for health check
export function getConnectionStatus() {
  const servers = {};
  for (const config of mcpServers) {
    const connected = connections.has(config.name);
    servers[config.name] = {
      connected,
      error: connectionErrors.get(config.name) || null
    };
  }
  return {
    connected: connections.size,
    total: mcpServers.length,
    servers
  };
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

  // Fix 8: Save as stale cache before updating
  if (tools.length > 0) {
    toolCache = { tools, serverMap, timestamp: Date.now() };
    staleCache = toolCache;
    console.log(`[MCP] Cached ${tools.length} tools from ${connections.size} servers`);
  } else if (staleCache) {
    console.warn(`[MCP] Tool refresh returned 0 tools — serving stale cache (${staleCache.tools.length} tools)`);
    return staleCache;
  } else {
    toolCache = { tools: [], serverMap: new Map(), timestamp: Date.now() };
    console.warn('[MCP] No tools available and no stale cache');
  }

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
  let connection = connections.get(serverName);

  // Fix 7: Try reconnect if not connected
  if (!connection) {
    const config = mcpServers.find(c => c.name === serverName);
    if (config) {
      console.log(`[MCP] ${serverName} not connected, attempting reconnect before tool call...`);
      const success = await reconnectServer(config);
      if (success) {
        connection = connections.get(serverName);
      }
    }
    if (!connection) throw new Error(`Server ${serverName} not connected`);
  }

  console.log(`[MCP] Calling ${serverName}.${originalName}`);

  // Fix 9: Tool call timeout
  const toolPromise = connection.client.callTool({
    name: originalName,
    arguments: args
  });
  const timeoutPromise = new Promise((_, reject) =>
    setTimeout(() => reject(new Error(`Tool call ${serverName}.${originalName} timed out after ${TOOL_CALL_TIMEOUT / 1000}s`)), TOOL_CALL_TIMEOUT)
  );

  let result;
  try {
    result = await Promise.race([toolPromise, timeoutPromise]);
  } catch (err) {
    // Fix 7: On connection error, fire-and-forget reconnect
    if (err.message?.includes('closed') || err.message?.includes('EPIPE') || err.message?.includes('not connected')) {
      const config = mcpServers.find(c => c.name === serverName);
      if (config) {
        reconnectServer(config).catch(() => {}); // fire-and-forget
      }
    }
    throw err;
  }

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

    // Fix 12: Better truncation warning
    if (text.length > TOOL_RESULT_MAX_CHARS) {
      const originalLength = text.length;
      console.log(`[MCP] Truncating ${serverName}.${originalName}: ${originalLength} → ${TOOL_RESULT_MAX_CHARS}`);
      text = text.slice(0, TOOL_RESULT_MAX_CHARS)
        + `\n\n[UWAGA: Wynik skrócony z ${originalLength} do ${TOOL_RESULT_MAX_CHARS} znaków. Poinformuj użytkownika, że dane mogą być niekompletne i zasugeruj zawężenie zapytania (np. mniejszy zakres dat, limit wyników).]`;
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
  staleCache = null;
  connectionErrors.clear();
  reconnecting.clear();
  console.log('[MCP] All connections closed');
}

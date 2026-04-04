import Anthropic from '@anthropic-ai/sdk';
import { getAllTools, callTool, getToolsForServer } from './mcp-orchestrator.js';
import {
  ANTHROPIC_MODEL, ROUTER_MODEL, MAX_TOKENS,
  getSystemPrompt, ROUTER_PROMPT, VALID_SERVERS,
  MAX_HISTORY_MESSAGES, MIN_API_INTERVAL_MS
} from './config.js';

const anthropic = new Anthropic();

// --- Rate limiter ---
let lastApiCall = 0;

async function rateLimitWait() {
  const now = Date.now();
  const elapsed = now - lastApiCall;
  if (elapsed < MIN_API_INTERVAL_MS) {
    const wait = MIN_API_INTERVAL_MS - elapsed;
    console.log(`[RateLimit] Waiting ${wait}ms`);
    await new Promise(r => setTimeout(r, wait));
  }
  lastApiCall = Date.now();
}

// --- Retry logic ---
const RETRY_DELAYS = [3000, 6000, 12000];

async function streamWithRetry(params, onText) {
  for (let attempt = 0; attempt <= RETRY_DELAYS.length; attempt++) {
    try {
      await rateLimitWait();
      const response = await anthropic.messages.create(params);

      let currentToolUse = null;
      let currentToolInput = '';
      const contentBlocks = [];
      // Fix 15: Track token usage
      let usage = null;

      for await (const event of response) {
        switch (event.type) {
          case 'content_block_start':
            if (event.content_block.type === 'text') {
              contentBlocks.push({ type: 'text', text: '' });
            } else if (event.content_block.type === 'tool_use') {
              currentToolUse = { id: event.content_block.id, name: event.content_block.name };
              currentToolInput = '';
              contentBlocks.push({
                type: 'tool_use',
                id: event.content_block.id,
                name: event.content_block.name,
                input: {}
              });
            }
            break;

          case 'content_block_delta':
            if (event.delta.type === 'text_delta') {
              onText(event.delta.text);
              const lastText = contentBlocks.findLast(b => b.type === 'text');
              if (lastText) lastText.text += event.delta.text;
            } else if (event.delta.type === 'input_json_delta') {
              currentToolInput += event.delta.partial_json;
            }
            break;

          case 'content_block_stop':
            if (currentToolUse) {
              try { currentToolUse.input = JSON.parse(currentToolInput || '{}'); }
              catch { currentToolUse.input = {}; }
              const toolBlock = contentBlocks.findLast(b => b.type === 'tool_use');
              if (toolBlock) toolBlock.input = currentToolUse.input;
              currentToolUse = null;
              currentToolInput = '';
            }
            break;

          // Fix 15: Capture usage from message_delta
          case 'message_delta':
            if (event.usage) {
              usage = { ...usage, ...event.usage };
            }
            break;

          case 'message_start':
            if (event.message?.usage) {
              usage = { ...usage, ...event.message.usage };
            }
            break;
        }
      }

      // Fix 15: Log token usage
      if (usage) {
        console.log(`[Anthropic] Tokens — input: ${usage.input_tokens || 0}, output: ${usage.output_tokens || 0}`);
      }

      return contentBlocks;
    } catch (err) {
      const is429 = err.status === 429
        || err.error?.type === 'rate_limit_error'
        || (typeof err.message === 'string' && err.message.includes('rate_limit'));

      if (is429 && attempt < RETRY_DELAYS.length) {
        const delay = RETRY_DELAYS[attempt];
        console.log(`[Anthropic] 429 — retry ${attempt + 1}/${RETRY_DELAYS.length} after ${delay}ms`);
        await new Promise(r => setTimeout(r, delay));
        continue;
      }
      throw err;
    }
  }
}

// --- Phase 1: Router (Haiku, no tools, ~500 tokens) ---
async function routeQuery(userMessage) {
  await rateLimitWait();

  console.log(`[Router] Routing query with ${ROUTER_MODEL}...`);
  const response = await anthropic.messages.create({
    model: ROUTER_MODEL,
    max_tokens: 20,
    system: ROUTER_PROMPT,
    messages: [{ role: 'user', content: userMessage }]
  });

  const text = response.content
    .filter(b => b.type === 'text')
    .map(b => b.text)
    .join('')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9\-]/g, '');

  const server = VALID_SERVERS.find(s => text.includes(s)) || null;
  console.log(`[Router] Result: "${text}" → server: ${server || 'none'}`);
  return server;
}

// --- Sliding window ---
function trimHistory(messages) {
  if (messages.length <= MAX_HISTORY_MESSAGES) return messages;
  const trimmed = messages.slice(-MAX_HISTORY_MESSAGES);
  if (trimmed[0].role !== 'user') {
    trimmed.shift();
  }
  return trimmed;
}

// --- Main entry point ---
// Fix 3: Accept signal param for client disconnect detection
export async function processChat(messages, { signal, onText, onToolUse, onToolResult, onProgress, onError, onDone }) {
  const MAX_TOOL_ROUNDS = 8;

  try {
    const lastUserMsg = [...messages].reverse().find(m => m.role === 'user');
    const userText = typeof lastUserMsg?.content === 'string'
      ? lastUserMsg.content
      : lastUserMsg?.content?.[0]?.text || '';

    await getAllTools();

    // Fix 3: Check if client disconnected
    if (signal?.aborted) return;

    onProgress?.('Routing...');
    const targetServer = await routeQuery(userText);

    if (signal?.aborted) return;

    let tools;
    if (targetServer) {
      const { tools: serverTools } = getToolsForServer(targetServer);
      tools = serverTools;
      console.log(`[Anthropic] Phase 2: ${tools.length} tools from ${targetServer}`);
    } else {
      tools = [];
      console.log('[Anthropic] Phase 2: no tools (conversational)');
    }

    const systemPrompt = getSystemPrompt();
    const workingMessages = trimHistory([...messages]);

    const estTokens = Math.round(
      JSON.stringify(workingMessages).length / 4 + JSON.stringify(tools).length / 4
    );
    console.log(`[Anthropic] Est input tokens: ${estTokens} (messages: ${workingMessages.length}, tools: ${tools.length})`);

    for (let round = 0; round < MAX_TOOL_ROUNDS; round++) {
      // Fix 3: Check abort before each API round
      if (signal?.aborted) {
        console.log('[Anthropic] Aborted — client disconnected');
        return;
      }

      console.log(`[Anthropic] Round ${round}`);
      onProgress?.('Generuję odpowiedź...');

      const contentBlocks = await streamWithRetry({
        model: ANTHROPIC_MODEL,
        max_tokens: MAX_TOKENS,
        system: systemPrompt,
        messages: workingMessages,
        tools: tools.length > 0 ? tools : undefined,
        stream: true
      }, onText);

      const toolUseBlocks = contentBlocks.filter(b => b.type === 'tool_use');

      if (toolUseBlocks.length === 0) {
        onDone();
        return;
      }

      workingMessages.push({ role: 'assistant', content: contentBlocks });

      const toolResults = [];
      for (const toolBlock of toolUseBlocks) {
        if (signal?.aborted) return;

        const toolShort = toolBlock.name.split('__').pop();
        onToolUse({ tool: toolBlock.name, args: toolBlock.input });
        onProgress?.(`Wywołuję ${toolShort}...`);

        try {
          const result = await callTool(toolBlock.name, toolBlock.input);
          const resultText = typeof result === 'string' ? result : JSON.stringify(result);

          toolResults.push({
            type: 'tool_result',
            tool_use_id: toolBlock.id,
            content: resultText
          });
          onToolResult({ tool: toolBlock.name, result: resultText.slice(0, 500) });
        } catch (err) {
          // Fix 10: Enhanced error message with instructions for Claude
          const errorMsg = `Error calling ${toolBlock.name}: ${err.message}. [Instrukcja: poinformuj użytkownika o błędzie narzędzia i kontynuuj rozmowę. Zasugeruj alternatywne podejście lub ponowienie próby.]`;
          toolResults.push({
            type: 'tool_result',
            tool_use_id: toolBlock.id,
            content: errorMsg,
            is_error: true
          });
          onToolResult({ tool: toolBlock.name, result: `Error: ${err.message}` });
        }
      }

      workingMessages.push({ role: 'user', content: toolResults });
      onProgress?.('Analizuję wyniki...');
    }

    onText('\n\n[Limit rund narzędzi]');
    onDone();
  } catch (err) {
    onError(err);
  }
}

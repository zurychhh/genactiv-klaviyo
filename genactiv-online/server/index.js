import 'dotenv/config';
import express from 'express';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { setupAuth, requireAuth } from './auth.js';
import { connectAll, shutdownAll } from './mcp-orchestrator.js';
import { processChat } from './anthropic-bridge.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3000');

const app = express();

// Trust Railway's reverse proxy (needed for secure cookies over HTTPS)
if (process.env.NODE_ENV === 'production') {
  app.set('trust proxy', 1);
}

app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// Auth setup
setupAuth(app);

// Health check (no auth)
app.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    uptime: Math.round(process.uptime()),
    timestamp: new Date().toISOString()
  });
});

// Static client files (require auth)
app.use('/', requireAuth, express.static(join(__dirname, '..', 'client')));

// Chat endpoint — SSE streaming
app.post('/api/chat', requireAuth, async (req, res) => {
  const { messages } = req.body;

  if (!messages || !Array.isArray(messages) || messages.length === 0) {
    return res.status(400).json({ error: 'messages array required' });
  }

  // SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');
  res.flushHeaders();

  const sendEvent = (type, data) => {
    res.write(`data: ${JSON.stringify({ type, data })}\n\n`);
  };

  await processChat(messages, {
    onText: (text) => sendEvent('text', text),
    onToolUse: ({ tool, args }) => sendEvent('tool_use', { tool, args }),
    onToolResult: ({ tool, result }) => sendEvent('tool_result', { tool, result }),
    onError: (err) => {
      console.error('[Chat] Error:', err.message);
      sendEvent('error', err.message);
      res.write('data: [DONE]\n\n');
      res.end();
    },
    onDone: () => {
      res.write('data: [DONE]\n\n');
      res.end();
    }
  });
});

// Graceful shutdown
async function shutdown(signal) {
  console.log(`\n[Server] ${signal} received, shutting down...`);
  await shutdownAll();
  process.exit(0);
}

process.on('SIGINT', () => shutdown('SIGINT'));
process.on('SIGTERM', () => shutdown('SIGTERM'));

// Start
async function start() {
  console.log('[Server] Connecting to MCP servers...');
  const connected = await connectAll();

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`[Server] GenActiv Online running at http://localhost:${PORT}`);
    console.log(`[Server] ${connected} MCP servers ready`);
  });
}

start().catch(err => {
  console.error('[Server] Fatal error:', err);
  process.exit(1);
});

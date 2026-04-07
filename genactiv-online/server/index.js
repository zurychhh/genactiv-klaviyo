import 'dotenv/config';
import express from 'express';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { setupAuth, requireAuth } from './auth.js';
import { connectAll, shutdownAll, getConnectionStatus } from './mcp-orchestrator.js';
import { processChat } from './anthropic-bridge.js';
import seoApi from './seo-api.js';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PORT = parseInt(process.env.PORT || '3000');

const app = express();

// Trust Railway's reverse proxy (needed for secure cookies over HTTPS)
if (process.env.NODE_ENV === 'production') {
  app.set('trust proxy', 1);
}

// Fix 18: Security headers (helmet)
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      scriptSrc: ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net"],
      styleSrc: ["'self'", "'unsafe-inline'", "fonts.googleapis.com"],
      fontSrc: ["'self'", "fonts.gstatic.com"],
      imgSrc: ["'self'", "data:"],
      connectSrc: ["'self'"]
    }
  }
}));

app.use(express.json({ limit: '1mb' }));
app.use(express.urlencoded({ extended: true }));

// Fix 16: Log sanitization
function sanitizeLogMessage(msg) {
  if (typeof msg !== 'string') return msg;
  return msg
    .replace(/sk-ant-[a-zA-Z0-9_-]+/g, 'sk-ant-***')
    .replace(/shpat_[a-zA-Z0-9]+/g, 'shpat_***')
    .replace(/EAA[a-zA-Z0-9]+/g, 'EAA***')
    .replace(/1\/\/[a-zA-Z0-9_-]+/g, '1//***')
    .replace(/pk_[a-zA-Z0-9]+/g, 'pk_***');
}

// Auth setup
setupAuth(app);

// Fix 2: Per-user rate limiting on /api/chat
const chatLimiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10, // 10 requests per minute per session
  keyGenerator: (req) => req.session?.id || req.ip,
  message: { error: 'Zbyt wiele zapytań. Poczekaj chwilę i spróbuj ponownie.' },
  standardHeaders: true,
  legacyHeaders: false
});

// Fix 4: Enhanced health check (no auth)
app.get('/api/health', (_req, res) => {
  const mcpStatus = getConnectionStatus();
  const mem = process.memoryUsage();

  const status = mcpStatus.connected > 0 ? 'ok' : 'degraded';
  const httpCode = mcpStatus.connected > 0 ? 200 : 503;

  res.status(httpCode).json({
    status,
    uptime: Math.round(process.uptime()),
    timestamp: new Date().toISOString(),
    mcp: {
      connected: mcpStatus.connected,
      total: mcpStatus.total,
      servers: mcpStatus.servers
    },
    memory: {
      rss: Math.round(mem.rss / 1024 / 1024),
      heap: Math.round(mem.heapUsed / 1024 / 1024)
    }
  });
});

// SEO Command Center API
app.use('/api/seo', requireAuth, seoApi);

// Static client files (require auth)
app.use('/', requireAuth, express.static(join(__dirname, '..', 'client')));

// Fix 6: Request timeout middleware (skip /api/chat — handled separately)
app.use((req, res, next) => {
  if (req.path === '/api/chat') return next();
  req.setTimeout(120_000, () => {
    if (!res.headersSent) {
      res.status(408).json({ error: 'Request timeout' });
    }
  });
  next();
});

// Fix 19: XSS validation for messages
function validateMessages(messages) {
  if (!Array.isArray(messages) || messages.length === 0) return false;
  for (const msg of messages) {
    if (!msg.role || !['user', 'assistant'].includes(msg.role)) return false;
    const content = typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content);
    if (content.length > 10_000) return false;
  }
  return true;
}

// Chat endpoint — SSE streaming
app.post('/api/chat', requireAuth, chatLimiter, async (req, res) => {
  const { messages } = req.body;

  if (!messages || !validateMessages(messages)) {
    return res.status(400).json({ error: 'Invalid messages array (max 10000 chars per message, role must be user or assistant)' });
  }

  // SSE headers
  res.setHeader('Content-Type', 'text/event-stream');
  res.setHeader('Cache-Control', 'no-cache');
  res.setHeader('Connection', 'keep-alive');
  res.setHeader('X-Accel-Buffering', 'no');
  res.flushHeaders();

  // Fix 3: SSE client disconnect detection
  let clientDisconnected = false;
  const abortController = new AbortController();

  req.on('close', () => {
    clientDisconnected = true;
    abortController.abort();
    console.log('[Chat] Client disconnected');
  });

  const sendEvent = (type, data) => {
    if (clientDisconnected) return;
    try {
      res.write(`data: ${JSON.stringify({ type, data })}\n\n`);
    } catch {
      clientDisconnected = true;
    }
  };

  // Fix 6: Absolute max timeout for /api/chat (180s)
  const chatTimeout = setTimeout(() => {
    if (!clientDisconnected) {
      console.log('[Chat] Request timed out (180s)');
      sendEvent('error', 'Przekroczono maksymalny czas przetwarzania (3 min). Spróbuj prostsze pytanie.');
      sendEvent('done', null);
      if (!clientDisconnected) {
        res.write('data: [DONE]\n\n');
        res.end();
      }
      clientDisconnected = true;
      abortController.abort();
    }
  }, 180_000);

  await processChat(messages, {
    signal: abortController.signal,
    onText: (text) => sendEvent('text', text),
    onToolUse: ({ tool, args }) => sendEvent('tool_use', { tool, args }),
    onToolResult: ({ tool, result }) => sendEvent('tool_result', { tool, result }),
    onProgress: (msg) => sendEvent('progress', msg),
    onError: (err) => {
      console.error('[Chat] Error:', sanitizeLogMessage(err.message));
      sendEvent('error', err.message);
      if (!clientDisconnected) {
        res.write('data: [DONE]\n\n');
        res.end();
      }
      clearTimeout(chatTimeout);
    },
    onDone: () => {
      if (!clientDisconnected) {
        res.write('data: [DONE]\n\n');
        res.end();
      }
      clearTimeout(chatTimeout);
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

// Fix 1: unhandledRejection / uncaughtException handlers
process.on('unhandledRejection', (reason) => {
  console.error('[Server] Unhandled rejection:', sanitizeLogMessage(String(reason)));
});

process.on('uncaughtException', (err) => {
  console.error('[Server] Uncaught exception:', sanitizeLogMessage(err.message));
  console.error(err.stack);
  // Give time to flush logs, then exit (Railway will restart)
  setTimeout(() => process.exit(1), 1000);
});

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

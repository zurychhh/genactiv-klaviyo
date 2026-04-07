/**
 * SEO Command Center — backend API
 * Direct MCP tool calls for SEO audit, GA4 organic traffic, and fix actions.
 */
import { Router } from 'express';
import { callTool, getConnectionStatus } from './mcp-orchestrator.js';

const router = Router();

// --- Diagnostic endpoint: show which MCP servers are connected ---
router.get('/status', async (req, res) => {
  try {
    const status = getConnectionStatus();
    res.json({
      ok: true,
      mcp: status,
      env: {
        GA4_PROPERTY_ID: process.env.GA4_PROPERTY_ID ? 'set' : 'MISSING',
        SHOPIFY_ACCESS_TOKEN: process.env.SHOPIFY_ACCESS_TOKEN ? 'set' : 'MISSING',
      }
    });
  } catch (err) {
    res.status(500).json({ ok: false, error: err.message });
  }
});

// --- SEO Audit (Shopify products + collections) ---
router.get('/audit', async (req, res) => {
  try {
    const scope = req.query.scope || 'all';
    const limit = Math.min(parseInt(req.query.limit) || 100, 250);

    console.log(`[SEO API] Calling get-seo-audit (scope=${scope}, limit=${limit})`);
    const result = await callTool('mcp__shopify-extended__get-seo-audit', { scope, limit });

    console.log(`[SEO API] Audit result type: ${typeof result}, keys: ${result && typeof result === 'object' ? Object.keys(result).join(',') : 'N/A'}`);

    // If result is a string, try to parse it as JSON
    let parsed = result;
    if (typeof result === 'string') {
      try { parsed = JSON.parse(result); } catch { /* keep as string */ }
    }

    // Pass through whatever we got — let frontend handle display
    if (parsed && typeof parsed === 'object') {
      // If it has issues array, it's a valid audit result (even if it also has other fields)
      res.json(parsed);
    } else {
      // Truly unexpected: not an object even after parsing
      const errMsg = typeof parsed === 'string' ? parsed : 'SEO audit tool returned non-object result';
      console.error('[SEO API] Audit non-object result:', typeof parsed, String(parsed).slice(0, 500));
      res.status(502).json({ error: errMsg, source: 'shopify-extended', resultType: typeof parsed });
    }
  } catch (err) {
    console.error('[SEO API] Audit error:', err.message, err.stack?.split('\n')[1]);
    res.status(500).json({ error: err.message, source: 'seo-api' });
  }
});

// --- GA4 Organic Traffic (top landing pages) ---
// Graceful degradation: if GA4 fails, return partial result so dashboard still works
router.get('/organic', async (req, res) => {
  const days = parseInt(req.query.days) || 30;
  const endDate = new Date().toISOString().split('T')[0];
  const startDate = new Date(Date.now() - days * 86400000).toISOString().split('T')[0];

  console.log(`[SEO API] Calling GA4 run_report (${startDate} → ${endDate})`);

  try {
    const result = await callTool('mcp__ga4__run_report', {
      property_id: process.env.GA4_PROPERTY_ID || '279858535',
      date_ranges: [{ start_date: startDate, end_date: endDate }],
      dimensions: ['pagePath'],
      metrics: ['sessions', 'activeUsers', 'screenPageViews'],
      dimension_filter: {
        filter: {
          field_name: 'sessionDefaultChannelGrouping',
          string_filter: { value: 'Organic Search', match_type: 'EXACT' }
        }
      },
      order_bys: [{ metric: { metric_name: 'sessions' }, desc: true }],
      limit: 50
    });

    // The GA4 result can be a string (from MCP) or an object
    let parsed = result;
    if (typeof result === 'string') {
      try { parsed = JSON.parse(result); } catch { parsed = { raw: result }; }
    }

    if (parsed && typeof parsed === 'object' && !parsed.error) {
      res.json(parsed);
    } else {
      const errMsg = parsed?.error || 'Unexpected response from GA4';
      console.error('[SEO API] GA4 returned error:', errMsg);
      // Graceful: return empty rows + error note (200, not 500)
      res.json({ rows: [], partial: true, ga4_error: errMsg, dateRange: { startDate, endDate } });
    }
  } catch (err) {
    console.error('[SEO API] Organic traffic error:', err.message);
    // Graceful degradation: return empty result instead of 500
    res.json({ rows: [], partial: true, ga4_error: err.message, dateRange: { startDate, endDate } });
  }
});

// --- Fix: Update product SEO meta ---
router.post('/fix/meta', async (req, res) => {
  try {
    const { items, dryRun } = req.body;
    if (!items || !Array.isArray(items) || items.length === 0) {
      return res.status(400).json({ error: 'items array required' });
    }
    if (items.length > 25) {
      return res.status(400).json({ error: 'Max 25 items per batch' });
    }

    const result = await callTool('mcp__shopify-extended__bulk-update-seo', {
      items,
      dryRun: dryRun || false
    });
    res.json(result);
  } catch (err) {
    console.error('[SEO API] Fix meta error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// --- Fix: Update product content (description, title) ---
router.post('/fix/content', async (req, res) => {
  try {
    const { productId, descriptionHtml, title, tags } = req.body;
    if (!productId) {
      return res.status(400).json({ error: 'productId required' });
    }

    const args = { productId };
    if (descriptionHtml !== undefined) args.descriptionHtml = descriptionHtml;
    if (title !== undefined) args.title = title;
    if (tags !== undefined) args.tags = tags;

    const result = await callTool('mcp__shopify-extended__update-product-content', args);
    res.json(result);
  } catch (err) {
    console.error('[SEO API] Fix content error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// --- Fix: Update ALT texts ---
router.post('/fix/alt', async (req, res) => {
  try {
    const { productId, images } = req.body;
    if (!productId || !images || !Array.isArray(images)) {
      return res.status(400).json({ error: 'productId and images array required' });
    }

    const result = await callTool('mcp__shopify-extended__update-product-images', {
      productId,
      images
    });
    res.json(result);
  } catch (err) {
    console.error('[SEO API] Fix ALT error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// --- Products list (for the dashboard) ---
router.get('/products', async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 50, 100);
    const result = await callTool('mcp__shopify-extended__get-products', { limit });
    res.json(result);
  } catch (err) {
    console.error('[SEO API] Products error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

export default router;

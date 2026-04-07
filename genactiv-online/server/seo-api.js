/**
 * SEO Command Center — backend API
 * Direct MCP tool calls for SEO audit, GA4 organic traffic, and fix actions.
 */
import { Router } from 'express';
import { callTool } from './mcp-orchestrator.js';

const router = Router();

// --- SEO Audit (Shopify products + collections) ---
router.get('/audit', async (req, res) => {
  try {
    const scope = req.query.scope || 'all';
    const limit = Math.min(parseInt(req.query.limit) || 100, 250);

    const result = await callTool('mcp__shopify-extended__get-seo-audit', { scope, limit });
    res.json(result);
  } catch (err) {
    console.error('[SEO API] Audit error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// --- GA4 Organic Traffic (top landing pages) ---
router.get('/organic', async (req, res) => {
  try {
    const days = parseInt(req.query.days) || 30;
    const endDate = new Date().toISOString().split('T')[0];
    const startDate = new Date(Date.now() - days * 86400000).toISOString().split('T')[0];

    const result = await callTool('mcp__ga4__run_report', {
      property_id: process.env.GA4_PROPERTY_ID || '279858535',
      date_ranges: [{ start_date: startDate, end_date: endDate }],
      dimensions: ['pagePath', 'sessionDefaultChannelGrouping'],
      metrics: ['sessions', 'activeUsers', 'screenPageViews', 'averageSessionDuration', 'bounceRate'],
      dimension_filter: {
        filter: {
          field_name: 'sessionDefaultChannelGrouping',
          string_filter: { value: 'Organic Search', match_type: 'EXACT' }
        }
      },
      order_bys: [{ metric: { metric_name: 'sessions' }, desc: true }],
      limit: 50
    });

    res.json(result);
  } catch (err) {
    console.error('[SEO API] Organic traffic error:', err.message);
    res.status(500).json({ error: err.message });
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

import 'dotenv/config';
import express from 'express';
import { GraphQLClient } from 'graphql-request';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { callTool, shutdownAll } from './mcp-client.js';

// Tool imports from shopify-mcp-extended
import { getTrafficSourceAnalytics } from '../shopify-mcp-extended/dist/tools/getTrafficSourceAnalytics.js';
import { getCampaignPerformance } from '../shopify-mcp-extended/dist/tools/getCampaignPerformance.js';
import { getConversionMetrics } from '../shopify-mcp-extended/dist/tools/getConversionMetrics.js';
import { getProductPerformance } from '../shopify-mcp-extended/dist/tools/getProductPerformance.js';
import { getOrders } from '../shopify-mcp-extended/dist/tools/getOrders.js';
import { getProducts } from '../shopify-mcp-extended/dist/tools/getProducts.js';

const __dirname = dirname(fileURLToPath(import.meta.url));

// --- Config ---
const {
  SHOPIFY_ACCESS_TOKEN,
  MYSHOPIFY_DOMAIN,
  PORT = '3001'
} = process.env;

if (!SHOPIFY_ACCESS_TOKEN || !MYSHOPIFY_DOMAIN) {
  console.error('Missing SHOPIFY_ACCESS_TOKEN or MYSHOPIFY_DOMAIN in .env');
  process.exit(1);
}

// --- GraphQL Client (same pattern as shopify-mcp-extended/src/index.ts) ---
const shopifyClient = new GraphQLClient(
  `https://${MYSHOPIFY_DOMAIN}/admin/api/2023-07/graphql.json`,
  {
    headers: {
      'X-Shopify-Access-Token': SHOPIFY_ACCESS_TOKEN,
      'Content-Type': 'application/json'
    }
  }
);

// --- Initialize tools ---
getTrafficSourceAnalytics.initialize(shopifyClient);
getCampaignPerformance.initialize(shopifyClient);
getConversionMetrics.initialize(shopifyClient);
getProductPerformance.initialize(shopifyClient);
getOrders.initialize(shopifyClient);
getProducts.initialize(shopifyClient);

// --- Cache ---
const cache = new Map();

function getCached(key, ttlMs) {
  const entry = cache.get(key);
  if (entry && Date.now() - entry.time < ttlMs) return entry.data;
  return null;
}

function setCache(key, data) {
  cache.set(key, { data, time: Date.now() });
}

// --- Express ---
const app = express();
app.use(express.static(join(__dirname, 'public')));

// Health
app.get('/api/health', (_req, res) => {
  res.json({
    status: 'ok',
    uptime: Math.round(process.uptime()),
    cacheEntries: cache.size,
    store: MYSHOPIFY_DOMAIN
  });
});

// Dashboard - main endpoint (4 analytics tools in parallel)
app.get('/api/dashboard', async (req, res) => {
  try {
    const { dateFrom, dateTo, force } = req.query;
    if (!dateFrom || !dateTo) {
      return res.status(400).json({ error: 'dateFrom and dateTo required' });
    }

    const cacheKey = `dashboard:${dateFrom}:${dateTo}`;
    if (force !== 'true') {
      const cached = getCached(cacheKey, 5 * 60 * 1000);
      if (cached) return res.json(cached);
    }

    const params = { dateFrom, dateTo, limit: 250 };

    const [traffic, campaigns, conversions, products] = await Promise.all([
      getTrafficSourceAnalytics.execute(params),
      getCampaignPerformance.execute(params),
      getConversionMetrics.execute({ ...params, groupBy: 'day' }),
      getProductPerformance.execute(params)
    ]);

    const result = { traffic, campaigns, conversions, products, fetchedAt: new Date().toISOString() };
    setCache(cacheKey, result);
    res.json(result);
  } catch (err) {
    console.error('Dashboard error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Recent orders
app.get('/api/orders/recent', async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 10, 50);
    const force = req.query.force;

    const cacheKey = `orders:recent:${limit}`;
    if (force !== 'true') {
      const cached = getCached(cacheKey, 2 * 60 * 1000);
      if (cached) return res.json(cached);
    }

    const result = await getOrders.execute({ status: 'any', limit, reverse: true, sortKey: 'CREATED_AT' });
    setCache(cacheKey, result);
    res.json(result);
  } catch (err) {
    console.error('Orders error:', err);
    res.status(500).json({ error: err.message });
  }
});

// Products
app.get('/api/products', async (req, res) => {
  try {
    const limit = Math.min(parseInt(req.query.limit) || 20, 50);
    const force = req.query.force;

    const cacheKey = `products:${limit}`;
    if (force !== 'true') {
      const cached = getCached(cacheKey, 10 * 60 * 1000);
      if (cached) return res.json(cached);
    }

    const result = await getProducts.execute({ limit });
    setCache(cacheKey, result);
    res.json(result);
  } catch (err) {
    console.error('Products error:', err);
    res.status(500).json({ error: err.message });
  }
});

// --- MCP-powered endpoints ---

const GA4_PROPERTY_ID = 279858535;
const META_ADS_ACCOUNT_ID = 'act_66396825';
const GOOGLE_ADS_CUSTOMER_ID = '3393382047';
const KLAVIYO_PLACED_ORDER_METRIC_ID = 'R6aTMS';

// GA4 - Traffic analytics
app.get('/api/ga4', async (req, res) => {
  try {
    const { dateFrom, dateTo, force } = req.query;
    if (!dateFrom || !dateTo) {
      return res.status(400).json({ error: 'dateFrom and dateTo required' });
    }

    const cacheKey = `ga4:${dateFrom}:${dateTo}`;
    if (force !== 'true') {
      const cached = getCached(cacheKey, 10 * 60 * 1000);
      if (cached) return res.json(cached);
    }

    const result = await callTool('ga4', 'run_report', {
      property_id: GA4_PROPERTY_ID,
      date_ranges: [{ start_date: dateFrom, end_date: dateTo }],
      dimensions: ['sessionSource', 'sessionMedium'],
      metrics: ['sessions', 'activeUsers', 'engagementRate', 'ecommercePurchases', 'purchaseRevenue'],
      order_bys: [{ metric: { metric_name: 'sessions' }, desc: true }],
      limit: 20,
      currency_code: 'PLN'
    });

    setCache(cacheKey, result);
    res.json(result);
  } catch (err) {
    console.error('GA4 error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// Meta Ads - Campaign insights
app.get('/api/meta-ads', async (req, res) => {
  try {
    const days = parseInt(req.query.days) || 7;
    const force = req.query.force;
    const timeRange = days <= 7 ? 'last_7d' : days <= 30 ? 'last_30d' : 'last_90d';

    const cacheKey = `meta-ads:${timeRange}`;
    if (force !== 'true') {
      const cached = getCached(cacheKey, 10 * 60 * 1000);
      if (cached) return res.json(cached);
    }

    const result = await callTool('meta-ads', 'get_insights', {
      object_id: META_ADS_ACCOUNT_ID,
      time_range: timeRange,
      level: 'campaign',
      limit: 20,
      compact: true
    });

    setCache(cacheKey, result);
    res.json(result);
  } catch (err) {
    console.error('Meta Ads error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// Google Ads - Campaign performance
app.get('/api/google-ads', async (req, res) => {
  try {
    const { dateFrom, dateTo, force } = req.query;
    if (!dateFrom || !dateTo) {
      return res.status(400).json({ error: 'dateFrom and dateTo required' });
    }

    const cacheKey = `google-ads:${dateFrom}:${dateTo}`;
    if (force !== 'true') {
      const cached = getCached(cacheKey, 10 * 60 * 1000);
      if (cached) return res.json(cached);
    }

    const result = await callTool('google-ads', 'run_gaql', {
      customer_id: GOOGLE_ADS_CUSTOMER_ID,
      query: `SELECT campaign.name, campaign.status, metrics.clicks, metrics.impressions, metrics.cost_micros, metrics.ctr, metrics.conversions, metrics.conversions_value FROM campaign WHERE segments.date BETWEEN '${dateFrom}' AND '${dateTo}' AND campaign.status != 'REMOVED' ORDER BY metrics.cost_micros DESC LIMIT 20`
    });

    setCache(cacheKey, result);
    res.json(result);
  } catch (err) {
    console.error('Google Ads error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// Klaviyo - Email marketing report
app.get('/api/klaviyo', async (req, res) => {
  try {
    const force = req.query.force;

    const cacheKey = 'klaviyo:campaigns';
    if (force !== 'true') {
      const cached = getCached(cacheKey, 15 * 60 * 1000);
      if (cached) return res.json(cached);
    }

    const result = await callTool('klaviyo', 'klaviyo_get_campaign_report', {
      model: 'claude',
      statistics: ['recipients', 'open_rate', 'click_rate', 'bounce_rate', 'unsubscribes', 'conversions', 'conversion_rate'],
      conversion_metric_id: KLAVIYO_PLACED_ORDER_METRIC_ID,
      value_statistics: ['revenue_per_recipient', 'conversion_value'],
      timeframe: { value: { key: 'last_30_days' } },
      filters: [{ field: 'send_channel', operator: 'equals', value: 'email' }]
    });

    setCache(cacheKey, result);
    res.json(result);
  } catch (err) {
    console.error('Klaviyo error:', err.message);
    res.status(500).json({ error: err.message });
  }
});

// --- Shutdown hooks ---
process.on('SIGINT', async () => {
  console.log('\nShutting down...');
  await shutdownAll();
  process.exit(0);
});
process.on('SIGTERM', async () => {
  console.log('\nShutting down...');
  await shutdownAll();
  process.exit(0);
});

app.listen(parseInt(PORT), () => {
  console.log(`GenActiv Dashboard running at http://localhost:${PORT}`);
  console.log(`Store: ${MYSHOPIFY_DOMAIN}`);
  console.log('MCP integrations: GA4, Meta Ads, Google Ads, Klaviyo (lazy connect)');
});

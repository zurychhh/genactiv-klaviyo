# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Client:** GenActiv.pl — Poland's #1 colostrum brand in pharmacies
**Platform:** Klaviyo + Shopify + Baselinker integration via MCP (Model Context Protocol)
**Primary Work:** HTML/CSS email template creation, campaign optimization, marketing automation, order/payment sync
**Web Terminal:** GenActiv Online — browser-based AI assistant deployed on Railway.app
**Language:** Polish (PL) for all UI, prompts, and user-facing content. Currency: PLN, no decimals.

## Quick Start (nowa maszyna)

```bash
git clone git@github.com:zurychhh/genactiv-klaviyo.git
cd genactiv-klaviyo
cp .env.example .env                    # Uzupelnij tokeny (Shopify, Baselinker, TikTok)
cp genactiv-online/.env.example genactiv-online/.env  # Uzupelnij tokeny (Anthropic, Klaviyo, etc.)
chmod +x setup-claude.sh && ./setup-claude.sh         # Instalacja: venv, npm, build, .mcp.json
claude                                  # Claude Code automatycznie wczyta CLAUDE.md + .mcp.json
```

Pelna instrukcja (konto GitHub, rotacja tokenow, deploy): `GITHUB_SETUP.md`

## Repository Structure

```
genactiv-klaviyo/
├── genactiv-online/           # ★ Web AI terminal (Express + SSE + MCP, deployed on Railway)
│   ├── client/                #   Frontend: HTML, CSS, JS (dark terminal theme)
│   │   ├── index.html         #   Main page (Polish UI) + capabilities panel
│   │   ├── seo.html           #   SEO Command Center dashboard
│   │   ├── style.css          #   Dark terminal theme
│   │   └── terminal.js        #   SSE client, markdown rendering, thinking indicator
│   └── server/                #   Backend: Express, Anthropic API, MCP orchestrator
│       ├── index.js           #   Express: auth, SSE streaming, health check, SEO API mount
│       ├── config.js          #   MCP server defs, models, system prompts, constants
│       ├── auth.js            #   Login (bcrypt + session, 24h expiry)
│       ├── mcp-orchestrator.js #  MCP connections, tool caching, result compression
│       ├── seo-api.js         #   SEO Command Center REST API
│       └── anthropic-bridge.js #  Two-phase routing, retry logic, rate limiting
├── shopify-mcp-extended/      # Extended Shopify MCP with analytics (TypeScript)
├── google-ads-mcp/            # Google Ads MCP server (Python/FastMCP)
├── templates/snippets/        # Reusable email HTML components
├── seo/                       # SEO implementation project
├── reports/                   # Generated reports (dashboards, traffic, consistency)
├── docs/                      # Documentation (audit checklists, migration plan, Meta Ads)
├── .github/workflows/         # GitHub Actions (automated payment sync)
├── Dockerfile                 # Railway Docker build (Node 18 + Python 3 + uv)
├── railway.json               # Railway.app deployment config
├── baselinker_api.py          # Baselinker API client
├── shopify_graphql.py         # Shopify GraphQL client (transactions)
├── shopify_theme_api.py       # Shopify Theme API client
├── sync_payment_id.py         # Payment ID sync: Shopify → Baselinker
├── dashboard-server/          # Legacy — replaced by genactiv-online
└── chat-ui/                   # Legacy — replaced by genactiv-online
```

## Build, Test & Dev Commands

### GenActiv Online (Web Terminal)

```bash
cd genactiv-online
cp .env.example .env            # Fill in API keys (first time only)
npm install
npm run dev                     # http://localhost:3000 (node --watch)
npm start                       # Production mode
npm test                        # Jest (ESM, requires --experimental-vm-modules)

# Run a single test file:
node --experimental-vm-modules node_modules/.bin/jest server/__tests__/crash.test.js

# Login: admin / (password from AUTH_PASSWORD_HASH bcrypt hash in .env)
```

Both `genactiv-online` and `shopify-mcp-extended` use ESM (`"type": "module"` in package.json).

### Shopify MCP Extended (TypeScript)

```bash
cd shopify-mcp-extended
npm install
npm run build                   # rimraf dist && tsc → dist/
npm run dev                     # ts-node with ESM loader
npm start                       # node dist/index.js
npm test                        # Jest (ts-jest ESM preset)
npm run lint                    # ESLint on src/**/*.ts
npm run clean                   # rimraf dist/

# Run a single test:
npx jest src/__tests__/crash.test.ts
```

### Google Ads MCP (Python)

```bash
cd google-ads-mcp/google-ads-mcp-server
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
fastmcp run server.py           # Starts MCP server via FastMCP
```

### Python Scripts (root level)

```bash
source venv/bin/activate        # Required for all root-level Python scripts
python baselinker_api.py orders|payments|sources|full
python sync_payment_id.py [--live]     # Dry run by default
python3 shopify_graphql.py orders|order|apps
python3 shopify_theme_api.py themes|assets|get|backup|update|search
```

### Credential Generation

```bash
# Generate bcrypt password hash for AUTH_PASSWORD_HASH:
node -e "require('bcryptjs').hash('your-password', 10).then(console.log)"

# Google Ads OAuth refresh token:
cd google-ads-mcp && python generate_refresh_token.py

# GA4 OAuth refresh token:
python generate_ga4_token.py

# TikTok access token (24h expiry, auto-refreshed by tiktok-ads-mcp):
python3 generate_tiktok_token.py
```

## Architecture: Two-Phase Query Routing

The web terminal uses a two-model approach to reduce token usage (22k → 1.8k tokens per request):

```
Browser → Express (auth + SSE) → Phase 1: Haiku classifies query → selects 1 MCP server
                                → Phase 2: Sonnet processes with only that server's tools
                                ⇅
                          8 MCP servers (each 6-20 tools)
```

**Key files:**
- `config.js` — MCP server definitions, model constants, system prompt (Polish), router prompt
- `anthropic-bridge.js` — Two-phase routing: `routeQuery()` calls Haiku (20 token limit), then Sonnet executes with filtered tools. Retry with 3s/6s/12s backoff on 429.
- `mcp-orchestrator.js` — MCP client lifecycle: 30s connect timeout, tool list caching (5 min TTL), stale cache fallback on fetch failure, exponential reconnection backoff (2s → 32s), result compression (nulls stripped, truncated at 15k chars)

**Configuration constants** (`config.js`):
| Setting | Value |
|---------|-------|
| Main model | `claude-sonnet-4-20250514` |
| Router model | `claude-haiku-4-5-20251001` |
| Max tokens | 4096 |
| Tool result limit | 15,000 chars |
| History window | 6 messages (3 pairs) |
| Rate limiter | 500ms minimum between API calls |
| Tool cache TTL | 5 minutes |

### SSE Streaming

Chat responses are streamed via Server-Sent Events with event types: `text`, `tool_use`, `tool_result`, `progress`, `error`, `done`.

### SEO Command Center API (`seo-api.js`)

REST endpoints (require auth):
- `GET /api/seo/status` — MCP server connection status
- `GET /api/seo/audit?scope=all&limit=100` — Shopify products/collections SEO issues
- `GET /api/seo/organic?days=30` — GA4 organic traffic breakdown
- `POST /api/seo/fix` — Execute SEO fixes (update metas, etc.)

GA4 failures return partial results (`200` with `partial: true`) instead of 5xx.

### Health Check

`GET /api/health` (no auth) — returns MCP connection status, memory usage, uptime.

## MCP Server Configuration

Eight MCP servers defined in `config.js`. Notable: **shopify-standard** and **shopify-extended** both run the same `shopify-mcp-extended/dist/index.js` binary (same tools, different routing labels).

| Server | Runtime | Command |
|--------|---------|---------|
| klaviyo | Python/uvx | `uvx klaviyo-mcp-server@0.4.0` |
| shopify-extended | Node.js | `node shopify-mcp-extended/dist/index.js` |
| shopify-standard | Node.js | Same binary as shopify-extended |
| meta-ads | Python | `python3 -m meta_ads_mcp` |
| google-ads | Python venv | `venv/bin/fastmcp run server.py` |
| ga4 | Python | `analytics-mcp` |
| tiktok-ads | Python | `python3 -m tiktok_ads_mcp` |
| senuto | Node.js/npx | `npx -y senuto-mcp` |

**Startup behavior:** `config.js` auto-generates Google Ads and GA4 credential JSON files from environment variables at startup (lines 9-59). Missing tokens trigger console warnings but don't block other servers.

### MCP Tool Usage Notes

| Server | Key Notes |
|--------|-----------|
| Klaviyo | `campaign_report` requires `conversion_metric_id`. Templates need full HTML + `{% unsubscribe %}` |
| Shopify Extended | `bulk-update-seo` max 25 items, has dry-run mode |
| Google Ads | Customer ID: 10-digit, no dashes. `primaryForGoal` — ALWAYS check explicitly, don't assume ENABLED = Primary |
| Senuto | Default: domain="genactiv.pl", country_id="200" (Poland Base 2.0), fetch_mode="topLevelDomain" |

## Railway Deployment

```bash
# IMPORTANT: Always unset stale RAILWAY_TOKEN before CLI use
unset RAILWAY_TOKEN

railway up                      # Deploy from project root (uses root Dockerfile)
railway variables set KEY=VALUE # Set env vars
railway logs                    # View logs
railway login --browserless     # Re-authenticate when session expires
railway whoami                  # Verify auth
```

- **Project:** cozy-trust | **Service:** exemplary-learning
- **Production URL:** `https://exemplary-learning-production-414a.up.railway.app`
- **Custom domain:** `genactiv.oleksiakconsulting.com` — currently **broken** (DNS/CNAME issue)

**Docker build** (root `Dockerfile`): Node 18 slim + Python 3 + uv → builds Shopify Extended TypeScript → Google Ads Python venv → installs meta-ads-mcp + analytics-mcp + tiktok-ads-mcp + senuto-mcp globally → copies genactiv-online. `NODE_OPTIONS="--max-old-space-size=512"`.

## Account IDs & Service References

| Service | ID |
|---------|-----|
| Shopify store | `genactiv.myshopify.com` |
| Shopify active theme | GEN-6 global - slideshow (ID: 162539340108) |
| Shopify gateway | Przelewy24 |
| GA4 Measurement ID | `G-KE8T99MGMJ` |
| GA4 Property ID | `279858535` |
| Google Ads MCC | `253-832-8866` (env: `2538328866`) |
| Google Ads Account | `339-338-2047` (env: `3393382047`) |
| Google Ads Conversion ID | `AW-779033182` |
| Meta Pixel ID | `370142134442442` |
| GTM Container | `GTM-5W5Z2ML` |

## Klaviyo Template Development

- Inline CSS only, table-based layouts. Max 600px desktop, min 320px mobile, stack on <480px. Total <100KB.
- Creating via MCP (`klaviyo_create_email_template`): requires complete HTML with `<html>` and `<body>` tags, unsubscribe link `{% unsubscribe 'Anuluj subskrypcję' %}`, images uploaded first via `klaviyo_upload_image_from_url`.

### Template Variables
```django
{{ first_name|default:"" }}           # Personalization
{{ event.ProductName }}               # Cart abandonment
{{ event.Price|floatformat:0 }}       # PLN (no decimals)
{{ event.CompareAtPrice }}            # Original price
{% unsubscribe 'Anuluj subskrypcję' %}  # Required
```

### Reusable Snippets
- `templates/snippets/product-card-abandoned-cart.html` — Product card with price comparison

## Brand Guidelines

| Element | Value |
|---------|-------|
| Brand Blue | `#0066CC` |
| GenActiv Red (CTAs) | `#EF3340` |
| Success Green | `#27ae60` |
| Trust Navy | `#1A3B5D` |
| Font | `'Branding-medium', Helvetica, Arial, sans-serif` |
| UTM | `?utm_source=klaviyo&utm_medium=email&utm_campaign=[name]` |

## Environment Variables

See `genactiv-online/.env.example` for full list. Key groups:
- `AUTH_USERNAME`, `AUTH_PASSWORD_HASH` — bcrypt login credentials
- `ANTHROPIC_API_KEY` — Claude API
- `KLAVIYO_API_KEY`, `SHOPIFY_ACCESS_TOKEN`, `MYSHOPIFY_DOMAIN` — core integrations
- `META_ACCESS_TOKEN` — Meta Graph API
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` — shared by Google Ads + GA4
- `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`
- `GA4_PROPERTY_ID`, `GA4_REFRESH_TOKEN`
- `TIKTOK_APP_ID`, `TIKTOK_SECRET`, `TIKTOK_ACCESS_TOKEN` — 24h expiry, auto-refreshed
- `SENUTO_API_KEY` — JWT, exp ~Sep 2026

## Known Issues

- **Google OAuth tokens** expire in 7 days when Google Cloud consent screen is in "Testing" mode. After publication, tokens don't expire. Regenerate with `python generate_refresh_token.py` (Ads) or `python generate_ga4_token.py` (GA4).
- **Meta Ads MCP** sometimes fails to connect locally (Python module issue). Works on Railway.
- **Railway CLI** reads token from `~/.railway/config.json`, but `RAILWAY_TOKEN` env var overrides it. Always `unset RAILWAY_TOKEN` before CLI use.
- **Pandectes consent banner** `cookiesBlockedByDefault=7` blocks all optional cookies by default, causing low attribution rates. Config in Shopify theme: `assets/pandectes-settings.json`, `snippets/pandectes-rules.liquid`.
- **Shopify Order API** does NOT store `gclid` — only UTM params.

## GitHub Actions

`.github/workflows/sync-payment-id.yml` — Payment ID sync Shopify → Baselinker
- Schedule: hourly (`0 * * * *`) + manual dispatch
- Secrets: `SHOPIFY_DOMAIN`, `SHOPIFY_TOKEN`, `BASELINKER_TOKEN`

## Local Python Scripts

All require `source venv/bin/activate`.

```bash
python3 shopify_theme_api.py themes|assets|get|backup|update|search
python3 shopify_graphql.py orders|order|apps
python baselinker_api.py orders|payments|sources|full
python sync_payment_id.py [--live]
```

Active Theme: GEN-6 global - slideshow (ID: 162539340108)

## SEO Project

Core technical SEO completed (Jan 2026). See `seo/SEO_PODSUMOWANIE_WDROZENIA.md` for summary.
Remaining: ~530 punctuation errors in scientific citations, footer typo "Cookkies". Strategic plan: `seo/Genactiv_SEO_Analiza_Rekomendacje.md`.

## Reports

Report generators in `reports/` directory. Run with `source venv/bin/activate && python3 reports/<script>.py`.
Key report: `reports/REMARKETING_AUDIT_2025-01-23.md` — attribution analysis (1% → 38.8% improvement).

## Key Documentation

- `docs/MIGRATION_PLAN_ONLINE.md` — Full migration specification (architecture diagrams, MCP configs)
- `docs/AUDYT_DANYCH_CHECKLIST.md` — Remarketing audit (5 phases, ~50 checkpoints)
- `docs/META_ADS_MCP_RESEARCH.md` — Meta Ads setup
- `google-ads-mcp/google-ads-mcp-server/README.md` — Google Ads MCP setup

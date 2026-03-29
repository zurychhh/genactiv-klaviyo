# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Client:** GenActiv.pl - Poland's #1 colostrum brand in pharmacies
**Platform:** Klaviyo + Shopify + Baselinker integration via MCP (Model Context Protocol)
**Primary Work:** HTML/CSS email template creation, campaign optimization, marketing automation, order/payment sync
**Web Terminal:** GenActiv Online — browser-based AI assistant deployed on Railway.app

## Architecture

```
genactiv-klaviyo/
├── genactiv-online/           # ★ Web AI terminal (Express + SSE + MCP, deployed on Railway)
│   ├── client/                #   Frontend: HTML, CSS, JS (dark terminal theme)
│   └── server/                #   Backend: Express, Anthropic API, MCP orchestrator
├── templates/snippets/        # Reusable email HTML components
├── google-ads-mcp/            # Google Ads MCP server (Python/FastMCP)
├── shopify-mcp-extended/      # Extended Shopify MCP with analytics (TypeScript, 15 tools)
├── seo/                       # SEO implementation project (COMPLETED: schema + metas)
├── reports/                   # Generated reports (dashboards, traffic, consistency)
├── docs/                      # Documentation (audit checklists, migration plan, Meta Ads)
├── dashboard-server/          # Dashboard backend (Node.js + MCP client) — legacy
├── dashboard/                 # Single-page dashboard HTML — legacy
├── chat-ui/                   # Chat UI frontend — legacy (replaced by genactiv-online)
├── theme_backups/             # Shopify theme file backups
├── .github/workflows/         # GitHub Actions (automated payment sync)
├── Dockerfile                 # Railway Docker build (Node 18 + Python 3 + uv)
├── railway.json               # Railway.app deployment config
├── baselinker_api.py          # Baselinker API client
├── shopify_graphql.py         # Shopify GraphQL client (transactions)
├── shopify_theme_api.py       # Shopify Theme API client
├── sync_payment_id.py         # Payment ID sync: Shopify -> Baselinker
├── generate_ga4_token.py      # GA4 OAuth token generator
└── venv/                      # Python virtual environment
```

## GenActiv Online (Web Terminal)

Browser-based AI assistant at `genactiv.oleksiakconsulting.com` — replaces local Claude Code CLI.

### Architecture
```
Browser → Express (auth + SSE) → Anthropic API ⇄ 6 MCP servers
                                                 ├── Klaviyo (Python/uvx)
                                                 ├── Shopify Extended (Node.js)
                                                 ├── Shopify Standard (Node.js)
                                                 ├── Meta Ads (Python)
                                                 ├── Google Ads (Python/FastMCP venv)
                                                 └── GA4 (Python/analytics-mcp)
```

### Two-Phase Query Routing
1. **Phase 1 (Router):** Haiku classifies query → selects target MCP server (~500 tokens)
2. **Phase 2 (Main):** Sonnet processes with only that server's tools (15-28 tools vs 93 total)

### Key Configuration (`genactiv-online/server/config.js`)
| Setting | Value |
|---------|-------|
| Main model | `claude-sonnet-4-20250514` |
| Router model | `claude-haiku-4-5-20251001` |
| Max tokens | 4096 |
| Tool result limit | 15,000 chars |
| History window | 6 messages (3 pairs) |
| Rate limiter | 3s minimum between API calls |
| Tool cache TTL | 5 minutes |
| Max tool rounds | 8 per conversation turn |

### File Structure
```
genactiv-online/
├── client/
│   ├── index.html              # Main page (Polish UI)
│   ├── style.css               # Dark terminal theme
│   └── terminal.js             # SSE client, markdown rendering, thinking indicator
├── server/
│   ├── index.js                # Express: auth, SSE streaming, health check
│   ├── config.js               # MCP servers, models, prompts, constants
│   ├── auth.js                 # Login (bcrypt + session, 24h expiry)
│   ├── mcp-orchestrator.js     # MCP connections, tool caching, result compression
│   └── anthropic-bridge.js     # Two-phase routing, retry logic, rate limiting
├── .env.example                # Env var template
├── package.json                # Dependencies
├── Dockerfile                  # Local Docker build
└── README.md                   # Polish documentation
```

### Local Development
```bash
cd genactiv-online
cp .env.example .env            # Fill in API keys
npm install
npm run dev                     # http://localhost:3000
# Login: admin / (password from AUTH_PASSWORD_HASH in .env)
```

### Railway Deployment
```bash
# WAŻNE: Railway CLI wymaga unset RAILWAY_TOKEN — stary token w env nadpisuje config
unset RAILWAY_TOKEN

# Deploy from project root (uses root Dockerfile + railway.json)
railway up

# Ustawianie zmiennych środowiskowych
railway variables set KEY=VALUE KEY2=VALUE2

# Logi
railway logs
```
- **Project:** cozy-trust | **Service:** exemplary-learning
- **URL:** `https://exemplary-learning-production-414a.up.railway.app`
- **Custom domain:** `genactiv.oleksiakconsulting.com` (CNAME → Railway)
- **Health check:** `GET /api/health` (no auth)

#### Railway CLI — rozwiązywanie problemów z logowaniem
Railway CLI (`/opt/homebrew/bin/railway` v4.30.3) odczytuje token z `~/.railway/config.json`.
Jeśli w środowisku shell istnieje zmienna `RAILWAY_TOKEN` (np. stary token), to **nadpisuje** config i powoduje błąd `Unauthorized`.

**Rozwiązanie:** Przed każdym wywołaniem `railway`:
```bash
unset RAILWAY_TOKEN
```
Weryfikacja: `railway whoami` powinno zwrócić email użytkownika.

Logowanie (gdy sesja wygaśnie):
```bash
railway login --browserless    # Daje link + kod do wklejenia na stronie Railway
```

### Docker Build (root `Dockerfile`)
Node 18 + Python 3 + uv → builds Shopify Extended MCP → builds Google Ads MCP venv → copies genactiv-online → installs meta-ads-mcp + analytics-mcp

### Environment Variables (`.env.example`)
```
AUTH_USERNAME, AUTH_PASSWORD_HASH       # Login credentials (bcrypt hash)
ANTHROPIC_API_KEY                       # Claude API (sk-ant-...)
KLAVIYO_API_KEY                         # Klaviyo private key (pk_...)
SHOPIFY_ACCESS_TOKEN                    # Shopify admin token (shpat_...)
MYSHOPIFY_DOMAIN                        # genactiv.myshopify.com
META_ACCESS_TOKEN                       # Meta Graph API token
GOOGLE_OAUTH_CLIENT_ID                  # Google OAuth (shared by Ads + GA4)
GOOGLE_OAUTH_CLIENT_SECRET              # Google OAuth secret
GOOGLE_ADS_DEVELOPER_TOKEN              # Google Ads dev token
GOOGLE_ADS_REFRESH_TOKEN                # Google Ads OAuth refresh token
GOOGLE_ADS_LOGIN_CUSTOMER_ID            # MCC ID: 2538328866
GA4_PROPERTY_ID                         # GA4 property: 279858535
GA4_REFRESH_TOKEN                       # GA4 OAuth refresh token
PORT, NODE_ENV, SESSION_SECRET          # Server config
```

### Known Issues & Solutions
- **429 Rate Limit:** Two-phase routing reduces payload from ~22k to ~1.8k tokens. Retry with 3s/6s/12s backoff.
- **Large tool results:** Auto-compressed (nulls stripped) and truncated at 15k chars.
- **Meta Ads MCP:** Sometimes fails to connect locally (Python module issue). Works on Railway.
- **Google OAuth tokens:** Expire when Google Cloud consent screen is in "Testing" mode (7 days). Po publication → tokeny nie wygasają. Regeneracja: `python generate_refresh_token.py` (Ads) / `python generate_ga4_token.py` (GA4).
- **Railway CLI auth:** Zawsze `unset RAILWAY_TOKEN` przed użyciem CLI (patrz sekcja wyżej).

## MCP Integrations

Seven MCP servers provide API access (6 active in genactiv-online, all 7 in local Claude Code):
- **Klaviyo MCP**: Email campaigns, flows, profiles, templates, metrics
- **Shopify MCP**: Products, customers, orders (standard tools)
- **Shopify Extended MCP**: Analytics - traffic sources, campaign performance, product performance
- **Google Ads MCP**: GAQL queries, keyword research (account: 339-338-2047)
- **Meta Ads MCP**: Facebook/Instagram campaigns, audiences, insights
- **GA4 MCP**: Analytics reports, realtime data (property: 279858535)
- **Chrome DevTools MCP**: Page inspection, screenshots, performance traces — local only

### Klaviyo MCP Tools
```
mcp__klaviyo__klaviyo_get_campaigns         # Campaigns (channel: email/sms)
mcp__klaviyo__klaviyo_get_campaign_report   # Campaign metrics (conversion_metric_id required)
mcp__klaviyo__klaviyo_get_flows             # Flows list
mcp__klaviyo__klaviyo_get_flow_report       # Flow metrics
mcp__klaviyo__klaviyo_get_profiles          # Profiles list
mcp__klaviyo__klaviyo_get_lists             # Subscription lists
mcp__klaviyo__klaviyo_get_segments          # Segments
mcp__klaviyo__klaviyo_get_metrics           # Available metrics
mcp__klaviyo__klaviyo_get_events            # Events (Viewed Product, etc.)
mcp__klaviyo__klaviyo_get_catalog_items     # Catalog products
mcp__klaviyo__klaviyo_create_email_template # Create template (full HTML + unsubscribe)
```

### Shopify MCP Tools
```
mcp__shopify__get-products                  # Products list (searchTitle, limit)
mcp__shopify__get-product-by-id             # Single product by ID
mcp__shopify__get-customers                 # Customers (searchQuery, limit)
mcp__shopify__get-orders                    # Orders (status, limit)
mcp__shopify__get-order-by-id               # Single order by ID
mcp__shopify__update-order                  # Update order (tags, note, etc.)
mcp__shopify__update-customer               # Update customer
mcp__shopify__get-customer-orders           # Orders for specific customer
```

### Shopify Extended MCP Tools
```
mcp__shopify-extended__get-traffic-source-analytics  # UTM/source breakdown for orders
mcp__shopify-extended__get-campaign-performance      # Campaign ROAS, revenue per source
mcp__shopify-extended__get-conversion-metrics        # Conversion rates by channel
mcp__shopify-extended__get-product-performance       # Product sales analytics
mcp__shopify-extended__get-customers                 # Extended customer data
mcp__shopify-extended__get-orders                    # Extended order data
mcp__shopify-extended__get-order-by-id               # Single order with full details
mcp__shopify-extended__get-customer-orders            # Orders for specific customer
mcp__shopify-extended__get-products                  # Product catalog
mcp__shopify-extended__get-product-by-id             # Single product details
mcp__shopify-extended__create-product                # Create product
mcp__shopify-extended__update-product-seo            # Update product meta title/description
mcp__shopify-extended__update-collection-seo         # Update collection meta title/description
mcp__shopify-extended__update-customer               # Update customer data
mcp__shopify-extended__update-order                  # Update order tags/notes
```

### Google Ads MCP Tools
```
mcp__google-ads__list_accounts              # List accounts
mcp__google-ads__run_gaql                   # Execute GAQL query
mcp__google-ads__run_keyword_planner        # Keyword research
```

### Meta Ads MCP Tools
```
mcp__meta-ads__get_campaigns                # Campaign list
mcp__meta-ads__get_insights                 # Performance insights (spend, ROAS, etc.)
mcp__meta-ads__get_ad_accounts              # Ad accounts
mcp__meta-ads__get_ads                      # Active ads
mcp__meta-ads__get_adsets                   # Ad sets
mcp__meta-ads__search_interests             # Interest targeting research
mcp__meta-ads__search_ads_archive           # Competitor ad research
```

### GA4 MCP Tools
```
mcp__ga4__run_report                        # Analytics report (sessions, users, etc.)
mcp__ga4__run_realtime_report               # Realtime data
mcp__ga4__get_account_summaries             # Account overview
mcp__ga4__get_property_details              # Property config
mcp__ga4__get_custom_dimensions_and_metrics # Custom dimensions
mcp__ga4__list_google_ads_links             # GA4-Ads linking status
```

## Local Python Scripts

All scripts require: `source venv/bin/activate`

### Baselinker Integration
```bash
python baselinker_api.py orders           # Recent orders
python baselinker_api.py payments <ID>    # Payment history
python baselinker_api.py sources          # Order sources
python baselinker_api.py full             # Orders + payments combined
```

### Shopify-Baselinker Payment Sync
```bash
python sync_payment_id.py                 # Dry run
python sync_payment_id.py --live          # Live sync
```

### Shopify GraphQL Client
Direct queries for transaction details not in MCP:
```bash
python3 shopify_graphql.py orders         # Orders with transactions
python3 shopify_graphql.py order <GID>    # Single order (gid://shopify/Order/...)
python3 shopify_graphql.py apps           # Installed apps
```

### Shopify Theme API
```bash
python3 shopify_theme_api.py themes              # List themes
python3 shopify_theme_api.py assets              # Files in active theme
python3 shopify_theme_api.py get <asset_key>     # Get file
python3 shopify_theme_api.py backup <asset_key>  # Backup before editing
python3 shopify_theme_api.py update <key> <file> # Update file
python3 shopify_theme_api.py search <term>       # Search in files
```
Active Theme: GEN-6 global - slideshow (ID: 162539340108)

## Shopify MCP Extended (TypeScript)

Local extension in `shopify-mcp-extended/` with custom analytics tools.

### Build Commands
```bash
cd shopify-mcp-extended
npm install                              # Install dependencies
npm run build                            # Build TypeScript → dist/
npm run dev                              # Dev mode with ts-node
npm test                                 # Run Jest tests
npm run lint                             # ESLint
```

### MCP Token Update
```bash
claude mcp remove shopify -s user
claude mcp add shopify -s user \
  -e SHOPIFY_ACCESS_TOKEN=shpat_YOUR_TOKEN \
  -e MYSHOPIFY_DOMAIN=genactiv.myshopify.com \
  -- node /Users/user/projects/genactiv-klaviyo/shopify-mcp-extended/dist/index.js
```

## GA4 Configuration

| Element | Wartość |
|---------|---------|
| Measurement ID | `G-KE8T99MGMJ` |
| Property ID (numeric) | `279858535` |
| Account ID | `73256159` |
| Property name | genactiv.pl – GA4 |

## Shopify Configuration

**Store:** `genactiv.myshopify.com` | **Gateway:** Przelewy24

## Klaviyo Template Development

### Requirements
- Inline CSS only, table-based layouts
- Max 600px desktop, min 320px mobile, stack on <480px
- Total size <100KB

### Template Variables
```django
{{ first_name|default:"" }}           # Personalization
{{ event.ProductName }}               # Cart abandonment
{{ event.Price|floatformat:0 }}       # PLN (no decimals)
{{ event.CompareAtPrice }}            # Original price
{% unsubscribe 'Anuluj subskrypcję' %}  # Required
```

### Creating via MCP
`mcp__klaviyo__klaviyo_create_email_template` requires:
- Complete HTML with `<html>` and `<body>` tags
- Unsubscribe link: `{% unsubscribe 'Anuluj subskrypcję' %}`
- Images: upload first via `klaviyo_upload_image_from_url`

## Brand Guidelines

| Element | Value |
|---------|-------|
| Brand Blue | `#0066CC` |
| GenActiv Red (CTAs) | `#EF3340` |
| Success Green | `#27ae60` |
| Trust Navy | `#1A3B5D` |
| Font | `'Branding-medium', Helvetica, Arial, sans-serif` |
| Language | Polish (PL) |
| Currency | PLN, no decimals |
| UTM | `?utm_source=klaviyo&utm_medium=email&utm_campaign=[name]` |

### Reusable Snippets
- `templates/snippets/product-card-abandoned-cart.html` - Product card with price comparison

## GitHub Actions

### Payment ID Sync
`.github/workflows/sync-payment-id.yml` syncs Payment ID Shopify → Baselinker
- Schedule: hourly (`0 * * * *`)
- Manual: workflow_dispatch
- Secrets: `SHOPIFY_DOMAIN`, `SHOPIFY_TOKEN`, `BASELINKER_TOKEN`

## Google Ads MCP Setup

Located in `google-ads-mcp/google-ads-mcp-server/`. See README.md there for full setup.
Required env vars: `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_OAUTH_CONFIG_PATH`

## Meta Ads Configuration

| Element | Value |
|---------|-------|
| Meta Pixel ID | `370142134442442` |
| Setup docs | `docs/META_ADS_MCP_RESEARCH.md`, `docs/META_ACCESS_TOKEN_INSTRUKCJA.md` |

## Pandectes Consent Banner

**Dashboard:** https://app.pandectes.io/
**GTM Container:** `GTM-5W5Z2ML`
**CRITICAL:** `cookiesBlockedByDefault=7` — all optional cookies blocked by default, causing 1% attribution rate

Consent Mode v2 mapping:
- `ad_storage`, `ad_personalization`, `ad_user_data` → Category 4 (Targeting) — DENIED by default
- `analytics_storage` → Category 2 (Performance) — DENIED by default
- `redactData: true` — IP/user IDs redacted without consent

Theme files: `assets/pandectes-settings.json`, `snippets/pandectes-rules.liquid`

## PDF Generation

WeasyPrint for invoice attachments:
```bash
source venv/bin/activate
python3 -c "from weasyprint import HTML; HTML('file.html').write_pdf('file.pdf')"
```

## Python Environment

```bash
source venv/bin/activate
# Packages: requests, weasyprint
```

## Reports & Dashboards

### Generated Reports (in `reports/`)
```bash
reports/dashboard_operacyjny_2026-03-02.html   # Operational dashboard (HTML)
reports/dashboard_operacyjny_2026-03-02.xlsx   # Operational dashboard (Excel)
reports/weryfikacja_zrodel_ruchu_20-26_02_2026.xlsx  # Traffic source verification
reports/raport_spojnosci_plan_napraw.xlsx      # Consistency report + repair plan
reports/REMARKETING_AUDIT_2025-01-23.md        # Remarketing deep-dive audit
```

### Report Generators
```bash
source venv/bin/activate
python3 reports/dashboard_operacyjny.py                # Generate operational dashboard
python3 reports/generate_raport_spojnosci.py           # Generate consistency report
python3 reports/weryfikacja_zrodel_ruchu_2026-02-20_26.py  # Traffic verification
```

### Dashboard Server (legacy — replaced by genactiv-online)
```bash
cd dashboard-server
node server.js                              # Start dashboard (port in .env)
# Connects to MCP servers for live data
```

## Migration Documentation

- `docs/MIGRATION_PLAN_ONLINE.md` — Full migration specification (26 KB, architecture diagrams, all MCP configs)
- `docs/migration_context.md` — Quick context summary for external developers
- `genactiv-online/README.md` — Polish quick-start guide

## Remarketing & Attribution Audit

**Status:** KRYTYCZNY — Attribution Rate = 1%
**Root cause:** Pandectes `cookiesBlockedByDefault=7` blocks targeting cookies
**Full report:** `reports/REMARKETING_AUDIT_2025-01-23.md`
**Audit checklist:** `docs/AUDYT_DANYCH_CHECKLIST.md` (5 phases, ~50 checkpoints)
**TODO:** `TODO_REMARKETING.md`

Key IDs:
- Google Ads Conversion ID: `AW-779033182`
- Meta Pixel: `370142134442442`
- Google Ads Manager: `253-832-8866`, Account: `339-338-2047`

## SEO Project

**Status:** Core technical SEO COMPLETED (Jan 2026)
**Summary:** `seo/SEO_PODSUMOWANIE_WDROZENIA.md`
**Plan:** `seo/SEO_IMPLEMENTATION_PLAN.md`

### Completed Tasks
1. BreadcrumbList Schema — 150+ pages via `snippets/breadcrumbs.liquid`
2. Collection Meta Descriptions — 24 collections via Shopify GraphQL API
3. Product Meta Descriptions — 8 products updated
4. FAQPage Schema — JSON-LD on `/pages/faq`

### Remaining SEO Work
- **Spelling typos (Priorytet 1):** ALL FIXED (verified live 2026-03-17) — "GENACITV", "prawidziwe", "Jeydnym", test FAQ entries, announcement bar
- **Punctuation errors (~530):** Still present — mostly in scientific citations (spaces before commas/periods, double spaces). See `seo/PELNY_RAPORT_BLEDOW_GENACTIV_FINAL.md`
- **FAQ Schema:** 3 duplicate FAQPage blocks (should be 1) — partially fixed
- **Footer typo:** "Polityka plików Cookkies" (double k) — visible on all pages, needs fix in theme
- **Strategic recommendations:** `seo/Genactiv_SEO_Analiza_Rekomendacje.md` (140k PLN / 6-month plan, awaiting approval)

### SEO Scripts
```bash
source venv/bin/activate
python3 seo/add_all_collection_metas.py        # Bulk add collection meta descriptions
python3 seo/full_site_spell_check.py           # Full site spellchecker (179 pages)
python3 seo/fix_genacitv_metafields.py         # Fix "GENACITV" typo in metafields
python3 seo/fix_collection_metas_from_word.py  # Apply metas from Word doc
```

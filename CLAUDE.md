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
├── klaviyo-mcp/               # Custom klaviyo-segments MCP server (Python/FastMCP)
├── sprint-2026-06/            # Sprint task tree (W1-W5 weeks, streams A-E)
├── scripts/                   # Daily agent runner, Teams notify, sprint scaffold
├── templates/design-system/   # Brand design system (colors, type, assets, email components)
├── templates/onboarding/      # 24 compiled onboarding email templates (A/B variants)
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

10 MCP servers configured in `.mcp.json`. Notable: **shopify-standard** and **shopify-extended** both run the same `shopify-mcp-extended/dist/index.js` binary (same tools, different routing labels). The web terminal (`config.js`) routes across 8 of these; `klaviyo-segments` is Claude Code-only.

| Server | Runtime | Command |
|--------|---------|---------|
| klaviyo | Python/uvx | `uvx klaviyo-mcp-server@0.4.0` (env: `PRIVATE_API_KEY`) |
| klaviyo-segments | Python/FastMCP | `venv/bin/fastmcp run klaviyo-mcp/server.py` (env: `KLAVIYO_API_KEY`) |
| shopify-extended | Node.js | `node shopify-mcp-extended/dist/index.js` |
| shopify-standard | Node.js | Same binary as shopify-extended |
| meta-ads | Python | `python3 -m meta_ads_mcp` |
| google-ads | Python venv | `venv/bin/fastmcp run server.py` |
| ga4 | Python | `analytics-mcp` |
| tiktok-ads | Python | `python3 -m tiktok_ads_mcp` |
| senuto | Node.js/npx | `npx -y senuto-mcp` |
| clarity | Node.js/npx | `npx @microsoft/clarity-mcp-server` |

**Startup behavior:** `config.js` auto-generates Google Ads and GA4 credential JSON files from environment variables at startup (lines 9-59). Missing tokens trigger console warnings but don't block other servers.

### Claude Code MCP Setup (local dev)

`.mcp.json` is gitignored (contains tokens). Setup for new machine:
1. Copy `.env.example` → `.env`, fill in tokens
2. Run `./setup-claude.sh` — generates `.mcp.json` from `.mcp.json.example` + `.env` tokens
3. Clarity MCP also loads from `.mcp.json` (token from `CLARITY_API_TOKEN` env var)

All 10 MCP servers are configured in `.mcp.json.example` with `__PLACEHOLDER__` format.

### MCP Tool Usage Notes

| Server | Key Notes |
|--------|-----------|
| Klaviyo | `campaign_report` requires `conversion_metric_id`. Templates need full HTML + `{% unsubscribe %}` |
| Shopify Extended | `bulk-update-seo` max 25 items, has dry-run mode |
| Google Ads | Customer ID: 10-digit, no dashes. `primaryForGoal` — ALWAYS check explicitly, don't assume ENABLED = Primary |
| Senuto | Default: domain="genactiv.pl", country_id="200" (Poland Base 2.0), fetch_mode="topLevelDomain" |
| Klaviyo Segments | Custom MCP in `klaviyo-mcp/`. 6 tools: `list_segments`, `get_segment`, `create_segment`, `create_rfm_segment`, `update_segment`, `delete_segment`. API revision `2026-01-15`. Placed Order metric ID: `R6aTMS`. Rate limits: 1/s, 15/min, 100/day for create. Condition logic: within group = OR, between groups = AND |
| Clarity | Project `3354986136401458`. Custom tags: `ab_theme_variant`, `theme_id`. JWT token (exp 2126). Limit: 10 req/day. Token passed as CLI arg, not env var |

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
| Shopify active theme | GEN-6 fix payment icons 2026-05-20 (ID: 199333609804) |
| Shopify app (Admin API) | Claude MCP (client: `01e7c03a4c2338052b3915eff6872c62`) |
| Shopify gateway | Przelewy24 |
| GA4 Measurement ID | `G-KE8T99MGMJ` |
| GA4 Property ID | `279858535` |
| Google Ads MCC | `253-832-8866` (env: `2538328866`) |
| Google Ads Account | `339-338-2047` (env: `3393382047`) |
| Google Ads Conversion ID | `AW-779033182` |
| Meta Pixel ID | `370142134442442` |
| GTM Container | `GTM-5W5Z2ML` |

## Claude Code Agent System

`.claude/agents/` contains two agent definitions used by the daily autonomous runner:

**orchestrator** (`orchestrator.md`) — Daily operational agent. 6-step cycle: pull tasks from Monday.com board "Sprint Czerwiec 2026" → triage (GOTOWE/BLOKADA_CZLOWIEK/BLOKADA_ZALEZNOSC) → escalate blocks via Teams webhook → execute GOTOWE tasks via task-runner subagent → update Monday → daily report to `reports/daily/{{DATE}}.md`.

**task-runner** (`task-runner.md`) — Executes a single sprint task. Receives `TASK_ID`, `TASK_DIR`, `DEFINITION_OF_DONE`, `PROMPT` from orchestrator. Returns structured `TASK_RESULT` block with status (done/needs-verify/failed). Guardrails: SEO bulk-update always dry-run first, theme changes always backup first, YMYL content never auto-publish.

**DRY_RUN mode** (default=1): reads Monday, simulates, writes only local files. `DRY_RUN=0`: full execution with MCP writes.

`.claude/settings.local.json` — Local permissions (allow list for MCP tools + Bash commands).

## Sprint System

`sprint-2026-06/` — Task tree organized by week (W1-W5) and stream:

| Stream | Focus |
|--------|-------|
| A | SEO/Organic (keyword research, bulk fixes, content engine) |
| B | Mobile UX (Clarity heatmaps, A/B test) |
| C | Klaviyo flows (RFM segments, Post-Purchase, Win-Back, cadence) |
| D | Subscriptions (Recharge/Bold/Skio research, bundles) |
| E | LP Generator (Liquid templates, Shopify Pages API) |

Each task directory contains `task.md` (definition + Claude Code prompt), `status.txt` (pending/done/failed), `artefakty/` (output artifacts). Owner labels: `CC` (fully automated), `CC+` (human QA needed), `MAN` (manual only).

Source CSV: `research/sprint-czerwiec-2026-tasks.csv`. Scaffold: `python3 scripts/scaffold-sprint.py`.

## Daily Agent Scripts

`scripts/` — Autonomous daily runner infrastructure:

- `runner.sh` — Creates git worktree at `/tmp/genactiv-agent-YYYY-MM-DD`, runs `claude -p` headless with `--agent orchestrator`, copies artifacts back, commits, removes worktree
- `notify.sh` — Teams Adaptive Card webhook (POST JSON). Functions: `notify_block` (attention) and `notify_report` (good, reads markdown up to 2000 chars)
- `scaffold-sprint.py` — Generates sprint tree from CSV (idempotent)
- `com.genactiv.dailyagent.plist` — macOS launchd config, runs at 07:00 daily

| Env Variable | Default | Description |
|-------------|---------|-------------|
| `DRY_RUN` | `1` | `1` = simulate, `0` = full execution |
| `BUDGET` | `5` | Max API spend in USD (`--max-budget-usd`) |
| `TEAMS_WEBHOOK_URL` | (empty) | Teams webhook — if empty, skips notifications |

## Design System & Email Standards

`templates/design-system/` — Full brand design system reconstructed from genactiv.pl. Includes `SKILL.md` (Claude Code skill: `genactiv-design`), `styles.css` (design tokens), `assets/` (logos, product photos, expert portraits), `emails/` (JSX email components for onboarding, cross-sell, A/B tests), `ui_kits/storefront/` (React components).

`templates/design-system/emails/design_handoff_recurring_emails/KLAVIYO_CODING_STANDARD.md` — Full Klaviyo email HTML coding standard (boilerplate, typography, bulletproof buttons, dark mode, pre-publish checklist). **Read this before creating any email template.**

`templates/onboarding/` — 24 compiled HTML email templates: Newsletter Nurture (NurOnb1-5 A/B) and Post-Purchase Onboarding (PurOnb1-5 A/B). Architecture in `ONBOARDING_PLAN_v2.md`. Known factual errors tracked in `ONBOARDING_REVIEW.md` (wrong Fiberbiom price/size, free shipping threshold is 300 zl not 99 zl).

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
| GenActiv Red (CTAs) | `#F5333F` (design system canonical; legacy refs may show `#EF3340`) |
| Fiberbiom Pink | `#F5669C` |
| Success Green | `#27ae60` |
| Trust Navy | `#1A3B5D` |
| Body text | `#1C1B1B` (warm near-black) |
| Background/cream | `#F4F1EE` |
| Font | `'Branding-medium', Helvetica, Arial, sans-serif` (substitute: Montserrat) |
| UTM | `?utm_source=klaviyo&utm_medium=email&utm_campaign=[name]` |

## Environment Variables

See `genactiv-online/.env.example` for full list. Key groups:
- `AUTH_USERNAME`, `AUTH_PASSWORD_HASH` — bcrypt login credentials
- `ANTHROPIC_API_KEY` — Claude API
- `KLAVIYO_API_KEY`, `SHOPIFY_ACCESS_TOKEN`, `MYSHOPIFY_DOMAIN` — core integrations
- `META_ACCESS_TOKEN` — Meta Graph API
- `GOOGLE_OAUTH_CLIENT_ID`, `GOOGLE_OAUTH_CLIENT_SECRET` — shared by Google Ads + GA4
- `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_REFRESH_TOKEN`, `GOOGLE_ADS_LOGIN_CUSTOMER_ID`
- `GA4_PROPERTY_ID`, `GA4_REFRESH_TOKEN` — web terminal uses refresh token; MCP server uses gcloud ADC at `~/.config/gcloud/application_default_credentials.json`
- `TIKTOK_APP_ID`, `TIKTOK_SECRET`, `TIKTOK_ACCESS_TOKEN` — 24h expiry, auto-refreshed
- `INTELLIGEMS_API_KEY` — `ig_live_...`, header: `intelligems-access-token`, endpoint: `api.intelligems.io/v25-10-beta`
- `SENUTO_API_KEY` — JWT, exp ~Sep 2026
- `TEAMS_WEBHOOK_URL` — Teams webhook for daily agent notifications (optional)
- `BUDGET` — Max daily agent API spend in USD (default: 5)

## Known Issues

- **Google OAuth tokens** expire in 7 days when Google Cloud consent screen is in "Testing" mode. After publication, tokens don't expire. Regenerate with `python generate_refresh_token.py` (Ads) or `python generate_ga4_token.py` (GA4).
- **Meta Ads MCP — locally use `npx -y meta-ads-mcp` (Node), NOT the Python package.** The PyPI `meta-ads-mcp` pins `mcp==1.23.0`, which conflicts with `fastmcp 3.x` and breaks the root-venv servers (klaviyo-segments). Do NOT `pip install meta-ads-mcp` into the root `venv/`. Works on Railway (installed globally there, isolated from the root venv).
- **Root `venv/` must stay on `fastmcp==3.4.2` + `mcp==1.27.2`** (required by `klaviyo-segments`, run via `venv/bin/fastmcp run klaviyo-mcp/server.py`). Symptom if broken: `/doctor` → "1 setup issue: MCP", klaviyo-segments "Failed to connect", ImportError on `streamable_http_client` / "FastMCP client support is not installed". Fix: `./venv/bin/pip install fastmcp==3.4.2 mcp==1.27.2` then `./venv/bin/pip uninstall -y meta-ads-mcp`; verify with `./venv/bin/pip check`. Pinned in `setup-claude.sh` and `klaviyo-mcp/requirements.txt`. Restart Claude Code after fixing (MCP connections are cached at startup).
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

Active Theme: GEN-6 fix payment icons 2026-05-20 (ID: 199333609804)

## SEO Project

Core technical SEO completed (Jan 2026). See `seo/SEO_PODSUMOWANIE_WDROZENIA.md` for summary.
Remaining: ~530 punctuation errors in scientific citations, footer typo "Cookkies". Strategic plan: `seo/Genactiv_SEO_Analiza_Rekomendacje.md`.

### SEO+GEO Sprint (July 2026)

Full plan: `reports/seo-geo-plan-wdrozenia.html`. Blocks A+B+C1 completed 2026-07-16:

**Block A (product data):** 6x FIBERBIOM meta fixes (4 titles + 2 descriptions — dwupak "30 saszetek"), double-comma fix Colostrum kapsulki, 21 ALT texts (5 Colostrum brzoskwinia + 16 FIBERBIOM). Rollback snapshot: `sprint-2026-06/W1/A1/artefakty/seo-snapshot-before-changes-2026-07-16.json`.

**Block A+ (2026-07-17):** Additional SEO fixes deployed via `genactiv-seo` framework:
- 4 missing ALT texts: 2 zestawy (Colostrum brzoskwinia + Fiberbiom), 2 dwupaki Colostrum A2. ALT coverage: 97% → 99%.
- 4 meta titles shortened to ≤60 chars: zestawy + dwupaki A2 (were 61-68 chars).
- 1 meta title bug fix: Zestaw porzeczka had wrong flavor ("ananasem" → "porzeczka").
- Bug fix in `shopify-mcp-extended/src/tools/updateProductImages.ts`: added ProductImage → MediaImage GID auto-mapping (query `media` alongside `images`, match by URL). Without this fix, ALT updates fail silently because `productUpdateMedia` requires MediaImage GIDs but audit/get-product return ProductImage GIDs.

**Block B (schema):** JSON-LD fixes in 3 theme files (product-template, header, article-template): brand Brand, gtin13+mpn, all images, http→https, sameAs filter, shippingDetails (PL, free >300 PLN), returnPolicy (14 days, free), Article schema with publisher.logo + mainEntityOfPage. Breadcrumb ogonek: collection "Blonnik" → "Błonnik". Backups: `sprint-2026-06/W1/A1/artefakty/theme-backup-2026-07-16/`. Skipped: B2 (author expert — needs data), B7 (Organization details — needs data), B8 (aggregateRating — SSW widget handles).

**Block C1 (llms.txt):** Custom brand page at `https://genactiv.pl/pages/llms-txt` (template `page.llms-txt.liquid` with `layout: none`). Page ID: 732391014732. Shopify's own UCP at `/llms.txt` is not overridable.

**Remaining:** C2 (dateModified), C3 (robots.txt check — admin), C4-C7 (4 articles — copywriter + review). Audyt kolekcji (SEO) jeszcze nie uruchomiony. Blok B do wdrożenia (wymaga theme write scope).

### Shopify GraphQL SEOInput — CRITICAL

When using `productUpdate` mutation with `seo` input, **always send both `title` AND `description`**. Omitting a field clears it to null — this is NOT a "keep existing" behavior. Example:
```graphql
# WRONG — clears description:
productUpdate(input: { id: "...", seo: { title: "new title" } })
# CORRECT — preserves description:
productUpdate(input: { id: "...", seo: { title: "new title", description: "existing desc" } })
```

## A/B Test: GEN-6 vs NOTOAGENCY (June 2026) — COMPLETED

Test of old theme (GEN-6) vs new theme (NOTOAGENCY) ran June 8-30, 2026 via Intelligems. **28,195 visitors, 661 orders, 80/20 split.** Test is now **closed** — GEN-6 at 100%.

### Result

| Metric | GEN-6 (control) | NOTOAGENCY | Δ | Significance |
|--------|-----------------|------------|---|-------------|
| Conversion Rate | 2.43% | 1.92% | **-20.9%** | **p=0.025 SIGNIFICANT** |
| Add to Cart | 5.46% | 4.92% | -9.9% | not significant |
| Abandoned Checkout | 32.2% | 38.9% | **+21.1%** | — |
| Revenue/visitor | 5.82 PLN | 4.61 PLN | **-20.7%** | p=0.085 borderline |

**Loss is concentrated in one screen — the product card with variant selection:**
- Capsules 120 pcs mobile: **-47%** (variant change triggers full page reload)
- Capsules 60 pcs mobile: **-63%** (same cause)
- Powder (no variant choice): **+9%** (proof the variant selector is the problem)
- Homepage: **+15%** (NOTO wins)
- Meta Ads (main budget): **parity / +5%** (safe)

### Decision & Next Steps

NOTO theme **on hold** — not deployable in parts (Shopify themes are all-or-nothing). Plan:
1. Rebuild product card inside NOTO theme (fix variant selector, add sticky ATC, pill buttons)
2. Optimize PageSpeed / Core Web Vitals
3. Re-test entire NOTO theme vs GEN-6
4. Deploy entire theme at once after confirmed win

### 9 Priorities for NOTO Rebuild

| P | Change | Owner | Expected Lift |
|---|--------|-------|--------------|
| P1 | **Section Rendering API** — zero reload on variant change | DEV | +25-40% ATC |
| P2 | **Pill buttons** instead of dropdown | GRAFIK | +15-20% ATC |
| P3 | **Sticky ATC bar** mobile (IntersectionObserver) | GRAFIK+DEV | +8-15% ATC |
| P4 | **Above-the-fold layout** PDP mobile (550px rule) | GRAFIK | +14-19% ATC |
| P5 | **Fix dead clicks ATC** (553/month, JS error) | DEV | fix |
| P6 | **Clickable product names** on listings (4,944 dead clicks) | DEV | fix |
| P7 | **Bottom navigation bar** (5 items, replaces hamburger 1.5% usage) | GRAFIK+DEV | +15-20% nav |
| P8 | **Homepage above-the-fold** (compact hero + category tiles) | GRAFIK | -16% quick back |
| P9 | **PageSpeed + Core Web Vitals** (LCP<2.5s, INP<200ms, CLS<0.1) | DEV | CWV pass |

### Theme IDs

| Theme | Shopify ID | Status |
|-------|-----------|--------|
| GEN-6 fix payment icons (active, production) | 199333609804 | **LIVE** |
| GEN-6 global - slideshow (original) | 162539340108 | Inactive |
| NOTOAGENCY | 190479794508 | On hold, needs product card rebuild |

### Key Artifacts

| File | Description |
|------|-------------|
| `docs/AB_TEST_RAPORT.md` | Full A/B test report (config, tracking fixes, results, funnel analysis, diagnosis) |
| `docs/REKOMENDACJE_KARTA_PRODUKTU_MENU.md` | 9 priorities with specs for GRAFIK + DEV (Section Rendering API, pill buttons, sticky ATC, bottom nav, PageSpeed) |
| `reports/AB_TEST_WERYFIKACJA_2026-06-16.html` | Data verification report (tracking fix validation) |
| `reports/roadmapa-H2-2026.tsv` | H2 2026 strategic roadmap (revenue targets, Marketing Automation, SEO, CRO, Retention) |

### Intelligems Integration

| Setting | Value |
|---------|-------|
| Experiment ID | `1c371ad8-5826-4c21-abdb-7d0d68390e81` |
| API | `api.intelligems.io/v25-10-beta`, header: `intelligems-access-token` |
| Env var | `INTELLIGEMS_API_KEY` (`ig_live_...`) |
| MCP server | Available at `https://ai.intelligems.io/mcp` (OAuth2, not yet connected) |

### Clarity A/B Limitations

Custom tags (`ab_theme_variant`, `theme_id`) are **NOT available via Clarity API** — only visible in Clarity UI (Filters → Custom Tags). The native Intelligems → Clarity integration was **never enabled** (requires manual toggle by d.slowik@notoagency.pl).

## H2 2026 Roadmap (Strategic Context)

**Goal:** +50% e-commerce revenue (PLN 222K/mo → PLN 334K/mo average). Full roadmap: `reports/roadmapa-H2-2026.tsv`.

| Stream | July Focus | H2 End Goal |
|--------|-----------|-------------|
| Marketing Automation | Post-purchase flow, RFM, campaigns 2×/wk | Lista 14K (from 7.9K), rev share 12% (from 5.1%), 14 flows |
| SEO | Content hub (4 articles), keyword×product mapping | Organic +65% (9.7K→16K sessions), CR 2.3% |
| eCommerce / CRO | Mobile CR 2.09%→2.30%, trust badges, sticky ATC A/B | CR 3.10% (from 2.34%), Mobile 2.80%, AOV 305 |
| Retention / Sub | Platform selection (Recharge/Bold/Skio), 3 bundles | Loyalty LIVE, sub 3+ products, repeat 62% (from 55%) |
| Product | Margin analysis, cross-sell pairs | AOV 305 (from 272), items/order 1.8 |

**Key milestones:** Sub launch (Aug), Referral launch (Sep), Pre-BF +2K subs (Oct), BF PLN 400K+ (Nov), Loyalty launch (Dec).

## Reports

Report generators in `reports/` directory. Run with `source venv/bin/activate && python3 reports/<script>.py`.
Key report: `reports/REMARKETING_AUDIT_2025-01-23.md` — attribution analysis (1% → 38.8% improvement).

## Key Documentation

- `docs/MIGRATION_PLAN_ONLINE.md` — Full migration specification (architecture diagrams, MCP configs)
- `docs/AUDYT_DANYCH_CHECKLIST.md` — Remarketing audit (5 phases, ~50 checkpoints)
- `docs/META_ADS_MCP_RESEARCH.md` — Meta Ads setup
- `docs/AB_TEST_RAPORT.md` — A/B test GEN-6 vs NOTOAGENCY (full report)
- `docs/REKOMENDACJE_KARTA_PRODUKTU_MENU.md` — Product card + menu rebuild specs (9 priorities)
- `google-ads-mcp/google-ads-mcp-server/README.md` — Google Ads MCP setup

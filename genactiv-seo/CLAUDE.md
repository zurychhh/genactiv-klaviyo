# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Agent package for SEO + GEO (AI-search) optimization of **Genactiv** — Poland's #1 colostrum brand in pharmacies. Shopify store connected via MCP with **write access**. Market: PL, currency: PLN, language: Polish.

This is NOT a traditional codebase — it's a set of agent definitions, commands, knowledge files, and a reporting template. Agents implement changes directly on the live Shopify store through MCP tools.

## Golden Rules

1. **YMYL / Health niche.** Highest E-E-A-T standard. No health content goes live without `seo-eeat-compliance` agent approval.
2. **Health claims = hard constraint.** Rulebook: `.claude/seo/health-claims-pl.md`. Colostrum has NO approved health claims in EU. When in doubt: "DO WERYFIKACJI PRAWNEJ" — never guess.
3. **Implement, don't just recommend.** Shopify MCP has WRITE access. Always follow `.claude/seo/implementation-rules.md`: show BEFORE/AFTER, wait for confirmation, log change, one-at-a-time (not bulk).
4. **GEO by default.** Optimize for Google AND AI-search (ChatGPT, Perplexity, AI Overviews, Gemini). Every agent applies `.claude/seo/geo-playbook.md`.
5. **First-party data > model opinion.** Prefer GA4 and (when available) GSC over general knowledge. Never fabricate search volumes or rankings.
6. **Conversion, not vanity traffic.** This is a store — prioritize revenue-driving queries and pages.
7. **Sources required.** Research claims need citations; competitive analysis needs URLs.

## Repository Structure

```
genactiv-seo/
├── CLAUDE.md                   # This file
├── README.md                   # Human onboarding (installation, agent list, command list)
├── templates/
│   └── dashboard.html          # Self-contained HTML report template (Chart.js)
├── reports/                    # Output folder for /report command
│   └── README.md
├── .claude/agents/             # 12 specialist agent definitions (.md)
├── .claude/commands/           # 12 workflow commands (.md)
└── .claude/seo/                # Knowledge base
    ├── health-claims-pl.md     # EU health claims rulebook for colostrum
    ├── implementation-rules.md # BEFORE/AFTER protocol, safety guardrails
    ├── geo-playbook.md         # AI-search optimization strategy
    ├── stack.md                # Current tool availability (Shopify, GA4, GSC status)
    ├── changelog.jsonl         # Change audit trail (append-only)
    ├── changelog-schema.md     # Schema for changelog entries
    ├── cadence.md              # Weekly/monthly/quarterly routine
    └── gsc-activation.md       # Google Search Console setup guide
```

Note: `.claude/` directories with agent/command/knowledge files may not yet exist if the package hasn't been fully scaffolded. The README.md documents all 12 planned agents and 11 commands.

## Architecture

### Agent Delegation Model

The system uses a **specialist delegation** pattern:

```
User → seo-orchestrator → delegates to specialist agent
                           ├── seo-tech-auditor        (Shopify MCP audits + fixes)
                           ├── seo-content-strategist   (research + writing + MCP publish)
                           ├── seo-geo-specialist       (AI-search citability)
                           ├── seo-schema-specialist    (JSON-LD via MCP)
                           ├── seo-data-analyst         (GA4 + Shopify analytics)
                           ├── seo-internal-linking     (cluster mapping + MCP linking)
                           ├── seo-eeat-compliance      (MANDATORY gate for health content)
                           ├── seo-reporter             (impact reports + HTML dashboard)
                           ├── seo-measurement-qa       (GA4/Shopify measurement validation)
                           ├── seo-reviews              (review program strategy)
                           └── seo-product-feed         (Google Shopping + AI data)
```

Agents with data/write access intentionally omit `tools` in frontmatter (inherit all session MCP tools). To restrict: add explicit `tools:` list with `mcp__<server>__<tool>` names.

### Relationship to Parent Project

This package lives inside `genactiv-klaviyo/` which has its own `.claude/agents/` (orchestrator + task-runner for daily sprint execution from Monday.com). The parent orchestrator can delegate SEO tasks to agents in this package.

### Measurement Pipeline

```
MCP write → log to .claude/seo/changelog.jsonl
                            ↓
/report command → seo-reporter agent
                            ↓
    GA4 data (organic sessions, conversions, revenue) per page
                            ↓
    reports/report-YYYY-MM-DD.md    (shareable markdown)
    reports/dashboard-YYYY-MM-DD.html (interactive browser dashboard)
```

Attribution honesty: correlation ≠ causation, supplement seasonality noted, maturation window acknowledged, no CTR/position data without GSC.

### Dashboard Template Data Format

`templates/dashboard.html` is self-contained (Chart.js via CDN). The `seo-reporter` agent replaces only the `REPORT_DATA` JavaScript object:

```javascript
const REPORT_DATA = {
  brand: "Genactiv",
  period: "16 cze – 13 lip 2026",
  generated: "2026-07-13",
  kpis: [
    { label: "Sesje organic", before: 12030, after: 14880, unit: "" },
    { label: "Konwersje", before: 214, after: 297, unit: "" },
    { label: "Przychód organic", before: 41200, after: 58900, unit: "PLN" },
    { label: "Widoczność GEO", value: "3 / 5", sub: "cytowania w AI-search" }
  ],
  timeline: {
    labels: ["T1", "T2", ...],        // week labels
    organicSessions: [2800, 2950, ...], // weekly values
    conversions: [48, 53, ...]
  },
  markers: [{ label: "T-004", text: "Meta tagi FIBERBIOM" }], // implementation markers
  tasks: [{
    id: "T-004", date: "2026-06-18", target: "/products/fiberbiom",
    change: "Meta title + description", kpi: "CTR organic",
    before: "1.8%", after: "2.4%", status: "live"  // or "reverted" or "draft"
  }],
  geo: [{ q: "najlepszy suplement na jelita", cited: true, engine: "Perplexity" }],
  caveats: "Brak GSC — pozycje i CTR niedostępne..."
};
```

Status pills: `.live` (green), `.reverted` (red), `.draft` (navy). Delta badges: `.up` (green), `.down` (red), `.flat` (gray).

## Available Commands

| Command | Purpose |
|---------|---------|
| `/seo-audit [scope]` | Full audit (tech + schema + GEO + links + E-E-A-T) |
| `/geo-audit [scope]` | AI-search visibility audit + plan |
| `/optimize-product [handle]` | Full product optimization with MCP implementation |
| `/content-brief [phrase]` | Content brief with research and compliance gate |
| `/schema-check [page]` | JSON-LD audit + generation/implementation |
| `/ga4-insights [range]` | GA4/Shopify insights → actionable recommendations |
| `/report [period]` | Impact report → markdown + HTML dashboard |
| `/log-change [description]` | Manual changelog entry (for changes made outside Claude Code) |
| `/measurement-qa [window]` | Validate measurement reliability before reporting |
| `/quick-wins [scope]` | Near-ranking + CTR gaps (requires GSC) |
| `/indexnow [urls]` | Notify Bing/IndexNow of changes (GEO) |

Start point when unsure: delegate to `seo-orchestrator`.

## Current Stack

- **Shopify**: MCP read + write. Store: `genactiv.myshopify.com`. Active theme ID: `199333609804`.
- **GA4**: Property `279858535`, Measurement ID `G-KE8T99MGMJ`.
- **Google Search Console**: Not yet connected. Agents ready. Activation guide: `.claude/seo/gsc-activation.md`.
- **No Ahrefs/Semrush**: Free research + "bring your own data" approach.

## Safety Protocol (Live Store)

Before any MCP write:
1. Show BEFORE/AFTER diff
2. Wait for user confirmation
3. Execute single change
4. Log to `.claude/seo/changelog.jsonl`

Health content: always route through `seo-eeat-compliance` before publishing. Bulk changes: only with explicit consent. Never modify prices, inventory, or order status without conscious approval.

## Shopify SEOInput Warning

When using `productUpdate` mutation with `seo` input, **always send both `title` AND `description`**. Omitting a field clears it to null (not "keep existing"):

```graphql
# WRONG — clears description:
productUpdate(input: { id: "...", seo: { title: "new title" } })
# CORRECT:
productUpdate(input: { id: "...", seo: { title: "new title", description: "existing desc" } })
```

## Current SEO Audit Status (2026-07-17)

Products audited: 50. Issues remaining: **1** (phantom image reference, unfixable).

| Metric | Before (17 lip AM) | After (17 lip PM) |
|--------|--------------------|--------------------|
| SEO issues | 9 | 1 |
| ALT coverage | 97% (148/153) | 99% (152/153) |
| Long meta titles | 4 | 0 |
| Meta title bugs | 1 (wrong flavor) | 0 |

### Changes deployed 2026-07-17

| Change | Products | Method |
|--------|----------|--------|
| 4 ALT texts added | Zestaw brzoskwinia+porzeczka, Zestaw brzoskwinia+ananas, A2 proszek dwupak, A2 kapsułki dwupak | Direct GraphQL (MCP bug workaround) |
| 4 meta titles shortened (≤60 zn.) | Same 4 products | `update-product-seo` MCP |
| 1 meta title flavor fix | Zestaw porzeczka ("ananasem" → "porzeczka") | `update-product-seo` MCP |

### Known MCP Bug (fixed, awaiting restart)

`shopify-mcp-extended/src/tools/updateProductImages.ts` — `productUpdateMedia` mutation requires `MediaImage` GIDs but audit and get-product return `ProductImage` GIDs (different numeric IDs for the same image). Fix: query `media(first: 50)` alongside `images`, build URL-based mapping ProductImage → MediaImage. Fix is built (`npm run build` done) but requires MCP server restart to take effect.

## Routine

See `.claude/seo/cadence.md` for weekly/monthly/quarterly schedule. Implementation priority order: measurement QA → GSC connection → Bing/IndexNow → reviews → product feed.

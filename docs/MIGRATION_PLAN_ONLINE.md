# GenActiv Klaviyo — Dokumentacja migracji do środowiska online

**Data:** 2026-03-23
**Cel:** Przeniesienie lokalnego środowiska Claude Code + MCP na serwer w chmurze z webowym terminalem
**Dla:** Zewnętrzny developer / zespół wdrożeniowy

---

## 1. CO TO JEST I JAK DZIAŁA (AKTUALNIE)

### 1.1 Architektura obecna

```
┌─────────────────────────────────────────────────────────────────┐
│  LOKALNY MAC (macOS Darwin 24.6.0)                              │
│                                                                  │
│  ┌──────────────┐     stdio      ┌─────────────────────────┐   │
│  │ Claude Code   │◄─────────────►│ MCP Server: Klaviyo     │   │
│  │ (CLI terminal)│◄─────────────►│ MCP Server: Shopify Ext │   │
│  │               │◄─────────────►│ MCP Server: Google Ads  │   │
│  │  Model:       │◄─────────────►│ MCP Server: Meta Ads    │   │
│  │  Claude Opus  │◄─────────────►│ MCP Server: GA4         │   │
│  │  (API call)   │◄─────────────►│ MCP Server: Chrome DevT │   │
│  └──────┬───────┘               └─────────────────────────┘   │
│         │                                                       │
│  ┌──────▼───────┐     ┌──────────────┐   ┌──────────────┐     │
│  │ chat-ui       │     │ dashboard-   │   │ Python       │     │
│  │ (Express+WS)  │     │ server       │   │ scripts      │     │
│  │ port 3000     │     │ port 3001    │   │ (venv)       │     │
│  └──────────────┘     └──────────────┘   └──────────────┘     │
└─────────────────────────────────────────────────────────────────┘
          │                     │
          ▼                     ▼
    Anthropic API         Zewnętrzne API:
    (Claude model)        Shopify, Klaviyo, Google Ads,
                          Meta Ads, GA4, Baselinker
```

### 1.2 Jak to działa

1. **Claude Code** = CLI od Anthropic, działa w terminalu. Użytkownik pisze polecenia w języku naturalnym.
2. Claude Code łączy się z **Anthropic API** (model Claude Opus) i z **7 serwerami MCP** przez stdio.
3. **MCP (Model Context Protocol)** = open standard Anthropic. Każdy MCP server to osobny proces, który Claude odpytuje przez stdin/stdout w formacie JSON-RPC.
4. **chat-ui** = prosta nakładka webowa (Express + WebSocket) — uruchamia `claude -p <query>` jako child process.
5. **dashboard-server** = backend REST API, który bezpośrednio importuje narzędzia Shopify Extended i łączy się z 4 MCP serwerami.

### 1.3 Czego oczekuje klient po migracji

- **Webowy terminal** do wpisywania poleceń i pracy z narzędziami MCP (jak obecny Claude Code CLI, ale w przeglądarce)
- Zachowanie wszystkich 7 połączeń MCP
- Dostępność 24/7 z dowolnego urządzenia
- Bez konieczności trzymania włączonego Maca

---

## 2. SERWERY MCP — PEŁNA SPECYFIKACJA

### 2.1 Tabela zbiorcza

| # | Serwer | Język | Transport | Źródło | Auth |
|---|--------|-------|-----------|--------|------|
| 1 | **Klaviyo** | Python | stdio | `uvx klaviyo-mcp-server@0.4.0` (PyPI) | API Key |
| 2 | **Shopify Extended** | TypeScript/Node | stdio | Lokalny kod (`shopify-mcp-extended/`) | API Token |
| 3 | **Google Ads** | Python (FastMCP) | stdio | Lokalny kod (`google-ads-mcp/`) | OAuth 2.0 + Dev Token |
| 4 | **Meta Ads** | Python | stdio | `python -m meta_ads_mcp` (pip) | Access Token |
| 5 | **GA4** | Binary | stdio | `analytics-mcp` (standalone) | OAuth 2.0 (ADC) |
| 6 | **Chrome DevTools** | Node.js | stdio | `npx chrome-devtools-mcp` (npm) | None (CDP) |
| 7 | **Shopify Standard** | Node.js | stdio | Z pakietu Shopify Extended | API Token |

### 2.2 Klaviyo MCP

```yaml
command: uvx
args: ["--with", "fastmcp>=2.8.0,<3.0.0", "klaviyo-mcp-server@0.4.0"]
env:
  PRIVATE_API_KEY: "pk_***"        # Klaviyo Private API Key
  READ_ONLY: "false"
  ALLOW_USER_GENERATED_CONTENT: "true"
```

**Narzędzia (11):** get_campaigns, get_campaign_report, get_flows, get_flow_report, get_profiles, get_lists, get_segments, get_metrics, get_events, get_catalog_items, create_email_template, upload_image_from_url, upload_image_from_file, get_email_template, create_campaign, create_event, create_profile, subscribe_profile_to_marketing, unsubscribe_profile_from_marketing, update_profile, get_account_details

**Zależności:** `uvx` (Python package runner, część `uv`), `fastmcp>=2.8.0,<3.0.0`

### 2.3 Shopify Extended MCP (LOKALNY KOD)

```yaml
command: node
args: ["/path/to/shopify-mcp-extended/dist/index.js"]
env:
  SHOPIFY_ACCESS_TOKEN: "shpat_***"
  MYSHOPIFY_DOMAIN: "genactiv.myshopify.com"
```

**Narzędzia (15):** get-products, get-product-by-id, get-customers, get-orders, get-order-by-id, get-customer-orders, create-product, update-product-seo, update-collection-seo, update-customer, update-order, get-traffic-source-analytics, get-campaign-performance, get-conversion-metrics, get-product-performance

**Zależności Node.js (package.json):**
```json
{
  "@modelcontextprotocol/sdk": "^1.17.1",
  "dotenv": "^16.0.3",
  "graphql": "^16.6.0",
  "graphql-request": "^5.1.0",
  "minimist": "^1.2.8",
  "zod": "^3.21.4"
}
```

**Node version:** `>=18.0.0`
**Shopify API version:** `2023-07`
**Build:** `npm run build` (TypeScript → `dist/`)

### 2.4 Google Ads MCP (LOKALNY KOD)

```yaml
command: fastmcp
args: ["run", "server.py"]
cwd: "/path/to/google-ads-mcp/google-ads-mcp-server/"
env:
  GOOGLE_ADS_DEVELOPER_TOKEN: "***"
  GOOGLE_ADS_OAUTH_CONFIG_PATH: "/path/to/client_secret.json"
  GOOGLE_ADS_LOGIN_CUSTOMER_ID: "2538328866"
```

**Narzędzia (3):** list_accounts, run_gaql, run_keyword_planner

**Zależności Python (requirements.txt):**
```
fastmcp>=0.8.0
requests>=2.31.0
python-dotenv>=1.0.0
google-auth>=2.23.0
google-auth-oauthlib>=1.1.0
google-auth-httplib2>=0.1.1
urllib3>=2.0.0
typing-extensions>=4.0.0
```

**Pliki uwierzytelniające:**
- `client_secret.json` — OAuth client credentials (stałe)
- `google_ads_token.json` — OAuth refresh/access token (wymaga odświeżenia co 7 dni w trybie "testing")

**Google Ads API version:** v23

### 2.5 Meta Ads MCP

```yaml
command: python
args: ["-m", "meta_ads_mcp"]
env:
  META_ACCESS_TOKEN: "***"   # Facebook long-lived access token
```

**Zależności:** Pakiet `meta-ads-mcp` (pip install)

### 2.6 GA4 MCP

```yaml
command: /Users/user/.local/bin/analytics-mcp
args: []
env: {}   # Uses Application Default Credentials (~/.config/gcloud/application_default_credentials.json)
```

**Property ID (hardcoded w kodzie dashboard):** `279858535`

**Uwaga:** Token OAuth wygasa co 7 dni (Google "testing" mode). Wymaga reauth przez `generate_ga4_token.py`.

### 2.7 Chrome DevTools MCP

```yaml
command: npx
args: ["chrome-devtools-mcp"]
env: {}
```

**Uwaga:** Wymaga działającego Chrome z włączonym Chrome DevTools Protocol. W środowisku chmurowym wymaga headless Chrome (np. Puppeteer, Playwright, lub Chromium w kontenerze).

---

## 3. ZMIENNE ŚRODOWISKOWE — KONSOLIDACJA

### 3.1 Wymagane sekrety (Vault / Secret Manager)

| Zmienna | Używana przez | Typ | Ważność |
|---------|---------------|-----|---------|
| `SHOPIFY_ACCESS_TOKEN` | Shopify MCP, Dashboard, Python scripts | `shpat_***` | Stały (dopóki nie zostanie odwołany) |
| `MYSHOPIFY_DOMAIN` | Shopify MCP, Dashboard | `genactiv.myshopify.com` | Stały (config, nie secret) |
| `KLAVIYO_API_KEY` | Klaviyo MCP, Dashboard | `pk_***` | Stały |
| `META_ACCESS_TOKEN` | Meta Ads MCP, Dashboard | Long-lived token | Wygasa ~60 dni |
| `GOOGLE_ADS_DEVELOPER_TOKEN` | Google Ads MCP, Dashboard | Token | Stały |
| `GOOGLE_ADS_OAUTH_CONFIG_PATH` | Google Ads MCP | Ścieżka do pliku | N/A |
| `GOOGLE_ADS_LOGIN_CUSTOMER_ID` | Google Ads MCP | `2538328866` | Stały (config) |
| `BASELINKER_TOKEN` | Python scripts, GitHub Actions | Token | Stały |
| `ANTHROPIC_API_KEY` | Claude API (model) | `sk-ant-***` | Stały |

### 3.2 Pliki uwierzytelniające (wymagają montowania / kopiowania)

| Plik | Serwer | Uwagi |
|------|--------|-------|
| `client_secret.json` | Google Ads MCP | OAuth client credentials |
| `google_ads_token.json` | Google Ads MCP | Refresh token, wygasa co 7 dni w "testing" mode |
| `application_default_credentials.json` | GA4 MCP | Standardowa lokalizacja: `~/.config/gcloud/` |

### 3.3 Hardcoded credentials (PROBLEM — wymaga refaktoru przed migracją)

**9 plików z hardcoded tokenami** (ten sam Shopify token w 8 plikach, Baselinker w 2):

| Plik | Co jest hardcoded |
|------|-------------------|
| `baselinker_api.py:12` | `BASELINKER_TOKEN` |
| `sync_payment_id.py:19,22` | `SHOPIFY_TOKEN`, `SHOPIFY_DOMAIN`, `BASELINKER_TOKEN` |
| `shopify_graphql.py:13` | `ACCESS_TOKEN` (shpat), `SHOPIFY_DOMAIN` |
| `shopify_theme_api.py:15` | `ACCESS_TOKEN` (shpat), `SHOPIFY_DOMAIN` |
| `reports/dashboard_operacyjny.py:30` | `SHOPIFY_TOKEN` (shpat) |
| `seo/fix_genacitv_typo.py:11` | `TOKEN` (shpat) |
| `seo/fix_genacitv_metafields.py:11` | `TOKEN` (shpat) |
| `seo/fix_collection_metas_from_word.py:14` | `TOKEN` (shpat) |
| `seo/add_all_collection_metas.py:15` | `TOKEN` (shpat) |
| `generate_ga4_token.py` | OAuth `client_id`, `client_secret` |

**WYMAGANE PRZED MIGRACJĄ:** Przenieść wszystkie hardcoded tokeny do zmiennych środowiskowych. Jeden wspólny `.env` w root + `python-dotenv` we wszystkich skryptach.

---

## 4. APLIKACJE WEBOWE (ISTNIEJĄCE)

### 4.1 Chat UI (port 3000)

**Architektura:** Express + WebSocket

```
Browser ←──WebSocket──→ Express Server ←──child_process──→ claude CLI
                                                              │
                                                         .mcp.json
                                                         (MCP servers)
```

**Jak działa:**
1. Użytkownik wpisuje pytanie w przeglądarce
2. WebSocket przesyła do serwera
3. Serwer uruchamia `claude -p "<query>"` jako child process
4. stdout Claude CLI jest streamowany przez WebSocket do przeglądarki
5. Timeout: 5 minut na query

**Zależności:**
```json
{
  "@anthropic-ai/sdk": "^0.71.2",
  "express": "^4.18.2",
  "ws": "^8.16.0"
}
```

**Problem dla migracji:** Wymaga zainstalowanego `claude` CLI na serwerze, co z kolei wymaga konta Anthropic i autoryzacji.

### 4.2 Dashboard Server (port 3001)

**Architektura:** Express REST API + statyczny frontend (SPA)

```
Browser ←──HTTP──→ Express Server ──→ Shopify GraphQL (direct import)
                                  ──→ GA4 MCP (stdio spawn)
                                  ──→ Meta Ads MCP (stdio spawn)
                                  ──→ Google Ads MCP (stdio spawn)
                                  ──→ Klaviyo MCP (stdio spawn)
```

**API Endpoints:**

| Endpoint | Source | Cache |
|----------|--------|-------|
| `GET /api/health` | Local | — |
| `GET /api/dashboard?dateFrom=&dateTo=` | Shopify GraphQL | 5 min |
| `GET /api/orders/recent?limit=` | Shopify GraphQL | 2 min |
| `GET /api/products?limit=` | Shopify GraphQL | 10 min |
| `GET /api/ga4?dateFrom=&dateTo=` | GA4 MCP | 10 min |
| `GET /api/meta-ads?days=` | Meta Ads MCP | 10 min |
| `GET /api/google-ads?dateFrom=&dateTo=` | Google Ads MCP | 10 min |
| `GET /api/klaviyo` | Klaviyo MCP | 15 min |

**Hardcoded IDs (do wyciągnięcia do env):**
- `GA4_PROPERTY_ID`: `279858535`
- `META_ADS_ACCOUNT_ID`: `act_66396825`
- `GOOGLE_ADS_CUSTOMER_ID`: `3393382047`
- `KLAVIYO_PLACED_ORDER_METRIC_ID`: `R6aTMS`

---

## 5. SKRYPTY PYTHON

### 5.1 Zależności

Wszystkie skrypty wymagają tylko pakietu `requests` (+ `google-auth-oauthlib` dla GA4 token gen).

**Wspólny venv:**
```bash
python3 -m venv venv
pip install requests weasyprint google-auth-oauthlib
```

### 5.2 GitHub Actions workflow

**Plik:** `.github/workflows/sync-payment-id.yml`

```yaml
name: Sync Payment ID (Shopify -> Baselinker)
on:
  schedule:
    - cron: '0 * * * *'    # co godzinę
  workflow_dispatch:         # manual trigger
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install requests
      - run: python sync_payment_id_auto.py --live
        env:
          SHOPIFY_DOMAIN: ${{ secrets.SHOPIFY_DOMAIN }}
          SHOPIFY_TOKEN: ${{ secrets.SHOPIFY_TOKEN }}
          BASELINKER_TOKEN: ${{ secrets.BASELINKER_TOKEN }}
```

**UWAGA:** Workflow odwołuje się do `sync_payment_id_auto.py`, który **nie istnieje** na dysku. Prawdopodobnie brakujący plik lub zmieniona nazwa. Wymaga naprawy.

---

## 6. WYZWANIA MIGRACYJNE

### 6.1 Problem #1: Claude Code CLI wymaga lokalnej instalacji

**Obecny chat-ui** uruchamia `claude -p <query>` jako child process. W chmurze:
- Trzeba zainstalować Claude Code CLI na serwerze
- Lub zamienić na bezpośrednie wywołania Anthropic API + własny MCP client

**Rekomendowane podejście:**

```
Opcja A: Claude Code CLI w kontenerze
  - Zainstalować claude CLI w Docker
  - Skonfigurować .mcp.json
  - chat-ui uruchamia claude jako child process (jak teraz)
  - PROS: Minimalne zmiany w kodzie
  - CONS: Zależność od Claude CLI, ograniczone skalowanie

Opcja B: Własny MCP client + Anthropic API (REKOMENDOWANE)
  - Użyć @modelcontextprotocol/sdk (już jest w dashboard-server)
  - Bezpośrednio łączyć się z MCP servers przez stdio
  - Wysyłać kontekst narzędzi do Anthropic Messages API
  - PROS: Pełna kontrola, skalowalność, brak zależności od CLI
  - CONS: Wymaga napisania orchestratora MCP ↔ Anthropic API
```

### 6.2 Problem #2: OAuth token refresh (Google Ads + GA4)

Google OAuth tokeny w trybie "testing" wygasają co 7 dni. Opcje:
1. **Opublikować aplikację Google Cloud** (jednorazowo) → tokeny nie wygasają
2. **Automatyczny refresh** w kodzie (już częściowo zaimplementowany w `google_auth.py`)
3. **Cron job** do odświeżania tokenów

### 6.3 Problem #3: Chrome DevTools MCP

Wymaga działającej instancji Chrome. W chmurze:
- **Headless Chromium** w kontenerze (np. `puppeteer/puppeteer` Docker image)
- Lub **Playwright** z headless Chrome
- Chrome DevTools Protocol (CDP) na porcie 9222

### 6.4 Problem #4: Hardcoded credentials

4 skrypty Python mają hardcoded tokeny. **MUSZĄ zostać zrefaktorowane** przed migracją — zmienne środowiskowe lub secret manager.

### 6.5 Problem #5: Brak Git repo

Projekt nie jest repozytorium Git. Brak `.gitignore`. Przed migracją:
1. `git init`
2. Utworzyć `.gitignore` (wykluczyć: `venv/`, `node_modules/`, `.env`, `*_secret.json`, `*_token.json`, `__pycache__/`)
3. Commit początkowy
4. Push do GitHub/GitLab

---

## 7. REKOMENDOWANA ARCHITEKTURA DOCELOWA

### 7.1 Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│  CLOUD (np. Railway / Fly.io / AWS ECS / VPS)                  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ Docker Container: "mcp-orchestrator"                      │   │
│  │                                                           │   │
│  │  ┌─────────────┐   MCP stdio   ┌──────────────────────┐ │   │
│  │  │ Web Terminal │◄────────────►│ MCP Server: Klaviyo   │ │   │
│  │  │ (Express+WS) │              │ MCP Server: Shopify   │ │   │
│  │  │              │              │ MCP Server: Google Ads │ │   │
│  │  │ Anthropic API│              │ MCP Server: Meta Ads   │ │   │
│  │  │ Messages     │              │ MCP Server: GA4        │ │   │
│  │  └──────┬───────┘              └──────────────────────┘ │   │
│  │         │                                                │   │
│  │  ┌──────▼───────┐     ┌──────────────────┐              │   │
│  │  │ Dashboard API │     │ Headless Chrome   │              │   │
│  │  │ (Express)     │     │ (CDP port 9222)   │              │   │
│  │  └──────────────┘     └──────────────────┘              │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌───────────────────┐                                          │
│  │ Secret Manager     │  ← Vault / AWS Secrets / Railway vars   │
│  │ (env vars)         │                                          │
│  └───────────────────┘                                          │
└─────────────────────────────────────────────────────────────────┘
         │
         ▼
   ┌─────────────┐
   │ Nginx/Caddy  │  ← HTTPS, auth, rate limiting
   │ (reverse     │
   │  proxy)      │
   └──────┬──────┘
          │
    Internet / Browser
```

### 7.2 Komponenty docelowe

| Komponent | Technologia | Rola |
|-----------|-------------|------|
| **Web Terminal** | Express + WebSocket + xterm.js | Interfejs użytkownika (jak terminal) |
| **MCP Orchestrator** | Node.js + `@modelcontextprotocol/sdk` | Zarządzanie MCP serwerami, routing tool calls |
| **LLM Backend** | Anthropic Messages API (Claude Opus) | Przetwarzanie poleceń, tool use |
| **Dashboard API** | Express (istniejący `dashboard-server`) | REST API z danymi biznesowymi |
| **Headless Chrome** | Puppeteer / Playwright | Dla Chrome DevTools MCP |
| **Reverse proxy** | Nginx / Caddy | HTTPS, auth, rate limiting |
| **Secret Manager** | Platform-native (Railway vars / AWS Secrets) | Przechowywanie tokenów |
| **Cron** | Platform-native lub node-cron | Payment sync (co godzinę), token refresh |

### 7.3 Stack technologiczny

```
Runtime:     Node.js >= 18 + Python >= 3.10
Container:   Docker (multi-stage build)
Hosting:     Railway.app / Fly.io / AWS ECS / VPS z Docker
HTTPS:       Let's Encrypt (automatyczne)
Auth:        Basic Auth lub OAuth (dla web terminala)
Monitoring:  Health checks na /api/health
```

---

## 8. DOCKER — PRZYKŁADOWA STRUKTURA

```dockerfile
# ============ Stage 1: Node.js base ============
FROM node:18-slim AS node-base
WORKDIR /app

# Shopify Extended MCP
COPY shopify-mcp-extended/package*.json ./shopify-mcp-extended/
RUN cd shopify-mcp-extended && npm ci --production
COPY shopify-mcp-extended/ ./shopify-mcp-extended/
RUN cd shopify-mcp-extended && npm run build

# Dashboard server
COPY dashboard-server/package*.json ./dashboard-server/
RUN cd dashboard-server && npm ci --production
COPY dashboard-server/ ./dashboard-server/

# Chat UI / Web terminal
COPY chat-ui/package*.json ./chat-ui/
RUN cd chat-ui && npm ci --production
COPY chat-ui/ ./chat-ui/

# ============ Stage 2: Python base ============
FROM python:3.11-slim AS python-base
RUN pip install --no-cache-dir \
    requests \
    fastmcp>=0.8.0 \
    python-dotenv \
    google-auth>=2.23.0 \
    google-auth-oauthlib>=1.1.0 \
    google-auth-httplib2 \
    meta-ads-mcp \
    uv

# ============ Stage 3: Final ============
FROM node:18-slim
# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip chromium && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=node-base /app ./
COPY --from=python-base /usr/local/lib/python3.11 /usr/local/lib/python3.11

# Python scripts + Google Ads MCP
COPY google-ads-mcp/ ./google-ads-mcp/
COPY *.py ./

EXPOSE 3000 3001

# Entry: process manager (pm2 / supervisord)
CMD ["node", "start.js"]
```

**UWAGA:** To jest szkic koncepcyjny. Finalny Dockerfile wymaga dopracowania zależności i ścieżek.

---

## 9. SCOPE PRACY DLA DEVELOPERA

### Faza 1: Przygotowanie (1-2 dni)
- [ ] Zrefaktorować hardcoded credentials → env vars (4 pliki Python)
- [ ] Inicjalizacja Git repo + `.gitignore`
- [ ] Opublikować Google Cloud OAuth app (żeby tokeny nie wygasały co 7 dni)
- [ ] Naprawić workflow GH Actions (`sync_payment_id_auto.py` → `sync_payment_id.py`)
- [ ] Utworzyć `requirements.txt` na poziomie root

### Faza 2: Konteneryzacja (3-5 dni)
- [ ] Dockerfile (multi-stage: Node.js + Python + Chromium)
- [ ] docker-compose.yml (dev environment)
- [ ] Konfiguracja MCP servers w kontenerze (ścieżki, env vars)
- [ ] Headless Chrome setup (CDP na port 9222)
- [ ] Testy: każdy MCP server odpala się i odpowiada na `list_tools`

### Faza 3: MCP Orchestrator (3-5 dni)
- [ ] Napisać serwis Node.js: MCP client → Anthropic Messages API → WebSocket
- [ ] Użyć `@modelcontextprotocol/sdk` (już w projekcie) do łączenia z MCP servers
- [ ] Implementacja tool_use flow: user query → Claude API → tool call → MCP server → result → Claude API → response
- [ ] Streaming odpowiedzi przez WebSocket

### Faza 4: Web Terminal Frontend (2-3 dni)
- [ ] xterm.js lub podobna biblioteka terminala w przeglądarce
- [ ] Markdown rendering w odpowiedziach
- [ ] Historia konwersacji (persystentna)
- [ ] Autoryzacja (Basic Auth / OAuth)

### Faza 5: Deploy + DevOps (2-3 dni)
- [ ] Deploy na wybraną platformę (Railway / Fly.io / VPS)
- [ ] HTTPS (Let's Encrypt / Cloudflare)
- [ ] Secret Manager (env vars na platformie)
- [ ] Cron job: payment sync (co godzinę)
- [ ] Cron job: Google OAuth token refresh
- [ ] Health checks + monitoring
- [ ] Backup strategy dla tokenów OAuth

### Faza 6: Testy i migracja (1-2 dni)
- [ ] E2E test każdego MCP narzędzia przez web terminal
- [ ] Test dashboard API
- [ ] Test cron jobs
- [ ] Dokumentacja dla użytkownika końcowego

**Szacowany czas:** 12-20 dni roboczych

---

## 10. PLIKI DO PRZEKAZANIA DEVELOPEROWI

### Kod źródłowy (cały katalog)
```
genactiv-klaviyo/
├── shopify-mcp-extended/     # Lokalny MCP server (TypeScript) — KLUCZOWY
├── google-ads-mcp/           # Lokalny MCP server (Python) — KLUCZOWY
├── dashboard-server/         # Dashboard backend — KLUCZOWY
├── chat-ui/                  # Istniejący web frontend — REFERENCJA
├── templates/                # Email templates
├── seo/                      # SEO scripts i dokumentacja
├── reports/                  # Report generators
├── docs/                     # Dokumentacja (w tym ten plik)
├── .github/workflows/        # CI/CD
├── baselinker_api.py         # Baselinker client
├── shopify_graphql.py        # Shopify GraphQL client
├── shopify_theme_api.py      # Shopify Theme client
├── sync_payment_id.py        # Payment sync script
├── generate_ga4_token.py     # GA4 token generator
└── CLAUDE.md                 # Dokumentacja projektu
```

### Sekrety (osobno, bezpiecznie)
- Wszystkie zmienne z sekcji 3.1
- Pliki: `client_secret.json`, `google_ads_token.json`, `application_default_credentials.json`

### NIE przesyłać
- `venv/` — odtworzyć z requirements
- `node_modules/` — odtworzyć z package.json
- `__pycache__/` — generowane automatycznie

---

## 11. ALTERNATYWNE PODEJŚCIA

### Opcja A: Claude Code na VPS (najprostsze)

Zainstalować Claude Code CLI na VPS, użyć istniejącego chat-ui jako frontend. Minimalne zmiany w kodzie.

| Pro | Con |
|-----|-----|
| Minimalna praca (2-3 dni) | Zależność od Claude CLI |
| Działa identycznie jak lokalnie | Brak skalowania |
| | Wymaga aktywnej subskrypcji Claude Code |

### Opcja B: Anthropic API + własny orchestrator (rekomendowane)

Napisać własny MCP orchestrator używając Anthropic Messages API + MCP SDK.

| Pro | Con |
|-----|-----|
| Pełna kontrola | Więcej pracy (12-20 dni) |
| Skalowalne | Wymaga Anthropic API key + billing |
| Brak zależności od CLI | |
| Możliwość customizacji UI | |

### Opcja C: Open-source MCP hosting (np. Cloudflare MCP, Smithery)

Użyć istniejącej platformy do hostowania MCP servers.

| Pro | Con |
|-----|-----|
| Managed infrastructure | Może nie obsługiwać wszystkich serwerów |
| Szybki start | Vendor lock-in |
| | Lokalny kod (Shopify Extended, Google Ads) wymaga adaptacji |

---

## 12. KONTAKT I PYTANIA

W razie pytań technicznych — uruchomić Claude Code w tym katalogu z poleceniem:
```
claude "Przeczytaj CLAUDE.md i docs/MIGRATION_PLAN_ONLINE.md, odpowiedz na pytanie: [pytanie]"
```

**Kluczowe pliki referencyjne:**
- `CLAUDE.md` — pełna dokumentacja projektu
- `dashboard-server/mcp-client.js` — wzorzec łączenia z MCP servers w Node.js
- `dashboard-server/server.js` — wzorzec REST API z MCP
- `chat-ui/server.js` — wzorzec WebSocket + Claude CLI

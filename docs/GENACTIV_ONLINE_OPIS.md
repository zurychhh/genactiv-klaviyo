# GenActiv Online — Opis biznesowy i techniczny

**Data:** 2026-03-29
**Status:** Produkcja — https://genactiv.oleksiakconsulting.com

---

## CZĘŚĆ I — Perspektywa biznesowa (CEO)

### Co to jest

GenActiv Online to prywatny asystent AI dostępny przez przeglądarkę, zbudowany wyłącznie dla GenActiv. Łączy się w czasie rzeczywistym z 6 platformami marketingowymi i sprzedażowymi firmy, i odpowiada na pytania po polsku — z konkretnymi danymi, nie ogólnikami.

Zamiast logować się do 6 osobnych paneli, zespół pyta w jednym oknie:

> „Ile sesji było na stronie w tym tygodniu?"
> „Pokaż aktywne kampanie Google Ads"
> „Jakie produkty sprzedały się najlepiej w marcu?"
> „Wyślij mi raport konwersji z Shopify"

Asystent sam decyduje, do którego systemu sięgnąć, pobiera dane, i prezentuje odpowiedź z tabelami, wykresami i podsumowaniem.

### Podłączone platformy

| Platforma | Co daje | Przykładowe pytania |
|-----------|---------|---------------------|
| **Klaviyo** | Email marketing — kampanie, flows, profile, segmenty, metryki | „Pokaż wyniki ostatnich 5 kampanii email", „Ile mamy aktywnych subskrybentów?" |
| **Shopify** (2 serwery) | Sprzedaż — zamówienia, produkty, klienci, analityka ruchu, UTM, konwersje, SEO | „Jakie było ROAS z Google?", „Pokaż zamówienia z ostatniego tygodnia" |
| **Google Ads** | Reklamy — kampanie, wydatki, słowa kluczowe, ROAS | „Ile wydaliśmy na reklamy w marcu?", „Pokaż aktywne kampanie PMax" |
| **GA4** | Analityka — sesje, użytkownicy, źródła ruchu, bounce rate | „Skąd przychodzą użytkownicy?", „Ile było konwersji z organica?" |
| **Meta Ads** | Reklamy Facebook/Instagram — kampanie, kreacje, grupy docelowe | „Pokaż wydatki na Meta Ads w tym miesiącu" |

### Wartość biznesowa

**1. Oszczędność czasu**
Jedno pytanie zastępuje 5–15 minut klikania po panelach. Zespół marketingu nie musi znać interfejsów 6 platform — wystarczy pytanie po polsku.

**2. Jeden punkt dostępu do wszystkich danych**
Dane z Klaviyo, Shopify, Google Ads, GA4 i Meta Ads w jednym oknie. Możliwość porównywania cross-platform (np. „Jak kampania email wpłynęła na ruch z GA4?").

**3. Bezpieczeństwo**
- Aplikacja chroniona loginem i hasłem (bcrypt)
- Sesja wygasa po 24h
- Dostęp ograniczony do autoryzowanych użytkowników
- Brak publicznie dostępnych danych — wszystko za autentykacją

**4. Niski koszt operacyjny**
- Hosting: Railway.app (~$5–20/mies. w zależności od użycia)
- AI: Anthropic API (Claude) — koszt per zapytanie, optymalizacja dwufazowa redukuje koszty ~90%
- Brak dedykowanego serwera, maintenance'u, ani zespołu IT

**5. Skalowalność**
Dodanie nowej platformy (np. Allegro, BaseLinker, Ceneo) wymaga jedynie podłączenia kolejnego serwera MCP — bez zmiany interfejsu ani logiki AI.

### Jak wygląda

- Ciemny interfejs w stylu ChatGPT / Claude.ai
- Branding GenActiv (kolory navy/blue/red, typografia Inter)
- Wiadomości z avatarami (Ty / GenActiv)
- Widoczne wywołania narzędzi (np. „run_report 2.3s") — transparentność, co AI robi
- Tabele, listy, bloki kodu z formatowaniem Markdown
- Responsywny — działa na telefonie i tablecie

### Roadmap — kierunki rozwoju

| Priorytet | Kierunek | Opis |
|-----------|----------|------|
| **P1** | Dashboardy automatyczne | Stały panel z KPI (sesje, zamówienia, ROAS) aktualizowany co godzinę |
| **P1** | Raporty cykliczne | Automatyczne generowanie raportu tygodniowego/miesięcznego i wysyłka na email |
| **P2** | Multi-user | Oddzielne konta z rolami (admin, viewer), historia per użytkownik |
| **P2** | Akcje wykonawcze | Nie tylko czytanie danych — tworzenie kampanii, aktualizacja produktów, odpowiadanie klientom |
| **P2** | BaseLinker MCP | Podłączenie systemu fulfillment (stany magazynowe, statusy zamówień) |
| **P3** | Allegro / Ceneo | Analityka marketplace'ów |
| **P3** | Powiadomienia proaktywne | Alert: „Kampania X przekroczyła budżet", „Bounce rate wzrósł o 50%" |
| **P3** | Eksport PDF/Excel | Pobieranie raportów w formatach biurowych |

---

## CZĘŚĆ II — Perspektywa techniczna (CTO)

### Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                        PRZEGLĄDARKA                         │
│  index.html + style.css + terminal.js                       │
│  (Inter font, marked.js, SSE EventSource)                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTPS (Railway / custom domain)
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                    EXPRESS SERVER (Node 18)                  │
│                                                             │
│  auth.js          — session-based auth (bcrypt + express-   │
│                     session), login page, 24h cookie        │
│                                                             │
│  index.js         — HTTP routes, SSE streaming endpoint     │
│                     POST /api/chat → SSE stream             │
│                     GET  /api/health → healthcheck          │
│                                                             │
│  anthropic-       — two-phase Anthropic API pipeline:       │
│  bridge.js          Phase 1: Haiku router (~20 tokens)      │
│                     Phase 2: Sonnet + targeted tools        │
│                     Retry logic (429 → 3s/6s/12s backoff)   │
│                     Rate limiter (3s min between calls)     │
│                                                             │
│  mcp-             — MCP client orchestrator:                │
│  orchestrator.js    stdio transport, tool caching (5 min),  │
│                     schema compression, result compression  │
│                     (nulls stripped), 15k char truncation    │
│                                                             │
│  config.js        — MCP server definitions, prompts,        │
│                     credential file generation at startup   │
│                                                             │
└────────┬──────┬──────┬──────┬──────┬──────┬─────────────────┘
         │      │      │      │      │      │
         ▼      ▼      ▼      ▼      ▼      ▼
     Klaviyo  Shopify Shopify Google  GA4   Meta
     (uvx/   Ext.    Std.    Ads    (pip)  Ads
     Python) (Node)  (Node)  (venv)        (pip)
```

### Kluczowy mechanizm: Two-Phase Routing

Problem: 6 serwerów MCP generuje ~93 narzędzia. Wysłanie ich wszystkich do Claude kosztuje ~22k tokenów per zapytanie.

Rozwiązanie:
1. **Faza 1 — Router (Haiku, ~$0.0001/zapytanie):** Haiku analizuje pytanie i zwraca nazwę serwera MCP (jedno słowo). Koszt: ~20 tokenów output.
2. **Faza 2 — Executor (Sonnet, z narzędziami):** Sonnet dostaje tylko narzędzia z wybranego serwera (3–15 zamiast 93). Koszt: ~300–1800 tokenów input zamiast 22k.

Redukcja kosztów: **~90%** w porównaniu z podejściem "wszystkie narzędzia w każdym zapytaniu".

### Stack technologiczny

| Warstwa | Technologia | Wersja |
|---------|-------------|--------|
| Runtime | Node.js | 18 (Docker slim) |
| Framework | Express.js | 4.18 |
| AI | Anthropic Claude API (Sonnet + Haiku) | SDK 0.71 |
| MCP | @modelcontextprotocol/sdk | 1.17 |
| Auth | express-session + bcryptjs | — |
| Markdown | marked.js | 12.x |
| Styling | Vanilla CSS (custom properties) | — |
| Font | Inter (Google Fonts) | — |
| Hosting | Railway.app (Docker) | — |
| Python (MCP) | 3.x + uv + venv | — |

### Struktura plików

```
genactiv-online/
├── client/
│   ├── index.html          # Single-page HTML (46 linii)
│   ├── style.css           # Design system (672 linii)
│   └── terminal.js         # Chat logic, SSE, tools (351 linii)
├── server/
│   ├── index.js            # Express routes + SSE (98 linii)
│   ├── auth.js             # Session auth + login page (147 linii)
│   ├── anthropic-bridge.js # Two-phase AI pipeline (223 linie)
│   ├── mcp-orchestrator.js # MCP connections + tool mgmt (197 linii)
│   └── config.js           # Server definitions + prompts (159 linii)
├── package.json
└── .env                    # 20 zmiennych środowiskowych

Dockerfile                  # Root — multi-stage Docker build
railway.json                # Railway deploy config
```

**Łącznie: ~1,893 linii kodu** (bez CSS) — celowo minimalistyczny, zero frameworków frontendowych.

### Serwery MCP — szczegóły techniczne

| Serwer | Język | Transport | Narzędzia | Uruchamianie |
|--------|-------|-----------|-----------|--------------|
| **klaviyo** | Python | stdio | 26 | `uvx klaviyo-mcp-server@0.4.0` (z fastmcp <3) |
| **shopify-extended** | TypeScript | stdio | 15 | Własny build: `shopify-mcp-extended/dist/index.js` |
| **shopify-standard** | TypeScript | stdio | 15 | Ten sam build co extended (pełny zestaw) |
| **google-ads** | Python | stdio | 3 | FastMCP w venv: `google-ads-mcp-server/server.py` |
| **ga4** | Python | stdio | 6 | pip `analytics-mcp` |
| **meta-ads** | Python | stdio | 28 | pip `meta-ads-mcp` |

### Zmienne środowiskowe

```
# Auth
AUTH_USERNAME                    # Login (default: admin)
AUTH_PASSWORD_HASH               # bcrypt hash hasła

# AI
ANTHROPIC_API_KEY                # Claude API key

# Klaviyo
KLAVIYO_API_KEY                  # Private API key (pk_...)

# Shopify
SHOPIFY_ACCESS_TOKEN             # Admin API token (shpat_...)
MYSHOPIFY_DOMAIN                 # genactiv.myshopify.com

# Meta Ads
META_ACCESS_TOKEN                # Graph API long-lived token

# Google OAuth (shared)
GOOGLE_OAUTH_CLIENT_ID           # OAuth app client ID
GOOGLE_OAUTH_CLIENT_SECRET       # OAuth app secret

# Google Ads
GOOGLE_ADS_DEVELOPER_TOKEN       # Developer token (MCC)
GOOGLE_ADS_REFRESH_TOKEN         # OAuth refresh token
GOOGLE_ADS_LOGIN_CUSTOMER_ID     # Manager account ID

# GA4
GA4_PROPERTY_ID                  # GA4 property (279858535)
GA4_REFRESH_TOKEN                # OAuth refresh token

# Server
PORT                             # Default: 3000
NODE_ENV                         # production / development
SESSION_SECRET                   # Random 32+ chars
```

### Docker Build

```dockerfile
FROM node:18-slim
# 1. Python 3 + uv (dla Klaviyo/Meta/GA4 MCP)
# 2. pip install meta-ads-mcp analytics-mcp
# 3. Google Ads MCP: venv + requirements.txt
# 4. Shopify Extended: npm ci + npm run build (TypeScript → JS)
# 5. genactiv-online: npm ci --production
# 6. CMD: node server/index.js
```

Obraz: ~400MB. Build time: ~3 min (Railway).

### Deployment

| Element | Wartość |
|---------|--------|
| Platforma | Railway.app |
| Projekt | cozy-trust |
| Service | exemplary-learning |
| URL | `exemplary-learning-production-414a.up.railway.app` |
| Custom domain | `genactiv.oleksiakconsulting.com` (CNAME) |
| Healthcheck | `GET /api/health` |
| Restart policy | ON_FAILURE |
| Region | US West (Railway default) |

### Optymalizacje kosztowe

| Optymalizacja | Efekt |
|---------------|-------|
| Two-phase routing (Haiku → Sonnet) | ~90% redukcja tokenów input |
| Schema compression (usunięcie examples, defaults) | ~30% mniejszy payload narzędzi |
| Result compression (usunięcie null/empty) | ~20% mniejszy payload wyników |
| Truncation (15k char limit) | Zapobiega eksplozji tokenów |
| Tool caching (5 min TTL) | Eliminuje powtórne listowanie |
| Rate limiter (3s min interval) | Zapobiega 429 errors |
| Retry with backoff (3s/6s/12s) | Automatyczne recovery |

### Bezpieczeństwo

- **Auth:** Session-based (express-session), bcrypt password hashing
- **Cookie:** httpOnly, secure (production), sameSite: strict, 24h expiry
- **Trust proxy:** Enabled w production (Railway reverse proxy)
- **API keys:** W zmiennych środowiskowych, nigdy w kodzie
- **Google credentials:** Generowane z env vars at startup do plików tymczasowych
- **No CORS:** Tylko same-origin requests
- **CSP:** Brak (do dodania w przyszłości)

### Znane ograniczenia i dług techniczny

| Problem | Wpływ | Priorytet naprawy |
|---------|-------|-------------------|
| Brak historii rozmów (localStorage) | Odświeżenie strony kasuje konwersację | P1 |
| Single-server routing | Jedno pytanie = jeden serwer MCP (nie cross-platform) | P2 |
| Brak CSP headers | Potencjalne XSS (niskie ryzyko — prywatna app) | P2 |
| Brak rate limiting per user | Jeden użytkownik może generować duże koszty API | P2 |
| Google OAuth token expiry | Tokeny wygasają (trzeba regenerować ręcznie) | P3 |
| Brak testów | Zero unit/integration tests | P3 |
| Brak logowania do pliku/serwisu | Logi tylko w stdout (Railway retention ~7 dni) | P3 |

### Jak dodać nowy serwer MCP

1. Dodaj definicję w `server/config.js` → tablica `mcpServers`:
```js
{
  name: 'nowy-serwer',
  command: 'node',          // lub python3, uvx, etc.
  args: ['path/to/server'],
  env: { API_KEY: process.env.NOWY_API_KEY || '' }
}
```

2. Dodaj nazwę do `ROUTER_PROMPT` w `config.js` z opisem po polsku.

3. Dodaj env var w Railway: `railway variables set NOWY_API_KEY=...`

4. Jeśli wymaga dodatkowych pakietów — dodaj do `Dockerfile`.

5. Deploy: `unset RAILWAY_TOKEN && railway up`

Czas dodania nowego serwera: **15–30 minut** (jeśli MCP server już istnieje).

---

*Dokument wygenerowany 2026-03-29. Aktualny stan: 6/6 serwerów MCP, produkcja na Railway.*

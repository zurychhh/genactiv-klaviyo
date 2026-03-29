# GenActiv MCP Online — Kontekst migracji

**Data rozpoczęcia:** 2026-03-23
**Klient:** oleksiakconsulting.com (Piotr Oleksiak)
**Email Railway:** oleksiakpiotrrafal@gmail.com

---

## Co robimy

Przenosimy lokalne środowisko Claude Code + MCP z Maca do chmury (Railway.app) jako webowy terminal dostępny z przeglądarki. Klient GenActiv (e-commerce, Shopify) korzysta z 7 serwerów MCP do zarządzania marketingiem i sprzedażą.

## Decyzje podjęte

| Kwestia | Decyzja |
|---------|---------|
| Opcja migracji | B "lite" — własny MCP orchestrator bazujący na istniejącym `dashboard-server/mcp-client.js` |
| Hosting | Railway.app |
| Domena | `genactiv.oleksiakconsulting.com` (subdomena, CNAME → Railway) |
| Obecna strona | oleksiakconsulting.com hostowana na **Vercel** |
| Auth | Login + hasło (form + express-session + bcrypt). Login: `admin`, hasło: `genactiv2026` |
| Transport | SSE (nie WebSocket — Vercel nie przepuszcza WS przez rewrites, a subdomena rozwiązuje problem) |
| Model LLM | `claude-sonnet-4-20250514` (tańszy na MVP) |
| Frontend | xterm.js + marked.js (CDN), dark theme |
| Scope MVP | Tylko web terminal z MCP. **Bez dashboardu** (port 3001) |

## Serwery MCP — MVP (4 z 7)

| # | Serwer | Status MVP | Język | Auth |
|---|--------|-----------|-------|------|
| 1 | **Klaviyo** | ✅ Włączony | Python (uvx) | API Key |
| 2 | **Shopify Extended** | ✅ Włączony | TypeScript/Node | API Token |
| 3 | **Meta Ads** | ✅ Włączony | Python (pip) | Access Token |
| 4 | **Shopify Standard** | ✅ Włączony | Node.js | API Token |
| 5 | Google Ads | ❌ Wyłączony | Python | OAuth **WYGASŁ** — wymaga publikacji Google Cloud app |
| 6 | GA4 | ❌ Wyłączony | Binary | OAuth **WYGASŁ** — j.w. |
| 7 | Chrome DevTools | ❌ Pominięty | Node.js | Wymaga headless Chrome (ciężki) |

## Problem Google OAuth

Oba tokeny Google (Ads + GA4) wygasły — refresh tokeny też nieważne bo aplikacja Google Cloud jest w trybie "testing" (7 dni życia refresh tokena). **Cron job NIE rozwiąże problemu** — trzeba opublikować aplikację Google Cloud (OAuth consent screen → "Publish"). To jest zaplanowane jako krok po MVP. Po publikacji dodajemy Google Ads i GA4 do orchestratora.

## Struktura projektu (Faza 1 — gotowa)

```
genactiv-klaviyo/                    # Katalog główny projektu
├── genactiv-online/                 # NOWY — aplikacja webowa
│   ├── server/
│   │   ├── index.js                 # Express + SSE + auth
│   │   ├── auth.js                  # Login/logout + session
│   │   ├── mcp-orchestrator.js      # Spawn 4 MCP serverów, getAllTools(), callTool()
│   │   ├── anthropic-bridge.js      # Anthropic API + tool_use loop + streaming
│   │   └── config.js                # Konfiguracja MCP serverów
│   ├── client/
│   │   ├── index.html               # Chat UI
│   │   ├── terminal.js              # SSE client + markdown
│   │   └── style.css                # Dark theme
│   ├── Dockerfile                   # Node 18 + Python 3.11 + uv
│   ├── railway.json                 # Deploy config
│   ├── package.json                 # ESM, 7 deps
│   └── .env.example
├── shopify-mcp-extended/            # Istniejący — MCP server (TypeScript)
├── google-ads-mcp/                  # Istniejący — wyłączony z MVP
├── dashboard-server/                # Istniejący — NIE migrujemy
│   └── mcp-client.js               # REFERENCJA dla orchestratora
├── chat-ui/                         # Istniejący — zastąpiony przez genactiv-online
├── CLAUDE.md                        # Dokumentacja projektu
└── docs/MIGRATION_PLAN_ONLINE.md    # Pełna specyfikacja migracji
```

## Fazy wdrożenia

| Faza | Opis | Status |
|------|------|--------|
| **1** | Inicjalizacja projektu — struktura, kod, 13 plików | ✅ Gotowa |
| **2** | Lokalne testy + deploy na Railway + custom domain | 🔄 W trakcie |
| **3** | DNS — CNAME `genactiv` → Railway | ⏳ Czeka na Fazę 2 |
| **4** | Post-MVP: publikacja Google Cloud app → dodanie Google Ads + GA4 | ⏳ Planowane |

## Railway

- CLI: v4.30.3, zalogowany
- Projekt: `genactiv-mcp-online` (tworzony w Fazie 2)
- Env vars: 10 zmiennych (auth, Anthropic, Klaviyo, Shopify, Meta, session)

## Kluczowe pliki referencyjne

- `CLAUDE.md` — pełna dokumentacja projektu GenActiv
- `docs/MIGRATION_PLAN_ONLINE.md` — specyfikacja migracji (architektura, MCP, env vars, Docker)
- `dashboard-server/mcp-client.js` — wzorzec MCP client (spawn, connect, callTool)
- `docs/phase1_prompt.md` — prompt Fazy 1 (struktura projektu)
- `docs/phase2_prompt.md` — prompt Fazy 2 (testy + deploy)

## Flow aplikacji (jak to działa)

```
Przeglądarka → genactiv.oleksiakconsulting.com
    → Login form (admin/genactiv2026)
    → Chat terminal (xterm.js)
    → User wpisuje pytanie
    → POST /api/chat {messages}
    → Express → anthropic-bridge.js
        → Pobiera tools[] z mcp-orchestrator (4 MCP servery)
        → Wysyła do Anthropic Messages API (stream: true)
        → Jeśli tool_use → mcp-orchestrator.callTool() → wynik → ponownie do API
        → Jeśli text → SSE stream do przeglądarki
    → Odpowiedź renderowana w terminalu (markdown)
```

## Env vars (nazwy — wartości w .env na dysku i na Railway)

```
AUTH_USERNAME, AUTH_PASSWORD_HASH, SESSION_SECRET
ANTHROPIC_API_KEY
KLAVIYO_API_KEY
SHOPIFY_ACCESS_TOKEN, MYSHOPIFY_DOMAIN
META_ACCESS_TOKEN
PORT, NODE_ENV
```

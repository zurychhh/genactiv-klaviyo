# GenActiv Online — Plan Rozwoju Q2 2026
## Odpowiedź na feedback interesariusza + roadmap Claude Code

**Data:** 4 kwietnia 2026
**Kontekst:** Review z interesariuszem po briefingu konsultanckim
**Format:** 5 bloków odpowiadających 5 punktom feedbacku → konkretne taski Claude Code

---

## TL;DR — Priorytetyzacja

| # | Feedback | Priorytet | Effort | Quick win? |
|---|----------|-----------|--------|------------|
| 1 | Rozbieżności danych między panelami | **KRYTYCZNY** | Średni | Tak (limit 250→paginacja) |
| 2 | Edytowanie/tworzenie (nie tylko analiza) | Wysoki | Duży | Częściowo (SEO tools już są) |
| 3 | Wrzucanie plików | Wysoki | Średni | Nie |
| 4 | Wiele wątków / historia | Średni | Duży | Nie |
| 5 | Senuto + Bing konektory | Średni | Średni | Tak (Bing = Google Ads pattern) |

---

## 1. ROZBIEŻNOŚCI DANYCH MIĘDZY PANELAMI

### Diagnoza

Po analizie kodu `shopify-mcp-extended` zidentyfikowałem **5 źródeł rozbieżności** przychodów MCP vs. Shopify Admin:

| Przyczyna | Wpływ | Lokalizacja w kodzie |
|-----------|-------|---------------------|
| **Limit 250 zamówień** — wszystkie analytics toole mają `first: Math.min(limit, 250)` | **GŁÓWNA PRZYCZYNA** — jeśli w zakresie dat jest >250 zamówień, reszta jest po cichu pomijana | `getOrders.ts:93-96`, używany przez wszystkie analytics |
| **Brak filtrowania statusu finansowego** — cancelled/refunded zamówienia wliczane do totali | Zawyżony przychód | `getConversionMetrics.ts` — brak filtra `financial_status:paid` |
| **Date filter na `created_at`** — Shopify Admin może używać `processed_at` | Rozbieżność na granicach okresów | Wszystkie query z `created_at:>=` |
| **Line item vs order total** — product performance sumuje line items, nie order totals | Nie uwzględnia order-level discountów | `getProductPerformance.ts:125` |
| **Campaign attribution ≠ total** — campaign performance liczy tylko zamówienia z UTM | Niższy total w widoku kampanii | `getCampaignPerformance.ts:119-126` |

### Plan naprawy — Claude Code taski

```
Blok 1: Paginacja (eliminacja limitu 250)
├── Task 1.1: Dodać cursor-based paginację do getOrders.ts
│   - Shopify GraphQL: pageInfo { hasNextPage, endCursor }
│   - Loop: while hasNextPage → fetch next page
│   - Nowy parametr: maxOrders (default: 1000, cap: 5000)
│   - Estimated: 2-3h
│
├── Task 1.2: Zaktualizować wszystkie analytics tools aby korzystały z paginacji
│   - getTrafficSourceAnalytics.ts
│   - getCampaignPerformance.ts
│   - getConversionMetrics.ts
│   - getProductPerformance.ts
│   - Estimated: 1-2h
│
├── Task 1.3: Dodać financial_status filter
│   - Default: financial_status:paid (exclude cancelled, refunded, voided)
│   - Opcjonalny parametr: includeAllStatuses: boolean
│   - Estimated: 1h

Blok 2: Spójność kalkulacji
├── Task 1.4: Ujednolicić revenue calculation
│   - Wszędzie: totalPriceSet.shopMoney.amount (order total)
│   - Product performance: dodać fallback na proportional discount distribution
│   - Dodać metrykę: grossRevenue vs netRevenue
│   - Estimated: 2h
│
├── Task 1.5: Dodać "data quality indicators" do każdego response
│   - ordersAnalyzed vs totalOrdersInRange (paginacja da 100%)
│   - journeyTrackingRate (% zamówień z danymi źródła)
│   - campaignAttributionRate (% z UTM)
│   - financialStatusBreakdown
│   - Estimated: 1h

Blok 3: Cross-validation tool
├── Task 1.6: Nowy tool: get-revenue-reconciliation
│   - Pobiera dane z Shopify GraphQL (sum revenue by date)
│   - Porównuje z wynikami analytics tools
│   - Zwraca diff + wyjaśnienie rozbieżności
│   - Estimated: 3-4h

Blok 4: Testy
├── Task 1.7: Unit testy na revenue calculations
│   - Mock data z known totals
│   - Test paginacji (>250 orders scenario)
│   - Test financial status filtering
│   - Estimated: 2h
```

**Łączny effort:** ~12-14h
**Quick win:** Task 1.1 + 1.3 (paginacja + status filter) — rozwiązuje ~80% problemu w 4h

---

## 2. EDYTOWANIE I TWORZENIE (nie tylko analiza)

### Stan obecny

Shopify Extended MCP **ma już 3 write tools**, ale zakres jest ograniczony:

| Tool | Co robi | Czego brakuje |
|------|---------|---------------|
| `update-product-seo` | Meta title + description | Brak: ALT text, content body |
| `update-collection-seo` | Meta title + description kolekcji | OK |
| `update-order` | Tags, notes, metafields | OK |

Klaviyo MCP **ma create tools**: `create_email_template`, `create_campaign`, `create_profile`, `subscribe_profile`.

### Czego brakuje — nowe write tools

```
Blok 1: Shopify Extended — nowe SEO write tools
├── Task 2.1: update-product-images (ALT text)
│   - GraphQL mutation: productUpdateMedia / productUpdate
│   - Input: productId + array of { imageId, altText }
│   - Bulk mode: update all images for a product at once
│   - Estimated: 3-4h
│
├── Task 2.2: update-product-content
│   - GraphQL mutation: productUpdate (descriptionHtml)
│   - Pozwala na edycję HTML body produktu
│   - Estimated: 2h
│
├── Task 2.3: bulk-update-seo (batch mode)
│   - Przyjmuje array of { productId, seo: { title, description } }
│   - Wykonuje mutations w pętli (Shopify rate limit: 2/sec)
│   - Progress reporting per item
│   - Estimated: 3h
│
├── Task 2.4: get-seo-audit
│   - Skanuje wszystkie produkty/kolekcje
│   - Zwraca: brakujące meta descriptions, brakujące ALT texty, za długie/krótkie titles
│   - Format: lista problemów z severity + suggested fix
│   - Estimated: 4h

Blok 2: Shopify Theme (nowy MCP lub rozszerzenie Extended)
├── Task 2.5: Rozważyć integrację shopify_theme_api.py jako MCP server
│   - get-theme-file, update-theme-file, search-theme-files
│   - Pozwala na edycję Liquid templates z poziomu terminala
│   - ⚠️ Ryzyko: write access do theme = potencjalnie niebezpieczne
│   - Safeguard: backup before edit, dry-run mode
│   - Estimated: 6-8h (nowy MCP server)

Blok 3: Klaviyo — rozszerzenie write capabilities
├── Task 2.6: Zweryfikować istniejące Klaviyo write tools
│   - create_email_template — działa? test end-to-end
│   - create_campaign — flow?
│   - Estimated: 2h (weryfikacja + dokumentacja)
```

**Łączny effort:** ~20-24h
**Quick win:** Task 2.1 (ALT text tool) — bezpośrednio adresuje feedback o SEO

### Workflow dla interesariusza (po wdrożeniu)

```
User: "Zrób audyt SEO produktów — brakujące ALT texty"
→ Router: shopify-extended
→ Tool: get-seo-audit → lista 47 obrazów bez ALT
→ User: "Dodaj ALT texty do produktu GenActiv Colostrum 60 kapsułek"
→ Tool: update-product-images → done
```

---

## 3. WRZUCANIE PLIKÓW

### Stan obecny

**Kompletny brak** — ani frontend (terminal.js), ani backend (index.js) nie obsługują file upload.

### Plan implementacji

```
Blok 1: Backend (Express)
├── Task 3.1: Dodać multer middleware do /api/chat
│   - npm install multer
│   - Limit: 10MB per file, max 3 pliki per request
│   - Dozwolone typy: .csv, .xlsx, .txt, .json, .html, .png, .jpg, .pdf
│   - Storage: /tmp/ (ephemeral, Railway)
│   - Estimated: 2-3h
│
├── Task 3.2: Przekazywanie plików do Anthropic API
│   - Obrazy: base64 encode → content block type: "image"
│   - Tekstowe: odczyt → wklejenie jako tekst w message content
│   - CSV/Excel: parse → JSON summary + first N rows
│   - PDF: extract text → wklejenie jako content
│   - Estimated: 4-5h
│
├── Task 3.3: File processing pipeline
│   - CSV: papaparse → auto-detect separator, headers
│   - XLSX: xlsx package → sheet names + data preview
│   - Cleanup: /tmp/ files usuwane po przetworzeniu
│   - Estimated: 3h

Blok 2: Frontend (terminal.js)
├── Task 3.4: UI komponent do uploadu
│   - Przycisk "📎" obok textarea (lub drag-and-drop zone)
│   - File preview (nazwa + rozmiar + typ)
│   - Możliwość usunięcia przed wysłaniem
│   - FormData zamiast JSON dla /api/chat (gdy są pliki)
│   - Estimated: 3-4h
│
├── Task 3.5: Progress indicator
│   - Upload progress bar (dla większych plików)
│   - "Przetwarzam plik..." status w terminalu
│   - Estimated: 1h

Blok 3: Integracja z MCP workflow
├── Task 3.6: Plik jako kontekst dla narzędzi
│   - User wrzuca CSV z danymi → AI analizuje + wywołuje MCP tools
│   - User wrzuca screenshota → AI opisuje co widzi
│   - User wrzuca HTML template → AI tworzy Klaviyo template
│   - Estimated: 2h (logika w anthropic-bridge.js)
```

**Łączny effort:** ~15-18h
**Brak quick winu** — wymaga zmian w obu warstwach (FE + BE)

---

## 4. WIELE WĄTKÓW / HISTORIA KONWERSACJI

### Stan obecny

- Jedna konwersacja per użytkownik
- Historia: 6 wiadomości (sliding window) w pamięci serwera
- localStorage: ostatnie 20 wiadomości (client-side, ginią po clear cache)
- Brak bazy danych, brak persystencji

### Plan implementacji

```
Blok 1: Baza danych (persystencja)
├── Task 4.1: Dodać SQLite (lub PostgreSQL na Railway)
│   - Tabele: conversations, messages, users
│   - Schema:
│     conversations: id, userId, title, serverTag, createdAt, updatedAt
│     messages: id, conversationId, role, content, toolCalls, createdAt
│   - SQLite = prostsze (better-sqlite3), zero config
│   - PostgreSQL = Railway addon, lepsze dla multi-user
│   - Decyzja: SQLite na start, migracja do PG gdy >5 userów
│   - Estimated: 4-5h
│
├── Task 4.2: API endpoints dla konwersacji
│   - GET /api/conversations — lista wątków usera
│   - POST /api/conversations — nowy wątek
│   - GET /api/conversations/:id — wiadomości wątku
│   - DELETE /api/conversations/:id — usunięcie
│   - PATCH /api/conversations/:id — rename
│   - Estimated: 3-4h
│
├── Task 4.3: Modyfikacja /api/chat
│   - Dodać conversationId do request body
│   - Zapisywać każdą parę user/assistant do DB
│   - Ładować historię z DB zamiast z request body
│   - Zwiększyć okno kontekstu: 6 → 10-12 messages (z DB)
│   - Estimated: 3h

Blok 2: Frontend — sidebar z wątkami
├── Task 4.4: Sidebar UI
│   - Lewa kolumna: lista wątków (tytuł + data + ikona serwera MCP)
│   - Auto-generowanie tytułu z pierwszego pytania
│   - Tagi/ikony: 📊 Analytics, 📧 Klaviyo, 🔍 SEO, 📈 Ads
│   - "Nowy wątek" button
│   - Estimated: 5-6h
│
├── Task 4.5: Przełączanie wątków
│   - Click na wątek → załaduj historię z API
│   - Zachowaj scroll position i stan terminala
│   - Animacja przejścia
│   - Estimated: 2-3h
│
├── Task 4.6: Wyszukiwanie w historii
│   - Search bar nad listą wątków
│   - Full-text search po treści wiadomości
│   - Estimated: 2h

Blok 3: Optymalizacja kontekstu
├── Task 4.7: Conversation summarization
│   - Po 10+ wiadomościach: Haiku generuje summary starej części
│   - Summary + ostatnie 6 messages = pełny kontekst
│   - Zmniejsza token cost przy długich konwersacjach
│   - Estimated: 3-4h
```

**Łączny effort:** ~25-30h
**Quick win:** Task 4.1 + 4.2 (backend DB + API) — fundamenty pod resztę

---

## 5. SENUTO + BING KONEKTORY

### 5A. Senuto MCP Server

Senuto to polskie narzędzie SEO (senuto.com) z REST API.

```
Task 5.1: Research Senuto API
├── Sprawdzić dokumentację API: https://api.senuto.com/docs
├── Kluczowe endpointy:
│   - Visibility Analysis (widoczność domeny)
│   - Keyword Research (frazy + wolumeny)
│   - SERP Analysis (pozycje w wynikach)
│   - Competitors (konkurencja)
│   - Content Planner (sugestie treści)
├── Auth: API key (header)
├── Estimated: 2h research

Task 5.2: Implementacja Senuto MCP (Python/FastMCP)
├── Wzorując się na google-ads-mcp (ten sam pattern)
├── Narzędzia:
│   - get_visibility — widoczność domeny genactiv.pl
│   - get_keywords — frazy z wolumenami i pozycjami
│   - get_competitors — analiza konkurencji SEO
│   - get_serp_analysis — pozycje dla wybranych fraz
│   - get_content_suggestions — sugestie treści (long-tail)
├── Estimated: 8-10h

Task 5.3: Integracja z routerem
├── Dodać "senuto" do config.js router prompt
├── Keywords: "SEO pozycje, widoczność, frazy kluczowe, Senuto, pozycjonowanie"
├── Env vars: SENUTO_API_KEY
├── Estimated: 1h
```

### 5B. Bing Ads MCP Server

Microsoft Advertising API (Bing Ads).

```
Task 5.4: Research Microsoft Advertising API
├── REST API: https://learn.microsoft.com/en-us/advertising/guides/
├── Auth: OAuth 2.0 (Microsoft Identity Platform)
│   - Client ID, Client Secret, Refresh Token
│   - Developer Token
├── Kluczowe endpointy:
│   - Reporting API (performance reports)
│   - Campaign Management (campaigns, ad groups, ads)
│   - Bulk API (large-scale operations)
├── Estimated: 2-3h research

Task 5.5: Implementacja Bing Ads MCP (Python/FastMCP)
├── Pattern: identyczny jak google-ads-mcp
├── Narzędzia:
│   - get_campaigns — lista kampanii
│   - get_performance_report — kliknięcia, wydatki, ROAS, konwersje
│   - get_keywords — słowa kluczowe z metrykami
│   - get_ad_groups — grupy reklam
│   - get_ads — poszczególne reklamy
├── Estimated: 8-10h

Task 5.6: Integracja z routerem + Dockerfile
├── Dodać "bing-ads" do config.js
├── Keywords: "Bing, Microsoft Ads, reklamy Bing"
├── Update Dockerfile: dodać bing-ads-mcp do build
├── Estimated: 2h
```

**Łączny effort:** ~25-30h
**Quick win:** Senuto (Task 5.1-5.3) — bezpośrednio wspiera SEO workflow

---

## HARMONOGRAM PROPONOWANY

### Sprint 1 (tydzień 1-2): Data Quality + Quick SEO Wins

| Task | Opis | Effort | Blokuje |
|------|------|--------|---------|
| 1.1 | Paginacja getOrders (>250) | 3h | 1.2 |
| 1.2 | Update analytics tools | 2h | — |
| 1.3 | Financial status filter | 1h | — |
| 1.5 | Data quality indicators | 1h | — |
| 2.1 | ALT text update tool | 4h | — |
| 2.4 | SEO audit tool | 4h | — |
| **Total** | | **~15h** | |

**Deliverable:** Dane z MCP odpowiadają Shopify Admin. Nowy tool do audytu + naprawy ALT textów.

### Sprint 2 (tydzień 3-4): File Upload + Revenue Reconciliation

| Task | Opis | Effort | Blokuje |
|------|------|--------|---------|
| 3.1 | Multer backend | 3h | 3.2 |
| 3.2 | Anthropic file passthrough | 5h | 3.6 |
| 3.4 | Upload UI | 4h | — |
| 1.6 | Revenue reconciliation tool | 4h | — |
| 1.7 | Unit testy | 2h | — |
| **Total** | | **~18h** | |

**Deliverable:** Można wrzucać pliki (CSV, obrazki, HTML). Revenue cross-validation.

### Sprint 3 (tydzień 5-6): Multi-thread + Senuto

| Task | Opis | Effort | Blokuje |
|------|------|--------|---------|
| 4.1 | SQLite DB | 5h | 4.2 |
| 4.2 | Conversations API | 4h | 4.4 |
| 4.4 | Sidebar UI | 6h | — |
| 5.1 | Senuto API research | 2h | 5.2 |
| 5.2 | Senuto MCP server | 10h | 5.3 |
| 5.3 | Router integration | 1h | — |
| **Total** | | **~28h** | |

**Deliverable:** Wiele wątków z historią. Senuto integration.

### Sprint 4 (tydzień 7-8): Bing + Polish + Write Tools

| Task | Opis | Effort | Blokuje |
|------|------|--------|---------|
| 5.4 | Bing API research | 3h | 5.5 |
| 5.5 | Bing Ads MCP | 10h | 5.6 |
| 5.6 | Router + Docker | 2h | — |
| 2.2 | Product content edit | 2h | — |
| 2.3 | Bulk SEO update | 3h | — |
| 4.5 | Thread switching | 3h | — |
| 4.7 | Conversation summarization | 4h | — |
| **Total** | | **~27h** | |

**Deliverable:** Bing Ads w terminalu. Bulk SEO operations. Płynne przełączanie wątków.

---

## ZALEŻNOŚCI I RYZYKA

| Ryzyko | Prawdopodobieństwo | Mitygacja |
|--------|---------------------|-----------|
| Senuto API — brak/ograniczona dokumentacja | Średnie | Task 5.1 to research-first; fallback: web scraping z API headless |
| Bing Ads — złożony OAuth Microsoft | Średnie | Wzorować na Google Ads flow; Microsoft ma SDK Pythonowy |
| SQLite na Railway — ephemeral filesystem | Wysokie | **Użyć Railway PostgreSQL addon** zamiast SQLite na produkcji |
| File upload — duże pliki = timeout | Niskie | Limit 10MB + streaming parse |
| Paginacja — Shopify rate limit (2/sec) | Niskie | Dodać backoff + progress reporting |

---

## DECYZJE DO PODJĘCIA PRZED STARTEM

1. **Baza danych:** SQLite (proste, lokalne) vs PostgreSQL (Railway addon, ~$7/mies.) — rekomenduję **PG na produkcji, SQLite na dev**
2. **Senuto:** Czy klient ma konto Senuto z API access? Potrzebny API key
3. **Bing Ads:** Czy klient ma konto Microsoft Advertising? Potrzebne credentials
4. **File upload limit:** 10MB wystarczy? Czy potrzebne duże pliki (video, heavy PDFs)?
5. **Theme editing:** Czy chcemy dać terminalowi write access do Shopify theme? (ryzyko vs. wygoda)

---

*Plan przygotowany: 4 kwietnia 2026*
*Do realizacji w Claude Code z subagentami per sprint*

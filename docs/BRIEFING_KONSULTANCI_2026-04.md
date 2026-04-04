# GenActiv — Briefing Techniczny i Biznesowy dla Konsultantów

**Data:** 4 kwietnia 2026
**Klient:** GenActiv.pl — Marka #1 colostrum w aptekach w Polsce
**Sklep:** genactiv.myshopify.com | Bramka: Przelewy24
**Kontakt techniczny:** Piotr Oleksiak (oleksiakpiotrrafal@gmail.com)

---

## Spis treści

1. [Podsumowanie wykonawcze](#1-podsumowanie-wykonawcze)
2. [Co zbudowaliśmy — GenActiv Online](#2-co-zbudowaliśmy--genactiv-online)
3. [Integracje MCP — 8 serwerów](#3-integracje-mcp--8-serwerów)
4. [E-mail marketing (Klaviyo)](#4-e-mail-marketing-klaviyo)
5. [SEO — stan prac](#5-seo--stan-prac)
6. [Krytyczny problem: Atrybucja remarketingowa = 1%](#6-krytyczny-problem-atrybucja-remarketingowa--1)
7. [Automatyzacja i raportowanie](#7-automatyzacja-i-raportowanie)
8. [Ograniczenia techniczne i znane problemy](#8-ograniczenia-techniczne-i-znane-problemy)
9. [Stack technologiczny](#9-stack-technologiczny)
10. [Otwarte pytania i decyzje do podjęcia](#10-otwarte-pytania-i-decyzje-do-podjęcia)

---

## 1. Podsumowanie wykonawcze

GenActiv.pl to polska marka colostrum bovinum, lider sprzedaży w aptekach. W ciągu ostatnich miesięcy zbudowaliśmy zintegrowaną platformę AI do zarządzania marketingiem, łączącą **7 serwisów API** (Klaviyo, Shopify, Google Ads, Meta Ads, GA4, TikTok Ads, Shopify Analytics) w jeden interfejs terminalowy dostępny z przeglądarki.

### Co działa
- **GenActiv Online** — przeglądarkowy terminal AI (Claude) z dostępem do 80+ narzędzi marketingowych
- **Klaviyo** — 52 kampanie, 4 flow-y automatyczne, szablony HTML
- **Shopify Extended** — niestandardowe narzędzia analityczne (ROAS kampanii, atrybucja źródeł ruchu, analityka produktów)
- **Google Ads + GA4** — pełne dane GAQL, raporty analityczne, keyword planner
- **Meta Ads** — kampanie, insights, audience research
- **Baselinker** — automatyczna synchronizacja Payment ID (co godzinę, GitHub Actions)
- **SEO techniczne** — schema BreadcrumbList (150+ stron), meta descriptions, FAQPage

### Co nie działa / wymaga uwagi
- **Atrybucja kampanii: 1%** — tylko 3 z 250 zamówień mają przypisane źródło kampanii (Pandectes consent)
- **TikTok Ads MCP** — skonfigurowany, ale nieaktywny (brak tokenu OAuth)
- **SEO strategiczne** — plan 140 tys. PLN / 6 miesięcy czeka na zatwierdzenie
- **~530 błędów interpunkcyjnych** na stronie (cytaty naukowe)
- **OAuth Google** — tokeny wygasają co 7 dni w trybie "Testing" (do publikacji consent screen)

---

## 2. Co zbudowaliśmy — GenActiv Online

### Architektura

```
Przeglądarka (genactiv.oleksiakconsulting.com)
      │
      │  SSE (Server-Sent Events)
      ▼
Express.js (Railway.app)
      │
      ├─ Autentykacja (bcrypt + sesja 24h)
      ├─ Rate limiter (500ms min między zapytaniami)
      │
      ▼
Anthropic API — Dwufazowy routing zapytań
      │
      ├─ Faza 1 (Router): Claude Haiku → klasyfikacja zapytania → wybór serwera MCP (~500 tokenów)
      └─ Faza 2 (Main): Claude Sonnet → przetwarzanie z narzędziami wybranego serwera (max 4096 tokenów)
              │
              ▼
        7 serwerów MCP (stdio)
              ├── Klaviyo (Python/uvx)
              ├── Shopify Extended (Node.js, 15 narzędzi analitycznych)
              ├── Shopify Standard (Node.js, CRUD)
              ├── Meta Ads (Python)
              ├── Google Ads (Python/FastMCP)
              ├── GA4 (Python/analytics-mcp)
              └── TikTok Ads (Python, nieaktywny)
```

### Dwufazowy routing — kluczowa optymalizacja

Problem: 80+ narzędzi MCP = ~22 tys. tokenów w jednym zapytaniu → 429 Rate Limit.

Rozwiązanie:
1. **Faza 1:** Haiku klasyfikuje zapytanie jednym słowem (np. "google-ads") — koszt ~500 tokenów
2. **Faza 2:** Sonnet otrzymuje tylko narzędzia wybranego serwera (3-21 zamiast 80+) — koszt ~1.8 tys. tokenów

Redukcja payload: **90%**. Eliminuje błędy 429.

### Deployment

| Element | Wartość |
|---------|---------|
| Hosting | Railway.app (Docker: Node 18 + Python 3 + uv) |
| URL | `genactiv.oleksiakconsulting.com` |
| Health check | `GET /api/health` |
| Projekt Railway | cozy-trust / exemplary-learning |
| Main model | claude-sonnet-4-20250514 |
| Router model | claude-haiku-4-5-20251001 |
| Max tool rounds | 8 per zapytanie |
| Historia konwersacji | 6 wiadomości (3 pary, sliding window) |
| Limit wyniku narzędzia | 15 000 znaków (auto-kompresja) |

### Koszty operacyjne

Główny koszt: Anthropic API (tokenowy). Dwufazowy routing zmniejsza zużycie tokenów o ~90% w porównaniu z naiwnym podejściem (wszystkie 80 narzędzi w każdym zapytaniu).

---

## 3. Integracje MCP — 8 serwerów

MCP (Model Context Protocol) to standard Anthropic do łączenia AI z zewnętrznymi API. Każdy serwer MCP udostępnia zestaw narzędzi (tools), które Claude może wywoływać w trakcie rozmowy.

### 3.1 Klaviyo MCP (21 narzędzi)

| Funkcja | Narzędzia |
|---------|-----------|
| Kampanie | get_campaigns, get_campaign (+ report z metrykami) |
| Flow-y | get_flows, get_flow (+ report) |
| Profile / Listy / Segmenty | get_profiles, get_lists, get_segments |
| Metryki / Eventy | get_metrics, get_events |
| Katalog | get_catalog_items |
| Tworzenie | create_email_template, create_campaign, create_profile |
| Subskrypcje | subscribe/unsubscribe_profile_to_marketing |
| Obrazy | upload_image_from_url, upload_image_from_file |

### 3.2 Shopify Extended MCP (15 narzędzi, custom)

Autorski serwer TypeScript z narzędziami analitycznymi, których brakuje w standardowym Shopify MCP:

| Narzędzie | Opis |
|-----------|------|
| **get-traffic-source-analytics** | Rozbicie źródeł ruchu (UTM) per zamówienie |
| **get-campaign-performance** | ROAS, przychód per źródło kampanii |
| **get-conversion-metrics** | CVR trendy per kanał |
| **get-product-performance** | Analityka sprzedaży produktów |
| update-product-seo | Aktualizacja meta title/description produktu |
| update-collection-seo | Aktualizacja meta kolekcji |
| + standardowy CRUD | get-products, get-orders, get-customers, etc. |

### 3.3 Google Ads MCP (3 narzędzia)

- **run_gaql** — zapytania GAQL (kliknięcia, wyświetlenia, konwersje, CPC, ROAS)
- **run_keyword_planner** — research słów kluczowych
- **list_accounts** — lista kont
- Konto: 339-338-2047 (MCC: 253-832-8866)

### 3.4 Meta Ads MCP (6+ narzędzi)

- get_campaigns, get_ad_accounts, get_adsets, get_ads
- **get_insights** — wydatki, ROAS, CTR, CPC, konwersje
- **search_interests** — research targetowania
- **search_ads_archive** — analiza konkurencji
- Pixel ID: 370142134442442

### 3.5 GA4 MCP (6 narzędzi)

- **run_report** — sesje, użytkownicy, źródła, pageviews, bounce rate
- **run_realtime_report** — dane w czasie rzeczywistym
- Property ID: 279858535, Measurement ID: G-KE8T99MGMJ

### 3.6 TikTok Ads MCP (6 narzędzi) — NIEAKTYWNY

- get_campaigns, get_ad_groups, get_ads, get_reports
- Status: kod wdrożony, brak tokenu OAuth
- Do aktywacji: `python3 generate_tiktok_token.py` + restart serwisu

### 3.7 Chrome DevTools MCP — tylko lokalne

- Automatyzacja przeglądarki, screenshoty, analiza performance
- Niedostępny w web terminalu (wymaga Chrome z DevTools Protocol)

---

## 4. E-mail marketing (Klaviyo)

### Stan konta

| Element | Wartość |
|---------|---------|
| Kampanie | 52 (email jako główny kanał, SMS segmentowy) |
| Flow-y | 4 aktywne (abandoned cart, post-purchase, welcome series, +1) |
| Integracja Shopify | Natywna (Placed Order, Browse Abandonment, etc.) |
| UTM | `?utm_source=klaviyo&utm_medium=email&utm_campaign=[name]` |

### Standardy szablonów

- Inline CSS, layout tabelowy, max 600px desktop, min 320px mobile
- Stack <480px, rozmiar <100KB
- Unsubscribe: `{% unsubscribe 'Anuluj subskrypcję' %}` (wymagany)
- Personalizacja: `{{ first_name|default:"" }}`, `{{ event.ProductName }}`
- Waluta: PLN, bez miejsc dziesiętnych

### Branding

| Element | Wartość |
|---------|---------|
| Brand Blue | `#0066CC` |
| GenActiv Red (CTA) | `#EF3340` |
| Success Green | `#27ae60` |
| Trust Navy | `#1A3B5D` |
| Font | `'Branding-medium', Helvetica, Arial, sans-serif` |
| Język | polski |

---

## 5. SEO — stan prac

### Zrealizowane (styczeń 2026)

| Zadanie | Zakres | Efekt |
|---------|--------|-------|
| BreadcrumbList Schema (JSON-LD) | ~150+ stron | +5-10% CTR w SERP |
| Meta descriptions — kolekcje | 24 kolekcje (via Shopify GraphQL) | +15-20% indeksacja kolekcji |
| Meta descriptions — produkty | 8 produktów (pokrycie: 98.8%) | +5% indeksacja produktów |
| FAQPage Schema | strona /pages/faq | Rich snippet eligible |
| Literówki | WSZYSTKIE poprawione (zweryfikowane 2026-03-17) | "GENACITV"→"GENACTIV", test FAQ, announcement bar |

### Do zrobienia

| Zadanie | Priorytet | Status |
|---------|-----------|--------|
| ~530 błędów interpunkcyjnych | Średni | Niezdecydowany — głównie cytaty naukowe |
| FAQ Schema — 3 duplikaty | Średni | Częściowo naprawione |
| Footer "Cookkies" (podwójne k) | Niski | Widoczne na wszystkich stronach |
| **Plan strategiczny SEO** | **Wysoki** | **Czeka na decyzję (140 tys. PLN / 6 mies.)** |

### Plan strategiczny SEO — główne wnioski

Dokument: `seo/Genactiv_SEO_Analiza_Rekomendacje.md`

**Mocne strony:**
- TOP 1-3 dla głównych fraz "colostrum" (silna pozycja w niszy)

**Problemy:**
- Stagnacja wzrostu (54% spadek ruchu lipiec vs. czerwiec 2025 — sezonowy?)
- Niska dywersyfikacja — 0 fraz TOP 3 poza kategorią "colostrum"
- Słaba obecność long-tail ("jak stosować", "skutki uboczne", "najlepsze colostrum")
- Niewykorzystane frazy transakcyjne ("kup colostrum", "opinie", "ceny")

**Rekomendacje strategiczne:**
- Ekspansja na "odporność", "zdrowie jelit", "probiotyki naturalne"
- Content marketing na long-tail
- Optymalizacja synergii PPC vs. organic (konkurują o te same frazy)

**Budżet:** 140 000 PLN | **Czas:** 6 miesięcy | **Status:** Oczekuje na zatwierdzenie

---

## 6. Krytyczny problem: Atrybucja remarketingowa = 1%

### Opis problemu

Spośród ~250 przeanalizowanych zamówień, **tylko 3** mają przypisane źródło kampanii (wszystkie 3 = Bing/Sembot). **Zero zamówień** przypisanych do Google Ads lub Meta Ads.

### Przyczyna źródłowa

Pandectes Consent Banner (GDPR) blokuje **wszystkie** opcjonalne cookies domyślnie:

```javascript
cookiesBlockedByDefault: "7"  // 1 (Functional) + 2 (Performance) + 4 (Targeting) = ALL BLOCKED
```

| Sygnał Consent Mode v2 | Kategoria | Default | Efekt |
|------------------------|-----------|---------|-------|
| `ad_storage` | 4 (Targeting) | **DENIED** | Brak śledzenia Google Ads |
| `ad_user_data` | 4 (Targeting) | **DENIED** | Brak danych first-party |
| `ad_personalization` | 4 (Targeting) | **DENIED** | Brak personalizowanych reklam |
| `analytics_storage` | 2 (Performance) | **DENIED** | Brak event tracking GA4 |

**Rezultat:** Remarketing nie działa. Google/Meta nie mogą budować audiences. Konwersje nie są raportowane.

### Wpływ biznesowy

- Nie wiemy, które kampanie generują sprzedaż
- Nie możemy optymalizować ROAS (brak danych konwersji)
- Remarketing lists praktycznie puste
- Budżet reklamowy wydawany "w ciemno"

### Możliwe rozwiązania (do dyskusji)

| Rozwiązanie | Opis | Ryzyko | Efekt |
|-------------|------|--------|-------|
| **1. UX consent bannera** | Zmiana tekstu/layoutu na bardziej zachęcający do akceptacji | Niskie | +10-30% consent rate |
| **2. Enhanced Conversions** | Haszowane email/telefon na thank_you page (obejście cookies) | Niskie | Dane konwersji nawet bez cookies |
| **3. Customer Match upload** | Upload listy klientów do Google/Meta Ads | Niskie | Remarketing bez cookies |
| **4. Server-Side GTM** | Przeniesienie tracking server-side (mniejsza zależność od cookies) | Średnie | Lepsza atrybucja |
| **5. Zmiana cookiesBlockedByDefault** | Z "7" na "3" (odblokowanie targeting) | **Prawne!** | Natychmiastowa poprawa, ale wymaga opinii prawnej GDPR |

### Status audytu

Dokument: `docs/AUDYT_DANYCH_CHECKLIST.md` — 5 faz, 50+ checkpointów

| Faza | Opis | Status |
|------|------|--------|
| 1. UTM Tagging | Poprawność tagowania kampanii | Nie rozpoczęta |
| 2. Conversion Tracking | Konfiguracja śledzenia konwersji | Nie rozpoczęta |
| 3. Consent & Privacy | Analiza consent rate i konfiguracji | Nie rozpoczęta |
| 4. Shopify as Aggregator | Weryfikacja atrybucji w Shopify | Nie rozpoczęta |
| 5. Integration Sync | Spójność danych między platformami | Nie rozpoczęta |

**Pełny raport:** `reports/REMARKETING_AUDIT_2025-01-23.md`

---

## 7. Automatyzacja i raportowanie

### GitHub Actions

| Workflow | Harmonogram | Opis |
|----------|-------------|------|
| sync-payment-id.yml | Co godzinę + manual | Synchronizacja Payment ID: Shopify → Baselinker |

### Raporty (generowane)

| Raport | Typ | Zawartość |
|--------|-----|-----------|
| Dashboard operacyjny | Excel (multi-sheet) | KPI tygodniowe, top produkty, źródła ruchu, trendy |
| Weryfikacja źródeł ruchu | Excel | Rozbicie UTM vs. rzeczywiste źródła |
| Raport spójności | Excel | Plan napraw niespójności danych |
| Audit remarketingu | Markdown | Deep-dive atrybucji (1% rate) |

### Skrypty Python (lokalne)

```
baselinker_api.py          — Klient Baselinker API (zamówienia, płatności)
sync_payment_id.py         — Sync Payment ID Shopify→Baselinker (dry run / --live)
shopify_graphql.py         — Zapytania GraphQL (transakcje, zamówienia)
shopify_theme_api.py       — Theme API (backup, update, search)
generate_ga4_token.py      — Regeneracja OAuth GA4
generate_tiktok_token.py   — Generowanie OAuth TikTok
dashboard_operacyjny.py    — Generator dashboardu operacyjnego
```

---

## 8. Ograniczenia techniczne i znane problemy

### Aktywne problemy

| Problem | Ważność | Przyczyna | Obejście |
|---------|---------|-----------|----------|
| **Atrybucja 1%** | KRYTYCZNY | Pandectes `cookiesBlockedByDefault=7` | Patrz sekcja 6 |
| **TikTok MCP nieaktywny** | Wysoki | Brak tokenu OAuth | `python3 generate_tiktok_token.py` (5 min) |
| **Google OAuth wygasa co 7 dni** | Wysoki | Consent screen w trybie "Testing" | Opublikować consent screen → tokeny nie wygasają |
| **Meta Ads MCP pada lokalnie** | Niski | Problem z modułem Python | Działa na Railway (Docker) |

### Ograniczenia architektoniczne

| Ograniczenie | Opis | Wpływ |
|-------------|------|-------|
| Historia 6 wiadomości | Sliding window (3 pary user/assistant) | Utrata kontekstu w dłuższych konwersacjach |
| Limit wyniku 15 tys. znaków | Duże wyniki z MCP są obcinane | Wymaga zawężania zapytań (daty, limity) |
| Brak bazy danych | Sesje w pamięci, brak persystencji | Restart = utrata sesji |
| Single-server routing | Jedno zapytanie = jeden serwer MCP | Nie obsługuje pytań cross-platform ("porównaj Google Ads vs Meta") |
| Max 8 tool rounds | Pętla tool_use ograniczona do 8 iteracji | Złożone analizy mogą być ucięte |
| ~10-20 równoległych użytkowników | Ograniczenie Railway (shared CPU/RAM) | Bottleneck: Anthropic API rate limits |

### Koszty i zależności

- **Anthropic API** — główny koszt operacyjny (tokenowy, zmienny)
- **Railway.app** — hosting (plan zależy od zużycia CPU/RAM)
- **7 zewnętrznych API** — każde z własnym limitem, tokenem, polityką
- **OAuth Google** — wymaga ręcznej regeneracji co 7 dni (do czasu publikacji consent screen)

---

## 9. Stack technologiczny

### Frontend (przeglądarka)
- HTML5 + CSS3 + vanilla JavaScript (bez frameworka)
- Dark terminal theme, markdown rendering (marked.js)
- SSE (Server-Sent Events) do streamingu odpowiedzi AI

### Backend
| Komponent | Technologia | Wersja |
|-----------|-------------|--------|
| Serwer | Express.js | 4.18.2 |
| AI SDK | @anthropic-ai/sdk | 0.71.2 |
| MCP SDK | @modelcontextprotocol/sdk | 1.17.1 |
| Auth | bcryptjs + express-session | 2.4.3 / 1.17.3 |
| Security | helmet | 8.1.0 |
| Runtime | Node.js | 18 |
| Python | 3.11+ | Dla MCP serwerów |

### Infrastruktura
| Element | Technologia |
|---------|-------------|
| Hosting | Railway.app (Docker) |
| CI/CD | GitHub Actions |
| DNS | CNAME → Railway |
| Konteneryzacja | Docker (Node 18 + Python 3 + uv) |
| Version control | GitHub |

### Zewnętrzne platformy
| Platforma | Rola |
|-----------|------|
| Shopify | E-commerce, produkty, zamówienia, customers |
| Klaviyo | Email/SMS marketing, automation |
| Google Ads | Reklama w wyszukiwarce |
| Meta Ads | Facebook/Instagram reklama |
| GA4 | Analityka webowa |
| TikTok Ads | Reklama TikTok (do aktywacji) |
| Baselinker | Synchronizacja zamówień/płatności |
| Pandectes | Consent management (GDPR) |
| Przelewy24 | Bramka płatności |

---

## 10. Otwarte pytania i decyzje do podjęcia

### Pilne (do rozwiązania w ciągu 1-2 tygodni)

1. **Jak naprawić atrybucję 1%?**
   - Które z rozwiązań z sekcji 6 wdrożyć?
   - Czy zmiana Pandectes wymaga opinii prawnej?
   - Jaki jest akceptowalny consent rate?

2. **Google OAuth consent screen — publikacja**
   - Publikacja eliminuje problem wygasających tokenów (7 dni → nigdy)
   - Wymaga: review przez Google (może potrwać)

3. **TikTok Ads — czy aktywować?**
   - Czy GenActiv prowadzi/planuje kampanie TikTok?
   - Jeśli tak — 5 min na generację tokenu OAuth

### Średnioterminowe (1-3 miesiące)

4. **Plan strategiczny SEO — 140 tys. PLN / 6 miesięcy**
   - Zatwierdzić, zmodyfikować, czy odrzucić?
   - Priorytet: long-tail vs. nowe nisze ("odporność", "zdrowie jelit")?

5. **Cross-platform queries**
   - Obecna architektura: 1 zapytanie = 1 serwer MCP
   - Pytania typu "porównaj Google Ads vs Meta Ads" wymagają przebudowy routingu
   - Czy to jest potrzebne?

6. **Persystencja danych**
   - Brak bazy danych (sesje w pamięci)
   - Czy potrzebna historia konwersacji? Logi? Dashboard?

### Strategiczne

7. **Skalowanie web terminala**
   - Obecny limit: ~10-20 użytkowników
   - Czy terminal ma być narzędziem wewnętrznym, czy produktem?
   - Plany na większe obciążenie?

8. **Automatyzacja marketingowa**
   - Dziś: terminal jest narzędziem query/response
   - Przyszłość: automatyczne kampanie? Scheduled reports? Alerty?
   - Jak daleko chcemy iść z automatyzacją?

9. **Budżet i ROI**
   - Koszt Anthropic API (tokenowy) — jaki miesięczny budżet?
   - Koszt Railway — jaki plan?
   - Jak mierzyć ROI platformy vs. ręczne zarządzanie marketingiem?

---

## Załączniki — kluczowe pliki w repozytorium

| Plik | Opis |
|------|------|
| `CLAUDE.md` | Główna dokumentacja projektu (architektura, konfiguracje, komendy) |
| `genactiv-online/server/config.js` | Konfiguracja wszystkich serwerów MCP, modeli AI, promptów |
| `docs/AUDYT_DANYCH_CHECKLIST.md` | Checklist audytu atrybucji (5 faz, 50+ checkpointów) |
| `reports/REMARKETING_AUDIT_2025-01-23.md` | Pełny raport audytu remarketingu |
| `seo/SEO_PODSUMOWANIE_WDROZENIA.md` | Podsumowanie wdrożenia SEO technicznego |
| `seo/Genactiv_SEO_Analiza_Rekomendacje.md` | Plan strategiczny SEO (140 tys. PLN) |
| `docs/MIGRATION_PLAN_ONLINE.md` | Specyfikacja migracji do web terminala |
| `genactiv-online/README.md` | Quick-start guide (po polsku) |

---

*Dokument przygotowany: 4 kwietnia 2026*
*Cel: Briefing dla zewnętrznych konsultantów — zarówno technicznych, jak i biznesowych*

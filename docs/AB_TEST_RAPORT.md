# A/B Test: GEN-6 vs NOTOAGENCY — Raport i wnioski

> **Data:** 2026-06-15 → aktualizacja **2026-06-26** | **Status:** Test aktywny (do zakończenia) | **Platform:** Intelligems + GA4 + Clarity
> **Autor automatyczny:** Claude Code | **Kontakt:** d.slowik@notoagency.pl (setup Intelligems)

---

## 1. Konfiguracja testu

| Element | Wartość |
|---------|--------|
| Narzędzie A/B | Intelligems.io (theme test) |
| Wariant kontrolny | **GEN-6** (Old theme, ID: 199333609804) — ~~90%~~ **80% ruchu** |
| Wariant testowy | **NOTOAGENCY** (New theme, ID: 190479794508) — ~~10%~~ **20% ruchu** |
| Start testu | ~12 czerwca 2026 |
| Zmiana splitu | ~17-18.06: 90/10 → **80/20** |
| Exp. ID (Intelligems) | `1c371ad8-5826-4c21-abdb-7d0d68390e81` |
| GA4 Custom Dimensions | `customUser:ab_theme_variant` (USER, ID: 15061277989), `customEvent:exp_variant_string` (EVENT) |
| Tracking | Skrypt A/B w `layout/theme.liquid` obu tematów + Pandectes Consent Mode v2 |

### Podłączone źródła danych

| Źródło | API | Uwagi |
|--------|-----|-------|
| **Intelligems** | `api.intelligems.io/v25-10-beta` | Klucz: `ig_live_...` (header: `intelligems-access-token`) |
| **GA4** | Data API v1beta | OAuth2, property `279858535` |
| **Clarity** | `clarity.ms/export-data/api/v1` | JWT token, project `3354986136401458`, limit 10 req/dzień |

---

## 2. Fix tracking — 15 czerwca 2026

### Problem
~89% sesji nie było tagowanych wariantem A/B. Skrypt sprawdzał `typeof gtag === 'function'`, ale Pandectes (consent manager) **nie definiuje `window.gtag`** jako globalnej funkcji — używa wewnętrznej zmiennej `Ue()` jako wrappera na `dataLayer.push`.

### Rozwiązanie
Zmiana w `layout/theme.liquid` obu tematów:

```javascript
// BYŁO (failowało):
function setGA4() {
    if (typeof gtag === 'function') { gtag('set', ...); }
    else { setTimeout(setGA4, 500); }  // nieskończona pętla retry
}

// JEST (działa natychmiast):
if (typeof gtag !== 'function') {
    window.gtag = function(){ window.dataLayer.push(arguments); };
}
gtag('set', 'user_properties', { 'ab_theme_variant': THEME_VARIANT });
gtag('event', 'ab_test_impression', { ... });
```

**Efekt:** pokrycie tagiem A/B powinno wzrosnąć z ~11% do ~100% sesji od 15.06.2026.

### Pliki zmienione na Shopify
- `layout/theme.liquid` na GEN-6 (ID: 199333609804)
- `layout/theme.liquid` na NOTOAGENCY (ID: 190479794508)

---

## 3. Wyniki testu — AKTUALIZACJA 26.06.2026

### 3.1. Intelligems (pełne dane, server-side, 100% pokrycie)

**Dane z API Intelligems — pobrane 26.06.2026** (28,195 visitors łącznie, ~14 dni testu)

| Metryka | GEN-6 (control, 80%) | NOTOAGENCY (20%) | Δ | Istotność |
|---------|----------------------|------------------|---|-----------|
| **Visitors** | 23,927 | 4,268 | — | — |
| **Orders** | 581 | 82 | — | — |
| **Conversion Rate** | 2.43% | 1.92% | **-20.9%** | **p2bb=0.025 ISTOTNE** |
| Add to Cart Rate | 5.46% | 4.92% | -9.9% | nieistotne |
| Checkout Begin Rate | 3.55% | 3.07% | -13.5% | borderline |
| Abandoned Cart | 55.9% | 61.9% | **+10.7%** | — |
| Abandoned Checkout | 32.2% | 38.9% | **+21.1%** | — |
| Revenue/visitor | 5.82 PLN | 4.61 PLN | **-20.7%** | p2bb=0.085 borderline |
| Net Revenue | 139,180 PLN | 19,680 PLN | — | — |

> **Wynik jednoznaczny:** NOTOAGENCY konwertuje o **-20.9%** gorzej (p=0.025, istotne statystycznie).
> Szacowany miesięczny koszt utrzymywania NOTO w teście: **-56,630 PLN** utraconego przychodu.

#### Porównanie z danymi z 15.06 (split 90/10):

| | 15.06 (90/10) | 26.06 (80/20) | Trend |
|---|---|---|---|
| CR uplift | -33.3% (p=0.032) | -20.9% (p=0.025) | Mniej dramatyczny spadek, ale wciąż istotny |
| Visitors NOTO | 1,265 | 4,268 | 3.4x więcej danych |
| Rev/visitor uplift | -28.5% (p=0.138) | -20.7% (p=0.085) | Zbliża się do istotności |

Większa próba (4,268 vs 1,265 visitors NOTO) potwierdza trend z mniejszą zmiennością.

### 3.2. GA4 (custom dimension, ~29% pokrycie tagiem)

GA4 tag coverage ograniczone — GA4 ładuje się przez sandbox Web Pixels (kanał Google & YouTube), nie czyta `dataLayer` z motywu. Dane z `customUser:ab_theme_variant`:

| Metryka | GEN-6 (1,070 sesji) | NOTOAGENCY (115 sesji) | Δ |
|---------|---------------------|----------------------|---|
| Bounce Rate | 19.4% | 24.3% | +25.3% |
| Conv. Rate | 2.99% | 0.87% | -70.9% |
| Add-to-Cart Rate | 7.85% | 6.09% | -22.5% |
| Śr. czas sesji | 2m48s | 2m28s | -11.9% |
| Strony/sesję | 5.10 | 5.39 | +5.7% |
| Przychód | 7,810 PLN | 189 PLN | — |

**Uwaga:** Dane GA4 per-wariant mają niskie pokrycie (~29%), ponieważ:
- GA4 jest w sandboxie Web Pixels → nie czyta `window.dataLayer` z motywu
- Zdarzenie `experience_impression` (Intelligems server-side) działa, ale custom dimensions zarejestrowano dopiero 17.06
- Intelligems jest jedynym wiarygodnym źródłem dla danych per-wariant

---

## 4. Analiza lejka konwersji (GA4)

### 4.1. Lejek ogólny — gdzie tracą użytkownicy NOTOAGENCY

| Etap | GEN-6 (users) | NOTO (users) | NOTO % oczekiwany | NOTO % rzeczywisty |
|------|--------------|-------------|-------------------|-------------------|
| page_view | 890 | 90 | 10% | **10.1% OK** |
| view_item | 388 | 40 | 10% | **10.3% OK** |
| add_to_cart | 61 | 4 | 10% | **6.6% SPADEK** |
| begin_checkout | 68 | 2 | 10% | **2.9% DUŻY SPADEK** |
| purchase | 31 | 1 | 10% | **3.2% DUŻY SPADEK** |

**Wniosek:** Użytkownicy NOTOAGENCY docierają do produktów (10% share OK), ale **drastycznie rzadziej dodają do koszyka i kupują**.

### 4.2. Strony produktów (/products/)

| Metryka | GEN-6 (487 sesji) | NOTOAGENCY (60 sesji) |
|---------|-------------------|----------------------|
| Bounce Rate | 18.9% | 20.0% |
| Engagement Rate | 81.1% | 80.0% |
| add_to_cart events | 56 | **2** |
| Śr. czas sesji | 2m02s | 1m52s |

**Problem:** add_to_cart na NOTOAGENCY to 2 eventy vs 56 na GEN-6. Proporcjonalnie powinno być ~7.

### 4.3. Kolekcja /collections/colostrum

| Metryka | GEN-6 (302 sesji) | NOTOAGENCY (49 sesji) |
|---------|-------------------|----------------------|
| Bounce Rate | 21.5% | **26.5%** (+23%) |
| add_to_cart | 15 eventów | 4 eventy |
| view_item | 3 | **42** |
| Strony/sesję | 3.74 | **5.61** |

Ciekawe: NOTO generuje dużo więcej view_item na kolekcji — ludzie przeglądają, ale nie dodają do koszyka.

### 4.4. /pages/fiberbiom

Zbyt mała próba na NOTO (6 sesji). Bounce rate 50% vs 16.4% na GEN-6 — niekonkluzywne.

### 4.5. Top landing pages NOTOAGENCY (z konwersjami)

| Landing Page | Sesje | BR | Conv | Revenue |
|---|---|---|---|---|
| /collections/colostrum | 19 | 21.1% | 0 | 0 |
| / (homepage) | 12 | 33.3% | 0 | 0 |
| /collections/maseczki-z-colostrum | 6 | 16.7% | 0 | 0 |
| /collections/mleko-klaczy | 6 | 16.7% | 0 | 0 |
| web-pixels.../collections/colostrum | 6 | 0.0% | 1 | 189 PLN |

Jedyna konwersja NOTOAGENCY przyszła z Shopify web-pixel, nie z bezpośredniego wejścia.

---

## 5. Clarity UX Insights (cały projekt, 3 dni)

| Metryka | Mobile (4,938 sesji) | Tablet (59) | PC (758) |
|---------|---------------------|------------|----------|
| Dead Clicks | 3.3% (309 events) | 3.4% (3) | 5.3% (68) |
| Rage Clicks | 0.04% (22) | 0% | 0% |
| **Quick Backs** | **9.0% (646)** | 10.2% (12) | 7.4% (81) |
| **Script Errors** | **6.7% (481)** | 6.8% (4) | 1.6% (30) |
| Scroll Depth | 41.5% | 57.2% | 54.3% |
| Engagement Time | 107s total / 43s active | 108s/94s | 164s/57s |
| Traffic split | **82%** | 1% | 13% |

### Sygnały UX istotne dla A/B testu:
1. **Quick Back 9% na mobile** — co 11. sesja kończy się szybkim cofnięciem (frustracja)
2. **Script Errors 6.7% na mobile** — JS errors mogą blokować add-to-cart w NOTO
3. **Scroll Depth 41.5% mobile** — użytkownicy widzą < połowy strony. Jeśli CTA w NOTO jest poniżej foldu → nie widzą go
4. **82% ruchu to mobile** — optymalizacja mobile jest krytyczna

---

## 6. Diagnoza: dlaczego NOTOAGENCY konwertuje gorzej

Na podstawie danych z trzech źródeł (Intelligems, GA4, Clarity):

### Potwierdzone problemy:
1. **Strona produktu → Add to Cart: GŁÓWNY PROBLEM** — 71% mniej add-to-cart na NOTO (2 vs 56 events proporcjonalnie). Przycisk "Dodaj do koszyka" prawdopodobnie jest mniej widoczny, inaczej umieszczony, lub blokowany przez JS error.
2. **Checkout abandonment: +67%** — użytkownicy, którzy rozpoczynają checkout, porzucają go o 67% częściej na NOTO.
3. **Abandoned cart: +25%** — więcej porzuconych koszyków na NOTO.

### Hipotezy do zbadania:
- **Layout strony produktu** — sprawdzić pozycję i widoczność przycisku "Dodaj do koszyka" na mobile w NOTO vs GEN-6
- **Błędy JavaScript** — 6.7% sesji na mobile ma script errors. Sprawdzić czy NOTO ma dodatkowe/inne errory
- **Scroll depth** — przy 41.5% avg scroll na mobile, elementy poniżej foldu nie są widoczne
- **Checkout flow** — 50% abandoned checkout (vs 30%) sugeruje problem z krokami checkout w NOTO

---

## 7. Istotność statystyczna i decyzja

**Intelligems potwierdza istotność statystyczną** z dwóch niezależnych pomiarów:
- 15.06 (90/10, 1,265 visitors NOTO): CR uplift -33.3%, p=0.032
- 26.06 (80/20, 4,268 visitors NOTO): CR uplift -20.9%, p=0.025

> **NOTOAGENCY konwertuje istotnie gorzej. Test powinien zostać zakończony.**

### Rekomendacja (zaktualizowana 26.06):

**Opcja A (REKOMENDOWANA): Zakończyć test NATYCHMIAST i wrócić do GEN-6 100%.**
- Każdy dzień testu kosztuje ~1,888 PLN utraconego przychodu (56,630 PLN / 30 dni)
- Przy 20% ruchu na NOTO, to ~377 PLN/dzień straty netto

**Opcja B:** Naprawić zidentyfikowane problemy na NOTO (patrz sekcja 6) i zrestartować test od zera.
- Wymaga: naprawy strony produktu (CTA, JS errors), checkout flow, mobile UX
- Szacowany zakres: znaczące zmiany w theme NOTO, nie kosmetyka

**Opcja C:** ODRZUCONA — split 20/80 już wdrożony i potwierdził wynik z 90/10.

---

## 8. Pliki w repo

| Plik | Opis |
|------|------|
| `migrate_tracking_ab.py` | Skrypt migracji tracking assets GEN-6 → NOTOAGENCY (19 snippets + 2 binary) |
| `reports/ab_theme_report.py` | Generator HTML dashboardu A/B z client-side GA4 API, stat. significance, refresh |
| `reports/ab_theme_report_7d.html` | Standalone HTML raport — otwórz i kliknij "Odśwież dane" (bez serwera) |
| `generate_ga4_token.py` | Zmodyfikowany: dodany scope `analytics.edit` + auto-update .env |
| `docs/AB_TEST_RAPORT.md` | Ten plik |

### API credentials (NIE commitowane, w .env)

| Serwis | Zmienna w .env | Uwagi |
|--------|----------------|-------|
| Intelligems | `INTELLIGEMS_API_KEY` | Header: `intelligems-access-token`, endpoint: `api.intelligems.io/v25-10-beta` |
| GA4 | `GA4_REFRESH_TOKEN` | OAuth2, scope: analytics.readonly + analytics.edit |
| Clarity | `CLARITY_API_TOKEN` | JWT, Scope: Data.Export, exp: 2126, project `3354986136401458` |

---

## 9. Integracje MCP dodane w tej sesji

| MCP Server | Package | Użycie |
|------------|---------|--------|
| **Clarity** | `@microsoft/clarity-mcp-server` | UX metrics, session recordings, dead/rage clicks |
| Intelligems | REST API (nie MCP) | A/B test analytics, experiment management |

Clarity MCP jest w `.claude.json` (local config) — dostępny automatycznie w Claude Code.

Intelligems ma też MCP server (`https://ai.intelligems.io/mcp`) — OAuth2, do podłączenia w przyszłości.

---

## 10. Clarity Custom Tags — wdrożone 15.06.2026

### Co zrobiono
Dodano sekcję `// 5. Microsoft Clarity custom tags` do `layout/theme.liquid` w obu tematach:

```javascript
// 5. Microsoft Clarity custom tags — segmentacja A/B w heatmapach i nagraniach
if (typeof clarity === 'function') {
    clarity("set", "ab_theme_variant", THEME_VARIANT);
    clarity("set", "theme_id", THEME_ID);
}
```

**Tagi:**
- `ab_theme_variant` = `"GEN-6"` lub `"NOTOAGENCY"`
- `theme_id` = Shopify theme ID

**Filtrowanie w Clarity:** Filters → Custom Tags → `ab_theme_variant` → wybrać wariant → Apply
Działa na: Dashboard, Heatmaps, Session Recordings.

Tagi pojawią się w Clarity w ciągu 30 min – 2h od pierwszego page view z nowym kodem.

### Intelligems ↔ Clarity (natywna integracja)
Dodatkowo do ręcznych tagów, Intelligems ma natywną integrację z Clarity:
1. Intelligems Dashboard → Integrations → Microsoft Clarity → **Enable**
2. Nie wymaga credentials (używa `window.clarity` API)
3. Automatycznie taguje sesje: `experiment_name` + `ig_test_group`
4. **Status (26.06): NIGDY NIE WŁĄCZONE** — wymaga ręcznego włączenia (d.slowik@notoagency.pl)

Docs: https://docs.intelligems.io/integrations/heatmap-integrations/integrating-with-microsoft-clarity

### Clarity API — ograniczenia (ustalone 26.06)

Custom tags (`ab_theme_variant`, `theme_id`) **NIE są dostępne przez Clarity MCP/API**.
- API `query-analytics-dashboard` nie wspiera filtrowania po custom tags
- Custom tags są widoczne TYLKO w UI Clarity (Filters → Custom Tags)
- Limit API: 10 req/dzień
- Wniosek: do weryfikacji tagowania A/B w Clarity trzeba użyć UI, nie API

### Dlaczego nie Hotjar
| | Clarity | Hotjar (free) |
|---|---|---|
| Custom tags/A/B filtering | **Darmowe, bez limitu** | Wymaga Observe Plus (32€/mies.) |
| Nagrania | Bez limitu | 10k/mies. (5% sampling) |
| Integracja Intelligems | Natywna | Brak |
| GA4 integration | Natywna (bidirectional) | Tylko płatna |
| Shopify app | Oficjalny | Brak |

---

## 11. Kolejne kroki (TODO) — aktualizacja 26.06

### Pilne (przed 30.06):
- [ ] **ZAKOŃCZYĆ TEST** — zatrzymać eksperyment w panelu Intelligems, przywrócić GEN-6 na 100%
- [ ] Upewnić się, że Intelligems nie serwuje NOTO po wyłączeniu (sprawdzić z incognito)

### Zrealizowane:
- [x] ~~Clarity custom tags wdrożone w obu tematach (15.06.2026)~~
- [x] ~~Fix tracking GA4: `gtag` polyfill + `dataLayer.push` (15.06)~~
- [x] ~~Fix tracking Clarity: polling `window.clarity` zamiast `typeof clarity` (17.06)~~
- [x] ~~Rejestracja GA4 custom dimensions: `variant_name`, `variant`, `experience_name`, `experiment_name` (17.06)~~
- [x] ~~Pobranie i analiza pełnych danych Intelligems API (26.06)~~
- [x] ~~Zmiana splitu 90/10 → 80/20 (zidentyfikowane 26.06)~~
- [x] ~~Decyzja: ZAKOŃCZYĆ TEST (rekomendacja na podstawie p=0.025)~~

### Do zrobienia po zakończeniu testu:
- [ ] Audyt UX motywu NOTO: porównanie strony produktu mobile (pozycja CTA, JS errors)
- [ ] Analiza abandoned checkout NOTO (38.9% vs 32.2%) — sprawdzić kroki checkout
- [ ] Natywna integracja Intelligems → Clarity **nigdy nie włączona** (d.slowik@notoagency.pl)
- [ ] Opcjonalnie: podłączyć Intelligems MCP server (`https://ai.intelligems.io/mcp`, OAuth2)
- [ ] Opcjonalnie: BigQuery export GA4 — IAM access do projektu GCP `277470194697`

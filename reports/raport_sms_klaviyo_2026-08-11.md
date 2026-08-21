# Raport: kanał SMS w Klaviyo — ostatnie 30 dni

**Okres analizy:** 12.07.2026 – 11.08.2026
**Data raportu:** 11.08.2026
**Konto Klaviyo:** Genactiv sp. z o.o. (`RSst7h`)
**Źródła danych:** Klaviyo API (campaigns, campaign-values-report, segments), GA4 (property `279858535`), Shopify (customer journey / UTM, 462 zamówienia)
**Metryka konwersji:** Placed Order (`R6aTMS`)

---

## 1. Co zostało wysłane

W ostatnich 30 dniach są **2 wysyłki SMS**, ale realna jest tylko jedna.

| Kampania | ID | Wysłano | Audience | Odbiorcy |
|---|---|---|---|---|
| „Wiadomość tekstowa - 28 lip 2026, 12:59" | `01KYM62RPNQ7CTT3W2PD8WKR6Y` | 28.07.2026, 19:59 (Europe/Warsaw) | segment **Fiberbiom** `QZZAZs` (497 profili) | **151** |
| „TEST" | `01KY7312PFYNWDEM3Z219456RA` | 23.07.2026, 12:10 | lista TESTOWA `RcRb62` | 1 |

**Treść wysyłki produkcyjnej:**

> Uzupełnij zapasy blonnika już dzis! Z kodem "LATO" odbierasz 15 % znizki na wszystkie produkty Fiberbiom. Wybierz ulubiony produkt; https://genactiv.pl/collections/blonnik

**Ustawienia renderowania wiadomości:**

| Parametr | Wartość |
|---|---|
| `shorten_links` | **false** |
| `add_org_prefix` | true |
| `add_info_link` | true |
| `add_opt_out_language` | true |
| `tracking_options.add_tracking_params` | true |
| `tracking_options.custom_tracking_params` | **[] (puste)** |

Kampania „TEST" z 23.07 kierowała na inny URL (`/collections/fiberbiom`) niż wysyłka produkcyjna (`/collections/blonnik`) — dalej pomijana w analizie ze względu na 1 odbiorcę.

---

## 2. Wyniki wg Klaviyo

Kampania `01KYM62RPNQ7CTT3W2PD8WKR6Y`, okno `last_30_days`, metryka konwersji Placed Order:

| Metryka | Wartość |
|---|---|
| Odbiorcy | 151 |
| Dostarczone | 149 (98,7%) |
| Failed | 2 (1,3%) |
| Bounced | 0 |
| **Kliknięcia (unique)** | **0 — CTR 0,00%** |
| Konwersje | 2 (unique: 2) |
| Conversion rate | 1,342% |
| Wartość konwersji | **284,95 zł** |
| AOV | 142,48 zł |
| Przychód / odbiorcę | 1,91 zł |
| Wypisy | 0 (0,00%) |
| Zgłoszenia spam | 0 |

Kampania „TEST": 1 odbiorca, 1 dostarczony, 0 kliknięć, 0 konwersji, 0 zł.

---

## 3. UTM i atrybucja — kampania SMS nie ma żadnego taggingu

### 3.1. Konfiguracja (Klaviyo)

`add_tracking_params = true`, ale `custom_tracking_params` jest puste, a w samej wiadomości **`shorten_links = false`**. Bez skracania linków Klaviyo wysyła surowy URL — nie dokleja parametrów UTM i nie mierzy kliknięć. To wyjaśnia CTR = 0% przy jednoczesnych 2 konwersjach.

### 3.2. Weryfikacja w GA4 (12.07–11.08)

Zapytanie: `sessionSource` / `sessionMedium` / `sessionCampaignName`, filtr `sessionSource CONTAINS klaviyo` OR `sessionMedium CONTAINS sms`.

**Wynik: 0 sesji z `medium = sms`.** Wszystkie 13 zwróconych wierszy to `klaviyo / email`:

| Kampania (GA4) | Sesje | Transakcje | Przychód |
|---|---|---|---|
| Zestawy wakacyjne | 133 | 7 | 1 638,65 zł |
| Zestawy_Podbicie | 107 | 9 | 3 334,80 zł |
| Copy of Shopify list welcome | 84 | 14 | 3 691,75 zł |
| Wakacje_Fiberbiom | 49 | 2 | 1 210,25 zł |
| Brzoskwinia_Darmowa Dostawa | 26 | 1 | 99,00 zł |
| Brzoskwinia premiera | 14 | 1 | 395,00 zł |
| Fiberbiom_Nowe smaki_mail2 | 12 | 0 | 0 zł |
| Fiberbiom nowe smaki | 9 | 1 | 55,00 zł |
| Ostatnio oglądany produkt | 4 | 0 | 0 zł |
| ac-mail4-no-free-shipping-shiping-coupon | 4 | 1 | 220,15 zł |
| Wyprzedaż Zooggies | 3 | 0 | 0 zł |
| onboarding_1_welcome_bold | 2 | 0 | 0 zł |
| klaviyo / (not set) | 1 | 0 | 0 zł |

### 3.3. Weryfikacja w Shopify (28.07–4.08)

462 zamówienia przeanalizowane, journey tracking rate 83%, przychód 117 867,02 zł.

`utm_source = klaviyo` → **3 zamówienia, 1 559,60 zł**, wszystkie z kampanii **mailowych**: `Wakacje_Fiberbiom`, `Fiberbiom_Nowe smaki_mail2`, `ac-mail4-no-free-shipping-shiping-coupon`. **Ani jednego zamówienia przypisanego do SMS.**

### 3.4. Analiza godzinowa strony docelowej (28.07)

GA4, landing page `CONTAINS /collections/blonnik`, wymiar `hour` (strefa Europe/Warsaw). SMS wysłany o **19:59**.

| Godzina 28.07 | Ruch direct / (none) | Transakcje |
|---|---|---|
| 14:00 | 1 | 0 |
| 18:00 | 2 | 0 |
| 19:00 | 2 | 1 (152,15 zł) |
| **20:00–23:59** | **0** | **0** |

Po wysyłce nie ma żadnej sesji direct na stronie docelowej. Jedyna transakcja tego dnia na tej stronie (152,15 zł, godz. 19:xx) miała miejsce **przed** wysyłką.

Dzienny rozkład ruchu na `/collections/blonnik` (26–31.07) potwierdza brak piku: direct = 0 / 1 / 6 / 6 / 0 / 1 sesji, przy dominującym `google / cpc` (340 / 495 / 149 / 91 / 45 / 41).

### 3.5. Wniosek z sekcji 3

Transakcyjność i ruch z SMS są **niemierzalne end-to-end**. Dwie konwersje raportowane przez Klaviyo pochodzą z atrybucji opartej na odbiorze wiadomości (bez zarejestrowanego kliknięcia), więc nie da się ich potwierdzić ani w GA4, ani w Shopify.

**Zastrzeżenia metodologiczne:**
- Baner zgód Pandectes (`cookiesBlockedByDefault=7`) blokuje opcjonalne cookies domyślnie, co zaniża GA4 — ale Shopify customer journey ma 83% pokrycia i również nie widzi ruchu z SMS.
- Kod rabatowy `LATO` był współdzielony z kampaniami mailowymi, więc nie nadaje się do rozdzielenia atrybucji między kanałami.

---

## 4. Benchmark: SMS vs e-mail (te same 30 dni)

Kampanie e-mail wysłane w oknie 12.07–11.08 (lista Shopify Newsletter):

| Kampania | Data | Odbiorcy | CTR unique | CR | Przychód | Przychód/odb. | Wypisy |
|---|---|---|---|---|---|---|---|
| Zestawy wakacyjne | 14.07 | 7 908 | 1,29% | 0,155% | 3 396,90 zł | 0,44 zł | 0,19% |
| Zestawy_Podbicie | 21.07 | 7 960 | 1,10% | 0,230% | 6 052,45 zł | 0,77 zł | 0,24% |
| Wakacje_Fiberbiom | 27.07 | 8 012 | 0,47% | 0,139% | 3 387,25 zł | 0,43 zł | 0,37% |
| **E-mail razem** | — | **23 880** | ~0,95% | **0,172%** | **12 836,60 zł** | **0,54 zł** | ~0,27% |
| **SMS** | 28.07 | **151** | 0% (brak trackingu) | **1,342%** | **284,95 zł** | **1,91 zł** | 0,00% |

**Różnica nominalna:** SMS 3,6× wyższy przychód na odbiorcę i 7,8× wyższy CR niż e-mail.

**Dlaczego nie jest to dowód:**
1. **n = 2 konwersje.** Przedział ufności 95% dla CR przy 2/149 to ok. 0,2%–4,8% — statystycznie nierozstrzygalne.
2. **Nierówne populacje.** SMS trafił do ciepłego segmentu klientów Fiberbiom (historia zakupu), e-maile do całej listy newslettera. To porównanie segmentu z listą, nie kanału z kanałem.
3. **Brak weryfikacji zewnętrznej** — przychód SMS opiera się wyłącznie na atrybucji Klaviyo bez potwierdzenia kliknięciem.

---

## 5. Wykorzystanie bazy

| Wskaźnik | Wartość |
|---|---|
| Segment „SMS" (`RHdhyb`) — profile ze zgodą marketingową SMS | **2 289** |
| Odbiorcy jedynej wysyłki produkcyjnej | 151 |
| **Pokrycie bazy w 30 dni** | **6,6%** |
| Segment „Fiberbiom" (`QZZAZs`) — wszystkie profile | 497 |
| Z tego ze zgodą SMS (= odbiorcy) | 151 (30,4%) |

Kanał jest praktycznie nieużywany: jedna wysyłka w miesiącu do 6,6% dostępnej bazy.

---

## 6. Rekomendacje (kolejność wdrożenia)

### P0 — naprawa pomiaru (bez tego reszta jest nieweryfikowalna)

1. **Włącz „Shorten links" w wiadomościach SMS.** Przyczyna źródłowa całego problemu: bez skracania nie ma ani click-trackingu, ani doklejania UTM.
2. **Uzupełnij `custom_tracking_params`**: `utm_source=klaviyo`, `utm_medium=sms`, `utm_campaign={nazwa kampanii}`. Obecnie lista jest pusta, mimo `add_tracking_params = true`.
3. **Nadawaj kampaniom SMS czytelne nazwy.** „Wiadomość tekstowa - 28 lip 2026, 12:59" trafi do `utm_campaign` i będzie nieużyteczne w raportach GA4/Shopify.
4. **Dedykowany kod rabatowy dla SMS** (np. `SMS15` zamiast współdzielonego `LATO`). Jedyna metoda atrybucji niezależna od cookies przy obecnej konfiguracji Pandectes. Uwaga: Shopify pozwala na jeden kod per zamówienie, a UpPromote/Revy potrafią nadpisywać kody — patrz `Known Issues` w root `CLAUDE.md`.

### P1 — koszt i skala

5. **Usuń polskie znaki diakrytyczne z treści.** Obecna wiadomość miesza „Uzupełnij / już" (ł, ż) z resztą tekstu pisaną bez ogonków. Jeden znak spoza GSM-7 przełącza całego SMS-a na UCS-2 (67 znaków na segment zamiast 153). Przy tej długości treści + prefiks organizacji + link informacyjny + formuła opt-out oznacza to ok. 2× wyższy koszt wysyłki. *Faktycznej liczby segmentów i kosztu nie widać przez API — do potwierdzenia w billingu Klaviyo.*
6. **Skaluj wysyłkę na pełną bazę 2 289 profili**, ale dopiero po wdrożeniu punktów 1–4 — inaczej ponownie nie będzie czego zmierzyć.

### P2 — pomiar efektu

7. **Powtórz analizę po pierwszej wysyłce z poprawnym taggingiem.** Dopiero wtedy powstanie podstawa do oceny jakości kanału: CTR, ruch w GA4 z `medium=sms`, transakcje w Shopify po `utm_source=klaviyo` + `utm_medium=sms`.
8. **Ustal minimalną wielkość próby przed testem.** Przy oczekiwanym CR rzędu 1% i chęci wykrycia różnicy vs e-mail potrzeba wysyłek rzędu 1 000+ odbiorców, nie 151.

---

## 7. Ocena kanału

Kanał SMS w GenActiv jest dziś **technicznie nieopomiarowany i praktycznie nieużywany**: jedna realna wysyłka do 6,6% bazy w ciągu 30 dni, zero zarejestrowanych kliknięć, zero ruchu widocznego w GA4 i Shopify. Wskaźniki raportowane przez Klaviyo (1,91 zł/odbiorcę, CR 1,34%) sugerują potencjał, ale przy 2 konwersjach nie stanowią podstawy do żadnego wniosku o jakości kanału. Priorytetem nie jest optymalizacja treści, tylko **przywrócenie mierzalności**.

---

## Załącznik: zapytania użyte w analizie

| Źródło | Zapytanie |
|---|---|
| Klaviyo | `get_campaigns(channel=sms, created_at >= 2026-06-01)` |
| Klaviyo | `get_campaign_report(send_channel=sms, timeframe=last_30_days, conversion_metric_id=R6aTMS)` |
| Klaviyo | `get_campaign_report(send_channel=email, timeframe=last_30_days, conversion_metric_id=R6aTMS)` |
| Klaviyo | `get_segment(RHdhyb / QZZAZs, include_profile_count=true)` |
| GA4 | `run_report(279858535, 2026-07-12..2026-08-11, dim: sessionSource/sessionMedium/sessionCampaignName, filter: source~klaviyo OR medium~sms)` |
| GA4 | `run_report(279858535, 2026-07-26..2026-07-31, dim: date/sessionSourceMedium, filter: landingPage~/collections/blonnik)` |
| GA4 | `run_report(279858535, 2026-07-28..2026-07-29, dim: date/hour/sessionSourceMedium/deviceCategory, filter: landingPage~/collections/blonnik)` |
| Shopify | `get-traffic-source-analytics(2026-07-28..2026-08-04, financialStatus=any, limit=500)` |

# Audyt konta Google Ads — Genactiv

**Konto:** Genactiv (ID 339-338-2047 / 3393382047) · waluta PLN
**Okres analizy:** 1 maja – 18 czerwca 2026
**Data audytu:** 18 czerwca 2026

---

## 0. TL;DR (jednym akapitem)

Konto **przepala budżet na obronę marki** (popyt, który masz za darmo z organiku) i jednocześnie **w ogóle nie wykorzystuje swojego najcenniejszego aktywu — 10 000+ lojalnych, powtarzalnych klientów**. Raportowany blended ROAS 15,7× jest zawyżony (Google nadpisuje sprzedaż ~50–67% względem Shopify). Najlepsza dźwignia: **mniej obrony brandu → więcej akwizycji NONBRAND + retencja przez Customer Match.**

---

## 1. Wyniki ogólne (maj–18 czerwca)

| Metryka | Wartość |
|---|---|
| Wydatki | **13 075 zł** |
| Wartość konwersji (raport Google) | **204 968 zł** |
| Konwersje | 780 |
| Kliknięcia / wyświetlenia | 11 274 / 204 881 |
| CTR / śr. CPC | 5,5% / 1,16 zł |
| Blended ROAS (zawyżony) | 15,7× |

### Rozbicie na kampanie

| Kampania | Wydatki | Udział | ROAS | CPA |
|---|---|---|---|---|
| PMax NONBRAND (Colostrum+Fiberbiom) | 7 864 zł | 60% | 6,9× | 35,2 |
| Search Brand (Manual CPC) | 4 005 zł | 31% | 23,0× | 13,1 |
| PMax Brand | 1 046 zł | 8% | 54,5× | 4,3 |
| PLA Brand (wstrzymana) | 159 zł | 1% | 9,5× | — |

### Trend maj → czerwiec (czerwiec = 18 dni)

| Kampania | Maj ROAS | Czerwiec ROAS | Uwaga |
|---|---|---|---|
| PMax NONBRAND | 7,75× | 5,83× | CPA 31,9 → 40,7 (+28%); spadł poniżej celu tROAS=7 |
| Search Brand | 32,6× | 18,9× | wydatki ~4× w górę, ROAS o połowę w dół |
| PMax Brand | 71,3× | 14,0× | konwersje 222 → 20 (kanibalizacja) |

---

## 2. Pięć kluczowych problemów

### 🔴 1. Przepalanie na brandzie (największy problem)
W czerwcu przerzucono popyt brandowy z taniego **PMax Brand** (CPA 4,3 / ROAS 54×) na **Search Brand Manual CPC** (CPA 13 / ROAS 19×) i wykręcono jego budżet ~4×.
**Efekt:** te same ~330 konw./mc, ale koszt obrony marki wzrósł **2,7× (1 940 → ~5 185 zł/mc)** — ok. **3 200 zł/mc wyrzucone bez przyrostu sprzedaży.**

### 🔴 2. PMax Brand „padł" = kanibalizacja, nie awaria
Dane dzienne: koszt rośnie, konwersje → 0. Search Brand odebrał mu zapytania brandowe (Google daje pierwszeństwo kampaniom Search nad PMax). To nie usterka — to skutek pkt 1.

### 🟠 3. Google Ads zawyża sprzedaż o ~48–67% vs Shopify
- Google raportuje: **204 968 zł** wartości.
- Shopify przypisuje źródłu „google": max **~138 tys.**, a jednoznacznie otagowanym płatnym kampaniom **~43 tys.**
- **Search Brand (92 tys. zł w Google!) nie ma śladu w Shopify** → to popyt, który konwertuje organicznie. Google organic samo dało 89 tys. zł / 344 zam.
- Wniosek: realny ROAS jest znacznie niższy niż 15,7×; „zasługa" brandu jest w dużej części fikcyjna.

### 🟠 4. UTM-y skopane (auto-tagging OK)
- Auto-tagging / GCLID = **włączony** (to działa).
- Ale ręczne szablony używają **niezdefiniowanych parametrów niestandardowych** `{_campaignname}` / `{_adgroupname}`:
  - Search Brand taguje się **pusto** → niewidoczny w Shopify,
  - oba PMax zlewają się w jeden worek „pmax_genactiv" → nie da się rozróżnić brand/nonbrand.
- **Fix:** statyczny `utm_campaign` per kampania w `final_url_suffix`, usunąć stary `tracking_url_template`.

### 🔴 5. Najcenniejsze aktywo niewykorzystane: 10 000+ klientów
- Baza klientów Shopify: **10 000+** (od 2021), silna powtórkowość (**5–12 zamówień/osoba**), cykl ~**30–60 dni**, AOV ~235–260 zł.
- W Google Ads jako dane 1st-party (Customer Match): **~200 (≈2%).**
- Remarketing faktycznie **nie działa** (jedyna kampania = 0 wydatków od kwietnia; w Q1 ROAS 1,4×).
- Listy remarketingowe za małe wobec ruchu → luki w tagu / zgodach / oknach członkostwa.

---

## 3. Plan Customer Match (główny lewar wzrostu)

Punkt wyjścia: 10 000+ klientów, cykl 30–60 dni, dziś w CM ~200. Budowa przez MCP Klaviyo-segments (segmenty dynamiczne, auto-odświeżanie).

### Segmenty do zbudowania (Klaviyo → Customer Match)

| # | Segment | Definicja | Zastosowanie |
|---|---|---|---|
| 1 | All buyers | ≥1 zakup | seed lookalike + baza wykluczeń |
| 2 | Recent buyers | 0–30 dni | **WYKLUCZAĆ** z akwizycji |
| 3 | Replenishment | 30–75 dni | kampania „dokup" (pod cykl) |
| 4 | Lapsed / win-back | 90–365 dni | reaktywacja z ofertą |
| 5 | VIP | ≥3 zam. / wysoki LTV | wyższe stawki, lojalność |
| 6 | One-timers | 1 zakup, >60 dni | konwersja na powtórkę |

Higiena: wyklucz `test@`, `*@brandactive.pl`, `*@genactiv.eu`. Spodziewany match rate ~50–70% → z 10k realnie ~5–7k dopasowanych (25–35× więcej niż dziś).

### Gdzie użyć
- **Search RLSA** (najszybszy zwrot, zero kanibalizacji): listy w obserwacji na NONBRAND → bid-up VIP/Replenishment +30–50%, Lapsed +15–20%.
- **Dedykowana kampania retencyjna** (Demand Gen / Display, CM-targeted): replenishment (niski tROAS) + win-back z kodem. Budżet startowy mały (30–50 zł/dz) — efektywność, nie skala.
- **PMax:** wyklucz „Recent buyers" z NONBRAND (przestań płacić za reaktywację), podaj „All buyers/VIP" jako audience signal, zrób **lookalike z VIP** (zastąp martwy legacy „podobni 1,1 mln").

### Fundament techniczny (warunek skuteczności)
- Enhanced Conversions (web) ON,
- okna członkostwa: purchasers **540 dni**,
- potwierdzić sync Klaviyo→Google i eksport audytoriów GA4↔Ads.

---

## 4. Roadmapa wdrożenia (kolejność)

| Prio | Akcja | Oczekiwany efekt |
|---|---|---|
| 1 🔴 | Auction insights brandu + **test pauzy Search Brand** 7–14 dni (obserwacja organiku w Shopify) | twarda inkrementalność przed cięciami |
| 2 🔴 | Po teście: budżet Search Brand 160 → ~60 zł/dz; brand wraca do taniego PMax Brand | −~3 tys. zł/mc |
| 3 🟠 | Naprawa UTM-ów (statyczne utm_campaign w final_url_suffix, usunąć stary template) | mierzalność w Shopify |
| 4 🟠 | NONBRAND: wykluczenia marki, tROAS 7 → ~6, obciąć Display/Discover, potem ↑ budżet | odblokowana akwizycja |
| 5 🔴 | Customer Match wg planu (200 → 5–7k) + retencja/replenishment + lookalike | nowy lewar wzrostu |
| 6 🟡 | Fundament: Enhanced Conversions, okna 540 dni, sync GA4/Klaviyo, czyszczenie list | warunek skuteczności |

---

## 5. Gotchas narzędziowe (do pamięci)

- `shopify_customer_count` zwraca 10000 (limit) **niezależnie od filtra** — bezużyteczny do repeat-rate; użyć Klaviyo.
- `get-customer-orders` zwraca pusto dla starszych klientów.
- `gads_change_history` (MCP) wywala błąd 400.
- Sortowanie `shopify_list_customers` po ORDERS_COUNT pada (pole `ordersCount` nieobecne w tej wersji API).
- W bazie Shopify są konta testowe/wewnętrzne z zawyżonymi zamówieniami (test@test.pl=59, *@brandactive.pl, *@genactiv.eu) — wykluczać przed CM.

---

*Audyt wykonany na danych z Google Ads API + Shopify (maj–czerwiec 2026). Liczby ze sprzedaży Shopify analizowane na próbce 2000 zamówień (limit narzędzia) — proporcje i kierunek wniosków pewne, wartości bezwzględne mogą być wyższe.*

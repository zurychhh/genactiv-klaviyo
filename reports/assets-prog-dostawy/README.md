# Próg darmowej dostawy — analiza, decyzja, wdrożenie

Katalog zawiera komplet artefaktów dla tematu „wysokość progu darmowej dostawy"
(sierpień 2026): analizę ekonomiczną, kod produkcyjny, backupy i skrypt wdrożeniowy.

---

## Stan na 31.08.2026

| # | Element | Gdzie jest | Co dalej |
|---|---|---|---|
| 1 | Decyzja: próg zostaje 300 zł | Zamknięte, udokumentowane | — |
| 2 | Pasek postępu `genactiv-free-shipping.liquid` | **PRODUKCJA** (motyw 199333609804) od 27.08 | Działa, nic nie czeka |
| 3 | Rekomendacje `genactiv-cart-boost.liquid` | Kopia motywu **204468388172**, przetestowane | **Czeka na zgodę na wdrożenie** |
| 4 | Reguły doboru: pula `bestsellery` + zestaw pierwszy | Wdrożone na kopii 31.08, zatwierdzone przez klienta | Wchodzi razem z pkt 3 |
| 5 | Pomiar efektu / test A/B | Rozpoznane, **decyzja nie podjęta** | Klient wybiera wariant — patrz sekcja 6 |
| 6 | Materiał dla klienta (deck przed/po) | Nieaktualny — stare zrzuty | Do odświeżenia przed pokazaniem |

**Blokada jest jedna:** brak zgody na wypchnięcie rekomendacji na produkcję
plus nierozstrzygnięty sposób pomiaru (sekcja 6). Reszta jest zrobiona.

Produkcja nietknięta od 27.08. Podgląd rekomendacji:
`https://genactiv.pl/?preview_theme_id=204468388172` (dodaj coś do koszyka).

---

## 1. Decyzja biznesowa

**Progu NIE obniżamy z 300 na 250 PLN.** Zamiast tego naprawiamy komunikat
i dokładamy cross-sell przy progu 300.

Pełna analiza: [`../analiza-prog-dostawy-250-2026-08-24.html`](../analiza-prog-dostawy-250-2026-08-24.html)
Materiał dla klienta: [`../prog-dostawy-przed-po-2026-08-26.html`](../prog-dostawy-przed-po-2026-08-26.html)

Trzy ustalenia, które przesądziły:

| Ustalenie | Liczba |
|---|---|
| Break-even obniżki przy marży 25% / 20% | 75% / 163% upliftu — nieosiągalne |
| Kanibalizacja: zamówienia 250–300 PLN, które dostałyby dostawę gratis bez zmiany zachowania | 268 (15,3% segmentu powracających) / 61 dni |
| Alternatywa (cross-sell przy 300) przy uplifcie 20% i marży 25% | **+2 185 PLN** vs **−2 291 PLN** dla obniżki |

**Dlaczego 300 to dobry próg:** leży w luce między „jeden drogi produkt"
(299 i 340 zł po rabacie = 254–289 zł) a „dwie sztuki hero" (179+179 = 304–358 zł).
Działa więc jako próg *„kup drugą sztukę"*. Zejście do 250 przeniosłoby go poniżej
strefy zakupu jednoproduktowego — 232 z 485 zamówień w paśmie 250–300 to zakupy
jednej sztuki premium, czyli czysty prezent.

**Hipoteza „250 da koszyki 400" — obalona.** Pozorny pik tuż nad progiem
(139 zamówień w paśmie 300–310) to w 100 przypadkach `179+179` z kodem rabatowym
15% = 304,30 zł. Wszystkie miały kod. To arytmetyka cennika, nie zachowanie klienta —
nie ma dowodu, że próg w ogóle napędza budowanie koszyka.

## 2. Co jest wdrożone

| Element | Plik | Status |
|---|---|---|
| Pasek postępu do darmowej dostawy | `genactiv-free-shipping.liquid` | **PRODUKCJA** od 27.08.2026 |
| Rekomendacje dopasowane do brakującej kwoty | `genactiv-cart-boost.liquid` | Gotowe, przetestowane na kopii — **czeka na zgodę** |

Motyw produkcyjny: **199333609804** (GEN-6 fix payment icons 2026-05-20)
Motyw testowy: **204468388172** (SNAPSHOT + pasek dostawy 2026-08-27)

### 2.1 Pasek postępu

Naprawia komunikat, który przed zmianą wyświetlał się jako `300   141 zl PLN` —
szarym drobnym drukiem, pod przyciskiem Google Pay, poniżej linii załamania.

Przyczyny błędu: `free_shipping_title` w ustawieniach motywu zawierał liczbę `"300"`
zamiast etykiety tekstowej, a JS motywu sklejał wartość z walutą podwójnie.

Po zmianie: `Do darmowej dostawy brakuje Ci 141 zł` + wizualny pasek, pod nagłówkiem
„Twój koszyk", **nad listą produktów**.

### 2.2 Rekomendacje dopasowane do luki

Pokazuje **wyłącznie produkty w cenie ≥ brakującej kwoty**, więc obietnica
„dodaj i masz dostawę gratis" jest zawsze prawdziwa. Przycisk „Dodaj" (AJAX +
przeładowanie koszyka).

**Reguły doboru** (kolejność stosowania):

1. **Pula:** kolekcja `bestsellery` (`genactiv.pl/collections/bestsellery`), 23 produkty.
2. **Filtr:** cena ≥ brakującej kwoty · wariant dostępny · produkt nie jest już
   w koszyku · `product_type` nie zawiera „Karma uzupełniająca" ani „Książki".
3. **Kolejność:** najtańszy pasujący **zestaw wielosztukowy** ląduje na pierwszym
   miejscu; pozostałe sloty wypełniają najtańsze pasujące pozycje (rosnąco).
4. **Liczba kart:** 3 na stronie koszyka, 2 w koszyku bocznym.

Zestaw rozpoznajemy **dwutorowo**:

- `ga_multipack_words` — słowa w tytule: `dwupak, trójpak, trojpak, trzypak,
  czteropak, zestaw, pakiet`. Łapie 6 dwupaków (169 / 245 / 269 / 289 / 340 / 340 zł).
- `ga_multipack_handles` — jawna lista uchwytów dla zestawów, które nie mówią tego
  w tytule. Dziś jedna pozycja: `colostrum-od-juniora-do-seniora-zawiesina`
  (275 zł, komplet dwóch **różnych** zawiesin). Dopisywana ręcznie.

Razem: 7 z 23 produktów oflagowanych jako zestaw.

Świadomie **nie** używamy heurystyki „tytuł zawiera +" — złapałaby
`FIBERBIOM - Błonnik + Colostrum`, który jest jednym produktem. Stąd lista uchwytów.

Pierwszeństwo dostaje **jeden** zestaw, nie wszystkie — reszta slotów zostaje
na tanie pozycje. Przy luce 26 zł daje to `169 zł (dwupak) → 89 zł`, więc obok
droższego zestawu klient widzi też tanie domknięcie progu.

**Kto realnie prowadzi.** Reguła wybiera *najtańszy pasujący* zestaw, a najtańszy
produkt w sklepie kosztuje 85 zł — więc luka nigdy nie przekracza 215 zł. W praktyce
pierwszą kartę zajmuje tylko dwupak 169 zł (luka ≤ 169) albo 245 zł (luka 170–215).
Zestawy 269 / 275 / 289 / 340 zł są oflagowane, ale nigdy nie wejdą na pierwsze
miejsce — pokazują się jako zwykłe karty. Żeby konkretny zestaw prowadził niezależnie
od ceny, trzeba go przypiąć osobno (dziś kod tego nie robi).

Kuratorowanie puli: klient zmienia zawartość kolekcji w Shopify, bez dotykania kodu.
Zmiana samej kolekcji → stała `ga_boost_pool` na górze snippetu.

Moduł ukrywa się sam, gdy próg jest osiągnięty lub gdy żaden produkt nie domyka luki.

**Dwa warianty rozmieszczenia:**

| Miejsce | Wywołanie | Układ |
|---|---|---|
| Strona koszyka — pod paskiem postępu, nad listą produktów | `{% include 'genactiv-cart-boost' %}` | 3 karty w rzędzie, stack < 750 px |
| Koszyk boczny — pod „Z wliczonym podatkiem…", **nad** szarym blokiem płatności | `{% include 'genactiv-cart-boost', compact: true %}` | 2 karty, zawsze jedna kolumna |

Wariant `compact` istnieje, bo drawer jest wąski (~390 px) niezależnie od szerokości
okna — media query na viewport by tu nie zadziałał, więc jedna kolumna wymuszona klasą.

Gdy obie instancje są na stronie (koszyk + drawer), każda czyta blok źródłowy
z własnej sekcji (`root.closest('form, .cart-drawer, [data-section-id]')`),
z fallbackiem na pierwszy w dokumencie.

## 3. Decyzje techniczne i dlaczego takie

**Nie dotykamy skompilowanego `assets/theme-dist.js`.** Oryginalny blok
`.cart__free-shipping` zostaje w DOM (ukryty przez CSS) i nadal jest przeliczany
przez funkcję motywu `_initFreeShipping()`. Nasze komponenty czytają z niego wartość
przez `MutationObserver`. Dzięki temu przeliczanie przy zmianie koszyka działa bez
ingerencji w logikę motywu.

**Nie dotykamy `config/settings_data.json`.** To jedyny plik motywu realnie edytowany
równolegle w panelu Dostosuj (27.08 o 09:41 ktoś w nim zapisywał). Snippet sam wykrywa,
że `free_shipping_title` zawiera liczbę zamiast etykiety, i podstawia poprawny tekst —
funkcja `sane()`. Jeśli ktoś kiedyś wpisze tam sensowną etykietę, snippet użyje jej.

**Nie publikujemy kopii motywu, tylko łatamy żywy w miejscu.** Publikacja kopii
skasowałaby cudze zmiany zrobione po duplikacji i zmieniłaby theme ID (rozjazd
w tagowaniu `theme_id` w Clarity). Pliki sekcji, które modyfikujemy, były nietknięte
od 20.05.2026 — zerowy konflikt.

**Bez emoji.** Ikony to inline SVG (paczka / checkmark), stroke 1,6 px, `currentColor`,
zero zależności zewnętrznych.

## 4. Wyniki testów

| Test | Wynik | Data |
|---|---|---|
| Renderowanie na stronie koszyka | OK | 27.08 |
| Renderowanie w koszyku bocznym (drawer) | OK | 27.08 |
| Przeliczanie dynamiczne (AJAX motywu, 159 → 318 zł) | OK — przeskok na stan „done" | 27.08 |
| Pozycja nad listą produktów (kolejność DOM) | OK | 27.08 |
| Wdrożenie na produkcję + weryfikacja bez parametru podglądu | OK | 27.08 |
| **Widok mobilny** | **OK** — zweryfikowane przez klienta | 30.08 |
| **Współpraca z Revy Upsell** | **OK** — bez konfliktu | 30.08 |
| Rekomendacje: dobór wg luki (141 zł → 159/161/169 zł) | OK | 30.08 |
| Rekomendacje: „Dodaj" → koszyk 318 zł → moduł chowa się sam | OK | 30.08 |
| Rekomendacje w koszyku bocznym — pozycja między tekstem o podatku a blokiem płatności | OK (potwierdzone kolejnością w DOM) | 30.08 |
| Rekomendacje w drawerze: luka 131 zł → 2 karty po 135 zł, jedna kolumna | OK | 30.08 |
| Rekomendacje w drawerze: „Dodaj" → koszyk 169 → 304 zł → pasek „Masz darmową dostawę!", moduł znika | OK | 30.08 |
| Podmiana puli na kolekcję `bestsellery` — 23 produkty w `POOL`, wszystkie z obrazkiem | OK | 31.08 |
| Rozpoznanie zestawów: 6 dwupaków oflagowanych, 17 pojedynczych nie — zero fałszywych trafień | OK | 31.08 |
| Kolejność, koszyk, luka 141 zł → `169 dwupak / 169 / 175` (159 zł pominięte — jest w koszyku) | OK | 31.08 |
| Kolejność, drawer, luka 26 zł → `169 dwupak / 89` | OK | 31.08 |
| Zestaw po uchwycie (`…od-juniora-do-seniora…`, 275 zł) oflagowany, `FIBERBIOM - Błonnik + Colostrum` nadal nie | OK — 7/23 | 31.08 |

Znany błąd, naprawiony 30.08: w `genactiv-cart-boost.liquid` był `{% for bad in
ga_excluded_types split: ',' %}` (brak pipe'a) — snippet cicho się nie renderował.
Poprawnie: `{% assign ... | split: ',' %}` i `{% for bad in ga_excluded_types %}`.

## 5. Wdrożenie i rollback

```bash
# dry-run (domyslnie)
python3 reports/assets-prog-dostawy/deploy.py <THEME_ID>

# zapis
python3 reports/assets-prog-dostawy/deploy.py <THEME_ID> --live

# rollback — przywraca 2 pliki sekcji z backupu
python3 reports/assets-prog-dostawy/deploy.py <THEME_ID> --rollback --live
```

Skrypt jest idempotentny (pomija include, jeśli już jest) i przerywa pracę, gdy
kotwica w pliku nie wystąpi dokładnie raz.

**Przed każdym wdrożeniem na produkcję** sprawdź, czy pliki są nadal zgodne
z backupem — inaczej nadpiszesz cudze zmiany:

```bash
# porownanie live vs backup-live-2026-08-27/
python3 -c "..."   # patrz: pre-flight w historii wdrozenia
```

Backup: `backup-live-2026-08-27/` — bajt w bajt kopie `cart-template.liquid`,
`cart-drawer.liquid`, `settings_data.json` + `MANIFEST.json` z checksumami.

## 6. Pomiar efektu i test A/B — co jest możliwe (rozpoznanie 31.08.2026)

Klient zapytał, czy da się natywnie w Shopify odpalić na jednym motywie test A/B
z 10% grupą kontrolną. Odpowiedź: **nie ma takiego mechanizmu**, a 10% i tak by
niczego nie zmierzyło.

### 6.1 Shopify nie ma natywnego A/B — zweryfikowane

Introspekcja schematu Admin API `2025-01` na naszym sklepie:

- typy / query / mutacje zawierające `experiment`, `abtest`, `split`, `bucket`,
  `personaliz` — **zero trafień**
- wszystko wokół motywów: `themeCreate`, `themeDuplicate`, `themeFilesUpsert`,
  `themeFilesCopy`, `themeFilesDelete`, `themePublish`, `themeUpdate`, `themeDelete`
  — czyli CRUD i publikacja, żadnego dzielenia ruchu
- typ `Audience`, który wyszedł w wyszukiwaniu, to `"The intended audience for the
  order status page"` — bez związku

Jeden opublikowany motyw = jedno doświadczenie dla wszystkich.

### 6.2 Intelligems jest zainstalowany, ale nie sterujemy nim z kodu

Na storefroncie ładuje się app embed `shopify://apps/intelligems-a-b-testing/blocks/
intelligems-script/…` → `cdn.intelligems.io/esm/0cce6fbe4549/bundle.js`.
To narzędzie, którym szedł test GEN-6 vs NOTOAGENCY.

**Konfiguracja tylko ręcznie w panelu Intelligems.** Wszystkie endpointy API
(`/experiments`, `/tests`, `/campaigns`, `/config`, `/me`, `/shop`) zwracają `404`
na kluczu `ig_live_…` przy `api.intelligems.io/v25-10-beta`.

Brakuje też scope'ów do rozpoznania apek z naszego tokenu: `read_pixels`
(webPixel → ACCESS_DENIED) i `read_script_tags` (403, „requires merchant approval").

### 6.3 Zrobienie tego samodzielnie — wykonalne i prostsze

Obie zmiany to snippety. Grupa kontrolna = nie renderujemy ich i odsłaniamy
oryginalny blok motywu (`.cart__free-shipping` i tak zostaje w DOM, tylko ukryty
CSS-em). Deterministyczny bucket z first-party cookie, ~15 linii.

Motyw ma już gotowe tagowanie z czerwcowego testu — blok „A/B Test Theme Identifier"
w `layout/theme.liquid` (dodany 2026-06-12) pcha `ab_theme_variant` do dataLayer,
GA4 user property i Clarity. Do tego dopinamy `ab_cart_variant`.

Zaleta wobec duplikowania motywu: `theme_id` się nie rozjeżdża, żadnej nowej
zależności, rollback = usunięcie gate'a.

### 6.4 Dlaczego 10% kontroli nic nie da — liczby

GA4, 30 dni do 30.08.2026:

| Zdarzenie | Sesje |
|---|---|
| `session_start` | 58 421 |
| `add_to_cart` | 3 325 |
| `view_cart` | 2 953 |
| `begin_checkout` | 3 626 |
| `purchase` | 1 183 |

Populacja testu to sesje docierające do koszyka: **98/dzień**. Przy 10% kontrola
dostaje **10 sesji dziennie** i to ona jest wąskim gardłem, nie ruch całkowity.

Czas do rozstrzygnięcia (istotność 95%, moc 80%, baseline koszyk→zakup 40,1%):

| Wykrywany efekt | 50/50 | 90/10 | n kontroli przy 90/10 |
|---|---|---|---|
| +3% | 533 dni | 1 480 dni | 14 566 |
| +5% | 192 dni | 534 dni | 5 258 |
| +10% | 48 dni | 134 dni | 1 322 |
| +15% | 22 dni | 60 dni | 590 |
| +20% | 12 dni | 34 dni | 333 |

Margines błędu przy 50/50 — czyli co realnie zobaczymy w raporcie:

| Czas | n na grupę | Margines błędu | Wykryjesz od |
|---|---|---|---|
| 3 tygodnie | ~1 000 | ±4,2 pp | +10% |
| 6 tygodni | ~2 100 | ±3,0 pp | +7,5% |
| 12 tygodni | ~4 100 | ±2,1 pp | +5% |

Realny efekt paska postępu z rekomendacjami to kilka procent, nie kilkanaście.
Najbardziej prawdopodobny wynik testu przy tym ruchu to **„nie wiemy"**.

**Zastrzeżenie do baseline.** 40,1% to proxy: sesje z `purchase` ÷ sesje
z `view_cart`. Część zakupów idzie przez koszyk boczny bez zdarzenia `view_cart`,
więc prawdziwy współczynnik jest niższy — a to wydłuża wszystkie terminy powyżej.

### 6.5 Rekomendacja

Dwie zmiany mają różny status i nie powinny iść w jednym teście:

- **Pasek postępu to naprawa błędu**, nie hipoteza. Komunikat `300  141 zl PLN`
  był zepsuty. Trzymanie połowy klientów na zepsutej wersji przez 6 tygodni nie
  ma sensu. Zostaje dla wszystkich.
- **Rekomendacje to hipoteza biznesowa** i tylko one nadają się na test.

Proponowany wariant: **50/50 na samych rekomendacjach** (obie grupy mają naprawiony
pasek), metryka: **średnia wartość koszyka i udział zamówień ≥300 zł** zamiast
samego współczynnika konwersji — bo na to moduł działa wprost i reaguje czulej.

Alternatywa, jeśli klient nie chce czekać: wdrożenie dla wszystkich i obserwacja
udziału zamówień ≥300 zł miesiąc do miesiąca. Nie jest to dowód przyczynowy,
ale jest od razu i nikt nie ogląda gorszej wersji.

**Decyzja klienta jeszcze nie zapadła.**

## 7. Otwarte

- **Marża: 25% czy 76%?** Klient podał 25%, brief Performance Marketing mówi
  „Suplementy ~76% brutto" i `COGS = 24% AOV`. Liczby 25% i 24% są podejrzanie bliskie —
  możliwa zamiana marży z COGS-em. Przy 76% obniżka progu wychodzi na plus
  (break-even 11,6%), choć cross-sell przy 300 i tak bije ją ~5×. Nie rozstrzygnięte.
- **Materiał dla klienta ma nieaktualne zrzuty** — z emoji i starą pozycją modułu,
  sprzed przeniesienia nad listę produktów.
- **Zachowanie „Dodaj" w koszyku bocznym.** Po dodaniu produktu przenosimy użytkownika
  na `/cart` (pełne przeładowanie), zamiast odświeżać panel w miejscu. Świadomy
  kompromis: motyw ma własną logikę koszyka, a wchodzenie w nią to ryzyko konfliktu.
  Działa poprawnie, ale to zmiana kontekstu — do dopracowania, jeśli klient zgłosi.
- **Zestaw na pierwszym miejscu vs siła oferty.** Reguła klienta (31.08) wypycha
  dwupak przed tanie pozycje — przy luce 26 zł pierwsza karta to 169 zł. To celowa
  gra o AOV, ale osłabia obietnicę „dorzuć drobiazg". Kompromis w kodzie: tylko
  **jeden** slot idzie do zestawu, reszta zostaje na najtańsze. Do zweryfikowania
  na danych, czy klikalność pierwszej karty nie spada.
- **Sposób pomiaru — decyzja otwarta.** Test 50/50 na rekomendacjach czy wdrożenie
  dla wszystkich plus obserwacja miesiąc do miesiąca? Analiza w sekcji 6, wybór
  po stronie klienta. Punkty odniesienia sprzed zmiany: udział zamówień ≥300 PLN
  = 26,1% całej bazy / 35,1% wśród powracających; items/order 1,29 przy płatnej
  dostawie vs 2,41 przy darmowej.

## 8. Ograniczenia danych

- **Okno 60 dni, nie 12 miesięcy.** Shopify Admin API bez scope `read_all_orders`
  cicho ucina wyniki. Faktyczny zakres analizy: 25.06–24.08.2026, 3 618 zamówień.
  To pełne off-season — pasmo 250–300 PLN w sezonie odpornościowym może być grubsze.
- **Uplift jest założeniem, nie pomiarem.** Wyniki podane jako siatka 10/20/30%
  z jawnym break-evenem, nie jako jedna liczba.
- **Nieujęty efekt na konwersji** — porzucenia koszyka na widok opłaty za dostawę
  nie widać w danych o zamówieniach. Działa na korzyść obniżki progu, niepoliczone.
- **Faktura DHL to jeden tydzień** (208 przesyłek, 08–14.08.2026). Średnia ważona
  krajowa ≤3 kg = 11,42 PLN netto, + opakowanie ≈ 15 PLN — zgodne z briefem.

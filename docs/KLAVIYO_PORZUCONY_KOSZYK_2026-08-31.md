# Porzucony koszyk w Klaviyo — sekcja wizualizacji i naprawa flow

**Data:** 2026-08-31
**Zakres:** szablon `XnCJxJ` („Koszyk mail 1 — WHY"), trzy flow koszykowe, 12 szablonów
**Status:** sekcja gotowa i opublikowana (`WL2W37`); naprawa 12 szablonów gotowa
(`[NAPRAWIONY 2026-08-31] …`). **Wszystko czeka na ręczne podpięcie w edytorze
Klaviyo — API nie zapisze szablonu w flow.**

Dokumentacja techniczna snippetu: `templates/snippets/README-koszyk.md`

---

## 1. Cel

Dodać do maila koszykowego wizualizację porzuconej oferty — kartę produktu
z miniaturą, nazwą, wariantem, ceną i przyciskiem powrotu — wstawioną pomiędzy
istniejącą grafikę z CTA „Dokończ zamówienie" a grafikę „↓70%".

Kod personalizacji miał pochodzić z szablonu referencyjnego `Y2rJvV`
(„porzucony-koszyk-mail1-18.11 - FINAL").

## 2. Stan zastany

`XnCJxJ` to szablon drag&drop złożony **wyłącznie z siedmiu grafik** plus ikon
social i stopki. Zero tekstu HTML, zero bloków przyciskowych.

Cztery rzeczy, które wywracały go jako mail koszykowy:

1. **Żaden obrazek nie miał linku** — wszystkie `href: null`. Jedyne klikalne
   elementy to Instagram, Facebook, YouTube, TikTok i unsubscribe. Mail
   o porzuconym koszyku nie miał ani jednej drogi powrotu do sklepu.
2. **Żaden obrazek nie miał `alt`** — przy zablokowanych grafikach odbiorca
   widział pustą białą kolumnę i stopkę po angielsku.
3. **Zero dynamiki koszyka** — statyczna grafika identyczna dla każdego odbiorcy.
4. **Stopka po angielsku** — „No longer want to receive these emails?"
   z gołym `{% unsubscribe %}` bez polskiej etykiety.

## 3. Ustalenia na danych produkcyjnych

### 3.1 Trigger to Added to Cart, nie Checkout Started

Pierwotnie analizowałem flow pod kątem Checkout Started — **błędnie**. Klient
wskazał zrzut z wyzwalacza: metryka **Added to Cart** (Shopify, `WcWiXd`),
jeden produkt na zdarzenie.

To zmieniło całą warstwę zmiennych.

### 3.2 Pola metryki Added to Cart — 150 realnych zdarzeń

| Zmienna | Wypełnienie | Uwagi |
|---------|-------------|-------|
| `event.ImageURL` | 100% | `cdn.shopify.com` |
| `event\|lookup:'Product Name'` | 100% | nazwa z karty produktowej Shopify |
| `event\|lookup:'Variant Name'` | **99%** | forma i wielkość opakowania |
| `event.Price` | 100% | float → wymaga `\|floatformat:0` |
| `event.CompareAtPrice` | **17%** | promocja to przypadek rzadki, nie domyślny |
| `event.Quantity` | 100% | float (`1.0`) |

**Trzy wnioski, które zmieniły kod:**

- **`Variant Name`, nie `Categories.2`.** `Categories.2` zwraca nazwy kolekcji
  marketingowych („Colostrum dla mamy", „Dermokosmetyki z Colostrum").
  `Variant Name` zwraca to, co ma być pod nazwą produktu: „tabletki do ssania
  60 sztuk", „płyn 300 ml", „15 saszetek".
- **`event.URL` prowadzi na `genactiv.myshopify.com`** w 150/150 zdarzeń, nie na
  `genactiv.pl`. Nie nadaje się do linkowania.
- **`event.extra.checkout_url` w tej metryce nie istnieje** — `$extra` zawiera
  wyłącznie klucz `standard`. To pole pochodzi z Checkout Started.

### 3.3 Decyzja klienta o linkowaniu

Wszystkie odnośniki (miniatura, nazwa, przycisk) prowadzą do **stałego adresu
koszyka** `https://genactiv.pl/cart`. Omija to zarówno problem domeny myshopify,
jak i nieistniejący `checkout_url`.

## 4. Zbudowana sekcja

`templates/snippets/porzucony-koszyk-jeden-produkt.html`

Czerwony blok (`#F03642`) z nagłówkiem „Ten produkt czeka w Twoim koszyku!",
białą kartą produktu i przyciskiem „Wróć po niego".

### Prezentacja przeceny

```
199 zł   2̶4̶4̶ ̶z̶ł̶
[ Oszczędzasz 45 zł ]   ← zielony chip #1E7A45 na #E7F5EC
```

- Cena po obniżce duża i czerwona, regularna mniejsza i przekreślona obok —
  wzrok trafia najpierw na to, ile klient faktycznie zapłaci.
- **Oszczędność w złotówkach, nie w procentach.** Procent wymagałby filtrów
  `divide`/`multiply`, których nie zweryfikowano na tym koncie. `minus` jest
  potwierdzony renderem (patrz 6.2).
- Cały blok promocyjny w `{% if %}`; gałąź `{% else %}` (sama cena) to
  **83% realnych przypadków**.

### RWD

- `table-layout: fixed` na tabeli karty — kolumny trzymają proporcje
  (21% / 62% / 17%) niezależnie od długości nazwy produktu.
- **Żadnego `white-space: nowrap`** — to ono rozpychało układ w pierwszej wersji.
- Mobile (`≤480px`): miniatura 30%, treść 70%, kolumna „szt." znika, ilość
  pojawia się pod wariantem — przez klasy `desktop-only` / `mobile-only`,
  które już były w CSS szablonu.

Zweryfikowane na 320 / 375 / 600 px, w tym stress test: bardzo długa nazwa,
kategoria w trzech członach, ceny czterocyfrowe. Nic nie wychodzi poza 600 px.

### Dark mode

Zgłoszony przez klienta: w trybie ciemnym nagłówek i napis na przycisku robiły
się czarne na czerwonym tle. Dwie warstwy obrony:

1. **Jawne tło na każdym `td` z białym tekstem** (`bgcolor` + `background-color`)
   — Gmail nie odwraca tekstu leżącego na zadeklarowanym tle. Działa też tam,
   gdzie media query są ignorowane.
2. **`@media (prefers-color-scheme: dark)`** z `!important` — dla Apple Mail
   i Outlooka.

## 5. Błąd produkcyjny znaleziony przy okazji

### 5.1 Martwe CTA w żywym flow

Audyt 58 wiadomości w 13 flowach wykrył, że **12 szablonów buduje główny
przycisk z `{{ event.extra.checkout_url }}`**, a wszystkie trzy flow koszykowe
stoją na Added to Cart. Efekt: pusty `href`.

Potwierdzone renderem przez `POST /api/template-render` na realnym zdarzeniu:

| Flow | Status | Szablon | Napis na przycisku | `href` po renderze |
|------|--------|---------|--------------------|--------------------|
| Abandoned Cart Reminder | **live** | `SXcBja` | DOKOŃCZ ZAMÓWIENIE | **pusty** |
| | **live** | `WeKAHD` | WRÓĆ DO KOSZYKA | **pusty** |
| | **live** | `Rf5XM2` | ZAMÓW Z RABATEM | **pusty** |
| | **live** | `UQquNm` | DOKOŃCZ ZAMÓWIENIE | **pusty** |
| _COLOSTRUM | draft (A/B) | 4 szablony | — | **pusty** |
| _FIBERBIOM | draft (A/B) | 4 szablony | — | **pusty** |

Każdy mail ma 8 linków, z czego dokładnie jeden pusty — zawsze ten główny.
Reszta (logo, stopka, social) działa. Mail dociera, wygląda dobrze, karta
produktu się wypełnia, a **jedyny przycisk mający sprowadzić klienta z powrotem
nie prowadzi nigdzie**. Stan taki od 19.11.2025.

Drafty `_COLOSTRUM` i `_FIBERBIOM` to nowe warianty przygotowane na test A/B
przeciwko żywej wersji — miały ten sam błąd i weszłyby z nim na produkcję.

**Poza koszykiem jest czysto** — w pozostałych dziesięciu flowach zero
niezgodności między użytymi zmiennymi a metryką triggera.

### 5.2 Pozostałe znaleziska audytu (58 wiadomości)

| Problem | Liczba szablonów |
|---------|------------------|
| obrazki bez `alt` | 23 |
| angielska stopka | 8 |
| brak `{% unsubscribe %}` | 5 |

Brak `{% unsubscribe %}` w żywych flow dotyczy `Shopify newsletter - welcome`
(`Uv8LFX`) i `Back In Stock Flow - Standard` (`Sr7CMm`) — do weryfikacji w UI.

## 6. Ograniczenia Klaviyo API (sprawdzone empirycznie)

### 6.1 Czego nie da się zapisać

| Próba | Wynik |
|-------|-------|
| `PATCH /api/templates/{id}` na szablonie `SYSTEM_DRAGGABLE` | **400** „Unsupported template type" |
| `PATCH /api/templates/{id}` na szablonie przypiętym do flow | **404** „Template does not exist" |
| `PATCH /api/flow-messages/{id}` | **405** Method Not Allowed |
| `GET /api/templates/{id}` na szablonie z flow | 200 — odczyt działa |
| `GET /api/templates` (biblioteka) | 120 pozycji, **żadnego z 12 szablonów flow** |

**Wniosek:** szablony drag&drop oraz szablony przypięte do wiadomości flow są
przez API **tylko do odczytu**. Zapis wyłącznie przez edytor Klaviyo albo przez
utworzenie nowego szablonu bibliotecznego.

**Pułapka `--clone-test`:** klon trafia do biblioteki i tam `PATCH` przechodzi.
Zielony wynik testu na klonie **nie oznacza**, że zapis na oryginale zadziała.
Tak właśnie powstała moja przedwczesna deklaracja o wgrożeniu — test sprawdzał
inny obiekt niż cel.

### 6.2 Co API potrafi i warto wykorzystać

- **`POST /api/template-render`** — renderuje szablon z podanym kontekstem.
  Jedyny sposób, żeby zweryfikować logikę Django (`{% if %}`, `|minus`,
  `|lookup`) bez wysyłania maila. Wymaga `data.type = "template"` i `attributes.id`
  (nie `template_id`). Nie przyjmuje inline HTML.
- Potwierdzone tą drogą: **filtr `|minus` działa** (269 / 350 zł → „Oszczędzasz
  81 zł"), porównanie `CompareAtPrice > Price` też — oba pola są typu float,
  więc nie ma pułapki string-vs-liczba.

### 6.3 Mapowanie flow → szablony

Trzy poziomy, niżej zejść się nie da:

```
1. GET /api/flows?include=flow-actions        ← jedno zapytanie na wszystko
2. GET /api/flow-actions/{id}/flow-messages   ← per akcja
3. GET /api/flow-messages/{id}/template       ← tu jest template_id
```

Pułapki: `fields[flow-action]=action_type` → 400. `flow-actions/{id}/flow-messages?include=template`
→ 400. `flows?include=...` **nie łączy się** z `additional-fields[flow]=definition`
→ 400 (metrykę triggera trzeba pobrać osobnym zapytaniem na flow). Limit jest
niski — bez pauzy i backoffu leci 429.

**Ostrzeżenie metodologiczne:** pierwszy skan zwrócił „nie znaleziono" przy 13
flowach, bo wszystkie zapytania padły na 400/429. Cisza po serii błędów nie jest
ustaleniem — skrypt musi liczyć i wypisywać błędy osobno.

## 7. Co zostało zrobione

| Element | Stan |
|---------|------|
| Sekcja koszyka (snippet) | gotowa, RWD i dark mode zweryfikowane |
| Szablon `WL2W37` — „Koszyk mail 1 — WHY + sekcja koszyka" | **opublikowany**, typ CODE, zweryfikowany renderem na obu gałęziach `{% if %}` |
| Polska stopka w `WL2W37` | poprawiona (`{% unsubscribe 'Anuluj subskrypcję' %}`) |
| 12 naprawionych szablonów koszykowych | **opublikowane do biblioteki**, każdy z rendererem potwierdzającym 0 pustych linków |
| Podmiana szablonów w flow | **NIE zrobiona** — API nie pozwala |
| Backupy | `templates/snippets/backup/` — 13 szablonów, `.html` + `.json` |

### Mapowanie: oryginał → naprawiony

| Flow | Mail | W flow | Naprawiony (biblioteka) |
|------|------|--------|--------------------------|
| Abandoned Cart Reminder (**live**) | 1 | `SXcBja` | `UhKKt6` |
| | 2 | `WeKAHD` | `VQhRVp` |
| | 3 | `Rf5XM2` | `VAq6Td` |
| | 4 | `UQquNm` | `VkwjR3` |
| _COLOSTRUM (draft, A/B) | 1 | `RznQK5` | `TicFin` |
| | 2 | `Uxdz9q` | `T4iUgc` |
| | 3 | `S7LD2i` | `THWd5G` |
| | 4 | `VGCq3g` | `VgujxZ` |
| _FIBERBIOM (draft, A/B) | 1 | `VNmEYw` | `TLytgz` |
| | 2 | `TnUJRq` | `S7n6im` |
| | 3 | `QXtNJi` | `XM9L4R` |
| | 4 | `VHJqD8` | `SGn8Lt` |

Wszystkie naprawione nazwane `[NAPRAWIONY 2026-08-31] …`.

Cztery poprawki w każdym, bez ruszania treści, układu i stylów:
CTA i dwa linki produktowe → `genactiv.pl/cart`, `Categories.2` → `Variant Name`,
`alt` dla logo i grafiki stopki.

### Dodatkowo naprawione w całym mailu (po weryfikacji renderem)

Render pełnego szablonu na prawdziwych zdarzeniach ujawnił dwa problemy poza
samą sekcją koszyka:

1. **Grafiki „Dokończ zamówienie" i „Wróć do koszyka" nie były klikalne.**
   W `XnCJxJ` żaden obrazek nie miał linku — wyglądały jak przyciski, ale
   kliknięcie nie robiło nic. Obie prowadzą teraz do koszyka. Mail ma
   **3 drogi powrotu do koszyka zamiast jednej**.
2. **Siedem grafik nie miało `alt`.** Mail to niemal same obrazki, więc przy
   zablokowanych grafikach odbiorca widział pustą białą kolumnę.

Stan `WL2W37` po zmianach: 12/12 obrazków z `alt`, 2 grafiki-przyciski
w odnośniku, 5 linków do koszyka, 0 pustych `href`.

### Potwierdzona kolejność bloków w `WL2W37`

```
1. logo GENACTIV
2. 250+ / Dokończ zamówienie
3. *** SEKCJA KOSZYKA ***      ← zgodnie z ustaleniem
4. ↓70% / bariera jelitowa
5. ekspert
6. Wróć do koszyka
7. opakowania
8. liofilizowane / skuteczność
```

### Weryfikacja dynamiki — obie gałęzie `{% if %}`

Przez `POST /api/template-render` na prawdziwych zdarzeniach Added to Cart:

| Wariant | Zdarzenie | Wynik |
|---------|-----------|-------|
| z promocją | COLOSTRUM JUNIOR, płyn 300 ml, 289 / 338 zł | cena, przekreślona regularna, „Oszczędzasz 49 zł" |
| bez promocji | COLOSTRUM GENACTIV 60 kapsułek, 105 zł | sama cena |

W obu: zero surowych tagów, zero pustych `href`, nazwa/wariant/zdjęcie z eventu.

## 8. Ograniczenie narzędzi: nie da się wysłać maila z grafikami

**Gmail MCP usuwa wszystkie znaczniki `<img>` z wysyłanej wiadomości.**
Potwierdzone testem minimalnym — wysłano:

```html
<p>Przed obrazkiem.</p><img src="...cloudfront..."/><p>Po obrazku.</p><img src="...shopify..."/><p>Koniec.</p>
```

Do skrzynki dotarło:

```html
<p>Przed obrazkiem.</p><p>Po obrazku.</p><p>Koniec.</p>
```

Tekst nienaruszony, oba obrazki wycięte, 1,1 KB. **To nie jest kwestia rozmiaru
maila ani struktury HTML** — obrazki znikają zawsze, niezależnie od źródła
(cloudfront i `cdn.shopify.com` tak samo).

Konsekwencje:

- Trzy wysyłki testowe w trakcie prac były pod względem wizualnym bezużyteczne:
  brakowało w nich wszystkich grafik, łącznie z miniaturą produktu.
- Wczesna diagnoza była błędna — zakładano blokadę obrazów po stronie odbiorcy,
  a przyczyna leżała w narzędziu wysyłkowym. Kosztowało to trzy rundy wysyłek.
- **Do testów wizualnych służą dwie drogi:** pliki HTML otwierane lokalnie
  (`templates/snippets/PELNY-MAIL-*.html`, komplet 12 grafik) albo wysyłka
  testowa z Klaviyo. Tylko ta druga jest miarodajna dla trybu ciemnego
  i renderowania na telefonie.

## 9. Następne kroki

Wszystko poniżej wymaga edytora Klaviyo — API nie zapisze szablonu przypiętego
do flow ani szablonu drag&drop (patrz 6.1).

### Priorytet 1 — żywy flow wysyła maile z martwym przyciskiem

Flow **Abandoned Cart Reminder** jest `live` i od 19.11.2025 wysyła cztery maile,
w których główny przycisk nie prowadzi nigdzie. To jedyne zadanie wpływające na
wiadomości wysyłane w tej chwili.

Dla każdej z czterech wiadomości: `Edit content` → `Copy from existing template`
→ wybrać odpowiedni `[NAPRAWIONY 2026-08-31] live-mailN` (mapowanie w sekcji 7).

### Priorytet 2 — przed startem testu A/B

To samo dla ośmiu wiadomości w draftach `_COLOSTRUM` i `_FIBERBIOM`. Bez tego
test A/B porówna dwie wersje, z których **obie** mają martwe CTA, więc wynik
nie powie nic o testowanej zmianie.

### Priorytet 3 — wysyłka testowa sekcji koszyka z Klaviyo

Szablon `WL2W37` → `Edytuj szablon` → **Wyślij testowy e-mail**.

To jedyna droga do miarodajnego sprawdzenia, bo maile wysyłane narzędziami
asystenta **nie zawierają grafik** (sekcja 8). Do sprawdzenia:

- czy miniatura produktu i pozostałe grafiki się wyświetlają,
- tryb ciemny na telefonie: czy nagłówek „Ten produkt czeka w Twoim koszyku"
  i napis „Wróć po niego" są białe,
- czy obie grafiki-przyciski („Dokończ zamówienie", „Wróć do koszyka")
  otwierają koszyk.

Podgląd bez wysyłki: `templates/snippets/PELNY-MAIL-z-promocja.html`
i `…-bez-promocji.html` — otwierane w przeglądarce, komplet 12 grafik.

### Priorytet 4 — podpięcie sekcji koszyka do flow

Zdecydować, do której wiadomości flow trafia `WL2W37`, i podpiąć ją w edytorze.
Decyzja biznesowa: czy zastępuje obecny mail 1, czy wchodzi jako nowy wariant
do testu A/B.

### Priorytet 5 — sprzątanie w `XnCJxJ`

Usunąć z niego nieaktualną sekcję koszyka **oraz osierocony blok tekstowy**
zawierający komentarz zaczynający się od `GENACTIV — sekcja`. To pozostałość po
wklejeniu wcześniejszej wersji; API tego nie usunie.

W koncie pojawił się też szablon `VhCmhk` („Koszyk mail 1 — WHY_original",
utworzony 31.08 15:21) — wygląda na kopię oryginału zrobioną po stronie klienta.
Warto ustalić, czy ma zostać, żeby nie mnożyć wariantów tego samego maila.

### Priorytet 6 — dług techniczny z audytu

23 szablony z obrazkami bez `alt`, 8 z angielską stopką, 5 bez
`{% unsubscribe %}` — w tym dwa w żywych flow: `Shopify newsletter - welcome`
(`Uv8LFX`) i `Back In Stock Flow - Standard` (`Sr7CMm`).

Pełna lista: `reports/audyt-szablonow-flow.csv`. Ponowny audyt:
`python3 templates/snippets/audyt_szablonow_flow.py`.

## 10. Narzędzia

| Skrypt | Zastosowanie |
|--------|--------------|
| `templates/snippets/build_koszyk_mail1.py` | Scala sekcję z szablonem, generuje podglądy na realnych zdarzeniach. Idempotentny — podmienia sekcję zamiast dokładać drugą |
| `templates/snippets/audyt_szablonow_flow.py` | Mapuje flow → szablony, wykrywa puste linki, domenę myshopify, zmienne niezgodne z metryką triggera, brak `{% unsubscribe %}`, obrazki bez `alt`. `--flow <fraza>` zawęża zakres |
| `templates/snippets/napraw_szablony_koszyk.py` | Naprawia 12 szablonów. Tryby: dry-run (domyślny), `--clone-test`, `--publish-library`, `--apply` |

Wyniki audytu: `reports/audyt-szablonow-flow.csv`.

## 11. Wnioski na przyszłość

- **Nie minifikować HTML maili.** Regex usuwający komentarze zjada zamknięcie
  warunkowego komentarza `<!--[if !mso]><!-->`, przez co `<meta charset>` ląduje
  wewnątrz niedomkniętego komentarza i polskie znaki zamieniają się w „199 zĹ".
  Wykryte przed wysyłką; oszczędność 4 KB nie była warta ryzyka.
- **Nie wklejać komentarzy dokumentacyjnych do Klaviyo.** Edytor drag&drop
  potrafi zamienić duży komentarz HTML w osobny blok tekstowy, który zostaje
  w szablonie. Dokumentacja należy do repo, w kodzie zostają tylko markery.
- **Weryfikować na tym obiekcie, który się zmienia.** Test na klonie nie dowodzi,
  że zapis na oryginale przejdzie, jeśli klon jest innego rodzaju zasobem.
- **Zawsze sprawdzać, czym są pola zdarzenia,** zanim się je wstawi do szablonu.
  Trzy z czterech błędów w tych mailach to użycie pola, które w danej metryce
  albo nie istnieje, albo znaczy co innego, niż sugeruje nazwa.
- **Sprawdzaj, co faktycznie dotarło, a nie co wysłałeś.** Trzy rundy maili
  testowych nie pokazały ani jednej grafiki, bo narzędzie wysyłkowe usuwa
  `<img>`. Pierwsza hipoteza (blokada obrazów u odbiorcy) była błędna
  i utrzymała się przez dwie wysyłki. Pobranie wysłanej wiadomości przez API
  i sprawdzenie jej treści zajęło minutę i rozstrzygnęło sprawę od razu.
- **Minimalny test bije spekulację.** Jeden mail z dwoma obrazkami i trzema
  akapitami dowiódł, że rzecz nie zależy od rozmiaru ani struktury HTML —
  czego nie dało się orzec, patrząc na 28-kilobajtowy szablon.

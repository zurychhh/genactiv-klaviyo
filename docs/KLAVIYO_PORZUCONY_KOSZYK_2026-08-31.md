# Porzucony koszyk w Klaviyo — sekcja wizualizacji i naprawa flow

**Data:** 2026-08-31
**Zakres:** szablon `XnCJxJ` („Koszyk mail 1 — WHY"), trzy flow koszykowe, 12 szablonów
**Status:** sekcja gotowa i opublikowana; naprawa 12 szablonów gotowa, **czeka na ręczne podpięcie w Klaviyo**

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

## 8. Następne kroki

### Priorytet 1 — żywy flow wysyła maile z martwym przyciskiem

W Klaviyo, dla każdej z czterech wiadomości flow **Abandoned Cart Reminder**:
`Edit content` → `Copy from existing template` → wybrać `[NAPRAWIONY 2026-08-31] live-mailN`.

To jedyne zadanie, które ma wpływ na obecnie wysyłane maile. Reszta może poczekać.

### Priorytet 2 — przed startem testu A/B

To samo dla ośmiu wiadomości w draftach `_COLOSTRUM` i `_FIBERBIOM`. Bez tego
test A/B porówna dwie wersje, z których obie mają martwe CTA.

### Priorytet 3 — sekcja koszyka

1. Podpiąć `WL2W37` do właściwej wiadomości flow (którą — decyzja biznesowa).
2. Usunąć ze starego `XnCJxJ` nieaktualną sekcję **oraz osierocony blok tekstowy**
   zawierający komentarz zaczynający się od `GENACTIV — sekcja`. To pozostałość
   po wklejeniu wcześniejszej wersji; API tego nie usunie.

### Priorytet 4 — weryfikacja, której nie da się zrobić zdalnie

- **Dark mode na telefonie** — czy nagłówek i napis na przycisku są białe.
  Wysłano dwa maile testowe na `oleksiakpiotrrafal@gmail.com`
  i `doperacz1935@gmail.com`; wynik nieznany.
- **Miniatura produktu w Gmailu** — w pierwszym teście kolumna była pusta.
  Nie ustalono, czy to blokada obrazów po stronie odbiorcy, czy błąd.
  W drugim teście zdjęcia idą z `cdn.shopify.com` (URL-e odpowiadają 200).

### Priorytet 5 — dług techniczny z audytu

23 szablony z obrazkami bez `alt`, 8 z angielską stopką, 5 bez
`{% unsubscribe %}` (w tym dwa w żywych flow — `Uv8LFX`, `Sr7CMm`).
Skrypt audytowy generuje pełną listę.

## 9. Narzędzia

| Skrypt | Zastosowanie |
|--------|--------------|
| `templates/snippets/build_koszyk_mail1.py` | Scala sekcję z szablonem, generuje podglądy na realnych zdarzeniach. Idempotentny — podmienia sekcję zamiast dokładać drugą |
| `templates/snippets/audyt_szablonow_flow.py` | Mapuje flow → szablony, wykrywa puste linki, domenę myshopify, zmienne niezgodne z metryką triggera, brak `{% unsubscribe %}`, obrazki bez `alt`. `--flow <fraza>` zawęża zakres |
| `templates/snippets/napraw_szablony_koszyk.py` | Naprawia 12 szablonów. Tryby: dry-run (domyślny), `--clone-test`, `--publish-library`, `--apply` |

Wyniki audytu: `reports/audyt-szablonow-flow.csv`.

## 10. Wnioski na przyszłość

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

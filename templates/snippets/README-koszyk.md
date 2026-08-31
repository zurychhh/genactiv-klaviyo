# Sekcja „Ten produkt czeka w Twoim koszyku"

Blok wizualizacji porzuconego koszyka wstawiany do szablonu Klaviyo
**„Koszyk mail 1 — WHY"** (`XnCJxJ`), pomiędzy grafikę z CTA „Dokończ zamówienie"
a grafikę „↓70%".

## Pliki

| Plik | Rola |
|------|------|
| `porzucony-koszyk-jeden-produkt.html` | Sama sekcja — to się wkleja do Klaviyo jako blok HTML |
| `build_koszyk_mail1.py` | Scala sekcję z szablonem, generuje podglądy. Read-only wobec Klaviyo |
| `koszyk-mail1-WHY-z-koszykiem.html` | Pełny szablon (wynik scalenia) |
| `koszyk-mail1-PODGLAD.html` | Podgląd, gałąź promocyjna, realne dane z eventu |
| `koszyk-mail1-PODGLAD-bez-promocji.html` | Podgląd, gałąź `{% else %}` — 83% realnych przypadków |
| `test-rwd-koszyk.html` | Kompaktowy mail testowy do wysyłki poza Klaviyo |

```bash
python3 templates/snippets/build_koszyk_mail1.py
```

Skrypt jest **idempotentny**: jeśli szablon w Klaviyo już zawiera sekcję,
usuwa ją i wstawia bieżącą wersję zamiast dokładać drugą. Przerywa, gdy
kotwica „70%" nie występuje dokładnie raz albo gdy grafika „Dokończ
zamówienie" nie znajduje się przed nią.

## Trigger i zmienne

Flow uruchamia metryka **Added to Cart** (Shopify, `WcWiXd`) — jeden produkt
na zdarzenie. Nie Checkout Started.

Pola zweryfikowane na **150 realnych zdarzeniach** (2026-08-31):

| Zmienna | Wypełnienie | Uwagi |
|---------|-------------|-------|
| `{{ event.ImageURL }}` | 100% | `cdn.shopify.com` |
| `{{ event\|lookup:'Product Name' }}` | 100% | nazwa z karty produktowej Shopify |
| `{{ event\|lookup:'Variant Name' }}` | 99% | forma i wielkość opakowania, np. „tabletki do ssania 60 sztuk" |
| `{{ event.Price }}` | 100% | float, stąd `\|floatformat:0` |
| `{{ event.CompareAtPrice }}` | **17%** | stąd gałąź `{% else %}` jest przypadkiem domyślnym |
| `{{ event.Quantity }}` | 100% | float (`1.0`), stąd `\|floatformat:0` |

### Czego NIE używamy i dlaczego

- **`{{ event.URL }}`** — w 150/150 zdarzeń wskazuje na `genactiv.myshopify.com`,
  nie na `genactiv.pl`. Wszystkie linki (zdjęcie, nazwa, przycisk) prowadzą do
  stałego adresu koszyka `https://genactiv.pl/cart`.
- **`{{ event.Categories.2 }}`** — zwraca nazwy kolekcji marketingowych
  („Colostrum dla mamy", „Dermokosmetyki z Colostrum"), a nie formę opakowania.
  Właściwe pole to `Variant Name`.
- **`{{ event.extra.checkout_url }}`** — w metryce Added to Cart nie istnieje
  (`$extra` zawiera wyłącznie klucz `standard`). To pole pochodzi z Checkout
  Started. Referencyjny szablon `Y2rJvV` mieszał oba źródła.

## Znany błąd w szablonie referencyjnym Y2rJvV

Szablon `Y2rJvV` („porzucony-koszyk-mail1-18.11 - FINAL") zrenderowany przez
`POST /api/template-render` na realnym zdarzeniu **Added to Cart**:

- karta produktu renderuje się poprawnie (nazwa, wariant, zdjęcie, cena),
- ale przycisk „DOKOŃCZ ZAMÓWIENIE" ma **pusty `href`** — używa
  `{{ event.extra.checkout_url }}`, którego w Added to Cart nie ma.

Czyli mail prowadziłby donikąd. Dlatego u nas wszystkie linki wskazują na stały
adres koszyka. Skan flowów (2026-08-31) pokazał, że `Y2rJvV` nie jest podpięty
do żadnego flow, więc nic obecnie nie wysyła.

## Dark mode

Gmail i Apple Mail odwracają kolory w trybie ciemnym — biały nagłówek i biały
napis na przycisku robiły się czarne na czerwonym tle. Dwie warstwy obrony:

1. **Jawne tło na każdym `td` z białym tekstem** (`bgcolor` + `background-color`).
   Gmail nie odwraca tekstu leżącego na zadeklarowanym tle. To działa również
   tam, gdzie media query są ignorowane.
2. **`@media (prefers-color-scheme: dark)`** z `!important` — dokłada
   `build_koszyk_mail1.py` do `<head>`. Respektują je Apple Mail i Outlook.

Reguły muszą być w `<head>`, więc przy wklejaniu samego snippetu jako bloku HTML
trzeba je dodać osobno w ustawieniach szablonu.

## RWD

- `table-layout: fixed` na tabeli karty — kolumny trzymają proporcje (21% / 62% / 17%)
  niezależnie od długości nazwy produktu. Bez tego długa nazwa rozpycha tabelę poza 600 px.
- Żadnego `white-space: nowrap` — to ono rozpychało układ w pierwszej wersji.
- Na mobile (`max-width: 480px`) miniatura idzie na 30%, treść na 70%,
  a kolumna „szt." znika — ilość pojawia się pod nazwą wariantu przez klasy
  `desktop-only` / `mobile-only`, które są już w CSS szablonu `XnCJxJ`.

## Pułapki, na których się przejechaliśmy

- **Nie minifikuj tego HTML.** Regex usuwający komentarze zjada zamknięcie
  warunkowego komentarza `<!--[if !mso]><!-->`, przez co `<meta charset>` ląduje
  wewnątrz niedomkniętego komentarza i polskie znaki zamieniają się w „199 zĹ".
- **Nie wklejaj komentarzy dokumentacyjnych do Klaviyo.** Edytor drag&drop
  potrafi zamienić duży komentarz HTML w osobny blok tekstowy, który zostaje
  w szablonie i którego skrypt nie usuwa razem z sekcją. Stąd ta dokumentacja
  jest w osobnym pliku, a snippet ma tylko markery `GC-CART-SECTION:START/END`.
- **Podgląd otwieraj z pliku `-PODGLAD`,** nie z `koszyk-mail1-WHY-z-koszykiem.html`.
  Ten drugi zawiera surowe tagi Klaviyo i zawsze będzie wyglądał na zepsuty:
  długie tagi rozpychają układ, dopóki nie zostaną zastąpione wartościami.

## Stan wdrożenia (2026-08-31)

| Szablon | ID | Stan |
|---------|-----|------|
| Koszyk mail 1 — WHY | `XnCJxJ` | drag&drop, zawiera **starą** wersję sekcji + osierocony blok tekstowy z komentarzem. Nie do uratowania przez API |
| Koszyk mail 1 — WHY + sekcja koszyka | `WL2W37` | **CODE, aktualny** — [edycja](https://www.klaviyo.com/email-editor/WL2W37/edit) |

Backup `XnCJxJ` sprzed zmian: `backup/XnCJxJ-backup-2026-08-31.json` (+ `.html`).

### Dlaczego nowy szablon zamiast poprawki starego

`PATCH /api/templates/{id}` na szablonie `SYSTEM_DRAGGABLE` zwraca
`400 Unsupported template type`. Sprawdzone na klonie, nie na produkcji.
Ani MCP, ani REST nie potrafią nadpisać szablonu drag&drop — jedyne drogi to
ręczna edycja w Klaviyo albo nowy szablon typu `CODE`.

### Weryfikacja `WL2W37` przez `POST /api/template-render`

Na realnych zdarzeniach Added to Cart, obie gałęzie `{% if %}`:

- **bez promocji** — FIBERBIOM Z ANANASEM, 179 zł: nazwa, wariant „15 saszetek",
  zdjęcie, cena, jeden link `genactiv.pl/cart`, zero surowych tagów
- **z promocją** — COLOSTRUM zawiesina dwupak, 269 / 350 zł: „269 zł", przekreślone
  „350 zł", „Oszczędzasz 81 zł" — **filtr `|minus` działa**, porównanie
  `CompareAtPrice > Price` też (oba pola są typu float)

Przy okazji poprawiono stopkę: było `No longer want to receive these emails?`
z gołym `{% unsubscribe %}`, jest polski tekst i `{% unsubscribe 'Anuluj subskrypcję' %}`.

### Gdzie te szablony są używane

Skan 58 wiadomości w 13 flowach (bez błędów): **ani `XnCJxJ`, ani `Y2rJvV`
nie są podpięte do żadnego flow**. `WL2W37` trzeba podpiąć ręcznie w edytorze flow.

## Naprawa flow „Abandoned Cart Reminder" (2026-08-31)

Flow jest **live** od 19.11.2025, trigger **Added to Cart**, a wszystkie cztery
szablony budowały CTA z `{{ event.extra.checkout_url }}` — pola, które istnieje
wyłącznie w Checkout Started. Efekt: główny przycisk miał pusty `href`.

| Szablon | Mail | Napis na przycisku |
|---------|------|--------------------|
| `SXcBja` | 1 | DOKOŃCZ ZAMÓWIENIE |
| `WeKAHD` | 2 | WRÓĆ DO KOSZYKA |
| `Rf5XM2` | 3 | ZAMÓW Z RABATEM |
| `UQquNm` | 4 | DOKOŃCZ ZAMÓWIENIE |

Ten sam błąd mają drafty `_COLOSTRUM` i `_FIBERBIOM` (po 4 szablony).

### Skrypt naprawczy

```bash
python3 templates/snippets/napraw_szablony_koszyk.py              # dry-run (domyślnie)
python3 templates/snippets/napraw_szablony_koszyk.py --clone-test # test na kopiach
python3 templates/snippets/napraw_szablony_koszyk.py --apply      # PATCH na żywych
```

Cztery poprawki na szablon, bez dotykania treści, układu i stylów:

1. CTA `event.extra.checkout_url` → `https://genactiv.pl/cart`
2. `href` przez `event.URL` (2×) → `https://genactiv.pl/cart` — bo `event.URL`
   w 150/150 zdarzeń wskazuje na `genactiv.myshopify.com`
3. `event.Categories.2` → `event|lookup:'Variant Name'`
4. `alt` dla logo i grafiki stopki

Skrypt jest idempotentny i ma twardą kontrolę po naprawie: przerywa dany
szablon, jeśli zostało cokolwiek z `checkout_url`, `event.URL`, `Categories.2`,
zniknął `{% unsubscribe %}`, uszkodziła się struktura `html`/`body` albo został
obrazek bez `alt`. Ta kontrola realnie zadziałała — maile 3 i 4 mają inną
grafikę stopki niż 1 i 2, więc pierwszy przebieg je odrzucił zamiast wgrać
półprodukt.

### Weryfikacja na kopiach (nie na produkcji)

Każdy szablon: klon → `PATCH` → render na realnym zdarzeniu → usunięcie klonu.

- pustych `href` po naprawie: **0** we wszystkich czterech (przed: 1)
- CTA `href` = `https://genactiv.pl/cart`
- obrazków bez `alt`: 0

Porównanie treści karty na zdarzeniu „FIBERBIOM - Błonnik + Colostrum":

```
PRZED:  FIBERBIOM - Błonnik + Colostrum | Colostrum proszek | Ilość: 1 | 179 zł
PO:     FIBERBIOM - Błonnik + Colostrum | 15 saszetek       | Ilość: 1 | 179 zł
```

„Colostrum proszek" to nazwa kolekcji z `Categories.2`; „15 saszetek" to
faktyczny wariant produktu.

Backupy sprzed zmian: `backup/{SXcBja,WeKAHD,Rf5XM2,UQquNm}-mail{1..4}-backup-2026-08-31.{html,json}`
Gotowe pliki: `naprawione/*-naprawiony.html`

## Ograniczenie API: szablonów w flow NIE da się zapisać

Sprawdzone 2026-08-31 na wszystkich 12 szablonach flow koszykowych:

| Próba | Wynik |
|-------|-------|
| `GET /api/templates/{id}` | **200** — odczyt działa, backup się robi |
| `PATCH /api/templates/{id}` | **404** „Template does not exist" |
| `PATCH /api/flow-messages/{id}` | **405** Method Not Allowed |
| `GET /api/templates` (biblioteka) | 120 pozycji, **żaden z naszych 12** |

Szablony przypięte do wiadomości flow żyją poza biblioteką szablonów i są przez
API tylko do odczytu. `--clone-test` przechodzi, bo klon trafia **do biblioteki**
— i to jest pułapka: zielony wynik testu nie oznacza, że `--apply` zadziała.

### Obejście: publikacja do biblioteki

`--publish-library` tworzy poprawione kopie jako szablony biblioteczne, które
w edytorze flow podpina się przez „Copy from existing template" zamiast wklejać
28 KB HTML ręcznie dwanaście razy.

| Flow | Mail | Oryginał (w flow) | Naprawiony (biblioteka) |
|------|------|-------------------|--------------------------|
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

Każdy naprawiony zweryfikowany renderem na realnym zdarzeniu Added to Cart:
**pustych `href` = 0** (przed naprawą: 1).

## Dwie naprawy w całym mailu (2026-08-31, po weryfikacji renderem)

Weryfikacja pełnego szablonu przez `POST /api/template-render` na prawdziwych
zdarzeniach ujawniła dwa problemy poza samą sekcją koszyka:

### 1. Grafiki-przyciski nie były klikalne

`6d4a1ba8…` („Dokończ zamówienie") i `489c06ca…` („Wróć do koszyka") to grafiki
**wyglądające jak przyciski**, ale w `XnCJxJ` żaden obrazek nie miał linku
(`href: null`). Kliknięcie nie robiło nic.

Teraz obie są owinięte w odnośnik do koszyka — `link_button_images()`
w `build_koszyk_mail1.py`. Mail ma dzięki temu **3 miejsca prowadzące do
koszyka** zamiast jednego.

### 2. Siedem grafik bez `alt`

Mail składa się niemal wyłącznie z obrazków, więc przy zablokowanych grafikach
odbiorca widział pustą białą kolumnę. `add_base_alt()` uzupełnia opisy —
wszystkie oparte na tym, co faktycznie jest na grafice:

| Grafika | `alt` |
|---------|-------|
| `8b069ddc` | GENACTIV |
| `6d4a1ba8` | 250+ aktywnych substancji w 1 suplemencie — Dokończ zamówienie |
| `2faa82e1` | Colostrum uszczelnia barierę jelitową… nawet o 70% |
| `96d71fb0` | Colostrum okiem eksperta — mgr Monika Stromkie-Złomaniec |
| `489c06ca` | Wróć do koszyka |
| `c1f72600` | Produkty GENACTIV Colostrum |
| `50bfc1e4` | Liofilizowane, potwierdzona skuteczność, szybko pobierane |

Stan `WL2W37` po `PATCH`: **12/12 obrazków z `alt`**, 2 grafiki-przyciski
w odnośniku, 5 linków do koszyka, 0 pustych `href`.

`PATCH` na `WL2W37` **działa**, bo to szablon biblioteczny typu `CODE` — inaczej
niż szablony w flow i inaczej niż drag&drop `XnCJxJ`.

## Weryfikacja dynamiki na prawdziwych zdarzeniach

Zamiast podstawiać dane własnym skryptem, cały szablon renderuje Klaviyo:

```
POST /api/template-render  {data:{type:"template",attributes:{id:"WL2W37",context:{event:{…}}}}}
```

Kontekst = `event_properties` prawdziwego zdarzenia Added to Cart, z kluczami
pozbawionymi prefiksu `$` (Klaviyo widzi `$extra` jako `event.extra`).

| Wariant | Zdarzenie | Wynik |
|---------|-----------|-------|
| z promocją | COLOSTRUM JUNIOR…, płyn 300 ml, 289 / 338 zł | cena, przekreślona regularna, „Oszczędzasz 49 zł" |
| bez promocji | COLOSTRUM GENACTIV 60 kapsułek, 105 zł | sama cena, bez chipa i przekreślenia |

W obu: zero surowych tagów, zero pustych `href`, nazwa/wariant/zdjęcie z eventu.
To potwierdza, że `{% if %}` działa w obie strony, a `|minus` liczy poprawnie.

# Persony LP → segmenty MECE w Klaviyo

**Data:** 10.09.2026
**Zakres:** 9 landing page'y person GenActiv → rozłączny i wyczerpujący podział bazy Klaviyo
**Baza:** 39 065 profili (z czego 9 088 ze zgodą marketingową e-mail)

---

## 1. Co zostało zrobione

Podział całej bazy Klaviyo na segmenty odpowiadające personom z landing page'y —
w formule MECE: **każdy profil trafia do dokładnie jednego segmentu, a segmenty
razem pokrywają 100% bazy.**

Pliki:

| Plik | Rola |
|------|------|
| `klaviyo-mcp/persona_config.py` | Jedyne źródło prawdy: 9 person, priorytety, sygnały, uzasadnienia |
| `klaviyo-mcp/persona_lib.py` | Klient Klaviyo API (segmenty, członkostwo, bulk import) |
| `klaviyo-mcp/persona_step1_signals.py` | Tworzy 16 segmentów-SYGNAŁÓW (surowych, nakładających się) |
| `klaviyo-mcp/persona_step2_assign.py` | Liczy przypisanie MECE + zapisuje właściwość profilu |
| `klaviyo-mcp/persona_step3_segments.py` | Tworzy docelowe segmenty `PERSONA \| …` + kontrola sumy |
| `reports/persony-lp-przypisanie.csv` | Liczebności per segment, z rozbiciem na źródło sygnału |

---

## 1a. Wynik — podział bazy (stan 10.09.2026)

| Segment w Klaviyo | ID | Razem | z LP | z produktu |
|---|---|---:|---:|---:|
| `PERSONA \| 01 JUNIOR \| Rodzic dziecka 3-7 lat` | `UcH6tk` | 9 141 | 274 | 8 867 |
| `PERSONA \| 02 WŁOSY \| Wypadanie i skóra głowy` | `WsTvTE` | 2 711 | 50 | 2 661 |
| `PERSONA \| 03 GLOW \| Kosmetyki do twarzy, nawilżenie` | `WKpx8H` | 3 578 | 23 | 3 555 |
| `PERSONA \| 04 SKIN&GUT \| Skóra od środka` | `VSuHtU` | 90 | 90 | 0 |
| `PERSONA \| 05 SILVERSI \| 50+, mleko klaczy` | `SELe3p` | 1 901 | 18 | 1 883 |
| `PERSONA \| 06 ODCHUDZANIE \| Fiberbiom w redukcji` | `TKxNzR` | 65 | 65 | 0 |
| `PERSONA \| 07 PŁASKI BRZUCH \| Wzdęcia` | `UF4Srx` | 170 | 170 | 0 |
| `PERSONA \| 08 REGULARNOŚĆ \| Wypróżnianie` | `WFmwPF` | 2 657 | 176 | 2 481 |
| `PERSONA \| 09 GUT FIXER \| Bariera jelitowa` | `Ww728T` | 12 914 | 290 | 12 624 |
| `PERSONA \| 10 REZ \| Zwierzęta (Furever)` | `Y4D8Bc` | 223 | 0 | 223 |
| `PERSONA \| 11 REZ \| Bez sygnału` | `RNsEqW` | 5 615 | — | — |
| **SUMA** | | **39 065** | 1 156 | 32 294 |

**Kontrola MECE przeszła na żywym koncie: suma segmentów = cała baza, 39 065 = 39 065.**
Rozłączność wynika z konstrukcji (jedna właściwość = jedna wartość), wyczerpanie
potwierdzone liczbowo.

Zauważ dysproporcję: **1 156 profili ma sygnał LP, 32 294 tylko produktowy**.
Cztery persony (`SKIN&GUT`, `ODCHUDZANIE`, `PŁASKI BRZUCH` oraz częściowo
`SILVERSI`) opierają się niemal wyłącznie na LP i dlatego są małe — to nie błąd,
tylko realny zasięg tych stron. Patrz §6.

Dodatkowo w koncie zostało **16 segmentów `SYG | …`** — surowe, żywe,
samoaktualizujące się pule sygnałów (9 × LP, 7 × produkt). Nie służą do wysyłek;
są materiałem wejściowym i podglądem bieżącego ruchu na landing page'ach.
Segment `TECH | Cała baza` (`SBMHS8`) to mianownik do kontroli sumy.

---

## 2. Dlaczego nie da się tego zrobić „zwykłymi" regułami segmentu

Dwa twarde ograniczenia, na które natrafiliśmy i które przesądziły o architekturze:

**(a) Same produkty NIE rozróżniają person.** Trzy persony Fiberbiomu
(odchudzanie / płaski brzuch / regularne wypróżnianie) promują *dokładnie te same
SKU*. Silversi i Skin&Gut Connector promują *dokładnie te same* produkty z mlekiem
klaczy. Z samego zakupu nie da się odróżnić tych intencji — potrzebny jest sygnał
deklaratywny.

**(a1) Ruch na LP jest mały.** 1 156 profili z sygnałem LP na 39 065 w bazie
(3,0%). Gdyby persony budować wyłącznie z wizyt na LP, dziewięć segmentów
objęłoby 3% bazy — stąd warstwa produktowa.

**(b) Klaviyo API nie pozwala wykluczyć segmentu z segmentu.** Warunek
`profile-group-membership` z `is_member: false` przyjmuje wyłącznie **listy**, nie
segmenty — próba podania ID segmentu kończy się `400: Group … does not exist`.
Sprawdzone na żywym koncie. Bez tego nie da się zbudować łańcucha
„persona 5 = swój sygnał ORAZ nie persona 1–4", a już na pewno nie da się wyrazić
segmentu dopełniającego („cała reszta bazy").

**Wniosek:** rozłączność musi wynikać ze **struktury danych**, nie z algebry
warunków. Dlatego przypisanie liczone jest raz, poza Klaviyo, a jego wynik
zapisany jest jako **jedna właściwość profilu** — właściwość ma z definicji jedną
wartość, więc MECE jest zagwarantowane konstrukcyjnie, a nie „wynegocjowane"
w kreatorze segmentów.

---

## 3. Sygnał, który to umożliwił

Zdarzenie **`Active on Site`** (metric `SHkgBz`) niesie właściwość **`page`**
z pełnym URL-em odwiedzanej strony. Landing page'e person są w niej widoczne:

```
"page": "https://genactiv.pl/pages/gutfixer?utm_source=…"
```

Dzięki temu wizyta na konkretnym LP jest filtrowalna warunkiem
`page contains "/pages/gutfixer"` — i to jest **jedyny** sygnał rozróżniający
persony dzielące ten sam koszyk produktowy.

Pozostałe wykorzystane sygnały:

| Metryka | ID | Użyta właściwość | Okno |
|---------|-----|------------------|------|
| Active on Site | `SHkgBz` | `page` (URL) | 365 dni |
| Ordered Product | `X6tAVW` | `SKU` | cała historia |
| Viewed Product | `Wic3Cx` | `URL` (uchwyt produktu) | 365 dni |

---

## 4. Reguła przypisania

Dwie warstwy, wewnątrz każdej rozstrzyga priorytet (niższy numer wygrywa).
Pierwsze trafienie kończy przypisanie.

### Warstwa 1 — wizyta na landing page'u (sygnał silny)

Wejście na LP to **zadeklarowany, świeży i konkretny problem**. Ma pierwszeństwo
przed historią zakupową, bo mówi, czego ktoś szuka *teraz*, a nie co kupił kiedyś.

### Warstwa 2 — kontakt z grupą produktową (sygnał słaby)

Stosowana wyłącznie do profili bez żadnego trafienia w LP. Mapowanie grup
produktowych na persony:

| Grupa produktowa | Persona | Podstawa |
|------------------|---------|----------|
| Produkty juniorskie | JUNIOR | SKU wyłączne dla tej persony |
| Szampon / maska / serum / bloker | WŁOSY | SKU wyłączne |
| Krem / maseczka | GLOW | SKU wyłączne |
| Mleko klaczy | SILVERSI | SKU wyłączne dla pary Silversi + Skin&Gut; Silversi jest domyślnym domem |
| Fiberbiom | REGULARNOŚĆ | **założenie** — patrz §6 |
| Colostrum dla dorosłych | GUT FIXER | LP Gut Fixer promuje dokładnie te SKU |
| Furever (psy, koty, konie) | REZ Zwierzęta | inny odbiorca |

`ODCHUDZANIE`, `PŁASKI BRZUCH` i `SKIN&GUT` **nie mają zasilania produktowego** —
ich produkty są w 100% współdzielone z innymi personami, więc mogą je zbudować
wyłącznie wizyty na LP. To celowe: lepiej mały precyzyjny segment niż duży zmyślony.

### Kolejność priorytetów i jej uzasadnienie

| Prio | Segment | Dlaczego tu |
|------|---------|-------------|
| 1 | JUNIOR — rodzic dziecka 3–7 lat | Kupuje dla kogoś innego niż on sam — intencja całkowicie rozłączna z resztą. Produkty juniorskie unikalne. |
| 2 | WŁOSY — wypadanie i skóra głowy | Unikalne SKU (szampon / maska / serum / bloker), nikt inny po nie nie sięga. |
| 3 | GLOW — kosmetyki do twarzy | Unikalne SKU kosmetyczne. Niżej niż włosy, bo kolekcje dermo łączą oba typy. |
| 4 | SKIN&GUT — skóra od środka | Dzieli produkty z Silversi w 100%; rozróżnia je **wyłącznie** LP. Wyżej, bo intencja węższa. |
| 5 | SILVERSI — 50+, mleko klaczy | Domyślny dom dla kupujących mleko klaczy bez sygnału LP. |
| 6 | ODCHUDZANIE — Fiberbiom w redukcji | Najbardziej odrębna komercyjnie z trzech person Fiberbiomu. |
| 7 | PŁASKI BRZUCH — wzdęcia | Objawowa, węższa niż ogólna regularność. |
| 8 | REGULARNOŚĆ — wypróżnianie | Najogólniejsza obietnica Fiberbiomu. |
| 9 | GUT FIXER — bariera jelitowa | Najszersza propozycja jelitowa; zbiera tych, którzy weszli w temat jelit bez węższej deklaracji. |

Priorytet rozstrzyga też sytuację, gdy ktoś odwiedził **kilka** LP — wygrywa
persona o niższym numerze. Alternatywą byłoby „ostatnia wizyta wygrywa", ale
Klaviyo nie udostępnia recency wizyty na poziomie segmentu bez przeciągania
pełnej historii zdarzeń.

---

## 5. Właściwości zapisywane na profilu

| Właściwość | Wartość |
|------------|---------|
| `persona_lp` | klucz segmentu, np. `gutfixer`, `junior`, `rez_fiberbiom` |
| `persona_lp_zrodlo` | `lp` (wizyta na landing page'u) albo `produkt` (zakup/przeglądanie) |
| `persona_lp_data` | data przeliczenia, np. `2026-09-10` |

`persona_lp_zrodlo` jest istotne operacyjnie: profile z `lp` mają sygnał mocny
i zasługują na komunikację dokładnie w języku danego LP. Profile z `produkt` to
przypisanie wywnioskowane — tam warto testować przekaz, nie zakładać.

Profil **bez żadnego sygnału nie dostaje właściwości** — segment
`persona_lp is not set` domyka podział na całą bazę bez potrzeby zapisu do
wszystkich 39 065 profili.

---

## 6. Gdzie przypisanie jest założeniem, a nie faktem

Decyzja z 10.09.2026: maksymalne pokrycie bazy. Dwie wieloznaczne grupy
produktowe zostały dopisane do najszerszej pasującej persony. Konsekwencje
trzeba znać:

**Fiberbiom bez sygnału LP → `REGULARNOŚĆ`.** Trzy LP Fiberbiomu promują
*identyczne* SKU, więc z samego zakupu nie da się odróżnić odchudzania od wzdęć
i od zaparć. Wybrano regularność, bo to najszersza obietnica produktu
(„73% badanych potwierdza — Fiberbiom wspomaga regularne wypróżnianie").
**To założenie.** Naturalny następny krok: test A/B trzech przekazów na tej
grupie — wynik testu jest tańszym i pewniejszym sposobem przypisania niż
domysł, i pozwoli zasilić `ODCHUDZANIE` oraz `PŁASKI BRZUCH` realnymi danymi.

**Colostrum dorosły bez sygnału LP → `GUT FIXER`.** Tu podstawa jest mocniejsza:
LP Gut Fixer promuje dokładnie te SKU (Colostrum proszek 45 g, Colostrum
120 kapsułek) obok Fiberbiomu. Dopasowanie wynika z treści LP, nie z domysłu.
Mimo to warto pamiętać, że dla wielu z tych osób motywacją jest **odporność**,
nie bariera jelitowa — a **odporność dorosłego nie ma własnego landing page'a**.
To największa grupa produktowa w katalogu bez dedykowanego LP; luka warta
zamknięcia.

### Jak nie dać się zwieść tym danym

Każdy profil niesie `persona_lp_zrodlo`:

- `lp` — sygnał mocny, osoba sama zadeklarowała problem wchodząc na LP,
- `produkt` — przypisanie wywnioskowane.

**Przy każdym pomiarze skuteczności przekazu rozbijaj wynik po tym polu.**
Zmieszanie obu źródeł w jednej metryce zafałszuje ocenę: segment z 428 osobami
z LP i 25 000 z produktu to w praktyce dwie różne publiczności pod jedną nazwą.

Uwaga na marginesie: istnieje też `/pages/fiberbiom` — strona-hub opisująca
wszystkie trzy korzyści naraz. Wizyta na niej **nie** deklaruje konkretnego
problemu, więc nie jest traktowana jako sygnał persony; zachowuje się dokładnie
tak jak zakup Fiberbiomu.

---

## 7. Jak często nowe profile trafiają do person

Trzy warstwy o różnej szybkości. Segmenty-SYGNAŁY (`SYG | …`) są **żywe** —
Klaviyo przelicza je sam, w praktyce w kilka minut od zdarzenia. Wolne jest
tylko przepisanie tego na właściwość `persona_lp`.

### Warstwa 1 — przyrostowa, co 15 minut (podstawowa)

`klaviyo-mcp/persona_step4_incremental.py` pobiera z segmentów-sygnałów
**wyłącznie profile, które dołączyły w ostatnim oknie** (filtr
`joined_group_at`). Zmierzony czas przebiegu: **~6 sekund**.

```bash
python3 klaviyo-mcp/persona_step4_incremental.py --lookback-minutes 45 --live
```

Harmonogram: `.github/workflows/persony-lp-incremental.yml`, cron `*/15`.
**Wymaga dodania sekretu `KLAVIYO_API_KEY` w ustawieniach repozytorium**
(Settings → Secrets and variables → Actions). Bez tego workflow kończy się błędem.

Okno 45 minut przy cronie co 15 minut daje trzykrotny zapas — pominięcie dwóch
przebiegów z rzędu niczego nie gubi, a nadmiarowe trafienia są nieszkodliwe,
bo skrypt zapisuje wyłącznie rzeczywiste zmiany.

**Reguła przyrostowa nigdy nie degraduje przypisania:**
1. sygnał LP bije każdy sygnał produktowy,
2. wśród sygnałów tego samego rodzaju wygrywa niższy `prio`,
3. przypisanie ze źródła `lp` nie zostanie nadpisane sygnałem produktowym.

Realny czas od zdarzenia do segmentu: **kilka minut** (ocena segmentu przez
Klaviyo) **+ do 15 minut** (cron) **+ ~1 minuta** (kolejka bulk import).
Praktycznie: **poniżej 20 minut**.

### Warstwa 2 — pełna rekoncyliacja, raz w miesiącu

Wyłapuje zmiany, których warstwa przyrostowa nie widzi (np. korekta priorytetów,
nowy produkt w katalogu, profile scalone).

```bash
python3 klaviyo-mcp/persona_step1_signals.py --live      # idempotentne
python3 klaviyo-mcp/persona_step2_assign.py --refresh --live
python3 klaviyo-mcp/persona_step3_segments.py --counts   # kontrola sumy
```

Uwaga: krok 2 pobiera pełne członkostwo (~55 tys. rekordów) i trwa **~15 minut**.

### Warstwa 3 — czas rzeczywisty dla wizyt na LP (opcjonalna, ręczna)

Klaviyo ma akcję flow **„Update profile property"** z wartością wpisaną na sztywno
— dokładnie to, czego tu trzeba. Flow wyzwalany metryką `Active on Site`
z warunkiem `page contains /pages/gutfixer` może ustawić `persona_lp = gutfixer`
w kilka minut, bez czekania na cron.

Koszt: **9 flowów do zbudowania ręcznie w UI** (API Klaviyo nie tworzy flowów).
Zysk względem warstwy 1: kilkanaście minut. Wolumen znikomy — wszystkich wizyt
na LP jest ~1 156 rocznie.

Jeśli to robić, przyjmij dla tej warstwy regułę **„ostatnia wizyta na LP wygrywa"**
(bez conditional splitów) — jest prostsza i sensowniejsza dla świeżej deklaracji
intencji niż statyczny priorytet. Warstwa 1 tego nie cofnie, bo nie degraduje
przypisań ze źródłem `lp`.

### Ważne: do wyzwalania automatyzacji nie potrzebujesz tej właściwości

Jeśli chodzi o to, żeby ktoś, kto **właśnie** wszedł na LP Gut Fixera, dostał
odpowiedni przekaz — wyzwalaj flow bezpośrednio zdarzeniem `Active on Site`
z warunkiem na `page`. To działa natychmiast. Właściwość `persona_lp` i segmenty
MECE służą do **targetowania kampanii i raportowania**, gdzie kwadrans opóźnienia
nie ma znaczenia.

### Zmiana konfiguracji

Priorytety, sygnały i nazwy: wyłącznie w `persona_config.py`. Potem krok 2 (pełne
przeliczenie) i krok 3.

---

## 7a. Pułapki API napotkane po drodze (do zapamiętania)

| Próba | Wynik |
|-------|-------|
| `profile-group-membership` z `is_member: false` i ID **segmentu** | `400 "Group … does not exist for company"` — przyjmuje tylko listy |
| To samo z polem `timeframe_filter` | `400 "'timeframe_filter' is not a valid field for … ProfileNoGroupMembershipCondition"` |
| `profile-property` z `"property": "persona_lp"` | `400 "All custom profile properties must be of the form: properties['property name']"` |
| `profile-property` z `"property": "properties['persona_lp']"` | działa ✓ |

Wbudowane pola (`first_name`, `email`, `phone_number`) adresuje się gołą nazwą —
własne **muszą** być w nawiasach. Łatwo się o to potknąć, bo istniejące segmenty
na koncie używają wyłącznie wbudowanych.

Zapis przez `POST /api/profile-bulk-import-jobs` **scala** `properties`
(zweryfikowane na profilu z `Shopify Tags`, `Initial Source`, `$consent` —
wszystkie przetrwały). Paczka do 10 000 profili / 5 MB; obiekt profilu przyjmuje
`id` zamiast e-maila.

---

## 8. Ograniczenia

- **Właściwość nie aktualizuje się sama** — robi to cron co 15 minut (§7).
  Jeśli workflow nie działa (brak sekretu, wyłączone Actions), nowe profile
  zostają w `REZ | Bez sygnału` i nikt tego nie zauważy. Segmenty-SYGNAŁY
  (`SYG | …`) są żywe zawsze i nadają się na kontrolę: rosnący `SYG` przy
  stojącym `PERSONA` oznacza, że cron nie chodzi.
- **`joined_group_at` liczy się od wejścia do segmentu, nie od zdarzenia.**
  W dniu utworzenia segmentu wszyscy jego członkowie mają ten sam
  `joined_group_at`, więc pierwszy przebieg przyrostowy z szerokim oknem
  pobiera całą bazę i trwa kilkanaście minut zamiast sekund. Po pierwszej
  godzinie problem znika. To samo zdarzy się po każdym odtworzeniu segmentu
  `SYG | …` — nie odtwarzaj ich bez potrzeby (krok 1 jest idempotentny).
- **Okno 365 dni na wizytę na LP.** Starsze wizyty nie liczą się jako sygnał.
- **Atrybucja onsite zależy od zgody cookie.** Przy konfiguracji Pandectes
  (`cookiesBlockedByDefault=7`) część ruchu na LP nie generuje `Active on Site` —
  realny zasięg person LP jest więc **niedoszacowany**, nie przeszacowany.
- **Segmenty pokrywają całą bazę, nie tylko zgody e-mail.** Z 39 065 profili
  zgodę marketingową e-mail ma 9 088. Do wysyłek łącz personę z istniejącym
  segmentem zgód albo z `AKTYWNI | otwarcie lub klik w 90 dni`.

---

## 9. Co z tym zrobić dalej

**1. Rozbijaj każdy pomiar po `persona_lp_zrodlo`.** `GUT FIXER` to 290 osób
z LP i 12 624 z produktu — to dwie różne publiczności pod jedną nazwą. Wspólna
metryka na nich niczego nie powie.

**2. Test A/B trzech przekazów Fiberbiomu na `REGULARNOŚĆ`.** 2 481 osób
przypisano tam na podstawie samego zakupu. Trzy warianty (odchudzanie / wzdęcia /
regularność) na tej grupie dadzą twardą podstawę do przepisania części z nich
do `ODCHUDZANIE` (dziś 65 osób) i `PŁASKI BRZUCH` (dziś 170) — czyli do
napełnienia dwóch person, które dziś są puste, danymi zamiast domysłem.

**3. Brakujący landing page: odporność dorosłego.** Największa grupa produktowa
w katalogu nie ma własnego LP; jej ruch wpada dziś do `GUT FIXER`. To jedyna
persona w tym zestawieniu, która istnieje w sprzedaży, ale nie istnieje
w komunikacji na stronie.

**4. Ruch na LP jest wąskim gardłem, nie segmentacja.** Cztery LP mają poniżej
100 zidentyfikowanych odwiedzających w 365 dni (`GLOW` 23, `SILVERSI` 18,
`ODCHUDZANIE` 65, `SKIN&GUT` 90). Przy takich liczbach żadna segmentacja nie
zrobi różnicy — najpierw ruch (płatny, newsletter, linkowanie wewnętrzne),
potem personalizacja. Uwaga: to liczby **zalogowanych/rozpoznanych** profili,
ruch całkowity jest wyższy — patrz zastrzeżenie o zgodzie cookie w §8.

**5. Przeliczaj raz w miesiącu** (§7). Bez tego nowe profile zostają
w `REZ | Bez sygnału`.

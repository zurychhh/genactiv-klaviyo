# A1 — Keyword research top 20 PDP + gap analysis + mapa sezonowa

**Wykonano:** 2026-08-17 · **Źródło danych:** Senuto API (klucz odblokowany 2026-08-17), GA4 (property 279858535)
**Status:** `needs-verify` — zadanie ma bramę ręczną (owner `CC+`)

## Co powstało

| Plik | Zawartość |
|------|-----------|
| `research/keyword-map-2026.csv` | **DoD** — 20 PDP × primary_kw, secondary_kw (4 frazy), volume, difficulty, CPC, nasza pozycja, luka konkurencyjna, tag sezonowy |
| `artefakty/gap-analysis-2026-08-17.csv` | 882 luki: konkurent w TOP10, my poza TOP10 — z wolumenem, trudnością i URL-em konkurenta |
| `artefakty/fetch_senuto_positions.py` | Pobiera pozycje z Senuto dla nas i konkurentów (read-only, idempotentny) |
| `artefakty/build_keyword_map.py` | Buduje obie tabele; reguły dopasowania fraz do PDP są w stałej `PDPS` |
| `artefakty/senuto-raw/` | Cache surowych odpowiedzi API (pozycje + Keyword Explorer) — **gitignore**, 5,7 MB, odtwarzalny |

Odtworzenie: `source venv/bin/activate && python3 sprint-2026-06/W1/A1/artefakty/fetch_senuto_positions.py && python3 sprint-2026-06/W1/A1/artefakty/build_keyword_map.py`

## WERYFIKACJA KONKURENTÓW — brief A1 był błędny

Zadanie kazało robić gap analysis „vs colostrigen.pl i immunolab". Sprawdzone w Senuto i w sieci:

- **Colostrigen to nasza własna marka**, nie konkurent. Produkty w aptekach figurują jako
  „Colostrum Genactiv (**Colostrigen**)" — producentem jest GENACTIV TRADE Sp. z o.o.
  Domeny `colostrigen.pl` / `.com` / `.eu` mają w Senuto zerową widoczność (nie istnieją jako serwisy).
- **`immunolab.com.pl` to firma mikrobiologiczna**, nie marka colostrum. Rankuje na
  „podłoże agarowe", „kurs mikrobiologii", „salmonella serotypy". Zero pokrycia tematycznego —
  wykluczona ze zbioru (pozostawiona w `COMPETITORS_CHECKED_OUT` jako ślad weryfikacji).

Gap analysis zrobiona na **realnych konkurentach organicznych** z Senuto `competitors/getData`:

| Domena | Wspólne frazy | Widoczność | TOP10 |
|--------|---------------|-----------|-------|
| genactiv.pl (my) | — | 48 275 | 1 059 |
| **genoscope.pl** | 134 | 24 412 | 966 |
| colostrumactive.pl | — | 406 | 69 |
| colostrumpolska.pl | — | 178 | 24 |

genoscope.pl sprzedaje m.in. „Colostrum Immune" — to najbliższy realny odpowiednik tego, co
brief nazwał „Immuno Lab", i jedyny konkurent w naszej skali.

## Główne wnioski

**1. Karty produktowe praktycznie nie istnieją w organicu.** Z 3 306 fraz w TOP50 tylko **181
prowadzi na PDP** (27 unikalnych kart), z czego 134 w TOP10. Resztę widoczności (2 665 fraz,
786 w TOP10) robi blog i `/pages/`.

**2. Fiberbiom — największa dziura.** 15 566 sesji w 90 dni (nr 1 wśród PDP), a karta rankuje
na **4 frazy, wszystkie o „arabinogalaktanie", najlepsza pozycja 16**. Cały ruch na tę kartę
jest płatny/bezpośredni. Frazy błonnikowe (`błonnik w proszku` 880/mc i sąsiednie) są
niezagospodarowane.

**3. genoscope.pl wygrywa blogiem, nie sklepem.** 1 864 z 2 446 ich fraz to blog, 757 w TOP10 —
dokładnie ta sama mechanika, którą my mamy na `/pages/`. Największe luki to treści, nie produkty:

| Fraza | Wolumen/mc | genoscope | my |
|-------|-----------|-----------|-----|
| ferrytyna | 74 000 | 3 | >50 |
| maść na blizny | 14 800 | 4 | >50 |
| maści na oparzenia | 6 600 | 4 | >50 |
| co na oparzenie | 5 400 | 8 | >50 |
| **siara** | 3 600 | 2 | >50 |
| colostrum kozie | 2 900 | 5 | >50 |
| maść ze srebrem | 2 400 | 2 | >50 |
| ciągłe zmęczenie | 1 900 | 4 | >50 |
| niska ferrytyna a jelita | 1 600 | 1 | 25 |

„Ferrytyna" i „ciągłe zmęczenie" pokrywają się z klastrami z monitoringu GEO
(`geo/llm-monitoring/queries.json`) — ten sam popyt widać w Google i w cytowaniach LLM.
„Siara" to synonim naszego rdzenia produktowego, na którym w ogóle nie jesteśmy.

**4. Kosmetyki mają znikomy popyt niebrandowy.** `maseczka z colostrum do twarzy` = 10/mc,
`maska colostrum` = 110/mc. Realny wolumen jest dopiero na frazach kategorii
(`maseczki na twarz` 6 600, `krem na blizny` 4 400, `serum na porost włosów` 2 400) —
kolumna `demand_tier` w mapie oznacza, gdzie PDP siedzi w niszy, a gdzie ma sens walka o kategorię.

**5. Sezonowość liczona z danych, nie z założeń.** Tag pochodzi z 12-miesięcznych trendów
Senuto (udział października–marca w rocznym wolumenie; ≥0,58 = `jesien-zima`, ≤0,42 = `wiosna-lato`).
Potwierdza hipotezę odpornościową: `colostrum dla dzieci` szczyt w **grudniu** (8 100/mc),
`tabletki do ssania na gardło` szczyt w grudniu, `bloker do skóry głowy` udział X–III = 0,79.
Frazy proszkowe wychodzą wiosenno-letnie (`colostrum w proszku` szczyt w czerwcu) — to sygnał,
że proszki sprzedają się w innym cyklu niż kapsułki i zawiesiny.

## Ograniczenia danych

- **`difficulty` jest tylko dla fraz, które ktokolwiek z badanych domen rankuje.** Senuto Keyword
  Explorer nie zwraca trudności — puste pole w mapie oznacza brak danych, nie zero.
- **Wolumeny to zaokrąglone kubełki Google** (10/20/30…880/1 000/1 300). Przy niskich wolumenach
  udział sezonowy jest zaszumiony — stąd konserwatywny próg 0,58.
- **`keywords_analysis` nie wspiera `country_id=200`** (Base 2.0) — tam Polska to `1`.
  `visibility_analysis` odwrotnie: `200`. Obie wartości są w skryptach zaszyte świadomie.
- Sesje GA4 z `pagePath` zawierają szum z web-pixel sandbox — odfiltrowany ręcznie przy budowie listy 20 PDP.

## Co dalej (propozycja do W2)

1. **Content na luki genoscope** — „siara", „ferrytyna", „colostrum kozie" to artykuły blogowe,
   nie zmiany na PDP. Wchodzi w blok C4–C7 (4 artykuły) ze sprintu SEO+GEO.
2. **Fiberbiom PDP** — przepisać meta i nagłówki pod `błonnik w proszku` / `błonnik na wzdęcia`
   zamiast pod „arabinogalaktan".
3. **Kanibalizacja** — `maseczka-z-colostrum-50-ml` i `maseczka-z-colostrum-genactiv-150ml` to
   ten sam produkt w dwóch pojemnościach i dostają identyczną mapę fraz. Do rozstrzygnięcia
   ręcznego: jedna karta kanoniczna albo różnicowanie treści.

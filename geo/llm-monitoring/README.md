# Monitoring cytowań GENACTIV w wyszukiwarkach AI

Zadanie **VIII-A3** (Sprint VIII, stream A · SEO/Organic). Cel: mierzalny, powtarzalny
miesięczny pomiar tego, czy GENACTIV jest wymieniany i linkowany w odpowiedziach
wyszukiwarek AI. Bez tego cel H2 „widoczność w LLM" jest niemierzalny.

## Co tu jest

| Plik | Rola |
|---|---|
| `queries.json` | Stały set 20 zapytań kontrolnych (id, zapytanie, klaster, intencja) |
| `run.py` | Automat: odpytuje silniki z API, liczy pokrycie, generuje CSV + Markdown |
| `results/<YYYY-MM>/` | Wyniki miesiąca: `report.csv`, `report.md`, `manual-checklist.md`, `raw/` |
| `KOSZTY_API.md` | Analiza dostępności i kosztu API — brama decyzyjna |

## Zasada nadrzędna: set zapytań jest STAŁY

Porównywalność miesiąc do miesiąca zależy wyłącznie od tego, że pytamy dokładnie o to samo.

- **Nie zmieniamy** brzmienia istniejących zapytań. Nigdy.
- Nowe zapytania **dopisujemy na końcu** z nowym `id` i datą w polu `added`. W raportach
  liczymy je osobno do czasu, aż uzbierają własną historię.
- Zapytania wycofane oznaczamy `"retired": "YYYY-MM"` zamiast usuwać — inaczej stare
  raporty przestają się dać odtworzyć.

## Silniki

| Silnik | Tryb | Uwaga |
|---|---|---|
| Perplexity (`sonar`) | automat (API) | Realny produkt AI-search z cytowaniami — najbliżej tego, co mierzymy |
| Gemini (`gemini-2.5-flash` + Google Search grounding) | automat (API) | **Przybliżenie** AI Overviews, nie to samo źródło. Traktować jako proxy, nie zamiennik |
| ChatGPT (z wyszukiwaniem) | ręcznie | Brak dostępnego API zwracającego cytowania w tym samym trybie |
| Google AI Overviews | ręcznie | Brak API. Blok AIO nie pojawia się dla każdego zapytania — to też jest wynik |

Automat i część ręczna używają **tego samego setu i tej samej tabeli**, więc wyniki
zestawiają się w jeden raport.

## Jak uruchomić

```bash
cd geo/llm-monitoring

python3 run.py --dry-run                    # plan, zero wywołań API
python3 run.py --checklist-only             # sama checklista ręczna
python3 run.py --engines gemini             # tylko Gemini
python3 run.py --engines perplexity,gemini  # pełny pomiar
python3 run.py --month 2026-09              # nadpisz etykietę miesiąca
```

Skrypt korzysta **wyłącznie z biblioteki standardowej** (`urllib`), bo systemowy
`python3` na tej maszynie nie ma `requests`. Nie wymaga venv.

Klucze czytane z `os.environ`, a jeśli ich tam nie ma — z głównego `.env` repo:

```
PERPLEXITY_API_KEY=...
GEMINI_API_KEY=...
```

Brak klucza = silnik pominięty z komunikatem, reszta pomiaru idzie dalej.
Przy zerze kluczy skrypt i tak generuje checklistę ręczną.

## Co skrypt zapisuje

Per zapytanie × silnik, zgodnie z Definition of Done:

| Kolumna CSV | Znaczenie |
|---|---|
| `data`, `silnik` | Kiedy i gdzie |
| `query_id`, `zapytanie`, `klaster`, `intencja` | Z `queries.json` |
| `genactiv_wymieniony` | Marka pada w treści odpowiedzi (łapie też `genaktiv`, `gen activ`, `geneactiv`, `genativ`) |
| `genactiv_zalinkowany` | W źródłach jest URL z `genactiv.pl` / `colostrum.pl` |
| `nasze_urle` | Które dokładnie URL-e zostały zacytowane |
| `konkurenci` | Wykryte kategorie: `colostrigen`, `immunolab`, `apteki`, `marketplace`, `portale-zdrowie` |
| `wszystkie_zrodla` | Pełna lista cytowanych URL-i |
| `blad` | Treść błędu, jeśli odpytanie padło |

`report.md` liczy z tego: pokrycie ogółem, per silnik, per klaster, top cytowane domeny,
udział konkurentów oraz **sekcję „Luki"** — zapytania bez GENACTIV wraz z tym, kto pojawił
się zamiast nas. To jest lista roboczo najważniejsza: mówi, co dopisać w treści.

Surowe odpowiedzi lądują w `raw/<silnik>_<id>.json` — bez nich nie da się później
zweryfikować, czy zmiana pokrycia to zmiana widoczności, czy zmiana zachowania modelu.

## Metodyka pomiaru ręcznego (ChatGPT, AI Overviews)

Generowana automatycznie do `results/<miesiąc>/manual-checklist.md`. Zasady:

1. **Nowa sesja / incognito**, bez zalogowania — personalizacja zaburza wynik.
2. **Lokalizacja Polska, język polski.** W ChatGPT włączone wyszukiwanie w sieci.
3. Zapytanie wklejane **dosłownie**, bez dopisków.
4. Brak bloku AI Overviews to też wynik — zapisujemy `brak AIO`, nie zostawiamy pustego pola.
5. **Cały pomiar ręczny robi jedna osoba tego samego dnia.** Rozbicie na kilka dni/osób
   psuje porównywalność bardziej niż opóźnienie pomiaru.

## Kadencja

| Kiedy | Co | Kto |
|---|---|---|
| 1.–3. dzień miesiąca | `run.py` na wszystkich dostępnych silnikach | CC (automat) |
| ten sam dzień | Checklista ręczna ChatGPT + AI Overviews | człowiek |
| po zebraniu obu | Przeniesienie wierszy ręcznych do `report.csv`, odczyt sekcji „Luki" | człowiek |
| kwartalnie | Przegląd setu: czy klastry nadal odpowiadają ofercie | człowiek |

## Ograniczenia — czytać przed interpretacją wyników

- **Odpowiedzi LLM są niedeterministyczne.** Nawet przy `temperature: 0` ten sam prompt
  potrafi dać inną listę źródeł. Pojedynczy pomiar to próbka, nie pomiar bezwzględny.
  Trend liczy się na przestrzeni miesięcy, nie z różnicy dwóch kolejnych odczytów.
- **Gemini grounding ≠ AI Overviews.** To inny system rankingowy. Nie raportować go jako
  „widoczność w AI Overviews" — od tego jest pomiar ręczny.
- **Gemini zwraca linki przez redirect** (`vertexaisearch.cloud.google.com`). `run.py`
  domyślnie je rozwija, żeby dało się powiedzieć, JAKI URL zacytowano. Wyłącznik: `--no-resolve`
  (szybciej, ale w CSV zostają nieczytelne linki pośrednie).
- **Detekcja marki jest tekstowa.** Wzmianka bez linku liczy się jako `wymieniony`, ale nie
  jako `zalinkowany` — to celowe rozróżnienie, bo ruch daje dopiero link.
- **Brak danych o pozycji i CTR** — do tego potrzebny jest Google Search Console, który nie
  jest jeszcze podpięty.

## Status setu zapytań

`queries.json` ma wersję **0.1-provisional**. Zapytania pokrywają pięć klastrów z definicji
zadania (wzdęcia, regularność, wybór błonnika, ferrytyna, wybór colostrum), ale pole
`priority` jest puste — priorytetyzacja wg realnego popytu wymaga Senuto.

**Blokada:** `senuto-mcp` nie jest skonfigurowany lokalnie. `SENUTO_API_KEY` nie istnieje
w głównym `.env`, a w `.mcp.json` siedzi niepodstawiony placeholder `__SENUTO_API_KEY__`.
Klucz istnieje wyłącznie jako zmienna środowiskowa na Railway (Senuto był integrowany
w commicie `ca84e28` tylko pod `genactiv-online`, nigdy pod lokalne Claude Code).

Sprawdzone zamienniki i dlaczego nie wystarczają:

- **Google Ads Keyword Planner** — `DEVELOPER_TOKEN_NOT_APPROVED`, token ma tylko explorer access.
- **Google Ads search terms (GAQL)** — działa, 109 fraz z ostatnich 90 dni, ale są w praktyce
  wyłącznie brandowe (`colostrum genactiv` 24 771 wyświetleń, `genactiv`, `fiberbiom`).
  Zero zapytań objawowych — kampanie są brandowe, więc to nie jest źródło popytu dla
  klastra objawowego.

Po odblokowaniu Senuto: uzupełnić `priority`, przestawić kolejność wg popytu, podbić wersję
do `1.0` i **od tego momentu set zamrozić**.

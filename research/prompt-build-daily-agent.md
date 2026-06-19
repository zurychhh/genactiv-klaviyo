# Prompt do Claude Code — zbuduj codziennego agenta operacyjnego

> Wklej całość do Claude Code w katalogu repo `genactiv-klaviyo`. Najpierw uzupełnij 3 zmienne na górze.

---

ZMIENNE (uzupełnij przed wklejeniem):
- ŚCIEŻKA_REPO = /Users/USER/projects/genactiv-klaviyo
- KANAŁ_ALERTÓW = Teams   # albo: Email
- MONDAY_BOARD = "Genactiv — Sprint Czerwiec 2026"

---

Jesteś tech-leadem tego repo. Zbuduj **codziennego agenta operacyjnego**, który rano bierze zadania z Monday na dany dzień, wykonuje je LOKALNIE w Claude Code (headless), eskaluje to co wymaga człowieka na {{KANAŁ_ALERTÓW}}, aktualizuje zadania w Monday i wysyła krótki raport. Pełna specyfikacja jest w `research/agent-codzienny-architektura.md` — trzymaj się jej. Konwencje repo i MCP są w `CLAUDE.md` i `.mcp.json`.

## Zakres do zbudowania (pliki)
1. `scripts/runner.sh` — punkt wejścia: tworzy `git worktree` (izolacja), odpala `claude -p` z `--mcp-config .mcp.json`, `--permission-mode acceptEdits`, zawężonym `--allowedTools` (Monday, shopify-extended, klaviyo, ga4, Bash, Read, Write, Edit), `--max-turns 60`, zapisuje log do `reports/daily/<data>.jsonl`, commituje artefakty, sprząta worktree. Bez `bypassPermissions`. Bez commitowania `.env`.
2. `scripts/orchestrator-prompt.md` — instrukcja agenta (6 kroków: pull → triage → eskalacja → egzekucja → update → raport). Logika dokładnie jak w sekcji 3 architektury.
3. `.claude/agents/task-runner.md` — subagent wykonujący POJEDYNCZE zadanie wg pola „Prompt Claude Code" z itemu; izolowany kontekst; zwraca status/artefakty/KPI/ryzyka.
4. `scripts/notify.sh` — wysyłka na {{KANAŁ_ALERTÓW}}. Dla Teams: Incoming Webhook (`$TEAMS_WEBHOOK_URL`). Dla Email: SMTP w Pythonie lub Gmail MCP. Dwie funkcje: `notify_block` (czego brakuje + linki) i `notify_report` (raport dnia).
5. `scripts/com.genactiv.dailyagent.plist` — launchd, `StartCalendarInterval` 07:00. **Nie ładuj go automatycznie** — tylko utwórz plik i opisz `launchctl load` w README.
6. `scripts/README-daily-agent.md` — jak uruchomić ręcznie, jak włączyć scheduler, jakie zmienne env.
7. `.env.example` — dopisz `TEAMS_WEBHOOK_URL` (lub zmienne SMTP/Gmail). Nie ruszaj `.env`.
8. `scripts/scaffold-sprint.py` — generuje drzewo folderów sprintu z `research/sprint-czerwiec-2026-tasks.csv` (patrz sekcja „Struktura folderów").

## Struktura folderów (TWARDE wymaganie)
Utwórz w katalogu głównym repo osobny folder sprintu, w nim podfolder per tydzień, a w nim podfolder per zadanie. Tam ląduje WSZYSTKO, co trafia do Monday (artefakty, treść update'ów, status):
```
sprint-2026-06/
├── W1/
│   ├── A1/   ├── A2/   ├── E1/   ├── B1/   ├── C1/   ├── D1/
│   │   ├── task.md              # metadane z arkusza: ID, tytuł, owner, priorytet, est, KPI, zależności, status, brama, DoD, „Prompt Claude Code”
│   │   ├── artefakty/           # pliki wyprodukowane przez zadanie (np. keyword-map.csv, seo-fix-plan.md, drafty, specyfikacje flow)
│   │   ├── monday-update-<data>.md   # DOKŁADNA treść tego, co poszło do Monday (status + komentarz + linki) — mirror 1:1
│   │   └── status.txt           # bieżący status (zsynchronizowany z Monday)
│   └── …
├── W2/ … W5/
└── INDEX.md                     # mapa: tydzień → zadanie → status → linki
```
Zasady:
- `scaffold-sprint.py` buduje całe drzewo i seeduje `task.md` z CSV (jedno źródło prawdy). Idempotentny — nie nadpisuje istniejących artefaktów.
- Każdy update do Monday agent zapisuje RÓWNIEŻ jako `monday-update-<data>.md` w folderze danego zadania (tożsamość treści).
- Artefakty zadania (pliki, raporty) trzymane są w jego `artefakty/`, a w komentarzu Monday są LINKI do nich (commit/ścieżka).
- `INDEX.md` aktualizowany po każdym runie.

## Logika triage (krok 2) — twardo wg kolumn Monday
Dla każdego itemu „na dziś" ustal stan startu:
- **BLOKADA_CZŁOWIEK** gdy `Brama ręczna = "Wymaga ręcznej interwencji przed startem"` LUB brak inputu wymienionego w `Definition of Done`.
- **BLOKADA_ZALEŻNOŚĆ** gdy którakolwiek pozycja z kolumny Dependency ≠ `Done`.
- **GOTOWE** w pozostałych przypadkach.

## Egzekucja + update (kroki 4–5)
- GOTOWE: wykonaj treść pola „Prompt Claude Code" przez subagent `task-runner`. Wszystkie produkowane pliki zapisuj do `sprint-2026-06/<tydzień>/<ID>/artefakty/`.
- Po wykonaniu ustaw status w Monday:
  - `Brama ręczna = "Weryfikacja ręczna przed Done"` → **`Czeka na weryfikację (CC done)`** (NIGDY samo `Done`),
  - brak bramki → **`Done`**.
  - Dodaj update/komentarz: co zrobiono + linki (commit/strona/raport) + KPI jeśli mierzalne.
  - Tę samą treść zapisz jako `sprint-2026-06/<tydzień>/<ID>/monday-update-<data>.md` (mirror 1:1) i zaktualizuj `status.txt` oraz `INDEX.md`.
- BLOKADA_*: nie wykonuj. Dla BLOKADA_CZŁOWIEK ustaw status `Wymaga ręcznej interwencji`, dorzuć do `notify_block` i zapisz `monday-update-<data>.md` z informacją czego brakuje.

## Guardrails (bezwzględne)
- Operacje destrukcyjne (bulk SEO, theme) zawsze najpierw **dry-run** + backup; bez akceptu nie zapisuj.
- **Zero auto-publikacji treści medycznych/YMYL** (A6/A7 zawsze BLOKADA_CZŁOWIEK).
- Sekrety/tokeny nigdy do logów ani do commitów. `.env` poza worktree.
- Gdy Monday MCP zwróci błąd autoryzacji (`MCP_AGENT_NOT_AUTHORIZED`) — zakończ run raportem „brak dostępu do Monday: admin musi włączyć Public Hosted MCP", nic nie wykonuj.

## Tryb pracy
- Pracuj przyrostowo, pokazuj diffy, NIE odpalaj schedulera ani realnych zapisów do Monday/Shopify dopóki nie przejdą testy.
- Najpierw zaimplementuj wszystko w **trybie suchym** (flaga `DRY_RUN=1` w `runner.sh`: agent tylko czyta Monday, symuluje egzekucję, drukuje co BY zrobił, wysyła testowe powiadomienie).
- Zapytaj mnie przed pierwszym uruchomieniem w trybie realnym (`DRY_RUN=0`).

## Kryteria akceptacji (przetestuj i pokaż wynik)
0. `python3 scripts/scaffold-sprint.py` — tworzy drzewo `sprint-2026-06/W*/[ID]/` z `task.md` per zadanie (z CSV). Idempotentne.
1. `DRY_RUN=1 bash scripts/runner.sh` — pobiera itemy „na dziś" z {{MONDAY_BOARD}}, wypisuje klasyfikację (GOTOWE / BLOKADA_CZŁOWIEK / BLOKADA_ZALEŻNOŚĆ) per item; w DRY_RUN zapisuje `monday-update-<data>.md` w folderach zadań (bez zapisu do Monday).
2. Symulacja BLOKADA_CZŁOWIEK → `notify_block` faktycznie dostarcza wiadomość na {{KANAŁ_ALERTÓW}} z linkami do itemów.
3. Symulacja GOTOWE → log pokazuje jaki status i komentarz BYŁBY ustawiony w Monday (w DRY_RUN bez zapisu).
4. Powstaje `reports/daily/<data>.md` z sekcjami ✅ / ⏸ / ⛔ i `notify_report` wysyła skrót.
5. `claude --help` — potwierdź, że użyte flagi (`-p`, `--mcp-config`, `--permission-mode`, `--allowedTools`, `--max-turns`, `--output-format`) istnieją w tej wersji; jeśli nie — dostosuj i wypisz różnice.

Na koniec: krótkie podsumowanie utworzonych plików + instrukcja włączenia schedulera + lista rzeczy, które muszę zrobić ręcznie (np. `TEAMS_WEBHOOK_URL`, włączenie Public Hosted MCP w Monday).

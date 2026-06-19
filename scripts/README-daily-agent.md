# Codzienny Agent Operacyjny Genactiv

Automatyczny agent, ktory codziennie rano pobiera zadania ze sprintu, triaguje je, wykonuje gotowe przez Claude Code headless z MCP, eskaluje blokady na Teams, i generuje raport.

## Architektura

```
macOS launchd (07:00)
    |
    v
runner.sh
    |-- git worktree (izolacja)
    |-- kopiuje .mcp.json, .env
    |
    v
claude -p (headless)
    |
    v
ORCHESTRATOR agent
    |-- 1. Pull zadan (Monday / fallback: task.md)
    |-- 2. Triage (GOTOWE / BLOKADA_CZLOWIEK / BLOKADA_ZALEZNOSC)
    |-- 3. Eskalacja (Teams webhook)
    |-- 4. Egzekucja (subagent task-runner per zadanie)
    |-- 5. Update Monday (status + komentarz)
    |-- 6. Raport dnia (reports/daily/ + Teams)
    |
    v
Commit artefaktow + cleanup worktree
```

## Prereqs

1. **Claude Code CLI** zainstalowane i zalogowane (`claude auth`)
2. **MCP serwery** skonfigurowane (`.mcp.json` — uruchom `./setup-claude.sh`)
3. **Python 3.10+** (dla scaffold-sprint.py)
4. **Git** z czystym working tree na branchu main

### Opcjonalne

- **Teams Webhook URL** — do powiadomien (`TEAMS_WEBHOOK_URL` w `.env`)
- **Monday MCP** — "Public Hosted MCP" wlaczone w Monday.com (admin)

## Setup

```bash
# 1. Upewnij sie ze .env i .mcp.json sa na miejscu
cp .env.example .env    # uzupelnij tokeny
./setup-claude.sh       # generuje .mcp.json

# 2. Dodaj TEAMS_WEBHOOK_URL do .env (opcjonalne)
# Teams → kanal → Workflows → "Post to a channel when a webhook request is received"
echo 'TEAMS_WEBHOOK_URL=https://...' >> .env

# 3. Scaffold drzewa sprintu
python3 scripts/scaffold-sprint.py

# 4. Sprawdz strukture
ls sprint-2026-06/W1/
```

## Uruchomienie reczne

```bash
# Dry run (domyslny, bezpieczny — NIE zapisuje do Monday/Shopify)
DRY_RUN=1 bash scripts/runner.sh

# Pelna egzekucja (zapisuje do Monday, wykonuje MCP)
DRY_RUN=0 bash scripts/runner.sh

# Z wiekszym budzetem
BUDGET=10 DRY_RUN=0 bash scripts/runner.sh
```

## Zmienne srodowiskowe

| Zmienna | Domyslna | Opis |
|---------|----------|------|
| `DRY_RUN` | `1` | `1` = symulacja, `0` = pelna egzekucja |
| `BUDGET` | `5` | Max koszt API w USD (`--max-budget-usd`) |
| `TEAMS_WEBHOOK_URL` | (puste) | Teams webhook — jesli puste, pomija powiadomienia |

Pozostale zmienne (Shopify, Klaviyo, GA4 itd.) ladowane z `.env` — patrz `.env.example`.

## Scheduler (launchd)

Plik `scripts/com.genactiv.dailyagent.plist` konfiguruje uruchomienie codziennie o 07:00.

```bash
# Skopiuj plist do LaunchAgents
cp scripts/com.genactiv.dailyagent.plist ~/Library/LaunchAgents/

# Zaladuj (uruchomi sie jutro o 07:00)
launchctl load ~/Library/LaunchAgents/com.genactiv.dailyagent.plist

# Sprawdz status
launchctl list | grep genactiv

# Wyladuj (wylacz scheduler)
launchctl unload ~/Library/LaunchAgents/com.genactiv.dailyagent.plist

# Logi
tail -f /tmp/genactiv-dailyagent.log
```

**WAZNE:** NIE laduj plist zanim nie przetestujesz recznie (`DRY_RUN=1 bash scripts/runner.sh`).

## Struktura plikow

```
scripts/
  scaffold-sprint.py       — generuje drzewo sprintu z CSV
  runner.sh                — punkt wejscia (worktree + claude headless)
  notify.sh                — powiadomienia Teams (block + report)
  com.genactiv.dailyagent.plist — scheduler macOS
  README-daily-agent.md    — ta dokumentacja

.claude/agents/
  orchestrator.md          — glowny agent sesji (6-krokowy cykl)
  task-runner.md           — subagent do egzekucji pojedynczego zadania

sprint-2026-06/            — drzewo sprintu (generowane przez scaffold-sprint.py)
  INDEX.md                 — spis tresci
  W1/A1/task.md            — definicja zadania
  W1/A1/artefakty/         — output agenta
  W1/A1/status.txt         — status (pending/done/failed)

reports/daily/             — raporty dzienne agenta
  2026-06-19.md            — raport dnia
  2026-06-19.jsonl         — surowy output Claude Code
```

## Przeplywy trybu DRY_RUN

### DRY_RUN=1 (domyslny)

1. Czyta zadania z Monday (lub task.md)
2. Wykonuje triage (loguje do reports/daily/)
3. **NIE** zapisuje statusow w Monday
4. **NIE** wykonuje operacji MCP (Shopify/Klaviyo)
5. Generuje raport z symulacja "co bylby zrobione"
6. Commituje lokalne pliki

### DRY_RUN=0

1. Pelny pull z Monday
2. Triage + eskalacja blokad (Teams)
3. Egzekucja zadan GOTOWE (MCP Shopify/Klaviyo/GA4)
4. Update statusow w Monday + komentarze
5. Raport dnia + Teams
6. Commit artefaktow

## Troubleshooting

### "claude CLI nie znalezione"
```bash
# Sprawdz PATH
which claude
# Jesli brak — zainstaluj lub dodaj do PATH
export PATH="/opt/homebrew/bin:$PATH"
```

### "Brak .mcp.json"
```bash
./setup-claude.sh
```

### Teams webhook nie dziala
```bash
# Test reczny
bash scripts/notify.sh report "Test wiadomosc"
# Sprawdz TEAMS_WEBHOOK_URL w .env
grep TEAMS_WEBHOOK_URL .env
```

### Worktree nie zostal usuniety
```bash
git worktree list
git worktree remove /tmp/genactiv-agent-YYYY-MM-DD --force
```

### Agent nie widzi Monday
1. Sprawdz czy "Public Hosted MCP" jest wlaczone w Monday.com (admin)
2. Sprawdz tokeny Monday w `.mcp.json`
3. Agent uzywa fallbacku: czyta zadania z sprint-2026-06/W*/*/task.md

## Rzeczy wymagajace recznej akcji

- [ ] Dodac `TEAMS_WEBHOOK_URL` do `.env`
- [ ] Wlaczyc "Public Hosted MCP" w Monday.com (panel admin)
- [ ] Przetestowac: `DRY_RUN=1 bash scripts/runner.sh`
- [ ] Dopiero potem: `launchctl load` plist
- [ ] Pierwszy run `DRY_RUN=0` po akceptacji wynikow dry run

# Codzienny agent operacyjny — architektura (Claude Code lokalnie + Monday)

**Rola:** orchestrator, który codziennie rano bierze zadania z Monday na dany dzień, wykonuje je lokalnie w Claude Code (tam jest MCP do Shopify/Klaviyo/GA4), eskaluje to, co wymaga człowieka (mail / Teams), aktualizuje zadania i wysyła krótki raport.

**Zasada nadrzędna:** silnikiem wykonawczym jest **Claude Code w środowisku lokalnym** (headless). Monday = źródło zadań + stan. Kanał powiadomień = mail i/lub Teams. Żadnych „deployów do produkcji" bez bramki ręcznej.

---

## 1. Architektura (high-level)

```
        ┌──────────── macOS launchd (codziennie 07:00) ─────────────┐
        │                                                          │
        ▼                                                          │
  runner.sh  ──►  git worktree (izolacja)  ──►  claude -p (headless, --mcp-config .mcp.json)
        │                                              │
        │                                              ▼
        │                                   ORCHESTRATOR (agent)
        │                                   1. pull zadań z Monday (dziś)
        │                                   2. TRIAGE (bramki/zależności/inputy)
        │                            ┌──────┴───────────────┐
        │                            ▼                       ▼
        │                 [potrzebny człowiek]        [brak przeszkód]
        │                  mail/Teams: czego           wykonaj zadanie
        │                  brakuje + link do itemu      (prompt z Monday,
        │                  → status „Wymaga ręcznej      MCP Shopify/Klaviyo…)
        │                    interwencji"                       │
        │                                                       ▼
        │                                          update itemu w Monday
        │                                          (status + komentarz + artefakty)
        │                                                       │
        ▼                                                       ▼
   commit logu  ◄───────────────  raport dnia (mail/Teams) ◄────┘
   reports/daily/RRRR-MM-DD.md
```

---

## 2. Komponenty

| # | Komponent | Czym jest | Uwaga |
|---|---|---|---|
| 1 | **Scheduler** | `launchd` na Macu (plist, `StartCalendarInterval`) | lokalnie, bo praca jest lokalna. Alternatywa: cron. NIE GitHub Actions (to chmura). |
| 2 | **Runner** | `runner.sh` — przygotowuje worktree, odpala Claude Code headless, loguje, commituje | jeden punkt wejścia |
| 3 | **Orchestrator** | agent Claude Code (prompt + `.claude/agents/`) | mózg: triage → exec → update → raport |
| 4 | **MCP connectors** | Monday, Shopify, Klaviyo, GA4 (z `.mcp.json`) | **Monday wymaga „Public Hosted MCP"** (obecnie zablokowane) |
| 5 | **Kanał powiadomień** | Teams Incoming Webhook (curl) i/lub e-mail (SMTP/Gmail MCP) | Teams webhook = najprościej, bez OAuth |
| 6 | **Stan + log** | `reports/daily/RRRR-MM-DD.md` w repo + statusy w Monday | audytowalność i idempotencja |

---

## 3. Przepływ dnia (dwie fazy w jednym runie)

**Faza A — Triage (zanim cokolwiek ruszy):**
Dla każdego zadania „na dziś" agent sprawdza warunki startu:
1. **Brama ręczna = „Wymaga ręcznej interwencji przed startem"** (A6, A7, D3, OPS2) → nie startuje sam.
2. **Status = „Zablokowane (zależność)"** i nie wszystkie zależności są `Done` → czeka.
3. **Brakujący input** (np. ceny do bundli, akcept medyczny treści, decyzja o apce) → eskalacja.

Jeśli którykolwiek warunek zachodzi → **mail/Teams**: lista „czego brakuje + dlaczego + link do itemu", a status itemu → `Wymaga ręcznej interwencji`. Te zadania **nie są wykonywane** w tym runie.

**Faza B — Egzekucja (zadania bez przeszkód):**
Dla zadań gotowych agent:
1. Czyta pole **„Prompt Claude Code"** z itemu i wykonuje (najlepiej **subagent per zadanie**, by izolować kontekst).
2. Respektuje guardrails z promptu (dry-run dla bulk SEO, backup przed zmianą theme, brak auto-publikacji treści medycznych).
3. Aktualizuje item w Monday:
   - `Brama ręczna = Weryfikacja przed Done` → status **`Czeka na weryfikację (CC done)`** (NIE `Done`),
   - brak bramki → **`Done`**,
   - dodaje **update/komentarz**: co zrobiono, linki do artefaktów (commit, strona, raport), KPI jeśli mierzalne.
4. Dorzuca pozycję do raportu dnia.

**Na koniec:** jeden **raport** (mail/Teams): ✅ zrobione, ⏸ czeka na człowieka (z czego konkretnie), ⛔ zablokowane zależnością, + link do `reports/daily/…md`.

> Taski odblokowane przez człowieka w ciągu dnia wskakują w **kolejnym** runie rano. Opcjonalnie: webhook z Monday („gdy status → Do zrobienia") odpala runner ponownie tego samego dnia (resume).

---

## 4. Mechanizm human-in-the-loop

Człowiek odblokowuje przez **zmianę w Monday** (jedno źródło prawdy), nie przez odpisywanie na maila:
- akcept/decyzja → ustaw status z `Wymaga ręcznej interwencji` na `Do zrobienia` (lub zaznacz kolumnę „Input gotowy"),
- weryfikacja outcome → z `Czeka na weryfikację (CC done)` na `Done`.

Powiadomienie mail/Teams zawiera **deep link** do itemu, żeby decyzja była jednym kliknięciem. (Czytanie odpowiedzi z maila/Teams jest możliwe, ale to dodatkowa złożoność — rekomendacja: decyzja w Monday.)

---

## 5. Code-ready fragmenty

### 5.1 launchd (macOS) — `~/Library/LaunchAgents/com.genactiv.dailyagent.plist`
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.genactiv.dailyagent</string>
  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>/Users/USER/projects/genactiv-klaviyo/scripts/runner.sh</string>
  </array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>7</integer><key>Minute</key><integer>0</integer></dict>
  <key>StandardOutPath</key><string>/tmp/genactiv-dailyagent.log</string>
  <key>StandardErrorPath</key><string>/tmp/genactiv-dailyagent.err</string>
</dict></plist>
```
`launchctl load ~/Library/LaunchAgents/com.genactiv.dailyagent.plist`

### 5.2 Runner — `scripts/runner.sh`
```bash
#!/usr/bin/env bash
set -euo pipefail
REPO="/Users/USER/projects/genactiv-klaviyo"
DAY=$(date +%F)
WT="/tmp/genactiv-agent-$DAY"

cd "$REPO"
git worktree add -f "$WT" HEAD          # izolacja: agent pracuje na kopii
cd "$WT"

# Headless Claude Code. allowedTools ogranicza ryzyko; permission-mode bez promptów.
claude -p "$(cat scripts/orchestrator-prompt.md)" \
  --mcp-config .mcp.json \
  --permission-mode acceptEdits \
  --allowedTools "mcp__monday__*,mcp__shopify-extended__*,mcp__klaviyo__*,mcp__ga4__*,Bash,Read,Write,Edit" \
  --max-turns 60 \
  --output-format stream-json > "reports/daily/$DAY.jsonl" || true

# Zatwierdź log/artefakty z powrotem do repo
git add -A && git commit -m "daily agent run $DAY" || true
git -C "$REPO" worktree remove "$WT" --force
```
> Wariant produkcyjny: zamiast `claude -p` użyj **Claude Agent SDK** (Python/TS) — pełna kontrola, subagenty, structured output, retry. `claude -p` jest szybkie na start.

### 5.3 Szkielet promptu orchestratora — `scripts/orchestrator-prompt.md`
```
Jesteś codziennym agentem operacyjnym Genactiv. Dziś: {{DATA}}.

KROK 1 — POBIERZ ZADANIA: z Monday (board „Sprint …") pobierz itemy, gdzie Daty obejmują dziś.
KROK 2 — TRIAGE: dla każdego itemu oznacz status startu:
  - BLOKADA_CZŁOWIEK jeśli Brama ręczna = „Wymaga ręcznej interwencji przed startem”
    LUB brakuje inputu wymienionego w Definition of Done.
  - BLOKADA_ZALEŻNOŚĆ jeśli któraś zależność (kolumna Dependency) ≠ Done.
  - GOTOWE w pozostałych przypadkach.
KROK 3 — ESKALACJA: dla BLOKADA_CZŁOWIEK wyślij JEDNĄ wiadomość (Teams/mail) z listą:
  [ID] zadanie — czego potrzeba od człowieka — link do itemu. Ustaw status itemu = „Wymaga ręcznej interwencji”.
KROK 4 — EGZEKUCJA: dla GOTOWE wykonaj treść z pola „Prompt Claude Code” (subagent per zadanie).
  Respektuj guardrails (dry-run, backup, brak auto-publikacji treści medycznych).
KROK 5 — UPDATE: w Monday ustaw status:
  - jeśli Brama ręczna = „Weryfikacja przed Done” → „Czeka na weryfikację (CC done)”,
  - inaczej → „Done”. Dodaj komentarz: co zrobiono + linki + KPI.
KROK 6 — RAPORT: zbuduj reports/daily/{{DATA}}.md i wyślij skrót (Teams/mail):
  ✅ zrobione | ⏸ czeka na człowieka (co) | ⛔ zależności | następny krok.
Nie wykonuj zadań oznaczonych BLOKADA_*. Loguj każdą decyzję.
```

### 5.4 Powiadomienie — Teams Incoming Webhook (najprostsze)
```bash
curl -s -H "Content-Type: application/json" -d '{
  "text": "🟡 Genactiv — wymagają człowieka (2026-06-..):\n• [D2] Bundle: zatwierdź ceny/marżę → <link>\n• [A6] Treści: QA medyczne 30 art. → <link>"
}' "$TEAMS_WEBHOOK_URL"
```
E-mail (alternatywa): mały skrypt SMTP w Pythonie albo Gmail MCP (`create_draft`/send) na wskazaną skrzynkę.

### 5.5 Subagent per zadanie — `.claude/agents/task-runner.md`
```
---
name: task-runner
description: Wykonuje pojedyncze zadanie sprintu wg promptu z Monday. Izolowany kontekst.
tools: mcp__shopify-extended__*, mcp__klaviyo__*, mcp__ga4__*, Bash, Read, Write, Edit
---
Dostajesz: ID zadania, Definition of Done, Prompt Claude Code. Wykonaj dokładnie prompt,
zweryfikuj DoD, zwróć: status (done/needs-verify/failed), artefakty (linki/commit), KPI, ryzyka.
```

---

## 6. Ryzyka i testy (guardrails)

| Ryzyko | Mitygacja |
|---|---|
| Agent wykona destrukcyjną akcję (bulk SEO, theme) | dry-run domyślnie + backup; `--allowedTools` bez `bypassPermissions`; worktree |
| Auto-publikacja treści medycznych (YMYL) | twarda bramka: A6/A7 zawsze BLOKADA_CZŁOWIEK, brak publikacji bez akceptu |
| Pętla/zawieszenie | `--max-turns`, timeout w launchd, alert gdy run > N min |
| Przeskoczenie weryfikacji (premature Done) | automatyzacja Monday (pkt 3 instrukcji importu) cofa Done bez weryfikacji |
| Sekrety w logach | nie loguj tokenów; log tylko statusy/artefakty; `.env` poza worktree commitem |
| Monday niedostępny | run kończy się raportem „brak dostępu", nic nie wykonuje |

**Testy przed włączeniem schedulera:** (1) run na 1 itemie testowym w trybie dry-run; (2) symulacja BLOKADA_CZŁOWIEK → czy przyszło Teams/mail; (3) symulacja GOTOWE → czy status i komentarz w Monday poprawne; (4) sprawdź raport dnia.

---

## 7. Kolejność wdrożenia

1. **Odblokuj Monday** („Public Hosted MCP") — bez tego agent nie czyta/nie pisze zadań. *(blokada krytyczna)*
2. Skonfiguruj kanał: **Teams Incoming Webhook** (5 min) lub SMTP/Gmail.
3. `scripts/runner.sh` + `orchestrator-prompt.md` + subagent `task-runner` → test ręczny (`bash runner.sh`).
4. Dodaj launchd (07:00) dopiero po udanym teście ręcznym.
5. (Opcjonalnie) webhook Monday → resume tego samego dnia po odblokowaniu przez człowieka.
6. (Opcjonalnie) migracja `claude -p` → **Agent SDK** dla produkcyjnej kontroli i retry.

> Wszystkie flagi Claude Code zweryfikuj pod swoją wersję (`claude --help`) — składnia headless/permission ewoluuje.

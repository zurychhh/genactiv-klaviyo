#!/usr/bin/env bash
# runner.sh — Entry point for Genactiv Daily Agent
#
# Usage:
#   DRY_RUN=1 bash scripts/runner.sh          # Dry run (default, safe)
#   DRY_RUN=0 bash scripts/runner.sh          # Full execution
#   BUDGET=2 bash scripts/runner.sh           # Custom budget (default: 5 USD)
#
# What it does:
#   1. Creates a git worktree for isolation
#   2. Copies .mcp.json (gitignored) into worktree
#   3. Runs Claude Code headless with orchestrator agent
#   4. Copies artifacts back to main repo
#   5. Commits results, cleans up worktree

set -euo pipefail

# ============================================
# Configuration
# ============================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$SCRIPT_DIR/.." && pwd)"
DAY=$(date +%F)
WT="/tmp/genactiv-agent-$DAY"
DRY_RUN="${DRY_RUN:-1}"
BUDGET="${BUDGET:-5}"
LOG_FILE="/tmp/genactiv-dailyagent-${DAY}.log"

# ============================================
# Logging
# ============================================
log() {
    echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "=== Genactiv Daily Agent — $DAY ==="
log "DRY_RUN=$DRY_RUN | BUDGET=$BUDGET USD"
log "Repo: $REPO"

# ============================================
# Pre-flight checks
# ============================================
if ! command -v claude &>/dev/null; then
    log "BLAD: claude CLI nie znalezione w PATH"
    exit 1
fi

if [[ ! -f "$REPO/.mcp.json" ]]; then
    log "OSTRZEZENIE: Brak .mcp.json — MCP serwery nie beda dostepne"
    log "Uruchom ./setup-claude.sh aby wygenerowac .mcp.json"
fi

# ============================================
# Load .env
# ============================================
if [[ -f "$REPO/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$REPO/.env"
    set +a
    log "Zaladowano .env"
fi

# ============================================
# Setup worktree
# ============================================
cd "$REPO"

# Cleanup stale worktree if exists
if [[ -d "$WT" ]]; then
    log "Usuwam stary worktree: $WT"
    git worktree remove "$WT" --force 2>/dev/null || rm -rf "$WT"
fi

log "Tworzenie worktree: $WT"
git worktree add -f "$WT" HEAD 2>&1 | tee -a "$LOG_FILE"
cd "$WT"

# Copy gitignored files needed by agent
if [[ -f "$REPO/.mcp.json" ]]; then
    cp "$REPO/.mcp.json" "$WT/.mcp.json"
    log "Skopiowano .mcp.json do worktree"
fi

if [[ -f "$REPO/.env" ]]; then
    cp "$REPO/.env" "$WT/.env"
    log "Skopiowano .env do worktree"
fi

# Ensure output directories exist
mkdir -p "$WT/reports/daily" "$WT/sprint-2026-06"

# ============================================
# Build prompt
# ============================================
PROMPT="Jestes codziennym agentem operacyjnym Genactiv. Dzis: ${DAY}.
DRY_RUN=${DRY_RUN}

Wykonaj pelny 6-krokowy cykl wg instrukcji z agenta orchestrator:
1. Pull zadan (Monday lub fallback: sprint-2026-06/W*/*/task.md)
2. Triage (GOTOWE / BLOKADA_CZLOWIEK / BLOKADA_ZALEZNOSC)
3. Eskalacja blokad (Teams via scripts/notify.sh)
4. Egzekucja zadan GOTOWE (subagent task-runner per zadanie)
5. Update Monday (jesli DRY_RUN=0)
6. Raport dnia: reports/daily/${DAY}.md + Teams

Pamietaj: DRY_RUN=${DRY_RUN}. Jesli 1 — czytaj, symuluj, pisz TYLKO lokalne pliki."

# ============================================
# Run Claude Code
# ============================================
ALLOWED_TOOLS="mcp__claude_ai_monday_com__*,mcp__shopify-extended__*,mcp__shopify-standard__*,mcp__klaviyo__*,mcp__klaviyo-segments__*,mcp__ga4__*,mcp__clarity__*,Bash,Read,Write,Edit,Glob,Grep,Task,WebFetch,WebSearch"

log "Uruchamiam Claude Code..."

# Check if --agent flag works with our agent
CLAUDE_CMD_ARGS=(
    -p "$PROMPT"
    --mcp-config .mcp.json
    --permission-mode acceptEdits
    --allowedTools "$ALLOWED_TOOLS"
    --max-budget-usd "$BUDGET"
    --output-format stream-json
)

# Try --agent first, fallback to --system-prompt
if claude agents 2>/dev/null | grep -q "orchestrator"; then
    CLAUDE_CMD_ARGS+=(--agent orchestrator)
    log "Uzyto: --agent orchestrator"
else
    # Fallback: load orchestrator.md as system prompt
    if [[ -f "$WT/.claude/agents/orchestrator.md" ]]; then
        ORCH_CONTENT=$(cat "$WT/.claude/agents/orchestrator.md")
        CLAUDE_CMD_ARGS+=(--append-system-prompt "$ORCH_CONTENT")
        log "Fallback: --append-system-prompt z orchestrator.md"
    else
        log "OSTRZEZENIE: Brak orchestrator.md — uzyto tylko promptu"
    fi
fi

# Execute
claude "${CLAUDE_CMD_ARGS[@]}" > "$WT/reports/daily/${DAY}.jsonl" 2>&1 || {
    log "Claude Code zakonczyl z bledem (kod: $?)"
}

log "Claude Code zakonczyl prace"

# ============================================
# Copy artifacts back to main repo
# ============================================
log "Kopiowanie artefaktow do glownego repo..."

# Reports
if [[ -d "$WT/reports/daily" ]]; then
    cp -r "$WT/reports/daily/"* "$REPO/reports/daily/" 2>/dev/null || true
fi

# Sprint directory
if [[ -d "$WT/sprint-2026-06" ]]; then
    cp -r "$WT/sprint-2026-06/"* "$REPO/sprint-2026-06/" 2>/dev/null || true
fi

# Research artifacts
if [[ -d "$WT/research" ]]; then
    cp -r "$WT/research/"* "$REPO/research/" 2>/dev/null || true
fi

# ============================================
# Commit results (in main repo)
# ============================================
cd "$REPO"

if [[ -n "$(git status --porcelain reports/ sprint-2026-06/ 2>/dev/null)" ]]; then
    log "Commitowanie wynikow..."
    git add reports/daily/ sprint-2026-06/ 2>/dev/null || true
    git commit -m "daily agent run $DAY (DRY_RUN=$DRY_RUN)" 2>/dev/null || true
    log "Commit utworzony"
else
    log "Brak zmian do commitowania"
fi

# ============================================
# Cleanup worktree
# ============================================
log "Czyszczenie worktree..."
git worktree remove "$WT" --force 2>/dev/null || {
    log "OSTRZEZENIE: Nie udalo sie usunac worktree $WT"
}

log "=== Zakonczono: $DAY ==="

#!/usr/bin/env bash
# notify.sh — Teams webhook notifications for Daily Agent
#
# Usage:
#   source scripts/notify.sh
#   notify_block "- [D2] Bundle: zatwierdz ceny"
#   notify_report "reports/daily/2026-06-19.md"
#
# Or directly:
#   bash scripts/notify.sh block "- [D2] Bundle: zatwierdz ceny"
#   bash scripts/notify.sh report "reports/daily/2026-06-19.md"
#
# Requires: TEAMS_WEBHOOK_URL env var (graceful skip if unset)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Load .env if present
if [[ -f "$REPO_ROOT/.env" ]]; then
    set -a
    # shellcheck disable=SC1091
    source "$REPO_ROOT/.env"
    set +a
fi

DAY=$(date +%F)

_check_webhook() {
    if [[ -z "${TEAMS_WEBHOOK_URL:-}" ]]; then
        echo "[notify] TEAMS_WEBHOOK_URL nie ustawiony — pomijam powiadomienie" >&2
        return 1
    fi
    return 0
}

_send_card() {
    local title="$1"
    local body="$2"
    local color="$3"

    # Teams Workflows webhooks require Adaptive Card format
    local payload
    payload=$(cat <<JSONEOF
{
    "type": "message",
    "attachments": [
        {
            "contentType": "application/vnd.microsoft.card.adaptive",
            "contentUrl": null,
            "content": {
                "\$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                "type": "AdaptiveCard",
                "version": "1.4",
                "body": [
                    {
                        "type": "TextBlock",
                        "text": "${title}",
                        "weight": "Bolder",
                        "size": "Medium",
                        "color": "${color}"
                    },
                    {
                        "type": "TextBlock",
                        "text": "${body}",
                        "wrap": true,
                        "spacing": "Medium"
                    },
                    {
                        "type": "TextBlock",
                        "text": "Genactiv Daily Agent — ${DAY}",
                        "isSubtle": true,
                        "size": "Small",
                        "spacing": "Medium"
                    }
                ]
            }
        }
    ]
}
JSONEOF
    )

    local http_code
    http_code=$(curl -s -o /dev/null -w "%{http_code}" \
        -H "Content-Type: application/json" \
        -d "$payload" \
        "$TEAMS_WEBHOOK_URL")

    if [[ "$http_code" =~ ^2 ]]; then
        echo "[notify] Wyslano do Teams (HTTP $http_code)"
    else
        echo "[notify] BLAD Teams webhook (HTTP $http_code)" >&2
    fi
}

notify_block() {
    # $1 — lista blokad (multiline string, kazda linia = 1 blokada)
    local blocks="${1:-(brak)}"
    _check_webhook || return 0

    _send_card \
        "Wymaga interwencji czlowieka" \
        "$blocks" \
        "Attention"
}

notify_report() {
    # $1 — sciezka do raportu dnia LUB tresc raportu
    local report_arg="${1:-}"
    local body

    if [[ -f "$report_arg" ]]; then
        # Czytaj plik, ogranicz do 2000 znakow (limit Adaptive Card)
        body=$(head -c 2000 "$report_arg")
    elif [[ -n "$report_arg" ]]; then
        body="$report_arg"
    else
        body="Raport dnia niedostepny."
    fi

    _check_webhook || return 0

    _send_card \
        "Raport dnia — ${DAY}" \
        "$body" \
        "Good"
}

# CLI mode: bash scripts/notify.sh <command> <arg>
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    cmd="${1:-}"
    arg="${2:-}"

    case "$cmd" in
        block)
            notify_block "$arg"
            ;;
        report)
            notify_report "$arg"
            ;;
        *)
            echo "Uzycie: bash scripts/notify.sh <block|report> <tresc|sciezka>"
            echo ""
            echo "  block  — wyslij liste blokad wymagajacych czlowieka"
            echo "  report — wyslij raport dnia (sciezka do .md lub tresc)"
            exit 1
            ;;
    esac
fi

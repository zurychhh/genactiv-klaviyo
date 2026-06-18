#!/usr/bin/env bash
set -euo pipefail

# GenActiv-Klaviyo — Setup Script
# Konfiguruje srodowisko: venv, npm, build, .mcp.json
#
# Uzycie:
#   chmod +x setup-claude.sh
#   ./setup-claude.sh

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}✓${NC} $1"; }
warn() { echo -e "  ${YELLOW}!${NC} $1"; }
fail() { echo -e "  ${RED}✗${NC} $1"; }

echo "============================================="
echo "  GenActiv-Klaviyo — Setup"
echo "============================================="
echo ""

# ------------------------------------------
# 1. Check requirements
# ------------------------------------------
echo "1) Sprawdzam wymagania..."

MISSING=0

if command -v node &>/dev/null; then
    NODE_VER=$(node -v | sed 's/v//')
    NODE_MAJOR=$(echo "$NODE_VER" | cut -d. -f1)
    if [ "$NODE_MAJOR" -ge 18 ]; then
        ok "Node.js $NODE_VER"
    else
        fail "Node.js $NODE_VER (wymagane >= 18)"
        MISSING=1
    fi
else
    fail "Node.js nie znaleziony (wymagane >= 18)"
    MISSING=1
fi

if command -v python3 &>/dev/null; then
    PY_VER=$(python3 --version | awk '{print $2}')
    ok "Python $PY_VER"
else
    fail "python3 nie znaleziony"
    MISSING=1
fi

if command -v npm &>/dev/null; then
    ok "npm $(npm -v)"
else
    fail "npm nie znaleziony"
    MISSING=1
fi

if [ "$MISSING" -eq 1 ]; then
    echo ""
    fail "Brakuje wymaganych narzedzi. Zainstaluj je i uruchom ponownie."
    exit 1
fi

echo ""

# ------------------------------------------
# 2. Root .env
# ------------------------------------------
echo "2) Plik .env (root — skrypty Python)..."

if [ -f .env ]; then
    ok ".env juz istnieje"
else
    if [ -f .env.example ]; then
        cp .env.example .env
        warn ".env skopiowany z .env.example — uzupelnij tokeny!"
    else
        warn "Brak .env.example — utworz .env recznie"
    fi
fi

echo ""

# ------------------------------------------
# 3. Python venv + dependencies
# ------------------------------------------
echo "3) Python venv..."

if [ ! -d venv ]; then
    python3 -m venv venv
    ok "Utworzono venv/"
else
    ok "venv/ juz istnieje"
fi

source venv/bin/activate
pip install --quiet --upgrade pip

# Root-level Python deps
pip install --quiet python-dotenv requests "fastmcp>=2.8.0,<3.0.0" 2>/dev/null && ok "pip: dotenv, requests" || warn "pip install czesciowo nie powiodl sie"

# Google Ads MCP deps
if [ -f google-ads-mcp/google-ads-mcp-server/requirements.txt ]; then
    pip install --quiet -r google-ads-mcp/google-ads-mcp-server/requirements.txt 2>/dev/null \
        && ok "pip: google-ads-mcp deps" \
        || warn "Google Ads MCP deps — czesciowo nie powiodlo sie"
fi

echo ""

# ------------------------------------------
# 4. genactiv-online (npm install)
# ------------------------------------------
echo "4) genactiv-online..."

if [ -d genactiv-online ]; then
    (cd genactiv-online && npm install --silent 2>/dev/null) && ok "npm install (genactiv-online)" || warn "npm install czesciowo nie powiodl sie"

    if [ ! -f genactiv-online/.env ] && [ -f genactiv-online/.env.example ]; then
        cp genactiv-online/.env.example genactiv-online/.env
        warn "genactiv-online/.env skopiowany z .env.example — uzupelnij tokeny!"
    fi
else
    warn "Katalog genactiv-online/ nie znaleziony"
fi

echo ""

# ------------------------------------------
# 5. shopify-mcp-extended (npm install + build)
# ------------------------------------------
echo "5) shopify-mcp-extended..."

if [ -d shopify-mcp-extended ]; then
    (cd shopify-mcp-extended && npm install --silent 2>/dev/null && npm run build 2>/dev/null) \
        && ok "npm install + build (shopify-mcp-extended)" \
        || warn "shopify-mcp-extended build nie powiodl sie"
else
    warn "Katalog shopify-mcp-extended/ nie znaleziony"
fi

echo ""

# ------------------------------------------
# 6. Generate .mcp.json from template + .env
# ------------------------------------------
echo "6) Generuje .mcp.json..."

if [ -f .mcp.json ]; then
    ok ".mcp.json juz istnieje — pomijam (usun recznie jesli chcesz wygenerowac od nowa)"
else
    if [ ! -f .mcp.json.example ]; then
        fail "Brak .mcp.json.example — nie moge wygenerowac"
    else
        # Helper: load var from .env files (root .env, then genactiv-online/.env as fallback)
        load_env_var() {
            local VAR_NAME="$1"
            local VAL=""
            if [ -f .env ]; then
                VAL=$(grep -E "^${VAR_NAME}=" .env 2>/dev/null | cut -d= -f2- || true)
            fi
            if [ -z "$VAL" ] && [ -f genactiv-online/.env ]; then
                VAL=$(grep -E "^${VAR_NAME}=" genactiv-online/.env 2>/dev/null | cut -d= -f2- || true)
            fi
            echo "$VAL"
        }

        # Load all tokens from .env files
        GOOGLE_ADS_DEV_TOKEN=$(load_env_var "GOOGLE_ADS_DEVELOPER_TOKEN")
        META_TOKEN=$(load_env_var "META_ACCESS_TOKEN")
        KLAVIYO_KEY=$(load_env_var "KLAVIYO_API_KEY")
        SHOPIFY_TOKEN=$(load_env_var "SHOPIFY_ACCESS_TOKEN")
        TIKTOK_APP=$(load_env_var "TIKTOK_APP_ID")
        TIKTOK_SEC=$(load_env_var "TIKTOK_SECRET")
        TIKTOK_TOK=$(load_env_var "TIKTOK_ACCESS_TOKEN")
        SENUTO_KEY=$(load_env_var "SENUTO_API_KEY")
        CLARITY_TOKEN=$(load_env_var "CLARITY_API_TOKEN")

        # Fallback to placeholders if not found
        [ -z "$GOOGLE_ADS_DEV_TOKEN" ] && GOOGLE_ADS_DEV_TOKEN="__GOOGLE_ADS_DEVELOPER_TOKEN__"
        [ -z "$META_TOKEN" ] && META_TOKEN="__META_ACCESS_TOKEN__"
        [ -z "$KLAVIYO_KEY" ] && KLAVIYO_KEY="__KLAVIYO_API_KEY__"
        [ -z "$SHOPIFY_TOKEN" ] && SHOPIFY_TOKEN="__SHOPIFY_ACCESS_TOKEN__"
        [ -z "$TIKTOK_APP" ] && TIKTOK_APP="__TIKTOK_APP_ID__"
        [ -z "$TIKTOK_SEC" ] && TIKTOK_SEC="__TIKTOK_SECRET__"
        [ -z "$TIKTOK_TOK" ] && TIKTOK_TOK="__TIKTOK_ACCESS_TOKEN__"
        [ -z "$SENUTO_KEY" ] && SENUTO_KEY="__SENUTO_API_KEY__"
        [ -z "$CLARITY_TOKEN" ] && CLARITY_TOKEN="__CLARITY_API_TOKEN__"

        HOME_DIR="$HOME"

        # Find analytics-mcp and meta-ads-mcp paths
        GA4_MCP_DIR=$(dirname "$(command -v analytics-mcp 2>/dev/null || echo "$HOME/.local/bin/analytics-mcp")")
        META_MCP_DIR=$(dirname "$(command -v meta-ads-mcp 2>/dev/null || echo "$HOME/.local/bin/meta-ads-mcp")")

        sed \
            -e "s|__PROJECT_DIR__|${PROJECT_DIR}|g" \
            -e "s|__HOME__|${HOME_DIR}|g" \
            -e "s|__GA4_MCP_PATH__|${GA4_MCP_DIR}|g" \
            -e "s|__META_ADS_MCP_PATH__|${META_MCP_DIR}|g" \
            -e "s|__GOOGLE_ADS_DEVELOPER_TOKEN__|${GOOGLE_ADS_DEV_TOKEN}|g" \
            -e "s|__META_ACCESS_TOKEN__|${META_TOKEN}|g" \
            -e "s|__KLAVIYO_API_KEY__|${KLAVIYO_KEY}|g" \
            -e "s|__SHOPIFY_ACCESS_TOKEN__|${SHOPIFY_TOKEN}|g" \
            -e "s|__TIKTOK_APP_ID__|${TIKTOK_APP}|g" \
            -e "s|__TIKTOK_SECRET__|${TIKTOK_SEC}|g" \
            -e "s|__TIKTOK_ACCESS_TOKEN__|${TIKTOK_TOK}|g" \
            -e "s|__SENUTO_API_KEY__|${SENUTO_KEY}|g" \
            -e "s|__CLARITY_API_TOKEN__|${CLARITY_TOKEN}|g" \
            .mcp.json.example > .mcp.json

        ok ".mcp.json wygenerowany z szablonu (10 serwerow MCP — z klaviyo-segments)"

        # Count remaining placeholders
        REMAINING=$(grep -c "__[A-Z_]*__" .mcp.json 2>/dev/null || echo "0")
        if [ "$REMAINING" -gt 0 ]; then
            warn "${REMAINING} placeholderow pozostalo w .mcp.json — uzupelnij tokeny w .env i usun .mcp.json, potem uruchom ponownie"
        else
            ok "Wszystkie tokeny uzupelnione z .env"
        fi
    fi
fi

echo ""

# ------------------------------------------
# Summary
# ------------------------------------------
echo "============================================="
echo "  Podsumowanie"
echo "============================================="
echo ""

# Checklist
[ -f .env ] && ok ".env (root)" || warn ".env (root) — brak, utworz z .env.example"
[ -f genactiv-online/.env ] && ok "genactiv-online/.env" || warn "genactiv-online/.env — brak"
[ -f .mcp.json ] && ok ".mcp.json" || warn ".mcp.json — brak"
[ -d venv ] && ok "Python venv/" || warn "Python venv/ — brak"
[ -d genactiv-online/node_modules ] && ok "genactiv-online/node_modules/" || warn "genactiv-online — npm install potrzebny"
[ -f shopify-mcp-extended/dist/index.js ] && ok "shopify-mcp-extended/dist/" || warn "shopify-mcp-extended — build potrzebny"

echo ""
echo "Nastepne kroki:"
echo "  1. Uzupelnij tokeny w .env i genactiv-online/.env"
echo "  2. Sprawdz .mcp.json (sciezki, tokeny)"
echo "  3. Uruchom: claude   (Claude Code automatycznie wczyta CLAUDE.md + .mcp.json)"
echo ""

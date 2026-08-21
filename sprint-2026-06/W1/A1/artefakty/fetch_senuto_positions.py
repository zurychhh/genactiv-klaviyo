#!/usr/bin/env python3
"""Pobiera pelne dane pozycji z Senuto (visibility_analysis) dla genactiv.pl i konkurentow.

Wynik: <artefakty>/senuto-raw/<domena>.json — lista rekordow ograniczona do pol,
ktorych uzywa build_keyword_map.py (keyword, position, url, searches, difficulty,
cpc, snippets, trends 12M). Skrypt jest read-only wobec Senuto i idempotentny —
ponowne uruchomienie nadpisuje cache swiezymi danymi.

    source venv/bin/activate
    python3 sprint-2026-06/W1/A1/artefakty/fetch_senuto_positions.py

Wymaga SENUTO_API_KEY w glownym .env. Klucz Senuto to JWT wazny 30 dni —
przy HTTP 404 z pustym body sprawdz najpierw date waznosci, nie sciezke endpointu.
"""

import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[4]
OUT_DIR = Path(__file__).resolve().parent / "senuto-raw"

API = "https://api.senuto.com/api/visibility_analysis/reports/positions/getData"
COUNTRY_ID = "200"          # Polska Base 2.0 (visibility_analysis; keywords_analysis uzywa "1")
FETCH_MODE = "topLevelDomain"
PAGE_LIMIT = 100            # twardy limit API — wyzsze wartosci sa ignorowane

DOMAINS = [
    "genactiv.pl",
    "genoscope.pl",          # realny konkurent #1 wg Senuto (134 wspolnych fraz)
    "colostrumactive.pl",
    "colostrumpolska.pl",
    "immunolab.com.pl",      # "Immuno Lab" z definicji zadania A1
]


def trim(row):
    st = row.get("statistics", {})
    return {
        "keyword": row.get("keyword"),
        "keyword_id": row.get("keyword_id"),
        "position": (st.get("position") or {}).get("current"),
        "url": (st.get("url") or {}).get("current"),
        "searches": (st.get("searches") or {}).get("current"),
        "difficulty": (st.get("difficulty") or {}).get("current"),
        "cpc": (st.get("cpc") or {}).get("current"),
        "snippets": (st.get("snippets") or {}).get("current") or [],
        "trends": (st.get("trends") or {}).get("history") or [],
    }


def fetch_domain(session, domain, api_key):
    rows, page = [], 1
    while True:
        resp = session.post(
            API,
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "domain": domain,
                "fetch_mode": FETCH_MODE,
                "country_id": COUNTRY_ID,
                "limit": PAGE_LIMIT,
                "page": page,
            },
            timeout=60,
        )
        if resp.status_code != 200:
            raise SystemExit(f"{domain} p{page}: HTTP {resp.status_code} — {resp.text[:200]}")
        payload = resp.json()
        if not payload.get("success"):
            raise SystemExit(f"{domain} p{page}: success=false — {resp.text[:200]}")
        rows.extend(trim(r) for r in (payload.get("data") or []))
        pg = payload.get("pagination") or {}
        print(f"  {domain}: strona {page}/{pg.get('page_count')} — lacznie {len(rows)}", flush=True)
        if not pg.get("has_next_page"):
            return rows
        page += 1
        time.sleep(0.3)


def main():
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("SENUTO_API_KEY")
    if not api_key:
        sys.exit("Brak SENUTO_API_KEY w .env")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    for domain in DOMAINS:
        print(f"Pobieram {domain}...", flush=True)
        rows = fetch_domain(session, domain, api_key)
        out = OUT_DIR / f"{domain}.json"
        out.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"  -> {out.name}: {len(rows)} fraz\n", flush=True)


if __name__ == "__main__":
    main()

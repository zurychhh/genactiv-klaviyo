#!/usr/bin/env python3
"""Uzupelnia `priority` w queries.json realnym popytem z Senuto Keyword Explorer.

Zapytania do LLM nie maja wlasnego wolumenu wyszukiwan — LLM to nie wyszukiwarka.
Priorytet liczymy wiec przez **frazy-proxy**: dla kazdego zapytania wskazujemy
1-2 frazy Google, ktore reprezentuja ten sam popyt, i bierzemy ich wolumen z
Senuto. Mapowanie proxy jest jawne (PROXY nizej) i zapisywane do queries.json,
zeby dalo sie je zakwestionowac przy kolejnym przegladzie setu.

`priority` = ranga 1..N wg wolumenu proxy (1 = najwiekszy popyt).

    source venv/bin/activate
    python3 geo/llm-monitoring/senuto_priority.py            # podglad
    python3 geo/llm-monitoring/senuto_priority.py --write    # zapis queries.json

Uwaga: `keywords_analysis` NIE przyjmuje country_id=200 — dla Polski jest tu `1`.
"""

import argparse
import json
import os
import sys
import time
import unicodedata
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = HERE / ".senuto-cache"
QUERIES = HERE / "queries.json"

KW_API = "https://api.senuto.com/api/keywords_analysis/reports/keywords/getKeywords"
KW_COUNTRY_ID = 1

# id zapytania -> frazy-proxy w Google reprezentujace ten sam popyt
PROXY = {
    "Q01": ["wzdęcia brzucha", "wzdęty brzuch"],
    "Q02": ["wzdęcia po jedzeniu", "co na wzdęcia"],
    "Q03": ["uczucie ciężkości w brzuchu", "wzdęty brzuch"],
    "Q04": ["błonnik na wzdęcia", "błonnik na zaparcia", "błonnik jelita"],
    "Q05": ["tabletki na wzdęcia", "leki na wzdęcia i gazy"],
    "Q06": ["wypróżnianie", "jak wypróżnić jelita"],
    "Q07": ["sposoby na zaparcia", "zaparcia"],
    "Q08": ["jak poprawić pracę jelit", "praca jelit"],
    "Q09": ["leniwe jelita", "leniwe jelita objawy"],
    "Q10": ["błonnik rozpuszczalny", "błonnik nierozpuszczalny"],
    "Q11": ["arabinogalaktan"],
    "Q12": ["błonnik w proszku", "najlepszy błonnik"],
    "Q13": ["ile błonnika dziennie"],
    "Q14": ["błonnik z kory modrzewia", "kora modrzewia"],
    "Q15": ["ferrytyna", "niska ferrytyna objawy"],
    "Q16": ["jak podnieść ferrytynę"],
    "Q17": ["laktoferyna"],
    "Q18": ["colostrum bovinum", "jakie colostrum wybrać"],
    "Q19": ["colostrum w proszku", "colostrum kapsułki"],
    "Q20": ["colostrum dla dorosłych", "colostrum na co pomaga"],
}


def fold(text):
    nfkd = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def fetch(session, api_key, seed, match_mode):
    cache = CACHE / f"{match_mode}--{fold(seed).replace(' ', '-')}.json"
    if cache.exists():
        return json.loads(cache.read_text(encoding="utf-8"))
    resp = session.post(
        KW_API,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "offset": 0, "page": 1, "limit": 100,
            "filtering": [{"filters": []}],
            "parameters": [{"data_fetch_mode": "keyword", "value": [seed]}],
            "country_id": KW_COUNTRY_ID,
            "match_mode": match_mode,
        },
        timeout=60,
    )
    if resp.status_code != 200 or not resp.json().get("success"):
        raise SystemExit(f"Senuto '{seed}': HTTP {resp.status_code} — {resp.text[:200]}")
    rows = resp.json().get("data") or []
    CACHE.mkdir(exist_ok=True)
    cache.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(0.3)
    return rows


CLUSTER_TOP_N = 20


def volume_for(session, api_key, phrase):
    """(popyt klastra, najsilniejsza fraza, liczba fraz).

    Senuto Keyword Explorer nie zwraca samego seeda jako rekordu (np. dla 'ferrytyna'
    dostajemy 'ferrytyna co to', 'ferrytyna normy'..., ale nie 'ferrytyna'), wiec
    pojedyncza fraza-head jest zawodna jako miara. Bierzemy sume wolumenow TOP-20
    fraz zawierajacych wszystkie slowa proxy — to popyt calego klastra, czyli to,
    co realnie stoi za jednym zapytaniem do LLM.
    """
    words = fold(phrase).split()
    for mode in ("narrow", "wide"):
        rows = fetch(session, api_key, phrase, mode)
        cands = [r for r in rows if all(w in fold(r.get("keyword")) for w in words)]
        if cands:
            cands.sort(key=lambda r: -(r.get("searches") or 0))
            top = cands[:CLUSTER_TOP_N]
            return sum(r.get("searches") or 0 for r in top), top[0]["keyword"], len(top)
    return 0, "", 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="zapisz queries.json")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("SENUTO_API_KEY")
    if not api_key:
        sys.exit("Brak SENUTO_API_KEY w .env")

    doc = json.loads(QUERIES.read_text(encoding="utf-8"))
    session = requests.Session()

    for q in doc["queries"]:
        proxies = PROXY.get(q["id"], [])
        if not proxies:
            sys.exit(f"Brak mapowania proxy dla {q['id']} — uzupelnij PROXY")
        scored = [volume_for(session, api_key, p) for p in proxies]
        vol, matched, n = max(scored, key=lambda t: t[0])
        q["demand_volume"] = vol
        q["demand_keywords"] = n
        q["demand_proxy_kw"] = matched or proxies[0]

    ranked = sorted(doc["queries"], key=lambda q: -q["demand_volume"])
    for rank, q in enumerate(ranked, 1):
        q["priority"] = rank
    doc["queries"] = ranked

    for q in ranked:
        print(f"  {q['priority']:>2}. {q['id']} {q['query'][:48]:50} "
              f"{q['demand_volume']:>6}/mc  ({q['demand_proxy_kw']})")

    if not args.write:
        print("\n(podglad — uruchom z --write, zeby zapisac)")
        return

    doc["_meta"]["version"] = "1.0"
    doc["_meta"]["status"] = "ZAMROZONY — set fraz nie zmienia sie miedzy pomiarami"
    doc["_meta"].pop("blocker", None)
    doc["_meta"]["priority_frozen"] = "2026-08-17"
    doc["_meta"]["priority_method"] = (
        "priority = ranga 1..N wg popytu klastra (1 = najwiekszy). Zapytania do LLM nie maja "
        "wlasnego wolumenu wyszukiwan, wiec dla kazdego wskazano frazy-proxy w Google "
        "(stala PROXY w geo/llm-monitoring/senuto_priority.py). demand_volume = suma "
        "miesiecznych wyszukiwan TOP-20 fraz zawierajacych wszystkie slowa proxy "
        "(Senuto Keyword Explorer, country_id=1, snapshot 2026-08-17); demand_proxy_kw = "
        "najsilniejsza fraza klastra, demand_keywords = ile fraz zlozylo sie na sume."
    )
    QUERIES.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"\nZapisano {QUERIES} — wersja {doc['_meta']['version']}")


if __name__ == "__main__":
    main()

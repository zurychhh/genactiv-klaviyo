"""KROK 1 — tworzy w Klaviyo segmenty-SYGNALY (surowe, celowo nakladajace sie).

To NIE sa segmenty docelowe. To material wejsciowy: kazdy odpowiada jednemu
sygnalowi (wizyta na LP albo kontakt z grupa produktowa). MECE powstaje
dopiero w kroku 2, przez priorytet.

Uzycie:
    python3 klaviyo-mcp/persona_step1_signals.py            # dry-run: pokazuje co zrobi
    python3 klaviyo-mcp/persona_step1_signals.py --live     # tworzy segmenty
    python3 klaviyo-mcp/persona_step1_signals.py --counts   # dolicza liczebnosci

Idempotentny: segment o istniejacej nazwie nie jest tworzony drugi raz.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import persona_lib as K            # noqa: E402
from persona_config import (       # noqa: E402
    PERSONAS, PRODUCT_SIGNALS, LP_DAYS, VIEW_DAYS)

PREFIX_LP = "SYG | LP "
PREFIX_PROD = "SYG | PRODUKT "
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "persona_signals.json")


def lp_definition(path: str) -> list[dict]:
    return [{"conditions": [K.cond_lp_visit(path, LP_DAYS)]}]


def product_definition(sku_frags: list[str], url_frags: list[str]) -> list[dict]:
    """Jedna grupa = OR wszystkich sygnalow produktowych (zakup LUB obejrzenie)."""
    conds = [K.cond_ordered_sku(s) for s in sku_frags]
    conds += [K.cond_viewed_url(u, VIEW_DAYS) for u in url_frags]
    return [{"conditions": conds}]


def planned() -> list[dict]:
    plan = []
    for p in PERSONAS:
        if p.get("lp"):
            plan.append({"kind": "lp", "key": p["key"],
                         "name": PREFIX_LP + p["key"],
                         "groups": lp_definition(p["lp"])})
    for key, sig in PRODUCT_SIGNALS.items():
        plan.append({"kind": "produkt", "key": key,
                     "name": PREFIX_PROD + key,
                     "groups": product_definition(sig["sku"], sig["url"])})
    return plan


def main() -> None:
    live = "--live" in sys.argv
    counts_only = "--counts" in sys.argv
    plan = planned()

    existing = {s["attributes"]["name"]: s["id"] for s in K.list_segments()}
    state = {}
    if os.path.exists(STATE):
        state = json.load(open(STATE))

    if counts_only:
        ids = {name: sid for name, sid in existing.items()
               if name.startswith(("SYG | LP ", "SYG | PRODUKT "))}
        print(f"Liczebnosci {len(ids)} segmentow-sygnalow (czekam na przeliczenie)...")
        counts = K.wait_until_ready(list(ids.values()))
        for name, sid in sorted(ids.items()):
            print(f"{counts.get(sid, -1):>7}  {name}   ({sid})")
        return

    print(f"{'TRYB LIVE' if live else 'DRY-RUN (dodaj --live aby utworzyc)'}\n")
    for item in plan:
        name = item["name"]
        n_cond = sum(len(g["conditions"]) for g in item["groups"])
        if name in existing:
            print(f"  ISTNIEJE  {name}  -> {existing[name]}")
            state[item["key"] + ":" + item["kind"]] = existing[name]
            continue
        print(f"  UTWORZ    {name}  ({n_cond} warunkow)")
        if live:
            r = K.create_segment(name, item["groups"])
            if r.get("_error"):
                print(f"      BLAD: {json.dumps(r['detail'], ensure_ascii=False)[:300]}")
                continue
            sid = r["data"]["id"]
            state[item["key"] + ":" + item["kind"]] = sid
            print(f"      -> {sid}")

    if live:
        json.dump(state, open(STATE, "w"), indent=2, ensure_ascii=False)
        print(f"\nZapisano mape ID: {STATE}")
    print(f"\nRazem w planie: {len(plan)} segmentow-sygnalow.")


if __name__ == "__main__":
    main()

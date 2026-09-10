"""KROK 3 — tworzy docelowe segmenty MECE oparte o wlasciwosc profilu.

Kazdy segment to jeden warunek: `persona_lp equals <klucz>`. Rozlacznosc jest
gwarantowana strukturalnie (wlasciwosc ma dokladnie jedna wartosc), a nie
algebra warunkow — Klaviyo API nie pozwala wykluczac segmentu z segmentu
(`group_ids` przyjmuje tylko listy, nie segmenty), wiec inaczej sie nie da.

Wyczerpanie bazy domyka ostatni segment: `persona_lp is not set`.

Uzycie:
    python3 klaviyo-mcp/persona_step3_segments.py            # dry-run
    python3 klaviyo-mcp/persona_step3_segments.py --live     # tworzy segmenty
    python3 klaviyo-mcp/persona_step3_segments.py --counts   # kontrola MECE
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import persona_lib as K            # noqa: E402
from persona_config import ALL_BUCKETS, PROPERTY  # noqa: E402

# Klaviyo wymaga, by wlasciwosci NIESTANDARDOWE byly adresowane w formie
# properties['nazwa']. Sama nazwa (jak przy wbudowanych `first_name`, `email`)
# daje 400: "All custom profile properties must be of the form:
# properties['property name']".
PROP_REF = f"properties['{PROPERTY}']"

PREFIX = "PERSONA | "
BEZ_SYGNALU = PREFIX + "11 REZ | Bez sygnału"
STATE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "persona_segments.json")


def prop_equals(value: str) -> list[dict]:
    return [{"conditions": [{"type": "profile-property", "property": PROP_REF,
                             "filter": {"type": "string", "operator": "equals",
                                        "value": value}}]}]


def prop_not_set() -> list[dict]:
    return [{"conditions": [{"type": "profile-property", "property": PROP_REF,
                             "filter": {"type": "existence", "operator": "not-set"}}]}]


def planned() -> list[dict]:
    plan = [{"name": f"{PREFIX}{b['prio']:02d} {b['name']}", "groups": prop_equals(b["key"])}
            for b in sorted(ALL_BUCKETS, key=lambda x: x["prio"])]
    plan.append({"name": BEZ_SYGNALU, "groups": prop_not_set()})
    return plan


def main() -> None:
    live = "--live" in sys.argv
    existing = {s["attributes"]["name"]: s["id"] for s in K.list_segments()}

    if "--counts" in sys.argv:
        ids = {n: i for n, i in existing.items() if n.startswith(PREFIX)}
        counts = K.wait_until_ready(list(ids.values()))
        total = 0
        print(f"{'LICZBA':>9}  SEGMENT")
        for name, sid in sorted(ids.items()):
            c = counts.get(sid, -1)
            total += max(c, 0)
            print(f"{c:>9,}".replace(",", " ") + f"  {name}")
        baza = [i for n, i in existing.items() if n.startswith("TECH | Cała baza")]
        print("-" * 60)
        print(f"{total:>9,}".replace(",", " ") + "  SUMA SEGMENTOW MECE")
        if baza:
            b = K.segment_count(baza[0])
            print(f"{b:>9,}".replace(",", " ") + "  CALA BAZA (mianownik)")
            print(f"\nKONTROLA: {'OK — suma = baza' if b == total else f'ROZJAZD {total - b:+,}'}")
        return

    print(f"{'TRYB LIVE' if live else 'DRY-RUN (dodaj --live)'}\n")
    state = {}
    for item in planned():
        if item["name"] in existing:
            print(f"  ISTNIEJE  {item['name']}")
            state[item["name"]] = existing[item["name"]]
            continue
        print(f"  UTWORZ    {item['name']}")
        if live:
            r = K.create_segment(item["name"], item["groups"])
            if r.get("_error"):
                print(f"      BLAD: {json.dumps(r['detail'], ensure_ascii=False)[:300]}")
                continue
            state[item["name"]] = r["data"]["id"]
            print(f"      -> {r['data']['id']}")
    if live:
        json.dump(state, open(STATE, "w"), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()

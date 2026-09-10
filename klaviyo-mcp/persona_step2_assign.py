"""KROK 2 — liczy przypisanie MECE i (opcjonalnie) zapisuje je do Klaviyo.

Logika przypisania — kazdy profil dostaje DOKLADNIE JEDNA wartosc:

  WARSTWA 1 (silniejsza): wizyta na landing page'u.
      Idziemy po personach rosnaco wg `prio`; pierwsze trafienie wygrywa.
      Uzasadnienie: wejscie na LP to zadeklarowany, swiezy i konkretny problem.
      To jedyny sygnal rozrozniajacy persony dzielace ten sam produkt.

  WARSTWA 2 (slabsza): kontakt z grupa produktowa (zakup calosc historii
      albo obejrzenie karty w 365 dni). Stosowana tylko do profili, ktore
      nie trafily w zadne LP, i tylko dla grup produktowych jednoznacznie
      wskazujacych jedna persone.

  BRAK — profil bez zadnego sygnalu nie dostaje wlasciwosci. Segment
      "persona_lp is not set" domyka podzial na cala baze.

Uzycie:
    python3 klaviyo-mcp/persona_step2_assign.py            # tylko analiza (dry-run)
    python3 klaviyo-mcp/persona_step2_assign.py --live     # + zapis wlasciwosci
"""
import collections
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import persona_lib as K            # noqa: E402
from persona_config import (       # noqa: E402
    PERSONAS, ALL_BUCKETS, PROPERTY, PROPERTY_SOURCE, PROPERTY_DATE)

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "persona_signals.json")
CACHE = os.path.join(HERE, "persona_members_cache.json")
OUT_CSV = os.path.join(os.path.dirname(HERE), "reports", "persony-lp-przypisanie.csv")
RUN_DATE = time.strftime("%Y-%m-%d")

BUCKET_BY_KEY = {b["key"]: b for b in ALL_BUCKETS}


def load_members(refresh: bool = False) -> dict[str, list[str]]:
    """Czlonkostwo kazdego segmentu-sygnalu. Cache na dysku — pobranie trwa kilka minut."""
    if os.path.exists(CACHE) and not refresh:
        return json.load(open(CACHE))
    state = json.load(open(STATE))
    members = {}
    for key, sid in state.items():
        ids = K.segment_profile_ids(sid)
        members[key] = sorted(ids)
        print(f"  pobrano {len(ids):>6}  {key}  ({sid})", flush=True)
    json.dump(members, open(CACHE, "w"))
    return members


def assign(members: dict[str, list[str]]) -> dict[str, tuple[str, str]]:
    """Zwraca {profile_id: (klucz_persony, zrodlo)}. Pierwsze trafienie wygrywa."""
    result: dict[str, tuple[str, str]] = {}

    # WARSTWA 1 — LP, persony rosnaco wg priorytetu
    for p in sorted(PERSONAS, key=lambda x: x["prio"]):
        for pid in members.get(p["key"] + ":lp", []):
            result.setdefault(pid, (p["key"], "lp"))

    # WARSTWA 2 — produkt. Kubelek moze byc zasilany sygnalem o innej nazwie
    # (np. persona `regularnosc` bierze sygnal `rez_fiberbiom`).
    for b in sorted(ALL_BUCKETS, key=lambda x: x["prio"]):
        sig = b.get("produkt")
        if not sig:
            continue
        for pid in members.get(sig + ":produkt", []):
            result.setdefault(pid, (b["key"], "produkt"))

    return result


def report(members: dict, result: dict) -> None:
    per_bucket = collections.Counter(k for k, _ in result.values())
    per_source = collections.Counter((k, s) for k, s in result.values())
    universe = set()
    for ids in members.values():
        universe |= set(ids)

    print(f"\n{'='*78}")
    print(f"PROFILE Z JAKIMKOLWIEK SYGNALEM: {len(universe):,}".replace(",", " "))
    print(f"PRZYPISANE:                      {len(result):,}".replace(",", " "))
    print(f"{'='*78}")
    print(f"{'PRIO':<5} {'SEGMENT':<42} {'RAZEM':>8} {'z LP':>7} {'z produktu':>11}")
    print("-" * 78)
    total = 0
    for b in sorted(ALL_BUCKETS, key=lambda x: x["prio"]):
        n = per_bucket.get(b["key"], 0)
        total += n
        print(f"{b['prio']:<5} {b['name']:<42} {n:>8,} {per_source.get((b['key'],'lp'),0):>7,}"
              f" {per_source.get((b['key'],'produkt'),0):>11,}".replace(",", " "))
    print("-" * 78)
    print(f"{'':<5} {'RAZEM PRZYPISANYCH':<42} {total:>8,}".replace(",", " "))
    assert total == len(result), "rozjazd sumy — przypisanie nie jest rozlaczne!"

    baza = int(os.environ.get("BAZA_PROFILI", "39065"))
    bez = baza - len(result)
    print(f"{'':<5} {'REZ | Bez sygnalu (persona_lp not set)':<42} {bez:>8,}".replace(",", " "))
    print("=" * 78)
    print(f"{'':<5} {'SUMA = CALA BAZA':<42} {baza:>8,}".replace(",", " "))
    print("\nKONTROLA MECE:")
    print("  - rozlacznosc: kazdy profil ma jedna wartosc `persona_lp` (pierwsze")
    print("    trafienie wygrywa, setdefault nie nadpisuje) -> zbiory sa parami rozlaczne")
    print(f"  - wyczerpanie: {len(result):,} przypisanych + {bez:,} bez sygnalu = {baza:,}"
          .replace(",", " "))

    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["prio", "klucz", "segment", "razem", "z_lp", "z_produktu", "opis"])
        for b in sorted(ALL_BUCKETS, key=lambda x: x["prio"]):
            w.writerow([b["prio"], b["key"], b["name"], per_bucket.get(b["key"], 0),
                        per_source.get((b["key"], "lp"), 0),
                        per_source.get((b["key"], "produkt"), 0), b["opis"]])
    print(f"CSV: {OUT_CSV}")


def write_properties(result: dict[str, tuple[str, str]]) -> None:
    """Bulk import — wlasciwosci profilu. Paczki po 3000, tylko `properties`."""
    by_value = collections.defaultdict(list)
    for pid, (key, src) in result.items():
        by_value[(key, src)].append(pid)

    batch, sent, failed = [], 0, 0
    def flush():
        nonlocal batch, sent, failed
        if not batch:
            return
        body = {"data": {"type": "profile-bulk-import-job",
                         "attributes": {"profiles": {"data": batch}}}}
        r = K.request("POST", "/profile-bulk-import-jobs", body)
        if r.get("_error"):
            failed += len(batch)
            print(f"    BLAD paczki ({len(batch)}): "
                  f"{json.dumps(r['detail'], ensure_ascii=False)[:400]}")
        else:
            sent += len(batch)
            print(f"    wyslano {sent:,}".replace(",", " "), flush=True)
        batch = []
        time.sleep(1.0)

    for (key, src), pids in by_value.items():
        for pid in pids:
            batch.append({"type": "profile", "id": pid, "attributes": {"properties": {
                PROPERTY: key, PROPERTY_SOURCE: src, PROPERTY_DATE: RUN_DATE}}})
            if len(batch) >= 3000:
                flush()
    flush()
    print(f"\nZapisano: {sent:,} profili, bledy: {failed:,}".replace(",", " "))


def main() -> None:
    live = "--live" in sys.argv
    refresh = "--refresh" in sys.argv
    print("Pobieram czlonkostwo segmentow-sygnalow"
          + (" (cache)" if os.path.exists(CACHE) and not refresh else " — kilka minut..."))
    members = load_members(refresh)
    result = assign(members)
    report(members, result)
    if live:
        print("\nZAPIS wlasciwosci do Klaviyo...")
        write_properties(result)
    else:
        print("\n(dry-run — nic nie zapisano; dodaj --live aby zapisac wlasciwosci)")


if __name__ == "__main__":
    main()

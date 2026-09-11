"""KROK 4 — przyrostowe domykanie person. Uruchamiany czesto (cron/Actions).

Po co: krok 2 przelicza cala baze (~15 min, 55 tys. rekordow). Do biezacego
domykania to za wolno i za drogo. Ten skrypt pobiera z segmentow-SYGNALOW
WYLACZNIE profile, ktore dolaczyly od ostatniego uruchomienia
(filtr `joined_group_at`), i zapisuje tylko rzeczywiste zmiany.

Regula (nigdy nie degraduje przypisania):
  1. Sygnal LP bije kazdy sygnal produktowy.
  2. Wsrod sygnalow tego samego rodzaju wygrywa nizszy `prio`.
  3. Profil z przypisaniem ze zrodla `lp` nie zostanie nadpisany sygnalem
     produktowym — nawet o wyzszym priorytecie.

Uzycie:
    python3 klaviyo-mcp/persona_step4_incremental.py            # dry-run
    python3 klaviyo-mcp/persona_step4_incremental.py --live
    python3 klaviyo-mcp/persona_step4_incremental.py --live --since 2026-09-01T00:00:00Z

Pierwsze uruchomienie bez `--since` i bez pliku stanu bierze ostatnia dobe.
"""
import datetime as dt
import json
import os
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import persona_lib as K            # noqa: E402
from persona_config import (       # noqa: E402
    ALL_BUCKETS, PROPERTY, PROPERTY_SOURCE, PROPERTY_DATE)

HERE = os.path.dirname(os.path.abspath(__file__))
SIGNALS = os.path.join(HERE, "persona_signals.json")
STATE = os.path.join(HERE, "persona_incremental_state.json")

PRIO = {b["key"]: b["prio"] for b in ALL_BUCKETS}
# klucz sygnalu produktowego -> kubelek docelowy (np. rez_fiberbiom -> regularnosc)
PROD_TO_BUCKET = {b["produkt"]: b["key"] for b in ALL_BUCKETS if b.get("produkt")}


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def since_default() -> str:
    return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).strftime(
        "%Y-%m-%dT%H:%M:%SZ")


def new_members(seg_id: str, since: str) -> list[str]:
    """Profile, ktore dolaczyly do segmentu po `since`."""
    ids, cursor = [], None
    while True:
        r = K.request("GET", f"/segments/{seg_id}/profiles", params={
            "page[size]": 100, "page[cursor]": cursor,
            "filter": f"greater-than(joined_group_at,{since})",
            "fields[profile]": "email"})
        if r.get("_error"):
            print(f"    BLAD {seg_id}: {json.dumps(r['detail'], ensure_ascii=False)[:200]}")
            return ids
        ids += [p["id"] for p in r["data"]]
        nxt = r.get("links", {}).get("next")
        if not nxt:
            return ids
        cursor = urllib.parse.parse_qs(urllib.parse.urlparse(nxt).query)["page[cursor]"][0]
        time.sleep(0.15)


def current_assignments(pids: list[str]) -> dict[str, tuple[str | None, str | None]]:
    """{profile_id: (persona_lp, persona_lp_zrodlo)} — paczkami po 50 ID."""
    out = {}
    for i in range(0, len(pids), 50):
        chunk = pids[i:i + 50]
        flt = "any(id,[" + ",".join(f'"{p}"' for p in chunk) + "])"
        r = K.request("GET", "/profiles", params={
            "filter": flt, "page[size]": 100, "fields[profile]": "properties"})
        if r.get("_error"):
            print(f"    BLAD odczytu profili: "
                  f"{json.dumps(r['detail'], ensure_ascii=False)[:200]}")
            continue
        for p in r["data"]:
            props = p["attributes"].get("properties") or {}
            out[p["id"]] = (props.get(PROPERTY), props.get(PROPERTY_SOURCE))
        time.sleep(0.2)
    return out


def best_candidate(signals: list[tuple[str, str]]) -> tuple[str, str]:
    """signals = [(klucz_kubelka, zrodlo)]. LP bije produkt, potem nizszy prio."""
    return min(signals, key=lambda s: (0 if s[1] == "lp" else 1, PRIO.get(s[0], 99)))


def main() -> None:
    live = "--live" in sys.argv
    since = None
    if "--since" in sys.argv:
        since = sys.argv[sys.argv.index("--since") + 1]
    elif "--lookback-minutes" in sys.argv:
        # Okno zachodzace — bez pliku stanu. Przy cronie co 15 min i oknie 45 min
        # pominiecie dwoch przebiegow z rzedu nadal nic nie gubi. Nadmiarowe
        # trafienia sa nieszkodliwe: zapisujemy wylacznie rzeczywiste zmiany.
        mins = int(sys.argv[sys.argv.index("--lookback-minutes") + 1])
        since = (dt.datetime.now(dt.timezone.utc)
                 - dt.timedelta(minutes=mins)).strftime("%Y-%m-%dT%H:%M:%SZ")
    elif os.path.exists(STATE):
        since = json.load(open(STATE)).get("last_run")
    since = since or since_default()

    run_started = now_iso()
    seg = json.load(open(SIGNALS))
    print(f"Nowi czlonkowie sygnalow od: {since}\n")

    # profil -> lista (kubelek, zrodlo) z NOWYCH sygnalow
    found: dict[str, list[tuple[str, str]]] = {}
    for state_key, seg_id in seg.items():
        key, kind = state_key.rsplit(":", 1)
        bucket = key if kind == "lp" else PROD_TO_BUCKET.get(key)
        if not bucket:
            continue                      # sygnal produktowy bez kubelka docelowego
        ids = new_members(seg_id, since)
        if ids:
            print(f"  {len(ids):>5} nowych  {state_key}")
        for pid in ids:
            found.setdefault(pid, []).append((bucket, kind))

    if not found:
        print("\nBrak nowych sygnalow — nic do zrobienia.")
        if live:
            json.dump({"last_run": run_started}, open(STATE, "w"), indent=2)
        return

    print(f"\nProfili z nowym sygnalem: {len(found)}")
    current = current_assignments(list(found))

    changes = []
    for pid, signals in found.items():
        cur_key, cur_src = current.get(pid, (None, None))
        cand_key, cand_kind = best_candidate(signals)
        cand_src = "lp" if cand_kind == "lp" else "produkt"

        if cur_key is None:
            pass                                            # pierwsze przypisanie
        elif cur_src == "lp" and cand_src == "produkt":
            continue                                        # nie degradujemy
        elif cur_src == cand_src and PRIO.get(cand_key, 99) >= PRIO.get(cur_key, 99):
            continue                                        # nie lepsze niz obecne
        if cur_key == cand_key and cur_src == cand_src:
            continue                                        # bez zmiany
        changes.append((pid, cand_key, cand_src, cur_key, cur_src))

    print(f"Rzeczywistych zmian: {len(changes)}")
    for pid, k, s, old_k, old_s in changes[:15]:
        # Pokazujemy tez zrodlo, inaczej awans `junior [produkt]` -> `junior [lp]`
        # wyglada w logu jak bezsensowny zapis tej samej wartosci.
        was = f"{old_k} [{old_s}]" if old_k else "(brak)"
        print(f"    {pid}  {was} -> {k} [{s}]")
    if len(changes) > 15:
        print(f"    … i {len(changes) - 15} wiecej")

    if not live:
        print("\n(dry-run — nic nie zapisano; dodaj --live)")
        return

    today = time.strftime("%Y-%m-%d")
    batch = [{"type": "profile", "id": pid, "attributes": {"properties": {
        PROPERTY: k, PROPERTY_SOURCE: s, PROPERTY_DATE: today}}}
        for pid, k, s, _old_k, _old_s in changes]
    sent = 0
    for i in range(0, len(batch), 3000):
        chunk = batch[i:i + 3000]
        r = K.request("POST", "/profile-bulk-import-jobs", {"data": {
            "type": "profile-bulk-import-job",
            "attributes": {"profiles": {"data": chunk}}}})
        if r.get("_error"):
            print(f"  BLAD zapisu: {json.dumps(r['detail'], ensure_ascii=False)[:300]}")
            sys.exit(1)                  # nie przesuwaj znacznika czasu przy bledzie
        sent += len(chunk)
        time.sleep(1.0)
    print(f"\nZapisano {sent} zmian.")
    json.dump({"last_run": run_started}, open(STATE, "w"), indent=2)
    print(f"Znacznik czasu przesuniety na {run_started}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Analiza zapasu wzrostu ruchu organicznego genactiv.pl.

Czyta cache z fetch_senuto_positions.py i odpowiada na pytanie: gdzie
sa najtansze wzrosty ruchu i ile realnie moga dac.

    source venv/bin/activate
    python3 sprint-2026-06/W1/A1/artefakty/analyze_traffic_headroom.py

Read-only. Wynik: podsumowanie na stdout + strinking-distance.csv.
"""

import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "senuto-raw" / "genactiv.pl.json"
OUT_CSV = HERE / "striking-distance-2026-09-01.csv"

# Przyblizona krzywa CTR dla polskich SERP-ow. To model, nie pomiar -
# sluzy do uszeregowania szans, nie do prognozy przychodu.
CTR = {1: 0.27, 2: 0.15, 3: 0.10, 4: 0.07, 5: 0.05,
       6: 0.04, 7: 0.03, 8: 0.025, 9: 0.02, 10: 0.018}
CTR_11_20 = 0.008
# AI Overview zabiera czesc klikniec nawet gdy pozycja sie nie zmienia.
AIO_PENALTY = 0.65


def ctr(pos):
    if pos is None or pos <= 0:
        return 0.0
    if pos <= 10:
        return CTR[pos]
    if pos <= 20:
        return CTR_11_20
    return 0.0


def bucket(pos):
    if pos is None or pos <= 0:
        return "brak"
    if pos <= 3:
        return "1-3"
    if pos <= 10:
        return "4-10"
    if pos <= 20:
        return "11-20"
    if pos <= 50:
        return "21-50"
    return ">50"


def main():
    rows = json.loads(RAW.read_text(encoding="utf-8"))
    print(f"Fraz w bazie: {len(rows)}\n")

    buckets = Counter()
    vol_by_bucket = Counter()
    aio_by_bucket = Counter()
    for r in rows:
        b = bucket(r.get("position"))
        buckets[b] += 1
        vol_by_bucket[b] += r.get("searches") or 0
        if "ai_overview" in (r.get("snippets") or []):
            aio_by_bucket[b] += 1

    print("ROZKLAD POZYCJI (frazy / laczny wolumen mies. / z AI Overview)")
    for b in ["1-3", "4-10", "11-20", "21-50", ">50", "brak"]:
        if buckets[b]:
            share = aio_by_bucket[b] / buckets[b] * 100
            print(f"  {b:>6}: {buckets[b]:>5} fraz | {vol_by_bucket[b]:>8,} wol. | "
                  f"AIO: {aio_by_bucket[b]:>4} ({share:.0f}%)")

    # --- Striking distance: pozycje 11-20, realny zapas ---
    sd = [r for r in rows
          if r.get("position") and 11 <= r["position"] <= 20 and (r.get("searches") or 0) > 0]
    sd.sort(key=lambda r: -(r.get("searches") or 0))

    total_now = sum((r["searches"] or 0) * ctr(r["position"]) for r in sd)
    # Scenariusz: awans 11-20 -> pozycja 8 (ostrozny, nie zakladamy TOP3)
    total_to8 = sum((r["searches"] or 0) * CTR[8] *
                    (AIO_PENALTY if "ai_overview" in (r.get("snippets") or []) else 1.0)
                    for r in sd)
    print(f"\nSTRIKING DISTANCE (pozycje 11-20)")
    print(f"  fraz: {len(sd)} | laczny wolumen: {sum(r['searches'] for r in sd):,}/mc")
    print(f"  szacunkowe klikniecia teraz : ~{total_now:,.0f}/mc")
    print(f"  po awansie na pozycje 8     : ~{total_to8:,.0f}/mc "
          f"(+{total_to8 - total_now:,.0f})")

    # --- Gdzie te frazy siedza (ktore URL-e optymalizowac) ---
    by_url = defaultdict(lambda: {"n": 0, "vol": 0, "kws": []})
    for r in sd:
        u = (r.get("url") or "(brak)").replace("genactiv.pl", "").replace(" › ", "/")
        by_url[u]["n"] += 1
        by_url[u]["vol"] += r["searches"]
        by_url[u]["kws"].append((r["keyword"], r["searches"], r["position"]))
    top_urls = sorted(by_url.items(), key=lambda kv: -kv[1]["vol"])[:12]

    print(f"\nURL-E Z NAJWIEKSZYM ZAPASEM (pozycje 11-20, wg wolumenu)")
    for u, d in top_urls:
        top_kw = sorted(d["kws"], key=lambda k: -k[1])[:2]
        kws = "; ".join(f"{k} ({v:,}, poz.{p})" for k, v, p in top_kw)
        print(f"  {d['vol']:>7,}/mc | {d['n']:>3} fraz | {u[:58]}")
        print(f"           {kws}")

    # --- Intencja: gdzie sa pieniadze ---
    print(f"\nINTENCJA W STRIKING DISTANCE")
    intents = Counter()
    intent_vol = Counter()
    for r in sd:
        i = (r.get("intentions") or {}).get("main_intent") or "brak"
        intents[i] += 1
        intent_vol[i] += r["searches"]
    for i, n in intents.most_common():
        print(f"  {i:>15}: {n:>4} fraz | {intent_vol[i]:>8,}/mc")

    # --- AI Overview: gdzie tracimy klikniecia mimo pozycji ---
    aio_top10 = [r for r in rows
                 if r.get("position") and 1 <= r["position"] <= 10
                 and "ai_overview" in (r.get("snippets") or [])]
    aio_top10.sort(key=lambda r: -(r.get("searches") or 0))
    aio_vol = sum(r.get("searches") or 0 for r in aio_top10)
    print(f"\nAI OVERVIEW MIMO TOP10")
    print(f"  fraz: {len(aio_top10)} | wolumen: {aio_vol:,}/mc")
    print(f"  szacowana utrata klikniec przy {(1-AIO_PENALTY)*100:.0f}% erozji: "
          f"~{sum((r['searches'] or 0) * ctr(r['position']) * (1-AIO_PENALTY) for r in aio_top10):,.0f}/mc")
    print("  najwieksze:")
    for r in aio_top10[:8]:
        print(f"    {r['searches']:>6,}/mc poz.{r['position']:>2}  {r['keyword'][:52]}")

    # --- CSV z pelna lista szans ---
    import csv
    with OUT_CSV.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["keyword", "volume", "position", "difficulty", "cpc", "url",
                    "main_intent", "journey_stage", "ai_overview", "people_also_ask"])
        for r in sd:
            sn = r.get("snippets") or []
            it = r.get("intentions") or {}
            w.writerow([r["keyword"], r["searches"], r["position"], r.get("difficulty"),
                        r.get("cpc"), r.get("url"), it.get("main_intent"),
                        it.get("journey_stage"),
                        "tak" if "ai_overview" in sn else "",
                        "tak" if "people_also_ask" in sn else ""])
    print(f"\nZapisano: {OUT_CSV.relative_to(HERE.parents[3])} ({len(sd)} wierszy)")


if __name__ == "__main__":
    main()

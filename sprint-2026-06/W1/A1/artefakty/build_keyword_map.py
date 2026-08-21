#!/usr/bin/env python3
"""A1 — buduje mape fraz primary/secondary dla top 20 PDP + gap analysis + tag sezonowy.

Zrodla:
  * senuto-raw/<domena>.json  — pozycje z visibility_analysis (fetch_senuto_positions.py)
  * Senuto Keyword Explorer   — popyt na frazy, ktorych jeszcze nie rankujemy
    (/api/keywords_analysis/reports/keywords/getKeywords, country_id=1 — ten modul
     NIE wspiera 200/Base 2.0)
  * lista PDP + sesje: GA4 (property 279858535), pagePath ~ /products/, 90 dni

Wynik:
  * research/keyword-map-2026.csv        — Definition of Done zadania A1
  * artefakty/gap-analysis-2026-08-17.csv — pelna lista luk (konkurent TOP10, my nie)

Sezonowosc liczona z realnych trendow Senuto (trend_1..trend_12 = 12 kolejnych
miesiecy, trend_1 najstarszy). Udzial pazdziernik-marzec >= 0.58 => jesien-zima.

    source venv/bin/activate
    python3 sprint-2026-06/W1/A1/artefakty/build_keyword_map.py
"""

import csv
import json
import os
import sys
import time
import unicodedata
from datetime import date
from pathlib import Path

import requests
from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RAW = HERE / "senuto-raw"
KW_CACHE = RAW / "keyword-explorer"

KW_API = "https://api.senuto.com/api/keywords_analysis/reports/keywords/getKeywords"
KW_COUNTRY_ID = 1          # keywords_analysis nie przyjmuje 200
SEASON_MONTHS = {10, 11, 12, 1, 2, 3}
SEASON_HI, SEASON_LO = 0.58, 0.42

BRAND_TOKENS = ("genactiv", "colostrigen", "fiberbiom", "colosregen", "genactive")

# Konkurenci organiczni wg Senuto (competitors/getData), nie wg brandu z briefu —
# patrz WERYFIKACJA_KONKURENTOW w README-A1.md.
COMPETITORS = ["genoscope.pl", "colostrumactive.pl", "colostrumpolska.pl"]
COMPETITORS_CHECKED_OUT = ["immunolab.com.pl"]   # sprawdzony, zero pokrycia tematycznego

# Obce marki — fraza brandowa konkurenta nie jest celem dla naszej karty produktu.
OTHER_BRANDS = (
    "lr ", " lr", "hepatica", "primabiotic", "podopharm", "podoflex", "skinflex",
    "isla", "osavi", "colvita", "genoscope", "colostrum active", "colostrum plus",
    "coloni", "system 4", "bio botanical", "pan tabletka", "biotigen", "colbiom",
    "immune-labs", "immune labs", "swanson", "now foods", "solgar", "ecolife",
    "diabetegen", "humoko",
)

# Frazy informacyjne / niezwiazane z zakupem — nie moga byc primary_kw karty produktu.
JUNK_PATTERNS = (
    "co to", "czym jest", "po angielsku", "krzyzowk", "przepis", "jak zrobic",
    "z jajka", "z drozdzy", "domow", "wymiona", "porod", "zrebi", "ile klacz",
    "hodowl", "dla psa", "dla kota", "dla koni", "dla zwierzat", "wikipedia",
    "znaczenie", "definicja", "po niemiecku", "tekst", "piosenk",
)

# Top 20 PDP wg sesji GA4 (2026-05-19..2026-08-16). `require` = grupy tokenow;
# fraza musi zawierac co najmniej jeden token z KAZDEJ grupy — to odsiewa
# ogolne "colostrum" (to fraza kolekcji, nie karty produktu). `exclude` = tokeny
# odrzucajace frazy o innej intencji produktowej niz dana karta.
PDPS = [
    ("fiberbiom-blonnik-colostrum", 15566,
     ["błonnik", "błonnik na wzdęcia", "błonnik witalny", "błonnik colostrum"],
     [["blonnik"]], ["plesznik", "witalny sklad", "gdzie wystepuje"]),
    ("colostrum-genactiv-proszek", 5877,
     ["colostrum proszek", "colostrum w proszku"],
     [["colostrum", "siara"], ["proszek", "proszku", "sypki"]], []),
    ("colostrum-genactiv-120-kapsulek", 4602,
     ["colostrum kapsułki", "colostrum tabletki"],
     [["colostrum", "siara"], ["kaps"]], []),
    ("serum-z-colostrum-genactiv-100-ml", 3027,   # serum do wlosow slabych/wypadajacych
     ["serum z colostrum", "serum na wypadanie włosów", "serum na porost włosów"],
     [["serum"], ["colostrum", "siara", "wlos", "wypadani", "porost"]], ["twarz", "rzes", "brwi"]),
    ("krem-z-colostrum-genactiv", 3015,
     ["krem z colostrum", "krem regeneracyjny colostrum", "krem na blizny",
      "krem regenerujący do twarzy"],
     [["krem"], ["colostrum", "siara", "regener", "blizn", "nawilz", "odbudow"]],
     ["do stop", "pod oczy", "sloneczn", "dla psa"]),
    ("fiberbiom-z-ananasem", 2590,
     ["błonnik z ananasem", "błonnik na wzdęcia", "błonnik na trawienie"],
     [["blonnik"], ["ananas", "wzdec", "trawien", "jelit", "zaparc"]], []),
    ("colostrum-genactiv-60-kapsulek", 2098,
     ["colostrum kapsułki", "colostrum tabletki"],
     [["colostrum", "siara"], ["kaps"]], []),
    ("colostrum-junior-z-czarnym-bzem-genactiv-zawiesina", 1789,
     ["colostrum dla dzieci", "colostrum junior", "colostrum w płynie dla dzieci"],
     [["colostrum", "siara"], ["dzieci", "dziecka", "junior", "niemowl"]], ["kozie"]),
    ("colostrum-genactiv-zawiesina", 1637,
     ["colostrum w płynie", "colostrum zawiesina"],
     [["colostrum", "siara"], ["plyn", "zawiesin"]], []),
    ("maseczka-z-colostrum-50-ml", 1544,          # maseczka do TWARZY
     ["maseczka z colostrum", "maseczka regenerująca do twarzy",
      "maseczka odżywcza do twarzy"],
     [["maseczk", "maska"], ["colostrum", "siara", "twarz"]],
     ["plachci", "plachta", "glink", "wegl", "wlos", "skory glowy", "kalendarz",
      "slime", "koreans"]),
    ("colostrum-z-brzoskwinia-proszek-60-g", 1333,
     ["colostrum proszek", "colostrum smakowe"],
     [["colostrum", "siara"], ["proszek", "proszku", "brzoskwini", "smak"]], []),
    ("colostrum-junior-z-czarnym-bzem-genactiv-proszek", 1311,
     ["colostrum dla dzieci proszek", "colostrum junior"],
     [["colostrum", "siara"], ["dzieci", "dziecka", "junior", "niemowl"]], ["kozie"]),
    ("bloker-z-colostrum-genactiv-90-ml", 1110,
     ["bloker do skóry głowy", "ochrona skóry głowy przed farbowaniem",
      "bloker do farbowania włosów"],
     [["bloker", "skory glowy"]], []),
    ("maska-z-colostrum-genactiv-250-ml", 1101,   # maska do SKORY GLOWY / wlosow
     ["maska do włosów colostrum", "maska do skóry głowy",
      "maska na wypadanie włosów", "maska do włosów"],
     [["maska", "maseczk"], ["colostrum", "siara", "skory glowy", "wlos"]],
     ["twarz", "glink", "wegl", "jajka", "drozdz", "chleb"]),
    ("colostrum-i-mleko-klaczy-200g", 910,
     ["mleko klaczy", "mleko klaczy colostrum"],
     [["klacz"], ["mleko", "mleka", "colostrum", "siara"]], ["napoj z mleka klaczy"]),
    ("colostrum-i-mleko-klaczy-genactiv-proszek-50-g", 889,
     ["mleko klaczy proszek", "mleko klaczy"],
     [["klacz"], ["mleko", "mleka", "colostrum", "siara"]], ["napoj z mleka klaczy"]),
    ("colostrum-z-malina-genactiv-tabletki-do-ssania-60-sztuk", 871,
     ["tabletki do ssania na gardło", "colostrum tabletki do ssania",
      "pastylki do ssania na gardło"],
     [["ssani", "pastylk"]], []),
    ("colostrum-genactiv-a2-kapsulki", 870,
     ["colostrum a2", "mleko a2", "beta kazeina a2"],
     [["a2"]], ["a2a2", "krow"]),
    ("maseczka-z-colostrum-genactiv-150ml", 854,  # ta sama maseczka do twarzy, 150 ml
     ["maseczka z colostrum", "maseczka nawilżająca do twarzy",
      "maseczka odżywcza do twarzy"],
     [["maseczk", "maska"], ["colostrum", "siara", "twarz"]],
     ["plachci", "plachta", "glink", "wegl", "wlos", "skory glowy", "kalendarz",
      "slime", "koreans"]),
    ("colostrum-z-bananem-genactiv-30-saszetek", 853,
     ["colostrum saszetki", "colostrum dla dzieci saszetki"],
     [["colostrum", "siara"], ["saszet", "banan"]], []),
]


def fold(text):
    """Bez ogonkow, lowercase — Senuto miesza pisownie ('blonnik'/'błonnik')."""
    nfkd = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def slug(text):
    return fold(text).replace(" ", "-").replace("/", "-")


def fetch_seed(session, api_key, seed):
    cache = KW_CACHE / f"{slug(seed)}.json"
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
            "match_mode": "wide",
        },
        timeout=60,
    )
    if resp.status_code != 200 or not resp.json().get("success"):
        raise SystemExit(f"Keyword Explorer '{seed}': HTTP {resp.status_code} — {resp.text[:200]}")
    rows = resp.json().get("data") or []
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding="utf-8")
    time.sleep(0.3)
    return rows


def season_of(row):
    """('jesien-zima'|'wiosna-lato'|'caloroczna', udzial X-III, miesiac szczytu)."""
    trends = [row.get(f"trend_{i}") or 0 for i in range(1, 13)]
    total = sum(trends)
    if not total:
        return "brak-danych", 0.0, ""
    today = date.today()
    # trend_1 = najstarszy z 12 miesiecy; trend_12 = ostatni pelny miesiac
    months = [((today.month - 1 - (12 - i)) % 12) + 1 for i in range(1, 13)]
    share = sum(v for m, v in zip(months, trends) if m in SEASON_MONTHS) / total
    peak = months[trends.index(max(trends))]
    tag = "jesien-zima" if share >= SEASON_HI else ("wiosna-lato" if share <= SEASON_LO else "caloroczna")
    return tag, round(share, 3), f"{peak:02d}"


def main():
    load_dotenv(ROOT / ".env")
    api_key = os.getenv("SENUTO_API_KEY")
    if not api_key:
        sys.exit("Brak SENUTO_API_KEY w .env")
    if not (RAW / "genactiv.pl.json").exists():
        sys.exit("Brak senuto-raw/ — uruchom najpierw fetch_senuto_positions.py")

    session = requests.Session()

    # --- pozycje: nasze i konkurencji ---------------------------------------
    def load_positions(domain):
        rows = json.loads((RAW / f"{domain}.json").read_text(encoding="utf-8"))
        best = {}
        for r in rows:
            k, p = fold(r["keyword"]), r.get("position")
            if p and (k not in best or p < best[k]["position"]):
                best[k] = {"position": p, "url": r.get("url"), "raw": r["keyword"]}
        return best

    ours = load_positions("genactiv.pl")
    comps = {d: load_positions(d) for d in COMPETITORS}

    # difficulty i wolumen to atrybuty frazy, nie domeny — laczymy ze wszystkich plikow
    kw_meta = {}
    for dom in ["genactiv.pl"] + COMPETITORS + COMPETITORS_CHECKED_OUT:
        for r in json.loads((RAW / f"{dom}.json").read_text(encoding="utf-8")):
            f = fold(r["keyword"])
            meta = kw_meta.setdefault(f, {})
            if r.get("difficulty") is not None:
                meta.setdefault("difficulty", r["difficulty"])
            if r.get("searches"):
                meta.setdefault("searches", r["searches"])

    def is_usable(f, exclude):
        if any(b in f for b in BRAND_TOKENS):
            return False
        if any(b in f for b in OTHER_BRANDS):
            return False
        if any(j in f for j in JUNK_PATTERNS):
            return False
        return not any(x in f for x in exclude)

    # --- kandydaci na frazy per PDP -----------------------------------------
    rows_out = []
    pdp_of_keyword = {}
    for handle, sessions, seeds, require, exclude in PDPS:
        pool = {}
        for seed in seeds:
            for r in fetch_seed(session, api_key, seed):
                kw = r.get("keyword")
                if not kw:
                    continue
                f = fold(kw)
                if not all(any(tok in f for tok in group) for group in require):
                    continue
                if not is_usable(f, exclude):
                    continue
                pool.setdefault(f, r)
        ranked = sorted(pool.values(), key=lambda r: -(r.get("searches") or 0))
        if not ranked:
            print(f"  UWAGA: brak kandydatow dla {handle}")
            continue

        pdp_url = f"https://genactiv.pl/products/{handle}"
        primary = ranked[0]
        secondary = ranked[1:5]
        tag, share, peak = season_of(primary)
        vol = primary.get("searches") or 0

        def pos_str(kw):
            hit = ours.get(fold(kw))
            return str(hit["position"]) if hit else ">50"

        rows_out.append({
            "pdp_url": pdp_url,
            "ga4_sessions_90d": sessions,
            "primary_kw": primary["keyword"],
            "secondary_kw": " | ".join(r["keyword"] for r in secondary),
            "volume": vol,
            "volume_secondary": sum(r.get("searches") or 0 for r in secondary),
            "demand_tier": "wysoki" if vol >= 1000 else ("sredni" if vol >= 100 else "nisza"),
            "difficulty": kw_meta.get(fold(primary["keyword"]), {}).get("difficulty", ""),
            "cpc": primary.get("cpc") or 0,
            "our_pos": pos_str(primary["keyword"]),
            "our_url": (ours.get(fold(primary["keyword"])) or {}).get("url", ""),
            "comp_gap": "",     # uzupelniane po gap analysis
            "season": tag,
            "season_share_X_III": share,
            "season_peak_month": peak,
        })

    # --- gap analysis: konkurent w TOP10, my poza TOP10 ----------------------
    # Liczone na PELNYM zbiorze fraz konkurentow, nie tylko na pulach PDP.
    # Mapowanie luki na PDP idzie przez te same reguly require/exclude co mapa fraz.
    def match_pdp(f):
        for handle, _s, _seeds, require, exclude in PDPS:
            if not all(any(tok in f for tok in group) for group in require):
                continue
            if any(x in f for x in exclude):
                continue
            return f"https://genactiv.pl/products/{handle}"
        return ""

    gap_rows, seen_gap = [], set()
    for dom, table in comps.items():
        for f, hit in table.items():
            if hit["position"] > 10:
                continue
            our = ours.get(f)
            if our and our["position"] <= 10:
                continue
            if not is_usable(f, []):
                continue
            key = (f, dom)
            if key in seen_gap:
                continue
            seen_gap.add(key)
            meta = kw_meta.get(f, {})
            gap_rows.append({
                "keyword": hit.get("raw", f),
                "volume": meta.get("searches", 0),
                "difficulty": meta.get("difficulty", ""),
                "our_pos": our["position"] if our else ">50",
                "competitor": dom,
                "competitor_pos": hit["position"],
                "competitor_url": hit.get("url", ""),
                "mapped_pdp": match_pdp(f),
            })

    # comp_gap w mapie fraz = najwieksze luki przypisane do danego PDP
    by_pdp = {}
    for g in sorted(gap_rows, key=lambda r: -(r["volume"] or 0)):
        if g["mapped_pdp"]:
            by_pdp.setdefault(g["mapped_pdp"], []).append(
                f"{g['keyword']} ({g['volume']}) → {g['competitor']}:{g['competitor_pos']}")
    for row in rows_out:
        hits = by_pdp.get(row["pdp_url"], [])[:3]
        row["comp_gap"] = " | ".join(hits) or "brak"

    out_csv = ROOT / "research" / "keyword-map-2026.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows_out[0].keys()))
        w.writeheader()
        w.writerows(rows_out)
    print(f"OK: {out_csv} — {len(rows_out)} PDP")

    gap_rows.sort(key=lambda r: -(r["volume"] or 0))
    gap_csv = HERE / "gap-analysis-2026-08-17.csv"
    with gap_csv.open("w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["keyword", "volume", "difficulty", "our_pos",
                                           "competitor", "competitor_pos",
                                           "competitor_url", "mapped_pdp"])
        w.writeheader()
        w.writerows(gap_rows)
    print(f"OK: {gap_csv} — {len(gap_rows)} luk "
          f"({sum(1 for r in gap_rows if r['mapped_pdp'])} zmapowanych na PDP)")


if __name__ == "__main__":
    main()

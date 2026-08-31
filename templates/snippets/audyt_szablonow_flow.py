#!/usr/bin/env python3
"""
Mapuje wszystkie flow (journeys) w Klaviyo na podpiete szablony i audytuje
ich linki oraz zmienne personalizacji.

Po co: w flow porzuconego koszyka jest wiele wiadomosci i czesc z nich moze
linkowac do pol, ktorych dana metryka nie niesie (np. event.extra.checkout_url
przy triggerze Added to Cart -> pusty href, przycisk prowadzi donikad).

Metoda (Klaviyo API nie pozwala zejsc ponizej trzech poziomow):

    1. GET /api/flows?include=flow-actions      <- 1 zapytanie na wszystko
    2. GET /api/flow-actions/{id}/flow-messages <- tylko akcje SEND_MESSAGE
    3. GET /api/flow-messages/{id}/template     <- po jednym na wiadomosc

Pulapki API, sprawdzone empirycznie 2026-08-31:
  - `fields[flow-action]=action_type` zwraca 400. Trzeba pobierac bez `fields`.
  - `flow-actions/{id}/flow-messages?include=template` zwraca 400.
  - `flows/{id}/flow-actions?include=flow-messages` zwraca 400.
  - Limit jest niski: bez throttlingu leci 429. Stad pauza i backoff.
  - Brak wyniku po serii bledow NIE znaczy "nie znaleziono" - skrypt liczy
    bledy osobno i wypisuje je, zeby nie mylic ciszy z ustaleniem.

Uzycie:
    python3 templates/snippets/audyt_szablonow_flow.py
    python3 templates/snippets/audyt_szablonow_flow.py --flow koszyk
"""
import io
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "templates/snippets"))
from build_koszyk_mail1 import read_key  # noqa: E402

API = "https://a.klaviyo.com/api"
REVISION = "2026-01-15"
PAUSE = 0.7
OUT = ROOT / "reports/audyt-szablonow-flow.csv"

# Pola, ktore niesie dana metryka. Zrodlo: realne eventy (patrz README-koszyk.md).
METRIC_FIELDS = {
    "Added to Cart": {
        "ma": {"ImageURL", "Price", "CompareAtPrice", "Quantity", "URL",
               "Product Name", "Variant Name", "Categories"},
        "nie_ma": {"extra.checkout_url", "extra.line_items"},
    },
    "Checkout Started": {
        "ma": {"extra.checkout_url", "extra.line_items", "Items", "Item Count"},
        "nie_ma": {"ImageURL", "Price", "CompareAtPrice", "Product Name",
                   "Variant Name", "URL"},
    },
}


def get(url, tries=6):
    for a in range(tries):
        try:
            req = urllib.request.Request(url, headers={
                "Authorization": f"Klaviyo-API-Key {read_key()}",
                "revision": REVISION, "accept": "application/vnd.api+json"})
            time.sleep(PAUSE)
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 429 and a < tries - 1:
                time.sleep(6 * (a + 1))
                continue
            return {"__err__": e.code}
        except Exception:
            if a == tries - 1:
                return {"__err__": "timeout"}
            time.sleep(3)


def analyze(html, trigger_metric):
    """Zwraca liste problemow znalezionych w HTML szablonu."""
    problems = []

    hrefs = re.findall(r'href\s*=\s*"([^"]*)"', html)
    puste = [h for h in hrefs if not h.strip()]
    if puste:
        problems.append(f"{len(puste)} pustych href")

    myshop = [h for h in hrefs if "myshopify" in h]
    if myshop:
        problems.append(f"{len(myshop)} linkow na myshopify.com")

    # zmienne event.* uzyte w szablonie
    used = set(re.findall(r"event\.([A-Za-z_][\w.]*)", html))
    used |= {f"{m}" for m in re.findall(r"event\|lookup:'([^']+)'", html)}

    spec = METRIC_FIELDS.get(trigger_metric or "")
    if spec:
        for u in sorted(used):
            for bad in spec["nie_ma"]:
                if u == bad or u.startswith(bad):
                    problems.append(f"uzywa event.{u}, a {trigger_metric} tego nie niesie")

    # href zbudowany wprost ze zmiennej, ktorej metryka nie ma -> martwy przycisk
    for h in hrefs:
        m = re.match(r"\{\{\s*event\.([\w.]+)", h.strip())
        if m and spec and any(m.group(1).startswith(b) for b in spec["nie_ma"]):
            problems.append(f"CTA linkuje przez event.{m.group(1)} -> bedzie pusty")

    if "{% unsubscribe" not in html:
        problems.append("brak {% unsubscribe %}")
    if re.search(r"No longer want to receive", html):
        problems.append("angielska stopka")

    imgs = re.findall(r"<img[^>]*>", html)
    bez_alt = [i for i in imgs if "alt=" not in i]
    if bez_alt:
        problems.append(f"{len(bez_alt)}/{len(imgs)} obrazkow bez alt")

    return sorted(set(problems)), sorted(used)


def main():
    filtr = None
    if "--flow" in sys.argv:
        filtr = sys.argv[sys.argv.index("--flow") + 1].lower()

    # Uwaga: Klaviyo nie laczy `include` z `additional-fields` w jednym zapytaniu
    # (zwraca 400), wiec definicje triggerow pobieramy osobno, per flow.
    print("1/3 pobieram flow + akcje (jedno zapytanie)...")
    d = get(f"{API}/flows?include=flow-actions")
    if "__err__" in d:
        sys.exit(f"Nie udalo sie pobrac flow: {d}")

    # metric_id -> nazwa metryki, zeby wiedziec jakie pola niesie trigger
    mets = get(f"{API}/metrics?fields[metric]=name")
    metryki = ({m["id"]: m["attributes"]["name"] for m in mets["data"]}
               if "__err__" not in mets else {})
    if not metryki:
        print("    UWAGA: nie pobrano metryk - kontrola zmiennych vs trigger bedzie pominieta")

    flows = {f["id"]: f["attributes"] for f in d["data"]}
    # akcje z sideloadu, przypisane do flow przez relationships
    akcje_flow = {}
    for f in d["data"]:
        ids = [r["id"] for r in
               f.get("relationships", {}).get("flow-actions", {}).get("data", [])]
        akcje_flow[f["id"]] = ids
    akcje = {a["id"]: a["attributes"] for a in d.get("included", [])}
    print(f"    flow: {len(flows)}, akcji: {len(akcje)}")

    rows, errors = [], []
    cel = [(fid, at) for fid, at in flows.items()
           if not filtr or filtr in at["name"].lower()]
    print(f"2/3 przechodze {len(cel)} flow...")

    for fid, fat in cel:
        nazwa, status = fat["name"], fat["status"]
        # nazwa metryki wyzwalajacej, np. "Added to Cart" - to od niej zalezy,
        # ktore pola event.* w ogole istnieja w szablonach tego flow
        defn = get(f"{API}/flows/{fid}?additional-fields[flow]=definition")
        trigger = fat.get("trigger_type") or ""
        if "__err__" in defn:
            errors.append(f"{nazwa}: definicja triggera -> {defn['__err__']}")
        else:
            trigs = (defn["data"]["attributes"].get("definition") or {}).get("triggers") or []
            mid = next((t.get("id") for t in trigs if t.get("type") == "metric"), None)
            trigger = metryki.get(mid) or trigger
        send = [aid for aid in akcje_flow.get(fid, [])
                if akcje.get(aid, {}).get("action_type") in (None, "SEND_MESSAGE")]
        for aid in send:
            msgs = get(f"{API}/flow-actions/{aid}/flow-messages")
            if "__err__" in msgs:
                errors.append(f"{nazwa}: wiadomosci akcji {aid} -> {msgs['__err__']}")
                continue
            for m in msgs.get("data", []):
                mid = m["id"]
                mnazwa = m["attributes"].get("name") or "(bez nazwy)"
                tpl = get(f"{API}/flow-messages/{mid}/template")
                if "__err__" in tpl:
                    errors.append(f"{nazwa}/{mnazwa}: szablon -> {tpl['__err__']}")
                    continue
                t = tpl.get("data")
                if not t:
                    rows.append([nazwa, status, trigger, mnazwa, "", "(brak szablonu)", "", ""])
                    continue
                html = t["attributes"].get("html") or ""
                probs, used = analyze(html, trigger)
                rows.append([nazwa, status, trigger or "", mnazwa,
                             t["id"], t["attributes"]["name"],
                             "; ".join(probs), ", ".join(used)])
                print(f"    [{status:6}] {nazwa[:34]:34} | {mnazwa[:22]:22} | "
                      f"{t['id']} | {'; '.join(probs)[:60]}")

    print("3/3 zapisuje raport...")
    OUT.parent.mkdir(exist_ok=True)
    import csv
    with io.open(OUT, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["flow", "status", "trigger", "wiadomosc", "template_id",
                    "template_name", "problemy", "uzyte_zmienne_event"])
        w.writerows(rows)

    print(f"\nZnaleziono {len(rows)} wiadomosci z szablonami -> {OUT.relative_to(ROOT)}")
    if errors:
        print(f"\nUWAGA: {len(errors)} miejsc NIE sprawdzono (brak wyniku != brak problemu):")
        for e in errors[:15]:
            print("   ", e)


if __name__ == "__main__":
    main()

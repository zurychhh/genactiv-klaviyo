#!/usr/bin/env python3
"""
Naprawia szablony flow "Abandoned Cart Reminder" (trigger: Added to Cart).

Problem zrodlowy: szablony powstaly dla metryki Checkout Started i siegaja po
pola, ktorych Added to Cart nie niesie. Efekt na produkcji, potwierdzony
renderem przez POST /api/template-render na realnym zdarzeniu: glowny przycisk
ma pusty href i nie prowadzi nigdzie.

Cztery poprawki na szablon:
  1. CTA  {{ event.extra.checkout_url }}  -> staly adres koszyka
     (pole istnieje tylko w Checkout Started; to jest ten martwy link)
  2. href {{ event.URL }}                 -> staly adres koszyka
     (w 150/150 zdarzen event.URL wskazuje na genactiv.myshopify.com)
  3. {{ event.Categories.2 }}             -> {{ event|lookup:'Variant Name' }}
     (Categories.2 zwraca nazwy kolekcji typu "Colostrum dla mamy";
      Variant Name zwraca forme opakowania, wypelnione w 149/150 zdarzen)
  4. alt dla logo i grafiki stopki (dostepnosc + tryb z zablokowanymi obrazami)

Nie rusza tresci, ukladu ani stylow.

Uzycie:
    python3 templates/snippets/napraw_szablony_koszyk.py              # dry-run
    python3 templates/snippets/napraw_szablony_koszyk.py --clone-test # test na klonie
    python3 templates/snippets/napraw_szablony_koszyk.py --apply      # PATCH na zywych
"""
import io
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "templates/snippets"))
from build_koszyk_mail1 import read_key  # noqa: E402

API = "https://a.klaviyo.com/api"
REVISION = "2026-01-15"
CART_URL = "https://genactiv.pl/cart"
OUTDIR = ROOT / "templates/snippets/naprawione"

# Wszystkie trzy flow koszykowe stoja na metryce Added to Cart i wszystkie
# 12 szablonow ma ten sam blad. Drafty ida na test A/B przeciwko zywej wersji,
# wiec musza byc naprawione razem z nia.
SZABLONY = [
    # flow "Abandoned Cart Reminder" — LIVE
    ("SXcBja", "live-mail1", "porzucony-koszyk-mail1"),
    ("WeKAHD", "live-mail2", "ac-mail2-no-free-shipping"),
    ("Rf5XM2", "live-mail3", "ac-mail3-free-shipping-coupon"),
    ("UQquNm", "live-mail4", "ac-mail4-no-free-shipping-shipping"),
    # flow "Abandoned Cart Reminder_COLOSTRUM" — draft (A/B)
    ("RznQK5", "colostrum-mail1", "porzucony-koszyk-mail1"),
    ("Uxdz9q", "colostrum-mail2", "ac-mail2-no-free-shipping"),
    ("S7LD2i", "colostrum-mail3", "ac-mail3-free-shipping-coupon"),
    ("VGCq3g", "colostrum-mail4", "ac-mail4-no-free-shipping-shipping"),
    # flow "Abandoned Cart Reminder_FIBERBIOM" — draft (A/B)
    ("VNmEYw", "fiberbiom-mail1", "porzucony-koszyk-mail1"),
    ("TnUJRq", "fiberbiom-mail2", "ac-mail2-no-free-shipping"),
    ("QXtNJi", "fiberbiom-mail3", "ac-mail3-free-shipping-coupon"),
    ("VHJqD8", "fiberbiom-mail4", "ac-mail4-no-free-shipping-shipping"),
]

BACKUP = ROOT / "templates/snippets/backup"

ALT = {
    "193ca763-519b-49f4-9629-667952120e2f": "GENACTIV",
    # grafika stopki - w mailach 1-2 jedno ujecie, w mailach 3-4 inne
    "8b80403a-0130-4c9d-946d-76b57fddf98b": "Produkty GENACTIV Colostrum",
    "1f7d2219-5cb1-4412-8bb0-ccd6090a7411": "Opakowania GENACTIV Colostrum z kapsułkami",
}


def req(url, method="GET", body=None, tries=5):
    for a in range(tries):
        try:
            r = urllib.request.Request(url, method=method,
                data=json.dumps(body).encode() if body else None,
                headers={"Authorization": f"Klaviyo-API-Key {read_key()}",
                         "revision": REVISION,
                         "accept": "application/vnd.api+json",
                         "content-type": "application/vnd.api+json"})
            time.sleep(0.7)
            with urllib.request.urlopen(r, timeout=90) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {"__ok__": resp.status}
        except urllib.error.HTTPError as e:
            if e.code == 429 and a < tries - 1:
                time.sleep(6 * (a + 1))
                continue
            return {"__err__": e.code, "body": e.read().decode()[:300]}
        except Exception as e:
            if a == tries - 1:
                return {"__err__": str(e)[:120]}
            time.sleep(3)


def napraw(html):
    """Zwraca (nowy_html, lista_zmian). Idempotentna - ponowne uruchomienie nic nie zmieni."""
    zmiany = []

    # 1. CTA przez checkout_url -> staly koszyk
    new, n = re.subn(r'href="\{\{\s*event\.extra\.checkout_url\s*\|?[^"}]*\}\}"',
                     f'href="{CART_URL}"', html)
    if n:
        zmiany.append(f"CTA checkout_url -> {CART_URL} ({n}x)")
    html = new

    # 2. linki produktowe przez event.URL (domena myshopify) -> staly koszyk
    new, n = re.subn(r'href="\{\{\s*event\.URL\s*\|?[^"}]*\}\}"',
                     f'href="{CART_URL}"', html)
    if n:
        zmiany.append(f"event.URL -> {CART_URL} ({n}x)")
    html = new

    # 3. Categories.2 -> Variant Name
    new, n = re.subn(r"\{\{\s*event\.Categories\.2\s*\|[^}]*\}\}",
                     "{{ event|lookup:'Variant Name'|default:'' }}", html)
    if n:
        zmiany.append(f"Categories.2 -> Variant Name ({n}x)")
    html = new

    # 4. alt dla obrazkow, ktore go nie maja
    for frag, alt in ALT.items():
        def add_alt(m):
            tag = m.group(0)
            return tag if "alt=" in tag else tag.replace("<img ", f'<img alt="{alt}" ', 1)
        new, n = re.subn(r"<img (?![^>]*\balt=)[^>]*" + re.escape(frag) + r"[^>]*>",
                         add_alt, html)
        if n:
            zmiany.append(f'alt="{alt}" ({n}x)')
        html = new

    return html, zmiany


def kontrola(html, nazwa):
    """Twarde asercje po naprawie - lepiej przerwac niz wgrac polprodukt."""
    bledy = []
    if re.search(r"event\.extra\.checkout_url", html):
        bledy.append("nadal jest event.extra.checkout_url")
    if re.search(r'href="\{\{\s*event\.URL', html):
        bledy.append("nadal jest href przez event.URL")
    if "event.Categories.2" in html:
        bledy.append("nadal jest Categories.2")
    if "{% unsubscribe" not in html:
        bledy.append("zniknal {% unsubscribe %}")
    if not re.search(r"<html", html, re.I) or not re.search(r"<body", html, re.I):
        bledy.append("uszkodzona struktura html/body")
    imgs = re.findall(r"<img[^>]*>", html)
    bez = sum(1 for i in imgs if "alt=" not in i)
    if bez:
        bledy.append(f"{bez} obrazkow nadal bez alt")
    if bledy:
        print(f"  KONTROLA NIEZDANA ({nazwa}): " + "; ".join(bledy))
    return not bledy


def render_probe(tid):
    """Renderuje szablon na realnym zdarzeniu Added to Cart i zwraca puste href."""
    import urllib.parse
    q = urllib.parse.urlencode({"filter": 'equals(metric_id,"WcWiXd")',
                                "sort": "-datetime",
                                "fields[event]": "event_properties", "page[size]": 1})
    ev = req(f"{API}/events?" + q)
    if "__err__" in ev:
        return None, f"nie pobrano zdarzenia: {ev['__err__']}"
    props = ev["data"][0]["attributes"]["event_properties"]
    ctx = {k.lstrip("$"): v for k, v in props.items()}
    r = req(f"{API}/template-render", "POST",
            {"data": {"type": "template", "attributes": {"id": tid, "context": {"event": ctx}}}})
    if "__err__" in r:
        return None, f"render nieudany: {r['__err__']}"
    h = r["data"]["attributes"]["html"]
    hrefs = re.findall(r'href\s*=\s*"([^"]*)"', h)
    return [x for x in hrefs if not x.strip()], props.get("Product Name")


def main():
    tryb = ("apply" if "--apply" in sys.argv else
            "library" if "--publish-library" in sys.argv else
            "clone" if "--clone-test" in sys.argv else "dry")
    print(f"Tryb: {tryb}\n")
    OUTDIR.mkdir(exist_ok=True)
    wyniki = []

    for tid, lab, opis in SZABLONY:
        d = req(f"{API}/templates/{tid}")
        if "__err__" in d:
            print(f"{tid}: nie pobrano ({d['__err__']}) - pomijam")
            continue
        a = d["data"]["attributes"]

        # backup oryginalu ZAWSZE, zanim cokolwiek policzymy - takze w dry-run
        BACKUP.mkdir(exist_ok=True)
        bp = BACKUP / f"{tid}-{lab}-backup-2026-08-31.html"
        if not bp.exists():
            io.open(bp, "w", encoding="utf-8").write(a["html"])
            io.open(bp.with_suffix(".json"), "w", encoding="utf-8").write(
                json.dumps(d["data"], ensure_ascii=False, indent=1))

        html, zmiany = napraw(a["html"])

        print(f"=== {tid} ({lab}) {opis}")
        if not zmiany:
            print("    brak zmian - juz naprawiony")
        for z in zmiany:
            print(f"    + {z}")
        if not kontrola(html, tid):
            print("    PRZERYWAM ten szablon\n")
            continue

        p = OUTDIR / f"{tid}-{lab}-naprawiony.html"
        io.open(p, "w", encoding="utf-8").write(html)
        print(f"    zapisano: {p.relative_to(ROOT)}")

        if tryb == "clone":
            c = req(f"{API}/template-clone", "POST", {"data": {"type": "template",
                    "attributes": {"id": tid, "name": f"ZZZ TEST {tid} - do usuniecia"}}})
            if "__err__" in c:
                print(f"    klon nieudany: {c['__err__']}\n"); continue
            cid = c["data"]["id"]
            pt = req(f"{API}/templates/{cid}", "PATCH", {"data": {"type": "template",
                     "id": cid, "attributes": {"html": html}}})
            if "__err__" in pt:
                print(f"    PATCH klona nieudany: {pt['__err__']} {pt.get('body','')[:120]}")
            else:
                puste, info = render_probe(cid)
                print(f"    render klona na zdarzeniu '{str(info)[:34]}': "
                      f"pustych href = {puste if puste is None else len(puste)}")
            req(f"{API}/templates/{cid}", "DELETE")
            print("    klon usuniety")

        elif tryb == "library":
            # Szablonow przypietych do flow NIE da sie zapisac przez API:
            #   PATCH /api/templates/{id}      -> 404 (nie ma ich w bibliotece)
            #   PATCH /api/flow-messages/{id}  -> 405 Method Not Allowed
            # Publikujemy wiec poprawione wersje do biblioteki, zeby dalo sie je
            # podpiac w edytorze flow bez recznego wklejania HTML.
            nowa = f"[NAPRAWIONY 2026-08-31] {lab} — {opis}"
            c = req(f"{API}/templates", "POST", {"data": {"type": "template",
                    "attributes": {"name": nowa, "editor_type": "CODE", "html": html}}})
            if "__err__" in c:
                print(f"    publikacja nieudana: {c['__err__']} {c.get('body','')[:140]}")
                continue
            nid = c["data"]["id"]
            puste, info = render_probe(nid)
            ok = puste is not None and len(puste) == 0
            print(f"    opublikowano: {nid}  ({nowa[:52]})")
            print(f"    render: pustych href = {puste if puste is None else len(puste)}"
                  f" {'OK' if ok else 'SPRAWDZ'}")
            wyniki.append(f"{tid}->{nid}")
            print()
            continue

        elif tryb == "apply":
            pt = req(f"{API}/templates/{tid}", "PATCH", {"data": {"type": "template",
                     "id": tid, "attributes": {"html": html}}})
            if "__err__" in pt:
                print(f"    PATCH NIEUDANY: {pt['__err__']} {pt.get('body','')[:150]}")
                if pt["__err__"] == 404:
                    print("    -> ten szablon jest przypiety do flow i nie ma go"
                          " w bibliotece; API go nie zapisze. Uzyj --publish-library")
                print()
                continue
            else:
                puste, info = render_probe(tid)
                print(f"    WGRANE. render: pustych href = "
                      f"{puste if puste is None else len(puste)}")
        wyniki.append(tid)
        print()

    print(f"Przetworzono {len(wyniki)}/{len(SZABLONY)} szablonow: {', '.join(wyniki)}")
    if len(wyniki) < len(SZABLONY):
        print(f"UWAGA: {len(SZABLONY) - len(wyniki)} szablonow NIE przetworzono"
              " — patrz komunikaty wyzej.")
    if tryb == "dry":
        print("\nTo byl dry-run. Nic nie zapisano do Klaviyo.")
        print("Test na kopiach:      --clone-test")
        print("Publikacja do biblioteki: --publish-library")
        print("PATCH na miejscu:     --apply  (dziala tylko dla szablonow z biblioteki)")


if __name__ == "__main__":
    main()

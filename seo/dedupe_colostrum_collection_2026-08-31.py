#!/usr/bin/env python3
"""
Usuwa z indeksu osierocony duplikat /collections/colostrum-1.

Stan zastany (2026-08-31):
  - colostrum-1 "Colostrum", 54 produkty, opublikowana 2026-07-28
  - /collections/colostrum "Colostrum", 57 produktow - #1 landing page w organicu
  - duplikat: HTTP 200, self-canonical, obecny w sitemapie, zero linkow
    wewnetrznych, ZERO sesji w GA4 przez 180 dni (wszystkie kanaly)

Dzialanie:
  1. backup pelnego JSON kolekcji do artefaktu
  2. depublikacja (published=false) -> storefront zaczyna zwracac 404
  3. przekierowanie /collections/colostrum-1 -> /collections/colostrum

Kolejnosc jest istotna: przekierowania Shopify uruchamiaja sie WYLACZNIE na 404,
wiec dopoki kolekcja zwraca 200, redirect bylby ignorowany.

REST, nie GraphQL - GraphQL urlRedirects i publications zwracaja ACCESS_DENIED,
natomiast REST redirects.json korzysta z write_content, a custom_collections
z write_products. Oba scope'y token posiada.

Domyslnie dry-run. Zapis: --live. Cofniecie: --rollback --live
"""

import os
import sys
import json
import time
import datetime
import requests
from dotenv import load_dotenv

BASE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE, '..', '.env'))

SHOP = os.environ["SHOPIFY_DOMAIN"]
TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]
API = f"https://{SHOP}/admin/api/2025-01"
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

DUP_ID = 688374645068
DUP_HANDLE = "colostrum-1"
DUP_PRODUCTS = 54
CANON_PATH = "/collections/colostrum"
DUP_PATH = "/collections/colostrum-1"
BACKUP = os.path.join(BASE, "artefakty", f"colostrum-1-backup-{DUP_ID}.json")


def get(path, **kw):
    r = requests.get(f"{API}/{path}", headers=HEADERS, timeout=30, **kw)
    r.raise_for_status()
    return r.json()


def storefront(path):
    r = requests.get(f"https://genactiv.pl{path}", allow_redirects=False, timeout=30)
    return r.status_code, r.headers.get("Location", "")


def find_redirect():
    for r in get("redirects.json", params={"path": DUP_PATH}).get("redirects", []):
        if r["path"] == DUP_PATH:
            return r
    return None


def main():
    live = "--live" in sys.argv
    rollback = "--rollback" in sys.argv
    print(f"Tryb: {'ROLLBACK' if rollback else 'WDROZENIE'} / "
          f"{'ZAPIS NA PRODUKCJI' if live else 'DRY-RUN (bez zapisu)'}\n")

    col = get(f"custom_collections/{DUP_ID}.json")["custom_collection"]

    # Zabezpieczenie: nie ruszaj niczego, jesli to nie jest ta kolekcja.
    if col["handle"] != DUP_HANDLE:
        print(f"PRZERWANIE: handle to '{col['handle']}', oczekiwano '{DUP_HANDLE}'")
        return 1
    count = get(f"collections/{DUP_ID}/products.json", params={"limit": 250})["products"]
    if len(count) != DUP_PRODUCTS:
        print(f"PRZERWANIE: kolekcja ma {len(count)} produktow, oczekiwano {DUP_PRODUCTS}. "
              "Zawartosc sie zmienila - zweryfikuj recznie.")
        return 1

    print(f"Cel   : {col['handle']} (id {col['id']}, {len(count)} produktow)")
    print(f"        published_at={col['published_at']} scope={col['published_scope']}")
    code, loc = storefront(DUP_PATH)
    print(f"        storefront teraz: HTTP {code}{' -> ' + loc if loc else ''}")
    ccode, _ = storefront(CANON_PATH)
    print(f"Kanon : {CANON_PATH} -> HTTP {ccode}")
    if ccode != 200:
        print("PRZERWANIE: kolekcja kanoniczna nie zwraca 200. Nie przekierowuje w prozne.")
        return 1

    existing = find_redirect()
    print(f"Redirect istniejacy: {existing if existing else 'brak'}\n")

    if rollback:
        print("Plan cofniecia:")
        print(f"  1. usun redirect {DUP_PATH}" + (f" (id {existing['id']})" if existing else " - brak, pomijam"))
        print(f"  2. przywroc published=true na kolekcji {DUP_ID}")
        if live:
            if existing:
                requests.delete(f"{API}/redirects/{existing['id']}.json", headers=HEADERS, timeout=30).raise_for_status()
                print("  redirect usuniety")
            requests.put(f"{API}/custom_collections/{DUP_ID}.json", headers=HEADERS, timeout=30,
                         json={"custom_collection": {"id": DUP_ID, "published": True}}).raise_for_status()
            print("  kolekcja przywrocona")
        else:
            print("\nNic nie zmieniono.")
        return 0

    print("Plan wdrozenia:")
    print(f"  1. backup -> {os.path.relpath(BACKUP, BASE)}")
    print(f"  2. published=false na kolekcji {DUP_ID} (storefront: 200 -> 404)")
    print(f"  3. redirect {DUP_PATH} -> {CANON_PATH}"
          + (" (JUZ ISTNIEJE, pomijam)" if existing else ""))

    if not live:
        print("\nNic nie zapisano. Uruchom z --live aby wdrozyc.")
        return 0

    os.makedirs(os.path.dirname(BACKUP), exist_ok=True)
    with open(BACKUP, "w", encoding="utf-8") as f:
        json.dump({"pobrano": datetime.datetime.now().isoformat(),
                   "custom_collection": col}, f, ensure_ascii=False, indent=2)
    print(f"\n  backup zapisany ({os.path.getsize(BACKUP)} B)")

    requests.put(f"{API}/custom_collections/{DUP_ID}.json", headers=HEADERS, timeout=30,
                 json={"custom_collection": {"id": DUP_ID, "published": False}}).raise_for_status()
    print("  depublikacja OK")

    if not existing:
        r = requests.post(f"{API}/redirects.json", headers=HEADERS, timeout=30,
                          json={"redirect": {"path": DUP_PATH, "target": CANON_PATH}})
        r.raise_for_status()
        print(f"  redirect utworzony (id {r.json()['redirect']['id']})")

    print("\n  czekam na propagacje...")
    time.sleep(8)
    code, loc = storefront(DUP_PATH)
    ccode, _ = storefront(CANON_PATH)
    print(f"  WERYFIKACJA {DUP_PATH}: HTTP {code}{' -> ' + loc if loc else ''}")
    print(f"  WERYFIKACJA {CANON_PATH}: HTTP {ccode}")

    good = code in (301, 302) and CANON_PATH in loc and ccode == 200
    print("\n  WYNIK: " + ("OK" if good else
          "niezgodny - sprawdz recznie, ewentualnie --rollback --live"))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())

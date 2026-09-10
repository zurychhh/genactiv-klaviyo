#!/usr/bin/env python3
"""
Uzupelnia brakujace meta title + description na kolekcjach Fiberbiom i Outlet.

Kontekst: audyt 2026-08-31 wykazal 6 kolekcji bez metadanych. Trzy z nich
(omnibus-label-*) zwracaja 404 na storefroncie - nie sa opublikowane, wiec nie
sa indeksowalne i nie wymagaja zmian. Czwarta (colostrum-1) to osierocony
duplikat /collections/colostrum i wymaga decyzji, nie metadanych.

Zgodnie z semantyka SEOInput ZAWSZE wysylamy title I description naraz -
pominiecie pola czysci je do null, a nie zachowuje.

Domyslnie dry-run. Zapis: --live
"""

import os
import sys
import json
import requests
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SHOP = os.environ["SHOPIFY_DOMAIN"]
TOKEN = os.environ["SHOPIFY_ACCESS_TOKEN"]
API_VERSION = "2025-01"
URL = f"https://{SHOP}/admin/api/{API_VERSION}/graphql.json"
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}

TARGETS = {
    "687888138572": {
        "handle": "fiberbiom",
        "title": "Fiberbiom – błonnik z colostrum na jelita | Genactiv",
        "description": (
            "Fiberbiom Genactiv – połączenie błonnika i colostrum bovinum "
            "wspierające pracę jelit i mikrobiotę. Poznaj całą linię Fiberbiom."
        ),
    },
    "688048341324": {
        "handle": "outlet",
        "title": "Outlet Genactiv – colostrum i kosmetyki w niższych cenach",
        "description": (
            "Outlet Genactiv – suplementy z colostrum i kosmetyki w obniżonych "
            "cenach. Oferta ograniczona dostępnością, sprawdź aktualne okazje."
        ),
    },
}

READ = """
query($id: ID!) {
  collection(id: $id) { id title handle seo { title description } }
}
"""

WRITE = """
mutation($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { id title handle seo { title description } }
    userErrors { field message }
  }
}
"""


def gql(query, variables):
    r = requests.post(URL, json={"query": query, "variables": variables}, headers=HEADERS, timeout=30)
    r.raise_for_status()
    body = r.json()
    if "errors" in body:
        raise RuntimeError(json.dumps(body["errors"])[:400])
    return body["data"]


def main():
    live = "--live" in sys.argv
    print(f"Tryb: {'ZAPIS NA PRODUKCJI' if live else 'DRY-RUN (bez zapisu)'}\n")

    ok = True
    for cid, spec in TARGETS.items():
        gid = f"gid://shopify/Collection/{cid}"
        before = gql(READ, {"id": gid})["collection"]

        if before["handle"] != spec["handle"]:
            print(f"  PRZERWANIE: {cid} ma handle '{before['handle']}', oczekiwano '{spec['handle']}'")
            return 1

        lt, ld = len(spec["title"]), len(spec["description"])
        print(f"[{before['handle']}] {before['title']}")
        print(f"  PRZED  title: {before['seo']['title']!r}")
        print(f"  PRZED  desc : {before['seo']['description']!r}")
        print(f"  PO     title ({lt:>3} zn.): {spec['title']}")
        print(f"  PO     desc  ({ld:>3} zn.): {spec['description']}")

        if not (50 <= lt <= 60):
            print(f"  UWAGA: title poza zakresem 50-60 znakow ({lt})")
            ok = False
        if not (120 <= ld <= 160):
            print(f"  UWAGA: description poza zakresem 120-160 znakow ({ld})")
            ok = False

        if live:
            data = gql(WRITE, {"input": {
                "id": gid,
                "seo": {"title": spec["title"], "description": spec["description"]},
            }})
            errs = data["collectionUpdate"]["userErrors"]
            if errs:
                print(f"  BLAD: {errs}")
                ok = False
            else:
                after = gql(READ, {"id": gid})["collection"]
                match = (after["seo"]["title"] == spec["title"]
                         and after["seo"]["description"] == spec["description"])
                print(f"  ZAPISANO, weryfikacja odczytem: {'OK' if match else 'NIEZGODNOSC'}")
                ok = ok and match
        print()

    if not live:
        print("Nic nie zapisano. Uruchom z --live aby wdrozyc.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

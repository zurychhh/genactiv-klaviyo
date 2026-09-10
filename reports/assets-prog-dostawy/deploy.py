#!/usr/bin/env python3
"""Wdraza pasek postepu do darmowej dostawy na wskazany motyw Shopify.

    python3 deploy.py <THEME_ID>            # dry-run (domyslnie)
    python3 deploy.py <THEME_ID> --live     # faktyczny zapis
    python3 deploy.py <THEME_ID> --rollback # przywraca pliki z backupu

Idempotentny: jesli include juz jest w pliku, pomija go.
Nie dotyka config/settings_data.json — snippet sam radzi sobie ze zlymi
etykietami w ustawieniach motywu.
"""
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, "..", "..", ".env"))

DOMAIN = os.getenv("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API = "2025-01"
H = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
BACKUP = os.path.join(HERE, "backup-live-2026-08-27")

SNIPPETS = [
    ("snippets/genactiv-free-shipping.liquid", "genactiv-free-shipping.liquid"),
    ("snippets/genactiv-cart-boost.liquid", "genactiv-cart-boost.liquid"),
]
INCLUDE = "{% include 'genactiv-free-shipping' %}"
# rekomendacje: tylko na stronie koszyka, w drawerze za malo miejsca
INCLUDE_BOOST = "{% include 'genactiv-cart-boost' %}"

# Kotwica w cart-template.liquid: zaraz pod naglowkiem "Twoj koszyk", NAD lista
# produktow. Panel podsumowania na mobile ladwie pod lista — modul tam znikal.
ANCHOR_TEMPLATE = """    <div class="cart-header">
      <h1 class="cart-header__title">{{ 'cart.general.title' | t }}</h1>
    </div>
"""
# Kotwica 1 w cart-drawer.liquid: pasek postepu, na gorze panelu
ANCHOR_DRAWER = """            <span class="cart__free-shipping-message">
              {{ settings.free_shipping_message }}
            </span>
          </div>
        {% endif %}
"""
# Kotwica 2 w cart-drawer.liquid: rekomendacje pod tekstem o podatku,
# NAD szarym blokiem z ikonami platnosci i dostawy
ANCHOR_DRAWER_BOOST = """        <div class="cart__shipping rte">{{ taxes_shipping_checkout }}</div>
"""
INCLUDE_BOOST_COMPACT = "{% include 'genactiv-cart-boost', compact: true %}"


def get_asset(theme, key):
    r = requests.get(f"https://{DOMAIN}/admin/api/{API}/themes/{theme}/assets.json",
                     headers=H, params={"asset[key]": key})
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json()["asset"]["value"]


def put_asset(theme, key, value, live):
    if not live:
        print(f"      [DRY-RUN] pominieto zapis {key} ({len(value.encode())} B)")
        return
    r = requests.put(f"https://{DOMAIN}/admin/api/{API}/themes/{theme}/assets.json",
                     headers=H, json={"asset": {"key": key, "value": value}})
    r.raise_for_status()
    print(f"      ZAPISANO {key} ({len(value.encode())} B)")
    time.sleep(0.4)


def patch(src, anchor, label, payload=None, marker=None):
    payload = payload or INCLUDE
    if (marker or INCLUDE) in src:
        print(f"      {label}: include juz obecny — pomijam")
        return src, False
    n = src.count(anchor)
    if n != 1:
        raise SystemExit(f"BLAD: kotwica w {label} wystapila {n}x (oczekiwano 1). Przerywam.")
    indent = " " * (len(anchor.split("\n")[0]) - len(anchor.split("\n")[0].lstrip()))
    out = src.replace(anchor, anchor + "\n" + indent + payload + "\n")
    print(f"      {label}: include wstawiony")
    return out, True


def rollback(theme, live):
    print(f"\nROLLBACK motywu {theme} z {BACKUP}")
    for key, fn in [("sections/cart-template.liquid", "sections__cart-template.liquid"),
                    ("sections/cart-drawer.liquid", "sections__cart-drawer.liquid")]:
        val = open(os.path.join(BACKUP, fn)).read()
        put_asset(theme, key, val, live)
    print("   snippet zostaje (jest nieaktywny bez include) — usun recznie, jesli chcesz")


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    theme = sys.argv[1]
    live = "--live" in sys.argv
    print("=" * 66)
    print(f"MOTYW {theme}   tryb: {'LIVE (zapis)' if live else 'DRY-RUN'}")
    print("=" * 66)

    if "--rollback" in sys.argv:
        rollback(theme, live)
        return

    print("\n[1/3] snippety")
    for key, fn in SNIPPETS:
        put_asset(theme, key, open(os.path.join(HERE, fn)).read(), live)

    print("\n[2/3] sections/cart-template.liquid")
    src = get_asset(theme, "sections/cart-template.liquid")
    out, changed = patch(src, ANCHOR_TEMPLATE, "cart-template",
                         INCLUDE + "\n" + " " * 4 + INCLUDE_BOOST)
    if changed:
        put_asset(theme, "sections/cart-template.liquid", out, live)

    print("\n[3/3] sections/cart-drawer.liquid")
    src = get_asset(theme, "sections/cart-drawer.liquid")
    out, ch1 = patch(src, ANCHOR_DRAWER, "cart-drawer / pasek")
    out, ch2 = patch(out, ANCHOR_DRAWER_BOOST, "cart-drawer / rekomendacje",
                     INCLUDE_BOOST_COMPACT, marker=INCLUDE_BOOST_COMPACT)
    if ch1 or ch2:
        put_asset(theme, "sections/cart-drawer.liquid", out, live)

    print("\nGOTOWE." if live else "\nDRY-RUN zakonczony — nic nie zapisano.")
    print(f"Podglad: https://{DOMAIN.replace('.myshopify.com','')}.myshopify.com"
          f"/?preview_theme_id={theme}")


if __name__ == "__main__":
    main()

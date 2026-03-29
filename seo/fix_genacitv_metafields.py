#!/usr/bin/env python3
"""
Fix GENACITV → GENACTIV typo in Shopify product metafields
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SHOP = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

HEADERS = {
    "X-Shopify-Access-Token": TOKEN,
    "Content-Type": "application/json"
}

# Products with GENACITV typo in metafields
PRODUCTS_TO_FIX = {
    "furever-horse-proszek-5500-g": "15338216522060",
    "furever-horse-proszek-2500-g": "15338216587596",
    "furever-dog-proszek-100-g": "15338216718668",
    "furever-dog-120-kapsulek": "15338216784204",
    "furever-dog-60-kapsulek": "15338216816972",
    "furever-cat-proszek-75g": "15338216882508",
    "furever-cat-90-kapsulek": "15338216948044",
    "furever-horse": "15338217046348",
    "furever-cat": "15338217079116",
    "furever-dog": "15338217111884",
    "all-furever-30-kapsulek": "15402702864716",
    "all-furever-90-kapsulek": "15402831020364",
    "all-furever-proszek-50-g": "15402833740108",
}


def get_product_metafields(product_id):
    """Get all metafields for a product"""
    url = f"https://{SHOP}/admin/api/{API_VERSION}/products/{product_id}/metafields.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("metafields", [])
    return []


def update_metafield(metafield_id, new_value):
    """Update a metafield value"""
    url = f"https://{SHOP}/admin/api/{API_VERSION}/metafields/{metafield_id}.json"
    data = {
        "metafield": {
            "id": metafield_id,
            "value": new_value
        }
    }
    response = requests.put(url, headers=HEADERS, json=data)
    return response.status_code == 200, response


def fix_typo_in_value(value):
    """Replace GENACITV with GENACTIV in a value"""
    if isinstance(value, str):
        return value.replace("GENACITV", "GENACTIV").replace("Genacitv", "Genactiv").replace("genacitv", "genactiv")
    return value


def has_typo(value):
    """Check if value contains the typo"""
    if isinstance(value, str):
        return "GENACITV" in value or "Genacitv" in value or "genacitv" in value
    return False


def fix_all_metafields():
    """Fix GENACITV typo in all product metafields"""

    results = {
        "fixed": [],
        "no_change_needed": [],
        "errors": []
    }

    print("=" * 60)
    print("POPRAWIANIE LITERÓWKI W METAFIELDS: GENACITV → GENACTIV")
    print("=" * 60)

    for handle, product_id in PRODUCTS_TO_FIX.items():
        print(f"\n[{handle}]")

        metafields = get_product_metafields(product_id)
        if not metafields:
            print(f"  → Brak metafields")
            continue

        product_fixed = False
        for mf in metafields:
            mf_id = mf["id"]
            mf_key = f"{mf['namespace']}.{mf['key']}"
            mf_value = mf["value"]

            if has_typo(mf_value):
                print(f"  → Znaleziono literówkę w {mf_key}")

                new_value = fix_typo_in_value(mf_value)
                success, response = update_metafield(mf_id, new_value)

                if success:
                    print(f"    ✅ Poprawiono metafield {mf_key}")
                    product_fixed = True
                    results["fixed"].append({
                        "handle": handle,
                        "metafield": mf_key,
                        "metafield_id": mf_id
                    })
                else:
                    print(f"    ❌ Błąd: {response.status_code}")
                    results["errors"].append({
                        "handle": handle,
                        "metafield": mf_key,
                        "error": response.text[:200]
                    })

                time.sleep(0.3)

        if not product_fixed:
            # Check if any metafield had typo
            had_typo = any(has_typo(mf["value"]) for mf in metafields)
            if not had_typo:
                print(f"  → Brak literówki w metafields")
                results["no_change_needed"].append(handle)

    # Summary
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    print(f"Poprawiono metafields: {len(results['fixed'])}")
    print(f"Produkty bez zmian: {len(results['no_change_needed'])}")
    print(f"Błędy: {len(results['errors'])}")

    if results["fixed"]:
        print("\nPoprawione metafields:")
        for item in results["fixed"]:
            print(f"  - {item['handle']}: {item['metafield']}")

    if results["errors"]:
        print("\nBłędy:")
        for item in results["errors"]:
            print(f"  - {item['handle']}: {item['metafield']} - {item['error']}")

    return results


if __name__ == "__main__":
    fix_all_metafields()

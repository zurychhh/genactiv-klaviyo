#!/usr/bin/env python3
"""
Fix GENACITV → GENACTIV typo in Shopify product descriptions
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

# Products with GENACITV typo (handle → ID mapping)
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
    "maska-z-colostrum-genactiv-250-ml": "7382565879982",
}


def get_product(product_id):
    """Get product details including body_html"""
    url = f"https://{SHOP}/admin/api/{API_VERSION}/products/{product_id}.json"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json().get("product")
    else:
        print(f"Error getting product {product_id}: {response.status_code}")
        return None


def update_product_description(product_id, new_body_html, new_title=None):
    """Update product body_html (description)"""
    url = f"https://{SHOP}/admin/api/{API_VERSION}/products/{product_id}.json"

    data = {
        "product": {
            "id": product_id,
            "body_html": new_body_html
        }
    }

    if new_title:
        data["product"]["title"] = new_title

    response = requests.put(url, headers=HEADERS, json=data)
    return response.status_code == 200, response


def fix_genacitv_typo():
    """Fix GENACITV → GENACTIV in all affected products"""

    results = {
        "fixed": [],
        "no_change_needed": [],
        "errors": []
    }

    print("=" * 60)
    print("POPRAWIANIE LITERÓWKI: GENACITV → GENACTIV")
    print("=" * 60)

    for handle, product_id in PRODUCTS_TO_FIX.items():
        print(f"\n[{handle}]")

        # Get current product
        product = get_product(product_id)
        if not product:
            results["errors"].append({"handle": handle, "error": "Nie można pobrać produktu"})
            continue

        body_html = product.get("body_html", "") or ""
        title = product.get("title", "")

        # Check if typo exists
        has_typo_in_body = "GENACITV" in body_html or "Genacitv" in body_html or "genacitv" in body_html
        has_typo_in_title = "GENACITV" in title or "Genacitv" in title or "genacitv" in title

        if not has_typo_in_body and not has_typo_in_title:
            print(f"  → Brak literówki, pomijam")
            results["no_change_needed"].append(handle)
            continue

        # Fix typo
        new_body_html = body_html.replace("GENACITV", "GENACTIV").replace("Genacitv", "Genactiv").replace("genacitv", "genactiv")
        new_title = None
        if has_typo_in_title:
            new_title = title.replace("GENACITV", "GENACTIV").replace("Genacitv", "Genactiv").replace("genacitv", "genactiv")

        # Count replacements
        replacements = body_html.count("GENACITV") + body_html.count("Genacitv") + body_html.count("genacitv")
        if has_typo_in_title:
            replacements += title.count("GENACITV") + title.count("Genacitv") + title.count("genacitv")

        print(f"  → Znaleziono {replacements} wystąpień literówki")

        # Update product
        success, response = update_product_description(product_id, new_body_html, new_title)

        if success:
            print(f"  ✅ Poprawiono!")
            results["fixed"].append({
                "handle": handle,
                "product_id": product_id,
                "replacements": replacements,
                "title_fixed": has_typo_in_title
            })
        else:
            print(f"  ❌ Błąd: {response.status_code} - {response.text[:200]}")
            results["errors"].append({
                "handle": handle,
                "error": f"{response.status_code}: {response.text[:200]}"
            })

        time.sleep(0.5)  # Rate limiting

    # Summary
    print("\n" + "=" * 60)
    print("PODSUMOWANIE")
    print("=" * 60)
    print(f"Poprawiono: {len(results['fixed'])} produktów")
    print(f"Bez zmian: {len(results['no_change_needed'])} produktów")
    print(f"Błędy: {len(results['errors'])} produktów")

    if results["fixed"]:
        print("\nPoprawione produkty:")
        for item in results["fixed"]:
            title_note = " (+ tytuł)" if item.get("title_fixed") else ""
            print(f"  - {item['handle']}: {item['replacements']} zamian{title_note}")

    if results["errors"]:
        print("\nBłędy:")
        for item in results["errors"]:
            print(f"  - {item['handle']}: {item['error']}")

    return results


if __name__ == "__main__":
    fix_genacitv_typo()

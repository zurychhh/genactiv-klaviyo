#!/usr/bin/env python3
"""
Synchronizacja Payment ID między Shopify a Baselinker

Ten skrypt:
1. Pobiera zamówienia z Baselinker (które nie mają external_payment_id)
2. Znajduje odpowiadające zamówienia w Shopify
3. Pobiera Payment ID z transakcji Shopify
4. Ustawia external_payment_id w Baselinker
"""

import requests
import json
import os
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

load_dotenv()

# ============== KONFIGURACJA ==============
SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
SHOPIFY_API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

BASELINKER_TOKEN = os.environ.get("BASELINKER_TOKEN", "")
BASELINKER_URL = "https://api.baselinker.com/connector.php"

# ============== SHOPIFY API ==============
def shopify_graphql(query, variables=None):
    """Wykonaj zapytanie GraphQL do Shopify"""
    endpoint = f"https://{SHOPIFY_DOMAIN}/admin/api/{SHOPIFY_API_VERSION}/graphql.json"
    headers = {
        "Content-Type": "application/json",
        "X-Shopify-Access-Token": SHOPIFY_TOKEN
    }
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(endpoint, headers=headers, json=payload)
    return response.json()

def get_shopify_order_payment_id(order_number):
    """Pobierz Payment ID dla zamówienia Shopify po numerze"""
    # Shopify order name format: #00059138
    # Baselinker shop_order_id: 59138
    # Szukamy po różnych formatach

    # Spróbuj z zerem z przodu (format Shopify: 00059138)
    padded = str(order_number).zfill(8)  # 59138 -> 00059138

    query = f'''
    query {{
      orders(first: 1, query: "name:#{padded} OR name:{order_number}") {{
        edges {{
          node {{
            id
            name
            transactions(first: 5) {{
              status
              gateway
              paymentId
            }}
          }}
        }}
      }}
    }}
    '''

    result = shopify_graphql(query)

    if result.get("data", {}).get("orders", {}).get("edges"):
        order = result["data"]["orders"]["edges"][0]["node"]
        transactions = order.get("transactions", [])

        # Znajdź udaną transakcję
        for txn in transactions:
            if txn.get("status") == "SUCCESS" and txn.get("paymentId"):
                return {
                    "shopify_name": order.get("name"),
                    "payment_id": txn.get("paymentId"),
                    "gateway": txn.get("gateway")
                }

    return None

# ============== BASELINKER API ==============
def baselinker_call(method, parameters=None):
    """Wywołaj metodę Baselinker API"""
    payload = {
        "token": BASELINKER_TOKEN,
        "method": method,
        "parameters": json.dumps(parameters or {})
    }

    response = requests.post(BASELINKER_URL, data=payload)

    if response.status_code != 200:
        return {"status": "ERROR", "error_message": f"HTTP {response.status_code}"}

    return response.json()

def get_baselinker_orders(days=7):
    """Pobierz zamówienia z Baselinker z ostatnich X dni"""
    date_from = int((datetime.now() - timedelta(days=days)).timestamp())

    result = baselinker_call("getOrders", {"date_from": date_from})

    if result.get("status") == "SUCCESS" or "orders" in result:
        return result.get("orders", [])
    return []

def get_order_payment_history(order_id):
    """Pobierz historię płatności zamówienia"""
    result = baselinker_call("getOrderPaymentsHistory", {"order_id": order_id})
    return result.get("payments", [])

def set_payment_id(order_id, payment_done, external_payment_id):
    """Ustaw external_payment_id dla zamówienia w Baselinker"""
    params = {
        "order_id": order_id,
        "payment_done": payment_done,
        "external_payment_id": external_payment_id[:30]  # max 30 znaków
    }

    result = baselinker_call("setOrderPayment", params)
    return result.get("status") == "SUCCESS"

# ============== SYNCHRONIZACJA ==============
def sync_payment_ids(days=7, dry_run=True, limit=10):
    """
    Synchronizuj Payment ID między Shopify a Baselinker

    Args:
        days: ile dni wstecz sprawdzać
        dry_run: jeśli True, tylko pokaże co zrobi (bez zmian)
    """
    print("=" * 60)
    print("SYNCHRONIZACJA PAYMENT ID: Shopify -> Baselinker")
    print("=" * 60)
    print(f"Tryb: {'DRY RUN (bez zmian)' if dry_run else 'LIVE (zapisuje zmiany)'}")
    print(f"Okres: ostatnie {days} dni")
    print()

    # Pobierz zamówienia z Baselinker
    print("📦 Pobieranie zamówień z Baselinker...")
    orders = get_baselinker_orders(days)
    print(f"   Znaleziono: {len(orders)} zamówień")
    print()

    synced = 0
    skipped = 0
    errors = 0
    processed = 0

    for order in orders:
        if limit and processed >= limit:
            print(f"\n⏹️  Osiągnięto limit {limit} zamówień")
            break
        processed += 1
        bl_order_id = order.get("order_id")
        shop_order_id = order.get("shop_order_id")
        payment_done = order.get("payment_done", 0)
        payment_method = order.get("payment_method", "")
        email = order.get("email", "")

        # Sprawdź czy już ma external_payment_id
        payments = get_order_payment_history(bl_order_id)
        has_payment_id = any(p.get("external_payment_id") for p in payments)

        if has_payment_id:
            skipped += 1
            continue

        # Pobierz Payment ID z Shopify
        shopify_data = get_shopify_order_payment_id(shop_order_id)

        if not shopify_data:
            print(f"⚠️  BL#{bl_order_id} (Shop#{shop_order_id}) - nie znaleziono w Shopify")
            errors += 1
            continue

        payment_id = shopify_data.get("payment_id")

        if not payment_id:
            print(f"⚠️  BL#{bl_order_id} (Shop#{shop_order_id}) - brak Payment ID w Shopify")
            errors += 1
            continue

        # Synchronizuj
        print(f"✅ BL#{bl_order_id} | Shop#{shop_order_id} | {payment_method}")
        print(f"   Email: {email}")
        print(f"   Payment ID: {payment_id}")

        if not dry_run:
            success = set_payment_id(bl_order_id, payment_done, payment_id)
            if success:
                print(f"   → Zapisano w Baselinker!")
                synced += 1
            else:
                print(f"   → BŁĄD zapisu!")
                errors += 1
        else:
            print(f"   → [DRY RUN] Zostanie zapisane")
            synced += 1

        print()

        # Rate limiting
        time.sleep(0.5)

    print("=" * 60)
    print("PODSUMOWANIE:")
    print(f"   Zsynchronizowano: {synced}")
    print(f"   Pominięto (już mają ID): {skipped}")
    print(f"   Błędy: {errors}")
    print("=" * 60)

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        sync_payment_ids(days=1, dry_run=False, limit=None)
    else:
        print("Uruchamiam w trybie DRY RUN (bez zmian)")
        print("Aby zapisać zmiany, użyj: python sync_payment_id.py --live")
        print()
        sync_payment_ids(days=1, dry_run=True, limit=5)

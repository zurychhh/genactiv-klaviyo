#!/usr/bin/env python3
"""
Baselinker API Client
Pozwala na pobieranie zamówień i historii płatności
"""

import requests
import json
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja
BASELINKER_TOKEN = os.environ.get("BASELINKER_TOKEN", "")
BASELINKER_URL = "https://api.baselinker.com/connector.php"

def call_api(method, parameters=None):
    """Wywołaj metodę Baselinker API"""
    payload = {
        "token": BASELINKER_TOKEN,
        "method": method,
        "parameters": json.dumps(parameters or {})
    }

    response = requests.post(BASELINKER_URL, data=payload)

    if response.status_code != 200:
        print(f"HTTP Error: {response.status_code}")
        return None

    result = response.json()

    if result.get("status") == "ERROR":
        print(f"API Error: {result.get('error_code')} - {result.get('error_message')}")
        return None

    return result

def get_orders(limit=10, date_from=None):
    """Pobierz zamówienia"""
    if date_from is None:
        # Ostatnie 7 dni
        date_from = int((datetime.now() - timedelta(days=7)).timestamp())

    params = {
        "date_from": date_from,
        "get_unconfirmed_orders": True
    }

    return call_api("getOrders", params)

def get_order_payments_history(order_id):
    """Pobierz historię płatności dla zamówienia"""
    params = {
        "order_id": order_id
    }

    return call_api("getOrderPaymentsHistory", params)

def get_order_sources():
    """Pobierz źródła zamówień (sklepy, marketplace)"""
    return call_api("getOrderSources")

def print_json(data):
    """Wyświetl JSON w czytelnym formacie"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    import sys

    print("=" * 60)
    print("BASELINKER API CLIENT")
    print("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "orders":
            print("\n📦 Pobieranie zamówień z ostatnich 7 dni...\n")
            result = get_orders()
            if result:
                orders = result.get("orders", [])
                print(f"Znaleziono {len(orders)} zamówień\n")

                # Pokaż podstawowe info o zamówieniach
                for order in orders[:10]:
                    order_id = order.get("order_id")
                    shop_order_id = order.get("shop_order_id")
                    payment_method = order.get("payment_method")
                    payment_done = order.get("payment_done")
                    total = order.get("order_page")

                    print(f"ID: {order_id} | Shop: {shop_order_id} | Płatność: {payment_method} | Zapłacono: {payment_done}")

                print("\n--- Pełne dane pierwszego zamówienia ---")
                if orders:
                    print_json(orders[0])

        elif command == "payments" and len(sys.argv) > 2:
            order_id = int(sys.argv[2])
            print(f"\n💳 Pobieranie historii płatności dla zamówienia {order_id}...\n")
            result = get_order_payments_history(order_id)
            print_json(result)

        elif command == "sources":
            print("\n🏪 Pobieranie źródeł zamówień...\n")
            result = get_order_sources()
            print_json(result)

        elif command == "full":
            print("\n📦 Pobieranie zamówień z pełnymi danymi płatności...\n")
            orders_result = get_orders()
            if orders_result:
                orders = orders_result.get("orders", [])
                print(f"Znaleziono {len(orders)} zamówień\n")

                for order in orders[:5]:
                    order_id = order.get("order_id")
                    shop_order_id = order.get("shop_order_id")
                    payment_method = order.get("payment_method")

                    print(f"\n{'='*50}")
                    print(f"Zamówienie: {shop_order_id} (BL ID: {order_id})")
                    print(f"Metoda płatności: {payment_method}")

                    # Pobierz historię płatności
                    payments = get_order_payments_history(order_id)
                    if payments:
                        print("Historia płatności:")
                        print_json(payments)

        else:
            print("Użycie:")
            print("  python baselinker_api.py orders           - pobierz zamówienia")
            print("  python baselinker_api.py payments <ID>    - pobierz historię płatności")
            print("  python baselinker_api.py sources          - pobierz źródła zamówień")
            print("  python baselinker_api.py full             - zamówienia + płatności")

    else:
        # Domyślnie: pokaż zamówienia
        print("\n📦 Pobieranie zamówień...\n")
        result = get_orders()
        if result:
            print_json(result)

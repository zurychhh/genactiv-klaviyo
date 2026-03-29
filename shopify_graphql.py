#!/usr/bin/env python3
"""
Shopify GraphQL API Client
Pozwala na wykonywanie dowolnych zapytań GraphQL do Shopify Admin API
"""

import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja
SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

ENDPOINT = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}/graphql.json"

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def execute_query(query, variables=None):
    """Wykonaj zapytanie GraphQL"""
    payload = {"query": query}
    if variables:
        payload["variables"] = variables

    response = requests.post(ENDPOINT, headers=HEADERS, json=payload)

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

    return response.json()

def get_orders_with_transactions(limit=5):
    """Pobierz zamówienia z pełnymi danymi transakcji"""
    query = """
    query GetOrdersWithTransactions($first: Int!) {
      orders(first: $first, sortKey: CREATED_AT, reverse: true) {
        edges {
          node {
            id
            name
            createdAt
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
            displayFinancialStatus
            paymentGatewayNames
            transactions(first: 10) {
              id
              kind
              status
              gateway
              formattedGateway
              createdAt
              amountSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
              paymentId
              receiptJson
              paymentDetails {
                ... on CardPaymentDetails {
                  company
                  number
                }
              }
            }
            customer {
              email
              firstName
              lastName
            }
          }
        }
      }
    }
    """
    return execute_query(query, {"first": limit})

def get_single_order_transactions(order_id):
    """Pobierz szczegóły transakcji dla konkretnego zamówienia"""
    # order_id format: gid://shopify/Order/1234567890
    query = """
    query GetOrderTransactions($id: ID!) {
      order(id: $id) {
        id
        name
        createdAt
        displayFinancialStatus
        paymentGatewayNames
        transactions(first: 10) {
          id
          kind
          status
          gateway
          formattedGateway
          createdAt
          amountSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          paymentId
          receiptJson
          authorizationCode
          errorCode
          parentTransaction {
            id
          }
        }
      }
    }
    """
    return execute_query(query, {"id": order_id})

def get_installed_apps():
    """Pobierz listę zainstalowanych aplikacji"""
    query = """
    query GetInstalledApps {
      currentAppInstallation {
        id
        app {
          title
          handle
          apiKey
        }
      }
      appInstallations(first: 50) {
        edges {
          node {
            id
            app {
              id
              title
              handle
              developerName
              apiKey
            }
            launchUrl
            accessScopes {
              handle
              description
            }
          }
        }
      }
    }
    """
    return execute_query(query)

def print_json(data):
    """Wyświetl JSON w czytelnym formacie"""
    print(json.dumps(data, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    print("=" * 60)
    print("SHOPIFY GRAPHQL CLIENT")
    print("=" * 60)

    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "orders":
            print("\n📦 Pobieranie zamówień z transakcjami...\n")
            result = get_orders_with_transactions(5)
            print_json(result)

        elif command == "order" and len(sys.argv) > 2:
            order_id = sys.argv[2]
            print(f"\n📦 Pobieranie transakcji dla zamówienia {order_id}...\n")
            result = get_single_order_transactions(order_id)
            print_json(result)

        elif command == "apps":
            print("\n📱 Pobieranie zainstalowanych aplikacji...\n")
            result = get_installed_apps()
            print_json(result)

        else:
            print("Użycie:")
            print("  python shopify_graphql.py orders        - pobierz zamówienia z transakcjami")
            print("  python shopify_graphql.py order <ID>    - pobierz transakcje dla zamówienia")
            print("  python shopify_graphql.py apps          - pobierz zainstalowane aplikacje")
    else:
        # Domyślnie: pobierz zamówienia
        print("\n📦 Pobieranie ostatnich zamówień z transakcjami...\n")
        result = get_orders_with_transactions(5)
        print_json(result)

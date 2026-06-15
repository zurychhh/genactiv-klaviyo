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

def create_page(title, body_html, handle=None, is_published=False, seo_title=None, seo_description=None):
    """Utwórz nową stronę (Page) w Shopify"""
    query = """
    mutation pageCreate($page: PageCreateInput!) {
      pageCreate(page: $page) {
        page {
          id
          title
          handle
          isPublished
          createdAt
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    page_input = {
        "title": title,
        "body": body_html,
        "isPublished": is_published
    }
    if handle:
        page_input["handle"] = handle
    if seo_title or seo_description:
        page_input["metafields"] = []
        if seo_title:
            page_input["metafields"].append({
                "namespace": "global",
                "key": "title_tag",
                "value": seo_title,
                "type": "single_line_text_field"
            })
        if seo_description:
            page_input["metafields"].append({
                "namespace": "global",
                "key": "description_tag",
                "value": seo_description,
                "type": "single_line_text_field"
            })
    return execute_query(query, {"page": page_input})


def update_page(page_id, title=None, body_html=None, is_published=None):
    """Zaktualizuj istniejącą stronę w Shopify"""
    query = """
    mutation pageUpdate($id: ID!, $page: PageUpdateInput!) {
      pageUpdate(id: $id, page: $page) {
        page {
          id
          title
          handle
          isPublished
          updatedAt
        }
        userErrors {
          field
          message
        }
      }
    }
    """
    page_input = {}
    if title is not None:
        page_input["title"] = title
    if body_html is not None:
        page_input["body"] = body_html
    if is_published is not None:
        page_input["isPublished"] = is_published
    return execute_query(query, {"id": page_id, "page": page_input})


def delete_page(page_id):
    """Usuń stronę z Shopify"""
    query = """
    mutation pageDelete($id: ID!) {
      pageDelete(id: $id) {
        deletedPageId
        userErrors {
          field
          message
        }
      }
    }
    """
    return execute_query(query, {"id": page_id})


def list_pages(limit=20):
    """Pobierz listę stron"""
    query = """
    query GetPages($first: Int!) {
      pages(first: $first) {
        edges {
          node {
            id
            title
            handle
            isPublished
            createdAt
            updatedAt
            bodySummary
          }
        }
      }
    }
    """
    return execute_query(query, {"first": limit})


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

        elif command == "pages":
            print("\n📄 Pobieranie listy stron...\n")
            result = list_pages()
            print_json(result)

        elif command == "page-create" and len(sys.argv) > 3:
            title = sys.argv[2]
            html_file = sys.argv[3]
            handle = sys.argv[4] if len(sys.argv) > 4 else None
            publish = "--publish" in sys.argv

            with open(html_file, "r", encoding="utf-8") as f:
                body_html = f.read()

            print(f"\n📄 Tworzenie strony '{title}'...")
            if handle:
                print(f"   Handle: {handle}")
            print(f"   Publish: {publish}")
            print(f"   HTML size: {len(body_html)} chars\n")

            result = create_page(title, body_html, handle=handle, is_published=publish)
            print_json(result)

        elif command == "page-update" and len(sys.argv) > 2:
            page_id = sys.argv[2]
            html_file = sys.argv[3] if len(sys.argv) > 3 else None
            publish = "--publish" in sys.argv
            unpublish = "--unpublish" in sys.argv

            body_html = None
            if html_file and not html_file.startswith("--"):
                with open(html_file, "r", encoding="utf-8") as f:
                    body_html = f.read()

            is_published = True if publish else (False if unpublish else None)

            print(f"\n📄 Aktualizacja strony {page_id}...\n")
            result = update_page(page_id, body_html=body_html, is_published=is_published)
            print_json(result)

        elif command == "page-delete" and len(sys.argv) > 2:
            page_id = sys.argv[2]
            print(f"\n🗑️ Usuwanie strony {page_id}...\n")
            result = delete_page(page_id)
            print_json(result)

        else:
            print("Użycie:")
            print("  python shopify_graphql.py orders                          - zamówienia z transakcjami")
            print("  python shopify_graphql.py order <GID>                     - transakcje zamówienia")
            print("  python shopify_graphql.py apps                            - zainstalowane aplikacje")
            print("  python shopify_graphql.py pages                           - lista stron")
            print("  python shopify_graphql.py page-create <title> <html_file> [handle] [--publish]")
            print("  python shopify_graphql.py page-update <GID> [html_file] [--publish|--unpublish]")
            print("  python shopify_graphql.py page-delete <GID>")
    else:
        # Domyślnie: pobierz zamówienia
        print("\n📦 Pobieranie ostatnich zamówień z transakcjami...\n")
        result = get_orders_with_transactions(5)
        print_json(result)

#!/usr/bin/env python3
"""Pobiera zamowienia z Shopify na potrzeby analizy progu darmowej dostawy.

Zapisuje surowe dane do JSON, zeby analiza byla odtwarzalna bez ponownego
odpytywania API. Read-only.

Uwaga: token 'Claude MCP' nie ma scope read_all_orders -> API cicho ucina
wyniki do ~60 dni. Skrypt raportuje faktyczny zakres dat w zwroconych danych.
"""
import json
import os
import sys
import time

import requests
from dotenv import load_dotenv

load_dotenv()

DOMAIN = os.getenv("MYSHOPIFY_DOMAIN", "genactiv.myshopify.com")
TOKEN = os.getenv("SHOPIFY_ACCESS_TOKEN")
API_VERSION = "2025-01"
URL = f"https://{DOMAIN}/admin/api/{API_VERSION}/graphql.json"

QUERY = """
query Orders($first: Int!, $after: String, $q: String!) {
  orders(first: $first, after: $after, query: $q, sortKey: CREATED_AT, reverse: false) {
    pageInfo { hasNextPage endCursor }
    nodes {
      id
      name
      createdAt
      displayFinancialStatus
      cancelledAt
      subtotalPriceSet { shopMoney { amount } }
      totalShippingPriceSet { shopMoney { amount } }
      totalDiscountsSet { shopMoney { amount } }
      totalPriceSet { shopMoney { amount } }
      currentTotalPriceSet { shopMoney { amount } }
      totalRefundedSet { shopMoney { amount } }
      discountCodes
      tags
      shippingLine { title originalPriceSet { shopMoney { amount } } }
      customer { id numberOfOrders }
      lineItems(first: 30) {
        nodes {
          quantity
          originalUnitPriceSet { shopMoney { amount } }
          discountedTotalSet { shopMoney { amount } }
          product { id title productType }
        }
      }
    }
  }
}
"""


def fetch(date_from, date_to):
    headers = {"X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json"}
    q = f"created_at:>={date_from} created_at:<={date_to}"
    out, cursor = [], None
    while True:
        r = requests.post(
            URL,
            headers=headers,
            json={"query": QUERY, "variables": {"first": 100, "after": cursor, "q": q}},
            timeout=60,
        )
        r.raise_for_status()
        body = r.json()
        if "errors" in body:
            print("GraphQL errors:", json.dumps(body["errors"])[:500], file=sys.stderr)
            sys.exit(1)
        block = body["data"]["orders"]
        out.extend(block["nodes"])
        print(f"  pobrano {len(out)}...", file=sys.stderr)
        if not block["pageInfo"]["hasNextPage"]:
            break
        cursor = block["pageInfo"]["endCursor"]
        time.sleep(0.6)
    return out


if __name__ == "__main__":
    date_from = sys.argv[1] if len(sys.argv) > 1 else "2025-08-01"
    date_to = sys.argv[2] if len(sys.argv) > 2 else "2026-08-24"
    orders = fetch(date_from, date_to)
    dates = sorted(o["createdAt"][:10] for o in orders)
    print(f"\nZAMOWIEN: {len(orders)}", file=sys.stderr)
    print(f"ZADANY zakres:    {date_from} -> {date_to}", file=sys.stderr)
    if dates:
        print(f"FAKTYCZNY zakres: {dates[0]} -> {dates[-1]}", file=sys.stderr)
    path = os.path.join(os.path.dirname(__file__), "raw-orders-shipping-threshold.json")
    with open(path, "w") as f:
        json.dump(orders, f)
    print(f"zapisano -> {path}", file=sys.stderr)

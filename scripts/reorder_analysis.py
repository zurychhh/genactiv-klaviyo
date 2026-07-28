#!/usr/bin/env python3
"""
Reorder Interval Analysis for GenActiv.pl
Pulls historical orders with line items from Shopify GraphQL API,
calculates reorder intervals per product per customer.
"""

import requests
import json
import sys
import os
import time
from datetime import datetime, timedelta
from collections import defaultdict
from statistics import mean, median, mode, stdev
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

ENDPOINT = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}/graphql.json"

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

def execute_query(query, variables=None):
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    response = requests.post(ENDPOINT, headers=HEADERS, json=payload)
    if response.status_code != 200:
        print(f"Error: {response.status_code}", file=sys.stderr)
        print(response.text, file=sys.stderr)
        return None
    data = response.json()
    if "errors" in data:
        print(f"GraphQL errors: {json.dumps(data['errors'], indent=2)}", file=sys.stderr)
    return data

def fetch_all_orders_with_line_items(max_pages=100):
    """
    Fetch orders with line items, paginating through all available orders.
    Returns list of order dicts with customer email, date, and line items.
    """
    query = """
    query GetOrdersWithLineItems($first: Int!, $after: String) {
      orders(first: $first, sortKey: CREATED_AT, reverse: true, after: $after) {
        pageInfo {
          hasNextPage
          endCursor
        }
        edges {
          node {
            id
            name
            createdAt
            displayFinancialStatus
            customer {
              id
              email
            }
            lineItems(first: 50) {
              edges {
                node {
                  title
                  quantity
                  product {
                    id
                    title
                    handle
                  }
                  variant {
                    title
                    sku
                  }
                  originalUnitPriceSet {
                    shopMoney {
                      amount
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
    """

    all_orders = []
    cursor = None
    page = 0

    while page < max_pages:
        page += 1
        variables = {"first": 250}  # max allowed by Shopify
        if cursor:
            variables["after"] = cursor

        print(f"  Fetching page {page}... (cursor: {cursor[:20] if cursor else 'None'})", file=sys.stderr)

        result = execute_query(query, variables)
        if not result or "data" not in result:
            print(f"  Error on page {page}, stopping.", file=sys.stderr)
            break

        orders_data = result["data"]["orders"]
        edges = orders_data["edges"]

        if not edges:
            print(f"  No more orders on page {page}.", file=sys.stderr)
            break

        for edge in edges:
            node = edge["node"]
            # Skip non-paid orders
            if node["displayFinancialStatus"] not in ("PAID", "PARTIALLY_REFUNDED"):
                continue

            customer = node.get("customer")
            if not customer or not customer.get("email"):
                continue

            order = {
                "id": node["id"],
                "name": node["name"],
                "date": node["createdAt"],
                "customer_id": customer["id"],
                "customer_email": customer["email"].lower().strip(),
                "line_items": []
            }

            for li_edge in node["lineItems"]["edges"]:
                li = li_edge["node"]
                product = li.get("product")
                if not product:
                    continue

                price = 0
                if li.get("originalUnitPriceSet"):
                    price = float(li["originalUnitPriceSet"]["shopMoney"]["amount"])

                order["line_items"].append({
                    "product_id": product["id"],
                    "product_title": product["title"],
                    "product_handle": product.get("handle", ""),
                    "variant_title": li.get("variant", {}).get("title", "") if li.get("variant") else "",
                    "sku": li.get("variant", {}).get("sku", "") if li.get("variant") else "",
                    "quantity": li["quantity"],
                    "unit_price": price,
                    "line_title": li["title"]
                })

            if order["line_items"]:
                all_orders.append(order)

        first_date = edges[-1]["node"]["createdAt"][:10] if edges else "?"
        last_date = edges[0]["node"]["createdAt"][:10] if edges else "?"
        print(f"  Page {page}: {len(edges)} orders ({first_date} to {last_date}), total so far: {len(all_orders)}", file=sys.stderr)

        if not orders_data["pageInfo"]["hasNextPage"]:
            print(f"  No more pages after page {page}.", file=sys.stderr)
            break

        cursor = orders_data["pageInfo"]["endCursor"]
        time.sleep(0.5)  # Rate limiting

    return all_orders


def normalize_product_name(title, handle):
    """
    Group products into logical product families for reorder analysis.
    E.g., FIBERBIOM 30 saszetek and FIBERBIOM Dwupak should be in the same family
    for the purpose of understanding consumption patterns.
    """
    title_lower = title.lower()

    # FIBERBIOM family
    if "fiberbiom" in title_lower:
        if "ananas" in title_lower:
            base = "FIBERBIOM Z ANANASEM"
        elif "porzeczk" in title_lower:
            base = "FIBERBIOM Z CZARNA PORZECZKA"
        else:
            base = "FIBERBIOM (original)"

        # Determine unit count
        if "dwupak" in title_lower or "60 saszet" in title_lower:
            return base, 60
        elif "trojpak" in title_lower or "trójpak" in title_lower or "90 saszet" in title_lower:
            return base, 90
        else:
            return base, 30  # default single pack

    # Colostrum capsules family
    if "colostrum genactiv" in title_lower and ("kapsułek" in title_lower or "kapsulki" in title_lower or "kapsuł" in title_lower):
        if "mleko klaczy" in title_lower:
            base = "COLOSTRUM I MLEKO KLACZY kapsulki"
            if "dwupak" in title_lower or "360" in title_lower:
                return base, 360
            else:
                return base, 180
        if "dwupak" in title_lower and "240" in title_lower:
            return "COLOSTRUM GENACTIV kapsulki", 240
        if "trójpak" in title_lower or "trojpak" in title_lower or "180 kapsułek" in title_lower:
            return "COLOSTRUM GENACTIV kapsulki", 180
        if "120" in title_lower:
            return "COLOSTRUM GENACTIV kapsulki", 120
        if "60" in title_lower:
            return "COLOSTRUM GENACTIV kapsulki", 60
        return "COLOSTRUM GENACTIV kapsulki", 60  # fallback

    # Colostrum banana sachets
    if "colostrum" in title_lower and "banan" in title_lower:
        if "proszek" in title_lower and "200g" in title_lower:
            if "dwupak" in title_lower:
                return "COLOSTRUM Z BANANEM proszek", 400  # grams
            return "COLOSTRUM Z BANANEM proszek", 200
        if "dwupak" in title_lower:
            return "COLOSTRUM Z BANANEM saszetki", 60
        if "trójpak" in title_lower or "trojpak" in title_lower:
            return "COLOSTRUM Z BANANEM saszetki", 90
        return "COLOSTRUM Z BANANEM saszetki", 30

    # Colostrum brzoskwinia
    if "brzoskwini" in title_lower:
        return "Colostrum z brzoskwinia", 1

    # Colostrum czarna porzeczka
    if "colostrum" in title_lower and "porzeczk" in title_lower and "fiberbiom" not in title_lower:
        if "dwupak" in title_lower:
            return "COLOSTRUM Z CZARNA PORZECZKA", 60
        return "COLOSTRUM Z CZARNA PORZECZKA", 30

    # Colostrum malina
    if "colostrum" in title_lower and "malin" in title_lower:
        if "trójpak" in title_lower or "trojpak" in title_lower:
            return "COLOSTRUM Z MALINA tabletki", 180
        if "dwupak" in title_lower:
            return "COLOSTRUM Z MALINA tabletki", 120
        if "20" in title_lower:
            return "COLOSTRUM Z MALINA tabletki", 20
        return "COLOSTRUM Z MALINA tabletki", 60

    # Colostrum proszek (puszka)
    if "colostrum genactiv" in title_lower and "proszek" in title_lower:
        if "dwupak" in title_lower:
            return "COLOSTRUM GENACTIV proszek", 90  # grams equiv
        return "COLOSTRUM GENACTIV proszek", 45

    # Colostrum i mleko klaczy proszek
    if "colostrum i mleko klaczy" in title_lower and ("proszek" in title_lower or "200g" in title_lower):
        if "dwupak" in title_lower:
            return "COLOSTRUM I MLEKO KLACZY proszek", 400
        if "50g" in title_lower:
            return "COLOSTRUM I MLEKO KLACZY proszek", 50
        return "COLOSTRUM I MLEKO KLACZY proszek", 200

    # Colostrum zawiesina
    if "colostrum" in title_lower and "zawiesina" in title_lower and "junior" not in title_lower:
        if "dwupak" in title_lower:
            return "COLOSTRUM GENACTIV zawiesina", 300
        return "COLOSTRUM GENACTIV zawiesina", 150

    # Colostrum Junior
    if "junior" in title_lower:
        base = "COLOSTRUM JUNIOR"
        if "dwupak" in title_lower:
            return base, 2
        if "trójpak" in title_lower or "trojpak" in title_lower:
            return base, 3
        return base, 1

    # Colostrum A2
    if "a2" in title_lower:
        if "proszek" in title_lower:
            if "dwupak" in title_lower:
                return "Colostrum A2 proszek", 2
            return "Colostrum A2 proszek", 1
        if "dwupak" in title_lower:
            return "Colostrum A2 kapsulki", 2
        return "Colostrum A2 kapsulki", 1

    # Mleko klaczy
    if "mleko klaczy" in title_lower and "colostrum" not in title_lower:
        if "kapsułki" in title_lower or "kapsuł" in title_lower:
            return "MLEKO KLACZY kapsulki", 120
        if "dwupak" in title_lower:
            return "MLEKO KLACZY proszek", 300
        if "saszet" in title_lower:
            return "MLEKO KLACZY saszetki", 30
        return "MLEKO KLACZY proszek", 150

    # Cosmetics - don't normalize, keep as-is
    for cosmetic in ["krem", "maseczka", "maska", "szampon", "serum", "bloker"]:
        if cosmetic in title_lower:
            return title.strip(), 1

    # FUREVER
    if "furever" in title_lower:
        return title.strip(), 1

    # Default
    return title.strip(), 1


def calculate_reorder_intervals(orders):
    """
    For each product family and customer, calculate the intervals between purchases.
    """
    # Build: customer -> product_family -> list of (date, quantity, units_in_pack)
    customer_product_orders = defaultdict(lambda: defaultdict(list))

    for order in orders:
        order_date = datetime.fromisoformat(order["date"].replace("Z", "+00:00"))
        customer = order["customer_email"]

        for item in order["line_items"]:
            family, units = normalize_product_name(item["product_title"], item.get("product_handle", ""))
            customer_product_orders[customer][family].append({
                "date": order_date,
                "quantity": item["quantity"],
                "units_in_pack": units,
                "total_units": item["quantity"] * units,
                "order_name": order["name"],
                "original_title": item["product_title"]
            })

    # Sort each customer's purchases by date
    for customer in customer_product_orders:
        for product in customer_product_orders[customer]:
            customer_product_orders[customer][product].sort(key=lambda x: x["date"])

    # Calculate intervals
    product_intervals = defaultdict(lambda: {
        "intervals": [],
        "repeat_buyers": 0,
        "single_buyers": 0,
        "total_purchases": 0,
        "multi_unit_purchases": 0,
        "customer_details": []
    })

    for customer, products in customer_product_orders.items():
        for product, purchases in products.items():
            product_intervals[product]["total_purchases"] += len(purchases)

            # Count multi-unit purchases
            for p in purchases:
                if p["quantity"] > 1 or p["total_units"] > p["units_in_pack"]:
                    product_intervals[product]["multi_unit_purchases"] += 1

            if len(purchases) >= 2:
                product_intervals[product]["repeat_buyers"] += 1

                customer_intervals = []
                for i in range(1, len(purchases)):
                    days = (purchases[i]["date"] - purchases[i-1]["date"]).days
                    customer_intervals.append(days)
                    product_intervals[product]["intervals"].append(days)

                product_intervals[product]["customer_details"].append({
                    "customer": customer[:3] + "***" + customer.split("@")[1] if "@" in customer else "***",
                    "purchase_count": len(purchases),
                    "intervals": customer_intervals,
                    "first_purchase": purchases[0]["date"].strftime("%Y-%m-%d"),
                    "last_purchase": purchases[-1]["date"].strftime("%Y-%m-%d"),
                    "total_span_days": (purchases[-1]["date"] - purchases[0]["date"]).days,
                    "quantities": [p["quantity"] for p in purchases],
                    "total_units": [p["total_units"] for p in purchases]
                })
            else:
                product_intervals[product]["single_buyers"] += 1

    return dict(product_intervals), customer_product_orders


def histogram(intervals, bins=None):
    """Create a histogram of intervals."""
    if bins is None:
        bins = [(0, 14), (15, 29), (30, 44), (45, 59), (60, 74), (75, 89), (90, 119), (120, 179), (180, 365), (366, 9999)]

    result = {}
    for low, high in bins:
        label = f"{low}-{high}" if high < 9999 else f"{low}+"
        count = sum(1 for x in intervals if low <= x <= high)
        result[label] = count
    return result


def main():
    print("=" * 70, file=sys.stderr)
    print("GENACTIV REORDER INTERVAL ANALYSIS", file=sys.stderr)
    print("=" * 70, file=sys.stderr)

    print("\n[1/3] Fetching all orders from Shopify...", file=sys.stderr)
    orders = fetch_all_orders_with_line_items(max_pages=50)

    if not orders:
        print("ERROR: No orders fetched!", file=sys.stderr)
        sys.exit(1)

    # Date range
    dates = [datetime.fromisoformat(o["date"].replace("Z", "+00:00")) for o in orders]
    min_date = min(dates)
    max_date = max(dates)
    span_days = (max_date - min_date).days

    print(f"\n  Total orders fetched: {len(orders)}", file=sys.stderr)
    print(f"  Date range: {min_date.strftime('%Y-%m-%d')} to {max_date.strftime('%Y-%m-%d')} ({span_days} days)", file=sys.stderr)

    # Unique customers
    unique_customers = set(o["customer_email"] for o in orders)
    print(f"  Unique customers: {len(unique_customers)}", file=sys.stderr)

    print("\n[2/3] Calculating reorder intervals...", file=sys.stderr)
    product_intervals, customer_product_orders = calculate_reorder_intervals(orders)

    print("\n[3/3] Generating report...", file=sys.stderr)

    # Build output
    output = {
        "metadata": {
            "generated_at": datetime.now().isoformat(),
            "total_orders": len(orders),
            "unique_customers": len(unique_customers),
            "date_range": {
                "from": min_date.strftime("%Y-%m-%d"),
                "to": max_date.strftime("%Y-%m-%d"),
                "span_days": span_days
            }
        },
        "product_reorder_analysis": {}
    }

    # Sort by repeat buyers descending
    sorted_products = sorted(
        product_intervals.items(),
        key=lambda x: x[1]["repeat_buyers"],
        reverse=True
    )

    for product, data in sorted_products:
        intervals = data["intervals"]

        entry = {
            "repeat_buyers": data["repeat_buyers"],
            "single_buyers": data["single_buyers"],
            "total_purchases": data["total_purchases"],
            "multi_unit_purchases": data["multi_unit_purchases"],
            "repeat_rate_pct": round(data["repeat_buyers"] / (data["repeat_buyers"] + data["single_buyers"]) * 100, 1) if (data["repeat_buyers"] + data["single_buyers"]) > 0 else 0
        }

        if intervals:
            entry["interval_stats"] = {
                "count": len(intervals),
                "mean_days": round(mean(intervals), 1),
                "median_days": round(median(intervals), 1),
                "min_days": min(intervals),
                "max_days": max(intervals),
                "stdev_days": round(stdev(intervals), 1) if len(intervals) > 1 else 0,
                "all_intervals": sorted(intervals)
            }

            try:
                entry["interval_stats"]["mode_days"] = mode(intervals)
            except:
                entry["interval_stats"]["mode_days"] = None

            entry["histogram"] = histogram(intervals)

        # Include customer detail (anonymized)
        if data["customer_details"]:
            entry["customer_details"] = data["customer_details"][:50]  # limit

        output["product_reorder_analysis"][product] = entry

    # Also calculate overall customer reorder behavior
    customer_order_counts = defaultdict(int)
    customer_dates = defaultdict(list)
    for order in orders:
        customer = order["customer_email"]
        customer_order_counts[customer] += 1
        customer_dates[customer].append(
            datetime.fromisoformat(order["date"].replace("Z", "+00:00"))
        )

    overall_intervals = []
    for customer, order_dates in customer_dates.items():
        if len(order_dates) >= 2:
            sorted_dates = sorted(order_dates)
            for i in range(1, len(sorted_dates)):
                days = (sorted_dates[i] - sorted_dates[i-1]).days
                overall_intervals.append(days)

    output["overall_reorder"] = {
        "customers_with_2plus_orders": sum(1 for c in customer_order_counts.values() if c >= 2),
        "customers_with_3plus_orders": sum(1 for c in customer_order_counts.values() if c >= 3),
        "customers_with_5plus_orders": sum(1 for c in customer_order_counts.values() if c >= 5),
        "total_reorder_intervals": len(overall_intervals),
    }

    if overall_intervals:
        output["overall_reorder"]["stats"] = {
            "mean_days": round(mean(overall_intervals), 1),
            "median_days": round(median(overall_intervals), 1),
            "min_days": min(overall_intervals),
            "max_days": max(overall_intervals),
            "stdev_days": round(stdev(overall_intervals), 1) if len(overall_intervals) > 1 else 0,
        }
        output["overall_reorder"]["histogram"] = histogram(overall_intervals)

    # Also: multi-unit purchasing analysis
    multi_unit_stats = defaultdict(lambda: {"single_unit": 0, "multi_unit": 0, "avg_qty": []})
    for order in orders:
        for item in order["line_items"]:
            family, units = normalize_product_name(item["product_title"], item.get("product_handle", ""))
            qty = item["quantity"]
            multi_unit_stats[family]["avg_qty"].append(qty)
            if qty > 1:
                multi_unit_stats[family]["multi_unit"] += 1
            else:
                multi_unit_stats[family]["single_unit"] += 1

    output["multi_unit_purchasing"] = {}
    for product, stats in sorted(multi_unit_stats.items(), key=lambda x: sum(x[1]["avg_qty"]), reverse=True):
        total = stats["single_unit"] + stats["multi_unit"]
        if total >= 5:  # only show products with meaningful data
            output["multi_unit_purchasing"][product] = {
                "total_line_items": total,
                "single_unit_pct": round(stats["single_unit"] / total * 100, 1),
                "multi_unit_pct": round(stats["multi_unit"] / total * 100, 1),
                "avg_quantity": round(mean(stats["avg_qty"]), 2)
            }

    print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
    print(f"\nDone. Output written to stdout.", file=sys.stderr)


if __name__ == "__main__":
    main()

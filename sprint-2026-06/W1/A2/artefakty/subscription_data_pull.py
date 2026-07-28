#!/usr/bin/env python3
"""
GenActiv Subscription Business Case - Data Pull from Shopify
Pulls orders with line items, products, and customer data for analysis.
"""

import requests
import json
import os
import sys
from dotenv import load_dotenv
from collections import defaultdict, Counter
from datetime import datetime, timedelta

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
        print(f"Error: {response.status_code}")
        print(response.text)
        return None
    return response.json()

def get_orders_with_line_items(cursor=None, limit=50):
    """Pull orders with line items, customer info"""
    after_clause = f', after: "{cursor}"' if cursor else ''
    query = f"""
    {{
      orders(first: {limit}, sortKey: CREATED_AT, reverse: true{after_clause}) {{
        edges {{
          cursor
          node {{
            id
            name
            createdAt
            totalPriceSet {{
              shopMoney {{
                amount
                currencyCode
              }}
            }}
            subtotalPriceSet {{
              shopMoney {{
                amount
              }}
            }}
            displayFinancialStatus
            lineItems(first: 20) {{
              edges {{
                node {{
                  title
                  variantTitle
                  quantity
                  originalUnitPriceSet {{
                    shopMoney {{
                      amount
                    }}
                  }}
                  product {{
                    id
                    title
                    productType
                  }}
                }}
              }}
            }}
            customer {{
              id
              email
              firstName
              lastName
              numberOfOrders
              createdAt
            }}
            shippingAddress {{
              city
              province
            }}
          }}
        }}
        pageInfo {{
          hasNextPage
          endCursor
        }}
      }}
    }}
    """
    return execute_query(query)

def get_products():
    """Pull all products with variants and prices"""
    query = """
    {
      products(first: 50) {
        edges {
          node {
            id
            title
            handle
            productType
            status
            totalInventory
            priceRangeV2 {
              minVariantPrice {
                amount
                currencyCode
              }
              maxVariantPrice {
                amount
                currencyCode
              }
            }
            variants(first: 20) {
              edges {
                node {
                  id
                  title
                  price
                  compareAtPrice
                  sku
                  inventoryQuantity
                }
              }
            }
            tags
          }
        }
      }
    }
    """
    return execute_query(query)

def get_customers_with_orders(cursor=None, limit=50):
    """Pull customers with order count and spend using REST API"""
    # Try REST API instead of GraphQL for customers
    rest_url = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}/customers.json"
    params = {
        'limit': limit,
        'order': 'total_spent DESC',
        'fields': 'id,email,first_name,last_name,orders_count,total_spent,created_at,updated_at'
    }
    if cursor:
        params['since_id'] = cursor

    response = requests.get(rest_url, headers={
        'X-Shopify-Access-Token': ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }, params=params)

    if response.status_code != 200:
        print(f"Customer REST Error: {response.status_code}", file=sys.stderr)
        return {'customers': [], 'has_next': False, 'last_id': None}

    data = response.json()
    customers = data.get('customers', [])
    # Convert to unified format
    result_customers = []
    for c in customers:
        result_customers.append({
            'id': str(c['id']),
            'email': c.get('email', ''),
            'firstName': c.get('first_name', ''),
            'lastName': c.get('last_name', ''),
            'numberOfOrders': c.get('orders_count', 0),
            'amountSpent': {'amount': str(c.get('total_spent', '0.00'))},
            'createdAt': c.get('created_at', ''),
            'updatedAt': c.get('updated_at', ''),
            'orders': {'edges': []}
        })

    last_id = customers[-1]['id'] if customers else None
    # Check Link header for pagination
    link_header = response.headers.get('Link', '')
    has_next = 'rel="next"' in link_header

    return {'customers': result_customers, 'has_next': has_next, 'last_id': last_id, 'link': link_header}

def pull_all_orders(max_pages=20):
    """Pull up to max_pages * 50 orders"""
    all_orders = []
    cursor = None
    for page in range(max_pages):
        print(f"  Pulling orders page {page+1}...", file=sys.stderr)
        result = get_orders_with_line_items(cursor=cursor)
        if not result or 'data' not in result or not result['data']['orders']['edges']:
            break
        edges = result['data']['orders']['edges']
        for edge in edges:
            all_orders.append(edge['node'])
        page_info = result['data']['orders']['pageInfo']
        if not page_info['hasNextPage']:
            break
        cursor = page_info['endCursor']
    return all_orders

def pull_all_customers(max_pages=20):
    """Pull top customers sorted by spend via REST API"""
    all_customers = []
    cursor = None
    for page in range(max_pages):
        print(f"  Pulling customers page {page+1}...", file=sys.stderr)
        result = get_customers_with_orders(cursor=cursor, limit=250)
        customers = result.get('customers', [])
        if not customers:
            break
        all_customers.extend(customers)
        if not result.get('has_next', False):
            break
        cursor = result.get('last_id')
    return all_customers

def analyze_data(orders, products, customers):
    """Comprehensive analysis for subscription business case"""
    analysis = {}

    # --- Product Catalog ---
    product_list = []
    if products and 'data' in products:
        for edge in products['data']['products']['edges']:
            p = edge['node']
            variants = []
            for v_edge in p['variants']['edges']:
                v = v_edge['node']
                variants.append({
                    'title': v['title'],
                    'price': float(v['price']),
                    'compareAtPrice': float(v['compareAtPrice']) if v['compareAtPrice'] else None,
                    'sku': v['sku'],
                    'inventory': v['inventoryQuantity']
                })
            product_list.append({
                'id': p['id'],
                'title': p['title'],
                'handle': p['handle'],
                'type': p['productType'],
                'status': p['status'],
                'inventory': p['totalInventory'],
                'min_price': float(p['priceRangeV2']['minVariantPrice']['amount']),
                'max_price': float(p['priceRangeV2']['maxVariantPrice']['amount']),
                'variants': variants,
                'tags': p.get('tags', [])
            })
    analysis['products'] = product_list

    # --- Order Analysis ---
    order_count = len(orders)
    total_revenue = sum(float(o['totalPriceSet']['shopMoney']['amount']) for o in orders)
    avg_order_value = total_revenue / order_count if order_count else 0

    # Products per order
    product_frequency = Counter()
    product_revenue = defaultdict(float)
    product_quantity = defaultdict(int)
    order_dates = []

    # Customer order mapping
    customer_orders = defaultdict(list)
    customer_products = defaultdict(lambda: defaultdict(list))  # customer -> product -> [dates]

    for o in orders:
        order_date = datetime.fromisoformat(o['createdAt'].replace('Z', '+00:00'))
        order_dates.append(order_date)

        customer_id = o['customer']['id'] if o.get('customer') else 'guest'
        customer_orders[customer_id].append({
            'date': order_date,
            'total': float(o['totalPriceSet']['shopMoney']['amount']),
            'products': []
        })

        for li_edge in o['lineItems']['edges']:
            li = li_edge['node']
            product_title = li['title']
            qty = li['quantity']
            price = float(li['originalUnitPriceSet']['shopMoney']['amount']) if li.get('originalUnitPriceSet') else 0

            product_frequency[product_title] += 1  # number of orders containing this product
            product_revenue[product_title] += price * qty
            product_quantity[product_title] += qty

            prod_id = li['product']['id'] if li.get('product') else product_title
            customer_products[customer_id][prod_id].append(order_date)
            customer_orders[customer_id][-1]['products'].append(product_title)

    analysis['order_summary'] = {
        'total_orders': order_count,
        'total_revenue': round(total_revenue, 2),
        'avg_order_value': round(avg_order_value, 2),
        'date_range': {
            'from': min(order_dates).isoformat() if order_dates else None,
            'to': max(order_dates).isoformat() if order_dates else None,
            'days': (max(order_dates) - min(order_dates)).days if len(order_dates) > 1 else 0
        }
    }

    # --- Product Popularity ---
    product_stats = []
    for product, freq in product_frequency.most_common():
        product_stats.append({
            'product': product,
            'order_count': freq,
            'total_quantity': product_quantity[product],
            'total_revenue': round(product_revenue[product], 2),
            'pct_of_orders': round(freq / order_count * 100, 1) if order_count else 0
        })
    analysis['product_popularity'] = product_stats

    # --- Customer Segmentation ---
    total_customers = len(customer_orders)
    repeat_customers = sum(1 for cid, ords in customer_orders.items() if len(ords) > 1)

    # Orders per customer distribution
    orders_per_customer = [len(ords) for ords in customer_orders.values()]
    orders_distribution = Counter(orders_per_customer)

    # Revenue per customer
    customer_revenue = {}
    for cid, ords in customer_orders.items():
        customer_revenue[cid] = sum(o['total'] for o in ords)

    # Top 20% customer revenue
    sorted_revenue = sorted(customer_revenue.values(), reverse=True)
    top_20_count = max(1, int(len(sorted_revenue) * 0.2))
    top_20_revenue = sum(sorted_revenue[:top_20_count])

    analysis['customer_segmentation'] = {
        'total_customers': total_customers,
        'repeat_customers': repeat_customers,
        'repeat_rate': round(repeat_customers / total_customers * 100, 1) if total_customers else 0,
        'orders_per_customer_avg': round(sum(orders_per_customer) / len(orders_per_customer), 2) if orders_per_customer else 0,
        'orders_distribution': dict(sorted(orders_distribution.items())),
        'top_20pct_revenue_share': round(top_20_revenue / total_revenue * 100, 1) if total_revenue else 0,
        'avg_customer_revenue': round(total_revenue / total_customers, 2) if total_customers else 0
    }

    # --- Reorder Analysis ---
    # Find customers who reordered the same product
    reorder_intervals = defaultdict(list)
    repeat_product_customers = defaultdict(int)

    for cid, products in customer_products.items():
        for prod_id, dates in products.items():
            if len(dates) > 1:
                sorted_dates = sorted(dates)
                for i in range(1, len(sorted_dates)):
                    interval = (sorted_dates[i] - sorted_dates[i-1]).days
                    # Find product name from the prod_id
                    prod_name = prod_id  # fallback
                    for o in orders:
                        for li in o['lineItems']['edges']:
                            if li['node'].get('product') and li['node']['product']['id'] == prod_id:
                                prod_name = li['node']['title']
                                break
                    reorder_intervals[prod_name].append(interval)
                repeat_product_customers[prod_name] += 1

    reorder_stats = []
    for product, intervals in reorder_intervals.items():
        if len(intervals) >= 2:
            avg_interval = sum(intervals) / len(intervals)
            median_interval = sorted(intervals)[len(intervals) // 2]
            reorder_stats.append({
                'product': product,
                'repeat_buyers': repeat_product_customers[product],
                'total_reorders': len(intervals),
                'avg_interval_days': round(avg_interval, 1),
                'median_interval_days': median_interval,
                'min_interval_days': min(intervals),
                'max_interval_days': max(intervals),
                'intervals': sorted(intervals)
            })
    reorder_stats.sort(key=lambda x: x['total_reorders'], reverse=True)
    analysis['reorder_analysis'] = reorder_stats

    # --- Product Combinations (basket analysis) ---
    basket_combos = Counter()
    for o in orders:
        items = []
        for li in o['lineItems']['edges']:
            items.append(li['node']['title'])
        if len(items) > 1:
            for i in range(len(items)):
                for j in range(i+1, len(items)):
                    combo = tuple(sorted([items[i], items[j]]))
                    basket_combos[combo] += 1

    combo_stats = []
    for combo, count in basket_combos.most_common(20):
        combo_stats.append({
            'products': list(combo),
            'co_purchase_count': count
        })
    analysis['product_combinations'] = combo_stats

    # --- Payment Methods ---
    # (from order data we can see gateway usage)

    # --- Customer Data from customer pull ---
    customer_detail_stats = []
    for c in customers:
        num_orders = c.get('numberOfOrders', '0')
        try:
            num_orders = int(num_orders)
        except:
            num_orders = 0
        total_spent = float(c['amountSpent']['amount']) if c.get('amountSpent') else 0

        # Get product list from customer's orders
        cust_products = []
        for o_edge in c.get('orders', {}).get('edges', []):
            o = o_edge['node']
            for li in o['lineItems']['edges']:
                cust_products.append(li['node']['title'])

        customer_detail_stats.append({
            'id': c['id'],
            'orders': num_orders,
            'total_spent': round(total_spent, 2),
            'created': c['createdAt'],
            'products': cust_products
        })

    # High-value customers (>3 orders)
    high_value = [c for c in customer_detail_stats if c['orders'] >= 3]
    analysis['high_value_customers'] = {
        'count': len(high_value),
        'avg_orders': round(sum(c['orders'] for c in high_value) / len(high_value), 1) if high_value else 0,
        'avg_spend': round(sum(c['total_spent'] for c in high_value) / len(high_value), 2) if high_value else 0,
        'total_spend': round(sum(c['total_spent'] for c in high_value), 2)
    }

    # Customer lifetime value tiers
    ltv_tiers = {
        '0-200': 0,
        '200-500': 0,
        '500-1000': 0,
        '1000-2000': 0,
        '2000-5000': 0,
        '5000+': 0
    }
    for c in customer_detail_stats:
        s = c['total_spent']
        if s < 200: ltv_tiers['0-200'] += 1
        elif s < 500: ltv_tiers['200-500'] += 1
        elif s < 1000: ltv_tiers['500-1000'] += 1
        elif s < 2000: ltv_tiers['1000-2000'] += 1
        elif s < 5000: ltv_tiers['2000-5000'] += 1
        else: ltv_tiers['5000+'] += 1
    analysis['ltv_distribution'] = ltv_tiers
    analysis['customer_detail_count'] = len(customer_detail_stats)

    return analysis


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'

    if mode == 'products':
        result = get_products()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif mode == 'orders':
        orders = pull_all_orders(max_pages=15)
        print(json.dumps(orders, indent=2, ensure_ascii=False))
    elif mode == 'customers':
        customers = pull_all_customers(max_pages=15)
        print(json.dumps(customers, indent=2, ensure_ascii=False))
    elif mode == 'all':
        print("=== PULLING ALL DATA ===", file=sys.stderr)

        print("\n--- Products ---", file=sys.stderr)
        products = get_products()

        print("\n--- Orders (up to 1500) ---", file=sys.stderr)
        orders = pull_all_orders(max_pages=30)
        print(f"  Got {len(orders)} orders", file=sys.stderr)

        print("\n--- Customers (top 750 by spend) ---", file=sys.stderr)
        customers = pull_all_customers(max_pages=15)
        print(f"  Got {len(customers)} customers", file=sys.stderr)

        print("\n--- Analyzing ---", file=sys.stderr)
        analysis = analyze_data(orders, products, customers)

        output_path = os.path.join(os.path.dirname(__file__), 'subscription_analysis_data.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False, default=str)
        print(f"\nAnalysis saved to {output_path}", file=sys.stderr)

        # Print summary to stdout
        print("\n" + "=" * 60)
        print("SUBSCRIPTION BUSINESS CASE - DATA SUMMARY")
        print("=" * 60)

        print(f"\nOrders analyzed: {analysis['order_summary']['total_orders']}")
        print(f"Revenue: {analysis['order_summary']['total_revenue']:,.2f} PLN")
        print(f"AOV: {analysis['order_summary']['avg_order_value']:,.2f} PLN")
        print(f"Date range: {analysis['order_summary']['date_range']['from'][:10]} to {analysis['order_summary']['date_range']['to'][:10]}")
        print(f"Days covered: {analysis['order_summary']['date_range']['days']}")

        print(f"\nCustomers in orders: {analysis['customer_segmentation']['total_customers']}")
        print(f"Repeat customers: {analysis['customer_segmentation']['repeat_customers']} ({analysis['customer_segmentation']['repeat_rate']}%)")
        print(f"Orders/customer avg: {analysis['customer_segmentation']['orders_per_customer_avg']}")
        print(f"Top 20% revenue share: {analysis['customer_segmentation']['top_20pct_revenue_share']}%")

        print(f"\n--- Product Popularity (top 15) ---")
        for p in analysis['product_popularity'][:15]:
            print(f"  {p['product'][:50]:50s} | {p['order_count']:4d} orders | {p['total_revenue']:10,.0f} PLN | {p['pct_of_orders']:5.1f}%")

        print(f"\n--- Reorder Analysis ---")
        for r in analysis['reorder_analysis'][:10]:
            print(f"  {r['product'][:50]:50s} | {r['repeat_buyers']:3d} repeat buyers | avg {r['avg_interval_days']:5.0f} days")

        print(f"\n--- Product Combinations (top 10) ---")
        for c in analysis['product_combinations'][:10]:
            print(f"  {c['products'][0][:30]:30s} + {c['products'][1][:30]:30s} | {c['co_purchase_count']:3d}x")

        print(f"\n--- Orders Distribution ---")
        for num, count in sorted(analysis['customer_segmentation']['orders_distribution'].items()):
            print(f"  {num} orders: {count} customers")

        print(f"\n--- High-Value Customers (3+ orders) ---")
        hv = analysis['high_value_customers']
        print(f"  Count: {hv['count']}")
        print(f"  Avg orders: {hv['avg_orders']}")
        print(f"  Avg spend: {hv['avg_spend']:,.2f} PLN")
        print(f"  Total spend: {hv['total_spend']:,.2f} PLN")

        print(f"\n--- LTV Distribution ---")
        for tier, count in analysis['ltv_distribution'].items():
            print(f"  {tier:12s} PLN: {count} customers")

        print(f"\n--- Products Catalog ---")
        for p in analysis['products']:
            if p['status'] == 'ACTIVE':
                print(f"  {p['title'][:50]:50s} | {p['min_price']:7.0f} - {p['max_price']:7.0f} PLN | inv: {p['inventory']:5d}")
    else:
        print("Usage: python subscription_data_pull.py [all|products|orders|customers]")

#!/usr/bin/env python3
"""Ekonomika obnizenia progu darmowej dostawy 300 -> 250 PLN.

Segment docelowy: klienci z min. 1 wczesniejszym zakupem (powracajacy).
Zrodla:
  - Shopify (raw-orders-shipping-threshold.json) — 60 dni, limit API
  - DHL faktura 1107107021 — realny koszt przesylki
  - Brief Performance Marketing v3 — struktura kosztow na zamowieniu
"""
import json
import os
import statistics
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw-orders-shipping-threshold.json")

# --- Parametry kosztowe (netto) ---
DHL_COST = 11.42          # sr. wazona krajowa <=3 kg, faktura DHL 08-14.08.2026
PACKAGING = 3.58          # dopelnienie do 15 PLN z briefu (wysylka+opakowanie)
FULFILL_COST = DHL_COST + PACKAGING
VAT = 1.23
PAYMENT_FEE = 0.01        # 1% AOV, wg briefu

MARGIN_SCENARIOS = [
    ("25% (zalozenie klienta)", 0.25),
    ("20% (wariant pesymistyczny)", 0.20),
    ("76% (wg briefu: COGS 24% AOV)", 0.76),
]

OLD_THRESHOLD = 300.0
NEW_THRESHOLD = 250.0


def load():
    with open(RAW) as f:
        return json.load(f)


def money(node, key):
    v = node.get(key)
    if not v or not v.get("shopMoney"):
        return 0.0
    return float(v["shopMoney"]["amount"] or 0)


def price_ladder(orders, min_share=0.01):
    """Realna drabinka cen katalogowych — tylko pozycje o istotnym wolumenie.

    Klient dociagajacy do progu nie dokłada 'brakującej kwoty', tylko konkretny
    produkt z tej drabinki. To zmienia inkrementalny przychod.
    """
    cnt = Counter()
    total = 0
    for o in orders:
        for li in o["lineItems"]["nodes"]:
            p = float(li["originalUnitPriceSet"]["shopMoney"]["amount"] or 0)
            if p > 0:
                cnt[round(p)] += li["quantity"]
                total += li["quantity"]
    return sorted(p for p, n in cnt.items() if n / total >= min_share)


def cheapest_closing(ladder, gap):
    """Najtanszy realny produkt, ktory domyka luke do progu."""
    for p in ladder:
        if p >= gap:
            return p
    return ladder[-1]


def prepare(orders):
    """Normalizuje zamowienia i odsiewa te, ktore nie naleza do analizy."""
    rows, skipped = [], Counter()
    for o in orders:
        if o.get("cancelledAt"):
            skipped["anulowane"] += 1
            continue
        if o.get("displayFinancialStatus") not in ("PAID", "PARTIALLY_REFUNDED"):
            skipped[f"status:{o.get('displayFinancialStatus')}"] += 1
            continue
        if money(o, "totalShippingPriceSet") >= 50:
            skipped["zagraniczne (dostawa >=50 PLN)"] += 1
            continue
        cust = o.get("customer") or {}
        n_orders = int(cust.get("numberOfOrders") or 0)
        subtotal = money(o, "subtotalPriceSet")
        ship_paid = money(o, "totalShippingPriceSet")
        rows.append({
            "name": o["name"],
            "date": o["createdAt"][:10],
            "subtotal": subtotal,               # po rabatach na produkty, bez dostawy
            "ship_paid": ship_paid,             # brutto, ile zaplacil klient
            "total": money(o, "totalPriceSet"),
            "discounts": money(o, "totalDiscountsSet"),
            "codes": o.get("discountCodes") or [],
            "returning": n_orders > 1,
            "n_orders": n_orders,
            "items": sum(li["quantity"] for li in o["lineItems"]["nodes"]),
            "ship_title": (o.get("shippingLine") or {}).get("title") or "",
        })
    return rows, skipped


def detect_threshold(rows):
    """Weryfikuje empirycznie, na jakiej wartosci dziala obecny prog."""
    print("\n=== WERYFIKACJA: gdzie faktycznie lezy obecny prog ===")
    print(f"{'przedzial subtotal':>22} | {'N':>5} | {'% z darmowa dost.':>18}")
    edges = [0, 100, 150, 200, 250, 280, 290, 295, 300, 310, 350, 400, 10 ** 9]
    for lo, hi in zip(edges, edges[1:]):
        seg = [r for r in rows if lo <= r["subtotal"] < hi]
        if not seg:
            continue
        free = sum(1 for r in seg if r["ship_paid"] == 0)
        label = f"{lo}-{hi}" if hi < 10 ** 8 else f"{lo}+"
        print(f"{label:>22} | {len(seg):>5} | {free / len(seg):>17.1%}")


def shipping_fee_stats(rows):
    fees = [r["ship_paid"] for r in rows if r["ship_paid"] > 0]
    print("\n=== ILE KLIENT PLACI ZA DOSTAWE (brutto) ===")
    for fee, n in Counter(round(f, 2) for f in fees).most_common(8):
        print(f"  {fee:>7.2f} PLN : {n:>5} zam. ({n / len(fees):>5.1%})")
    print(f"  srednia: {statistics.mean(fees):.2f} PLN brutto "
          f"= {statistics.mean(fees) / VAT:.2f} PLN netto")
    return statistics.mean(fees) / VAT


def band(rows, lo, hi):
    return [r for r in rows if lo <= r["subtotal"] < hi]


def analyse(rows, label, fee_net, ladder, uplift_rates=(0.10, 0.20, 0.30)):
    print("\n" + "=" * 78)
    print(f"SEGMENT: {label}  (N = {len(rows)})")
    print("=" * 78)

    paid_ship = [r for r in rows if r["ship_paid"] > 0]
    free_ship = [r for r in rows if r["ship_paid"] == 0]
    print(f"  placi za dostawe : {len(paid_ship):>5} ({len(paid_ship)/len(rows):>5.1%})"
          f"  AOV {statistics.mean([r['subtotal'] for r in paid_ship]):.0f} PLN"
          f"  items {statistics.mean([r['items'] for r in paid_ship]):.2f}")
    print(f"  darmowa dostawa  : {len(free_ship):>5} ({len(free_ship)/len(rows):>5.1%})"
          f"  AOV {statistics.mean([r['subtotal'] for r in free_ship]):.0f} PLN"
          f"  items {statistics.mean([r['items'] for r in free_ship]):.2f}")

    # --- A. KANIBALIZACJA: kto dostanie dostawe za darmo, choc dzis placi ---
    cannib = [r for r in band(paid_ship, NEW_THRESHOLD, OLD_THRESHOLD)]
    lost_fee = len(cannib) * fee_net
    print(f"\n  [A] KANIBALIZACJA — subtotal {NEW_THRESHOLD:.0f}-{OLD_THRESHOLD:.0f} PLN, dzis placa dostawe")
    print(f"      zamowien: {len(cannib)} ({len(cannib)/len(rows):.1%} segmentu)")
    print(f"      utracony przychod z dostawy: {lost_fee:,.0f} PLN netto / 60 dni")

    # --- B. STREFA DOCIAGNIECIA: kto moze dolozyc produkt, by dobic do 250 ---
    reach = [r for r in paid_ship if 150 <= r["subtotal"] < NEW_THRESHOLD]
    gap = [NEW_THRESHOLD - r["subtotal"] for r in reach]
    print(f"\n  [B] STREFA DOCIAGNIECIA — subtotal 150-{NEW_THRESHOLD:.0f} PLN")
    print(f"      zamowien: {len(reach)} ({len(reach)/len(rows):.1%} segmentu)")
    print(f"      sr. brakujaca kwota do {NEW_THRESHOLD:.0f}: {statistics.mean(gap):.0f} PLN"
          f"  (mediana {statistics.median(gap):.0f} PLN)")
    print(f"      [dla porownania, do progu {OLD_THRESHOLD:.0f}: "
          f"{statistics.mean([OLD_THRESHOLD - r['subtotal'] for r in reach]):.0f} PLN]")

    # Realny dosypany produkt, nie 'brakujaca kwota'
    addons = [cheapest_closing(ladder, g) for g in gap]
    avg_addon = statistics.mean(addons)
    print(f"      REALNY dosypany produkt (najtanszy z katalogu domykajacy luke):")
    print(f"        srednio {avg_addon:.0f} PLN  (mediana {statistics.median(addons):.0f} PLN)")
    print(f"        drabinka cen: {ladder}")

    # --- C. WYNIK per scenariusz marzy x scenariusz upliftu ---
    print(f"\n  [C] WYNIK NETTO / 60 DNI (PLN) — inkrement = realny produkt {avg_addon:.0f} PLN")
    print(f"      {'marza':<32} " + "  ".join(f"uplift {u:>4.0%}" for u in uplift_rates))
    results = {}
    for mlabel, m in MARGIN_SCENARIOS:
        cells = []
        for u in uplift_rates:
            n_up = len(reach) * u
            inc_rev = n_up * avg_addon
            gain = inc_rev * (m - PAYMENT_FEE)     # marza na dolozonym produkcie
            lost_up = n_up * fee_net               # oni tez przestaja placic dostawe
            net = gain - lost_up - lost_fee
            cells.append(net)
            results[(mlabel, u)] = net
        print(f"      {mlabel:<32} " + "  ".join(f"{c:>+11,.0f}" for c in cells))

    # --- D. Prog rentownosci ---
    print(f"\n  [D] BREAK-EVEN — jaki % strefy [B] musi dociagnac, by wyjsc na zero")
    for mlabel, m in MARGIN_SCENARIOS:
        per_order = avg_addon * (m - PAYMENT_FEE) - fee_net
        denom = len(reach) * per_order
        tag = f"(marza netto na dociagnietym zam.: {per_order:+.2f} PLN)"
        if denom <= 0:
            print(f"      {mlabel:<32} NIEOSIAGALNY {tag}")
        else:
            print(f"      {mlabel:<32} {lost_fee / denom:>6.1%}  {tag}")

    # --- E. Wariant alternatywny: zostawiamy 300, robimy cross-sell ---
    reach300 = [r for r in paid_ship if 150 <= r["subtotal"] < OLD_THRESHOLD]
    gap300 = [OLD_THRESHOLD - r["subtotal"] for r in reach300]
    addons300 = [cheapest_closing(ladder, g) for g in gap300]
    avg300 = statistics.mean(addons300)
    print(f"\n  [E] ALTERNATYWA — prog zostaje {OLD_THRESHOLD:.0f}, dokladamy cross-sell w koszyku")
    print(f"      pula: {len(reach300)} zam.  realny dosypany produkt: {avg300:.0f} PLN")
    print(f"      {'marza':<32} " + "  ".join(f"uplift {u:>4.0%}" for u in uplift_rates))
    for mlabel, m in MARGIN_SCENARIOS:
        cells = []
        for u in uplift_rates:
            n_up = len(reach300) * u
            net = n_up * (avg300 * (m - PAYMENT_FEE) - fee_net)   # brak kanibalizacji
            cells.append(net)
        print(f"      {mlabel:<32} " + "  ".join(f"{c:>+11,.0f}" for c in cells))
    return results, cannib, reach


def main():
    orders = load()
    rows, skipped = prepare(orders)
    dates = sorted(r["date"] for r in rows)
    print("=" * 78)
    print("EKONOMIKA PROGU DARMOWEJ DOSTAWY 300 -> 250 PLN")
    print("=" * 78)
    print(f"Zamowien pobranych: {len(orders)}  |  po filtrach: {len(rows)}")
    print(f"Odrzucone: {dict(skipped)}")
    print(f"Zakres dat (FAKTYCZNY): {dates[0]} -> {dates[-1]}  ({len(set(dates))} dni)")
    print(f"Koszt fulfillmentu: DHL {DHL_COST} + opakowanie {PACKAGING} = {FULFILL_COST:.2f} PLN netto")

    detect_threshold(rows)
    fee_net = shipping_fee_stats(rows)
    ladder = price_ladder(orders)

    returning = [r for r in rows if r["returning"]]
    new = [r for r in rows if not r["returning"]]
    analyse(returning, "KLIENCI Z MIN. 1 WCZESNIEJSZYM ZAKUPEM (powracajacy)", fee_net, ladder)
    analyse(new, "KLIENCI NOWI (kontrola)", fee_net, ladder)
    analyse(rows, "CALA BAZA (kontrola)", fee_net, ladder)

    # roczna ekstrapolacja
    print("\n" + "=" * 78)
    print("UWAGA SKALOWANIE: powyzsze to 60 dni OFF-SEASON (lip-sie).")
    print("Wg briefu off-season = 40% rocznej sprzedazy, sezon = 60%.")
    print("Mnoznik na rok NIE jest 6x — sezon ma inny rozklad koszyka.")
    print("=" * 78)


if __name__ == "__main__":
    main()

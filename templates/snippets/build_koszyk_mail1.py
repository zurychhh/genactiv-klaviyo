#!/usr/bin/env python3
"""
Scala sekcje "Ten produkt czeka w Twoim koszyku" z szablonem Klaviyo
"Koszyk mail 1 - WHY" (XnCJxJ).

Sekcja trafia POMIEDZY grafike z CTA "Dokoncz zamowienie" (6d4a1ba8...)
a grafike "70%" (2faa82e1...).

Skrypt jest read-only wobec Klaviyo: pobiera szablon, sklada wynik na dysku,
niczego nie zapisuje przez API.

Uzycie:
    python3 templates/snippets/build_koszyk_mail1.py            # build + demo
    python3 templates/snippets/build_koszyk_mail1.py --demo-only
"""
import io
import re
import json
import os
import pathlib
import sys
import urllib.request

TEMPLATE_ID = "XnCJxJ"
API_REVISION = "2026-01-15"

# Kotwica: grafika "70%". Sekcja wchodzi tuz przed blokiem, ktory ja zawiera.
ANCHOR_IMAGE = "2faa82e1-15cf-44fc-9c73-aadcc5147175"
BLOCK_OPEN = '<div class="mj-column-per-100 mj-outlook-group-fix component-wrapper"'

# Grafika z CTA "Dokoncz zamowienie" - musi wystapic PRZED punktem wstawienia.
CTA_IMAGE = "6d4a1ba8-5f55-42bf-b716-8d63a323156c"

MEDIA_QUERY = """
@media only screen and (max-width: 480px) {
    td.gc-cart-pad {
        padding-left: 14px !important;
        padding-right: 14px !important;
        padding-top: 26px !important;
        padding-bottom: 28px !important
        }
    td.gc-card-pad {
        padding: 14px !important
        }
    td.gc-cart-thumb {
        width: 30% !important;
        padding-right: 12px !important
        }
    td.gc-cart-body {
        width: 70% !important
        }
    td.gc-cart-h {
        font-size: 23px !important;
        padding-bottom: 20px !important
        }
    div.gc-cart-title {
        font-size: 15px !important
        }
    span.gc-cart-price {
        font-size: 20px !important
        }
    td.gc-cta-space {
        padding-top: 26px !important
        }
    }
/* --- DARK MODE ---
   Gmail/Apple Mail odwracaja kolory w trybie ciemnym: bialy naglowek
   i bialy tekst przycisku robily sie czarne na czerwonym tle.
   Ponizsze reguly przywracaja kolory tam, gdzie klient je respektuje. */
@media (prefers-color-scheme: dark) {
    td.gc-cart-h, td.gc-cart-h * {
        color: #FFFFFF !important
        }
    a.gc-cta-link {
        color: #FFFFFF !important
        }
    td.gc-cta-cell {
        border-color: #FFFFFF !important
        }
    table.gc-card, td.gc-card-pad {
        background-color: #FFFFFF !important
        }
    div.gc-cart-title, div.gc-cart-title a {
        color: #1C1B1B !important
        }
    td.gc-cart-qty {
        color: #1C1B1B !important
        }
    div.gc-cart-variant {
        color: #F03642 !important
        }
    td.gc-cart-save {
        background-color: #E7F5EC !important;
        color: #1E7A45 !important
        }
    }"""

ROOT = pathlib.Path(__file__).resolve().parents[2]
SNIPPET = ROOT / "templates/snippets/porzucony-koszyk-jeden-produkt.html"
OUT_FULL = ROOT / "templates/snippets/koszyk-mail1-WHY-z-koszykiem.html"
OUT_DEMO = ROOT / "templates/snippets/koszyk-mail1-PODGLAD.html"
OUT_DEMO_NOPROMO = ROOT / "templates/snippets/koszyk-mail1-PODGLAD-bez-promocji.html"


def read_key():
    for env in (ROOT / "genactiv-online/.env", ROOT / ".env"):
        if not env.exists():
            continue
        for line in io.open(env, encoding="utf-8"):
            if line.startswith("KLAVIYO_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
                if key:
                    return key
    sys.exit("Brak KLAVIYO_API_KEY w .env")


def fetch_template():
    req = urllib.request.Request(
        f"https://a.klaviyo.com/api/templates/{TEMPLATE_ID}",
        headers={
            "Authorization": f"Klaviyo-API-Key {read_key()}",
            "revision": API_REVISION,
            "accept": "application/vnd.api+json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["data"]["attributes"]["html"]


END_MARK = "KONIEC sekcji porzuconego koszyka"


def remove_existing_section(html):
    """Usuwa sekcje juz obecna w szablonie - inaczej build ja duplikuje.

    Szablon w Klaviyo bywa aktualizowany recznie miedzy uruchomieniami,
    wiec skrypt musi byc idempotentny. Obsluguje zarowno wersje z
    markerami GC-CART-SECTION, jak i starsza bez nich.
    """
    if END_MARK not in html:
        return html, False

    start = html.find("<!-- GC-CART-SECTION:START -->")
    if start == -1:
        # starsza wersja bez markerow - cofnij sie od pierwszego gc-cart-pad
        pad = html.find("gc-cart-pad")
        if pad == -1:
            sys.exit("Znaleziono koniec sekcji, ale nie jej poczatek - przerywam.")
        cand = [html.rfind("<!-- ====", 0, pad), html.rfind(BLOCK_OPEN, 0, pad)]
        start = max(c for c in cand if c != -1)

    end = html.find("-->", html.find(END_MARK))
    if end == -1:
        sys.exit("Nie znaleziono domkniecia komentarza koncowego - przerywam.")
    end += len("-->")
    tail = html[end:end + 40]
    if "GC-CART-SECTION:END" in tail:
        end = html.find("-->", html.find("GC-CART-SECTION:END")) + len("-->")

    html = html[:start] + html[end:]

    # Osierocony komentarz dokumentacyjny: przy wklejaniu do edytora Klaviyo
    # trafil do osobnego bloku tekstowego i nie mieszci sie w zakresie wyzej.
    html = re.sub(r"<!-- =+\s*GENACTIV — sekcja.*?=+ -->", "", html, flags=re.S)
    return html, True


def insert_section(html, section):
    """Wstawia sekcje przed blokiem zawierajacym grafike '70%'."""
    anchor = html.find(ANCHOR_IMAGE)
    if anchor == -1:
        sys.exit(f"Nie znaleziono kotwicy {ANCHOR_IMAGE} - szablon sie zmienil, przerywam.")
    if html.count(ANCHOR_IMAGE) != 1:
        sys.exit(f"Kotwica {ANCHOR_IMAGE} wystepuje {html.count(ANCHOR_IMAGE)}x, oczekiwano 1 - przerywam.")

    cta = html.find(CTA_IMAGE)
    if cta == -1 or cta > anchor:
        sys.exit("Grafika 'Dokoncz zamowienie' nie wystepuje przed grafika '70%' - przerywam.")

    at = html.rfind(BLOCK_OPEN, 0, anchor)
    if at == -1:
        sys.exit("Nie znaleziono poczatku bloku grafiki '70%' - przerywam.")

    return html[:at] + section.rstrip() + "\n" + html[at:]


def polish_footer(html):
    """Stopka XnCJxJ jest po angielsku, a unsubscribe bez polskiej etykiety."""
    old = ("No longer want to receive these emails? {% unsubscribe %}.")
    new = ("Nie chcesz już otrzymywać tych wiadomości? "
           "{% unsubscribe 'Anuluj subskrypcję' %}.")
    if old in html:
        return html.replace(old, new), True
    return html, False


def add_media_query(html):
    if "gc-cart-pad" in html.split("</head>")[0]:
        return html  # juz dodane
    close = html.rfind("</style></head>")
    if close == -1:
        sys.exit("Nie znaleziono konca <style> w <head> - przerywam.")
    return html[:close] + MEDIA_QUERY + html[close:]


ADDED_TO_CART_METRIC = "WcWiXd"


def fetch_real_event():
    """Ostatni realny event Added to Cart - podglad na prawdziwych danych."""
    q = urllib.parse.urlencode({
        "filter": f'equals(metric_id,"{ADDED_TO_CART_METRIC}")',
        "sort": "-datetime",
        "fields[event]": "event_properties",
        "page[size]": 1,
    })
    req = urllib.request.Request(
        "https://a.klaviyo.com/api/events?" + q,
        headers={"Authorization": f"Klaviyo-API-Key {read_key()}",
                 "revision": API_REVISION, "accept": "application/vnd.api+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)["data"]
    if not data:
        return None
    return data[0]["attributes"]["event_properties"]


def build_demo(ev):
    """Mapuje pola snippetu na wartosci z realnego eventu (lub zapasowe)."""
    ev = ev or {}
    price = ev.get("Price") or 199
    compare = ev.get("CompareAtPrice")
    # 83% eventow nie ma CompareAtPrice - dla podgladu galezi promocyjnej
    # dokladamy cene regularna, jesli realny event jej nie niesie
    compare_demo = compare or round(float(price) * 1.23)
    name = ev.get("Product Name") or "Twój produkt"
    return {
        "{{ event.ImageURL|default:'' }}": ev.get("ImageURL", ""),
        "{{ event|lookup:'Product Name'|default:'Produkt w Twoim koszyku' }}": name,
        "{{ event|lookup:'Product Name'|default:'Twój produkt' }}": name,
        "{{ event|lookup:'Variant Name'|default:'' }}": ev.get("Variant Name", ""),
        "{{ event.Quantity|floatformat:0|default:'1' }}":
            str(int(float(ev.get("Quantity") or 1))),
        "{{ event.Price|floatformat:0 }}": str(int(float(price))),
        "{{ event.CompareAtPrice|floatformat:0 }}": str(int(float(compare_demo))),
        "{{ event.CompareAtPrice|minus:event.Price|floatformat:0 }}":
            str(int(float(compare_demo) - float(price))),
        # stopka - zeby podglad nadawal sie do wyslania jako mail testowy
        "{% unsubscribe %}": '<a href="#" style="color:#727272;">Anuluj subskrypcję</a>',
        "{{ organization.name }}": "GENACTIV",
        "{{ organization.full_address }}": "[adres organizacji z Klaviyo]",
    }


IF_TAG = "{% if event.CompareAtPrice and event.CompareAtPrice > event.Price %}"


def render_demo(html, demo, promo=True):
    """Podglad: podstawia dane i rozwija wybrana galaz {% if %}.

    promo=True  -> galaz z cena regularna i oszczednoscia
    promo=False -> galaz {% else %}, czyli 83% realnych przypadkow
    """
    out = html
    for var, val in demo.items():
        out = out.replace(var, val)
    start, mid, end = out.find(IF_TAG), out.find("{% else %}"), out.find("{% endif %}")
    if -1 in (start, mid, end):
        return out
    branch = out[start + len(IF_TAG):mid] if promo else out[mid + len("{% else %}"):end]
    return out[:start] + branch + out[end + len("{% endif %}"):]


def main():
    section = io.open(SNIPPET, encoding="utf-8").read()
    html = fetch_template()
    print(f"Pobrano {TEMPLATE_ID}: {len(html):,} znakow")

    html, had = remove_existing_section(html)
    if had:
        print(f"Wykryto sekcje juz obecna w szablonie - podmieniam "
              f"(po usunieciu: {len(html):,} znakow)")

    merged = add_media_query(insert_section(html, section))
    merged, fixed = polish_footer(merged)
    if fixed:
        print("Stopka: angielski tekst + gole {% unsubscribe %} -> wersja polska")
    if merged.count(END_MARK) != 1:
        sys.exit(f"BLAD: sekcja wystepuje {merged.count(END_MARK)}x zamiast 1 - przerywam.")
    io.open(OUT_FULL, "w", encoding="utf-8").write(merged)
    print(f"Zapisano pelny szablon -> {OUT_FULL.relative_to(ROOT)} ({len(merged):,} znakow)")

    ev = fetch_real_event()
    if ev:
        print(f"Realny event Added to Cart: {ev.get('Product Name')!r} / "
              f"{ev.get('Variant Name')!r} / {ev.get('Price')} zl / "
              f"CompareAtPrice={ev.get('CompareAtPrice')}")
    else:
        print("UWAGA: brak realnych eventow, podglad na danych zapasowych")
    demo = build_demo(ev)

    io.open(OUT_DEMO, "w", encoding="utf-8").write(render_demo(merged, demo, promo=True))
    print(f"Zapisano podglad promo -> {OUT_DEMO.relative_to(ROOT)}")
    io.open(OUT_DEMO_NOPROMO, "w", encoding="utf-8").write(
        render_demo(merged, demo, promo=False))
    print(f"Zapisano podglad bez promocji -> {OUT_DEMO_NOPROMO.relative_to(ROOT)}")

    # sanity check kolejnosci
    i_cta = merged.find(CTA_IMAGE)
    i_sec = merged.find("KONIEC sekcji porzuconego koszyka")
    i_70 = merged.find(ANCHOR_IMAGE)
    ok = i_cta < i_sec < i_70
    print(f"Kolejnosc CTA < sekcja < 70%: {'OK' if ok else 'BLAD'}  ({i_cta} < {i_sec} < {i_70})")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()

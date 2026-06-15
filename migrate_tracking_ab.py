#!/usr/bin/env python3
"""
Migracja tracking scripts GEN-6 → NOTOAGENCY + A/B test identifier
Kopiuje Pandectes, CrazyEgg, app snippets i dodaje theme identifier do obu tematów.
"""

import requests
import json
import sys
import os
import time
import base64
from dotenv import load_dotenv

load_dotenv()

SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")
BASE_URL = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}"
HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}

SOURCE_THEME = 199333609804  # GEN-6 (aktywny, baseline 90%)
TARGET_THEME = 190479794508  # NOTOAGENCY (nowy, 10%)

# Rate limit: max 4 req/s, we do 2/s to be safe
REQUEST_DELAY = 0.6

def api_get(endpoint):
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, headers=HEADERS)
    time.sleep(REQUEST_DELAY)
    return resp.status_code, resp.json() if resp.text else None

def api_put(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    resp = requests.put(url, headers=HEADERS, json=data)
    time.sleep(REQUEST_DELAY)
    return resp.status_code, resp.json() if resp.text else None

def get_asset(theme_id, key):
    """Pobierz asset z tematu (text content)"""
    status, resp = api_get(f"/themes/{theme_id}/assets.json?asset[key]={key}")
    if status == 200:
        asset = resp.get("asset", {})
        return asset.get("value") or asset.get("attachment")
    print(f"  ❌ Nie mogę pobrać {key}: {status}")
    return None

def get_asset_binary(theme_id, key):
    """Pobierz asset jako base64 (dla obrazów)"""
    status, resp = api_get(f"/themes/{theme_id}/assets.json?asset[key]={key}&fields=key,attachment")
    if status == 200:
        return resp.get("asset", {}).get("attachment")
    print(f"  ❌ Nie mogę pobrać binary {key}: {status}")
    return None

def put_asset_text(theme_id, key, value):
    """Wgraj text asset"""
    data = {"asset": {"key": key, "value": value}}
    status, resp = api_put(f"/themes/{theme_id}/assets.json", data)
    if status in (200, 201):
        print(f"  ✅ {key}")
        return True
    print(f"  ❌ {key}: {status} - {resp}")
    return False

def put_asset_binary(theme_id, key, attachment_b64):
    """Wgraj binary asset (base64)"""
    data = {"asset": {"key": key, "attachment": attachment_b64}}
    status, resp = api_put(f"/themes/{theme_id}/assets.json", data)
    if status in (200, 201):
        print(f"  ✅ {key} (binary)")
        return True
    print(f"  ❌ {key}: {status} - {resp}")
    return False

# =====================================================
# A/B TEST IDENTIFIER SNIPPET
# =====================================================

AB_SNIPPET_TEMPLATE = """<!-- A/B Test Theme Identifier — GenActiv (added {date}) -->
<script>
(function() {{
  var THEME_VARIANT = '{variant}';
  var THEME_ID = '{theme_id}';

  // 1. dataLayer push (for GTM when re-enabled)
  window.dataLayer = window.dataLayer || [];
  window.dataLayer.push({{
    'event': 'ab_theme_loaded',
    'ab_theme_variant': THEME_VARIANT,
    'ab_theme_id': THEME_ID
  }});

  // 2. GA4 user property (works with gtag from content_for_header)
  function setGA4() {{
    if (typeof gtag === 'function') {{
      gtag('set', 'user_properties', {{
        'ab_theme_variant': THEME_VARIANT
      }});
      gtag('event', 'ab_test_impression', {{
        'ab_theme_variant': THEME_VARIANT,
        'ab_theme_id': THEME_ID
      }});
    }} else {{
      setTimeout(setGA4, 500);
    }}
  }}
  setGA4();

  // 3. Cookie for server-side / CrazyEgg / Hotjar segmentation
  document.cookie = 'ab_theme=' + THEME_VARIANT + ';path=/;max-age=2592000;SameSite=Lax';

  // 4. Meta tag for easy inspection
  var meta = document.createElement('meta');
  meta.name = 'ab-theme-variant';
  meta.content = THEME_VARIANT;
  document.head.appendChild(meta);
}})();
</script>
<!-- End A/B Test Theme Identifier -->"""

def generate_ab_snippet(variant, theme_id):
    from datetime import datetime
    return AB_SNIPPET_TEMPLATE.format(
        variant=variant,
        theme_id=theme_id,
        date=datetime.now().strftime('%Y-%m-%d')
    )

# =====================================================
# MAIN MIGRATION
# =====================================================

def copy_text_assets():
    """Kopiuj text-based assets z GEN-6 do NOTOAGENCY"""
    text_assets = [
        "snippets/pandectes-rules.liquid",
        "snippets/revy-upsell-script.liquid",
        "snippets/socialshopwave-helper.liquid",
        "snippets/socialshopwave-fb.liquid",
        "snippets/socialshopwave-gplus.liquid",
        "snippets/socialshopwave-widget-auth.liquid",
        "snippets/socialshopwave-widget-fave.liquid",
        "snippets/socialshopwave-widget-recommends.liquid",
        "snippets/socialshopwave-custom.css.liquid",
        "snippets/hulkapps-reorder-css.liquid",
        "snippets/hulkapps-order-json.liquid",
        "snippets/hulkapps-orders-json.liquid",
        "snippets/cookie-consent.liquid",
        "snippets/cookies-style.liquid",
        "snippets/taginstall-head.liquid",
        "snippets/taginstall-body.liquid",
    ]

    json_assets = [
        "assets/pandectes-settings.json",
    ]

    js_assets = [
        "assets/pandectes-rules.min.js",
    ]

    css_assets = [
        "assets/socialshopwave-custom.css",
    ]

    all_text = text_assets + json_assets + js_assets + css_assets

    ok = 0
    fail = 0
    for key in all_text:
        print(f"  📋 Kopiuję {key}...")
        content = get_asset(SOURCE_THEME, key)
        if content is None:
            fail += 1
            continue
        if put_asset_text(TARGET_THEME, key, content):
            ok += 1
        else:
            fail += 1

    return ok, fail

def copy_binary_assets():
    """Kopiuj obrazy (binary) z GEN-6 do NOTOAGENCY"""
    image_assets = [
        "assets/pandectes-logo.png",
        "assets/pandectes-reopen-logo.png",
    ]

    ok = 0
    fail = 0
    for key in image_assets:
        print(f"  🖼️  Kopiuję {key} (binary)...")
        b64 = get_asset_binary(SOURCE_THEME, key)
        if b64 is None:
            fail += 1
            continue
        if put_asset_binary(TARGET_THEME, key, b64):
            ok += 1
        else:
            fail += 1

    return ok, fail

def update_notoagency_theme_liquid():
    """Dodaj Pandectes + CrazyEgg + A/B identifier do NOTOAGENCY theme.liquid"""
    print("\n📝 Edytuję layout/theme.liquid w NOTOAGENCY...")

    content = get_asset(TARGET_THEME, "layout/theme.liquid")
    if content is None:
        print("  ❌ Nie mogę pobrać theme.liquid!")
        return False

    ab_snippet = generate_ab_snippet("NOTOAGENCY", str(TARGET_THEME))

    # Sprawdź czy już dodane
    if "ab_theme_variant" in content:
        print("  ⚠️  A/B identifier już istnieje w NOTOAGENCY - pomijam")
        return True

    # Znajdź miejsce w <head> — po <meta charset>
    insert_marker = '<meta charset="utf-8">'
    if insert_marker not in content:
        # Fallback: po <head>
        insert_marker = "<head>"

    tracking_block = f"""
<script src="{{{{ 'pandectes-rules.js' | file_url }}}}"></script>
<script type="text/javascript" src="//script.crazyegg.com/pages/scripts/0122/4300.js" async="async"></script>
{ab_snippet}
"""

    content = content.replace(
        insert_marker,
        insert_marker + tracking_block,
        1  # only first occurrence
    )

    # Dodaj app snippets przed </body>
    app_snippets = """
  {%- render 'hulkapps-reorder-css' -%}
  {%- render 'revy-upsell-script' -%}
"""

    # Wstaw przed </body> ale po Responso
    if "revy-upsell-script" not in content:
        content = content.replace("</body>", app_snippets + "</body>", 1)

    return put_asset_text(TARGET_THEME, "layout/theme.liquid", content)

def update_gen6_theme_liquid():
    """Dodaj A/B identifier do GEN-6 (baseline) theme.liquid"""
    print("\n📝 Dodaję A/B identifier do GEN-6 (baseline)...")

    content = get_asset(SOURCE_THEME, "layout/theme.liquid")
    if content is None:
        print("  ❌ Nie mogę pobrać theme.liquid!")
        return False

    if "ab_theme_variant" in content:
        print("  ⚠️  A/B identifier już istnieje w GEN-6 - pomijam")
        return True

    ab_snippet = generate_ab_snippet("GEN-6", str(SOURCE_THEME))

    # W GEN-6, wstaw po pandectes-rules.js
    insert_after = '<script src="{{ \'pandectes-rules.js\' | file_url }}"></script>'
    if insert_after in content:
        content = content.replace(insert_after, insert_after + "\n" + ab_snippet, 1)
    else:
        # Fallback: po <head>
        content = content.replace("<head>", "<head>\n" + ab_snippet, 1)

    return put_asset_text(SOURCE_THEME, "layout/theme.liquid", content)

# =====================================================

def main():
    print("=" * 60)
    print("MIGRACJA TRACKING: GEN-6 → NOTOAGENCY + A/B IDENTIFIERS")
    print(f"Source: GEN-6 (ID: {SOURCE_THEME}) — baseline 90%")
    print(f"Target: NOTOAGENCY (ID: {TARGET_THEME}) — variant 10%")
    print("=" * 60)

    if "--dry-run" in sys.argv:
        print("\n🔍 DRY RUN — pokazuję co bym zrobił:\n")
        print("1. Skopiuję snippets: pandectes, revy, socialshopwave, hulkapps, taginstall, cookies")
        print("2. Skopiuję assets: pandectes-settings.json, pandectes-rules.min.js, pandectes images")
        print("3. Edytuję NOTOAGENCY theme.liquid: +Pandectes +CrazyEgg +A/B identifier")
        print("4. Edytuję GEN-6 theme.liquid: +A/B identifier")
        print(f"\nA/B snippet (NOTOAGENCY):\n{generate_ab_snippet('NOTOAGENCY', str(TARGET_THEME))}")
        print(f"\nA/B snippet (GEN-6):\n{generate_ab_snippet('GEN-6', str(SOURCE_THEME))}")
        return

    # Step 1: Copy text assets
    print("\n📦 KROK 1: Kopiowanie text assets...")
    text_ok, text_fail = copy_text_assets()
    print(f"   Wynik: {text_ok} OK, {text_fail} FAIL")

    # Step 2: Copy binary assets (images)
    print("\n🖼️  KROK 2: Kopiowanie binary assets (images)...")
    bin_ok, bin_fail = copy_binary_assets()
    print(f"   Wynik: {bin_ok} OK, {bin_fail} FAIL")

    # Step 3: Update NOTOAGENCY theme.liquid
    print("\n✏️  KROK 3: Aktualizacja NOTOAGENCY theme.liquid...")
    noto_ok = update_notoagency_theme_liquid()

    # Step 4: Add A/B identifier to GEN-6
    print("\n✏️  KROK 4: Dodanie A/B identifier do GEN-6...")
    gen6_ok = update_gen6_theme_liquid()

    # Summary
    print("\n" + "=" * 60)
    print("PODSUMOWANIE MIGRACJI")
    print("=" * 60)
    print(f"Text assets:    {text_ok}/{text_ok + text_fail}")
    print(f"Binary assets:  {bin_ok}/{bin_ok + bin_fail}")
    print(f"NOTOAGENCY theme.liquid: {'✅' if noto_ok else '❌'}")
    print(f"GEN-6 A/B identifier:   {'✅' if gen6_ok else '❌'}")
    print()
    print("🔍 JAK ODRÓŻNIĆ TEMATY W ANALITYCE:")
    print("  • GA4 → User Properties → ab_theme_variant: 'GEN-6' vs 'NOTOAGENCY'")
    print("  • GA4 → Events → ab_test_impression (custom event)")
    print("  • dataLayer → ab_theme_variant (gdy GTM zostanie odkomentowany)")
    print("  • Cookie → ab_theme=GEN-6 / ab_theme=NOTOAGENCY")
    print("  • HTML → <meta name='ab-theme-variant' content='...'>")
    print()
    print("📊 W GA4 utwórz custom dimension:")
    print("   Scope: User | Property: ab_theme_variant")
    print("   Potem filtry/segmenty w raportach po wariancie tematu")
    print()
    if text_fail > 0 or bin_fail > 0:
        print(f"⚠️  {text_fail + bin_fail} plików nie udało się skopiować — sprawdź logi powyżej")

if __name__ == "__main__":
    main()

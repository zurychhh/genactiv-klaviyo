#!/usr/bin/env python3
"""
Fix tagowania wariantu A/B w Microsoft Clarity.

Problem: snippet A/B w <head> wywoluje clarity("set", ...) za guardem
  if (typeof clarity === 'function') { ... }
ale biegnie zanim loader Clarity wystartuje -> guard = false -> tag nigdy
sie nie ustawia -> custom tag ab_theme_variant pusty w Clarity.

Fix: poll na window.clarity (do ~30s), tag ustawiany gdy Clarity gotowy.
Clarity dziala w glownym oknie (nagrywa DOM), wiec poll zadziala.

Usage:
  python3 fix_clarity_tagging.py            # dry-run (pokazuje co zmieni)
  python3 fix_clarity_tagging.py --live     # backup + push do obu motywow
"""
import sys
from shopify_theme_api import get_asset, update_asset, backup_asset

THEMES = [
    (199333609804, "GEN-6 (AKTYWNY, baseline)"),
    (190479794508, "NOTOAGENCY (wariant)"),
]
ASSET = "layout/theme.liquid"

OLD_BLOCK = """  // 5. Microsoft Clarity custom tags — segmentacja A/B w heatmapach i nagraniach
  if (typeof clarity === 'function') {
    clarity("set", "ab_theme_variant", THEME_VARIANT);
    clarity("set", "theme_id", THEME_ID);
  }"""

NEW_BLOCK = """  // 5. Microsoft Clarity custom tags — poll az Clarity sie zaladuje (fix 2026-06-17)
  (function setClarityTags(tries) {
    if (typeof window.clarity === 'function') {
      window.clarity("set", "ab_theme_variant", THEME_VARIANT);
      window.clarity("set", "theme_id", THEME_ID);
    } else if (tries < 60) {
      setTimeout(function () { setClarityTags(tries + 1); }, 500);
    }
  })(0);"""

ALREADY_MARK = "setClarityTags"


def main():
    live = "--live" in sys.argv
    print("=" * 64)
    print("FIX CLARITY A/B TAGGING  —  " + ("LIVE (push do Shopify)" if live else "DRY-RUN"))
    print("=" * 64)

    for theme_id, label in THEMES:
        print(f"\n>>> {label}  (ID: {theme_id})")
        asset = get_asset(theme_id, ASSET)
        if not asset:
            print("   ❌ Nie udalo sie pobrac theme.liquid — pomijam")
            continue
        content = asset.get("value", "")

        if ALREADY_MARK in content:
            print("   ⏭️  Juz naprawione (setClarityTags obecny) — pomijam")
            continue
        if OLD_BLOCK not in content:
            print("   ⚠️  Nie znalazlem oczekiwanego bloku Clarity — pomijam (sprawdz recznie)")
            continue

        new_content = content.replace(OLD_BLOCK, NEW_BLOCK, 1)
        print(f"   ✅ Blok Clarity znaleziony. Rozmiar: {len(content)} -> {len(new_content)} znakow")

        if not live:
            print("   (dry-run) nie zapisuje. Uruchom z --live aby wypchnac.")
            continue

        bkp = backup_asset(theme_id, ASSET)
        if not bkp:
            print("   ❌ Backup nieudany — PRZERYWAM dla bezpieczenstwa")
            continue
        update_asset(theme_id, ASSET, new_content)

    print("\nGotowe." + ("" if live else "  (to byl DRY-RUN — dodaj --live)"))


if __name__ == "__main__":
    main()

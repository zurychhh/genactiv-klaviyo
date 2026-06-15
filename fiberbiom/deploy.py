#!/usr/bin/env python3
"""
Deploy Fiberbiom Landing Page to Shopify theme + create Page.
Uploads all sections, snippets, templates, and assets to the active theme,
then creates a Page with handle 'fiberbiom' assigned to the template.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopify_theme_api import get_main_theme, update_asset
from shopify_graphql import create_page, list_pages, update_page, execute_query

FIBERBIOM_DIR = os.path.dirname(os.path.abspath(__file__))

# Files to upload to theme, mapped as (local_path, theme_asset_key)
FILES = [
    # CSS & JS
    ("assets/fiberbiom.css", "assets/fiberbiom.css"),
    ("assets/fiberbiom.js", "assets/fiberbiom.js"),

    # Snippets
    ("snippets/fiberbiom-button.liquid", "snippets/fiberbiom-button.liquid"),

    # Sections
    ("sections/fiberbiom-hero.liquid", "sections/fiberbiom-hero.liquid"),
    ("sections/fiberbiom-problem.liquid", "sections/fiberbiom-problem.liquid"),
    ("sections/fiberbiom-solution.liquid", "sections/fiberbiom-solution.liquid"),
    ("sections/fiberbiom-how-it-works.liquid", "sections/fiberbiom-how-it-works.liquid"),
    ("sections/fiberbiom-stats.liquid", "sections/fiberbiom-stats.liquid"),
    ("sections/fiberbiom-how-to-use.liquid", "sections/fiberbiom-how-to-use.liquid"),
    ("sections/fiberbiom-faq.liquid", "sections/fiberbiom-faq.liquid"),
    ("sections/fiberbiom-cta-banner.liquid", "sections/fiberbiom-cta-banner.liquid"),
    ("sections/fiberbiom-bibliography.liquid", "sections/fiberbiom-bibliography.liquid"),

    # Template
    ("templates/page.fiberbiom.json", "templates/page.fiberbiom.json"),
]


def deploy_theme_files(theme_id, dry_run=False):
    """Upload all files to the Shopify theme."""
    print(f"\n{'[DRY RUN] ' if dry_run else ''}Uploading {len(FILES)} files to theme {theme_id}...\n")

    success = 0
    failed = 0

    for local_rel, asset_key in FILES:
        local_path = os.path.join(FIBERBIOM_DIR, local_rel)

        if not os.path.exists(local_path):
            print(f"  SKIP  {asset_key} — local file not found: {local_rel}")
            failed += 1
            continue

        with open(local_path, "r", encoding="utf-8") as f:
            content = f.read()

        size_kb = len(content.encode('utf-8')) / 1024

        if dry_run:
            print(f"  WOULD UPLOAD  {asset_key} ({size_kb:.1f} KB)")
            success += 1
        else:
            result = update_asset(theme_id, asset_key, content)
            if result:
                print(f"  OK    {asset_key} ({size_kb:.1f} KB)")
                success += 1
            else:
                print(f"  FAIL  {asset_key}")
                failed += 1

    print(f"\nResult: {success} uploaded, {failed} failed")
    return failed == 0


def ensure_page(dry_run=False):
    """Create or find the Fiberbiom page with handle 'fiberbiom'."""
    print("\nChecking for existing 'fiberbiom' page...")

    # Check if page already exists
    result = list_pages(50)
    if result and 'data' in result:
        for edge in result['data'].get('pages', {}).get('edges', []):
            node = edge['node']
            if node.get('handle') == 'fiberbiom':
                page_id = node['id']
                print(f"  Found existing page: {page_id} (handle: fiberbiom)")

                if not node.get('isPublished') and not dry_run:
                    print("  Publishing page...")
                    update_page(page_id, is_published=True)

                return page_id

    # Create new page
    if dry_run:
        print("  WOULD CREATE page 'Fiberbiom' with handle 'fiberbiom'")
        return None

    print("  Creating new page 'Fiberbiom'...")
    result = create_page(
        title="Fiberbiom",
        body_html="<p>Ta strona korzysta z szablonu page.fiberbiom. Treść jest zarządzana przez sekcje w Theme Editor.</p>",
        handle="fiberbiom",
        is_published=True
    )

    if result and 'data' in result:
        page_data = result['data'].get('pageCreate', {})
        errors = page_data.get('userErrors', [])
        if errors:
            print(f"  ERROR: {errors}")
            return None

        page = page_data.get('page', {})
        page_id = page.get('id')
        print(f"  Created: {page_id} (handle: {page.get('handle')})")
        return page_id

    print(f"  ERROR: {result}")
    return None


def main():
    dry_run = "--dry-run" in sys.argv

    print("=" * 60)
    print("FIBERBIOM LANDING PAGE — DEPLOY")
    print("=" * 60)

    # Step 1: Get active theme
    theme = get_main_theme()
    if not theme:
        print("ERROR: Could not find active theme")
        sys.exit(1)

    theme_id = theme.get("id")
    theme_name = theme.get("name")
    print(f"\nActive theme: {theme_name} (ID: {theme_id})")

    # Step 2: Upload files
    ok = deploy_theme_files(theme_id, dry_run=dry_run)
    if not ok and not dry_run:
        print("\nSome files failed to upload. Aborting page creation.")
        sys.exit(1)

    # Step 3: Create/find page
    page_id = ensure_page(dry_run=dry_run)

    # Summary
    print("\n" + "=" * 60)
    if dry_run:
        print("DRY RUN complete. Run without --dry-run to deploy.")
    else:
        print("DEPLOY COMPLETE")
        print(f"\nPage: https://genactiv.myshopify.com/pages/fiberbiom")
        print(f"Theme Editor: Shopify Admin → Online Store → Themes → Customize → Pages → Fiberbiom")
        if page_id:
            print(f"\nIMPORTANT: Go to Shopify Admin → Pages → Fiberbiom")
            print(f"  → Set 'Theme template' to 'page.fiberbiom'")
            print(f"  (GraphQL API cannot assign templates to pages)")
    print("=" * 60)


if __name__ == "__main__":
    main()

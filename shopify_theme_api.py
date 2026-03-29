#!/usr/bin/env python3
"""
Shopify Theme API Client
Zarządzanie motywami Shopify - odczyt i edycja plików theme
"""

import requests
import json
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja (ta sama co w shopify_graphql.py)
SHOPIFY_DOMAIN = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
ACCESS_TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

BASE_URL = f"https://{SHOPIFY_DOMAIN}/admin/api/{API_VERSION}"

HEADERS = {
    "Content-Type": "application/json",
    "X-Shopify-Access-Token": ACCESS_TOKEN
}


def api_get(endpoint):
    """GET request do Shopify API"""
    url = f"{BASE_URL}{endpoint}"
    response = requests.get(url, headers=HEADERS)
    return response.status_code, response.json() if response.text else None


def api_put(endpoint, data):
    """PUT request do Shopify API"""
    url = f"{BASE_URL}{endpoint}"
    response = requests.put(url, headers=HEADERS, json=data)
    return response.status_code, response.json() if response.text else None


def api_delete(endpoint):
    """DELETE request do Shopify API"""
    url = f"{BASE_URL}{endpoint}"
    response = requests.delete(url, headers=HEADERS)
    return response.status_code, response.json() if response.text else None


# ============================================
# THEME OPERATIONS
# ============================================

def list_themes():
    """Lista wszystkich motywów"""
    status, data = api_get("/themes.json")
    if status == 200 and data:
        return data.get("themes", [])
    elif status == 403:
        print("❌ BŁĄD 403: Brak uprawnień read_themes!")
        print("   Dodaj scope 'read_themes' w Shopify Admin → Apps → [App] → API scopes")
        return None
    else:
        print(f"❌ Błąd {status}: {data}")
        return None


def get_main_theme():
    """Pobierz aktywny (main) motyw"""
    themes = list_themes()
    if themes:
        for theme in themes:
            if theme.get("role") == "main":
                return theme
    return None


def list_assets(theme_id):
    """Lista wszystkich plików w motywie"""
    status, data = api_get(f"/themes/{theme_id}/assets.json")
    if status == 200 and data:
        return data.get("assets", [])
    elif status == 403:
        print("❌ BŁĄD 403: Brak uprawnień read_themes!")
        return None
    else:
        print(f"❌ Błąd {status}: {data}")
        return None


def get_asset(theme_id, asset_key):
    """Pobierz zawartość konkretnego pliku"""
    # URL encode the asset key
    encoded_key = requests.utils.quote(asset_key, safe='')
    status, data = api_get(f"/themes/{theme_id}/assets.json?asset[key]={encoded_key}")
    if status == 200 and data:
        return data.get("asset", {})
    elif status == 403:
        print("❌ BŁĄD 403: Brak uprawnień read_themes!")
        return None
    elif status == 404:
        print(f"❌ Plik nie znaleziony: {asset_key}")
        return None
    else:
        print(f"❌ Błąd {status}: {data}")
        return None


def update_asset(theme_id, asset_key, content):
    """Zaktualizuj/utwórz plik w motywie"""
    data = {
        "asset": {
            "key": asset_key,
            "value": content
        }
    }
    status, response = api_put(f"/themes/{theme_id}/assets.json", data)
    if status == 200:
        print(f"✅ Zaktualizowano: {asset_key}")
        return response.get("asset", {})
    elif status == 403:
        print("❌ BŁĄD 403: Brak uprawnień write_themes!")
        print("   Dodaj scope 'write_themes' w Shopify Admin → Apps → [App] → API scopes")
        return None
    else:
        print(f"❌ Błąd {status}: {response}")
        return None


def delete_asset(theme_id, asset_key):
    """Usuń plik z motywu"""
    encoded_key = requests.utils.quote(asset_key, safe='')
    status, data = api_delete(f"/themes/{theme_id}/assets.json?asset[key]={encoded_key}")
    if status == 200:
        print(f"✅ Usunięto: {asset_key}")
        return True
    elif status == 403:
        print("❌ BŁĄD 403: Brak uprawnień write_themes!")
        return False
    else:
        print(f"❌ Błąd {status}: {data}")
        return False


def backup_asset(theme_id, asset_key):
    """Utwórz backup pliku przed edycją"""
    asset = get_asset(theme_id, asset_key)
    if asset and asset.get("value"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = "theme_backups"
        os.makedirs(backup_dir, exist_ok=True)

        # Zamień / na _ w nazwie pliku
        safe_name = asset_key.replace("/", "_")
        backup_file = f"{backup_dir}/{safe_name}_{timestamp}.backup"

        with open(backup_file, "w", encoding="utf-8") as f:
            f.write(asset.get("value", ""))

        print(f"📦 Backup zapisany: {backup_file}")
        return backup_file
    return None


# ============================================
# HELPER FUNCTIONS
# ============================================

def find_consent_files(theme_id):
    """Znajdź pliki związane z consent/cookies"""
    assets = list_assets(theme_id)
    if not assets:
        return []

    consent_keywords = ["consent", "cookie", "gdpr", "privacy", "pandectes", "gtm", "gtag", "google"]
    found = []

    for asset in assets:
        key = asset.get("key", "").lower()
        for keyword in consent_keywords:
            if keyword in key:
                found.append(asset.get("key"))
                break

    return found


def search_in_assets(theme_id, search_term):
    """Szukaj tekstu w plikach motywu"""
    assets = list_assets(theme_id)
    if not assets:
        return []

    found = []
    search_lower = search_term.lower()

    # Przeszukuj tylko pliki tekstowe
    text_extensions = [".liquid", ".json", ".js", ".css", ".html"]

    for asset in assets:
        key = asset.get("key", "")
        if any(key.endswith(ext) for ext in text_extensions):
            content_asset = get_asset(theme_id, key)
            if content_asset and content_asset.get("value"):
                if search_lower in content_asset.get("value", "").lower():
                    found.append(key)

    return found


def print_json(data):
    """Wyświetl JSON w czytelnym formacie"""
    print(json.dumps(data, indent=2, ensure_ascii=False))


# ============================================
# CLI INTERFACE
# ============================================

def print_help():
    print("""
Shopify Theme API - Zarządzanie motywami

UŻYCIE:
  python shopify_theme_api.py <komenda> [argumenty]

KOMENDY:
  themes                    - Lista wszystkich motywów
  assets                    - Lista plików w aktywnym motywie
  assets <theme_id>         - Lista plików w konkretnym motywie

  get <asset_key>           - Pobierz zawartość pliku (z aktywnego motywu)
  get <theme_id> <key>      - Pobierz zawartość pliku z konkretnego motywu

  update <key> <file>       - Zaktualizuj plik z lokalnego pliku
  update <theme_id> <key> <file>

  backup <asset_key>        - Utwórz backup pliku

  find-consent              - Znajdź pliki związane z consent/cookies
  search <term>             - Szukaj tekstu w plikach motywu

PRZYKŁADY:
  python shopify_theme_api.py themes
  python shopify_theme_api.py get layout/theme.liquid
  python shopify_theme_api.py find-consent
  python shopify_theme_api.py search "Pandectes"
  python shopify_theme_api.py search "gtag"
""")


if __name__ == "__main__":
    print("=" * 60)
    print("SHOPIFY THEME API CLIENT")
    print(f"Store: {SHOPIFY_DOMAIN}")
    print("=" * 60)

    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    command = sys.argv[1]

    # === THEMES ===
    if command == "themes":
        print("\n🎨 Lista motywów:\n")
        themes = list_themes()
        if themes:
            for theme in themes:
                role = theme.get("role", "")
                status = "✅ AKTYWNY" if role == "main" else f"({role})"
                print(f"  ID: {theme.get('id')} | {theme.get('name')} {status}")

    # === ASSETS ===
    elif command == "assets":
        theme_id = sys.argv[2] if len(sys.argv) > 2 else None

        if not theme_id:
            theme = get_main_theme()
            if theme:
                theme_id = theme.get("id")
                print(f"\n📁 Pliki w aktywnym motywie: {theme.get('name')} (ID: {theme_id})\n")
        else:
            print(f"\n📁 Pliki w motywie ID: {theme_id}\n")

        if theme_id:
            assets = list_assets(theme_id)
            if assets:
                # Grupuj po folderach
                folders = {}
                for asset in assets:
                    key = asset.get("key", "")
                    folder = key.split("/")[0] if "/" in key else "(root)"
                    if folder not in folders:
                        folders[folder] = []
                    folders[folder].append(key)

                for folder in sorted(folders.keys()):
                    print(f"\n  📂 {folder}/")
                    for file in sorted(folders[folder]):
                        print(f"     - {file}")

                print(f"\n  Łącznie: {len(assets)} plików")

    # === GET ===
    elif command == "get":
        if len(sys.argv) < 3:
            print("Użycie: python shopify_theme_api.py get <asset_key>")
            sys.exit(1)

        # Sprawdź czy podano theme_id czy tylko key
        if len(sys.argv) == 3:
            asset_key = sys.argv[2]
            theme = get_main_theme()
            theme_id = theme.get("id") if theme else None
        else:
            theme_id = sys.argv[2]
            asset_key = sys.argv[3]

        if theme_id:
            print(f"\n📄 Pobieranie: {asset_key}\n")
            asset = get_asset(theme_id, asset_key)
            if asset:
                print(f"Key: {asset.get('key')}")
                print(f"Content-Type: {asset.get('content_type')}")
                print(f"Size: {asset.get('size')} bytes")
                print(f"Updated: {asset.get('updated_at')}")
                print("\n--- ZAWARTOŚĆ ---\n")
                print(asset.get("value", "(brak zawartości - plik binarny?)"))

    # === BACKUP ===
    elif command == "backup":
        if len(sys.argv) < 3:
            print("Użycie: python shopify_theme_api.py backup <asset_key>")
            sys.exit(1)

        asset_key = sys.argv[2]
        theme = get_main_theme()
        if theme:
            backup_asset(theme.get("id"), asset_key)

    # === FIND-CONSENT ===
    elif command == "find-consent":
        print("\n🔍 Szukam plików związanych z consent/cookies...\n")
        theme = get_main_theme()
        if theme:
            found = find_consent_files(theme.get("id"))
            if found:
                print("Znalezione pliki:")
                for f in found:
                    print(f"  - {f}")
            else:
                print("Nie znaleziono plików z 'consent/cookie/gdpr' w nazwie.")

    # === SEARCH ===
    elif command == "search":
        if len(sys.argv) < 3:
            print("Użycie: python shopify_theme_api.py search <term>")
            sys.exit(1)

        search_term = sys.argv[2]
        print(f"\n🔍 Szukam '{search_term}' w plikach motywu...\n")
        print("(To może potrwać - przeszukuję wszystkie pliki tekstowe)\n")

        theme = get_main_theme()
        if theme:
            found = search_in_assets(theme.get("id"), search_term)
            if found:
                print(f"Znaleziono w {len(found)} plikach:")
                for f in found:
                    print(f"  - {f}")
            else:
                print(f"Nie znaleziono '{search_term}' w żadnym pliku.")

    # === UPDATE ===
    elif command == "update":
        if len(sys.argv) < 4:
            print("Użycie: python shopify_theme_api.py update <asset_key> <local_file>")
            print("   lub: python shopify_theme_api.py update <theme_id> <asset_key> <local_file>")
            sys.exit(1)

        if len(sys.argv) == 4:
            asset_key = sys.argv[2]
            local_file = sys.argv[3]
            theme = get_main_theme()
            theme_id = theme.get("id") if theme else None
        else:
            theme_id = sys.argv[2]
            asset_key = sys.argv[3]
            local_file = sys.argv[4]

        if theme_id and os.path.exists(local_file):
            # Najpierw backup
            print(f"\n📦 Tworzę backup przed edycją...")
            backup_asset(theme_id, asset_key)

            # Wczytaj nową zawartość
            with open(local_file, "r", encoding="utf-8") as f:
                new_content = f.read()

            print(f"\n📝 Aktualizuję {asset_key}...")
            update_asset(theme_id, asset_key, new_content)
        elif not os.path.exists(local_file):
            print(f"❌ Plik nie istnieje: {local_file}")

    # === HELP ===
    elif command in ["help", "-h", "--help"]:
        print_help()

    else:
        print(f"❌ Nieznana komenda: {command}")
        print_help()

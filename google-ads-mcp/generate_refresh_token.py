#!/usr/bin/env python3
"""
Google Ads API Refresh Token Generator
Uses local server method (opens browser automatically)
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
import json
import os
import sys

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv()

_client_id = os.environ.get("GOOGLE_OAUTH_CLIENT_ID") or os.environ.get("GA4_OAUTH_CLIENT_ID", "")
_client_secret = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET") or os.environ.get("GA4_OAUTH_CLIENT_SECRET", "")

if not _client_id or not _client_secret:
    print("Ustaw GOOGLE_OAUTH_CLIENT_ID i GOOGLE_OAUTH_CLIENT_SECRET w .env")
    sys.exit(1)

CLIENT_CONFIG = {
    "installed": {
        "client_id": _client_id,
        "client_secret": _client_secret,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

SCOPES = ["https://www.googleapis.com/auth/adwords"]

def main():
    print("=" * 70)
    print("  GOOGLE ADS API - REFRESH TOKEN GENERATOR")
    print("  Konto: Genactiv (253-832-8866)")
    print("=" * 70)
    print()
    print("Przegladarka otworzy sie automatycznie...")
    print("Zaloguj sie na konto Google powiazane z Google Ads.")
    print()

    # Create flow
    flow = InstalledAppFlow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES
    )

    # Run local server - opens browser automatically
    # Port 8080 is commonly allowed, with fallback ports
    try:
        credentials = flow.run_local_server(
            port=8080,
            prompt='consent',
            authorization_prompt_message='',
            success_message='Autoryzacja zakonczona! Mozesz zamknac to okno.',
            open_browser=True
        )
    except Exception as e:
        print(f"Port 8080 zajety, probuje 8090...")
        credentials = flow.run_local_server(
            port=8090,
            prompt='consent',
            authorization_prompt_message='',
            success_message='Autoryzacja zakonczona! Mozesz zamknac to okno.',
            open_browser=True
        )

    print()
    print("=" * 70)
    print("  SUKCES! Oto Twoje dane:")
    print("=" * 70)
    print()
    print(f"REFRESH_TOKEN={credentials.refresh_token}")
    print()

    # Save credentials in format usable by MCP server
    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_id": CLIENT_CONFIG["installed"]["client_id"],
        "client_secret": CLIENT_CONFIG["installed"]["client_secret"],
        "scopes": SCOPES
    }

    # Save to the location MCP server expects
    script_dir = os.path.dirname(os.path.abspath(__file__))
    token_path = os.path.join(script_dir, "google-ads-mcp-server", "google_ads_token.json")

    os.makedirs(os.path.dirname(token_path), exist_ok=True)
    with open(token_path, "w") as f:
        json.dump(token_data, f, indent=2)

    print(f"Token zapisany do: {token_path}")
    print()

    # Also save legacy format
    developer_token = os.environ.get("GOOGLE_ADS_DEVELOPER_TOKEN", "")
    login_customer_id = os.environ.get("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "2538328866")
    legacy_data = {
        "refresh_token": credentials.refresh_token,
        "client_id": CLIENT_CONFIG["installed"]["client_id"],
        "client_secret": CLIENT_CONFIG["installed"]["client_secret"],
        "developer_token": developer_token,
        "login_customer_id": login_customer_id
    }

    legacy_path = os.path.join(script_dir, "google_ads_credentials.json")
    with open(legacy_path, "w") as f:
        json.dump(legacy_data, f, indent=2)

    print(f"Zapisano takze do: {legacy_path}")
    print()
    print("=" * 70)
    print("Teraz zrestartuj Claude Code aby MCP uzylo nowego tokena!")
    print("=" * 70)

if __name__ == "__main__":
    main()

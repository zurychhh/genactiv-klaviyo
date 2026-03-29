#!/usr/bin/env python3
"""
Google Ads API Refresh Token Generator
Uses local server method (opens browser automatically)
"""

from google_auth_oauthlib.flow import InstalledAppFlow
import json
import os

CLIENT_CONFIG = {
    "installed": {
        "client_id": "922442902358-nrq0c7it50uoiq0gfoeeii7lgfvcbq97.apps.googleusercontent.com",
        "client_secret": "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",
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
    legacy_data = {
        "refresh_token": credentials.refresh_token,
        "client_id": CLIENT_CONFIG["installed"]["client_id"],
        "client_secret": CLIENT_CONFIG["installed"]["client_secret"],
        "developer_token": "uA8Vjo2J4B-3qVdH4LcEXQ",
        "login_customer_id": "2538328866"
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

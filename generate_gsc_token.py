#!/usr/bin/env python3
"""
Google Search Console API - OAuth Token Generator
Uses the same Google Cloud project as GA4 / Google Ads.
Generates a refresh token for GSC MCP server.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
import json
import os
import re

load_dotenv()

CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("GA4_OAUTH_CLIENT_ID", ""),
        "client_secret": os.environ.get("GA4_OAUTH_CLIENT_SECRET", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
]


def main():
    print("=" * 70)
    print("  GOOGLE SEARCH CONSOLE - TOKEN GENERATOR")
    print("  Domena: genactiv.pl")
    print("=" * 70)
    print()
    print("Przegladarka otworzy sie automatycznie...")
    print("Zaloguj sie na TO SAMO konto Google co dla GA4 / Google Ads.")
    print()

    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)

    try:
        credentials = flow.run_local_server(
            port=8086,
            prompt='consent',
            authorization_prompt_message='',
            success_message='Autoryzacja GSC zakonczona! Mozesz zamknac to okno.',
            open_browser=True
        )
    except Exception:
        print("Port 8086 zajety, probuje 8096...")
        credentials = flow.run_local_server(
            port=8096,
            prompt='consent',
            authorization_prompt_message='',
            success_message='Autoryzacja GSC zakonczona! Mozesz zamknac to okno.',
            open_browser=True
        )

    print()
    print("SUKCES!")
    print()
    print("GSC_REFRESH_TOKEN (do .env):")
    print(credentials.refresh_token)
    print()

    # Update .env
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_content = f.read()
        if "GSC_REFRESH_TOKEN=" in env_content:
            env_content = re.sub(
                r"GSC_REFRESH_TOKEN=.*",
                f"GSC_REFRESH_TOKEN={credentials.refresh_token}",
                env_content
            )
        else:
            env_content += f"\nGSC_REFRESH_TOKEN={credentials.refresh_token}\n"
        with open(env_path, "w") as f:
            f.write(env_content)
        print(f"Zaktualizowano {env_path}")

    print()
    print("=" * 70)
    print("GOTOWE! Uzyj tego tokena w konfiguracji MCP serwera GSC.")
    print("Scope: webmasters.readonly (read-only)")
    print("Zrestartuj Claude Code po konfiguracji .mcp.json")
    print("=" * 70)


if __name__ == "__main__":
    main()

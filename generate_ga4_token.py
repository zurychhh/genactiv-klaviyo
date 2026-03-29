#!/usr/bin/env python3
"""
GA4 Analytics API - OAuth Token Generator
Uses the same Google Cloud project as Google Ads MCP.
Generates Application Default Credentials for analytics-mcp.
"""

from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
import json
import os

load_dotenv()

# Same client credentials as Google Ads (same GCP project 922442902358)
CLIENT_CONFIG = {
    "installed": {
        "client_id": os.environ.get("GA4_OAUTH_CLIENT_ID", ""),
        "client_secret": os.environ.get("GA4_OAUTH_CLIENT_SECRET", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://localhost"]
    }
}

SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]

def main():
    print("=" * 70)
    print("  GA4 ANALYTICS API - TOKEN GENERATOR")
    print("  Konto: GenActiv (G-KE8T99MGMJ)")
    print("  Projekt GCP: 922442902358")
    print("=" * 70)
    print()
    print("Przegladarka otworzy sie automatycznie...")
    print("Zaloguj sie na TO SAMO konto Google co dla Google Ads.")
    print()

    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)

    try:
        credentials = flow.run_local_server(
            port=8085,
            prompt='consent',
            authorization_prompt_message='',
            success_message='Autoryzacja GA4 zakonczona! Mozesz zamknac to okno.',
            open_browser=True
        )
    except Exception:
        print("Port 8085 zajety, probuje 8095...")
        credentials = flow.run_local_server(
            port=8095,
            prompt='consent',
            authorization_prompt_message='',
            success_message='Autoryzacja GA4 zakonczona! Mozesz zamknac to okno.',
            open_browser=True
        )

    print()
    print("SUKCES!")
    print()

    # Save as Application Default Credentials (ADC)
    # This is where gcloud would save them - analytics-mcp reads from here
    adc_dir = os.path.expanduser("~/.config/gcloud")
    os.makedirs(adc_dir, exist_ok=True)
    adc_path = os.path.join(adc_dir, "application_default_credentials.json")

    adc_data = {
        "client_id": CLIENT_CONFIG["installed"]["client_id"],
        "client_secret": CLIENT_CONFIG["installed"]["client_secret"],
        "refresh_token": credentials.refresh_token,
        "type": "authorized_user"
    }

    with open(adc_path, "w") as f:
        json.dump(adc_data, f, indent=2)

    print(f"Token zapisany do: {adc_path}")
    print()
    print("=" * 70)
    print("GOTOWE! analytics-mcp uzyje tego tokena automatycznie.")
    print("Zrestartuj Claude Code zeby MCP serwer GA4 sie zaladowal.")
    print("=" * 70)

if __name__ == "__main__":
    main()

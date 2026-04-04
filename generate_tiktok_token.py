#!/usr/bin/env python3
"""
TikTok Business API - OAuth Token Generator
Generates access_token + refresh_token for tiktok-ads-mcp.

Usage:
    python3 generate_tiktok_token.py

Flow:
1. Opens browser with TikTok authorization URL
2. User logs in, accepts permissions
3. TikTok redirects to genactiv.pl/?auth_code=XXX
4. User copies auth_code from URL, pastes into terminal
5. Script exchanges code for access_token + refresh_token

Note: Access tokens expire every 24h. Refresh tokens are valid for 1 year.
Use refresh_token to get new access_token automatically (tiktok-ads-mcp handles this).
"""

import json
import urllib.parse
import webbrowser
import requests

APP_ID = "7612480542698176529"
APP_SECRET = "08f4714fd078a0b314a318acbb163648d9f20c8d"
REDIRECT_URI = "https://genactiv.pl/"

AUTH_URL = "https://business-api.tiktok.com/portal/auth"
TOKEN_URL = "https://business-api.tiktok.com/open_api/v1.3/oauth2/access_token/"


def main():
    print("=" * 70)
    print("  TIKTOK BUSINESS API - TOKEN GENERATOR")
    print("  App ID:", APP_ID)
    print("=" * 70)
    print()

    # Build authorization URL
    params = {
        "app_id": APP_ID,
        "redirect_uri": REDIRECT_URI,
        "state": "genactiv",
    }
    auth_url = f"{AUTH_URL}?{urllib.parse.urlencode(params)}"

    print("Otwieram przegladarke z TikTok Business autoryzacja...")
    print()
    print("URL:", auth_url)
    print()
    webbrowser.open(auth_url)

    print("Po zalogowaniu TikTok przekieruje na:")
    print(f"  {REDIRECT_URI}?auth_code=XXXXX")
    print()

    auth_code = input("Wklej auth_code z URL: ").strip()

    if not auth_code:
        print("Blad: auth_code jest pusty!")
        return

    print()
    print("Wymieniam auth_code na access_token...")

    response = requests.post(TOKEN_URL, json={
        "app_id": APP_ID,
        "secret": APP_SECRET,
        "auth_code": auth_code,
    })

    data = response.json()

    if data.get("code") != 0:
        print(f"Blad API: {data.get('message', 'Unknown error')}")
        print(json.dumps(data, indent=2))
        return

    token_data = data.get("data", {})
    access_token = token_data.get("access_token", "")
    advertiser_ids = token_data.get("advertiser_ids", [])

    print()
    print("=" * 70)
    print("SUKCES!")
    print("=" * 70)
    print()
    print(f"ACCESS_TOKEN: {access_token}")
    print(f"ADVERTISER_IDS: {advertiser_ids}")
    print()
    print("=" * 70)
    print("Ustaw w Railway:")
    print()
    print(f"  TIKTOK_ACCESS_TOKEN={access_token}")
    print(f"  TIKTOK_APP_ID={APP_ID}")
    print(f"  TIKTOK_SECRET={APP_SECRET}")
    print()
    print("Token wygasa co 24h — tiktok-ads-mcp odswieza go automatycznie")
    print("za pomoca refresh flow (APP_ID + SECRET).")
    print("=" * 70)


if __name__ == "__main__":
    main()

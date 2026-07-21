#!/usr/bin/env python3
"""Autoryzacja TikTok Shop Open API dla GenActiv — zdobycie access_token + refresh_token + shop_cipher.

Flow (TikTok Shop Partner/Seller Open API, host auth.tiktok-shops.com):
  1) `url`            → wypisuje link autoryzacyjny; otwierasz go w przeglądarce zalogowanej
                         na konto sprzedawcy GenActiv i klikasz „Autoryzuj".
  2) po autoryzacji TikTok przekieruje na REDIRECT_URI z ?code=XXXX (odczytujesz z paska adresu).
  3) `code XXXX`      → wymienia auth_code na access_token + refresh_token (token/get),
                         potem pobiera listę autoryzowanych sklepów → zapisuje shop_cipher.
  4) `refresh`        → odświeża access_token przy użyciu refresh_token.

Wszystko ląduje w .tiktok-shop.env (obok app_key/app_secret). Skrypt jest samodzielny (nie importuje serwera).

Uwaga do linku autoryzacyjnego: w Partner Center na stronie aplikacji jest gotowy „Authorization URL"
(czasem z service_id). Jeśli poniższy link nie zadziała, WKLEJ ten z panelu — flow z kodem jest ten sam.
"""
import hashlib
import hmac
import json
import os
import sys
import time
from urllib.parse import quote

import requests

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".tiktok-shop.env")
ENV_PATH = os.path.abspath(ENV_PATH)

AUTH_BASE = "https://auth.tiktok-shops.com/api/v2"
API_BASE = "https://open-api.tiktokglobalshop.com"
# Link autoryzacyjny (seller-facing). service_id z Partner Center; fallback na app_key-based.
AUTHORIZE_URL = "https://services.tiktokshop.com/open/authorize"
SHOPS_VER = "202309"  # /authorization/{ver}/shops
EXCLUDE = {"app_secret", "access_token", "sign", "token"}


def _load_env():
    env = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env


def _save_env(updates):
    env = _load_env()
    env.update(updates)
    with open(ENV_PATH, "w") as f:
        for k, v in env.items():
            f.write(f"{k}={v}\n")
    os.chmod(ENV_PATH, 0o600)


def _sign(path, params, secret, body_str=None):
    """Podpis TikTok Shop: HMAC-SHA256(secret, secret + path + concat(sorted k+v) + body + secret) → hex lowercase.
    Wyklucza sign/access_token/app_secret/token. Body doklejane tylko dla JSON (nie multipart)."""
    keys = sorted(k for k in params if k not in EXCLUDE)
    base = path + "".join(f"{k}{params[k]}" for k in keys)
    if body_str:
        base += body_str
    wrapped = f"{secret}{base}{secret}"
    return hmac.new(secret.encode(), wrapped.encode(), hashlib.sha256).hexdigest()


def cmd_url(env):
    app_key = env.get("TIKTOK_SHOP_APP_KEY", "")
    service_id = env.get("TIKTOK_SHOP_SERVICE_ID", "")
    redirect = env.get("TIKTOK_SHOP_REDIRECT_URI", "https://genactiv.pl/tiktok-callback")
    state = "genactiv"
    print("\n=== Link autoryzacyjny TikTok Shop ===\n")
    if service_id:
        url = f"{AUTHORIZE_URL}?service_id={service_id}&state={state}"
        print("Wariant A (service_id z Partner Center):")
        print(url + "\n")
    print("Wariant B (app_key):")
    print(f"{AUTHORIZE_URL}?app_key={app_key}&state={state}\n")
    print("NAJPEWNIEJ: skopiuj gotowy 'Authorization URL' ze strony aplikacji w Partner Center.")
    print(f"Redirect skonfigurowany: {redirect}")
    print("\nPo autoryzacji odczytaj ?code=... z paska adresu i uruchom:")
    print("  python3 generate_tiktok_shop_token.py code <TWOJ_CODE>\n")


def cmd_code(env, auth_code):
    app_key = env["TIKTOK_SHOP_APP_KEY"]
    app_secret = env["TIKTOK_SHOP_APP_SECRET"]
    r = requests.get(f"{AUTH_BASE}/token/get", params={
        "app_key": app_key, "app_secret": app_secret,
        "auth_code": auth_code, "grant_type": "authorized_code",
    }, timeout=60)
    data = r.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    if data.get("code") not in (0, None):
        print("\n❌ Wymiana kodu nie powiodła się — patrz message wyżej.")
        return
    d = data.get("data", {})
    updates = {
        "TIKTOK_SHOP_ACCESS_TOKEN": d.get("access_token", ""),
        "TIKTOK_SHOP_REFRESH_TOKEN": d.get("refresh_token", ""),
        "TIKTOK_SHOP_ACCESS_TOKEN_EXPIRE": str(d.get("access_token_expire_in", "")),
    }
    _save_env(updates)
    print(f"\n✅ Zapisano access_token/refresh_token do {ENV_PATH}")
    _fetch_shop_cipher(app_key, app_secret, d.get("access_token", ""))


def _fetch_shop_cipher(app_key, app_secret, access_token):
    path = f"/authorization/{SHOPS_VER}/shops"
    ts = int(time.time())
    params = {"app_key": app_key, "timestamp": ts}
    params["sign"] = _sign(path, params, app_secret)
    r = requests.get(API_BASE + path, params=params,
                     headers={"x-tts-access-token": access_token, "content-type": "application/json"}, timeout=60)
    data = r.json()
    print("\n=== Autoryzowane sklepy ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    shops = (data.get("data") or {}).get("shops") or []
    if shops:
        cipher = shops[0].get("cipher", "")
        _save_env({"TIKTOK_SHOP_CIPHER": cipher, "TIKTOK_SHOP_ID": str(shops[0].get("id", ""))})
        print(f"\n✅ Zapisano shop_cipher = {cipher}  (sklep: {shops[0].get('name','?')})")
    else:
        print("\n⚠️  Brak sklepów w odpowiedzi — jeśli code==0 ale pusto, sprawdź czy sklep autoryzował appkę.")


def cmd_refresh(env):
    r = requests.get(f"{AUTH_BASE}/token/refresh", params={
        "app_key": env["TIKTOK_SHOP_APP_KEY"], "app_secret": env["TIKTOK_SHOP_APP_SECRET"],
        "refresh_token": env["TIKTOK_SHOP_REFRESH_TOKEN"], "grant_type": "refresh_token",
    }, timeout=60)
    data = r.json()
    print(json.dumps(data, indent=2, ensure_ascii=False))
    if data.get("code") in (0, None):
        d = data.get("data", {})
        _save_env({
            "TIKTOK_SHOP_ACCESS_TOKEN": d.get("access_token", ""),
            "TIKTOK_SHOP_REFRESH_TOKEN": d.get("refresh_token", ""),
            "TIKTOK_SHOP_ACCESS_TOKEN_EXPIRE": str(d.get("access_token_expire_in", "")),
        })
        print("\n✅ Odświeżono access_token.")


def main():
    env = _load_env()
    if not env.get("TIKTOK_SHOP_APP_KEY") or not env.get("TIKTOK_SHOP_APP_SECRET"):
        print(f"Brak app_key/app_secret w {ENV_PATH}"); sys.exit(1)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "url"
    if cmd == "url":
        cmd_url(env)
    elif cmd == "code":
        if len(sys.argv) < 3:
            print("Użycie: generate_tiktok_shop_token.py code <AUTH_CODE>"); sys.exit(1)
        cmd_code(env, sys.argv[2])
    elif cmd == "refresh":
        cmd_refresh(env)
    else:
        print("Komendy: url | code <AUTH_CODE> | refresh")


if __name__ == "__main__":
    main()

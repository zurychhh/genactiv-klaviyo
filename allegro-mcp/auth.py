"""Allegro Device Flow — jednorazowe logowanie (RFC 8628).

Uruchom ręcznie gdy trzeba (po)łączyć aplikację z kontem:
    python auth.py
Pokaże kod + link, poczeka aż zatwierdzisz w przeglądarce, zapisze tokeny
do allegro_tokens.json (access_token + refresh_token). Serwer MCP potem
sam odświeża access_token przez refresh_token.

Wymaga ALLEGRO_CLIENT_ID i ALLEGRO_CLIENT_SECRET w środowisku/.env.
"""
import base64
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

try:
    from dotenv import load_dotenv
    load_dotenv(pathlib.Path(__file__).resolve().parents[1] / ".env")
except Exception:
    pass

CID = os.environ["ALLEGRO_CLIENT_ID"]
SECRET = os.environ["ALLEGRO_CLIENT_SECRET"]
TOKENS_PATH = pathlib.Path(__file__).with_name("allegro_tokens.json")
BASIC = base64.b64encode(f"{CID}:{SECRET}".encode()).decode()


def _post(url: str, data: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=urllib.parse.urlencode(data).encode(),
        headers={"Authorization": f"Basic {BASIC}", "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main() -> None:
    dev = _post("https://allegro.pl/auth/oauth/device", {"client_id": CID})
    print("\n=== AUTORYZACJA ALLEGRO ===")
    print("1) Otwórz:", dev["verification_uri_complete"])
    print("   (lub", dev["verification_uri"], "i wpisz kod:", dev["user_code"], ")")
    print("2) Zaloguj się i kliknij 'Skojarz'. Czekam...\n")
    deadline = time.time() + dev.get("expires_in", 600)
    interval = dev.get("interval", 5)
    while time.time() < deadline:
        try:
            tok = _post("https://allegro.pl/auth/oauth/token", {
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
                "device_code": dev["device_code"],
            })
            tok["obtained_at"] = int(time.time())
            TOKENS_PATH.write_text(json.dumps(tok, indent=2))
            print("OK — tokeny zapisane do", TOKENS_PATH)
            return
        except urllib.error.HTTPError as e:
            err = json.loads(e.read().decode() or "{}").get("error", "")
            if err in ("authorization_pending", "slow_down"):
                time.sleep(interval)
                continue
            print("BŁĄD:", err or e.code)
            return
    print("TIMEOUT: brak autoryzacji w czasie")


if __name__ == "__main__":
    main()

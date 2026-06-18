"""Allegro MCP server — wrapper na Allegro REST API (api.allegro.pl).

Autoryzacja: Device Flow (patrz auth.py). Tokeny w allegro_tokens.json.
access_token jest automatycznie odświeżany przez refresh_token.

Wymaga ALLEGRO_CLIENT_ID i ALLEGRO_CLIENT_SECRET w środowisku (do odświeżania).
Uruchomienie: fastmcp run server.py
"""
import base64
import json
import os
import pathlib
import time
import urllib.error
import urllib.parse
import urllib.request

from fastmcp import FastMCP

API = "https://api.allegro.pl"
ACCEPT = "application/vnd.allegro.public.v1+json"
TOKENS_PATH = pathlib.Path(__file__).with_name("allegro_tokens.json")
CID = os.environ.get("ALLEGRO_CLIENT_ID", "")
SECRET = os.environ.get("ALLEGRO_CLIENT_SECRET", "")

mcp = FastMCP("allegro")


def _load_tokens() -> dict:
    if not TOKENS_PATH.exists():
        return {}
    return json.loads(TOKENS_PATH.read_text())


def _refresh(tok: dict) -> dict:
    basic = base64.b64encode(f"{CID}:{SECRET}".encode()).decode()
    data = urllib.parse.urlencode({
        "grant_type": "refresh_token",
        "refresh_token": tok["refresh_token"],
    }).encode()
    req = urllib.request.Request(
        "https://allegro.pl/auth/oauth/token",
        data=data,
        headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        new = json.loads(r.read().decode())
    new["obtained_at"] = int(time.time())
    TOKENS_PATH.write_text(json.dumps(new, indent=2))
    return new


def _access_token() -> str | None:
    tok = _load_tokens()
    if not tok:
        return None
    # odśwież jeśli wygasa w ciągu 2 min
    if time.time() >= tok.get("obtained_at", 0) + tok.get("expires_in", 0) - 120:
        if tok.get("refresh_token"):
            tok = _refresh(tok)
    return tok.get("access_token")


def request(method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    """Wykonuje request do Allegro API. Zwraca dict (parsed JSON) lub {status:ERROR}."""
    token = _access_token()
    if not token:
        return {"status": "ERROR", "error_message": "Brak tokenów — uruchom auth.py (device flow)."}
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None}, doseq=True)
    headers = {"Authorization": f"Bearer {token}", "Accept": ACCEPT}
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = ACCEPT
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {"status": "SUCCESS", "http_status": r.status}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:800]
        try:
            detail = json.loads(detail)
        except Exception:
            pass
        return {"status": "ERROR", "http_status": e.code, "error": detail}
    except Exception as e:  # noqa: BLE001
        return {"status": "ERROR", "error_message": f"{type(e).__name__}: {e}"}


# ============================ KONTO ============================

@mcp.tool
def get_me() -> dict:
    """Dane zalogowanego konta Allegro (login, firma, NIP, marketplace, funkcje)."""
    return request("GET", "/me")


# ============================ OFERTY ============================

@mcp.tool
def get_offers(limit: int = 20, offset: int = 0, name: str | None = None,
               publication_status: str | None = None, selling_format: str | None = None) -> dict:
    """Lista ofert sprzedawcy. publication_status: ACTIVE/INACTIVE/ACTIVATING/ENDED.
    selling_format: BUY_NOW/AUCTION/ADVERTISEMENT. name = filtr po nazwie."""
    params = {"limit": limit, "offset": offset, "name": name}
    if publication_status:
        params["publication.status"] = publication_status
    if selling_format:
        params["sellingMode.format"] = selling_format
    return request("GET", "/sale/offers", params)


@mcp.tool
def get_offer(offer_id: str) -> dict:
    """Pełne dane oferty (product-offer): nazwa, parametry, ceny, stany, opis, zdjęcia."""
    return request("GET", f"/sale/product-offers/{offer_id}")


@mcp.tool
def update_offer_quantity(offer_id: str, quantity: int) -> dict:
    """Zmienia dostępny stan magazynowy oferty."""
    return request("PATCH", f"/sale/product-offers/{offer_id}", body={"stock": {"available": quantity}})


@mcp.tool
def update_offer_price(offer_id: str, price: str, currency: str = "PLN") -> dict:
    """Zmienia cenę 'kup teraz' oferty. price jako string, np. '79.99'."""
    return request("PATCH", f"/sale/product-offers/{offer_id}",
                   body={"sellingMode": {"price": {"amount": price, "currency": currency}}})


# ============================ ZAMÓWIENIA ============================

@mcp.tool
def get_orders(limit: int = 20, offset: int = 0, status: str | None = None,
               fulfillment_status: str | None = None, updated_at_from: str | None = None) -> dict:
    """Lista zamówień (checkout-forms). status: BOUGHT/FILLED_IN/READY_FOR_PROCESSING/CANCELLED.
    fulfillment_status: NEW/PROCESSING/READY_FOR_SHIPMENT/SENT/PICKED_UP/CANCELLED/SUSPENDED.
    updated_at_from = ISO8601, np. '2026-06-01T00:00:00.000Z'."""
    params = {"limit": limit, "offset": offset, "status": status,
              "fulfillment.status": fulfillment_status, "updatedAt.gte": updated_at_from}
    return request("GET", "/order/checkout-forms", params)


@mcp.tool
def get_order(order_id: str) -> dict:
    """Szczegóły zamówienia: kupujący, pozycje, dostawa, płatność, faktura."""
    return request("GET", f"/order/checkout-forms/{order_id}")


@mcp.tool
def set_order_fulfillment(order_id: str, status: str) -> dict:
    """Zmienia status realizacji zamówienia.
    status: NEW/PROCESSING/READY_FOR_SHIPMENT/SENT/PICKED_UP/CANCELLED/SUSPENDED."""
    return request("PUT", f"/order/checkout-forms/{order_id}/fulfillment", body={"status": status})


@mcp.tool
def get_order_shipments(order_id: str) -> dict:
    """Przesyłki przypięte do zamówienia."""
    return request("GET", f"/order/checkout-forms/{order_id}/shipments")


# ============================ WIADOMOŚCI ============================

@mcp.tool
def get_threads(limit: int = 20, offset: int = 0) -> dict:
    """Lista wątków wiadomości (Centrum wiadomości)."""
    return request("GET", "/messaging/threads", {"limit": limit, "offset": offset})


@mcp.tool
def get_thread_messages(thread_id: str, limit: int = 20, offset: int = 0) -> dict:
    """Wiadomości w danym wątku."""
    return request("GET", f"/messaging/threads/{thread_id}/messages", {"limit": limit, "offset": offset})


@mcp.tool
def send_message(thread_id: str, text: str) -> dict:
    """Wysyła wiadomość w wątku do kupującego."""
    return request("POST", f"/messaging/threads/{thread_id}/messages", body={"text": text})


# ============================ OCENY / DYSKUSJE / ROZLICZENIA ============================

@mcp.tool
def get_user_ratings(limit: int = 20, offset: int = 0) -> dict:
    """Oceny sprzedawcy wystawione przez kupujących."""
    return request("GET", "/sale/user-ratings", {"limit": limit, "offset": offset})


@mcp.tool
def get_disputes(limit: int = 20, offset: int = 0) -> dict:
    """Lista dyskusji/sporów z kupującymi."""
    return request("GET", "/sale/disputes", {"limit": limit, "offset": offset})


@mcp.tool
def get_billing_entries(limit: int = 20, offset: int = 0) -> dict:
    """Wpisy rozliczeniowe (opłaty, prowizje Allegro)."""
    return request("GET", "/billing/billing-entries", {"limit": limit, "offset": offset})


# ============================ KATEGORIE / PARAMETRY ============================

@mcp.tool
def get_categories(parent_id: str | None = None) -> dict:
    """Drzewo kategorii Allegro. Bez parent_id = kategorie najwyższego poziomu."""
    return request("GET", "/sale/categories", {"parent.id": parent_id})


@mcp.tool
def get_category_parameters(category_id: str) -> dict:
    """Parametry wymagane/dozwolone w danej kategorii (do wystawiania ofert)."""
    return request("GET", f"/sale/categories/{category_id}/parameters")


# ============================ AWARYJNIE ============================

@mcp.tool
def allegro_raw_request(method: str, path: str, params_json: str = "{}", body_json: str = "") -> dict:
    """Dowolny endpoint Allegro API. method=GET/POST/PUT/PATCH/DELETE, path np. '/sale/offers'.
    params_json = JSON query params; body_json = JSON ciała (puste = brak).
    Pełna dokumentacja: https://developer.allegro.pl/documentation/"""
    try:
        params = json.loads(params_json) if params_json else {}
        body = json.loads(body_json) if body_json else None
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON: {e}"}
    return request(method.upper(), path, params or None, body)


if __name__ == "__main__":
    mcp.run()

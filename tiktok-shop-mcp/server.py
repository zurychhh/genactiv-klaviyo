"""TikTok Shop MCP (GENACTIV) — konektor do TikTok Shop Partner/Seller Open API.

Host: https://open-api.tiktokglobalshop.com  (docsy: partner.tiktokshop.com)
To INNE API niż TikTok Ads — osobna aplikacja (app_key/app_secret), autoryzacja OAuth,
podpis HMAC-SHA256 na każdym żądaniu, wersja w ścieżce (np. /product/202309/...).

Podpis (potwierdzony z ref. impl. + dok. „Sign your API request"):
  base   = path + concat(sorted 'klucz'+'wartość', bez sign/access_token/app_secret/token)
           + body_json (jeśli JSON, nie multipart)
  sign   = HMAC_SHA256(app_secret, app_secret + base + app_secret).hexdigest()  # lowercase
  timestamp = Unix SECONDS; access_token w nagłówku x-tts-access-token; shop_cipher jako query param.

Grupy narzędzi:
  - KONTO/AUTORYZACJA: get_authorized_shops, get_token_info
  - KATALOG-REFERENCJE: get_categories, get_category_attributes, get_brands, get_warehouses, get_category_rules
  - PRODUKTY: search_products, get_product, create_product, edit_product, update_price, update_inventory,
              activate_products, deactivate_products, delete_products, upload_product_image
  - UNIWERSALNA FURTKA: tts_get / tts_post / tts_put / tts_delete (dowolny endpoint, poprawny podpis)

Env (.tiktok-shop.env): TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET, TIKTOK_SHOP_ACCESS_TOKEN,
     TIKTOK_SHOP_CIPHER (domyślny sklep). Uruchomienie: fastmcp run server.py
"""
import hashlib
import hmac
import json as _json
import os
import time

import requests
from fastmcp import FastMCP

# Jedno źródło prawdy: .tiktok-shop.env (obok katalogu serwera). Env var nadpisuje plik.
ENV_PATH = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".tiktok-shop.env"))
AUTH_BASE = "https://auth.tiktok-shops.com/api/v2"


def _read_env_file():
    d = {}
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    d[k.strip()] = v.strip()
    return d


def _write_env_file(updates):
    d = _read_env_file()
    d.update(updates)
    with open(ENV_PATH, "w") as f:
        for k, v in d.items():
            f.write(f"{k}={v}\n")
    os.chmod(ENV_PATH, 0o600)


_ENV = _read_env_file()


def _cfg(key, default=""):
    return os.environ.get(key) or _ENV.get(key, default)


APP_KEY = _cfg("TIKTOK_SHOP_APP_KEY")
APP_SECRET = _cfg("TIKTOK_SHOP_APP_SECRET")
ACCESS_TOKEN = _cfg("TIKTOK_SHOP_ACCESS_TOKEN")
REFRESH_TOKEN = _cfg("TIKTOK_SHOP_REFRESH_TOKEN")
SHOP_CIPHER = _cfg("TIKTOK_SHOP_CIPHER")
try:
    ACCESS_EXPIRE = int(_cfg("TIKTOK_SHOP_ACCESS_TOKEN_EXPIRE", "0") or "0")
except ValueError:
    ACCESS_EXPIRE = 0

BASE = "https://open-api.tiktokglobalshop.com"
PVER = "202309"   # wersja API produktów (w ścieżce) — zmiana w jednym miejscu
LVER = "202309"   # logistyka (magazyny)
AVER = "202309"   # authorization (sklepy)
EXCLUDE = {"app_secret", "access_token", "sign", "token"}

mcp = FastMCP("tiktok-shop")


def _sign(path, params, body_str=None):
    keys = sorted(k for k in params if k not in EXCLUDE)
    base = path + "".join(f"{k}{params[k]}" for k in keys)
    if body_str:
        base += body_str
    wrapped = f"{APP_SECRET}{base}{APP_SECRET}"
    return hmac.new(APP_SECRET.encode(), wrapped.encode(), hashlib.sha256).hexdigest()


def _ok(resp):
    try:
        data = resp.json()
    except ValueError:
        return {"status": "ERROR", "http_status": resp.status_code, "error": {"raw": resp.text[:2000]}}
    if resp.status_code >= 400 or (isinstance(data, dict) and data.get("code") not in (0, None)):
        return {"status": "ERROR", "http_status": resp.status_code,
                "code": data.get("code"), "message": data.get("message"),
                "request_id": data.get("request_id"), "error": data.get("data", data)}
    return {"status": "OK", "data": data.get("data", data), "request_id": data.get("request_id")}


def _ensure_token():
    """Auto-odświeżanie access_token, gdy wygasł/zbliża się do wygaśnięcia (bufor 5 min)."""
    global ACCESS_TOKEN, REFRESH_TOKEN, ACCESS_EXPIRE
    if not REFRESH_TOKEN or not ACCESS_EXPIRE:
        return
    if time.time() < ACCESS_EXPIRE - 300:
        return
    r = requests.get(f"{AUTH_BASE}/token/refresh", params={
        "app_key": APP_KEY, "app_secret": APP_SECRET,
        "refresh_token": REFRESH_TOKEN, "grant_type": "refresh_token"}, timeout=60)
    data = r.json()
    if data.get("code") in (0, None) and data.get("data"):
        d = data["data"]
        ACCESS_TOKEN = d.get("access_token", ACCESS_TOKEN)
        REFRESH_TOKEN = d.get("refresh_token", REFRESH_TOKEN)
        ACCESS_EXPIRE = int(d.get("access_token_expire_in", ACCESS_EXPIRE) or ACCESS_EXPIRE)
        _write_env_file({
            "TIKTOK_SHOP_ACCESS_TOKEN": ACCESS_TOKEN,
            "TIKTOK_SHOP_REFRESH_TOKEN": REFRESH_TOKEN,
            "TIKTOK_SHOP_ACCESS_TOKEN_EXPIRE": str(ACCESS_EXPIRE)})


def _request(method, path, query=None, body=None, use_shop_cipher=True, files=None, extra_headers=None):
    """Rdzeń: buduje parametry (app_key, timestamp, shop_cipher), podpisuje, wysyła."""
    _ensure_token()
    params = {"app_key": APP_KEY, "timestamp": int(time.time())}
    if use_shop_cipher and SHOP_CIPHER:
        params["shop_cipher"] = SHOP_CIPHER
    if query:
        params.update({k: v for k, v in query.items() if v is not None})

    body_str = None
    headers = {"x-tts-access-token": ACCESS_TOKEN}
    if files is None:
        headers["content-type"] = "application/json"
        if body is not None:
            body_str = _json.dumps(body, separators=(",", ":"), ensure_ascii=False)
    if extra_headers:
        headers.update(extra_headers)

    params["sign"] = _sign(path, params, body_str)
    url = BASE + path
    if method == "GET":
        r = requests.get(url, params=params, headers=headers, timeout=60)
    elif method == "DELETE":
        r = requests.delete(url, params=params, headers=headers,
                            data=(body_str.encode() if body_str else None), timeout=60)
    elif files is not None:
        r = requests.post(url, params=params, headers=headers, files=files, timeout=180)
    elif method == "PUT":
        r = requests.put(url, params=params, headers=headers, data=body_str.encode(), timeout=120)
    else:
        r = requests.post(url, params=params, headers=headers,
                         data=(body_str.encode() if body_str else b"{}"), timeout=120)
    return _ok(r)


# ───────────────────────── UNIWERSALNA FURTKA ─────────────────────────

@mcp.tool
def tts_get(path: str, query: dict | None = None, use_shop_cipher: bool = True) -> dict:
    """GET dowolnego endpointu TikTok Shop. path np. '/product/202309/categories'. Podpis liczony automatycznie."""
    return _request("GET", path, query=query, use_shop_cipher=use_shop_cipher)


@mcp.tool
def tts_post(path: str, body: dict | None = None, query: dict | None = None, use_shop_cipher: bool = True) -> dict:
    """POST dowolnego endpointu. body → JSON. Podpis (z body) liczony automatycznie."""
    return _request("POST", path, query=query, body=(body or {}), use_shop_cipher=use_shop_cipher)


@mcp.tool
def tts_put(path: str, body: dict | None = None, query: dict | None = None, use_shop_cipher: bool = True) -> dict:
    """PUT dowolnego endpointu (np. edycja produktu /product/202309/products/{id})."""
    return _request("PUT", path, query=query, body=(body or {}), use_shop_cipher=use_shop_cipher)


@mcp.tool
def tts_delete(path: str, body: dict | None = None, query: dict | None = None, use_shop_cipher: bool = True) -> dict:
    """DELETE dowolnego endpointu."""
    return _request("DELETE", path, query=query, body=body, use_shop_cipher=use_shop_cipher)


# ───────────────────────── KONTO / AUTORYZACJA ─────────────────────────

@mcp.tool
def get_authorized_shops() -> dict:
    """Lista sklepów autoryzowanych pod tokenem: id, name, region, cipher, seller_type.
    Z 'cipher' bierze się shop_cipher potrzebny do reszty wywołań (bez shop_cipher w samym tym wywołaniu)."""
    return _request("GET", f"/authorization/{AVER}/shops", use_shop_cipher=False)


@mcp.tool
def get_token_info() -> dict:
    """Diagnostyka konfiguracji serwera: czy są ustawione klucze/token/cipher (nie ujawnia wartości)."""
    return {"status": "OK", "data": {
        "app_key_set": bool(APP_KEY), "app_secret_set": bool(APP_SECRET),
        "access_token_set": bool(ACCESS_TOKEN), "shop_cipher_set": bool(SHOP_CIPHER),
        "product_api_version": PVER, "base": BASE}}


# ───────────────────────── KATALOG — REFERENCJE ─────────────────────────

@mcp.tool
def get_categories(locale: str = "pl-PL", keyword: str | None = None) -> dict:
    """Drzewo kategorii sklepu (do wyboru category_id przy tworzeniu produktu)."""
    q = {"locale": locale}
    if keyword:
        q["keyword"] = keyword
    return _request("GET", f"/product/{PVER}/categories", query=q)


@mcp.tool
def get_category_attributes(category_id: str, locale: str = "pl-PL") -> dict:
    """Atrybuty (wymagane/opcjonalne) danej kategorii — potrzebne do poprawnego create_product."""
    return _request("GET", f"/product/{PVER}/categories/{category_id}/attributes", query={"locale": locale})


@mcp.tool
def get_category_rules(category_id: str) -> dict:
    """Reguły kategorii: czy wymagany brand, certyfikaty, rozmiar/tabela, ograniczenia."""
    return _request("GET", f"/product/{PVER}/categories/{category_id}/rules")


@mcp.tool
def get_brands(category_id: str | None = None, keyword: str | None = None, page_size: int = 100) -> dict:
    """Lista marek (brand_id). Filtr po kategorii/nazwie."""
    q = {"page_size": page_size}
    if category_id:
        q["category_id"] = category_id
    if keyword:
        q["keyword"] = keyword
    return _request("GET", f"/product/{PVER}/brands", query=q)


@mcp.tool
def get_warehouses() -> dict:
    """Magazyny sklepu (warehouse_id) — wymagane w inventory przy tworzeniu produktu."""
    return _request("GET", f"/logistics/{LVER}/warehouses")


# ───────────────────────── PRODUKTY — ODCZYT ─────────────────────────

@mcp.tool
def search_products(status: str | None = None, page_size: int = 50,
                    page_token: str | None = None, seller_sku: str | None = None) -> dict:
    """Lista/wyszukiwanie produktów sklepu. status: DRAFT/PENDING/FAILED/ACTIVATE/SELLER_DEACTIVATED/...
    Zwraca products[] + next_page_token (paginacja)."""
    body = {}
    if status:
        body["status"] = status
    if seller_sku:
        body["seller_skus"] = [seller_sku]
    q = {"page_size": page_size}
    if page_token:
        q["page_token"] = page_token
    return _request("POST", f"/product/{PVER}/products/search", query=q, body=body)


@mcp.tool
def get_product(product_id: str) -> dict:
    """Pełne dane produktu po ID."""
    return _request("GET", f"/product/{PVER}/products/{product_id}")


# ───────────────────────── PRODUKTY — ZAPIS ─────────────────────────

@mcp.tool
def upload_product_image(image_url: str, use_case: str = "MAIN_IMAGE") -> dict:
    """Wgrywa obraz produktu z publicznego URL i zwraca uri (do main_images w create_product).
    use_case: MAIN_IMAGE / ATTRIBUTE_IMAGE / DESCRIPTION_IMAGE / SIZE_CHART_IMAGE / CERTIFICATION_IMAGE."""
    img = requests.get(image_url, timeout=120)
    if img.status_code >= 400:
        return {"status": "ERROR", "message": f"Nie pobrano obrazu ({img.status_code})", "url": image_url}
    files = {"data": ("image.jpg", img.content)}
    return _request("POST", f"/product/{PVER}/images/upload", query={"use_case": use_case},
                    files=files, use_shop_cipher=False)


@mcp.tool
def create_product(product_body: dict) -> dict:
    """Tworzy produkt. product_body to gotowy obiekt wg schematu TikTok Shop, m.in.:
      title, description (HTML), category_id, brand_id?, main_images:[{uri}],
      package_weight:{value,unit}, package_dimensions:{length,width,height,unit},
      skus:[{sales_attributes:[...], seller_sku, price:{amount,currency}, inventory:[{warehouse_id,quantity}]}].
    Najpierw wgraj zdjęcia (upload_product_image) i pobierz atrybuty (get_category_attributes)."""
    return _request("POST", f"/product/{PVER}/products", body=product_body)


@mcp.tool
def edit_product(product_id: str, product_body: dict) -> dict:
    """Edycja istniejącego produktu (pełny obiekt jak w create_product). PUT /products/{id}."""
    return _request("PUT", f"/product/{PVER}/products/{product_id}", body=product_body)


@mcp.tool
def update_price(product_id: str, skus: list) -> dict:
    """Aktualizacja cen wariantów bez ruszania reszty. skus:[{id, price:{amount,currency}}]."""
    return _request("POST", f"/product/{PVER}/products/{product_id}/prices/update", body={"skus": skus})


@mcp.tool
def update_inventory(product_id: str, skus: list) -> dict:
    """Aktualizacja stanów magazynowych. skus:[{id, inventory:[{warehouse_id, quantity}]}]."""
    return _request("POST", f"/product/{PVER}/products/{product_id}/inventory/update", body={"skus": skus})


@mcp.tool
def activate_products(product_ids: list) -> dict:
    """Publikuje/aktywuje produkty (lista ID)."""
    return _request("POST", f"/product/{PVER}/products/activate", body={"product_ids": product_ids})


@mcp.tool
def deactivate_products(product_ids: list) -> dict:
    """Wycofuje produkty ze sprzedaży (lista ID)."""
    return _request("POST", f"/product/{PVER}/products/deactivate", body={"product_ids": product_ids})


@mcp.tool
def delete_products(product_ids: list) -> dict:
    """Usuwa produkty (lista ID). DELETE /products."""
    return _request("DELETE", f"/product/{PVER}/products", body={"product_ids": product_ids})


if __name__ == "__main__":
    mcp.run()

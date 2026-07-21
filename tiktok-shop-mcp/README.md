# TikTok Shop MCP (GenActiv)

Serwer MCP do **TikTok Shop Partner/Seller Open API** — tworzenie i edycja produktów w sklepie
TikTok Shop GENACTIV (region PL). To **inne API niż TikTok Ads** — osobna aplikacja, osobna
autoryzacja, podpis HMAC-SHA256 na każdym żądaniu.

- **Host API:** `https://open-api.tiktokglobalshop.com`
- **Host autoryzacji:** `https://auth.tiktok-shops.com/api/v2`
- **Wersja endpointów:** `202309` (stałe `PVER`/`LVER`/`AVER` w `server.py`)
- **Docsy:** https://partner.tiktokshop.com

## Pliki

| Plik | Rola |
|---|---|
| `server.py` | Serwer FastMCP `tiktok-shop` (20 narzędzi). Sam czyta klucze z `../.tiktok-shop.env` i auto-odświeża access_token. |
| `generate_tiktok_shop_token.py` | Autoryzacja OAuth: `url` → `code <CODE>` → (auto) `shop_cipher`; oraz `refresh`. |
| `../.tiktok-shop.env` | **Sekrety — NIE w repo** (`.gitignore`, chmod 600). Wzór: `.tiktok-shop.env.example`. |

## Konfiguracja (nowa maszyna)

1. Skopiuj wzór i uzupełnij `app_key` + `app_secret` (z TikTok Shop Partner Center → strona aplikacji):
   ```bash
   cp .tiktok-shop.env.example .tiktok-shop.env
   chmod 600 .tiktok-shop.env
   # uzupełnij TIKTOK_SHOP_APP_KEY, TIKTOK_SHOP_APP_SECRET, TIKTOK_SHOP_SERVICE_ID
   ```
2. Autoryzuj sklep (uzyskanie access_token + refresh_token + shop_cipher):
   ```bash
   source venv/bin/activate
   python3 tiktok-shop-mcp/generate_tiktok_shop_token.py url        # wypisze link
   # otwórz link na koncie sprzedawcy → Autoryzuj → skopiuj ?code= z paska adresu
   python3 tiktok-shop-mcp/generate_tiktok_shop_token.py code <CODE> # zapisze token + shop_cipher
   ```
3. Wpis MCP (Claude Code `.claude.json` / Desktop `claude_desktop_config.json`):
   ```json
   "tiktok-shop": {
     "type": "stdio",
     "command": "/ABS/PATH/genactiv-klaviyo-main/venv/bin/fastmcp",
     "args": ["run", "/ABS/PATH/genactiv-klaviyo-main/tiktok-shop-mcp/server.py"]
   }
   ```
   Sekretów w configu nie trzeba — serwer bierze je z `.tiktok-shop.env`.
   **Po zmianie configu zrestartuj Claude Code/Desktop** (połączenia MCP cache'owane przy starcie).

## Narzędzia

- **Konto/furtka:** `get_authorized_shops`, `get_token_info`, `tts_get`/`tts_post`/`tts_put`/`tts_delete`
- **Referencje katalogu:** `get_categories`, `get_category_attributes`, `get_category_rules`, `get_brands`, `get_warehouses`
- **Produkty (odczyt):** `search_products`, `get_product`
- **Produkty (zapis):** `create_product`, `edit_product`, `update_price`, `update_inventory`,
  `activate_products`, `deactivate_products`, `delete_products`, `upload_product_image`

## Podpis żądania (HMAC-SHA256)

Odwzorowany z ref. impl. i dok. „Sign your API request":

```
base = path + concat(sorted 'klucz'+'wartość', z pominięciem sign/access_token/app_secret/token)
       + body_json (tylko dla JSON — nie dla multipart)
sign = HMAC_SHA256(app_secret, app_secret + base + app_secret).hexdigest()   # hex lowercase
```

- `timestamp` w **sekundach** Unix; access_token w nagłówku `x-tts-access-token`; `shop_cipher` jako query param.
- **Body podpisywane bajt-w-bajt tak, jak wysyłane** (kompaktowy JSON, `ensure_ascii=False`).

## Gotchy (z wdrożenia 21.07.2026)

- Link autoryzacyjny **musi mieć `service_id`**, nie `app_key` — z `app_key` wraca bez `code`.
- Redirect URI **bez spacji/entera na końcu** — spacja (`%20`) → brak `code` w powrocie.
- Niedokończona autoryzacja blokuje kolejną („tej usługi nie można odnowić") — dokończyć lub wyczyścić w Seller Center.
- `auth_code` jest krótko ważny — wymieniać na token **od razu**.
- Uprawnienia (scopes) dodaje się w Partner Center w **„Zarządzaj interfejsem API usługi"** (brak → błąd „LocalServiceList is empty"). Do produktów: `seller.product.*` + `seller.global_product.*`.
- Wersje endpointów **zapisu** (202309) potwierdzić przy pierwszym użyciu — mogą różnić się od odczytu.

## Stan sklepu (żywe dane 21.07.2026)

- Sklep **GENACTIV**, region PL, typ LOCAL.
- Magazyn sprzedażowy do `inventory`: `warehouse_id = 7647115186386994966` (GENACTIV Dąbrówka).
- W katalogu jest już **67 produktów** — przy masowym tworzeniu uważać na dublowanie.

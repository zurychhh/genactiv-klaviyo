"""Baselinker MCP server — wrapper na Baselinker API (connector.php).

Wystawia najważniejsze metody Baselinkera jako narzędzia MCP:
zamówienia, płatności, statusy, magazyny i stany produktów.

Token: zmienna środowiskowa BASELINKER_TOKEN (nagłówek X-BLToken).
Uruchomienie: fastmcp run server.py  (lub przez Claude Desktop / .mcp.json)
"""
import os
import json
import urllib.parse
import urllib.request

from fastmcp import FastMCP

API_URL = "https://api.baselinker.com/connector.php"
TOKEN = os.environ.get("BASELINKER_TOKEN", "")

mcp = FastMCP("baselinker")


def call_api(method: str, parameters: dict | None = None) -> dict:
    """Wywołuje metodę Baselinker API i zwraca odpowiedź jako dict."""
    if not TOKEN:
        return {"status": "ERROR", "error_message": "Brak BASELINKER_TOKEN w środowisku"}
    payload = {"method": method, "parameters": json.dumps(parameters or {}, ensure_ascii=False)}
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(API_URL, data=data, headers={"X-BLToken": TOKEN})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:  # noqa: BLE001 — błąd zwracamy do modelu, nie wywalamy serwera
        return {"status": "ERROR", "error_message": f"{type(e).__name__}: {e}"}


@mcp.tool
def get_order_sources() -> dict:
    """Lista źródeł zamówień (sklepy, Allegro, osobiste itd.)."""
    return call_api("getOrderSources")


@mcp.tool
def get_order_status_list() -> dict:
    """Lista statusów zamówień skonfigurowanych na koncie."""
    return call_api("getOrderStatusList")


@mcp.tool
def get_orders(
    date_from: int | None = None,
    order_id: int | None = None,
    status_id: int | None = None,
    get_unconfirmed_orders: bool = False,
    filter_email: str | None = None,
) -> dict:
    """Pobiera zamówienia (max 100 na stronę, od date_from jako unix timestamp).

    Aby stronicować: użyj największego order_id z poprzedniej odpowiedzi + 1.
    """
    params: dict = {"get_unconfirmed_orders": get_unconfirmed_orders}
    if date_from is not None:
        params["date_confirmed_from"] = date_from
    if order_id is not None:
        params["order_id"] = order_id
    if status_id is not None:
        params["status_id"] = status_id
    if filter_email:
        params["filter_email"] = filter_email
    return call_api("getOrders", params)


@mcp.tool
def get_order_payments_history(order_id: int, show_full_history: bool = True) -> dict:
    """Historia płatności dla danego zamówienia."""
    return call_api(
        "getOrderPaymentsHistory",
        {"order_id": order_id, "show_full_history": show_full_history},
    )


@mcp.tool
def get_journal_list(last_log_id: int = 0, logs_types: list[int] | None = None) -> dict:
    """Dziennik zdarzeń zamówień (zmiany statusów, nowe zamówienia) od last_log_id."""
    params: dict = {"last_log_id": last_log_id}
    if logs_types:
        params["logs_types"] = logs_types
    return call_api("getJournalList", params)


@mcp.tool
def get_inventories() -> dict:
    """Lista katalogów/magazynów (inventories) w Baselinker."""
    return call_api("getInventories")


@mcp.tool
def get_inventory_products_list(
    inventory_id: int,
    filter_name: str | None = None,
    filter_sku: str | None = None,
    page: int = 1,
) -> dict:
    """Lista produktów w danym katalogu (inventory_id z get_inventories)."""
    params: dict = {"inventory_id": inventory_id, "page": page}
    if filter_name:
        params["filter_name"] = filter_name
    if filter_sku:
        params["filter_sku"] = filter_sku
    return call_api("getInventoryProductsList", params)


@mcp.tool
def get_inventory_products_stock(inventory_id: int, page: int = 1) -> dict:
    """Stany magazynowe produktów w danym katalogu."""
    return call_api("getInventoryProductsStock", {"inventory_id": inventory_id, "page": page})


@mcp.tool
def get_inventory_products_data(inventory_id: int, product_ids_json: str) -> dict:
    """Pełne dane kart produktowych (nazwy, opisy, parametry, zdjęcia, ceny, stany)
    dla podanych ID. product_ids_json = JSON listy, np. '[12345, 12346]'.
    """
    try:
        ids = json.loads(product_ids_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w product_ids_json: {e}"}
    return call_api("getInventoryProductsData", {"inventory_id": inventory_id, "products": ids})


@mcp.tool
def get_inventory_text_field_keys(inventory_id: int) -> dict:
    """Dostępne klucze pól tekstowych — w tym per-kanał do synchronizacji opisów,
    np. 'description|pl|allegro_16310', 'name|pl|shop_2007999'. Użyj ich w set_product_text_fields.
    """
    return call_api("getInventoryAvailableTextFieldKeys", {"inventory_id": inventory_id})


@mcp.tool
def get_inventory_integrations(inventory_id: int) -> dict:
    """Integracje katalogu (kanały sprzedaży): Shopify (shop), Allegro itd. + ich ID kont.
    ID kont są potrzebne do pól per-kanał typu 'description|pl|shop_<id>' / '...|allegro_<id>'.
    """
    return call_api("getInventoryIntegrations", {"inventory_id": inventory_id})


@mcp.tool
def get_inventory_price_groups() -> dict:
    """Grupy cenowe (price_group_id) — potrzebne do update_inventory_products_prices."""
    return call_api("getInventoryPriceGroups")


@mcp.tool
def get_inventory_warehouses() -> dict:
    """Magazyny (warehouse_id) — w stanach używaj formatu 'bl_<warehouse_id>'."""
    return call_api("getInventoryWarehouses")


@mcp.tool
def get_inventory_categories(inventory_id: int) -> dict:
    """Kategorie produktów w katalogu."""
    return call_api("getInventoryCategories", {"inventory_id": inventory_id})


# ============================ ZAPIS / EDYCJA ============================

@mcp.tool
def set_order_status(order_id: int, status_id: int) -> dict:
    """Zmienia status zamówienia. status_id pobierz z get_order_status_list."""
    return call_api("setOrderStatus", {"order_id": order_id, "status_id": status_id})


@mcp.tool
def set_order_statuses(order_ids: list[int], status_id: int) -> dict:
    """Zmienia status wielu zamówień naraz (hurtowo)."""
    return call_api("setOrderStatuses", {"order_ids": order_ids, "status_id": status_id})


@mcp.tool
def add_order_payment(
    order_id: int,
    payment_done: float,
    payment_comment: str = "",
    external_payment_id: str = "",
) -> dict:
    """Dopisuje płatność do zamówienia. payment_done = kwota (dodatnia=wpłata, ujemna=zwrot)."""
    params: dict = {"order_id": order_id, "payment_done": payment_done}
    if payment_comment:
        params["payment_comment"] = payment_comment
    if external_payment_id:
        params["external_payment_id"] = external_payment_id
    return call_api("addOrderPaymentReceived", params)


@mcp.tool
def set_order_fields(order_id: int, fields_json: str) -> dict:
    """Edytuje pola zamówienia. fields_json = JSON, np.
    '{"admin_comment":"sprawdzone","email":"x@y.pl","phone":"600..."}'.
    Dozwolone pola m.in.: admin_comment, user_comment, email, phone,
    delivery_fullname, delivery_address, delivery_city, delivery_postcode,
    invoice_fullname, invoice_nip, delivery_method, delivery_price.
    """
    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w fields_json: {e}"}
    fields["order_id"] = order_id
    return call_api("setOrderFields", fields)


@mcp.tool
def add_inventory_product(inventory_id: int, product_json: str) -> dict:
    """Dodaje lub aktualizuje produkt w katalogu. product_json = JSON z polami produktu
    (np. product_id do aktualizacji, sku, ean, text_fields, prices, stock, tax_rate, weight).
    Bez product_id tworzy nowy produkt; z product_id aktualizuje istniejący.
    """
    try:
        product = json.loads(product_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w product_json: {e}"}
    product["inventory_id"] = inventory_id
    return call_api("addInventoryProduct", product)


@mcp.tool
def set_product_text_fields(inventory_id: int, product_id: int, text_fields_json: str) -> dict:
    """Edytuje nazwy/opisy/parametry karty produktu — także per-kanał (sync do Shopify/Allegro).
    text_fields_json = JSON mapy klucz->wartość. Klucze z get_inventory_text_field_keys, np.:
    '{"name":"Nowa nazwa","description":"<p>opis PL</p>","features":{"Marka":"GenActiv"}}'
    Sync opisu tylko na Allegro: '{"description|pl|allegro_16310":"<p>opis allegro</p>"}'
    Sync nazwy tylko na Shopify genactiv: '{"name|pl|shop_2007999":"Nazwa na Shopify"}'
    Puste pole per-kanał = dziedziczy z głównego opisu.
    """
    try:
        text_fields = json.loads(text_fields_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w text_fields_json: {e}"}
    return call_api(
        "addInventoryProduct",
        {"inventory_id": inventory_id, "product_id": product_id, "text_fields": text_fields},
    )


@mcp.tool
def delete_inventory_product(inventory_id: int, product_id: int) -> dict:
    """Usuwa produkt z katalogu. UWAGA: operacja nieodwracalna."""
    return call_api("deleteInventoryProduct", {"inventory_id": inventory_id, "product_id": product_id})


@mcp.tool
def add_inventory_category(inventory_id: int, name: str, parent_id: int = 0) -> dict:
    """Dodaje kategorię produktów (parent_id=0 = poziom główny)."""
    return call_api(
        "addInventoryCategory",
        {"inventory_id": inventory_id, "name": name, "parent_id": parent_id},
    )


@mcp.tool
def update_inventory_products_stock(inventory_id: int, products_json: str) -> dict:
    """Aktualizuje stany magazynowe. products_json = JSON mapy
    {"product_id": {"bl_<warehouse_id>": stock}}, np. '{"12345": {"bl_8220": 50}}'.
    warehouse_id pobierz z get_inventory_warehouses (np. 8220 = B2C).
    """
    try:
        products = json.loads(products_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w products_json: {e}"}
    return call_api("updateInventoryProductsStock", {"inventory_id": inventory_id, "products": products})


@mcp.tool
def update_inventory_products_prices(inventory_id: int, products_json: str) -> dict:
    """Aktualizuje ceny. products_json = JSON mapy
    {"product_id": {"price_group_id": price}}, np. '{"12345": {"3553": 79.99}}'.
    price_group_id pobierz z get_inventory_price_groups (3553 = Domyślna).
    """
    try:
        products = json.loads(products_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w products_json: {e}"}
    return call_api("updateInventoryProductsPrices", {"inventory_id": inventory_id, "products": products})


# ============================ ZDJĘCIA PRODUKTÓW ============================

def _get_product_images(inventory_id: int, product_id: int) -> dict:
    """Pomocnik: zwraca bieżącą mapę zdjęć produktu {pozycja: url} lub {}."""
    data = call_api("getInventoryProductsData", {"inventory_id": inventory_id, "products": [product_id]})
    if data.get("status") != "SUCCESS":
        return {}
    pd = data.get("products", {}).get(str(product_id), {})
    imgs = pd.get("images") or {}
    return {str(k): v for k, v in imgs.items()}


@mcp.tool
def get_product_images(inventory_id: int, product_id: int) -> dict:
    """Zwraca galerię zdjęć produktu jako mapę {pozycja: URL} (pozycje 0–15)."""
    return {"status": "SUCCESS", "images": _get_product_images(inventory_id, product_id)}


@mcp.tool
def set_product_images(inventory_id: int, product_id: int, images_json: str) -> dict:
    """USTAWIA CAŁĄ galerię zdjęć (nadpisuje istniejącą). images_json = JSON mapy
    {"pozycja": "URL lub data:image/...;base64,..."}, pozycje 0–15, np.
    '{"0":"https://.../front.jpg","1":"https://.../back.jpg"}'.
    Pozycja 0 = zdjęcie główne. Pominięte pozycje zostaną usunięte z galerii.
    Aby tylko dodać/usunąć pojedyncze zdjęcie, użyj add_product_image_url / delete_product_image.
    """
    try:
        images = json.loads(images_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w images_json: {e}"}
    images = {str(k): v for k, v in images.items()}
    return call_api(
        "addInventoryProduct",
        {"inventory_id": inventory_id, "product_id": product_id, "images": images},
    )


@mcp.tool
def add_product_image_url(inventory_id: int, product_id: int, image_url: str, position: int | None = None) -> dict:
    """Dodaje JEDNO zdjęcie z URL, zachowując pozostałe (read-modify-write).
    position 0–15 — jeśli pominięte, wstawia na pierwszą wolną pozycję. position 0 = główne.
    """
    images = _get_product_images(inventory_id, product_id)
    if position is None:
        slot = next((i for i in range(16) if str(i) not in images), None)
        if slot is None:
            return {"status": "ERROR", "error_message": "Galeria pełna (16/16). Zwolnij pozycję."}
        position = slot
    images[str(position)] = image_url
    return call_api(
        "addInventoryProduct",
        {"inventory_id": inventory_id, "product_id": product_id, "images": images},
    )


@mcp.tool
def delete_product_image(inventory_id: int, product_id: int, position: int) -> dict:
    """Usuwa jedno zdjęcie z danej pozycji (0–15), zachowując pozostałe."""
    images = _get_product_images(inventory_id, product_id)
    if str(position) not in images:
        return {"status": "ERROR", "error_message": f"Brak zdjęcia na pozycji {position}."}
    images[str(position)] = ""  # pusty string = usunięcie pozycji w Baselinker
    return call_api(
        "addInventoryProduct",
        {"inventory_id": inventory_id, "product_id": product_id, "images": images},
    )


@mcp.tool
def add_order_invoice(order_id: int, series_id: int | None = None) -> dict:
    """Wystawia fakturę do zamówienia. series_id — opcjonalna seria numeracji."""
    params: dict = {"order_id": order_id}
    if series_id is not None:
        params["series_id"] = series_id
    return call_api("addOrderInvoice", params)


# ============================ KURIERZY / PRZESYŁKI ============================

@mcp.tool
def get_couriers_list() -> dict:
    """Lista dostępnych kurierów (code + nazwa). code użyjesz w pozostałych metodach kurierskich."""
    return call_api("getCouriersList")


@mcp.tool
def get_courier_accounts(courier_code: str) -> dict:
    """Konta danego kuriera podłączone w Baselinker (account_id do create_package)."""
    return call_api("getCourierAccounts", {"courier_code": courier_code})


@mcp.tool
def get_courier_fields(courier_code: str) -> dict:
    """Pola wymagane/opcjonalne do nadania przesyłki danym kurierem
    (struktura formularza: pola, opcje, wartości domyślne)."""
    return call_api("getCourierFields", {"courier_code": courier_code})


@mcp.tool
def get_courier_services(courier_code: str, account_id: int, fields_json: str = "[]", packages_json: str = "[]") -> dict:
    """Dostępne usługi kuriera dla konkretnej przesyłki (gdy kurier wymaga wyboru usługi).
    fields_json/packages_json jak w create_package."""
    try:
        fields = json.loads(fields_json)
        packages = json.loads(packages_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON: {e}"}
    return call_api("getCourierServices", {
        "courier_code": courier_code, "account_id": account_id,
        "fields": fields, "packages": packages,
    })


@mcp.tool
def create_package(order_id: int, courier_code: str, fields_json: str, packages_json: str, account_id: int | None = None) -> dict:
    """Tworzy przesyłkę kurierską dla zamówienia (generuje etykietę u kuriera).
    fields_json = JSON listy pól, np. '[{"id":"package_type","value":"PACKAGE"}]'
      (dostępne pola: get_courier_fields).
    packages_json = JSON listy paczek, np. '[{"weight":1.5,"width":20,"height":10,"length":30}]'.
    account_id z get_courier_accounts (jeśli kurier ma kilka kont).
    """
    try:
        fields = json.loads(fields_json)
        packages = json.loads(packages_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON: {e}"}
    params: dict = {"order_id": order_id, "courier_code": courier_code, "fields": fields, "packages": packages}
    if account_id is not None:
        params["account_id"] = account_id
    return call_api("createPackage", params)


@mcp.tool
def create_package_manual(order_id: int, courier_code: str, package_number: str, fields_json: str = "[]") -> dict:
    """Dopisuje przesyłkę z własnym numerem listu przewozowego (bez generowania etykiety).
    Użyj, gdy etykietę zrobiłeś poza Baselinkerem. package_number = numer trackingu.
    """
    try:
        fields = json.loads(fields_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON w fields_json: {e}"}
    return call_api("createPackageManual", {
        "order_id": order_id, "courier_code": courier_code,
        "package_number": package_number, "fields": fields,
    })


@mcp.tool
def get_order_packages(order_id: int) -> dict:
    """Lista przesyłek przypiętych do zamówienia (package_id, numery, kurier)."""
    return call_api("getOrderPackages", {"order_id": order_id})


@mcp.tool
def get_courier_packages_status_history(package_ids_json: str) -> dict:
    """Historia statusów śledzenia przesyłek. package_ids_json = JSON listy, np. '[123,124]'."""
    try:
        ids = json.loads(package_ids_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON: {e}"}
    return call_api("getCourierPackagesStatusHistory", {"package_ids": ids})


@mcp.tool
def get_label(courier_code: str, package_id: int | None = None, package_number: str | None = None) -> dict:
    """Pobiera etykietę przewozową (zwraca dane w base64 + rozszerzenie, np. PDF).
    Podaj package_id (z get_order_packages) lub package_number.
    """
    params: dict = {"courier_code": courier_code}
    if package_id is not None:
        params["package_id"] = package_id
    if package_number is not None:
        params["package_number"] = package_number
    return call_api("getLabel", params)


@mcp.tool
def delete_courier_package(courier_code: str, package_id: int, force_delete: bool = False) -> dict:
    """Usuwa/anuluje przesyłkę u kuriera. force_delete=True wymusza usunięcie z Baselinkera
    nawet gdy anulowanie u kuriera się nie powiodło."""
    return call_api("deleteCourierPackage", {
        "courier_code": courier_code, "package_id": package_id, "force_delete": force_delete,
    })


@mcp.tool
def baselinker_raw_call(method: str, parameters_json: str = "{}") -> dict:
    """Awaryjne: dowolna metoda Baselinker API. parameters_json = JSON ze stringa.

    Użyj gdy potrzebna metoda nie ma dedykowanego narzędzia powyżej.
    Pełna lista metod: https://api.baselinker.com/
    """
    try:
        params = json.loads(parameters_json)
    except json.JSONDecodeError as e:
        return {"status": "ERROR", "error_message": f"Niepoprawny JSON: {e}"}
    return call_api(method, params)


if __name__ == "__main__":
    mcp.run()

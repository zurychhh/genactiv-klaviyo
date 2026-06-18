"""Klaviyo Segments MCP server — uzupelnia luke oficjalnego klaviyo-mcp-server.

Oficjalny klaviyo-mcp-server (uvx, v0.4.0) NIE ma tworzenia/edycji segmentow,
nawet przy READ_ONLY=false. Ten serwer dokłada brakujące operacje zapisu na
Segments API (POST/PATCH/DELETE /api/segments) + builder warunkow RFM.

Auth: zmienna srodowiskowa KLAVIYO_API_KEY (klucz PRYWATNY pk_..., scope
segments:write). Naglowek: Authorization: Klaviyo-API-Key <key>.
Rewizja API: 2026-01-15. Limity Create Segment: 1/s, 15/min, 100/dzien.

Uruchomienie: fastmcp run server.py  (lub przez Claude Desktop / .mcp.json)

------------------------------------------------------------------------------
SCHEMAT definition.condition_groups (zweryfikowany na zywym koncie GENACTIV):

  definition = { "condition_groups": [ <group>, <group>, ... ] }
  group      = { "conditions": [ <condition>, ... ] }

  LOGIKA:  conditions W grupie  -> OR
           osobne condition_groups -> AND

  condition (profile-metric):
  {
    "type": "profile-metric",
    "metric_id": "R6aTMS",                  # Placed Order (Shopify)
    "measurement": "count" | "sum",         # count=czestotliwosc, sum=suma $value
    "measurement_filter": {
        "type": "numeric",
        "operator": "greater-than" | "greater-than-or-equal" | "equals",
        "value": <number>
    },
    "timeframe_filter":
        {"type":"date","operator":"in-the-last","unit":"day","quantity":N}  # recency
      | {"type":"date","operator":"before"|"after","date":"2026-04-01T00:00:00+00:00"}
      | null,                               # null = bez ograniczenia czasu (all-time)
    "metric_filters": [                     # opcjonalne: filtr po produkcie/kolekcji
        {"property":"Collections","filter":{"type":"list","operator":"contains-any","value":["Colostrum"]}}
    ]
  }
------------------------------------------------------------------------------
"""
import json
import os
import urllib.error
import urllib.request

from fastmcp import FastMCP

API = "https://a.klaviyo.com/api"
REVISION = "2026-01-15"
PLACED_ORDER_METRIC_ID = "R6aTMS"  # Placed Order (Shopify) — domyslna metryka RFM
# Klucz prywatny pk_...; fallback na PRIVATE_API_KEY (konwencja oficjalnego serwera).
API_KEY = os.environ.get("KLAVIYO_API_KEY", "") or os.environ.get("PRIVATE_API_KEY", "")

mcp = FastMCP("klaviyo-segments")


def request(method: str, path: str, body: dict | None = None, params: dict | None = None) -> dict:
    """Request do Klaviyo API. Zwraca dict (parsed JSON) lub {status: ERROR, ...}."""
    if not API_KEY:
        return {"status": "ERROR", "error_message": "Brak KLAVIYO_API_KEY (klucz prywatny pk_) w srodowisku."}
    url = API + path
    if params:
        import urllib.parse
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    headers = {
        "Authorization": f"Klaviyo-API-Key {API_KEY}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/vnd.api+json"
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {"status": "SUCCESS", "http_status": r.status}
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:1500]
        try:
            detail = json.loads(detail)
        except Exception:
            pass
        return {"status": "ERROR", "http_status": e.code, "error": detail}
    except Exception as e:  # noqa: BLE001 — blad zwracamy do modelu, nie wywalamy serwera
        return {"status": "ERROR", "error_message": f"{type(e).__name__}: {e}"}


# ============================ HELPERY (builder warunkow) ============================
# Nie sa toolami MCP — uzywane wewnetrznie przez create_rfm_segment.

def _metric_condition(measurement: str, operator: str, value, timeframe: dict | None,
                      metric_id: str = PLACED_ORDER_METRIC_ID) -> dict:
    """Pojedynczy warunek profile-metric."""
    return {
        "type": "profile-metric",
        "metric_id": metric_id,
        "measurement": measurement,
        "measurement_filter": {"type": "numeric", "operator": operator, "value": value},
        "timeframe_filter": timeframe,
    }


def _tf_in_last(days: int) -> dict:
    return {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": days}


def build_rfm_condition_groups(
    ordered_within_days: int | None = None,
    not_ordered_within_days: int | None = None,
    min_orders: int | None = None,
    order_counts_any: list[int] | None = None,
    min_total_value: float | None = None,
    ever_purchased: bool = False,
    metric_id: str = PLACED_ORDER_METRIC_ID,
) -> list[dict]:
    """Sklada condition_groups dla segmentu RFM. Kazdy parametr = osobna grupa (AND).

    - ordered_within_days: kupil w ostatnich N dni  (count >= 1 in-the-last N day)  [Recency: aktywny]
    - not_ordered_within_days: NIE kupil w ostatnich N dni  (count == 0 in-the-last N day)  [Recency: usypia]
    - min_orders: min. liczba zamowien all-time  (count >= N, timeframe null)  [Frequency]
    - order_counts_any: dokladna liczba zamowien, OR w jednej grupie, np. [1,2]  [Frequency: pasmo]
    - min_total_value: min. suma wartosci zamowien all-time  (sum >= X, timeframe null)  [Monetary]
    - ever_purchased: dodaje grupe "kupil kiedykolwiek" (count >= 1, timeframe null) — by wykluczyc nigdy-nie-kupujacych
    """
    groups: list[dict] = []
    if ordered_within_days is not None:
        groups.append({"conditions": [
            _metric_condition("count", "greater-than-or-equal", 1, _tf_in_last(ordered_within_days), metric_id)
        ]})
    if not_ordered_within_days is not None:
        groups.append({"conditions": [
            _metric_condition("count", "equals", 0, _tf_in_last(not_ordered_within_days), metric_id)
        ]})
    if min_orders is not None:
        groups.append({"conditions": [
            _metric_condition("count", "greater-than-or-equal", min_orders, None, metric_id)
        ]})
    if order_counts_any:
        groups.append({"conditions": [
            _metric_condition("count", "equals", c, None, metric_id) for c in order_counts_any
        ]})
    if min_total_value is not None:
        groups.append({"conditions": [
            _metric_condition("sum", "greater-than-or-equal", min_total_value, None, metric_id)
        ]})
    if ever_purchased:
        groups.append({"conditions": [
            _metric_condition("count", "greater-than-or-equal", 1, None, metric_id)
        ]})
    return groups


# ============================ TOOLE: ODCZYT ============================

@mcp.tool
def list_segments() -> dict:
    """Lista segmentow konta (id, nazwa, definicja, daty)."""
    return request("GET", "/segments", params={
        "fields[segment]": "name,definition,definition.condition_groups,created,updated,is_active,is_processing"
    })


@mcp.tool
def get_segment(segment_id: str, with_profile_count: bool = True) -> dict:
    """Pelne dane segmentu. with_profile_count=True dolacza aktualna liczebnosc (baseline)."""
    params = {"fields[segment]": "name,definition,definition.condition_groups,created,updated,is_active,is_processing"}
    if with_profile_count:
        params["additional-fields[segment]"] = "profile_count"
    return request("GET", f"/segments/{segment_id}", params=params)


# ============================ TOOLE: ZAPIS ============================

@mcp.tool
def create_segment(name: str, condition_groups: list[dict], is_starred: bool = False) -> dict:
    """Tworzy segment z podanej listy condition_groups (pelna kontrola nad schematem).

    condition_groups: lista grup wg schematu w naglowku pliku.
    PAMIETAJ: conditions w grupie -> OR, osobne grupy -> AND.
    Zwraca obiekt segmentu z 'id' (lub {status: ERROR, error: ...} przy bledzie walidacji).
    """
    body = {"data": {"type": "segment", "attributes": {
        "name": name,
        "definition": {"condition_groups": condition_groups},
        "is_starred": is_starred,
    }}}
    return request("POST", "/segments", body=body)


@mcp.tool
def create_rfm_segment(
    name: str,
    ordered_within_days: int | None = None,
    not_ordered_within_days: int | None = None,
    min_orders: int | None = None,
    order_counts_any: list[int] | None = None,
    min_total_value: float | None = None,
    ever_purchased: bool = False,
    metric_id: str = PLACED_ORDER_METRIC_ID,
    is_starred: bool = False,
) -> dict:
    """Tworzy segment RFM na metryce Placed Order (domyslnie R6aTMS). Wygodny wrapper.

    Parametry (kazdy ustawiony = osobna grupa = AND; szczegoly w build_rfm_condition_groups):
      ordered_within_days     -> Recency: kupil w ostatnich N dni
      not_ordered_within_days -> Recency: NIE kupil w ostatnich N dni
      min_orders              -> Frequency: >= N zamowien (all-time)
      order_counts_any        -> Frequency: dokladnie jedna z wartosci, np. [1,2] (OR)
      min_total_value         -> Monetary: suma wartosci zamowien >= X (all-time)
      ever_purchased          -> wymusza "kupil kiedykolwiek" (wyklucza nigdy-nie-kupujacych)

    Przyklad (Champions): create_rfm_segment("RFM | Champions", ordered_within_days=60,
             min_orders=3, min_total_value=400).
    """
    groups = build_rfm_condition_groups(
        ordered_within_days, not_ordered_within_days, min_orders,
        order_counts_any, min_total_value, ever_purchased, metric_id,
    )
    if not groups:
        return {"status": "ERROR", "error_message": "Podaj co najmniej jeden warunek RFM."}
    return create_segment(name, groups, is_starred)


@mcp.tool
def update_segment(segment_id: str, name: str | None = None,
                   condition_groups: list[dict] | None = None) -> dict:
    """Aktualizuje nazwe i/lub definicje segmentu (PATCH)."""
    attributes: dict = {}
    if name is not None:
        attributes["name"] = name
    if condition_groups is not None:
        attributes["definition"] = {"condition_groups": condition_groups}
    if not attributes:
        return {"status": "ERROR", "error_message": "Nic do aktualizacji (podaj name lub condition_groups)."}
    body = {"data": {"type": "segment", "id": segment_id, "attributes": attributes}}
    return request("PATCH", f"/segments/{segment_id}", body=body)


@mcp.tool
def delete_segment(segment_id: str) -> dict:
    """Usuwa segment. Operacja nieodwracalna."""
    return request("DELETE", f"/segments/{segment_id}")


if __name__ == "__main__":
    mcp.run()

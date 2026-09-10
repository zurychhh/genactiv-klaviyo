"""Wspolna biblioteka do pracy z Klaviyo API dla projektu person LP.

Klucz czytany z .mcp.json (nie jest w repo). Rewizja API: 2026-01-15.
Limity Klaviyo: create segment 1/s, 15/min, 100/dzien -> pacing w create_segment().
"""
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://a.klaviyo.com/api"
REVISION = "2026-01-15"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def api_key() -> str:
    key = os.environ.get("KLAVIYO_API_KEY", "")
    if key:
        return key
    with open(os.path.join(ROOT, ".mcp.json")) as f:
        cfg = json.load(f)
    for srv in cfg.get("mcpServers", {}).values():
        env = srv.get("env", {}) or {}
        for name in ("KLAVIYO_API_KEY", "PRIVATE_API_KEY"):
            if env.get(name, "").startswith("pk_"):
                return env[name]
    raise SystemExit("Brak klucza pk_ w .mcp.json ani w KLAVIYO_API_KEY")


KEY = api_key()


def request(method: str, path: str, body: dict | None = None, params: dict | None = None,
            retries: int = 5) -> dict:
    url = API + path
    if params:
        url += "?" + urllib.parse.urlencode({k: v for k, v in params.items() if v is not None})
    headers = {
        "Authorization": f"Klaviyo-API-Key {KEY}",
        "revision": REVISION,
        "Accept": "application/vnd.api+json",
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/vnd.api+json"
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                raw = r.read().decode()
                return json.loads(raw) if raw else {"_status": r.status}
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:2000]
            # 429 = rate limit; backoff i ponow
            if e.code == 429 and attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            try:
                detail = json.loads(detail)
            except Exception:
                pass
            return {"_error": True, "http_status": e.code, "detail": detail}
        except Exception as e:  # noqa: BLE001
            if attempt < retries - 1:
                time.sleep(3)
                continue
            return {"_error": True, "detail": f"{type(e).__name__}: {e}"}
    return {"_error": True, "detail": "retries exhausted"}


# ------------------------------ SEGMENTY ------------------------------

def list_segments() -> list[dict]:
    out, cursor = [], None
    while True:
        r = request("GET", "/segments", params={"page[cursor]": cursor})
        if r.get("_error"):
            raise SystemExit(f"list_segments: {r}")
        out += r["data"]
        cursor = None
        nxt = r.get("links", {}).get("next")
        if not nxt:
            break
        cursor = urllib.parse.parse_qs(urllib.parse.urlparse(nxt).query)["page[cursor]"][0]
    return out


def create_segment(name: str, condition_groups: list[dict]) -> dict:
    body = {"data": {"type": "segment", "attributes": {
        "name": name, "definition": {"condition_groups": condition_groups}}}}
    r = request("POST", "/segments", body)
    time.sleep(4.5)  # 15/min
    return r


def delete_segment(seg_id: str) -> dict:
    r = request("DELETE", f"/segments/{seg_id}")
    time.sleep(1.5)
    return r


def segment_count(seg_id: str) -> int | None:
    r = request("GET", f"/segments/{seg_id}", params={"additional-fields[segment]": "profile_count"})
    if r.get("_error"):
        return None
    a = r["data"]["attributes"]
    return None if a.get("is_processing") else a.get("profile_count")


def wait_until_ready(seg_ids: list[str], timeout: int = 900) -> dict[str, int]:
    """Czeka az wszystkie segmenty przelicza sie; zwraca {id: count}."""
    counts, t0 = {}, time.time()
    pending = list(seg_ids)
    while pending and time.time() - t0 < timeout:
        still = []
        for sid in pending:
            c = segment_count(sid)
            if c is None:
                still.append(sid)
            else:
                counts[sid] = c
            time.sleep(0.4)
        pending = still
        if pending:
            time.sleep(10)
    for sid in pending:
        counts[sid] = -1  # nie zdazyl sie przeliczyc
    return counts


def segment_profile_ids(seg_id: str) -> set[str]:
    """Wszystkie profile_id nalezace do segmentu (paginacja po 100)."""
    ids, cursor = set(), None
    while True:
        r = request("GET", f"/segments/{seg_id}/profiles",
                    params={"page[size]": 100, "page[cursor]": cursor, "fields[profile]": "email"})
        if r.get("_error"):
            raise SystemExit(f"segment_profile_ids({seg_id}): {r}")
        ids |= {p["id"] for p in r["data"]}
        nxt = r.get("links", {}).get("next")
        if not nxt:
            break
        cursor = urllib.parse.parse_qs(urllib.parse.urlparse(nxt).query)["page[cursor]"][0]
        time.sleep(0.15)
    return ids


# ------------------------------ WARUNKI ------------------------------

M_ACTIVE_ON_SITE = "SHkgBz"
M_ORDERED_PRODUCT = "X6tAVW"
M_VIEWED_PRODUCT = "Wic3Cx"
M_PLACED_ORDER = "R6aTMS"

TF_ALLTIME = {"type": "date", "operator": "alltime"}


def tf_days(n: int) -> dict:
    return {"type": "date", "operator": "in-the-last", "unit": "day", "quantity": n}


def cond_metric(metric_id: str, timeframe: dict, metric_filters: list | None = None,
                op: str = "greater-than", value: int = 0) -> dict:
    return {
        "type": "profile-metric",
        "metric_id": metric_id,
        "measurement": "count",
        "measurement_filter": {"type": "numeric", "operator": op, "value": value},
        "timeframe_filter": timeframe,
        "metric_filters": metric_filters,
    }


def f_str_contains(prop: str, value: str) -> dict:
    return {"property": prop, "filter": {"type": "string", "operator": "contains", "value": value}}


def cond_lp_visit(path: str, days: int = 365) -> dict:
    """Odwiedzil konkretny landing page (Active on Site -> wlasciwosc `page`)."""
    return cond_metric(M_ACTIVE_ON_SITE, tf_days(days), [f_str_contains("page", path)])


def cond_ordered_sku(fragment: str) -> dict:
    return cond_metric(M_ORDERED_PRODUCT, TF_ALLTIME, [f_str_contains("SKU", fragment)])


def cond_viewed_url(fragment: str, days: int = 365) -> dict:
    return cond_metric(M_VIEWED_PRODUCT, tf_days(days), [f_str_contains("URL", fragment)])

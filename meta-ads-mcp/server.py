"""Meta Ads MCP (GENACTIV, jeden serwer) — pełny konektor do Meta Marketing API.

Zastępuje oba wcześniejsze rozwiązania jednym serwerem:
  - operacje ODCZYTU/ZARZĄDZANIA (jak oryginalny npx meta-ads-mcp): konta, kampanie,
    ad sety, reklamy, kreacje, insighty, status (pause/resume), preview, token.
  - operacje ZAPISU, których oryginał NIE miał: upload obrazu, create_ad,
    kreacja wieloformatowa (asset_feed_spec + placement customization), update kreacji.
  - graph_get / graph_post / delete_object — uniwersalna furtka do Graph API na resztę.

Env: META_ACCESS_TOKEN (wymagany), META_API_VERSION (domyślnie v21.0),
     META_AD_ACCOUNT_ID (domyślne konto, format act_XXXX).
Uruchomienie: fastmcp run server.py
"""
import json
import os

import requests
from fastmcp import FastMCP

TOKEN = os.environ.get("META_ACCESS_TOKEN", "")
VER = os.environ.get("META_API_VERSION", "v21.0")
DEFAULT_ACCT = os.environ.get("META_AD_ACCOUNT_ID", "")
BASE = f"https://graph.facebook.com/{VER}"

mcp = FastMCP("meta-ads")

# stałe GENACTIV (konto act_1468836364771482) — domyślne tożsamości do tworzenia reklam
GENACTIV_PAGE_ID = "291918870818824"
GENACTIV_IG_USER_ID = "17841402903788419"
GENACTIV_PIXEL_ID = "370142134442442"
DEFAULT_URL_TAGS = ("utm_source={{site_source_name}}&utm_medium={{placement}}"
                    "&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_id={{campaign.id}}")


def _acct(account_id):
    a = (account_id or DEFAULT_ACCT or "").strip()
    if a and not a.startswith("act_"):
        a = "act_" + a
    return a


def _ok(resp):
    try:
        data = resp.json()
    except ValueError:
        data = {"raw": resp.text}
    if resp.status_code >= 400 or (isinstance(data, dict) and "error" in data):
        return {"status": "ERROR", "http_status": resp.status_code, "error": data}
    return {"status": "OK", "data": data}


def _get(path, params=None):
    p = dict(params or {})
    p["access_token"] = TOKEN
    return _ok(requests.get(f"{BASE}/{path.lstrip('/')}", params=p, timeout=120))


def _post(path, data=None):
    d = {k: (json.dumps(v) if isinstance(v, (dict, list)) else v) for k, v in (data or {}).items()}
    d["access_token"] = TOKEN
    return _ok(requests.post(f"{BASE}/{path.lstrip('/')}", data=d, timeout=120))


# ───────────────────────── ODCZYT / KONTO / TOKEN ─────────────────────────

@mcp.tool
def get_ad_accounts() -> dict:
    """Lista kont reklamowych dostępnych pod tokenem (id, nazwa, status, waluta)."""
    return _get("me/adaccounts", {"fields": "id,name,account_status,currency,timezone_name,balance"})


@mcp.tool
def get_token_info() -> dict:
    """Info o tokenie: zalogowany user + przyznane uprawnienia (scopes)."""
    me = _get("me", {"fields": "id,name"})
    perms = _get("me/permissions")
    return {"status": "OK", "me": me.get("data"), "permissions": perms.get("data")}


@mcp.tool
def list_pages() -> dict:
    """Fanpage'e pod tokenem + podpięte konta IG (page_id / instagram_business_account)."""
    return _get("me/accounts", {"fields": "id,name,instagram_business_account{id,username}"})


# ───────────────────────── KAMPANIE ─────────────────────────

@mcp.tool
def list_campaigns(account_id: str | None = None, status: str | None = None, limit: int = 50) -> dict:
    """Lista kampanii konta. status opcjonalnie: ACTIVE/PAUSED/ARCHIVED."""
    params = {"fields": "id,name,objective,status,effective_status,daily_budget,lifetime_budget,created_time", "limit": limit}
    if status:
        params["effective_status"] = json.dumps([status])
    return _get(f"{_acct(account_id)}/campaigns", params)


@mcp.tool
def get_campaign(campaign_id: str) -> dict:
    """Szczegóły kampanii."""
    return _get(campaign_id, {"fields": "id,name,objective,status,effective_status,bid_strategy,daily_budget,lifetime_budget,special_ad_categories,start_time,stop_time"})


@mcp.tool
def create_campaign(name: str, objective: str = "OUTCOME_SALES", status: str = "PAUSED",
                    daily_budget: int | None = None, bid_strategy: str | None = None,
                    special_ad_categories: str = "NONE", account_id: str | None = None) -> dict:
    """Tworzy kampanię (domyślnie PAUSED). objective np. OUTCOME_SALES/OUTCOME_TRAFFIC."""
    body = {"name": name, "objective": objective, "status": status,
            "special_ad_categories": [special_ad_categories]}
    if daily_budget:
        body["daily_budget"] = daily_budget
    if bid_strategy:
        body["bid_strategy"] = bid_strategy
    return _post(f"{_acct(account_id)}/campaigns", body)


@mcp.tool
def update_campaign(campaign_id: str, fields_json: str) -> dict:
    """Aktualizuje pola kampanii (JSON, np. {\"name\":\"...\",\"daily_budget\":5000})."""
    return _post(campaign_id, json.loads(fields_json))


@mcp.tool
def pause_campaign(campaign_id: str) -> dict:
    """Wstrzymuje kampanię (status=PAUSED)."""
    return _post(campaign_id, {"status": "PAUSED"})


@mcp.tool
def resume_campaign(campaign_id: str) -> dict:
    """Wznawia kampanię (status=ACTIVE)."""
    return _post(campaign_id, {"status": "ACTIVE"})


@mcp.tool
def delete_campaign(campaign_id: str) -> dict:
    """Usuwa kampanię."""
    return _ok(requests.delete(f"{BASE}/{campaign_id}", params={"access_token": TOKEN}, timeout=60))


# ───────────────────────── AD SETY ─────────────────────────

@mcp.tool
def list_ad_sets(campaign_id: str | None = None, account_id: str | None = None, limit: int = 50) -> dict:
    """Lista ad setów dla kampanii (campaign_id) albo całego konta (account_id)."""
    params = {"fields": "id,name,campaign_id,status,effective_status,daily_budget,billing_event,optimization_goal", "limit": limit}
    node = f"{campaign_id}/adsets" if campaign_id else f"{_acct(account_id)}/adsets"
    return _get(node, params)


@mcp.tool
def get_ad_set(adset_id: str) -> dict:
    """Pełny spec ad seta (targeting, promoted_object, optymalizacja, budżet, attribution)."""
    return _get(adset_id, {"fields": "name,campaign{name},status,effective_status,optimization_goal,billing_event,bid_strategy,daily_budget,destination_type,promoted_object,attribution_spec,targeting"})


@mcp.tool
def create_ad_set(campaign_id: str, name: str, optimization_goal: str = "OFFSITE_CONVERSIONS",
                  billing_event: str = "IMPRESSIONS", daily_budget: int = 15000,
                  bid_strategy: str = "LOWEST_COST_WITHOUT_CAP", status: str = "PAUSED",
                  pixel_id: str | None = None, custom_event_type: str = "PURCHASE",
                  countries_json: str = "[\"PL\"]", age_min: int = 18, age_max: int = 65,
                  advantage_audience: int = 1, excluded_custom_audiences_json: str | None = None,
                  publisher_platforms_json: str | None = None,
                  targeting_json: str | None = None, account_id: str | None = None) -> dict:
    """Tworzy ad set (domyślnie PAUSED). Domyślnie konwersje na pixel GENACTIV, PL 18-65,
    Advantage audience on. Pełny override targetingu przez targeting_json; promoted_object
    budowany z pixel_id (domyślnie pixel GENACTIV) + custom_event_type."""
    if targeting_json:
        targeting = json.loads(targeting_json)
    else:
        targeting = {
            "geo_locations": {"countries": json.loads(countries_json), "location_types": ["home", "recent"]},
            "age_min": age_min, "age_max": age_max,
            "targeting_automation": {"advantage_audience": advantage_audience},
        }
        if excluded_custom_audiences_json:
            targeting["excluded_custom_audiences"] = [{"id": i} for i in json.loads(excluded_custom_audiences_json)]
        if publisher_platforms_json:
            targeting["publisher_platforms"] = json.loads(publisher_platforms_json)
    body = {
        "name": name, "campaign_id": campaign_id,
        "optimization_goal": optimization_goal, "billing_event": billing_event,
        "bid_strategy": bid_strategy, "daily_budget": daily_budget, "status": status,
        "promoted_object": {"pixel_id": pixel_id or GENACTIV_PIXEL_ID, "custom_event_type": custom_event_type},
        "attribution_spec": [{"event_type": "CLICK_THROUGH", "window_days": 7},
                             {"event_type": "VIEW_THROUGH", "window_days": 1}],
        "targeting": targeting,
    }
    return _post(f"{_acct(account_id)}/adsets", body)


# ───────────────────────── REKLAMY / KREACJE ─────────────────────────

@mcp.tool
def list_ads(adset_id: str | None = None, campaign_id: str | None = None,
             account_id: str | None = None, limit: int = 50) -> dict:
    """Lista reklam (adset_id / campaign_id / account_id)."""
    params = {"fields": "id,name,status,effective_status,adset{name},creative{id,name}", "limit": limit}
    node = (f"{adset_id}/ads" if adset_id else
            f"{campaign_id}/ads" if campaign_id else f"{_acct(account_id)}/ads")
    return _get(node, params)


@mcp.tool
def list_creatives(account_id: str | None = None, limit: int = 50) -> dict:
    """Lista kreacji w bibliotece konta."""
    return _get(f"{_acct(account_id)}/adcreatives",
                {"fields": "id,name,url_tags,instagram_user_id,object_type", "limit": limit})


@mcp.tool
def get_insights(object_id: str, date_preset: str = "last_30d", level: str | None = None,
                 fields: str = "impressions,clicks,spend,reach,ctr,cpc,cpm,actions,purchase_roas",
                 breakdowns: str | None = None) -> dict:
    """Insighty dla obiektu (account/campaign/adset/ad). date_preset np. today/last_7d/last_30d.
    level opcjonalnie: account/campaign/adset/ad. breakdowns np. 'publisher_platform,platform_position'."""
    params = {"date_preset": date_preset, "fields": fields}
    if level:
        params["level"] = level
    if breakdowns:
        params["breakdowns"] = breakdowns
    return _get(f"{object_id}/insights", params)


@mcp.tool
def preview_ad(creative_id: str, ad_format: str = "MOBILE_FEED_STANDARD") -> dict:
    """Podgląd kreacji w danym formacie. ad_format np. MOBILE_FEED_STANDARD, INSTAGRAM_STANDARD,
    INSTAGRAM_STORY, FACEBOOK_STORY_MOBILE, INSTAGRAM_REELS, DESKTOP_FEED_STANDARD, RIGHT_COLUMN_STANDARD."""
    return _get(f"{creative_id}/previews", {"ad_format": ad_format})


@mcp.tool
def upload_image_from_url(image_url: str, account_id: str | None = None) -> dict:
    """Pobiera obrazek z `image_url` (np. public_url z Monday) i wgrywa do biblioteki konta.
    Zwraca image_hash. Pobiera bajty po stronie serwera, więc działa dla URL-i niewidocznych dla Meta."""
    acct = _acct(account_id)
    if not acct:
        return {"status": "ERROR", "error": "Brak account_id i META_AD_ACCOUNT_ID"}
    src = requests.get(image_url, timeout=120)
    if src.status_code >= 400:
        return {"status": "ERROR", "error": f"Nie pobrano obrazka ({src.status_code}) z {image_url}"}
    r = requests.post(f"{BASE}/{acct}/adimages",
                      data={"access_token": TOKEN}, files={"filename": ("creative.png", src.content)}, timeout=120)
    res = _ok(r)
    if res.get("status") == "OK":
        imgs = res["data"].get("images", {})
        if imgs:
            first = next(iter(imgs.values()))
            res["image_hash"] = first.get("hash")
            res["image_url"] = first.get("url")
    return res


@mcp.tool
def create_image_creative(name: str, image_hash: str, message: str, link_url: str,
                          page_id: str | None = None, headline: str | None = None,
                          description: str | None = None, cta_type: str = "SHOP_NOW",
                          url_tags: str | None = None, instagram_user_id: str | None = None,
                          account_id: str | None = None) -> dict:
    """Tworzy kreację z jednym obrazem (object_story_spec). page_id/IG domyślnie GENACTIV.
    Dla pełnego pokrycia placementów (1:1/4:5/9:16) użyj create_multiformat_creative."""
    acct = _acct(account_id)
    link_data = {"message": message, "link": link_url, "image_hash": image_hash,
                 "call_to_action": {"type": cta_type, "value": {"link": link_url}}}
    if headline:
        link_data["name"] = headline
    if description:
        link_data["description"] = description
    story = {"page_id": page_id or GENACTIV_PAGE_ID, "link_data": link_data}
    payload = {"name": name, "object_story_spec": json.dumps(story),
               "url_tags": url_tags or DEFAULT_URL_TAGS, "access_token": TOKEN}
    iu = instagram_user_id if instagram_user_id is not None else GENACTIV_IG_USER_ID
    if iu:
        payload["instagram_user_id"] = iu
    return _ok(requests.post(f"{BASE}/{acct}/adcreatives", data=payload, timeout=60))


@mcp.tool
def create_multiformat_creative(name: str, square_hash: str, vertical_hash: str, story_hash: str,
                                message: str, link_url: str, page_id: str | None = None,
                                headline: str | None = None, description: str | None = None,
                                cta_type: str = "SHOP_NOW", url_tags: str | None = None,
                                instagram_user_id: str | None = None,
                                account_id: str | None = None) -> dict:
    """JEDNA kreacja z 3 formatami mapowanymi na placementy (asset_feed_spec + asset_customization_rules):
    story_hash 9:16 → Stories/Reels (FB+IG), vertical_hash 4:5 → feedy (FB+IG), square_hash 1:1 → catch-all.
    page_id/IG domyślnie GENACTIV. url_tags domyślnie dynamiczne UTM konta."""
    acct = _acct(account_id)
    afs = {
        "images": [{"hash": square_hash, "adlabels": [{"name": "sq"}]},
                   {"hash": vertical_hash, "adlabels": [{"name": "vt"}]},
                   {"hash": story_hash, "adlabels": [{"name": "st"}]}],
        "bodies": [{"text": message}],
        "link_urls": [{"website_url": link_url}],
        "call_to_action_types": [cta_type],
        "ad_formats": ["SINGLE_IMAGE"],
        "asset_customization_rules": [
            {"customization_spec": {"publisher_platforms": ["facebook", "instagram", "messenger"],
                                    "facebook_positions": ["story", "facebook_reels"],
                                    "instagram_positions": ["story", "reels"],
                                    "messenger_positions": ["story"]},
             "image_label": {"name": "st"}},
            {"customization_spec": {"publisher_platforms": ["facebook", "instagram"],
                                    "facebook_positions": ["feed", "marketplace", "video_feeds", "profile_feed"],
                                    "instagram_positions": ["stream", "explore", "explore_home", "profile_feed"]},
             "image_label": {"name": "vt"}},
            {"customization_spec": {"publisher_platforms": ["facebook", "instagram", "audience_network", "messenger"]},
             "image_label": {"name": "sq"}},
        ],
    }
    if headline:
        afs["titles"] = [{"text": headline}]
    if description:
        afs["descriptions"] = [{"text": description}]
    payload = {"name": name, "object_story_spec": json.dumps({"page_id": page_id or GENACTIV_PAGE_ID}),
               "asset_feed_spec": json.dumps(afs), "url_tags": url_tags or DEFAULT_URL_TAGS,
               "access_token": TOKEN}
    iu = instagram_user_id if instagram_user_id is not None else GENACTIV_IG_USER_ID
    if iu:
        payload["instagram_user_id"] = iu
    return _ok(requests.post(f"{BASE}/{acct}/adcreatives", data=payload, timeout=60))


@mcp.tool
def create_ad(name: str, adset_id: str, creative_id: str,
              status: str = "PAUSED", account_id: str | None = None) -> dict:
    """SPINA creative z ad setem jako realna reklama (Ad). Domyślnie PAUSED (robocza)."""
    return _post(f"{_acct(account_id)}/ads",
                 {"name": name, "adset_id": adset_id, "creative": {"creative_id": creative_id}, "status": status})


@mcp.tool
def update_ad_creative(ad_id: str, creative_id: str) -> dict:
    """Podmienia kreację w istniejącej reklamie."""
    return _post(ad_id, {"creative": {"creative_id": creative_id}})


@mcp.tool
def update_ad_status(ad_id: str, status: str) -> dict:
    """Zmienia status reklamy: ACTIVE / PAUSED."""
    return _post(ad_id, {"status": status})


# ───────────────────────── UNIWERSALNA FURTKA ─────────────────────────

@mcp.tool
def graph_get(path: str, params_json: str | None = None) -> dict:
    """Surowy GET do Graph API. path np. 'me/accounts' albo '<id>'; params_json = dodatkowe parametry JSON."""
    return _get(path, json.loads(params_json) if params_json else None)


@mcp.tool
def graph_post(path: str, data_json: str | None = None) -> dict:
    """Surowy POST do Graph API. path np. 'act_XXX/ads'; data_json = body (obiekty jako zagnieżdżony JSON)."""
    return _post(path, json.loads(data_json) if data_json else None)


@mcp.tool
def delete_object(object_id: str) -> dict:
    """Usuwa obiekt (ad/creative/adset/campaign) przez DELETE."""
    return _ok(requests.delete(f"{BASE}/{object_id}", params={"access_token": TOKEN}, timeout=60))


if __name__ == "__main__":
    mcp.run()

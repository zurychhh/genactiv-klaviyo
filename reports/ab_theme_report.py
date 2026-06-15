#!/usr/bin/env python3
"""
A/B Theme Comparison Report — GEN-6 vs NOTOAGENCY
Generuje raport HTML z live-refresh i kalkulatorem istotności statystycznej.

Użycie:
  python3 reports/ab_theme_report.py              # Generuj HTML (7 dni) i otwórz
  python3 reports/ab_theme_report.py --days 14    # Ostatnie 14 dni
  python3 reports/ab_theme_report.py --serve      # Dashboard z live-refresh na localhost:8090
  python3 reports/ab_theme_report.py --realtime   # Real-time (CLI)
"""

import os
import sys
import json
import math
import requests
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'genactiv-online', '.env'))

PROPERTY_ID = os.environ.get("GA4_PROPERTY_ID", "279858535")
CLIENT_ID = os.environ.get("GOOGLE_OAUTH_CLIENT_ID", "")
CLIENT_SECRET = os.environ.get("GOOGLE_OAUTH_CLIENT_SECRET", "")
REFRESH_TOKEN = os.environ.get("GA4_REFRESH_TOKEN", "")

SERVE_PORT = 8090

# =====================================================
# GA4 API helpers
# =====================================================

def get_access_token():
    resp = requests.post("https://oauth2.googleapis.com/token", data={
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "grant_type": "refresh_token"
    })
    if resp.status_code != 200:
        print(f"  Token refresh failed: {resp.status_code} {resp.text}")
        return None
    return resp.json()["access_token"]

def ga4_report(access_token, date_ranges, dimensions, metrics, dimension_filter=None, limit=10):
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runReport"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    body = {
        "dateRanges": date_ranges,
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
        "limit": limit,
        "keepEmptyRows": True,
    }
    if dimension_filter:
        body["dimensionFilter"] = dimension_filter
    resp = requests.post(url, headers=headers, json=body)
    if resp.status_code != 200:
        return None
    return resp.json()

def ga4_realtime(access_token, dimensions, metrics):
    url = f"https://analyticsdata.googleapis.com/v1beta/properties/{PROPERTY_ID}:runRealtimeReport"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}
    body = {
        "dimensions": [{"name": d} for d in dimensions],
        "metrics": [{"name": m} for m in metrics],
    }
    resp = requests.post(url, headers=headers, json=body)
    if resp.status_code != 200:
        return None
    return resp.json()

def parse_rows(report_data):
    if not report_data or "rows" not in report_data:
        return []
    dim_headers = [h["name"] for h in report_data.get("dimensionHeaders", [])]
    met_headers = [h["name"] for h in report_data.get("metricHeaders", [])]
    rows = []
    for row in report_data["rows"]:
        dims = {dim_headers[i]: row["dimensionValues"][i]["value"] for i in range(len(dim_headers))}
        mets = {met_headers[i]: row["metricValues"][i]["value"] for i in range(len(met_headers))}
        rows.append({**dims, **mets})
    return rows

# =====================================================
# Metrics config
# =====================================================

METRICS_CONFIG = [
    ("sessions",                "Sesje",                 "num",   True),
    ("totalUsers",              "Użytkownicy",           "num",   True),
    ("bounceRate",              "Bounce Rate",            "pct",   False),
    ("averageSessionDuration",  "Śr. czas sesji",        "dur",   True),
    ("engagementRate",          "Engagement Rate",        "pct",   True),
    ("engagedSessions",         "Engaged sessions",      "num",   True),
    ("screenPageViewsPerSession","Strony/sesję",         "dec",   True),
    ("screenPageViews",         "Pageviews",             "num",   True),
    ("eventCount",              "Events",                "num",   True),
    ("conversions",             "Konwersje",             "num",   True),
    ("totalRevenue",            "Przychód",              "money", True),
    ("ecommercePurchases",      "Zakupy",                "num",   True),
    ("addToCarts",              "Add to Cart",           "num",   True),
    ("itemViews",               "Product Views",         "num",   True),
]

METRIC_NAMES = [m[0] for m in METRICS_CONFIG]

# =====================================================
# Statistical significance
# =====================================================

def calc_sample_size(baseline_rate, mde, alpha=0.05, power=0.80):
    """Required sample size per group for two-proportion z-test.
    baseline_rate: e.g. 0.45 for 45% bounce rate
    mde: minimum detectable effect in absolute terms, e.g. 0.05 for 5pp
    Returns n per group (before adjusting for unequal split).
    """
    from math import ceil
    z_alpha = 1.96 if alpha == 0.05 else 2.576  # 95% or 99%
    z_beta = 0.8416 if power == 0.80 else 1.2816  # 80% or 90%

    p1 = baseline_rate
    p2 = baseline_rate - mde  # assume improvement = lower bounce
    if p2 < 0:
        p2 = 0.01

    p_bar = (p1 + p2) / 2
    n = ((z_alpha * math.sqrt(2 * p_bar * (1 - p_bar)) +
          z_beta * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2) / ((p1 - p2) ** 2)
    return ceil(n)

def calc_z_test(n_a, rate_a, n_b, rate_b):
    """Two-proportion z-test. Returns z-score and p-value."""
    if n_a == 0 or n_b == 0:
        return 0, 1.0
    p_pool = (rate_a * n_a + rate_b * n_b) / (n_a + n_b)
    if p_pool == 0 or p_pool == 1:
        return 0, 1.0
    se = math.sqrt(p_pool * (1 - p_pool) * (1/n_a + 1/n_b))
    if se == 0:
        return 0, 1.0
    z = (rate_b - rate_a) / se
    # Two-tailed p-value approximation
    p_value = 2 * (1 - _norm_cdf(abs(z)))
    return z, p_value

def _norm_cdf(x):
    """Standard normal CDF approximation (Abramowitz & Stegun)."""
    a1, a2, a3, a4, a5 = 0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    p = 0.3275911
    sign = 1 if x >= 0 else -1
    x = abs(x)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t * math.exp(-x*x/2)
    return 0.5 * (1.0 + sign * y)

# =====================================================
# Data fetching
# =====================================================

def fetch_theme_data(access_token, date_ranges, dim_filter):
    all_data = {}
    for i in range(0, len(METRIC_NAMES), 10):
        batch = METRIC_NAMES[i:i+10]
        raw = ga4_report(access_token, date_ranges, [], batch, dim_filter)
        rows = parse_rows(raw)
        if rows:
            all_data.update(rows[0])
    return all_data if all_data else None

def fetch_all_data(days=7):
    """Fetch data for both themes. Returns dict for JSON API."""
    access_token = get_access_token()
    if not access_token:
        return {"error": "Token refresh failed"}

    date_ranges = [{"startDate": f"{days}daysAgo", "endDate": "today"}]

    gen6_filter = {"filter": {"fieldName": "customUser:ab_theme_variant",
        "stringFilter": {"matchType": "EXACT", "value": "GEN-6", "caseSensitive": True}}}
    noto_filter = {"filter": {"fieldName": "customUser:ab_theme_variant",
        "stringFilter": {"matchType": "EXACT", "value": "NOTOAGENCY", "caseSensitive": True}}}

    gen6_data = fetch_theme_data(access_token, date_ranges, gen6_filter)
    noto_data = fetch_theme_data(access_token, date_ranges, noto_filter)

    # Realtime
    rt = ga4_realtime(access_token, ["customUser:ab_theme_variant"], ["activeUsers", "eventCount"])
    rt_rows = parse_rows(rt) if rt else []
    realtime = {}
    for r in rt_rows:
        v = r.get("customUser:ab_theme_variant", "")
        if v:
            realtime[v] = {"activeUsers": int(r.get("activeUsers", 0)), "eventCount": int(r.get("eventCount", 0))}

    # Statistical significance for bounce rate
    sig = {}
    gen6_sessions = int(float(gen6_data.get("sessions", 0))) if gen6_data else 0
    noto_sessions = int(float(noto_data.get("sessions", 0))) if noto_data else 0
    gen6_bounce = float(gen6_data.get("bounceRate", 0)) if gen6_data else 0
    noto_bounce = float(noto_data.get("bounceRate", 0)) if noto_data else 0

    baseline_bounce = gen6_bounce if gen6_bounce > 0 else 0.45
    required_per_group = calc_sample_size(baseline_bounce, 0.05)
    # With 90/10 split, NOTOAGENCY (10%) is the bottleneck
    required_noto = required_per_group
    required_gen6 = required_per_group

    z_score, p_value = calc_z_test(gen6_sessions, gen6_bounce, noto_sessions, noto_bounce)

    sig = {
        "bounceRate": {
            "gen6_n": gen6_sessions,
            "noto_n": noto_sessions,
            "gen6_rate": gen6_bounce,
            "noto_rate": noto_bounce,
            "required_per_group": required_per_group,
            "required_noto_adjusted": int(required_per_group),
            "progress_noto_pct": min(100, round(noto_sessions / max(required_per_group, 1) * 100, 1)),
            "progress_gen6_pct": min(100, round(gen6_sessions / max(required_per_group, 1) * 100, 1)),
            "z_score": round(z_score, 3),
            "p_value": round(p_value, 4),
            "is_significant": p_value < 0.05,
            "confidence_pct": round((1 - p_value) * 100, 1) if p_value < 1 else 0,
            "mde": 0.05,
            "alpha": 0.05,
            "power": 0.80,
        },
    }

    # Same for conversion rate
    gen6_conv = int(float(gen6_data.get("ecommercePurchases", 0))) if gen6_data else 0
    noto_conv = int(float(noto_data.get("ecommercePurchases", 0))) if noto_data else 0
    gen6_cr = gen6_conv / gen6_sessions if gen6_sessions > 0 else 0
    noto_cr = noto_conv / noto_sessions if noto_sessions > 0 else 0
    baseline_cr = gen6_cr if gen6_cr > 0 else 0.02
    required_cr = calc_sample_size(baseline_cr, 0.01)
    z_cr, p_cr = calc_z_test(gen6_sessions, gen6_cr, noto_sessions, noto_cr)

    sig["conversionRate"] = {
        "gen6_n": gen6_sessions,
        "noto_n": noto_sessions,
        "gen6_rate": round(gen6_cr, 4),
        "noto_rate": round(noto_cr, 4),
        "required_per_group": required_cr,
        "progress_noto_pct": min(100, round(noto_sessions / max(required_cr, 1) * 100, 1)),
        "z_score": round(z_cr, 3),
        "p_value": round(p_cr, 4),
        "is_significant": p_cr < 0.05,
        "confidence_pct": round((1 - p_cr) * 100, 1) if p_cr < 1 else 0,
        "mde": 0.01,
        "alpha": 0.05,
        "power": 0.80,
    }

    return {
        "gen6": gen6_data,
        "noto": noto_data,
        "realtime": realtime,
        "significance": sig,
        "days": days,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "period": {
            "start": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
            "end": datetime.now().strftime("%Y-%m-%d"),
        },
        "metrics_config": [{"key": m[0], "label": m[1], "format": m[2], "higher_is_better": m[3]} for m in METRICS_CONFIG],
    }

# =====================================================
# HTML dashboard (self-contained with JS refresh)
# =====================================================

def generate_dashboard_html(initial_data_json, serve_mode=False, access_token="", token_expiry=""):
    api_base = f"http://localhost:{SERVE_PORT}" if serve_mode else ""

    # For standalone HTML, embed credentials for client-side refresh
    ga4_config_json = json.dumps({
        "property_id": PROPERTY_ID,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "refresh_token": REFRESH_TOKEN,
        "metrics": METRIC_NAMES,
        "metrics_config": [{"key": m[0], "label": m[1], "format": m[2], "higher_is_better": m[3]} for m in METRICS_CONFIG],
    }) if not serve_mode else "{}"

    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>A/B Theme Report — GenActiv</title>
<style>
:root {{
    --blue: #0066CC; --red: #EF3340; --green: #27ae60; --navy: #1A3B5D;
    --bg: #0d1117; --card: #161b22; --border: #30363d;
    --text: #c9d1d9; --text-dim: #8b949e; --text-bright: #f0f6fc;
    --yellow: #d29922;
}}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ background: var(--bg); color: var(--text); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif; padding: 24px; }}
.container {{ max-width: 960px; margin: 0 auto; }}

/* Header */
header {{ text-align: center; margin-bottom: 24px; padding: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 12px; }}
header h1 {{ color: var(--text-bright); font-size: 22px; margin-bottom: 6px; }}
header .subtitle {{ color: var(--text-dim); font-size: 13px; }}
.period-badge {{ display: inline-block; margin-top: 10px; padding: 4px 14px; background: var(--navy); color: var(--blue); border-radius: 20px; font-size: 13px; font-weight: 600; }}
.split-row {{ display: flex; justify-content: center; gap: 40px; margin-top: 14px; }}
.split-box {{ text-align: center; }}
.split-box .pct {{ font-size: 32px; font-weight: 800; }}
.split-box .pct.gen6 {{ color: var(--blue); }}
.split-box .pct.noto {{ color: var(--red); }}
.split-box .lbl {{ font-size: 11px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 0.5px; }}

/* Refresh bar */
.toolbar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; flex-wrap: wrap; gap: 10px; }}
.toolbar .meta {{ font-size: 12px; color: var(--text-dim); }}
.toolbar .meta .live-dot {{ display: inline-block; width: 8px; height: 8px; border-radius: 50%; background: var(--green); margin-right: 4px; animation: pulse 2s infinite; }}
@keyframes pulse {{ 0%,100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}
.btn-group {{ display: flex; gap: 6px; }}
.btn {{ padding: 8px 16px; border: 1px solid var(--border); background: var(--card); color: var(--text-bright); border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; transition: all 0.15s; }}
.btn:hover {{ background: var(--border); }}
.btn.active {{ border-color: var(--blue); color: var(--blue); }}
.btn.refresh {{ border-color: var(--green); color: var(--green); }}
.btn.refresh:hover {{ background: rgba(39,174,96,0.15); }}
.btn.refresh.loading {{ opacity: 0.5; pointer-events: none; }}

/* Realtime strip */
.rt-strip {{ display: flex; gap: 12px; margin-bottom: 20px; }}
.rt-card {{ flex: 1; padding: 14px; background: var(--card); border: 1px solid var(--border); border-radius: 10px; text-align: center; }}
.rt-card .rt-val {{ font-size: 28px; font-weight: 800; font-variant-numeric: tabular-nums; }}
.rt-card .rt-label {{ font-size: 11px; color: var(--text-dim); text-transform: uppercase; margin-top: 2px; }}
.rt-card.gen6 .rt-val {{ color: var(--blue); }}
.rt-card.noto .rt-val {{ color: var(--red); }}
.rt-card.total .rt-val {{ color: var(--text-bright); }}

/* Table */
table {{ width: 100%; border-collapse: collapse; background: var(--card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
thead th {{ background: var(--navy); color: var(--text-bright); padding: 12px 14px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
thead th:nth-child(n+2) {{ text-align: right; }}
thead th.gen6 {{ color: var(--blue); }}
thead th.noto {{ color: var(--red); }}
tbody td {{ padding: 11px 14px; border-top: 1px solid var(--border); font-size: 14px; }}
tbody tr:hover {{ background: rgba(48,54,61,0.4); }}
.metric-name {{ font-weight: 500; color: var(--text-bright); }}
.val {{ text-align: right; font-variant-numeric: tabular-nums; }}
.delta {{ text-align: right; }}
.badge {{ display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
.badge.positive {{ background: rgba(39,174,96,0.15); color: #3fb950; }}
.badge.negative {{ background: rgba(239,51,64,0.15); color: #f85149; }}
.badge.neutral {{ background: rgba(139,148,158,0.15); color: #8b949e; }}

/* Significance panel */
.sig-panel {{ margin-top: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; }}
.sig-panel h2 {{ color: var(--text-bright); font-size: 16px; margin-bottom: 16px; }}
.sig-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
@media (max-width: 700px) {{ .sig-grid {{ grid-template-columns: 1fr; }} }}
.sig-card {{ padding: 20px; background: var(--bg); border: 1px solid var(--border); border-radius: 10px; }}
.sig-card h3 {{ font-size: 14px; color: var(--text-bright); margin-bottom: 14px; }}
.sig-card .verdict {{ font-size: 15px; font-weight: 700; margin-bottom: 12px; padding: 8px 14px; border-radius: 8px; text-align: center; }}
.verdict.significant {{ background: rgba(39,174,96,0.15); color: #3fb950; border: 1px solid rgba(39,174,96,0.3); }}
.verdict.not-yet {{ background: rgba(210,153,34,0.12); color: var(--yellow); border: 1px solid rgba(210,153,34,0.3); }}
.verdict.no-data {{ background: rgba(139,148,158,0.1); color: var(--text-dim); border: 1px solid var(--border); }}

/* Progress bar */
.progress-row {{ margin: 10px 0; }}
.progress-label {{ display: flex; justify-content: space-between; font-size: 12px; color: var(--text-dim); margin-bottom: 4px; }}
.progress-bar {{ height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }}
.progress-fill {{ height: 100%; border-radius: 4px; transition: width 0.5s ease; }}
.progress-fill.gen6 {{ background: var(--blue); }}
.progress-fill.noto {{ background: var(--red); }}
.progress-fill.done {{ background: var(--green); }}

/* Stats grid */
.stat-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 6px; margin-top: 12px; }}
.stat {{ font-size: 12px; }}
.stat .stat-label {{ color: var(--text-dim); }}
.stat .stat-val {{ color: var(--text-bright); font-weight: 600; font-variant-numeric: tabular-nums; }}

/* Conditions checklist */
.conditions {{ margin-top: 24px; background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 24px; }}
.conditions h2 {{ color: var(--text-bright); font-size: 16px; margin-bottom: 14px; }}
.conditions ul {{ list-style: none; padding: 0; }}
.conditions li {{ padding: 8px 0; border-bottom: 1px solid var(--border); font-size: 13px; display: flex; align-items: flex-start; gap: 10px; }}
.conditions li:last-child {{ border-bottom: none; }}
.conditions .icon {{ font-size: 16px; flex-shrink: 0; margin-top: 1px; }}
.conditions .check {{ color: var(--green); }}
.conditions .warn {{ color: var(--yellow); }}
.conditions .cross {{ color: var(--red); }}
.conditions .pending {{ color: var(--text-dim); }}
.cond-desc {{ color: var(--text-dim); font-size: 12px; margin-top: 2px; }}

/* No data */
.no-data {{ text-align: center; padding: 40px; background: var(--card); border: 1px dashed var(--border); border-radius: 12px; margin-bottom: 20px; }}
.no-data h2 {{ color: var(--text-bright); margin-bottom: 10px; font-size: 18px; }}
.no-data code {{ background: var(--border); padding: 2px 6px; border-radius: 4px; font-size: 12px; }}

footer {{ text-align: center; margin-top: 24px; color: var(--text-dim); font-size: 11px; }}
footer code {{ background: var(--border); padding: 2px 4px; border-radius: 3px; font-size: 11px; }}
</style>
</head>
<body>
<div class="container">

<header>
    <h1>A/B Theme Comparison Report</h1>
    <div class="subtitle">GenActiv.pl — Shopify Theme A/B Test</div>
    <div class="period-badge" id="period-badge">—</div>
    <div class="split-row">
        <div class="split-box"><div class="pct gen6">90%</div><div class="lbl">GEN-6 (baseline)</div></div>
        <div class="split-box"><div class="pct noto">10%</div><div class="lbl">NOTOAGENCY (variant)</div></div>
    </div>
</header>

<div class="toolbar">
    <div class="meta">
        <span class="live-dot"></span>
        Ostatnia aktualizacja: <span id="updated-at">—</span>
    </div>
    <div class="btn-group">
        <button class="btn" onclick="loadData(7)" id="btn-7d">7 dni</button>
        <button class="btn" onclick="loadData(14)" id="btn-14d">14 dni</button>
        <button class="btn" onclick="loadData(30)" id="btn-30d">30 dni</button>
        <button class="btn refresh" onclick="refreshData()" id="btn-refresh">Odśwież dane</button>
    </div>
</div>

<div class="rt-strip" id="rt-strip">
    <div class="rt-card total"><div class="rt-val" id="rt-total">—</div><div class="rt-label">Aktywni teraz</div></div>
    <div class="rt-card gen6"><div class="rt-val" id="rt-gen6">—</div><div class="rt-label">GEN-6 live</div></div>
    <div class="rt-card noto"><div class="rt-val" id="rt-noto">—</div><div class="rt-label">NOTOAGENCY live</div></div>
</div>

<div id="no-data-banner" style="display:none"></div>

<table>
<thead>
    <tr>
        <th>Metryka</th>
        <th class="gen6">GEN-6</th>
        <th class="noto">NOTOAGENCY</th>
        <th>Delta</th>
    </tr>
</thead>
<tbody id="metrics-body">
    <tr><td colspan="4" style="text-align:center;color:var(--text-dim);padding:20px">Ładowanie danych...</td></tr>
</tbody>
</table>

<div class="sig-panel">
    <h2>Istotność statystyczna</h2>
    <div class="sig-grid" id="sig-grid">
        <div class="sig-card"><div class="verdict no-data">Ładowanie...</div></div>
    </div>
</div>

<div class="conditions">
    <h2>Warunki istotności statystycznej testu A/B</h2>
    <ul id="conditions-list"></ul>
</div>

<footer>
    <p>GA4 Property: {PROPERTY_ID} | Dimension: <code>customUser:ab_theme_variant</code></p>
    <p style="margin-top:4px">CLI: <code>python3 reports/ab_theme_report.py --serve</code></p>
</footer>

</div>

<script>
const API_BASE = "{api_base}";
let currentDays = 7;
let DATA = {initial_data_json};

// ======================== Formatters ========================
function fmtNum(v) {{
    const n = parseFloat(v || 0);
    if (Number.isInteger(n)) return n.toLocaleString('pl-PL');
    return n.toLocaleString('pl-PL', {{minimumFractionDigits:2, maximumFractionDigits:2}});
}}
function fmtPct(v) {{ return (parseFloat(v || 0) * 100).toFixed(1) + '%'; }}
function fmtDur(v) {{
    const s = Math.round(parseFloat(v || 0));
    const m = Math.floor(s / 60);
    return m + 'm ' + (s % 60) + 's';
}}
function fmtMoney(v) {{ return Math.round(parseFloat(v || 0)).toLocaleString('pl-PL') + ' PLN'; }}
function fmtDec(v) {{ return parseFloat(v || 0).toFixed(2); }}

const FORMATTERS = {{ num: fmtNum, pct: fmtPct, dur: fmtDur, money: fmtMoney, dec: fmtDec }};

function deltaBadge(a, b, higherBetter, isPct) {{
    a = parseFloat(a || 0); b = parseFloat(b || 0);
    if (a === 0) return '<span class="badge neutral">n/a</span>';
    let diff = ((b - a) / a) * 100;
    let sign = diff > 0 ? '+' : '';
    let display = isPct ? (sign + ((b-a)*100).toFixed(1) + 'pp') : (sign + diff.toFixed(1) + '%');
    let dir = isPct ? (b - a) : diff;
    let cls = Math.abs(dir) < 1 ? 'neutral' : ((dir > 0 && higherBetter) || (dir < 0 && !higherBetter)) ? 'positive' : 'negative';
    return `<span class="badge ${{cls}}">${{display}}</span>`;
}}

// ======================== Render ========================
function render(data) {{
    DATA = data;
    const gen6 = data.gen6 || {{}};
    const noto = data.noto || {{}};
    const rt = data.realtime || {{}};
    const sig = data.significance || {{}};

    // Period
    document.getElementById('period-badge').textContent = `${{data.period?.start}} → ${{data.period?.end}} (${{data.days}} dni)`;
    document.getElementById('updated-at').textContent = data.generated_at || '—';

    // Realtime
    const rtGen6 = rt['GEN-6']?.activeUsers || 0;
    const rtNoto = rt['NOTOAGENCY']?.activeUsers || 0;
    document.getElementById('rt-gen6').textContent = rtGen6;
    document.getElementById('rt-noto').textContent = rtNoto;
    document.getElementById('rt-total').textContent = rtGen6 + rtNoto;

    // No data banner
    const hasData = Object.keys(gen6).length > 0 || Object.keys(noto).length > 0;
    const banner = document.getElementById('no-data-banner');
    if (!hasData) {{
        banner.style.display = 'block';
        banner.innerHTML = '<div class="no-data"><h2>Brak danych A/B</h2><p>Skrypty zostały właśnie wdrożone. Dane pojawią się po pierwszych sesjach.</p></div>';
    }} else {{
        banner.style.display = 'none';
    }}

    // Metrics table
    const metrics = data.metrics_config || [];
    let rows = '';
    metrics.forEach(m => {{
        const fmt = FORMATTERS[m.format] || fmtNum;
        const va = gen6[m.key] || '0';
        const vb = noto[m.key] || '0';
        const isPct = m.format === 'pct';
        rows += `<tr>
            <td class="metric-name">${{m.label}}</td>
            <td class="val">${{fmt(va)}}</td>
            <td class="val">${{fmt(vb)}}</td>
            <td class="delta">${{deltaBadge(va, vb, m.higher_is_better, isPct)}}</td>
        </tr>`;
    }});
    document.getElementById('metrics-body').innerHTML = rows;

    // Significance cards
    renderSignificance(sig);

    // Conditions checklist
    renderConditions(data);

    // Active day button
    document.querySelectorAll('.btn-group .btn:not(.refresh)').forEach(b => b.classList.remove('active'));
    const activeBtn = document.getElementById(`btn-${{data.days}}d`);
    if (activeBtn) activeBtn.classList.add('active');
}}

function renderSignificance(sig) {{
    let html = '';

    // Bounce Rate card
    const br = sig.bounceRate || {{}};
    html += sigCard('Bounce Rate', br, v => (v*100).toFixed(1)+'%', false);

    // Conversion Rate card
    const cr = sig.conversionRate || {{}};
    html += sigCard('Conversion Rate', cr, v => (v*100).toFixed(2)+'%', true);

    document.getElementById('sig-grid').innerHTML = html;
}}

function sigCard(title, s, rateFmt, higherBetter) {{
    if (!s || !s.gen6_n) {{
        return `<div class="sig-card"><h3>${{title}}</h3><div class="verdict no-data">Brak danych</div></div>`;
    }}

    let verdictClass, verdictText;
    if (s.is_significant) {{
        verdictClass = 'significant';
        verdictText = `Istotny statystycznie (p=${{s.p_value.toFixed(4)}}, ${{s.confidence_pct}}% confidence)`;
    }} else if (s.gen6_n < 100 || s.noto_n < 30) {{
        verdictClass = 'no-data';
        verdictText = 'Za mało danych';
    }} else {{
        verdictClass = 'not-yet';
        verdictText = `Brak istotności (p=${{s.p_value.toFixed(4)}}, potrzeba więcej danych)`;
    }}

    const progNoto = Math.min(100, s.progress_noto_pct || 0);
    const progGen6 = Math.min(100, s.progress_gen6_pct || 0);
    const progNotoClass = progNoto >= 100 ? 'done' : 'noto';
    const progGen6Class = progGen6 >= 100 ? 'done' : 'gen6';

    return `<div class="sig-card">
        <h3>${{title}}</h3>
        <div class="verdict ${{verdictClass}}">${{verdictText}}</div>
        <div class="progress-row">
            <div class="progress-label"><span>NOTOAGENCY: ${{s.noto_n}} / ${{s.required_per_group}} sesji</span><span>${{progNoto.toFixed(0)}}%</span></div>
            <div class="progress-bar"><div class="progress-fill ${{progNotoClass}}" style="width:${{progNoto}}%"></div></div>
        </div>
        <div class="progress-row">
            <div class="progress-label"><span>GEN-6: ${{s.gen6_n}} / ${{s.required_per_group}} sesji</span><span>${{progGen6.toFixed(0)}}%</span></div>
            <div class="progress-bar"><div class="progress-fill ${{progGen6Class}}" style="width:${{progGen6}}%"></div></div>
        </div>
        <div class="stat-grid">
            <div class="stat"><span class="stat-label">GEN-6 rate:</span> <span class="stat-val">${{rateFmt(s.gen6_rate)}}</span></div>
            <div class="stat"><span class="stat-label">NOTO rate:</span> <span class="stat-val">${{rateFmt(s.noto_rate)}}</span></div>
            <div class="stat"><span class="stat-label">Z-score:</span> <span class="stat-val">${{s.z_score}}</span></div>
            <div class="stat"><span class="stat-label">p-value:</span> <span class="stat-val">${{s.p_value}}</span></div>
            <div class="stat"><span class="stat-label">MDE:</span> <span class="stat-val">${{(s.mde*100)}}pp</span></div>
            <div class="stat"><span class="stat-label">Power:</span> <span class="stat-val">${{s.power*100}}%</span></div>
        </div>
    </div>`;
}}

function renderConditions(data) {{
    const gen6 = data.gen6 || {{}};
    const noto = data.noto || {{}};
    const sig = data.significance?.bounceRate || {{}};
    const gen6n = parseInt(gen6.sessions || 0);
    const noton = parseInt(noto.sessions || 0);
    const req = sig.required_per_group || 800;

    const conditions = [
        {{
            check: gen6n > 0 && noton > 0,
            warn: gen6n > 0 || noton > 0,
            label: 'Dane zbierają się z obu wariantów',
            desc: `GEN-6: ${{gen6n}} sesji, NOTOAGENCY: ${{noton}} sesji. Oba muszą mieć >0.`,
        }},
        {{
            check: noton >= req,
            warn: noton >= req * 0.3,
            label: `Minimalna próbka NOTOAGENCY (10%): ${{noton}} / ${{req}} sesji`,
            desc: `Przy splicie 90/10 mniejsza grupa (10%) jest wąskim gardłem. Potrzebujesz min. ${{req}} sesji w NOTOAGENCY.`,
        }},
        {{
            check: gen6n >= req,
            warn: gen6n >= req * 0.3,
            label: `Minimalna próbka GEN-6 (90%): ${{gen6n}} / ${{req}} sesji`,
            desc: `Baseline potrzebuje tyle samo sesji co variant (${{req}}).`,
        }},
        {{
            check: data.days >= 7,
            warn: data.days >= 3,
            label: `Test trwa min. 7 pełnych dni (teraz: ${{data.days}})`,
            desc: 'Potrzeba min. 1 pełnego tygodnia, żeby uwzględnić różnice weekday vs weekend. Ideał: 2-4 tygodnie.',
        }},
        {{
            check: noton >= 100 && Math.abs((noton / (gen6n + noton)) - 0.1) < 0.03,
            warn: noton > 0 && gen6n > 0,
            label: 'Split 90/10 jest zachowany (brak skrzywienia)',
            desc: `Aktualny split: GEN-6 ${{gen6n > 0 ? ((gen6n/(gen6n+noton))*100).toFixed(1) : '—'}}% / NOTO ${{noton > 0 ? ((noton/(gen6n+noton))*100).toFixed(1) : '—'}}%. Powinno być ~90/10.`,
        }},
        {{
            check: sig.is_significant === true,
            warn: sig.p_value < 0.10,
            label: 'Osiągnięta istotność statystyczna (p < 0.05)',
            desc: `Aktualnie p=${{sig.p_value || '—'}}. Wynik jest istotny gdy p < 0.05 (95% confidence). Test: two-proportion z-test, MDE=5pp, power=80%.`,
        }},
        {{
            check: false,
            warn: true,
            label: 'Brak zmian w kampaniach/promocjach w trakcie testu',
            desc: 'Upewnij się, że w trakcie testu nie ruszałeś kampanii Google Ads, Meta Ads, newsletterów ani promocji cenowych — to wpłynie na wyniki.',
        }},
        {{
            check: false,
            warn: true,
            label: 'Consent banner (Pandectes) identyczny na obu tematach',
            desc: 'Różne ustawienia consent banneru = różny % mierzonego ruchu. Skopiowane 2026-06-12.',
        }},
    ];

    let html = '';
    conditions.forEach(c => {{
        let iconClass, icon;
        if (c.check) {{ iconClass = 'check'; icon = '&#10003;'; }}
        else if (c.warn) {{ iconClass = 'warn'; icon = '&#9888;'; }}
        else {{ iconClass = 'pending'; icon = '&#9679;'; }}
        html += `<li>
            <span class="icon ${{iconClass}}">${{icon}}</span>
            <div>
                <div>${{c.label}}</div>
                <div class="cond-desc">${{c.desc}}</div>
            </div>
        </li>`;
    }});
    document.getElementById('conditions-list').innerHTML = html;
}}

// ======================== GA4 client-side API ========================
const GA4_CONFIG = {ga4_config_json};
let _cachedAccessToken = null;
let _tokenExpiresAt = 0;

async function getAccessToken() {{
    if (_cachedAccessToken && Date.now() < _tokenExpiresAt) return _cachedAccessToken;
    if (!GA4_CONFIG.client_id) return null;
    try {{
        const resp = await fetch('https://oauth2.googleapis.com/token', {{
            method: 'POST',
            headers: {{ 'Content-Type': 'application/x-www-form-urlencoded' }},
            body: new URLSearchParams({{
                client_id: GA4_CONFIG.client_id,
                client_secret: GA4_CONFIG.client_secret,
                refresh_token: GA4_CONFIG.refresh_token,
                grant_type: 'refresh_token',
            }})
        }});
        if (!resp.ok) return null;
        const data = await resp.json();
        _cachedAccessToken = data.access_token;
        _tokenExpiresAt = Date.now() + (data.expires_in - 60) * 1000;
        return _cachedAccessToken;
    }} catch(e) {{ console.error('Token refresh error:', e); return null; }}
}}

async function ga4Report(token, dateRanges, metrics, dimFilter) {{
    const url = `https://analyticsdata.googleapis.com/v1beta/properties/${{GA4_CONFIG.property_id}}:runReport`;
    const body = {{
        dateRanges, dimensions: [], metrics: metrics.map(m => ({{name: m}})),
        limit: 10, keepEmptyRows: true,
    }};
    if (dimFilter) body.dimensionFilter = dimFilter;
    const resp = await fetch(url, {{
        method: 'POST',
        headers: {{ 'Authorization': `Bearer ${{token}}`, 'Content-Type': 'application/json' }},
        body: JSON.stringify(body),
    }});
    if (!resp.ok) return null;
    return resp.json();
}}

async function ga4Realtime(token) {{
    const url = `https://analyticsdata.googleapis.com/v1beta/properties/${{GA4_CONFIG.property_id}}:runRealtimeReport`;
    const resp = await fetch(url, {{
        method: 'POST',
        headers: {{ 'Authorization': `Bearer ${{token}}`, 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
            dimensions: [{{name: 'customUser:ab_theme_variant'}}],
            metrics: [{{name: 'activeUsers'}}, {{name: 'eventCount'}}],
        }}),
    }});
    if (!resp.ok) return null;
    return resp.json();
}}

function parseGA4Rows(report) {{
    if (!report || !report.rows) return {{}};
    const mh = (report.metricHeaders || []).map(h => h.name);
    const result = {{}};
    (report.rows[0]?.metricValues || []).forEach((v, i) => {{ result[mh[i]] = v.value; }});
    return result;
}}

// Normal CDF for significance calc (Abramowitz & Stegun)
function normCdf(x) {{
    const a1=0.254829592, a2=-0.284496736, a3=1.421413741, a4=-1.453152027, a5=1.061405429, p=0.3275911;
    const sign = x >= 0 ? 1 : -1;
    x = Math.abs(x);
    const t = 1.0 / (1.0 + p * x);
    const y = 1.0 - (((((a5*t + a4)*t) + a3)*t + a2)*t + a1)*t * Math.exp(-x*x/2);
    return 0.5 * (1.0 + sign * y);
}}

function calcSampleSize(baseRate, mde) {{
    const zAlpha = 1.96, zBeta = 0.8416;
    const p1 = baseRate, p2 = Math.max(0.01, baseRate - mde);
    const pBar = (p1 + p2) / 2;
    return Math.ceil(Math.pow(zAlpha * Math.sqrt(2*pBar*(1-pBar)) + zBeta * Math.sqrt(p1*(1-p1)+p2*(1-p2)), 2) / Math.pow(p1-p2, 2));
}}

function calcZTest(nA, rA, nB, rB) {{
    if (nA === 0 || nB === 0) return {{z: 0, p: 1}};
    const pPool = (rA*nA + rB*nB) / (nA+nB);
    if (pPool === 0 || pPool === 1) return {{z: 0, p: 1}};
    const se = Math.sqrt(pPool*(1-pPool)*(1/nA + 1/nB));
    if (se === 0) return {{z: 0, p: 1}};
    const z = (rB - rA) / se;
    return {{z: Math.round(z*1000)/1000, p: Math.round(2*(1-normCdf(Math.abs(z)))*10000)/10000}};
}}

function buildSignificance(gen6, noto) {{
    const gen6s = parseInt(gen6?.sessions || 0);
    const notos = parseInt(noto?.sessions || 0);
    const gen6b = parseFloat(gen6?.bounceRate || 0);
    const notob = parseFloat(noto?.bounceRate || 0);
    const baseBounce = gen6b > 0 ? gen6b : 0.45;
    const reqBounce = calcSampleSize(baseBounce, 0.05);
    const ztBounce = calcZTest(gen6s, gen6b, notos, notob);

    const gen6c = parseInt(gen6?.ecommercePurchases || 0);
    const notoc = parseInt(noto?.ecommercePurchases || 0);
    const gen6cr = gen6s > 0 ? gen6c/gen6s : 0;
    const notocr = notos > 0 ? notoc/notos : 0;
    const baseCr = gen6cr > 0 ? gen6cr : 0.02;
    const reqCr = calcSampleSize(baseCr, 0.01);
    const ztCr = calcZTest(gen6s, gen6cr, notos, notocr);

    return {{
        bounceRate: {{
            gen6_n: gen6s, noto_n: notos, gen6_rate: gen6b, noto_rate: notob,
            required_per_group: reqBounce,
            progress_noto_pct: Math.min(100, Math.round(notos/Math.max(reqBounce,1)*1000)/10),
            progress_gen6_pct: Math.min(100, Math.round(gen6s/Math.max(reqBounce,1)*1000)/10),
            z_score: ztBounce.z, p_value: ztBounce.p,
            is_significant: ztBounce.p < 0.05,
            confidence_pct: ztBounce.p < 1 ? Math.round((1-ztBounce.p)*1000)/10 : 0,
            mde: 0.05, alpha: 0.05, power: 0.80,
        }},
        conversionRate: {{
            gen6_n: gen6s, noto_n: notos, gen6_rate: Math.round(gen6cr*10000)/10000, noto_rate: Math.round(notocr*10000)/10000,
            required_per_group: reqCr,
            progress_noto_pct: Math.min(100, Math.round(notos/Math.max(reqCr,1)*1000)/10),
            z_score: ztCr.z, p_value: ztCr.p,
            is_significant: ztCr.p < 0.05,
            confidence_pct: ztCr.p < 1 ? Math.round((1-ztCr.p)*1000)/10 : 0,
            mde: 0.01, alpha: 0.05, power: 0.80,
        }},
    }};
}}

async function fetchAllClientSide(days) {{
    const token = await getAccessToken();
    if (!token) return null;

    const dateRanges = [{{startDate: days+'daysAgo', endDate: 'today'}}];
    const metrics = GA4_CONFIG.metrics || [];
    const mkFilter = (val) => ({{filter: {{fieldName: 'customUser:ab_theme_variant', stringFilter: {{matchType: 'EXACT', value: val, caseSensitive: true}}}}}});

    // Fetch in batches of 10 metrics (GA4 API limit)
    let gen6 = {{}}, noto = {{}};
    for (let i = 0; i < metrics.length; i += 10) {{
        const batch = metrics.slice(i, i+10);
        const [g, n] = await Promise.all([
            ga4Report(token, dateRanges, batch, mkFilter('GEN-6')),
            ga4Report(token, dateRanges, batch, mkFilter('NOTOAGENCY')),
        ]);
        Object.assign(gen6, parseGA4Rows(g));
        Object.assign(noto, parseGA4Rows(n));
    }}

    // Realtime
    const rtRaw = await ga4Realtime(token);
    const realtime = {{}};
    if (rtRaw?.rows) {{
        rtRaw.rows.forEach(r => {{
            const v = r.dimensionValues?.[0]?.value;
            if (v) realtime[v] = {{
                activeUsers: parseInt(r.metricValues?.[0]?.value || 0),
                eventCount: parseInt(r.metricValues?.[1]?.value || 0),
            }};
        }});
    }}

    const now = new Date();
    const start = new Date(now); start.setDate(start.getDate() - days);

    return {{
        gen6: Object.keys(gen6).length > 0 ? gen6 : null,
        noto: Object.keys(noto).length > 0 ? noto : null,
        realtime,
        significance: buildSignificance(gen6, noto),
        days,
        generated_at: now.toISOString().slice(0,19).replace('T',' '),
        period: {{ start: start.toISOString().slice(0,10), end: now.toISOString().slice(0,10) }},
        metrics_config: GA4_CONFIG.metrics_config || DATA?.metrics_config || [],
    }};
}}

// ======================== Data loading ========================
async function loadData(days) {{
    currentDays = days;
    const btn = document.getElementById('btn-refresh');
    btn.classList.add('loading');
    btn.textContent = 'Ładowanie...';

    try {{
        let data = null;
        if (API_BASE) {{
            // Serve mode: fetch from local backend
            const resp = await fetch(`${{API_BASE}}/api/data?days=${{days}}`);
            data = await resp.json();
        }} else if (GA4_CONFIG.client_id) {{
            // Standalone mode: fetch directly from GA4 API
            data = await fetchAllClientSide(days);
        }}
        if (data) render(data);
        else btn.textContent = 'Błąd — brak danych';
    }} catch (e) {{
        console.error('Fetch error:', e);
        btn.textContent = 'Błąd połączenia';
    }}

    setTimeout(() => {{
        btn.classList.remove('loading');
        btn.textContent = 'Odśwież dane';
    }}, 1500);
}}

function refreshData() {{
    loadData(currentDays);
}}

// Initial render
if (DATA && !DATA.error) {{
    currentDays = DATA.days || 7;
    render(DATA);
}}
</script>
</body>
</html>"""

# =====================================================
# HTTP server for live mode
# =====================================================

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/" or parsed.path == "/index.html":
            initial = fetch_all_data(7)
            html = generate_dashboard_html(json.dumps(initial, ensure_ascii=False), serve_mode=True)
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))

        elif parsed.path == "/api/data":
            params = parse_qs(parsed.query)
            days = int(params.get("days", [7])[0])
            data = fetch_all_data(days)
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        print(f"  [{datetime.now().strftime('%H:%M:%S')}] {args[0]}")

# =====================================================
# CLI
# =====================================================

def run_realtime_check():
    print("  Real-time A/B check...")
    access_token = get_access_token()
    if not access_token:
        return
    data = ga4_realtime(access_token, ["customUser:ab_theme_variant"], ["activeUsers", "eventCount"])
    rows = parse_rows(data) if data else []
    if not rows:
        print("  Brak aktywnych użytkowników z A/B tagiem.")
        return
    for row in rows:
        variant = row.get("customUser:ab_theme_variant", "(not set)")
        users = row.get("activeUsers", "0")
        events = row.get("eventCount", "0")
        print(f"  {variant or '(brak tagu)'}: {users} użytkowników, {events} eventów")

def main():
    days = 7
    serve = False
    realtime = False

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--days" and i + 2 <= len(sys.argv):
            days = int(sys.argv[i + 2])
        elif arg == "--serve":
            serve = True
        elif arg == "--realtime":
            realtime = True
        elif arg.isdigit():
            days = int(arg)

    print("=" * 60)
    print("  A/B THEME REPORT — GenActiv")
    print("  GEN-6 (baseline, 90%) vs NOTOAGENCY (variant, 10%)")
    print("=" * 60)

    if realtime:
        run_realtime_check()
        return

    if serve:
        print(f"\n  Dashboard: http://localhost:{SERVE_PORT}")
        print(f"  API:       http://localhost:{SERVE_PORT}/api/data?days=7")
        print(f"  Ctrl+C aby zatrzymać\n")
        server = HTTPServer(("", SERVE_PORT), DashboardHandler)
        try:
            import webbrowser
            webbrowser.open(f"http://localhost:{SERVE_PORT}")
        except Exception:
            pass
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n  Zatrzymano.")
        return

    # Static HTML generation
    print(f"\n  Generuję raport ({days} dni)...")
    data = fetch_all_data(days)

    output_path = os.path.join(os.path.dirname(__file__), f"ab_theme_report_{days}d.html")
    html = generate_dashboard_html(json.dumps(data, ensure_ascii=False), serve_mode=False)
    with open(output_path, "w") as f:
        f.write(html)
    print(f"  Raport zapisany: {output_path}")

    try:
        import webbrowser
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
    except Exception:
        pass

if __name__ == "__main__":
    main()

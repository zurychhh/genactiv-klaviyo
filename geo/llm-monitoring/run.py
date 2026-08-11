#!/usr/bin/env python3
"""
VIII-A3 · Monitoring cytowań GENACTIV w wyszukiwarkach AI.

Odpytuje silniki AI-search, dla których mamy API (Perplexity, Gemini z groundingiem),
stałym setem zapytań z queries.json i zapisuje: czy GENACTIV jest wymieniony,
czy podany jest link (jaki URL) i jacy konkurenci są cytowani.

Wyłącznie biblioteka standardowa — systemowy python3 nie ma `requests`.

Użycie:
    python3 run.py --dry-run                      # plan bez wywołań API
    python3 run.py --engines perplexity           # tylko Perplexity
    python3 run.py --engines perplexity,gemini    # oba
    python3 run.py --month 2026-08                # nadpisz etykietę miesiąca
    python3 run.py --checklist-only               # sama checklista ręczna

Klucze API (env albo ../../.env):
    PERPLEXITY_API_KEY
    GEMINI_API_KEY
"""

import argparse
import csv
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, OrderedDict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DEFAULT_QUERIES = os.path.join(HERE, "queries.json")
DEFAULT_RESULTS = os.path.join(HERE, "results")

# --- Detekcja -----------------------------------------------------------------
# Wzorce marki — łapią też literówki, które realnie występują w wyszukiwaniach
# (potwierdzone w Google Ads search terms: genaktiv, geneactiv, genativ, gen activ).
BRAND_PATTERNS = [
    r"genactiv",
    r"gen\s+activ",
    r"genaktiv",
    r"geneactiv",
    r"genativ",
]

OUR_DOMAINS = [
    "genactiv.pl",
    "colostrum.pl",
    "genactiv.myshopify.com",
]

# Konkurenci i kategorie źródeł. Klucz = etykieta w raporcie.
COMPETITORS = OrderedDict([
    ("colostrigen", {"text": [r"colostrigen"], "domains": ["colostrigen.pl"]}),
    ("immunolab", {"text": [r"immunolab"], "domains": ["immunolab.pl"]}),
    ("apteki", {"text": [], "domains": [
        "doz.pl", "gemini.pl", "aptekagemini.pl", "ziko.pl", "cefarm24.pl",
        "i-apteka.pl", "apteka-melissa.pl", "aptelia.pl", "superpharm.pl",
        "apteliapharma.pl", "aptekaolmed.pl",
    ]}),
    ("marketplace", {"text": [], "domains": [
        "allegro.pl", "ceneo.pl", "amazon.pl", "empik.com",
    ]}),
    ("portale-zdrowie", {"text": [], "domains": [
        "medonet.pl", "poradnikzdrowie.pl", "wylecz.to", "mp.pl",
        "hellozdrowie.pl", "abczdrowie.pl", "zdrowie.tvn.pl",
    ]}),
])

# --- Silniki ------------------------------------------------------------------
ENGINES = {
    "perplexity": {
        "env": "PERPLEXITY_API_KEY",
        "model": "sonar",
        "url": "https://api.perplexity.ai/chat/completions",
    },
    # UWAGA: modele 2.5 nie są już dostępne dla nowych kluczy ("no longer available
    # to new users"). Grounding wymaga włączonego billingu — na czystym free tierze
    # google_search zwraca 429, choć samo generowanie działa. Szczegóły: KOSZTY_API.md.
    "gemini": {
        "env": "GEMINI_API_KEY",
        "model": "gemini-3.6-flash",
        "url": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
    },
}

MANUAL_ENGINES = ["chatgpt", "ai-overviews"]

USER_AGENT = "genactiv-llm-monitoring/1.0"
REQUEST_TIMEOUT = 90
PAUSE_BETWEEN_CALLS = 1.5


# --- Pomocnicze ---------------------------------------------------------------

def load_dotenv(path):
    """Wczytuje KEY=VALUE z .env do os.environ (nie nadpisuje istniejących)."""
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


def http_post_json(url, payload, headers, timeout=REQUEST_TIMEOUT, retries=3):
    """POST JSON → dict. Ponawia na 429/5xx z backoffem."""
    body = json.dumps(payload).encode("utf-8")
    base_headers = {"Content-Type": "application/json", "User-Agent": USER_AGENT}
    base_headers.update(headers or {})

    last_error = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, headers=base_headers, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:600]
            last_error = "HTTP {}: {}".format(exc.code, detail)
            if exc.code in (429, 500, 502, 503, 504) and attempt < retries - 1:
                wait = 3 * (2 ** attempt)
                sys.stderr.write("   ! {} — ponawiam za {}s\n".format(exc.code, wait))
                time.sleep(wait)
                continue
            raise RuntimeError(last_error)
        except (urllib.error.URLError, TimeoutError) as exc:
            last_error = "URLError: {}".format(exc)
            if attempt < retries - 1:
                time.sleep(3 * (2 ** attempt))
                continue
            raise RuntimeError(last_error)
    raise RuntimeError(last_error or "nieznany błąd")


def resolve_redirect(url, timeout=15):
    """Rozwija redirect (Gemini zwraca linki przez vertexaisearch)."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.geturl()
    except Exception:
        return url


def domain_of(url):
    try:
        netloc = urllib.parse.urlparse(url).netloc.lower()
        return netloc[4:] if netloc.startswith("www.") else netloc
    except Exception:
        return ""


# --- Wywołania silników -------------------------------------------------------

def query_perplexity(query, api_key, model):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": query}],
        "temperature": 0,
    }
    data = http_post_json(
        ENGINES["perplexity"]["url"],
        payload,
        {"Authorization": "Bearer {}".format(api_key)},
    )
    answer = ""
    choices = data.get("choices") or []
    if choices:
        answer = (choices[0].get("message") or {}).get("content") or ""

    urls = []
    for item in data.get("citations") or []:
        if isinstance(item, str):
            urls.append(item)
        elif isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])
    for item in data.get("search_results") or []:
        if isinstance(item, dict) and item.get("url"):
            urls.append(item["url"])

    return {"answer": answer, "urls": urls, "raw": data}


def query_gemini(query, api_key, model, resolve=True):
    url = ENGINES["gemini"]["url"].format(model=model) + "?key=" + urllib.parse.quote(api_key)
    payload = {
        "contents": [{"parts": [{"text": query}]}],
        "tools": [{"google_search": {}}],
        "generationConfig": {"temperature": 0},
    }
    try:
        data = http_post_json(url, payload, {})
    except RuntimeError as exc:
        # Starsze modele używają google_search_retrieval zamiast google_search.
        if "google_search" not in str(exc):
            raise
        payload["tools"] = [{"google_search_retrieval": {}}]
        data = http_post_json(url, payload, {})

    candidates = data.get("candidates") or []
    answer = ""
    urls = []
    if candidates:
        content = candidates[0].get("content") or {}
        answer = "".join(p.get("text", "") for p in content.get("parts") or [])
        grounding = candidates[0].get("groundingMetadata") or {}
        for chunk in grounding.get("groundingChunks") or []:
            web = chunk.get("web") or {}
            raw_url = web.get("uri")
            if not raw_url:
                continue
            # Gemini zwraca redirect przez vertexaisearch — bez rozwinięcia
            # nie da się powiedzieć, JAKI URL został zacytowany.
            urls.append(resolve_redirect(raw_url) if resolve else raw_url)

    return {"answer": answer, "urls": urls, "raw": data}


# --- Analiza ------------------------------------------------------------------

def analyse(answer, urls):
    text = (answer or "").lower()
    domains = [domain_of(u) for u in urls]
    joined_domains = " ".join(domains)

    brand_mentioned = any(re.search(p, text, re.IGNORECASE) for p in BRAND_PATTERNS)

    our_urls = [u for u, d in zip(urls, domains) if any(d == od or d.endswith("." + od) for od in OUR_DOMAINS)]
    brand_in_sources = bool(our_urls) or any(
        re.search(p, joined_domains, re.IGNORECASE) for p in BRAND_PATTERNS
    )

    competitors_found = []
    for name, cfg in COMPETITORS.items():
        hit_text = any(re.search(p, text, re.IGNORECASE) for p in cfg["text"])
        hit_domain = any(
            d == cd or d.endswith("." + cd) for d in domains for cd in cfg["domains"]
        )
        if hit_text or hit_domain:
            competitors_found.append(name)

    return {
        "brand_mentioned": brand_mentioned,
        "brand_linked": bool(our_urls),
        "brand_in_sources": brand_in_sources,
        "our_urls": our_urls,
        "all_urls": urls,
        "domains": domains,
        "competitors": competitors_found,
    }


# --- Raporty ------------------------------------------------------------------

CSV_FIELDS = [
    "data", "silnik", "query_id", "zapytanie", "klaster", "intencja",
    "genactiv_wymieniony", "genactiv_zalinkowany", "nasze_urle",
    "konkurenci", "wszystkie_zrodla", "blad",
]


def write_csv(rows, path):
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _pct(part, whole):
    return "0%" if not whole else "{:.0f}%".format(100.0 * part / whole)


def build_markdown(rows, queries, month, engines_used, errors):
    ok_rows = [r for r in rows if not r["blad"]]
    total = len(ok_rows)
    mentioned = sum(1 for r in ok_rows if r["genactiv_wymieniony"] == "TAK")
    linked = sum(1 for r in ok_rows if r["genactiv_zalinkowany"] == "TAK")

    lines = []
    lines.append("# Monitoring cytowań GENACTIV w wyszukiwarkach AI — {}".format(month))
    lines.append("")
    lines.append("**Wygenerowano:** {}".format(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")))
    lines.append("**Silniki (API):** {}".format(", ".join(engines_used) if engines_used else "brak"))
    lines.append("**Zapytań w secie:** {}".format(len(queries)))
    lines.append("**Udanych odpytań:** {} / {}".format(total, len(rows)))
    lines.append("")

    lines.append("## Pokrycie ogółem")
    lines.append("")
    lines.append("| Metryka | Wartość | Udział |")
    lines.append("|---|---|---|")
    lines.append("| GENACTIV wymieniony w odpowiedzi | {} | {} |".format(mentioned, _pct(mentioned, total)))
    lines.append("| GENACTIV z linkiem w źródłach | {} | {} |".format(linked, _pct(linked, total)))
    lines.append("")

    # Per silnik
    lines.append("## Per silnik")
    lines.append("")
    lines.append("| Silnik | Odpytań | Wymieniony | Zalinkowany |")
    lines.append("|---|---|---|---|")
    for engine in engines_used:
        sub = [r for r in ok_rows if r["silnik"] == engine]
        m = sum(1 for r in sub if r["genactiv_wymieniony"] == "TAK")
        l = sum(1 for r in sub if r["genactiv_zalinkowany"] == "TAK")
        lines.append("| {} | {} | {} ({}) | {} ({}) |".format(
            engine, len(sub), m, _pct(m, len(sub)), l, _pct(l, len(sub))))
    lines.append("")

    # Per klaster
    lines.append("## Per klaster")
    lines.append("")
    lines.append("| Klaster | Odpytań | Wymieniony | Zalinkowany |")
    lines.append("|---|---|---|---|")
    for cluster in sorted({r["klaster"] for r in ok_rows}):
        sub = [r for r in ok_rows if r["klaster"] == cluster]
        m = sum(1 for r in sub if r["genactiv_wymieniony"] == "TAK")
        l = sum(1 for r in sub if r["genactiv_zalinkowany"] == "TAK")
        lines.append("| {} | {} | {} ({}) | {} ({}) |".format(
            cluster, len(sub), m, _pct(m, len(sub)), l, _pct(l, len(sub))))
    lines.append("")

    # Top cytowane domeny
    lines.append("## Top cytowane źródła")
    lines.append("")
    counter = Counter()
    for row in ok_rows:
        for url in (row["wszystkie_zrodla"] or "").split(" | "):
            dom = domain_of(url)
            if dom:
                counter[dom] += 1
    if counter:
        lines.append("| Domena | Cytowań | Nasza? |")
        lines.append("|---|---|---|")
        for dom, count in counter.most_common(25):
            ours = "TAK" if any(dom == od or dom.endswith("." + od) for od in OUR_DOMAINS) else ""
            lines.append("| {} | {} | {} |".format(dom, count, ours))
    else:
        lines.append("_Brak zebranych źródeł._")
    lines.append("")

    # Konkurencja
    lines.append("## Konkurenci / kategorie źródeł")
    lines.append("")
    comp_counter = Counter()
    for row in ok_rows:
        for name in (row["konkurenci"] or "").split(", "):
            if name:
                comp_counter[name] += 1
    if comp_counter:
        lines.append("| Kategoria | Wystąpień | Udział odpytań |")
        lines.append("|---|---|---|")
        for name, count in comp_counter.most_common():
            lines.append("| {} | {} | {} |".format(name, count, _pct(count, total)))
    else:
        lines.append("_Brak wykrytych konkurentów._")
    lines.append("")

    # Luki — najważniejsza sekcja operacyjna
    lines.append("## Luki — zapytania bez GENACTIV")
    lines.append("")
    gaps = [r for r in ok_rows if r["genactiv_wymieniony"] == "NIE"]
    if gaps:
        lines.append("| ID | Zapytanie | Klaster | Silnik | Kto zamiast nas |")
        lines.append("|---|---|---|---|---|")
        for row in gaps:
            lines.append("| {} | {} | {} | {} | {} |".format(
                row["query_id"], row["zapytanie"], row["klaster"],
                row["silnik"], row["konkurenci"] or "—"))
    else:
        lines.append("_Brak luk — GENACTIV wymieniony we wszystkich odpytaniach._")
    lines.append("")

    if errors:
        lines.append("## Błędy odpytań")
        lines.append("")
        for err in errors:
            lines.append("- `{}` / `{}` → {}".format(err["silnik"], err["query_id"], err["blad"]))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("**Metodyka:** patrz `geo/llm-monitoring/README.md`. ")
    lines.append("Set zapytań jest stały — porównywalność miesiąc do miesiąca zależy od niezmieniania brzmienia zapytań.")
    lines.append("")
    return "\n".join(lines)


def build_manual_checklist(queries, month):
    """Checklista dla silników bez API — ChatGPT i Google AI Overviews."""
    lines = []
    lines.append("# Checklista ręczna — ChatGPT i Google AI Overviews · {}".format(month))
    lines.append("")
    lines.append("Ten sam set zapytań co automat, ta sama tabela — żeby wyniki dało się zestawić.")
    lines.append("")
    lines.append("## Jak wypełnić")
    lines.append("")
    lines.append("1. **Nowa sesja / tryb incognito.** Bez zalogowania i bez historii — personalizacja zaburza wynik.")
    lines.append("2. **Lokalizacja: Polska, język polski.** W ChatGPT włącz wyszukiwanie w sieci.")
    lines.append("3. Wklej zapytanie **dosłownie** — bez dopisków i doprecyzowań.")
    lines.append("4. Dla AI Overviews: wpisz zapytanie w Google i sprawdź, czy pojawia się blok AI. Jeśli nie ma bloku → `brak AIO`.")
    lines.append("5. Uzupełnij wiersz. `Wymieniony` = marka pada w treści odpowiedzi. `Zalinkowany` = jest klikalne źródło z genactiv.pl.")
    lines.append("6. Jedna osoba robi cały pomiar tego samego dnia — inaczej porównywalność siada.")
    lines.append("")
    lines.append("Data pomiaru: `____-__-__`  ·  Wykonał(a): `____________`")
    lines.append("")

    for engine in MANUAL_ENGINES:
        label = "ChatGPT (z wyszukiwaniem)" if engine == "chatgpt" else "Google AI Overviews"
        lines.append("## {}".format(label))
        lines.append("")
        lines.append("| ID | Zapytanie | Wymieniony? | Zalinkowany? | Jaki URL | Konkurenci w odpowiedzi | Uwagi |")
        lines.append("|---|---|---|---|---|---|---|")
        for q in queries:
            lines.append("| {} | {} | ☐ TAK ☐ NIE | ☐ TAK ☐ NIE |  |  |  |".format(q["id"], q["query"]))
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("Po wypełnieniu przenieś dane do `report.csv` tego miesiąca (kolumny jak w automacie),")
    lines.append("żeby raport zbiorczy liczył pokrycie na wszystkich czterech silnikach.")
    lines.append("")
    return "\n".join(lines)


# --- Main ---------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Monitoring cytowań GENACTIV w AI-search")
    parser.add_argument("--queries", default=DEFAULT_QUERIES, help="ścieżka do queries.json")
    parser.add_argument("--engines", default="perplexity,gemini", help="perplexity,gemini")
    parser.add_argument("--month", default=None, help="etykieta miesiąca, domyślnie bieżący (YYYY-MM)")
    parser.add_argument("--out", default=DEFAULT_RESULTS, help="katalog wyników")
    parser.add_argument("--dry-run", action="store_true", help="pokaż plan, nie wywołuj API")
    parser.add_argument("--checklist-only", action="store_true", help="tylko checklista ręczna")
    parser.add_argument("--no-resolve", action="store_true", help="nie rozwijaj redirectów Gemini")
    args = parser.parse_args()

    load_dotenv(os.path.join(REPO_ROOT, ".env"))

    with open(args.queries, "r", encoding="utf-8") as fh:
        spec = json.load(fh)
    queries = spec["queries"]
    month = args.month or datetime.now().strftime("%Y-%m")

    out_dir = os.path.join(args.out, month)
    os.makedirs(os.path.join(out_dir, "raw"), exist_ok=True)

    # Checklista ręczna jest niezależna od API — generujemy zawsze.
    checklist_path = os.path.join(out_dir, "manual-checklist.md")
    with open(checklist_path, "w", encoding="utf-8") as fh:
        fh.write(build_manual_checklist(queries, month))
    print("Checklista ręczna: {}".format(checklist_path))
    if args.checklist_only:
        return 0

    requested = [e.strip() for e in args.engines.split(",") if e.strip()]
    available, missing = [], []
    for engine in requested:
        if engine not in ENGINES:
            sys.stderr.write("Nieznany silnik: {}\n".format(engine))
            return 2
        if os.environ.get(ENGINES[engine]["env"]):
            available.append(engine)
        else:
            missing.append((engine, ENGINES[engine]["env"]))

    print("\nSet zapytań: {} ({})".format(len(queries), spec.get("_meta", {}).get("version", "?")))
    print("Miesiąc: {}".format(month))
    print("Silniki z kluczem: {}".format(", ".join(available) or "BRAK"))
    for engine, env_var in missing:
        print("Silnik POMINIĘTY: {} — brak {}".format(engine, env_var))

    if args.dry_run:
        print("\n--dry-run: {} wywołań API do wykonania.".format(len(available) * len(queries)))
        for q in queries[:5]:
            print("   {} [{}] {}".format(q["id"], q["cluster"], q["query"]))
        if len(queries) > 5:
            print("   … i {} więcej".format(len(queries) - 5))
        return 0

    if not available:
        print("\nBrak kluczy API — wygenerowano wyłącznie checklistę ręczną.")
        print("Ustaw PERPLEXITY_API_KEY i/lub GEMINI_API_KEY w .env i uruchom ponownie.")
        return 0

    rows, errors = [], []
    today = datetime.now().strftime("%Y-%m-%d")
    total_calls = len(available) * len(queries)
    done = 0

    for engine in available:
        cfg = ENGINES[engine]
        api_key = os.environ[cfg["env"]]
        print("\n=== {} ({}) ===".format(engine, cfg["model"]))

        for q in queries:
            done += 1
            print("[{}/{}] {} {}".format(done, total_calls, q["id"], q["query"][:60]))

            row = {
                "data": today,
                "silnik": engine,
                "query_id": q["id"],
                "zapytanie": q["query"],
                "klaster": q["cluster"],
                "intencja": q["intent"],
                "genactiv_wymieniony": "",
                "genactiv_zalinkowany": "",
                "nasze_urle": "",
                "konkurenci": "",
                "wszystkie_zrodla": "",
                "blad": "",
            }

            try:
                if engine == "perplexity":
                    result = query_perplexity(q["query"], api_key, cfg["model"])
                else:
                    result = query_gemini(q["query"], api_key, cfg["model"], resolve=not args.no_resolve)

                raw_path = os.path.join(out_dir, "raw", "{}_{}.json".format(engine, q["id"]))
                with open(raw_path, "w", encoding="utf-8") as fh:
                    json.dump(result["raw"], fh, ensure_ascii=False, indent=2)

                found = analyse(result["answer"], result["urls"])
                row["genactiv_wymieniony"] = "TAK" if found["brand_mentioned"] else "NIE"
                row["genactiv_zalinkowany"] = "TAK" if found["brand_linked"] else "NIE"
                row["nasze_urle"] = " | ".join(found["our_urls"])
                row["konkurenci"] = ", ".join(found["competitors"])
                row["wszystkie_zrodla"] = " | ".join(found["all_urls"])

                flag = "✓" if found["brand_mentioned"] else "·"
                print("   {} wymieniony={} link={} konkurenci={}".format(
                    flag, row["genactiv_wymieniony"], row["genactiv_zalinkowany"],
                    row["konkurenci"] or "—"))

            except Exception as exc:  # noqa: BLE001 — chcemy dokończyć pomiar mimo błędu
                row["blad"] = str(exc)[:300]
                errors.append({"silnik": engine, "query_id": q["id"], "blad": row["blad"]})
                print("   BŁĄD: {}".format(row["blad"][:120]))

            rows.append(row)
            time.sleep(PAUSE_BETWEEN_CALLS)

    csv_path = os.path.join(out_dir, "report.csv")
    md_path = os.path.join(out_dir, "report.md")
    write_csv(rows, csv_path)
    with open(md_path, "w", encoding="utf-8") as fh:
        fh.write(build_markdown(rows, queries, month, available, errors))

    ok = [r for r in rows if not r["blad"]]
    mentioned = sum(1 for r in ok if r["genactiv_wymieniony"] == "TAK")
    print("\n" + "=" * 60)
    print("Odpytań udanych: {}/{}".format(len(ok), len(rows)))
    print("GENACTIV wymieniony: {} ({})".format(mentioned, _pct(mentioned, len(ok))))
    print("CSV:       {}".format(csv_path))
    print("Markdown:  {}".format(md_path))
    print("Checklista:{}".format(checklist_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""
Tablica sprintów (kanban) — Genactiv.pl, CZERWIEC 2026.
Pełny plan operacyjny tydzień-po-tygodniu. Regeneracja: `python3 build_sprint_june.py`.
"""
import html
OUT = "sprint-czerwiec-2026.html"

WEEKS = [
    {"id": "W1", "label": "Tydzień 1", "dates": "1–7 cze (pon–niedz)", "focus": "Setup, audyty, research"},
    {"id": "W2", "label": "Tydzień 2", "dates": "8–14 cze", "focus": "Start egzekucji: fixy, silniki"},
    {"id": "W3", "label": "Tydzień 3", "dates": "15–21 cze", "focus": "Launch: A/B layout + flows + treści"},
    {"id": "W4", "label": "Tydzień 4", "dates": "22–28 cze", "focus": "Skalowanie + cadence"},
    {"id": "W5", "label": "Domknięcie", "dates": "29–30 cze", "focus": "Review + handoff do lipca"},
]

STREAMS = {
    "A": ("SEO / Organic", "#0066CC"),
    "B": ("Konwersja (CRO)", "#EF3340"),
    "C": ("Klaviyo / Email", "#8b5cf6"),
    "D": ("Retencja / LTV", "#27ae60"),
    "E": ("Automatyzacja / LP", "#f59e0b"),
    "OPS": ("Operacje / Review", "#1A3B5D"),
}
BOT = {"cc": ("CC", "Claude Code", "#0066CC"),
       "hy": ("CC+", "Hybryda (Claude Code + człowiek)", "#8b5cf6"),
       "hu": ("MAN", "Ręcznie / specjalista", "#6b7280")}
PRI = {"P1": "#EF3340", "P2": "#f59e0b", "P3": "#9ca3af"}

def T(id, week, stream, title, owner, pri, est, kpi, dep, dod, prompt=None):
    return {"id": id, "week": week, "stream": stream, "title": title, "owner": owner,
            "pri": pri, "est": est, "kpi": kpi, "dep": dep, "dod": dod, "prompt": prompt}

TASKS = [
 # ---------------- WEEK 1 ----------------
 T("A1","W1","A","Keyword research top 20 PDP + gap analysis (Colostrigen, Immuno Lab) + mapa sezonowa fraz",
   "hy","P1","8h","enabler (cały stream A)","—",
   "Mapa fraz primary+secondary per top 20 PDP; lista luk vs 2 konkurentów; tag sezonowy (odporność=jesień/zima). Zapis: research/keyword-map-2026.csv.",
   "W Claude Code: użyj senuto-mcp (domain=genactiv.pl, country_id=200, fetch_mode=topLevelDomain) — pobierz frazy dla top 20 produktów po sesjach z GA4. Dla każdej frazy: volume, pozycja, trudność. Zrób gap analysis vs colostrigen.pl i immunolab — frazy gdzie oni są w TOP10 a my nie. Otaguj frazy sezonowo (odporność=Q4/Q1). Wynik zapisz jako research/keyword-map-2026.csv (kolumny: pdp_url, primary_kw, secondary_kw, volume, our_pos, comp_gap, season)."),
 T("A2","W1","A","Pull SEO audit + plan bulk-fix (338 alt, 59 meta titles, 18 meta desc)",
   "cc","P1","4h","enabler (SEO health)","—",
   "Eksport audytu z Shopify Extended; lista fixów z priorytetem; dry-run gotowy do odpalenia w W2.",
   "W Claude Code: odpal SEO audit z shopify-mcp-extended (scope=all). Wyeksportuj listę: obrazy bez alt (338), produkty bez meta title (59), bez meta description (18). Pogrupuj per typ i przygotuj payloady do bulk-update-seo (pamiętaj limit 25 items/wywołanie, użyj dry-run). NIE wykonuj jeszcze zapisu — tylko dry-run i raport co zostanie zmienione. Zapisz plan jako research/seo-fix-plan.md."),
 T("E1","W1","E","Spec review LP Generatora + test integracji Shopify Pages API + schema design",
   "cc","P1","6h","enabler (throughput A+B)","—",
   "Config JSON schema zatwierdzony; auth Pages API działa; 1 strona testowa zdeployowana i edytowalna w panelu Shopify.",
   "W Claude Code: na bazie docs/MIGRATION_PLAN_ONLINE.md i sekcji LP Generator zweryfikuj config schema (lp_type, hero, sections[], seo, tracking). Przetestuj shopify_theme_api.py / Shopify Pages API: utwórz testową stronę /pages/lp-test z 1 sekcją hero, potwierdź że jest edytowalna w panelu Shopify (Online Store → Pages). Zwróć: status auth, ID strony, link, checklist co działa/co brakuje."),
 T("B1","W1","B","Mobile UX audit — start + instalacja heatmap (Hotjar/Clarity)",
   "hy","P1","5h","enabler (CRO mobile)","—",
   "Hotjar/Clarity live na aktywnym theme (GEN-6, ID 162539340108); nagrania startują; framework audytu (checklist mobile).",
   "W Claude Code: wstaw snippet Microsoft Clarity do aktywnego theme przez shopify_theme_api.py (theme ID 162539340108) — najlepiej do layout/theme.liquid przed </head>, z backupem przed zmianą (komenda backup). Potwierdź instalację i zwróć link do podglądu. Część analityczną (audyt UX) robi specjalista CRO ręcznie."),
 T("C1","W1","C","Setup segmentacji RFM w Klaviyo + szkielety copy kampanii",
   "cc","P1","4h","enabler (email rev.)","—",
   "Segmenty RFM utworzone (champions, loyal, potential, at-risk, hibernating) z baseline liczebności; 3 szablony copy gotowe.",
   "W Claude Code: przez klaviyo-mcp utwórz segmenty RFM na bazie historii zamówień: Champions (recent+często+dużo), Loyal, Potential Loyalist, At-Risk, Hibernating, New. Zwróć liczebność każdego segmentu (baseline). Dodatkowo wygeneruj 3 szablony copy PL (newsletter edukacyjny, promo, restock) z {{ first_name|default:\"\" }} i {% unsubscribe 'Anuluj subskrypcję' %}."),
 T("D1","W1","D","Research subskrypcji (Recharge/Bold/Skio) — shortlist + analiza kohort/hard userów",
   "hu","P1","4h","enabler (subskrypcja VII)","—",
   "Matryca porównawcza 3 apek (cena, funkcje, fit Shopify/Przelewy24, PL); rekomendacja 1 narzędzia; baseline retencji kohort. Decyzja do 1.07.",
   None),

 # ---------------- WEEK 2 ----------------
 T("A3","W2","A","Bulk fix alt textów (338) przez MCP",
   "cc","P1","3h","organic indexation · +PLN 1–2K","A2",
   "100% pokrycia alt text; potwierdzone ponownym audytem; brak regresji.",
   "W Claude Code: wykonaj plan z research/seo-fix-plan.md dla alt textów. Generuj alt opisowo z nazwy produktu + kontekstu (PL, naturalne, z frazą gdy sensowne, bez keyword stuffing). Wykonuj bulk-update-seo partiami po 25, najpierw dry-run potem zapis. Po zakończeniu odpal ponowny audyt i potwierdź 100% pokrycia. Raport: ile zmieniono, przed/po."),
 T("A4","W2","A","Content/Copy engine v1 + generacja 1. partii (20–30 artykułów draft)",
   "cc","P1","ciągłe","content velocity (SEO)","A1, E2",
   "Engine generuje artykuł z briefu+frazy (struktura H2/H3, schema FAQ, meta); 20–30 draftów w kolejce do QA medycznego.",
   "W Claude Code: zbuduj content engine — funkcja: input(primary_kw, secondary_kw[], intent, produkt_powiązany) → output(tytuł SEO, meta description, artykuł 800–1200 słów PL z H2/H3, sekcja FAQ ze schema, wewnętrzne linki do PDP, CTA). Źródło fraz: research/keyword-map-2026.csv (tag season). Wygeneruj 20–30 draftów dla fraz odpornościowych (sezon Q4 — publikujemy latem, by zrankować przed jesienią). Zapisz do research/content-drafts/. NIE publikuj — czekają na QA medyczne (A6)."),
 T("E2","W2","E","LP Generator v1 — szablony Liquid (product LP + condition LP)",
   "cc","P1","10h","enabler (LP throughput)","E1",
   "2 szablony renderują się z configu, deploy via Pages API, output w pełni edytowalny w panelu Shopify; zgodne z brand guidelines.",
   "W Claude Code: zaimplementuj 2 szablony LP Generatora (Liquid): (1) product LP, (2) condition LP. Sekcje: hero, benefits_grid, product_showcase, testimonials (judge_me), faq (+schema), content_block, cta_banner. Kolory brand: #0066CC, CTA #EF3340, font Branding-medium. Deploy przez Pages API. Warunek krytyczny: po deployu strona MUSI być edytowalna w Shopify Pages (nie hardkoduj tak, by blokować edycję). Test: postaw /pages/colostrum-na-odpornosc i potwierdź edytowalność."),
 T("B2","W2","B","Mobile UX audit — raport + top 3 drop-off + hipotezy A/B layoutu",
   "hu","P1","6h","enabler (A/B layout)","B1",
   "Raport z 3 zpriorytetyzowanymi problemami mobile + hipotezy nowego layoutu + metryka sukcesu (CR mobile) + mockup wariantu.",
   None),
 T("C2","W2","C","Build Post-Purchase flow (2 maile: thank you + cross-sell)",
   "hy","P1","6h","email rev. +PLN 4K","C1",
   "Flow live w Klaviyo; mail 1 (thank you, T+0) i mail 2 (cross-sell powiązanych kategorii, T+5); przetestowane na profilu testowym.",
   "W Claude Code: przez klaviyo-mcp zbuduj Post-Purchase flow wyzwalany 'Placed Order'. Mail 1 (delay 0): podziękowanie + jak stosować produkt (edukacja, retencja). Mail 2 (delay 5 dni): cross-sell — jeśli kupił colostrum, poleć fiberbiom i odwrotnie (event.ProductName warunkowo). Pełny HTML inline CSS, max 600px, {% unsubscribe 'Anuluj subskrypcję' %}. Obrazy najpierw upload przez klaviyo_upload_image_from_url. Copy PL dopisuje/zatwierdza człowiek przed włączeniem."),

 # ---------------- WEEK 3 ----------------
 T("A5","W3","A","Bulk fix meta titles (59) + meta descriptions (18)",
   "cc","P1","3h","organic CR · +PLN 2K","A1, A2",
   "≥95% pokrycia meta title/desc; zweryfikowane audytem; tytuły z frazą primary + brand, desc z CTA.",
   "W Claude Code: dokończ research/seo-fix-plan.md — meta titles (59) i descriptions (18). Tytuł: [Primary KW] — [benefit] | GenActiv (≤60 zn.), frazy z keyword-map-2026.csv. Desc: ≤155 zn., z CTA i frazą. Bulk-update-seo partiami po 25, dry-run → zapis. Ponowny audyt na potwierdzenie ≥95%."),
 T("A6","W3","A","QA medyczne fala 1 (30 artykułów) + publikacja + zgłoszenie do GSC",
   "hy","P1","ciągłe","organic sessions · +PLN 3K","A4",
   "30 artykułów po QA medycznym (poprawność, zgodność z claimami suplementowymi PL), opublikowanych na blogu, sitemap zaktualizowany, URLe zgłoszone w Google Search Console.",
   "W Claude Code: po akceptacji medycznej opublikuj zatwierdzone artykuły z research/content-drafts/ na blog Shopify (Pages/Blog API), z meta+schema. Zaktualizuj sitemap. Wygeneruj listę URLi do ręcznego zgłoszenia w GSC. Człowiek robi QA medyczne PRZED tym krokiem (zgodność z dozwolonymi oświadczeniami)."),
 T("B3","W3","B","▶ Build + launch A/B testu NOWEGO LAYOUTU (homepage + PDP, mobile-first)",
   "hy","P1","12h","CR mobile +0,3–0,5pp · +PLN 8K","B2, E1",
   "Test A/B live (split 50/50); wariant: sticky ATC mobile + trust badges + nowy układ above-the-fold; tracking w GA4 + narzędziu; min. próbka i czas trwania ustalone (≥2 tyg.).",
   "W Claude Code: zbuduj wariant B layoutu wg hipotez z raportu B2 (sticky Add-to-Cart na mobile, trust badges pod ceną, przebudowa above-the-fold). Zaimplementuj jako theme variant lub przez narzędzie A/B. Skonfiguruj split 50/50, event GA4 na purchase per wariant. Zwróć link podglądu obu wariantów + jak czytać wyniki. Analiza istotności = specjalista CRO."),
 T("C3","W3","C","Build Win-Back flow (90-dni nieaktywni)",
   "hy","P2","4h","email rev. + reaktywacja","C1",
   "Flow live; segment 90-day inactive; 2 maile (przypomnienie + zachęta/oferta); przetestowane.",
   "W Claude Code: przez klaviyo-mcp zbuduj Win-Back flow dla segmentu 'nie kupił od 90 dni'. Mail 1: 'tęsknimy' + przypomnienie wartości produktu. Mail 2 (T+4): zachęta (mały rabat lub bestseller). HTML inline, unsubscribe. Copy zatwierdza człowiek."),
 T("D2","W3","D","Audyt bundli + utworzenie 3 zestawów (colostrum+fiberbiom, family, starter)",
   "hy","P2","6h","AOV + items/order · +PLN 4K","D1",
   "3 bundle live z ceną pakietową; widoczne w kolekcji i jako cross-sell na PDP; nazwy i opisy PL.",
   "W Claude Code: utwórz 3 produkty-bundle w Shopify (przez Shopify MCP/GraphQL): (1) Colostrum + Fiberbiom (gut+odporność), (2) Family Pack, (3) Starter Kit. Ustaw cenę pakietową (rabat vs suma składowych), opis PL, tagi. Człowiek zatwierdza ceny/marżę. Dodaj jako rekomendację na powiązanych PDP."),

 # ---------------- WEEK 4 ----------------
 T("A7","W4","A","Generacja + QA fala 2 (do 60–100 łącznie) + start programmatic /colostrum-na-[stan]",
   "hy","P1","ciągłe","content velocity · +PLN 3–5K","A4, A6",
   "Łącznie 60–100 artykułów opublikowanych w czerwcu; szablon programmatic gotowy; pierwsze 10 stron condition wygenerowanych.",
   "W Claude Code: wygeneruj 2. falę artykułów (do łącznie 60–100), QA medyczne falami, publikuj. Dodatkowo zbuduj programmatic generator: dla listy stanów (odporność, przeziębienie, jelita, energia, dzieci, seniorzy...) generuj /pages/colostrum-na-[stan] z content_block + FAQ schema + powiązane produkty. Wygeneruj pierwsze 10. Pilnuj unikalności (nie duplikuj treści)."),
 T("C4","W4","C","Cadence kampanii 2×/tydzień + segmentacja per zainteresowanie produktem",
   "hy","P1","4h","campaign rev. +PLN 4K","C1",
   "Kalendarz kampanii 2×/tydz. na resztę czerwca i lipiec; kampanie targetowane per segment/kategoria; pierwsze 2 wysłane.",
   "W Claude Code: zaplanuj kalendarz 2 kampanii/tydzień (klaviyo-mcp). Segmentuj per zainteresowanie (kupujący colostrum vs fiberbiom). Przygotuj pierwsze 2 kampanie z copy z szablonów C1. Wysyłkę/akceptację potwierdza człowiek. Pamiętaj: campaign_report wymaga conversion_metric_id."),
 T("E3","W4","E","Integracja content/LP engine z auto-SEO checklist + QA",
   "cc","P2","6h","LP/artykuł jakość","E2, A4",
   "Generowane LP i artykuły automatycznie dostają poprawne meta/schema/OG; QA checklist przechodzi w 100%; brak błędów walidacji schema.",
   "W Claude Code: dodaj warstwę auto-SEO do content/LP engine: automatyczne meta title/description, JSON-LD (Product/FAQPage/BreadcrumbList), OG tags, canonical. Dodaj walidację schema (rich results test). Uruchom na wygenerowanych dotąd LP/artykułach i napraw błędy. Raport: ile assetów, ile błędów schema naprawiono."),
 T("B4","W4","B","Monitoring A/B (odczyt interim) + page speed quick wins",
   "hy","P2","4h","CR mobile (w toku)","B3",
   "Interim read testu (kierunek + czy zbliżamy się do istotności); lista quick-win speed (obrazy, lazy load) wdrożona jeśli bezpieczna.",
   "W Claude Code: zrób audyt Core Web Vitals strony (LCP/CLS/INP) i przygotuj listę quick-winów (WebP, lazy load, defer skryptów). Wdroż bezpieczne zmiany przez theme API z backupem. Interim read A/B (kierunek) — pełna decyzja w lipcu, robi CRO."),
 T("D3","W4","D","Decyzja narzędzia subskrypcji + start konfiguracji (pod launch lipcowy)",
   "hu","P1","4h","enabler (subskrypcja VII)","D1",
   "Apka subskrypcyjna wybrana (do 1.07) i zainstalowana; konfiguracja produktów top 3 rozpoczęta; plan launchu na lipiec.",
   None),

 # ---------------- W5 CLOSEOUT ----------------
 T("OPS1","W5","OPS","Snapshot KPI czerwca + raport co dowieziono vs plan",
   "cc","P1","3h","governance","wszystkie",
   "Snapshot z MCP: CR overall/mobile, organic sessions, lista email, email revenue, # artykułów, status A/B; tabela plan vs realizacja; lista przeniesień do lipca.",
   "W Claude Code: pobierz z MCP snapshot na koniec czerwca: GA4 (sesje, CR overall/mobile, organic sessions), Shopify (przychód, zamówienia, AOV), Klaviyo (lista, flow/campaign revenue). Zestaw z baseline i targetem. Wygeneruj reports/czerwiec-2026-review.md: plan vs realizacja per zadanie + KPI delta + co przechodzi na lipiec."),
 T("OPS2","W5","OPS","Handoff do lipca: decyzja A/B, gotowość subskrypcji, lock content velocity",
   "hu","P1","2h","governance","B4, D3, A7",
   "Decyzja: wdrożyć/iterować wariant layoutu; subskrypcja gotowa do launchu 1–7 lipca; ustalone tempo treści na lipiec (≥40 art.).",
   None),
]

def esc(s): return html.escape(str(s), quote=True)

def card(t):
    sc = STREAMS[t["stream"]]
    b = BOT[t["owner"]]
    h = f'<div class="card" style="--ac:{sc[1]}">'
    h += f'<div class="crow"><span class="sid">{t["stream"]}</span><span class="cid">{esc(t["id"])}</span>'
    h += f'<span class="pri" style="background:{PRI[t["pri"]]}">{t["pri"]}</span>'
    h += f'<span class="bot" style="background:{b[2]}" title="{esc(b[1])}">{b[0]}</span></div>'
    h += f'<div class="ctitle">{esc(t["title"])}</div>'
    h += f'<div class="cmeta"><span>⏱ {esc(t["est"])}</span><span class="kpi">↑ {esc(t["kpi"])}</span></div>'
    h += f'<div class="cdep">⛓ zależy od: {esc(t["dep"])}</div>'
    h += f'<details><summary>Definition of Done {"+ prompt CC" if t["prompt"] else ""}</summary>'
    h += f'<p class="dod"><b>DoD:</b> {esc(t["dod"])}</p>'
    if t["prompt"]:
        h += f'<div class="prompt"><div class="plab">▷ Prompt do Claude Code</div><code>{esc(t["prompt"])}</code></div>'
    h += '</details></div>'
    return h

def build():
    H = [f'''<!DOCTYPE html><html lang="pl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Sprint Czerwiec 2026 — Genactiv.pl (operacyjnie)</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
:root{{--blue:#0066CC;--blue-dk:#1A3B5D;--red:#EF3340;--green:#27ae60;--ink:#15202b;--ink-2:#4a5663;--ink-3:#8a94a0;--paper:#f6f8fb;--card:#fff;--line:#e3e9f0;--line-2:#eef2f7}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ink);background:var(--paper);font-size:15px;line-height:1.5;-webkit-font-smoothing:antialiased}}
.serif{{font-family:'Fraunces',Georgia,serif;letter-spacing:-.015em}}
.mono{{font-family:'JetBrains Mono',monospace}}
.wrap{{max-width:1640px;margin:0 auto;padding:0 24px}}
.hero{{background:linear-gradient(135deg,#0b1f33,#0066CC 120%);color:#fff;padding:40px 0 34px}}
.hero h1{{font-size:2.1rem;font-weight:700}}
.hero .sub{{font-size:.98rem;color:rgba(255,255,255,.85);max-width:80ch;margin-top:10px}}
.hero .pills{{display:flex;gap:9px;flex-wrap:wrap;margin-top:16px}}
.pill{{background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);padding:5px 12px;border-radius:999px;font-size:.74rem;font-weight:600}}
.legend{{display:flex;gap:14px;flex-wrap:wrap;padding:16px 0;font-size:.73rem;color:var(--ink-2);align-items:center}}
.legend .tagb{{font-family:'JetBrains Mono',monospace;font-size:.58rem;font-weight:700;color:#fff;border-radius:4px;padding:2px 6px}}
.legend .sdot{{width:12px;height:12px;border-radius:3px;display:inline-block;vertical-align:middle;margin-right:4px}}
.toolbar{{display:flex;gap:10px;margin:6px 0 16px}}
.btn{{background:var(--blue);color:#fff;border:none;border-radius:8px;padding:7px 14px;font-size:.78rem;font-weight:600;cursor:pointer;font-family:inherit}}
.btn.sec{{background:#fff;color:var(--blue);border:1px solid var(--blue)}}
.board{{display:flex;gap:14px;overflow-x:auto;padding-bottom:20px;align-items:flex-start}}
.col{{flex:0 0 320px;background:#eef2f7;border-radius:14px;padding:12px}}
.col.closeout{{background:#eaf3fb;flex-basis:300px}}
.colhead{{margin-bottom:12px}}
.colhead .wk{{font-family:'Fraunces',serif;font-weight:600;font-size:1.05rem}}
.colhead .dt{{font-size:.72rem;color:var(--ink-3);font-weight:600}}
.colhead .fc{{font-size:.72rem;color:var(--blue);font-weight:600;margin-top:3px}}
.colhead .cnt{{float:right;background:#fff;border:1px solid var(--line);border-radius:999px;font-size:.64rem;font-weight:700;color:var(--ink-2);padding:2px 8px}}
.card{{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--ac);border-radius:10px;padding:11px;margin-bottom:10px}}
.crow{{display:flex;gap:5px;align-items:center;margin-bottom:6px}}
.sid{{width:18px;height:18px;border-radius:5px;background:var(--ac);color:#fff;font-size:.62rem;font-weight:700;display:grid;place-items:center;font-family:'JetBrains Mono',monospace}}
.cid{{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:var(--ink-3);font-weight:600}}
.crow .pri,.crow .bot{{font-family:'JetBrains Mono',monospace;font-size:.56rem;font-weight:700;color:#fff;border-radius:4px;padding:1px 5px;margin-left:auto}}
.crow .bot{{margin-left:3px}}
.ctitle{{font-weight:600;font-size:.82rem;line-height:1.3;margin-bottom:7px}}
.cmeta{{display:flex;gap:6px;flex-wrap:wrap;font-size:.66rem;margin-bottom:5px}}
.cmeta span{{background:var(--line-2);border-radius:5px;padding:2px 7px;color:var(--ink-2);font-weight:600}}
.cmeta .kpi{{background:#eafaf1;color:#1b7a43;border:1px solid #bfe9cf}}
.cdep{{font-size:.64rem;color:var(--ink-3);font-weight:600;margin-bottom:5px}}
details{{margin-top:4px}}
summary{{cursor:pointer;font-size:.66rem;color:var(--blue);font-weight:700;list-style:none}}
summary::-webkit-details-marker{{display:none}}
summary::before{{content:"▸ "}} details[open] summary::before{{content:"▾ "}}
.dod{{font-size:.7rem;color:var(--ink-2);background:#fafcff;border-left:2px solid var(--line);padding:6px 8px;border-radius:5px;margin-top:5px;line-height:1.45}}
.prompt{{margin-top:7px;background:#0b1f33;border-radius:7px;padding:8px}}
.plab{{font-family:'JetBrains Mono',monospace;font-size:.6rem;color:#7fb0e0;font-weight:700;margin-bottom:4px;letter-spacing:.05em}}
.prompt code{{display:block;font-family:'JetBrains Mono',monospace;font-size:.64rem;color:#dfe9f5;white-space:pre-wrap;line-height:1.5}}
footer{{padding:24px 0 44px;color:var(--ink-3);font-size:.76rem}}
@media print{{body{{background:#fff}}.board{{flex-wrap:wrap}}.col{{flex-basis:48%}}details p,.prompt{{display:block}}}}
</style></head><body>''']

    H.append('''<header class="hero"><div class="wrap">
<div class="mono" style="font-size:.66rem;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.7)">Genactiv.pl · Plan operacyjny · CZERWIEC 2026 · sprint startowy</div>
<h1 class="serif">Sprint czerwiec — tydzień po tygodniu</h1>
<p class="sub">Fundament pod +50% YoY. Każda karta: owner (CC / hybryda / ręcznie), estymacja, zależności, Definition of Done i wpływ na KPI. Przy zadaniach Claude Code rozwiń kartę po gotowy prompt do wklejenia. Motyw miesiąca: <b>uruchomić silniki</b> (content/LP engine, A/B layout, flows, segmentacja) — żeby od lipca tylko skalować.</p>
<div class="pills"><span class="pill">Cel czerwca: +PLN 20 000 / mies. (18% celu)</span><span class="pill">Nowy layout A/B — START w W3</span><span class="pill">60–100 artykułów (falami, QA medyczne)</span><span class="pill">Decyzja subskrypcji do 1.07</span></div>
</div></header>''')

    H.append('<div class="wrap"><div class="legend">'
             '<span><span class="sdot" style="background:#0066CC"></span>A · SEO</span>'
             '<span><span class="sdot" style="background:#EF3340"></span>B · CRO</span>'
             '<span><span class="sdot" style="background:#8b5cf6"></span>C · Klaviyo</span>'
             '<span><span class="sdot" style="background:#27ae60"></span>D · LTV</span>'
             '<span><span class="sdot" style="background:#f59e0b"></span>E · Automatyzacja</span>'
             '<span><span class="sdot" style="background:#1A3B5D"></span>OPS</span>'
             '<span style="margin-left:8px"><span class="tagb" style="background:#EF3340">P1</span> <span class="tagb" style="background:#f59e0b">P2</span> <span class="tagb" style="background:#9ca3af">P3</span> priorytet</span>'
             '<span><span class="tagb" style="background:#0066CC">CC</span> Claude Code · <span class="tagb" style="background:#8b5cf6">CC+</span> hybryda · <span class="tagb" style="background:#6b7280">MAN</span> ręcznie</span>'
             '</div>')
    H.append('<div class="toolbar"><button class="btn" onclick="document.querySelectorAll(\'details\').forEach(d=>d.open=true)">Rozwiń wszystkie (DoD + prompty)</button><button class="btn sec" onclick="document.querySelectorAll(\'details\').forEach(d=>d.open=false)">Zwiń</button></div>')

    H.append('<div class="board">')
    for wk in WEEKS:
        cards = [t for t in TASKS if t["week"] == wk["id"]]
        co = " closeout" if wk["id"] == "W5" else ""
        H.append(f'<div class="col{co}"><div class="colhead"><span class="cnt">{len(cards)} zad.</span><div class="wk">{esc(wk["label"])}</div><div class="dt">{esc(wk["dates"])}</div><div class="fc">{esc(wk["focus"])}</div></div>')
        for t in cards:
            H.append(card(t))
        H.append('</div>')
    H.append('</div></div>')

    H.append('''<footer><div class="wrap">
Genactiv.pl · Sprint operacyjny czerwiec 2026 · 22 zadania / 5 streamów · estymacje czasu i KPI kierunkowe.<br>
Zależności (⛓) wyznaczają kolejność w tygodniu. Karty P1 = ścieżka krytyczna — robione najpierw. Prompty CC zakładają podpięte MCP: shopify-extended, klaviyo, senuto, GA4. Dane do snapshotu (OPS1) — odśwież baseline o okres od stycznia 2026.
</div></footer></body></html>''')

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(H))
    print("OK ->", OUT, "| zadań:", len(TASKS))

if __name__ == "__main__":
    build()

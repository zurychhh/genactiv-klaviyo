# -*- coding: utf-8 -*-
"""
Generator interaktywnej roadmapy wzrostu Genactiv.pl H2 2026.
Dane trzymane w strukturze poniżej — regeneracja: `python3 build_roadmap.py`.
Po odświeżeniu danych z MCP (Shopify/Klaviyo/GA4) wystarczy podmienić BASELINE i KPI w cells.
"""
import html

OUT = "roadmapa-wzrostu-h2-2026.html"

# ---- META ----
STREAMS = [
    {"id": "A", "name": "SEO / Organic", "color": "#0066CC",
     "kpi": "organic sessions · frazy TOP3 · organic CR", "contrib": "+PLN 28 000 · 25% celu",
     "levers": ["Fix 457 SEO issues", "Alt text 0,3%→100%", "Meta titles/desc",
                "Content engine (auto)", "Reaktywacja starych art.", "Programmatic SEO",
                "Schema / snippets", "Internal linking", "AEO / LLM"]},
    {"id": "B", "name": "Konwersja (CRO)", "color": "#EF3340",
     "kpi": "CR sesja→order · CR mobile · AOV", "contrib": "+PLN 25 000 · 22% celu",
     "levers": ["Nowy layout (A/B czerwiec)", "Mobile CRO (gap −1,17pp)", "PDP / sticky ATC",
                "Reviews / trust", "Pricing / bundle / promo", "Cross-sell / upsell",
                "Free-ship threshold", "Personalizacja", "Checkout: one-page (utrzymanie)"]},
    {"id": "C", "name": "Klaviyo / Email+SMS", "color": "#8b5cf6",
     "kpi": "lista zgód · flow rev. · email rev. share", "contrib": "+PLN 22 000 · 20% celu",
     "levers": ["Rozrost bazy 8K→14K", "Post-purchase / win-back", "VIP / sunset / birthday",
                "Replenishment (sezon)", "Cadence 2–3×/tydz.", "SMS (0→3,5K)",
                "RFM segmentacja", "Popup / lead magnet"]},
    {"id": "D", "name": "Retencja / LTV", "color": "#27ae60",
     "kpi": "repeat rate · items/order · subskrypcja · LTV", "contrib": "+PLN 22 000 · 19% celu",
     "levers": ["Bundle (3 nowe)", "Subskrypcja (top 3 SKU)", "Program lojalnościowy (tiers)",
                "Referral (MGM)", "Cross-sell / 2. zakup", "Gift sets / gift cards",
                "Cohort / win-back", "Replenishment-driven loyalty"]},
    {"id": "E", "name": "Automatyzacja / LP+Content", "color": "#f59e0b",
     "kpi": "% automatyzacji · LP/artykuł live · throughput", "contrib": "+PLN 15 694 · 14% celu",
     "levers": ["LP Generator (Claude Code)", "Content/Copy engine", "6 typów szablonów",
                "Edytowalne w Shopify Pages", "Auto SEO (meta/schema/OG)", "Auto-warianty A/B",
                "Personalizacja per UTM", "Self-service zespołu"]},
]

MONTHS = [
    {"k": "VI", "name": "Czerwiec", "theme": "Fundament + nowy layout A/B"},
    {"k": "VII", "name": "Lipiec", "theme": "Content velocity + email scale"},
    {"k": "VIII", "name": "Sierpień", "theme": "Konwersja + subskrypcja/loyalty"},
    {"k": "IX", "name": "Wrzesień", "theme": "Back-to-Health (sezon ↑)"},
    {"k": "X", "name": "Październik", "theme": "Pre-holiday prep"},
    {"k": "XI", "name": "Listopad", "theme": "BFCM · PEAK", "peak": True},
    {"k": "XII", "name": "Grudzień", "theme": "Święta + NY + 2027"},
]

# Sezonowość: low / mid / high / peak
SEASON = {
    "VI":  {"odp": "low",  "gut": "mid",  "ev": "—"},
    "VII": {"odp": "low",  "gut": "low",  "ev": "wyprzedaże letnie"},
    "VIII":{"odp": "mid",  "gut": "mid",  "ev": "powrót z wakacji"},
    "IX":  {"odp": "high", "gut": "high", "ev": "Back-to-Health"},
    "X":   {"odp": "high", "gut": "mid",  "ev": "pre-holiday"},
    "XI":  {"odp": "peak", "gut": "mid",  "ev": "BFCM"},
    "XII": {"odp": "peak", "gut": "high", "ev": "Święta + NY prep"},
}

# Impact inkrementalny / mies. (PLN tys.), monthly revenue target, % celu
IMPACT = {
    "VI":  (20, "242K", "18%"), "VII": (31, "254K", "27%"), "VIII": (42, "265K", "37%"),
    "IX":  (54, "277K", "48%"), "X": (54, "277K", "48%"), "XI": (85, "308K", "75%"),
    "XII": (59, "282K", "52%"),
}

# bot: cc=Claude Code, hu=manual/specialist, hy=hybrid
def w(title, bot, pri, detail):
    return {"t": title, "bot": bot, "pri": pri, "detail": detail}
def d(title, bot, pri, kpi, detail):
    return {"t": title, "bot": bot, "pri": pri, "kpi": kpi, "detail": detail}

# ---- TREŚĆ: CELLS[stream_id][month_key] = (work, deliv) ----
CELLS = {
"A": {
 "VI": (w("Keyword research top 20 PDP + gap analysis (Colostrigen, Immuno Lab); mapowanie sezonowe fraz odpornościowych", "hy", "P1",
          "Co: research słów kluczowych pod produkty i analiza luki vs konkurencja. Dlaczego tu: bez mapy fraz content engine generuje 'w ciemno'. Priorytet P1 — fundament dla całego streamu A."),
        d("Content engine LIVE + 60–100 artykułów (odporność, dawkowanie, kategorie) — automatyzacja + QA medyczne falami; fix 338 alt + 59 meta titles + 18 meta desc (bulk MCP)", "cc", "P1", "organic CR 1,74%→1,9% · +PLN 6K",
          "Co: silnik generowania treści (Claude Code) + duża pierwsza partia artykułów + masowa naprawa metadanych przez MCP. Dlaczego tu i dlaczego tak dużo: artykuły odpornościowe publikujemy w MARTWYM sezonie (lato), by zdążyły się zaindeksować i zrankować PRZED jesiennym szczytem infekcji. Guardrail YMYL: treści zdrowotne wymagają human QA medycznego falami — stąd 60–100, a nie 100 surowych w 1 dzień (thin content szkodzi). Priorytet P1, najwyższe ICE (648/630).")),
 "VII": (w("Audyt internal linking + optymalizacja sitemap; reaktywacja 20 starych artykułów (refresh, update dat, linkowanie)", "hy", "P2",
          "Co: porządkowanie struktury linków i odświeżenie istniejących treści. Dlaczego tu: 'reaktywacja contentu pisanego' — stare artykuły mają już autorytet, refresh jest tańszy niż nowy content i szybciej rankuje. Priorytet P2."),
        d("+40 artykułów (2. partia) + 19 opisów produktów + schema (Product/FAQ/Breadcrumb) na wszystkich PDP", "cc", "P1", "organic sessions +10% · +PLN 5K",
          "Co: druga fala treści + structured data. Dlaczego tu: kumulujemy bibliotekę do 100+ artykułów; schema = rich snippets = wyższy CTR w SERP. Priorytet P1 — content compound effect.")),
 "VIII": (w("Monitoring rankingów + backlink outreach do blogów health PL", "hu", "P2",
          "Co: budowa autorytetu domeny przez linki zewnętrzne. Dlaczego tu: po publikacji treści potrzebują linków, by przebić konkurencję. Manualne — wymaga relacji i negocjacji. Priorytet P2."),
        d("+50 stron programmatic /colostrum-na-[stan] + 6 artykułów pogłębionych (SIBO, IBS, alergia, ciąża)", "cc", "P1", "organic sessions +15% · +PLN 8K",
          "Co: automatyczne generowanie stron pod long-tail zdrowotny. Dlaczego tu: programmatic SEO skaluje pokrycie fraz bez ręcznej pracy — idealne pod Claude Code. Sezon: te frazy zaczynają rosnąć od września. Priorytet P1.")),
 "IX": (w("Link building (10 guest posts) + Google Discover optimization", "hu", "P3",
          "Co: dalsza budowa autorytetu + optymalizacja pod feed Discover. Dlaczego tu: wzmacnia treści tuż przed sezonem szczytowym. Priorytet P3 — wspierające."),
        d("Kampania 'Back to Health' (8 artykułów) + optymalizacja top 25 LP pod featured snippets + video YT na blogu", "hy", "P1", "organic CR →2,15% · +PLN 12K",
          "Co: treści dopasowane do szczytu sezonu odpornościowego. Dlaczego tu: WRZESIEŃ to start sezonu infekcyjnego — intencja wyszukiwań 'odporność' rośnie skokowo. Treść z czerwca/lipca już rankuje, teraz dokładamy sezonowe. Priorytet P1 — sezonowy peak.")),
 "X": (w("Fix crawl errors + update sitemap + Core Web Vitals", "cc", "P2",
          "Co: higiena techniczna SEO. Dlaczego tu: przed ruchem holiday strona musi być czysta i szybka. Automatyzowalne audytem MCP. Priorytet P2."),
        d("Programmatic v2 (/colostrum-[brand]-opinie, /colostrum-vs-[konkurent]) + holiday keyword prep (prezent zdrowie, BF suplementy)", "cc", "P2", "organic sessions +10% · +PLN 15K",
          "Co: strony porównawcze i opiniowe + przygotowanie fraz świątecznych. Dlaczego tu: intencja zakupowa rośnie przed świętami; 'vs/opinie' łapią dolny lejek. Priorytet P2.")),
 "XI": (w("Monitoring dzienny rankingów + szybkie update treści wg performance", "hy", "P2",
          "Co: bieżąca reakcja na to, co rankuje w szczycie. Dlaczego tu: BFCM = maksymalna konkurencja w SERP, liczy się tempo. Priorytet P2."),
        d("Holiday content push (gift guides, 'najlepsze suplementy na prezent', BF comparison) + opt 'colostrum Black Friday'", "hy", "P1", "organic traffic holiday · +PLN 18K",
          "Co: treści pod świąteczną intencję prezentową + BF. Dlaczego tu: największy wolumen wyszukiwań zakupowych w roku. Priorytet P1 — bezpośrednio przy peaku przychodu.")),
 "XII": (w("Annual SEO audit + strategia fraz 2027", "hy", "P3",
          "Co: podsumowanie i planowanie. Dlaczego tu: domknięcie roku + setup pod styczniowy sezon postanowień. Priorytet P3."),
        d("'Nowy Rok, Nowe Zdrowie' + year-in-review + proaktywna optymalizacja pod styczniowe frazy zdrowotne", "hy", "P2", "momentum styczeń · +PLN 15K",
          "Co: treści pod sezon postanowień noworocznych. Dlaczego tu: styczeń to drugi szczyt (zdrowie, dieta, odporność) — publikujemy w grudniu, by zdążyć zrankować. Priorytet P2 — sezonowe wyprzedzenie.")),
},
"B": {
 "VI": (w("Mobile UX audit + instalacja heatmap (Hotjar/Clarity); identyfikacja top 3 punktów drop-off na mobile", "hu", "P1",
          "Co: diagnoza UX i miejsc porzuceń na mobile. Dlaczego tu: 79% ruchu to mobile z CR 2,09% (gap −1,17pp do desktop) — najpierw mierzymy, potem zmieniamy. Priorytet P1 — fundament CRO."),
        d("▶ START A/B testu NOWEGO LAYOUTU (homepage + PDP) — wariant mobile-first, sticky ATC, trust badges", "hy", "P1", "CR mobile +0,3–0,5pp · +PLN 8K",
          "Co: główny test layoutu rusza w czerwcu (najbardziej skalowalne rozwiązanie). Dlaczego tu: layout dotyka 100% sesji — najwyższa dźwignia, dlatego startuje od razu, równolegle z audytem. Priorytet P1, kamień milowy. Claude Code buduje warianty, specjalista CRO analizuje wyniki.")),
 "VII": (w("Page speed / CWV audit; analiza pierwszych wyników A/B layoutu", "hy", "P2",
          "Co: optymalizacja szybkości + odczyt danych z testu layoutu. Dlaczego tu: speed wpływa na CR mobile; layout potrzebuje ~3–4 tyg. na istotność. Priorytet P2."),
        d("Wdrożenie zwycięskiego layoutu + galeria zdjęć PDP (zoom, swipe) + A/B #2 (układ benefitów above-the-fold)", "hy", "P1", "CR mobile →2,30% · +PLN 8K",
          "Co: rollout wygranego wariantu + kolejny test PDP. Dlaczego tu: zwycięzca z czerwca skalujemy na całość; kolejny test na PDP. Uwaga: NIE testujemy checkoutu — jest już one-page (utrzymanie). Priorytet P1.")),
 "VIII": (w("Cross-browser mobile testing + analiza cart abandonment", "hu", "P2",
          "Co: QA na urządzeniach + diagnoza porzuceń koszyka. Dlaczego tu: przed pushem konwersji eliminujemy bugi. Priorytet P2."),
        d("Urgency (stock counters, recently purchased) + widget recenzji (Judge.me/Loox) na PDP", "hy", "P2", "CR →2,52% · +PLN 10K",
          "Co: social proof + elementy pilności. Dlaczego tu: recenzje i pilność to sprawdzone dźwignie konwersji na PDP (checkout zostawiamy bez zmian). Priorytet P2.")),
 "IX": (w("Mobile speed: target CWV all green; optymalizacja obrazów (WebP, lazy load)", "cc", "P2",
          "Co: domknięcie wydajności mobile. Dlaczego tu: sezon ↑ = więcej ruchu mobile, każdy 0,1s liczy się przy CR. Automatyzowalne. Priorytet P2."),
        d("A/B #3 homepage (hero, bestsellery, social proof) + personalizowane rekomendacje produktów + predictive search", "hy", "P1", "CR →2,52% · +PLN 12K",
          "Co: test układu strony głównej + personalizacja. Dlaczego tu: rosnący ruch sezonowy = większa próbka testowa + personalizacja podnosi AOV. Priorytet P1.")),
 "X": (w("Backup payment gateway + monitoring wydajności (bez zmian layoutu checkoutu — one-page wdrożony)", "hu", "P2",
          "Co: zabezpieczenie płatności i wydajności pod ruch BF. Dlaczego tu: niezawodność przed peakiem, NIE optymalizacja checkoutu. Priorytet P2."),
        d("A/B #4 cart (cross-sell widget, free-ship threshold PLN 250) + gift wrapping + promo bar z countdownem", "hy", "P2", "AOV +PLN 10–15 · +PLN 12K",
          "Co: testy koszyka i progu darmowej dostawy + opcje świąteczne. Dlaczego tu: free-ship threshold to bezpośrednia dźwignia AOV (cel 272→305). Priorytet P2.")),
 "XI": (w("Real-time monitoring CR / cart / page speed w trakcie BFCM", "cc", "P1",
          "Co: czujki wydajności na żywo w szczycie. Dlaczego tu: w BFCM minuta downtime = utracony przychód. Dashboard automatyczny. Priorytet P1."),
        d("BF landing (via LP Generator) + flash sale (tiered discounts, mystery box) + exit-intent popup BF", "hy", "P1", "BF conversion spike · +PLN 20K",
          "Co: dedykowana strona BF + mechaniki promocyjne. Dlaczego tu: szczyt sprzedaży roku, najwyższy zwrot z optymalizacji oferty. Priorytet P1, kamień milowy.")),
 "XII": (w("Full CRO audit H2 — co zadziałało, co skalować w 2027", "hu", "P3",
          "Co: retrospektywa testów. Dlaczego tu: domknięcie i nauka pod 2027. Priorytet P3."),
        d("Last-minute gift optimization (express delivery badges) + New Year promo page + ewaluacja PWA/app", "hy", "P3", "holiday tail · +PLN 12K",
          "Co: optymalizacja końcówki świątecznej + plan app. Dlaczego tu: łapiemy spóźnionych kupujących + planujemy kanał mobilny. Priorytet P3.")),
},
"C": {
 "VI": (w("Setup segmentacji RFM + szablony copy do kampanii cyklicznych", "cc", "P1",
          "Co: segmentacja klientów (Recency/Frequency/Monetary) + biblioteka maili. Dlaczego tu: bez segmentów kampanie lecą 'do wszystkich' = niski CR; RFM robi się przez MCP. Priorytet P1."),
        d("Post-Purchase flow (2 maile) + Win-Back (90d) + cadence kampanii 2×/tydzień", "hy", "P1", "email rev. +PLN 8K",
          "Co: nowe automatyzacje + częstsze kampanie. Dlaczego tu: Welcome generuje 81% rev z flows — reszta nie istnieje; najszybszy zwrot (ICE 576/512). Claude Code drafuje przez MCP, human dopisuje copy PL. Priorytet P1.")),
 "VII": (w("SMS pilot research (zgodność RODO) + systematyczny A/B subject lines", "hu", "P2",
          "Co: przygotowanie kanału SMS i testów tematów. Dlaczego tu: SMS wymaga osobnej zgody RODO — najpierw compliance. Priorytet P2."),
        d("VIP flow (top 10% spenderów) + Sunset flow (180d, re-engage→suppress) + segmentacja kampanii per produkt", "hy", "P2", "email rev. +PLN 10K",
          "Co: flow lojalnościowy dla najlepszych + czyszczenie listy + targetowanie. Dlaczego tu: VIP mają najwyższy LTV; sunset chroni deliverability. Priorytet P2.")),
 "VIII": (w("Clean list (usuń 180d po sunset) + audyt deliverability", "cc", "P2",
          "Co: higiena listy i dostarczalności. Dlaczego tu: przed skalowaniem wolumenu (SMS, BF) lista musi być zdrowa. Priorytet P2."),
        d("▶ SMS pilot LIVE (back-in-stock, flash sale, cart recovery) + Birthday flow + Replenishment flow (sezonowy reorder)", "hy", "P1", "SMS + replen. +PLN 12K",
          "Co: uruchomienie SMS + flow uzupełnienia zapasów. Dlaczego tu: Replenishment liczy timing reorderu wg wielkości opakowania — dla FMCG (colostrum) to bezpośrednia dźwignia 2. zakupu i sezonowości. Priorytet P1, kamień milowy.")),
 "IX": (w("Zaawansowana segmentacja RFM + dynamic content blocks", "cc", "P2",
          "Co: dynamiczne treści maili wg segmentu. Dlaczego tu: personalizacja podnosi CR w sezonowym peaku ruchu. Priorytet P2."),
        d("Seria 'Back to Health' (4 maile) + segment churn-risk (predictive) + automatyzacja winback", "hy", "P1", "email rev. +PLN 15K",
          "Co: kampania sezonowa + zapobieganie odpływowi. Dlaczego tu: wrzesień = peak intencji 'odporność', a churn-risk łapie odpływających zanim odejdą. Priorytet P1.")),
 "X": (w("A/B popup (timing, copy, incentive) + warm-up IP pod wysokie wolumeny", "hy", "P1",
          "Co: optymalizacja zapisów + rozgrzanie IP. Dlaczego tu: przed BF musimy urosnąć bazę i nie wpaść w spam przy dużych wysyłkach. Priorytet P1 — krytyczne dla XI."),
        d("Pre-BF list growth popup ('BF ofertę dostaniesz 24h wcześniej') + VIP early access + holiday templates (5 wariantów)", "hy", "P1", "lista +1200 · +PLN 12K",
          "Co: agresywny rozrost bazy zgód przed BF + szablony. Dlaczego tu: każdy zapis przed BF = przychód w listopadzie; baza to KPI (8K→14K). Priorytet P1.")),
 "XI": (w("Deliverability monitoring + fallback campaigns gotowe + skalowanie wolumenu", "hu", "P1",
          "Co: zabezpieczenie wysyłek w szczycie. Dlaczego tu: przy 6 mailach BF ryzyko throttlingu/spamu rośnie. Priorytet P1."),
        d("Sekwencja BF: Teaser (T-7) → VIP early (T-1) → Launch → Reminder (D+1) → Cyber Monday (D+3) → Last Chance (D+5) + 3× SMS", "hy", "P1", "email/SMS BF +PLN 25K",
          "Co: pełna kampania BFCM email+SMS. Dlaczego tu: największy pojedynczy driver przychodu w streamie C w całym roku. Priorytet P1, kamień milowy.")),
 "XII": (w("Strategia email 2027 + ocena zdrowia listy", "hu", "P3",
          "Co: planowanie i podsumowanie. Dlaczego tu: domknięcie roku. Priorytet P3."),
        d("Holiday finish (Xmas reminder, NY resolutions) + VIP thank you + raport roczny subskrybentów", "hy", "P2", "holiday email +PLN 15K",
          "Co: końcówka świąteczna + start sezonu postanowień. Dlaczego tu: NY resolutions = wysoka intencja zdrowotna w styczniu, budujemy zapowiedź w grudniu. Priorytet P2.")),
},
"D": {
 "VI": (w("Research subskrypcji (Recharge/Bold/Skio — shortlist, decyzja do 1.07) + analiza kohort i hard userów", "hu", "P1",
          "Co: wybór narzędzia subskrypcyjnego + baseline retencji. Dlaczego tu: subskrypcja to najsilniejszy driver MRR — decyzja narzędzia blokuje launch w lipcu. Priorytet P1."),
        d("Audyt bundli + 3 nowe zestawy (colostrum+fiberbiom, family pack, starter kit)", "hy", "P2", "AOV + items/order · +PLN 4K",
          "Co: nowe oferty pakietowe. Dlaczego tu: bundle natychmiast podnosi AOV i items/order (1,5→1,8) bez czekania na projekty. Priorytet P2.")),
 "VII": (w("Ankieta klientów o subskrypcji + research programu lojalnościowego (FMCG: low-margin, replenishment-driven)", "hu", "P1",
          "Co: walidacja popytu + projekt mechaniki lojalności. Dlaczego tu: w FMCG (colostrum to produkt cykliczny) lojalność musi nagradzać POWTARZALNOŚĆ, nie tylko wartość — to inny model niż w fashion. Priorytet P1 — pogłębiony research przed launchem."),
        d("▶ Subskrypcja LIVE na top 3 produktach (Colostrum 120, Fiberbiom, Colostrum proszek) — rabat 10%", "hu", "P1", "repeat rate ↑ · +PLN 6K",
          "Co: uruchomienie modelu subskrypcyjnego. Dlaczego tu: colostrum to produkt do regularnego stosowania — subskrypcja zamienia jednorazowy zakup w cykliczny przychód (MRR). Priorytet P1, kamień milowy.")),
 "VIII": (w("Referral research + analiza performance bundli; projekt tierów lojalności (Bronze/Silver/Gold) i reguł punktów", "hu", "P1",
          "Co: pogłębienie programu lojalnościowego — tiery, earn/redeem, integracja z subskrypcją (bonus pkt za sub). Dlaczego tu: mechanika musi działać z subskrypcją, dlatego projektowana po jej launchu. FMCG: punkty kalibrowane do niskiej marży. Priorytet P1."),
        d("▶ Program lojalnościowy LIVE (punkty: zakup/recenzja/polecenie; tiery) + cross-sell na Thank You + upsell modal pre-checkout", "hy", "P1", "repeat rate +3pp · +PLN 8K",
          "Co: uruchomienie lojalności + mechaniki cross/upsell. Dlaczego tu: amplifikuje subskrypcję (extra punkty za sub) i pcha 2. zakup oraz cross na nowe kategorie. Priorytet P1, kamień milowy.")),
 "IX": (w("Analiza subscription churn + LTV cohort analysis", "cc", "P2",
          "Co: pomiar utrzymania subskrypcji i LTV kohort. Dlaczego tu: po 2 mies. subskrypcji widać pierwszy churn — reagujemy. Automatyzowalne raportem. Priorytet P2."),
        d("Pause-instead-of-cancel + Referral LIVE (daj PLN 20, dostań PLN 20) + bundle-of-the-month", "hy", "P1", "referrals + retencja · +PLN 10K",
          "Co: redukcja churnu subskrypcji + program poleceń (MGM). Dlaczego tu: 'pause' ratuje subskrypcje sezonowe; referral obniża CAC. Priorytet P1.")),
 "X": (w("Package design + holiday LP via generator", "hy", "P2",
          "Co: przygotowanie produktów prezentowych. Dlaczego tu: świąteczne SKU trzeba przygotować z wyprzedzeniem. Priorytet P2."),
        d("Holiday gift sets (3 warianty) + gift cards launch + subscription gift ('Podaruj zdrowie na 3 mies.')", "hy", "P2", "AOV + nowi klienci · +PLN 10K",
          "Co: oferta prezentowa + karty podarunkowe. Dlaczego tu: gift = pozyskanie nowych klientów (obdarowani) + subscription gift wprowadza ich w cykl. Priorytet P2.")),
 "XI": (w("Track new-vs-returning BF + planowanie post-BF winback", "cc", "P2",
          "Co: analiza struktury kupujących BF. Dlaczego tu: BF przyciąga łowców okazji — kluczowe jest ich potem zatrzymać. Priorytet P2."),
        d("BF exclusive dla subskrybentów (+5%) + '2+1 gratis' + post-BF retention (konwersja BF buyers → subskrybenci)", "hy", "P1", "LTV BF cohort · +PLN 15K",
          "Co: oferty lojalizujące w BF + konwersja na subskrypcję. Dlaczego tu: zamiana jednorazowych BF-kupujących w cykl to największa dźwignia LTV roku. Priorytet P1, kamień milowy.")),
 "XII": (w("Ewolucja programu lojalnościowego 2027 + cohort analysis", "hu", "P3",
          "Co: planowanie rozwoju lojalności. Dlaczego tu: domknięcie roku + roadmap 2027. Priorytet P3."),
        d("'NY Resolution' subscription push (commitment 3 mies., −15%) + appreciation top 100 klientów + raport retencji", "hy", "P2", "NY subskrypcje · +PLN 12K",
          "Co: push subskrypcji pod postanowienia + program docenienia. Dlaczego tu: styczeń = peak motywacji zdrowotnej, 3-mies. commitment buduje MRR na Q1. Priorytet P2.")),
},
"E": {
 "VI": (w("Spec review LP Generatora + integracja Shopify Pages API + schema design; spec Content/Copy engine", "cc", "P1",
          "Co: architektura narzędzi automatyzacji (LP + treści). Dlaczego tu: to fundament mnożnika throughputu dla A i B — im wcześniej, tym szybciej skalują pozostałe streamy. Priorytet P1."),
        d("LP Generator v1 (Liquid, 2 szablony) + Content/Copy engine v1 (artykuły, opisy, meta) — output edytowalny w Shopify Pages", "cc", "P1", "throughput LP/treści · +PLN 0 (faza dev)",
          "Co: pierwsza wersja generatora LP + silnika treści/copy. Dlaczego tu i ASAP: 'automatyzacja contentu i copy' to warunek publikacji 100+ artykułów (stream A) i dziesiątek LP. Kluczowe: wszystko osadzone na Shopify Pages pozostaje w PEŁNI edytowalne ręcznie. 100% Claude Code. Priorytet P1.")),
 "VII": (w("QA wszystkich szablonów + integracja SEO checklist do pipeline", "cc", "P2",
          "Co: kontrola jakości szablonów + wbudowanie reguł SEO. Dlaczego tu: zanim skalujemy produkcję, output musi być powtarzalnie poprawny. Priorytet P2."),
        d("LP Gen v2 (+3 szablony: blog, seasonal promo, bundle) + auto-deploy via Pages API; Content engine: batch 40 art./tydz.", "cc", "P2", "tempo publikacji ↑ · +PLN 2K",
          "Co: rozbudowa szablonów + automatyczny deploy + skalowanie produkcji treści. Dlaczego tu: to E dostarcza moc, dzięki której A robi 40+ artykułów/mies. Priorytet P2.")),
 "VIII": (w("Performance monitoring LP + rozbudowa biblioteki szablonów", "cc", "P3",
          "Co: pomiar skuteczności LP. Dlaczego tu: dane sterują, które szablony rozwijać. Priorytet P3."),
        d("Auto SEO layer (meta/schema/OG auto) + A/B integration (warianty LP) + dashboard performance LP", "cc", "P2", "LP CR ↑ · +PLN 4K",
          "Co: automatyczna optymalizacja SEO LP + generowanie wariantów A/B. Dlaczego tu: łączy E z B (testy) i A (SEO) — jeden silnik zasila oba. Priorytet P2.")),
 "IX": (w("Integracja z Klaviyo (LP-triggered flows)", "cc", "P2",
          "Co: LP wyzwala automatyzacje email. Dlaczego tu: domyka pętlę onsite→email w sezonie. Priorytet P2."),
        d("Personalization layer (hero/CTA wg UTM source) + AI copy suggestions dla sekcji LP", "cc", "P2", "LP CR ↑ · +PLN 5K",
          "Co: personalizacja LP wg źródła ruchu + podpowiedzi copy. Dlaczego tu: ruch sezonowy z różnych kanałów konwertuje lepiej przy dopasowanym przekazie. Priorytet P2.")),
 "X": (w("Load testing + CMS/UI dla zespołu non-tech", "cc", "P2",
          "Co: test obciążenia + interfejs dla marketingu. Dlaczego tu: przed BF i przed self-service zespół musi móc działać bez dev. Priorytet P2."),
        d("Holiday template pack (BF LP, Gift Guide LP, NY LP) + quick-deploy system (LP live < 15 min)", "cc", "P2", "szybkie LP holiday · +PLN 5K",
          "Co: gotowe szablony świąteczne + ekspresowy deploy. Dlaczego tu: w sezonie liczy się czas postawienia LP. Priorytet P2.")),
 "XI": (w("Analytics dashboard wydajności LP w czasie rzeczywistym", "cc", "P2",
          "Co: monitoring LP na żywo w BFCM. Dlaczego tu: szybka reakcja na to, co konwertuje w szczycie. Priorytet P2."),
        d("Real-time LP variants (stock-aware: 'zostało 15 szt.') + auto-trigger email po wizycie LP bez zakupu", "cc", "P2", "auto konwersja · +PLN 7K",
          "Co: dynamiczne LP zależne od stanu magazynu + automatyczny retargeting email. Dlaczego tu: maksymalizuje konwersję ruchu BF bez ręcznej pracy. Priorytet P2.")),
 "XII": (w("Roadmapa automatyzacji 2027 + ocena ROI narzędzi", "cc", "P3",
          "Co: planowanie i rozliczenie automatyzacji. Dlaczego tu: domknięcie roku. Priorytet P3."),
        d("LP Generator v3 — full self-service dla zespołu marketingu + dokumentacja + training (cel: 90% automatyzacji)", "cc", "P1", "90% self-service · +PLN 5K",
          "Co: pełna samoobsługa zespołu + przekazanie wiedzy. Dlaczego tu: cel roku — 90% produkcji LP/treści bez dev, by tempo było trwałe w 2027. Priorytet P1, kamień milowy.")),
},
}

# ---------- RENDER ----------
BOT = {"cc": ("CC", "Claude Code", "#0066CC"),
       "hy": ("CC+", "Hybryda (Claude Code + człowiek)", "#8b5cf6"),
       "hu": ("MAN", "Ręcznie / specjalista", "#6b7280")}
PRI = {"P1": "#EF3340", "P2": "#f59e0b", "P3": "#9ca3af"}
SEASON_COLOR = {"low": "#eef2f7", "mid": "#cfe0f0", "high": "#7fb0e0", "peak": "#f59e0b"}
SEASON_LABEL = {"low": "niski", "mid": "śr.", "high": "wysoki", "peak": "SZCZYT"}

def esc(s): return html.escape(s, quote=True)

def badges(item, is_deliv):
    b = BOT[item["bot"]]
    out = f'<span class="pri" style="background:{PRI[item["pri"]]}">{item["pri"]}</span>'
    out += f'<span class="bot" style="background:{b[2]}" title="{esc(b[1])}">{b[0]}</span>'
    if is_deliv and item.get("kpi"):
        out += f'<span class="kpiup">{esc(item["kpi"])}</span>'
    return out

def cell_html(work, deliv):
    h = '<div class="cell">'
    for item, cls, lab, isd in ((work, "work", "Prace", False), (deliv, "deliv", "Deliverable", True)):
        ms = " milestone" if (isd and item["t"].startswith("▶")) else ""
        h += f'<div class="blk {cls}{ms}">'
        h += f'<div class="brow">{badges(item, isd)}</div>'
        h += f'<b>{lab}</b><span class="ttl">{esc(item["t"])}</span>'
        h += f'<details><summary>i — co to / dlaczego tu / priorytet</summary><p>{esc(item["detail"])}</p></details>'
        h += '</div>'
    return h + '</div>'

def build():
    cols = "150px " + " ".join("minmax(184px,1fr)" for _ in MONTHS)
    H = []
    H.append(f'''<!DOCTYPE html><html lang="pl"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Roadmapa Wzrostu E-commerce — Genactiv.pl · H2 2026</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600;9..144,700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>
:root{{--blue:#0066CC;--blue-dk:#1A3B5D;--red:#EF3340;--green:#27ae60;--ink:#15202b;--ink-2:#4a5663;--ink-3:#8a94a0;--paper:#f6f8fb;--card:#fff;--line:#e3e9f0;--line-2:#eef2f7}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Inter',system-ui,sans-serif;color:var(--ink);background:var(--paper);font-size:15px;line-height:1.55;-webkit-font-smoothing:antialiased}}
.serif{{font-family:'Fraunces',Georgia,serif;letter-spacing:-.015em;line-height:1.08}}
.mono{{font-family:'JetBrains Mono',monospace;letter-spacing:.12em;text-transform:uppercase;font-size:.66rem;font-weight:500}}
.wrap{{max-width:1560px;margin:0 auto;padding:0 28px}}
.hero{{background:linear-gradient(135deg,#0b1f33,#0066CC 120%);color:#fff;padding:50px 0 42px}}
.hero .wrap{{display:flex;flex-direction:column;gap:20px}}
.hero h1{{font-size:2.6rem;font-weight:700;max-width:20ch}}
.hero h1 em{{font-style:normal;color:#ffd23f}}
.hero .sub{{font-size:1.02rem;color:rgba(255,255,255,.84);max-width:78ch}}
.pill{{display:inline-flex;align-items:center;gap:7px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.18);padding:5px 12px;border-radius:999px;font-size:.74rem;font-weight:600}}
.pill .d{{width:6px;height:6px;border-radius:50%;background:#ffd23f}}
.warn{{background:#fff4e6;border-left:4px solid #f59e0b;color:#7a4a00;padding:6px 12px;border-radius:8px;font-size:.78rem;font-weight:600;display:inline-block}}
section{{padding:40px 0}}
.shead{{display:flex;align-items:baseline;gap:14px;margin-bottom:18px;flex-wrap:wrap}}
.shead .n{{font-family:'JetBrains Mono',monospace;color:var(--blue);font-weight:500;font-size:.85rem}}
.shead h2{{font-family:'Fraunces',serif;font-size:1.5rem;font-weight:600}}
.shead p{{color:var(--ink-2);font-size:.9rem;margin-left:auto;max-width:54ch;text-align:right}}
.kpis{{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden}}
.kpi{{background:var(--card);padding:16px}}
.kpi .lbl{{font-size:.7rem;color:var(--ink-3);font-weight:600;text-transform:uppercase;letter-spacing:.06em}}
.kpi .val{{font-family:'Fraunces',serif;font-size:1.45rem;font-weight:600;margin-top:6px}}
.kpi .delta{{font-size:.76rem;font-weight:600;margin-top:4px;color:var(--green)}}
.streams{{display:grid;grid-template-columns:repeat(5,1fr);gap:14px}}
.sc{{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:16px;border-top:4px solid var(--ac)}}
.sc .tag{{font-weight:700;font-size:.92rem;display:flex;align-items:center;gap:8px}}
.sc .tag .ch{{width:22px;height:22px;border-radius:6px;background:var(--ac);color:#fff;display:grid;place-items:center;font-size:.72rem;font-weight:700;font-family:'JetBrains Mono',monospace}}
.sc .kpi-line{{font-size:.72rem;color:var(--ink-3);margin:8px 0 6px;font-weight:600}}
.sc .contrib{{font-size:.8rem;font-weight:700;color:var(--ac);margin-bottom:12px}}
.sc .lev-h{{font-size:.64rem;text-transform:uppercase;letter-spacing:.08em;color:var(--ink-3);font-weight:700;margin-bottom:6px}}
.sc ul{{list-style:none;display:flex;flex-wrap:wrap;gap:5px}}
.sc li{{font-size:.7rem;background:var(--line-2);border-radius:6px;padding:3px 8px;color:var(--ink-2);font-weight:500}}
.toolbar{{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-bottom:14px}}
.btn{{background:var(--blue);color:#fff;border:none;border-radius:8px;padding:7px 14px;font-size:.78rem;font-weight:600;cursor:pointer;font-family:inherit}}
.btn.sec{{background:#fff;color:var(--blue);border:1px solid var(--blue)}}
.tl-scroll{{overflow-x:auto;border:1px solid var(--line);border-radius:16px;background:var(--card)}}
.tl{{display:grid;grid-template-columns:{cols};min-width:1480px}}
.tl > div{{border-bottom:1px solid var(--line-2);border-right:1px solid var(--line-2);padding:10px 11px}}
.tl .corner{{background:var(--blue-dk);color:#fff;position:sticky;left:0;z-index:3;display:flex;flex-direction:column;justify-content:center}}
.tl .corner .big{{font-family:'Fraunces',serif;font-weight:600;font-size:.92rem}}
.tl .corner .sm{{font-size:.64rem;opacity:.7;margin-top:2px}}
.tl .mhead{{background:#f0f4f9;text-align:center;font-weight:700}}
.tl .mhead .mo{{font-family:'Fraunces',serif;font-size:1rem}}
.tl .mhead .theme{{font-size:.6rem;color:var(--blue);font-weight:600;margin-top:2px}}
.tl .mhead.peak{{background:#fff4e6}} .tl .mhead.peak .mo,.tl .mhead.peak .theme{{color:var(--red)}}
.tl .srow-h{{position:sticky;left:0;z-index:2;background:#fafcff;display:flex;flex-direction:column;justify-content:center;border-left:4px solid #f59e0b}}
.tl .srow-h .t{{font-weight:700;font-size:.74rem}} .tl .srow-h .k{{font-size:.6rem;color:var(--ink-3);font-weight:600}}
.scell{{display:flex;flex-direction:column;gap:3px;font-size:.62rem}}
.sbar{{display:flex;align-items:center;gap:5px}}
.sdot{{width:9px;height:9px;border-radius:2px;flex:none}}
.scell .ev{{font-weight:700;color:var(--ink-2);font-size:.64rem;margin-top:2px}}
.tl .rh{{position:sticky;left:0;z-index:2;background:var(--card);display:flex;flex-direction:column;justify-content:center;gap:3px;border-left:4px solid var(--ac)}}
.tl .rh .t{{font-weight:700;font-size:.82rem}} .tl .rh .k{{font-size:.62rem;color:var(--ink-3);font-weight:600}}
.cell{{font-size:.72rem;display:flex;flex-direction:column;gap:7px}}
.blk{{border-radius:7px;padding:6px 8px;line-height:1.32}}
.blk.work{{background:var(--line-2);color:var(--ink-2)}}
.blk.deliv{{background:color-mix(in srgb,var(--ac) 12%,#fff);border:1px solid color-mix(in srgb,var(--ac) 30%,#fff)}}
.blk.deliv.milestone{{box-shadow:0 0 0 2px color-mix(in srgb,var(--ac) 32%,#fff) inset}}
.brow{{display:flex;gap:4px;align-items:center;flex-wrap:wrap;margin-bottom:3px}}
.pri,.bot{{font-family:'JetBrains Mono',monospace;font-size:.56rem;font-weight:700;color:#fff;border-radius:4px;padding:1px 5px;letter-spacing:.04em}}
.kpiup{{font-size:.58rem;font-weight:700;color:var(--green);background:#eafaf1;border:1px solid #bfe9cf;border-radius:4px;padding:1px 5px}}
.blk b{{display:block;font-size:.55rem;text-transform:uppercase;letter-spacing:.07em;font-weight:700;opacity:.85;margin-bottom:1px}}
.blk.deliv b{{color:var(--ac);opacity:1}}
.ttl{{display:block;font-weight:600;font-size:.71rem;color:var(--ink)}}
details{{margin-top:5px}}
summary{{cursor:pointer;font-size:.58rem;color:var(--ink-3);font-weight:600;list-style:none;user-select:none}}
summary::-webkit-details-marker{{display:none}}
summary::before{{content:"▸ ";color:var(--blue)}}
details[open] summary::before{{content:"▾ "}}
details p{{font-size:.66rem;color:var(--ink-2);margin-top:4px;background:#fff;border-left:2px solid var(--line);padding:5px 7px;border-radius:4px;line-height:1.45}}
.tl .ir-h{{position:sticky;left:0;z-index:2;background:var(--blue-dk);color:#fff;display:flex;flex-direction:column;justify-content:center;border-left:4px solid #ffd23f}}
.tl .ir-h .t{{font-weight:700;font-size:.8rem}} .tl .ir-h .k{{font-size:.6rem;opacity:.75;font-weight:600}}
.icell{{background:#fbfdff;display:flex;flex-direction:column;justify-content:flex-end;gap:6px;padding-bottom:12px}}
.bar{{background:linear-gradient(180deg,#3a8fe0,#0066CC);border-radius:5px 5px 0 0;width:100%;display:flex;align-items:flex-start;justify-content:center;padding-top:4px}}
.bar span{{color:#fff;font-weight:700;font-size:.7rem;font-family:'JetBrains Mono',monospace}}
.bar.peak{{background:linear-gradient(180deg,#ff7a5c,#EF3340)}}
.icell .cum{{font-size:.58rem;color:var(--ink-3);text-align:center;font-weight:600}}
.tl > div:nth-last-child(-n+8){{border-bottom:none}}
.legend{{display:flex;gap:16px;flex-wrap:wrap;margin-top:14px;font-size:.72rem;color:var(--ink-2)}}
.legend .it{{display:flex;align-items:center;gap:6px}}
.legend .sw{{width:13px;height:13px;border-radius:4px}}
.legend .tagb{{font-family:'JetBrains Mono',monospace;font-size:.58rem;font-weight:700;color:#fff;border-radius:4px;padding:1px 5px}}
.notes{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-top:6px}}
.note{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:15px;border-left:4px solid var(--red)}}
.note h4{{font-size:.88rem;margin-bottom:6px}} .note p{{font-size:.78rem;color:var(--ink-2)}}
.note.seq{{border-left-color:var(--blue)}} .note.auto{{border-left-color:#f59e0b}} .note.q{{border-left-color:#27ae60}}
footer{{padding:28px 0 48px;color:var(--ink-3);font-size:.76rem;text-align:center}}
@media print{{body{{background:#fff}}.tl-scroll{{overflow:visible}}details{{}}details p{{display:block}}}}
</style></head><body>''')

    # HERO
    H.append(f'''<header class="hero"><div class="wrap">
<div class="mono" style="color:rgba(255,255,255,.7)">Genactiv.pl · Roadmapa Wzrostu E-commerce · H2 2026 · Claude Code + MCP (Shopify · Klaviyo · GA4)</div>
<h1 class="serif">Plan dojścia do <em>+50% YoY</em> w grudniu 2026</h1>
<p class="sub">5 streamów × 7 miesięcy, liniowo. Każdy punkt ma <b>priorytet</b> (P1/P2/P3), oznaczenie <b>kto wykonuje</b> (Claude Code / hybryda / ręcznie), a deliverable dodatkowo <b>szacowany wzrost KPI</b>. Kliknij „▸ i" przy dowolnym punkcie, by rozwinąć: co to jest, dlaczego znalazło się w tym miejscu i jak jest priorytetyzowane.</p>
<div style="display:flex;gap:10px;flex-wrap:wrap">
<span class="pill"><span class="d"></span>Cel: 222 657 → 334 000 PLN/mies. (+50%)</span>
<span class="pill"><span class="d"></span>Do wygenerowania: +112 694 PLN/mies.</span>
<span class="pill"><span class="d"></span>czerwiec → grudzień 2026</span></div>
<span class="warn">⚠ Baseline = grudzień 2025–maj 2026. DO ODŚWIEŻENIA o dane od stycznia 2026 (pull z MCP w Claude Code — prompt w stopce).</span>
</div></header>''')

    # KPI
    H.append('''<section><div class="wrap"><div class="shead"><span class="n">01</span><h2 class="serif">Baseline → Target</h2><p>Liczby do odświeżenia o okres od stycznia 2026.</p></div>
<div class="kpis">
<div class="kpi"><div class="lbl">Przychód / mies.</div><div class="val">222 657 PLN</div><div class="delta">→ 334 000 · +50%</div></div>
<div class="kpi"><div class="lbl">Konwersja (CR)</div><div class="val">2,34%</div><div class="delta">→ 3,10% · +0,76pp</div></div>
<div class="kpi"><div class="lbl">AOV</div><div class="val">272 PLN</div><div class="delta">→ 305 · +12%</div></div>
<div class="kpi"><div class="lbl">Lista email</div><div class="val">7 972</div><div class="delta">→ 14 000 · +76%</div></div>
<div class="kpi"><div class="lbl">Repeat purchase</div><div class="val">55%</div><div class="delta">→ 62% · +7pp</div></div>
</div></div></section>''')

    # STREAMS
    H.append('<section style="background:#fff;border-top:1px solid var(--line);border-bottom:1px solid var(--line)"><div class="wrap"><div class="shead"><span class="n">02</span><h2 class="serif">Streamy, levery i wkład w cel</h2><p>Pięć filarów. Każdy z KPI, szacowanym wkładem miesięcznym i lewarami.</p></div><div class="streams">')
    for s in STREAMS:
        lis = "".join(f"<li>{esc(l)}</li>" for l in s["levers"])
        H.append(f'''<div class="sc" style="--ac:{s['color']}"><div class="tag"><span class="ch">{s['id']}</span>{esc(s['name'])}</div>
<div class="kpi-line">KPI: {esc(s['kpi'])}</div><div class="contrib">{esc(s['contrib'])}</div>
<div class="lev-h">Levery</div><ul>{lis}</ul></div>''')
    H.append('</div></div></section>')

    # TIMELINE
    H.append('<section><div class="wrap"><div class="shead"><span class="n">03</span><h2 class="serif">Roadmapa liniowa · czerwiec → grudzień 2026</h2><p>Wiersz = stream. Kolumna = miesiąc. Pasek sezonowości na górze, impact na dole.</p></div>')
    H.append('<div class="toolbar"><button class="btn" onclick="document.querySelectorAll(\'details\').forEach(d=>d.open=true)">Rozwiń wszystkie opisy</button><button class="btn sec" onclick="document.querySelectorAll(\'details\').forEach(d=>d.open=false)">Zwiń wszystkie</button></div>')
    H.append('<div class="tl-scroll"><div class="tl">')
    # header
    H.append('<div class="corner"><span class="big serif">Stream / Miesiąc</span><span class="sm">prace + deliverable</span></div>')
    for m in MONTHS:
        pk = " peak" if m.get("peak") else ""
        H.append(f'<div class="mhead{pk}"><div class="mo">{esc(m["name"])}</div><div class="theme">{esc(m["theme"])}</div></div>')
    # seasonality row
    H.append('<div class="srow-h"><span class="t">Sezonowość</span><span class="k">kategorie + handel</span></div>')
    for m in MONTHS:
        sv = SEASON[m["k"]]
        H.append(f'''<div class="scell">
<div class="sbar"><span class="sdot" style="background:{SEASON_COLOR[sv['odp']]}"></span>Odporność/Colostrum: {SEASON_LABEL[sv['odp']]}</div>
<div class="sbar"><span class="sdot" style="background:{SEASON_COLOR[sv['gut']]}"></span>Gut/Fiberbiom: {SEASON_LABEL[sv['gut']]}</div>
<div class="ev">◆ {esc(sv['ev'])}</div></div>''')
    # stream rows
    for s in STREAMS:
        H.append(f'<div class="rh" style="--ac:{s["color"]}"><span class="t">{s["id"]} · {esc(s["name"].split("/")[0].strip())}</span><span class="k">{esc(s["kpi"].split("·")[0].strip())}</span></div>')
        for m in MONTHS:
            work, deliv = CELLS[s["id"]][m["k"]]
            H.append(f'<div style="--ac:{s["color"]}">{cell_html(work, deliv)}</div>')
    # impact row
    H.append('<div class="ir-h"><span class="t">Δ Impact</span><span class="k">inkrement./mies.</span></div>')
    mx = max(v[0] for v in IMPACT.values())
    for m in MONTHS:
        val, rev, pct = IMPACT[m["k"]]
        hpx = int(28 + (val / mx) * 102)
        pk = " peak" if m.get("peak") else ""
        H.append(f'<div class="icell"><div class="bar{pk}" style="height:{hpx}px"><span>+{val}K</span></div><div class="cum">→ {rev} · {pct} celu</div></div>')
    H.append('</div></div>')  # tl, tl-scroll

    # legend
    H.append('''<div class="legend">
<div class="it"><span class="sw" style="background:var(--line-2)"></span>Prace</div>
<div class="it"><span class="sw" style="background:color-mix(in srgb,#0066CC 14%,#fff);border:1px solid #0066CC"></span>Deliverable</div>
<div class="it"><span class="tagb" style="background:#EF3340">P1</span><span class="tagb" style="background:#f59e0b">P2</span><span class="tagb" style="background:#9ca3af">P3</span>priorytet</div>
<div class="it"><span class="tagb" style="background:#0066CC">CC</span>Claude Code</div>
<div class="it"><span class="tagb" style="background:#8b5cf6">CC+</span>hybryda</div>
<div class="it"><span class="tagb" style="background:#6b7280">MAN</span>ręcznie / specjalista</div>
<div class="it"><span class="kpiup">+X%</span>szac. wzrost KPI</div>
<div class="it">▶ kamień milowy</div></div>''')
    H.append('</div></section>')

    # NOTES
    H.append('''<section style="background:#fff;border-top:1px solid var(--line)"><div class="wrap"><div class="shead"><span class="n">04</span><h2 class="serif">Zasady, sezonowość i decyzje</h2><p>Logika kolejności, sezonowości i odpowiedzi na kluczowe pytania.</p></div><div class="notes">
<div class="note q"><h4>Dlaczego nie 100 surowych artykułów w jeden dzień?</h4><p>Robimy <b>dużą partię (60–100) już w czerwcu</b> dzięki content engine — to świadoma, agresywna decyzja. Ale colostrum to treści zdrowotne (YMYL): Google trzyma wysoki próg jakości, a masa thin/duplikatów potrafi <b>zaszkodzić</b> całej domenie. Stąd: generujemy automatem, ale publikujemy <b>falami z human QA medycznym</b> i kierujemy budżet indeksacji na strony z realną intencją. Bonus strategiczny: publikujemy w martwym sezonie (lato), żeby zrankować PRZED jesiennym szczytem.</p></div>
<div class="note seq"><h4>Sekwencja LTV i priorytety</h4><p>Bundle (VI) → <b>Subskrypcja (VII)</b> → <b>Lojalność (VIII)</b> → Referral (IX). Lojalność projektowana PO subskrypcji, bo musi z nią współgrać (bonus punktów za sub). P1 = ścieżka krytyczna i najwyższe ICE (fix SEO 648/630, cadence 576, nowy layout, subskrypcja). P2 = wysokie, P3 = wspierające.</p></div>
<div class="note auto"><h4>Sezonowość = sterownik kalendarza</h4><p>Colostrum/odporność: szczyt IX–II (sezon infekcyjny), dno VII–VIII. Fiberbiom/gut: stabilny, wzrost IX i I (postanowienia). Dlatego content odpornościowy front-ładujemy latem, kampanie 'Back to Health' i churn-prevention odpalamy we wrześniu, a Replenishment flow dopina cykliczność FMCG. BFCM (XI) i święta/NY (XII) to nakładka handlowa na sezon zdrowotny.</p></div>
</div>
<div class="notes" style="margin-top:14px">
<div class="note"><h4>Loyalty — pogłębione podejście (FMCG)</h4><p>Model dla produktu cyklicznego, nie fashion: nagradzamy <b>powtarzalność i replenishment</b>, nie tylko wartość koszyka. Tiery (Bronze/Silver/Gold) wg liczby zamówień + earn za zakup/recenzję/polecenie; redemption kalibrowane do niskiej marży. Integracja: bonus punktów za subskrypcję, punkty pushują 2. zakup i cross na nowe kategorie. Sekwencja: research VII → projekt VIII → launch VIII → ewolucja XII.</p></div>
<div class="note"><h4>Co robi Claude Code, a co człowiek</h4><p><b>Claude Code (CC):</b> bulk SEO fixes, generowanie artykułów/opisów/meta, programmatic pages, LP Generator, segmentacja RFM, dashboardy, schema, personalizacja. <b>Hybryda (CC+):</b> flows Klaviyo (draft+copy), A/B (warianty+analiza), content (gen+QA medyczne). <b>Ręcznie (MAN):</b> link building/guest posty, UX audit, decyzje merch/pricing, wybór i konfiguracja apek (subskrypcja, lojalność), compliance RODO.</p></div>
<div class="note"><h4>Checkout — bez zmian</h4><p>Checkout jest już one-page — <b>nie testujemy ani nie przebudowujemy układu</b>. Stream B utrzymuje go (niezawodność, backup gateway, monitoring pod BF), a całą energię CRO kieruje na layout, PDP, koszyk, social proof i personalizację.</p></div>
</div></div></section>''')

    H.append('''<footer><div class="wrap">
Genactiv.pl · Roadmapa Wzrostu E-commerce H2 2026 · cel +50% YoY · estymacje impactu kierunkowe i konserwatywne.<br>
<b>Prompt do Claude Code (odświeżenie danych od stycznia 2026):</b> „Pobierz z MCP (Shopify, Klaviyo, GA4 property 279858535) dane za okres 2026-01-01 → dziś: przychód netto i liczba zamówień (Shopify), AOV, items/order, repeat purchase rate, sesje + CR overall/mobile/desktop + udział kanałów (GA4), liczba profili i revenue z flows/kampanii (Klaviyo). Przelicz baseline miesięczny, zaktualizuj target +50% i podmień liczby w build_roadmap.py (BASELINE/IMPACT), po czym wygeneruj HTML."
</div></footer></body></html>''')

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("".join(H))
    print("OK ->", OUT)

if __name__ == "__main__":
    build()

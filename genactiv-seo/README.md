# Genactiv SEO + GEO — pakiet agentów do Claude Code

Zestaw agentów i workflow SEO oraz GEO (AI-search) dla marki Genactiv (suplementy z colostrum, Shopify przez MCP z prawem zapisu, PL). Agenci nie tylko audytują — realnie WDRAŻAJĄ zmiany przez Shopify MCP, z bramką compliance i zasadami bezpieczeństwa.

## Uruchomienie
Pakiet jest częścią repozytorium `genactiv-klaviyo`. Nie wymaga osobnej instalacji — wystarczy `git pull`.

```bash
cd genactiv-klaviyo/genactiv-seo
claude
```
W Claude Code sprawdź: `/mcp` (czy Shopify + GA4 podłączone). MCP konfiguracja dziedziczy się z głównego `.mcp.json`.
Za każdym razem pracuj z tego folderu: `cd genactiv-seo` → `claude`. (Po edycji pliku agenta zrestartuj sesję.)

## Agenci (planowane — pliki `.claude/agents/` do stworzenia)
| Agent | Rola |
|---|---|
| `seo-orchestrator` | Planuje i deleguje; zacznij tu przy złożonych zadaniach |
| `seo-tech-auditor` | Technika przez Shopify MCP + żywe strony; audyt i wdrożenia |
| `seo-content-strategist` | Research darmowy + pisanie treści SEO+GEO + publikacja przez MCP |
| `seo-geo-specialist` | Cytowalność w AI, encja marki, monitoring widoczności w AI |
| `seo-schema-specialist` | JSON-LD (SEO+GEO), wdrożenie przez MCP |
| `seo-data-analyst` | GA4+Shopify teraz (+GSC później) + monitoring AI |
| `seo-internal-linking` | Klastry i linkowanie, wdrożenie przez MCP |
| `seo-eeat-compliance` | OBOWIĄZKOWA bramka: E-E-A-T + oświadczenia zdrowotne |
| `seo-reporter` | Raporty wpływu (przed/po, w czasie, kumulatywnie) + dashboard HTML |
| `seo-measurement-qa` | QA pomiaru GA4/Shopify (fundament wiarygodnych raportów) |
| `seo-reviews` | Program recenzji: konwersja + E-E-A-T + gwiazdki (ostrożnie) |
| `seo-product-feed` | Dane produktowe pod Google Shopping i AI |

## Komendy (planowane — pliki `.claude/commands/` do stworzenia)
- `/seo-audit [obszar]` — pełny audyt (technika + schema + GEO + linki + E-E-A-T)
- `/geo-audit [obszar]` — audyt widoczności w AI + plan
- `/optimize-product [handle]` — pełna optymalizacja produktu z wdrożeniem przez MCP
- `/content-brief [fraza]` — brief treści z researchem i compliance
- `/schema-check [strona]` — audyt + generacja/wdrożenie JSON-LD
- `/ga4-insights [zakres]` — wnioski z GA4/Shopify → działania
- `/report [okres]` — raport wpływu (przed/po, w czasie, kumulatywnie) → markdown + dashboard HTML
- `/log-change [opis]` — ręczny wpis do dziennika zmian (dla zmian spoza Claude Code)
- `/measurement-qa [okno]` — sprawdź wiarygodność pomiaru przed raportowaniem
- `/quick-wins [zakres]` — (po GSC) near-ranking i luki CTR
- `/indexnow [url-e]` — szybkie zgłoszenie zmian do Bing/IndexNow (GEO)

## Bezpieczeństwo (żywy sklep, nisza zdrowotna)
Reguły w `.claude/seo/implementation-rules.md`:
- Każdy zapis przez MCP: pokaż PRZED/PO → potwierdzenie → zapis → log zmian.
- Treść zdrowotna zawsze po `seo-eeat-compliance`.
- Zmiany masowe tylko za wyraźną zgodą; nie ruszać cen/stanów/statusu bez świadomej zgody.

## Podłączanie MCP
Agenci z danymi/zapisem mają celowo pominięte pole `tools` (dziedziczą wszystkie narzędzia sesji, w tym Shopify/GA4 MCP). Chcesz zawęzić? Dodaj w ich frontmatterze `tools` z nazwami MCP `mcp__<serwer>__<narzędzie>` (dokładne nazwy przez `/mcp`).

## Gdy dojdzie Google Search Console
Podepnij MCP GSC → włącz „tryb GSC" w `seo-data-analyst` → przenieś GSC w `stack.md` z „później" do „teraz" → możesz dorobić `/quick-wins` na wzór `/ga4-insights`.

## Zastrzeżenie
`.claude/seo/health-claims-pl.md` to filtr redukujący ryzyko, NIE porada prawna. Finalne oświadczenia zdrowotne potwierdzaj z działem regulacyjnym/prawnym Genactiv. Dla colostrum brak dopuszczonych oświadczeń zdrowotnych w UE — traktuj poważnie, także w treściach „pod AI".


## Raportowanie (jak mierzysz efekt)
Każda zmiana wdrożona przez MCP zapisuje się w `.claude/seo/changelog.jsonl`. Komenda `/report` uruchamia `seo-reporter`, który:
- liczy przed/po dla każdej zmiany z danych GA4 (sesje organic, konwersje, przychód) na poziomie strony,
- buduje oś czasu ze znacznikami wdrożeń i ujęcie kumulatywne,
- zapisuje `reports/report-YYYY-MM-DD.md` (do udostępniania) i `reports/dashboard-YYYY-MM-DD.html` (otwierasz w przeglądarce).
Raporter jest uczciwy co do atrybucji: sygnalizuje sezonowość suplementów, okno dojrzewania i to, że bez GSC nie ma jeszcze pozycji/CTR.
Zmiany zrobione poza Claude Code dodasz ręcznie przez `/log-change`.


## Podłączenie Google Search Console
Pełna instrukcja krok po kroku: `.claude/seo/gsc-activation.md`. W skrócie: załóż property typu Domena (`sc-domain:genactiv.pl`), zweryfikuj przez DNS/Shopify, prześlij sitemap, podłącz do Claude Code (konektor hostowany „no-code" albo lokalny serwer społecznościowy `mcp-gsc`), przenieś GSC w `stack.md` do „teraz" i używaj `/quick-wins`. Uwaga: dane GSC mają opóźnienie ~2–3 dni; serwery GSC poza oficjalnym GA4 to strony trzecie — nadawaj minimalne, read-only uprawnienia.

## Rutyna
Zobacz `.claude/seo/cadence.md` — co uruchamiać co tydzień / miesiąc / kwartał. Kolejność wdrażania priorytetów: measurement QA → GSC → Bing/IndexNow, recenzje, feed.
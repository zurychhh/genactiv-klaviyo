# A1 — Keyword research top 20 PDP + gap analysis + mapa sezonowa fraz

> **WYKONANE 2026-08-17 — status `needs-verify` (brama ręczna, owner CC+).**
> Wyniki i pełny opis: [`artefakty/README-A1.md`](artefakty/README-A1.md).
> DoD: `research/keyword-map-2026.csv` + `artefakty/gap-analysis-2026-08-17.csv` (882 luki).
>
> **Korekta briefu:** oryginalny tytuł zadania brzmiał „gap analysis (Colostrigen, Immuno Lab)".
> Obie nazwy okazały się błędne — **Colostrigen to nasza własna marka**
> („Colostrum Genactiv (Colostrigen)", producent GENACTIV TRADE), a `immunolab.com.pl`
> to firma mikrobiologiczna bez pokrycia tematycznego. Gap analysis zrobiona na realnych
> konkurentach z Senuto `competitors/getData`: **genoscope.pl** (134 wspólne frazy),
> colostrumactive.pl, colostrumpolska.pl. Prompt poniżej jest oryginalny — zostawiony
> jako zapis tego, co zlecono; wykonanie odbiegło od niego świadomie.

**Sprint:** Tydzień 1 (W1)
**Daty:** 1–7 cze (pon–niedz)
**Stream:** A — SEO / Organic
**Owner:** CC+ / Hybryda
**Priorytet:** P1
**Estymacja:** 8h
**Wplyw KPI:** enabler (cały stream A)
**Zaleznosci:** —
**Status poczatkowy:** Do zrobienia
**Brama reczna:** Weryfikacja ręczna przed Done

## Definition of Done

Mapa fraz primary+secondary per top 20 PDP; lista luk vs 2 konkurentów; tag sezonowy (odporność=jesień/zima). Zapis: research/keyword-map-2026.csv.

## Prompt Claude Code

W Claude Code: użyj senuto-mcp (domain=genactiv.pl, country_id=200, fetch_mode=topLevelDomain) — pobierz frazy dla top 20 produktów po sesjach z GA4. Dla każdej frazy: volume, pozycja, trudność. Zrób gap analysis vs colostrigen.pl i immunolab — frazy gdzie oni są w TOP10 a my nie. Otaguj frazy sezonowo (odporność=Q4/Q1). Wynik zapisz jako research/keyword-map-2026.csv (kolumny: pdp_url, primary_kw, secondary_kw, volume, our_pos, comp_gap, season).

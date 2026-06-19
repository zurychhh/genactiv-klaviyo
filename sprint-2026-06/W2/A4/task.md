# A4 — Content/Copy engine v1 + generacja 1. partii (20–30 artykułów draft)

**Sprint:** Tydzień 2 (W2)
**Daty:** 8–14 cze
**Stream:** A — SEO / Organic
**Owner:** CC / Claude Code
**Priorytet:** P1
**Estymacja:** ciągłe
**Wplyw KPI:** content velocity (SEO)
**Zaleznosci:** A1, E2
**Status poczatkowy:** Zablokowane (zależność)
**Brama reczna:** Weryfikacja ręczna przed Done

## Definition of Done

Engine generuje artykuł z briefu+frazy (struktura H2/H3, schema FAQ, meta); 20–30 draftów w kolejce do QA medycznego.

## Prompt Claude Code

W Claude Code: zbuduj content engine — funkcja: input(primary_kw, secondary_kw[], intent, produkt_powiązany) → output(tytuł SEO, meta description, artykuł 800–1200 słów PL z H2/H3, sekcja FAQ ze schema, wewnętrzne linki do PDP, CTA). Źródło fraz: research/keyword-map-2026.csv (tag season). Wygeneruj 20–30 draftów dla fraz odpornościowych (sezon Q4 — publikujemy latem, by zrankować przed jesienią). Zapisz do research/content-drafts/. NIE publikuj — czekają na QA medyczne (A6).

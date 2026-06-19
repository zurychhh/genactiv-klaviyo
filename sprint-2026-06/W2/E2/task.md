# E2 — LP Generator v1 — szablony Liquid (product LP + condition LP)

**Sprint:** Tydzień 2 (W2)
**Daty:** 8–14 cze
**Stream:** E — Automatyzacja / LP
**Owner:** CC / Claude Code
**Priorytet:** P1
**Estymacja:** 10h
**Wplyw KPI:** enabler (LP throughput)
**Zaleznosci:** E1
**Status poczatkowy:** Zablokowane (zależność)
**Brama reczna:** Weryfikacja ręczna przed Done

## Definition of Done

2 szablony renderują się z configu, deploy via Pages API, output w pełni edytowalny w panelu Shopify; zgodne z brand guidelines.

## Prompt Claude Code

W Claude Code: zaimplementuj 2 szablony LP Generatora (Liquid): (1) product LP, (2) condition LP. Sekcje: hero, benefits_grid, product_showcase, testimonials (judge_me), faq (+schema), content_block, cta_banner. Kolory brand: #0066CC, CTA #EF3340, font Branding-medium. Deploy przez Pages API. Warunek krytyczny: po deployu strona MUSI być edytowalna w Shopify Pages (nie hardkoduj tak, by blokować edycję). Test: postaw /pages/colostrum-na-odpornosc i potwierdź edytowalność.

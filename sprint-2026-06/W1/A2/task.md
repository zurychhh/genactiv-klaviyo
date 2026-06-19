# A2 — Pull SEO audit + plan bulk-fix (338 alt, 59 meta titles, 18 meta desc)

**Sprint:** Tydzień 1 (W1)
**Daty:** 1–7 cze (pon–niedz)
**Stream:** A — SEO / Organic
**Owner:** CC / Claude Code
**Priorytet:** P1
**Estymacja:** 4h
**Wplyw KPI:** enabler (SEO health)
**Zaleznosci:** —
**Status poczatkowy:** Do zrobienia
**Brama reczna:** Weryfikacja ręczna przed Done

## Definition of Done

Eksport audytu z Shopify Extended; lista fixów z priorytetem; dry-run gotowy do odpalenia w W2.

## Prompt Claude Code

W Claude Code: odpal SEO audit z shopify-mcp-extended (scope=all). Wyeksportuj listę: obrazy bez alt (338), produkty bez meta title (59), bez meta description (18). Pogrupuj per typ i przygotuj payloady do bulk-update-seo (pamiętaj limit 25 items/wywołanie, użyj dry-run). NIE wykonuj jeszcze zapisu — tylko dry-run i raport co zostanie zmienione. Zapisz plan jako research/seo-fix-plan.md.

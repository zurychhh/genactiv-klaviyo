# C2 — Build Post-Purchase flow (2 maile: thank you + cross-sell)

**Sprint:** Tydzień 2 (W2)
**Daty:** 8–14 cze
**Stream:** C — Klaviyo / Email
**Owner:** CC+ / Hybryda
**Priorytet:** P1
**Estymacja:** 6h
**Wplyw KPI:** email rev. +PLN 4K
**Zaleznosci:** C1
**Status poczatkowy:** Zablokowane (zależność)
**Brama reczna:** Weryfikacja ręczna przed Done

## Definition of Done

Flow live w Klaviyo; mail 1 (thank you, T+0) i mail 2 (cross-sell powiązanych kategorii, T+5); przetestowane na profilu testowym.

## Prompt Claude Code

W Claude Code: przez klaviyo-mcp zbuduj Post-Purchase flow wyzwalany 'Placed Order'. Mail 1 (delay 0): podziękowanie + jak stosować produkt (edukacja, retencja). Mail 2 (delay 5 dni): cross-sell — jeśli kupił colostrum, poleć fiberbiom i odwrotnie (event.ProductName warunkowo). Pełny HTML inline CSS, max 600px, {% unsubscribe 'Anuluj subskrypcję' %}. Obrazy najpierw upload przez klaviyo_upload_image_from_url. Copy PL dopisuje/zatwierdza człowiek przed włączeniem.

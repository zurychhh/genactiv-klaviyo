# C1 — Setup segmentacji RFM w Klaviyo + szkielety copy kampanii

**Sprint:** Tydzień 1 (W1)
**Daty:** 1–7 cze (pon–niedz)
**Stream:** C — Klaviyo / Email
**Owner:** CC / Claude Code
**Priorytet:** P1
**Estymacja:** 4h
**Wplyw KPI:** enabler (email rev.)
**Zaleznosci:** —
**Status poczatkowy:** Do zrobienia
**Brama reczna:** Weryfikacja ręczna przed Done

## Definition of Done

Segmenty RFM utworzone (champions, loyal, potential, at-risk, hibernating) z baseline liczebności; 3 szablony copy gotowe.

## Prompt Claude Code

W Claude Code: przez klaviyo-mcp utwórz segmenty RFM na bazie historii zamówień: Champions (recent+często+dużo), Loyal, Potential Loyalist, At-Risk, Hibernating, New. Zwróć liczebność każdego segmentu (baseline). Dodatkowo wygeneruj 3 szablony copy PL (newsletter edukacyjny, promo, restock) z {{ first_name|default:"" }} i {% unsubscribe 'Anuluj subskrypcję' %}.

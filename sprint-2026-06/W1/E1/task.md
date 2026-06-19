# E1 — Spec review LP Generatora + test integracji Shopify Pages API + schema design

**Sprint:** Tydzień 1 (W1)
**Daty:** 1–7 cze (pon–niedz)
**Stream:** E — Automatyzacja / LP
**Owner:** CC / Claude Code
**Priorytet:** P1
**Estymacja:** 6h
**Wplyw KPI:** enabler (throughput A+B)
**Zaleznosci:** —
**Status poczatkowy:** Do zrobienia
**Brama reczna:** Weryfikacja ręczna przed Done

## Definition of Done

Config JSON schema zatwierdzony; auth Pages API działa; 1 strona testowa zdeployowana i edytowalna w panelu Shopify.

## Prompt Claude Code

W Claude Code: na bazie docs/MIGRATION_PLAN_ONLINE.md i sekcji LP Generator zweryfikuj config schema (lp_type, hero, sections[], seo, tracking). Przetestuj shopify_theme_api.py / Shopify Pages API: utwórz testową stronę /pages/lp-test z 1 sekcją hero, potwierdź że jest edytowalna w panelu Shopify (Online Store → Pages). Zwróć: status auth, ID strony, link, checklist co działa/co brakuje.

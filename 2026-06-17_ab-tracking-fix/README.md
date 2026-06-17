# Fix tagowania A/B (GA4 + Clarity) — 2026-06-17

Test A/B **GEN-6 vs NOTOAGENCY** (Intelligems, exp `1c371ad8-5826-4c21-abdb-7d0d68390e81`).
Punkt wyjścia: raport z 16.06 stwierdzał, że tagowanie wariantu „nie działa" (~21% pokrycia w GA4, pusto w Clarity) i błędnie diagnozował przyczynę jako *timing gtag vs Pandectes consent*. Ta sesja ustaliła faktyczne przyczyny i wdrożyła poprawki.

## Zawartość folderu

| Plik | Co to |
|---|---|
| `AB_TEST_WERYFIKACJA_2026-06-16.html` | **Zaktualizowany raport** (kopia z `reports/`) — poprawiona przyczyna + status fixów |
| `CLARITY_SCIAGA_NOTO.html` | Ściąga: jak po 24–48 h oglądać nagrania NOTO w Clarity (filtry, na co patrzeć) |
| `fix_clarity_tagging.py` | Skrypt, który naprawił snippet Clarity w obu motywach (idempotentny, dry-run domyślnie) |
| `theme_backups_przed_fixem/` | Backupy `layout/theme.liquid` obu motywów SPRZED edycji (do ew. rollbacku) |

## Co ustalono (diagnoza)

**Motywy (uwaga — CLAUDE.md mylił ID):**
- Aktywny/published = `199333609804` (GEN-6 fix payment icons) — serwuje genactiv.pl.
- NOTOAGENCY (wariant, serwowany przez Intelligems mimo unpublished) = `190479794508`.
- `162539340108` to STARY unpublished — nie mylić.

**GA4 — tag z motywu nie działa, bo GA4 jest w sandboxie.** GTM (`GTM-5W5Z2ML`) zakomentowany w obu motywach; ID GA4 nie ma w `theme.liquid`. GA4 ładuje się tylko przez kanał Google&YouTube → **sandbox Web Pixels**, który nie czyta `dataLayer` motywu. Dlatego `gtag('set', user_properties)` ze snippetu nigdy nie dociera do GA4 (~21%).

**Clarity — błąd w snippecie.** `clarity("set", …)` był pod `if (typeof clarity === 'function')`, który na górze `<head>` jest `false` (loader Clarity jeszcze nie wystartował) → blok pomijany bez retry → tag pusty.

## Co wdrożono (fixy)

1. **Clarity (NAPRAWIONE, oba motywy)** — `fix_clarity_tagging.py` zamienił guard na polling `window.clarity` (co 500 ms, do ~30 s). Push przez Shopify Asset API. Backupy w `theme_backups_przed_fixem/`.
   - ⚠️ Storefront chwilowo serwował starą wersję przez full-page cache Shopify — edycja potwierdzona w źródle (Asset API), cache propaguje minuty–~1 h.
2. **GA4 (NAPRAWIONE inaczej niż sądził raport)** — integracja **Intelligems → GA4 już działa**: zdarzenie `experience_impression` (3129/28 dni, server-side, pełne pokrycie). Brakowało tylko rejestracji parametrów jako **custom dimensions**. Zarejestrowano przez GA4 Admin API (EVENT scope, zestaw pokrywający): `variant_name`, `variant`, `experience_name`, `experiment_name`.

## Follow-up (do zrobienia za 24–48 h)

- [ ] **Clarity:** w dashboardzie (projekt `3354986136401458`) sprawdzić, czy custom tag `ab_theme_variant` pokazuje `GEN-6`/`NOTOAGENCY`; oglądać nagrania NOTO wg `CLARITY_SCIAGA_NOTO.html`.
- [ ] **GA4:** sprawdzić (Data API, `customEvent:<param>` przy `eventName=experience_impression`), **która z 4 zarejestrowanych nazw się zapełnia** → zostawić ją, resztę zarchiwizować.
- [ ] **BigQuery (opcjonalnie, dane historyczne):** eksport GA4 jest w projekcie GCP `277470194697` (dataset `analytics_279858535`), ale konto `doperacz1935@gmail.com` nie ma tam IAM. Poprosić właściciela projektu (agencja) o `roles/bigquery.jobUser` + `roles/bigquery.dataViewer`.

## Ograniczenia

- Clarity najpewniej **nie nagrywa hostowanego checkoutu Shopify** → przeciek NOTO w checkoucie (porzucenia +43%) diagnozować z Intelligems, nie z Clarity.
- Rejestracja custom dimension w GA4 **nie działa wstecz** — dane per-wariant dopiero od 17.06.

---
*Oryginały: skrypt i raporty są też w `../reports/` i w roocie repo. Ten folder to czytelny snapshot pracy z 17.06.*

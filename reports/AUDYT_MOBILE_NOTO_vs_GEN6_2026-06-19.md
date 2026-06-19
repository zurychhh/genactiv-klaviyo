# Audyt mobile per-layout — GEN-6 vs NOTOAGENCY
**Data:** 2026-06-19 · **Dla:** specjalista CRO · **Źródło danych ilościowych:** Intelligems (czysty rozdział wariantów)

---

## 0. Kontekst i stan techniczny (zweryfikowany — zero zmian w motywach)

- **Test:** Intelligems „New theme" `1c371ad8-5826-4c21-abdb-7d0d68390e81`, typ **theme test**, start **2026-06-08**, split **80/20**, status *started*.
- **Arms:**
  - **Control (80%) = GEN-6 = motyw `199333609804`** „GEN-6 fix payment icons" = **żywy MAIN** (serwuje genactiv.pl). Wariant Intelligems `5c618faa-9a84-43f8-9434-298c089b1e03`.
  - **Wariant (20%) = NOTOAGENCY = motyw `190479794508`** (unpublished, serwowany przez Intelligems). Wariant Intelligems `3983b13b-d16e-4192-9db1-89f3bf1a62ae`.
  - ⚠️ Motyw `162539340108` („GEN-6 global - slideshow") jest **poza testem** — stary, nie mylić z control.
- **Tagowanie Clarity:** oba żywe arm **już mają** blok „A/B Test Theme Identifier" w `<head>` (`ab_theme_variant` = `GEN-6` / `NOTOAGENCY`, polling `window.clarity`, fix 2026-06-17). **Iniekcja niepotrzebna.**
- **Konektor Clarity↔Intelligems:** integracja Clarity w Intelligems = **enabled** (od 2026-06-15) → sesje tagowane wariantem.
- **OGRANICZENIE:** Clarity API/MCP **nie filtruje po custom tagu**, a oba motywy serwują na **tych samych URL-ach** → rozdział per-layout w Clarity możliwy **wyłącznie w UI Clarity** (filtr po `ab_theme_variant`). Dane ilościowe per-layout pochodzą z Intelligems.

---

## 1. Lejek mobile — całość (od 2026-06-08)

| Krok (mobile) | GEN-6 (control) | NOTOAGENCY (wariant) | Δ rel. |
|---|---|---|---|
| Wizyty | 10 370 | 1 507 | — |
| View collection | 46,0% | 47,3% | +2,8% |
| View product (PDP) | 40,1% | 41,0% | +2,3% |
| **Add to cart** | **7,28%** | **6,37%** | **−12,5%** |
| Begin checkout | 4,49% | 3,92% | −12,9% |
| Konwersja | 3,23% | 2,59% | **−19,9%** (p2bc 10%) |
| Abandoned checkout rate | 28,8% | 35,6% | +23,8% (gorzej) |
| AOV | 243,24 zł | 230,36 zł | −5% |
| Sztuk/zam. | 1,44 | 1,23 | −14,8% |
| Rev/wizytę | 7,86 zł | 5,96 zł | **−24%** (p2bc 12%) |

**Szac. wpływ pełnego wdrożenia NOTOAGENCY: −60 686 zł/mies.**
Browsing na parze (PDP/kolekcja ≈ równo), strata zaczyna się od ATC w dół.

---

## 2. Trend w czasie (cumulative, mobile) — luka się NIE zamyka

| Dzień | Konwersja uplift | Rev/wiz uplift | p2bc |
|---|---|---|---|
| 06-08 | +54% | +222% | — |
| 06-10 | −16% | +4% | — |
| 06-12 | −26% | −8% | 18% |
| 06-15 | −14% | −10% | 25% |
| 06-17 | −18% | −21% | 13% |
| **06-19** | **−20%** | **−24%** | **10%** |

- Pierwsze 2 dni („+54%") = artefakt małej próby (95 wizyt). Po ustabilizowaniu deficyt trzyma się **−15% do −24%** od ~06-11.
- `p2bc` spadło z ~25% do **~10%** → model w ~90% przekonany, że **control jest lepszy**. Kierunek stały, niesłabnący.
- Tempo wariantu ~**125 wizyt mobile/dobę** → do twardej istotności (p2bc <5%) jeszcze ~1–2 tyg.

---

## 3. Rozbicie per źródło ruchu (mobile) — deficyt NIE jest równomierny

| Kanał | Wizyty G/N | CVR GEN-6 | CVR NOTO | Δ CVR | Rev/wiz G→N | p2bc NOTO |
|---|---|---|---|---|---|---|
| **Paid Social** | 4815 / 740 | 2,43% | **2,57%** | **+0,14 pp** | 5,33 → 5,60 | **0,63** ✅ |
| **Paid Search** | 2067 / 276 | 5,22% | 3,99% | **−1,23 pp** | 13,80 → 8,59 | 0,22 ❌ |
| Organic Search | 1869 / 196 | 2,19% | 2,04% | −0,15 pp | 5,43 → 5,09 | — |
| Direct | 814 / 82 | 3,93% | 1,22% | −2,71 pp | 9,70 → 3,82 | — |

- Mix ruchu porównywalny między arm → to **realna różnica per kanał, nie artefakt struktury**.
- **Na największym kanale mobile — Paid Social — NOTO NIE przegrywa** (par/lekko wyżej, p2bc 0,63). Najpewniejszy odczyt.
- **Cały deficyt pochodzi głównie z Paid Search (i Direct).** Paid Search to najlepszy kanał GEN-6 (5,22%), więc jego osłabienie zaniża blended najmocniej.

---

## 4. Paid Search mobile — gdzie dokładnie przecieka (2 dziury)

| Krok | GEN-6 (n=2067) | NOTO (n=276) | Δ rel. |
|---|---|---|---|
| View product (PDP) | 44,6% | 47,8% | +7% (NOTO dociera do PDP **częściej**) |
| Add to cart | 11,61% | 9,06% | **−22%** |
| **PDP→ATC** (ATC/PDP-view) | ~26,1% | ~18,9% | **−28%** ← DZIURA #1 |
| Begin checkout | 7,60% | 7,25% | −5% (≈ równo) |
| **Checkout completion** (orders/started) | **68,8%** (108/157) | **55,0%** (11/20) | **−20%** ← DZIURA #2 |
| Abandoned checkout rate | 31,2% | 45,0% | +44% |
| Konwersja | 5,22% | 3,99% | −23,7% (p2bc 21%) |
| Rev/wizytę | 13,80 zł | 8,59 zł | **−38%** (p2bc 13%) |

**Wniosek:** NOTO na high-intent search traci **nie na ekspozycji, a na egzekucji**:
1. **PDP → Add to Cart (−28%)** — ruch dociera do karty produktu (nawet częściej niż na GEN-6) i tam się zatyka.
2. **Domknięcie checkoutu (55% vs 69%, +44% porzuceń)** — kto startuje checkout (≈ tak samo często), na NOTO kończy rzadziej.
Mniejszy koszyk (−14% szt., −18% AOV) dokłada się do −38% rev/wizytę.

---

## 5. Co ma zrobić CRO (protokół Clarity — UI, bo API nie rozdzieli)

Dashboard Clarity (projekt `3354986136401458`), filtr bazowy: **Device = Mobile**, zakres od **2026-06-08**, Custom tag **`ab_theme_variant` = `NOTOAGENCY`** (i porównawczo `GEN-6`). *Najpierw sprawdź, że tag ma 2 wartości — to potwierdza, że connector taguje.*

Priorytet — kanał Paid Search:
1. **PDP bez ATC** — heatmapa PDP mobile + nagrania z `rage/dead clicks` na „Dodaj do koszyka"; widoczność ceny/CTA powyżej linii zgięcia; scroll depth do ATC.
2. **Cart / Begin-checkout bez OrderSuccess** — przejście koszyk→checkout. ⚠️ Sam hostowany checkout Shopify Clarity zwykle **nie nagrywa** → porzucenia w samym checkoucie potwierdzaj w Intelligems.

**Linki podglądu:**
- GEN-6 (control, żywy): `https://genactiv.pl/` lub `https://genactiv.pl/?preview_theme_id=199333609804`
- NOTOAGENCY (wariant): `https://genactiv.pl/?preview_theme_id=190479794508`

---

## 6. Rekomendacja i zastrzeżenia

**Rekomendacja:** NOTOAGENCY na mobile konsekwentnie przegrywa (deficyt stabilny 8 dni, pewność rośnie), ale **problem jest zlokalizowany**: high-intent search (PDP→ATC + checkout), nie social. Opcje:
- **Ratować test:** naprawić PDP→koszyk i checkout dla wejść search, potem restart — nie ruszać layoutu pod social.
- **Albo** ograniczyć ekspozycję wariantu na Paid Search/Direct mobile.

**Zastrzeżenia statystyczne:** wariant mobile = 1 507 wizyt / 39 zam.; per-kanał jeszcze cieniej (Paid Search 276/11, krok „checkout completion" = 20 sesji). p2bc 10–21% → **kierunkowo mocne, ale nie istotne statystycznie**. Najpewniejszy odczyt: Paid Social (neutralny/pozytywny dla NOTO).

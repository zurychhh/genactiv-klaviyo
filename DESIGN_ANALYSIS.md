# DESIGN_ANALYSIS.md — Fiberbiom Landing Page

Analiza projektu graficznego: `Desktop - 1.png` (1440 x 5771 px)

---

## 1. Layout & Sekcje (od gory do dolu)

| # | Sekcja | Y-range (px) | Tlo | Layout |
|---|--------|-------------|-----|--------|
| 1 | **Hero** | 0–450 | Gradient ciemny czerwony (`#A42D2B` → `#B84040`) | 2 kol: tekst (lewo) + packshot na papierze toaletowym (prawo, full-bleed) |
| 2 | **Problem** | 450–800 | Bialy `#FFFFFF` | 2 kol: zdjecie produktu z rozowym dekoracyjnym prostokatem (lewo) + heading + body + CTA (prawo) |
| 3 | **Solution / About** | 800–1350 | Bialy `#FFFFFF` z rozowym dekor. prostokatem za zdjeciem | 2 kol odwrocone: heading + body + CTA (lewo) + zdjecie kobiety z produktem (prawo) |
| 4 | **How it works** | 1350–1900 | Bialy `#FFFFFF` | Heading centrowany + grid 3 karty (rozowa / jasna / burgundowa) |
| 5 | **Stats / Social proof** | 1900–2360 | Lewo: rozowy `#F67FB4`, prawo: czerwony placeholder `#EF3340` | 2 kol: duze "73%" + tekst (lewo) + obraz/video placeholder (prawo) |
| 6 | **How to use** | 2360–3270 | Bialy `#FFFFFF` | 2 kol: kolaz 7 dni tygodnia grid (lewo) + heading + instrukcja + CTA (prawo) |
| 7 | **Q&A** | 3270–4355 | Bialy `#FFFFFF` | Badge "Q&A" + 3 pytania accordion, separowane linami |
| 8 | **CTA Banner** | 4355–4940 | Rozowy `#F67FB4` | 2 kol: heading + sub + CTA (lewo) + zdjecie kobiety z produktem (prawo), dekoracyjne fale/linie |
| 9 | **Bibliografia** | 4940–5771 | Bialy `#FFFFFF` | Heading "BIBLIOGRAFIA" + lista referencji naukowych, drobny tekst |

---

## 2. Paleta kolorow (HEX z ekstrakcji pikselowej)

| Token | HEX | Uzycie |
|-------|-----|--------|
| `--fb-color-hero-bg` | `#A42D2B` | Hero tlo (gradient do `#B84040`) |
| `--fb-color-red` | `#EF3340` | CTA buttony, akcenty, headingi "How to use", karta 1 "How it works" |
| `--fb-color-pink` | `#F67FB4` | Stats tlo, CTA banner tlo, dekoracyjne elementy, tekst Q&A |
| `--fb-color-pink-medium` | `#E76C9C` | Q&A badge, tekst pytan |
| `--fb-color-burgundy` | `#610C1A` | Karta 3 "How it works" (ciemne tlo) |
| `--fb-color-white` | `#FFFFFF` | Tla sekcji, tekst na ciemnym tle |
| `--fb-color-text` | `#1A1A1A` | Glowny tekst body (na bialym tle) |
| `--fb-color-text-muted` | `#404040` | Tekst body drugorzedny |
| `--fb-color-text-light` | `#BFBFBF` | Tekst bibliografii |
| `--fb-color-pink-soft` | `#FDE5E7` | Delikatny roz — dekoracyjne prostokaty za zdjeciami |
| `--fb-color-card-light` | `#FFF0F3` | Karta 2 "How it works" (jasne tlo) |

---

## 3. Typografia

**Identyfikacja fontu:** Na podstawie ksztaltow liter (geometryczny sans-serif, zaokraglone, otwarty `a`, rownomierne proporcje) — najbardziej pasuje **Poppins** (Google Fonts). Alternatywy: Plus Jakarta Sans, Montserrat.

| Element | Size (desktop) | Weight | Line-height | Letter-spacing | Fluid clamp |
|---------|---------------|--------|-------------|----------------|-------------|
| H1 (hero) | ~48–56px | 700 (Bold) | 1.1 | -0.02em | `clamp(2rem, 4vw + 1rem, 3.5rem)` |
| H2 (section headings) | ~36–42px | 700 | 1.15 | -0.01em | `clamp(1.75rem, 3vw + 0.5rem, 2.625rem)` |
| H3 (card titles) | ~24–28px | 600 (SemiBold) | 1.2 | 0 | `clamp(1.25rem, 2vw + 0.25rem, 1.75rem)` |
| Eyebrow (nad headingami) | ~14px | 600 | 1.4 | 0.1em | `clamp(0.75rem, 1vw, 0.875rem)` |
| Body | ~16–18px | 400 (Regular) | 1.6 | 0 | `clamp(0.9375rem, 1vw + 0.25rem, 1.125rem)` |
| Small / caption | ~12–13px | 400 | 1.5 | 0.02em | `clamp(0.6875rem, 0.8vw, 0.8125rem)` |
| "73%" (stats) | ~120–160px | 800 (ExtraBold) | 1.0 | -0.03em | `clamp(5rem, 12vw, 10rem)` |
| CTA button text | ~14–16px | 600 | 1.0 | 0.05em | — |
| Q&A badge "Q&A" | ~18px | 700 | 1.0 | 0.05em | — |
| Bibliography | ~11–12px | 400 | 1.5 | 0 | — |

---

## 4. Spacing Scale

| Element | Wartosc | Fluid |
|---------|---------|-------|
| Section padding (vertical) | 80–120px | `clamp(3rem, 8vw, 7.5rem)` |
| Container max-width | 1280px | — |
| Container padding (horizontal) | 40px (desktop), 20px (mobile) | `clamp(1.25rem, 4vw, 2.5rem)` |
| Grid gap (karty) | 24–32px | `clamp(1rem, 2vw, 2rem)` |
| Element gap (tekst-tekst) | 16–24px | — |
| CTA button padding | 14px 32px | — |
| Card padding | 32–40px | `clamp(1.5rem, 3vw, 2.5rem)` |
| Card border-radius | 16–20px | 16px |
| Button border-radius | 4–6px | 4px |
| Dekoracyjny prostokat offset | ~20px w prawo, ~20px w dol | — |

---

## 5. Komponenty UI

### 5.1 Przyciski (CTA)

**Wariant primary (czerwony):**
- Background: `#EF3340`
- Text: `#FFFFFF`, uppercase, font-weight 600, letter-spacing 0.05em
- Padding: `14px 32px`
- Border-radius: `4px`
- Hover: darken 10% (`#D42D38`), subtle shadow
- 5 instancji na stronie — wszystkie parametryzowalne

**Wariant na rozowym tle (banner CTA):**
- Background: `#EF3340` (ten sam)
- Text: `#FFFFFF`
- Wiekszy — padding `16px 40px`

### 5.2 Karty (How it works)

3 karty w rzedzie, rowna wysokosc:
| Karta | Background | Tekst tytul | Tekst body | Border-radius |
|-------|-----------|-------------|------------|---------------|
| 1 — "Blonnik rozpuszczalny" | `#EF3340` | `#FFFFFF` | `#FFFFFF` | 16px |
| 2 — "Genactiv Colostrum" | `#FFF0F3` (jasny roz) | `#1A1A1A` | `#404040` | 16px |
| 3 — "Synergia dwoch substancji" | `#610C1A` (burgundy) | `#F49495` (jasny roz) | `#F1CCDE` | 16px |

Kazda karta: ikona SVG na gorze, tytul H3, body text, opcjonalnie "dowiedz sie wiecej" link.

### 5.3 Q&A Accordion

- Badge "Q&A" — rounded rectangle, bg `#E76C9C`, tekst bialy, border-radius 8px
- Pytanie: tekst rozowy/czerwony `#E76C9C`, font-weight 600
- Odpowiedz: tekst ciemny, font-weight 400
- Separator: linia 1px `#FFA2D0` (pink soft)
- Otwarcie/zamkniecie: natywny `<details>/<summary>` + CSS transition

### 5.4 Dekoracyjne prostokaty

- Sekcja Problem (za zdjeciem): prostokat `#F67FB4` z zaokragleniem ~16px, przesuniety -20px w lewo i +20px w dol wzgledem obrazu
- Sekcja Solution (za zdjeciem): identycznie, ale mirror (przesuniety w prawo)
- Realizacja: `::after` pseudo-element na kontenerze obrazu

### 5.5 Faliste linie (CTA Banner)

- 2-3 dekoracyjne linie sinusoidalne na rozowym tle
- Kolor: `#FFFFFF` z opacity ~0.2
- Realizacja: inline SVG path lub CSS `background-image` z SVG data URI

### 5.6 Kolaz 7 dni (How to use)

- Grid 3 kolumny (Pon-Pt + Sob + Ndz)
- Kazda komorka: zdjecie saszetki + label dnia tygodnia jako overlay
- Pod gridem: podpis "Codzienny rytual w 30 sekund!"
- Border-radius na komorkach: 12px

---

## 6. Obrazy — inventory

| Asset | Sekcja | Typ | Orientacja | Alt text | Loading |
|-------|--------|-----|-----------|----------|---------|
| `fiberbiom-hero.webp` | Hero | Content | Landscape/square | "Opakowania Fiberbiom na tle lazienki" | `fetchpriority="high"` |
| `fiberbiom-problem.webp` | Problem | Content | Portrait | "Fiberbiom na rozowym tle" | `lazy` |
| `fiberbiom-solution.webp` | Solution | Content | Portrait | "Kobieta z opakowaniem Fiberbiom" | `lazy` |
| `fiberbiom-stats.webp` | Stats | Content (placeholder) | Landscape | "Badanie kliniczne Fiberbiom" | `lazy` |
| `fiberbiom-week-*.webp` | How to use | Content | Square (x7) | "Saszetka Fiberbiom — [dzien]" | `lazy` |
| `fiberbiom-banner-woman.webp` | CTA Banner | Content | Portrait | "Kobieta z Fiberbiom" | `lazy` |
| Rozowe prostokaty | Problem/Solution | Dekoracja | — | `alt=""` | CSS only |
| Faliste linie | CTA Banner | Dekoracja | — | `alt=""` | CSS/SVG only |
| Ikony kart | How it works | Dekoracja | Square (3x) | `alt=""` | Inline SVG |

---

## 7. CTA Flow — hierarchia akcji

| # | Sekcja | Label CTA | Akcja docelowa |
|---|--------|----------|---------------|
| 1 | Hero | "SPRAWDZ FIBERBIOM" | Scroll do produktu lub link do PDP |
| 2 | Problem | "POZNAJ FIBERBIOM" | Scroll do sekcji Solution |
| 3 | Solution | "WYPRUBUJ FIBERBIOM" | Link do PDP |
| 4 | How to use | "KUP TERAZ" | Link do PDP / checkout |
| 5 | CTA Banner | "ZAMOW 15% TANIEJ Z KODEM 'FIBERBIOM'" | Link do PDP z kodem rabatowym |

Wszystkie CTA parametryzowalne w schema: `button_label` + `button_url`.

---

## 8. Proponowana struktura plikow

```
sections/
  fiberbiom-hero.liquid            # Sekcja 1 — hero z packshotem
  fiberbiom-problem.liquid         # Sekcja 2 — problem z dekoracyjnym prostokatem
  fiberbiom-solution.liquid        # Sekcja 3 — rozwiazanie (odwrocony layout)
  fiberbiom-how-it-works.liquid    # Sekcja 4 — 3 karty skladnikow (blocks)
  fiberbiom-stats.liquid           # Sekcja 5 — 73% social proof
  fiberbiom-how-to-use.liquid      # Sekcja 6 — kolaz + instrukcja
  fiberbiom-faq.liquid             # Sekcja 7 — Q&A accordion (blocks) + JSON-LD FAQPage
  fiberbiom-cta-banner.liquid      # Sekcja 8 — koncowy banner z kodem rabatowym
  fiberbiom-bibliography.liquid    # Sekcja 9 — referencje naukowe (blocks)
snippets/
  fiberbiom-button.liquid          # Reusable CTA button (label, url, variant)
templates/
  page.fiberbiom.json              # Template JSON z 9 sekcjami i default settings
assets/
  fiberbiom.css                    # Wszystkie style — design tokens + 9 sekcji
  fiberbiom.js                     # FAQ accordion (jesli <details> nie wystarczy)
```

### Dlaczego 1 plik CSS zamiast per-section?

- Wspoldzielone design tokens (kolory, fonty, spacing) musza byc w jednym miejscu
- Shopify laduje kazdy `stylesheet_tag` jako osobny request — 1 plik = lepszy performance
- BEM naming z prefiksem `fiberbiom-{section}__` zapobiega kolizjom
- Lacznie ~400-500 linii CSS — nie wymaga podzialu

### Template JSON

`page.fiberbiom.json` bedzie zawierac:
- `sections` z 9 entries w kolejnosci (order: 1-9)
- Kazda sekcja z `type`, `settings` (wszystkie domyslne wartosci z projektu), `blocks`
- `order` array definiujacy kolejnosc

---

## 9. Uwagi do realizacji

1. **Obrazy:** Potrzebuje dostarczenia 6-8 zdjec produktowych w wysokiej rozdzielczosci (min 1600px szerokosc). Na razie uzyje `image_picker` w schema z placeholder SVG.

2. **Font Poppins:** Zaladuje przez Google Fonts `<link>` w sekcji hero (lub w `fiberbiom.css` przez `@import`) — tylko weights 400, 600, 700, 800.

3. **Stats placeholder:** Czerwony prostokat w sekcji Stats to placeholder na obraz/video — zrealizuje jako `image_picker` w schema. Klient wgra docelowy material.

4. **Responsive kolaz:** Grid 7 dni na mobile zmieni sie z 3x3 na 2x4 lub stack.

5. **Kontrast:** Bialy tekst na `#F67FB4` rozowym tle (banner) daje contrast ratio ~2.9:1 — PONIŻEJ WCAG AA (4.5:1). Rozwiazanie: uzyte beda biale lub bardzo ciemne warianty, lub zgrubimy font (large text >=3:1). Do decyzji.

6. **JSON-LD:** Sekcja FAQ wygeneruje `FAQPage` structured data automatycznie z blokow.

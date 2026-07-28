# Genactiv — Design System

A working brand & UI design system reconstructed from the live storefront at **https://genactiv.pl/**. It packages Genactiv's colors, type, real logo + product imagery, iconography notes, voice/tone, and a high-fidelity recreation of the storefront UI so design agents can produce on-brand mockups, slides, and prototypes.

> **Source of truth:** the public Shopify storefront **https://genactiv.pl/** (theme by Brand Active, "Technologia Shopify"). There was **no codebase, Figma, or deck** supplied — everything here is reconstructed from the live site's markup, copy, exposed brand assets (logo, product photography, feature icons, payment/delivery glyphs pulled from `cdn.shopify.com`), and the site's declared `theme-color`. Treat exact font identity and the full secondary palette as **best-effort approximations** (see Caveats).

---

## 1. Company & product context

**Genactiv® (Genactiv Sp. z o.o., Poznań / Dąbrówka, Poland)** is a Polish manufacturer of dietary supplements and cosmetics built around two natural raw materials: **bovine colostrum** (*colostrum bovinum*) and **mare's milk** (*mleko klaczy*). The brand positions itself as pure, minimally processed and "100% faithful to nature," and leads with a market-leadership claim: **"Colostrum nr 1 w aptekach w Polsce"** (the #1 colostrum in Polish pharmacies, immunity category, per IQVIA MAT 12/2024).

Master tagline: **"GENACTIV®. Twój plan na zdrowie."** ("Your plan for health.")

### Product lines / surfaces represented
| Line | What it is | Visual cue |
|---|---|---|
| **Genactiv® Colostrum** | Flagship: lyophilised colostrum in capsules, tablets, powder & sachets; "Junior" kids' variants (e.g. czarny bez / elderberry). "250 active ingredients in one substance." | Brand **red** `#F5333F`, white jars, golden powder |
| **Genactiv® Fiberbiom** | Soluble fibre (larch arabinogalactan) **+** Genactiv® Colostrum for gut microbiome & barrier. "Lekkość błonnika. Moc colostrum!" | **Pink** `#F5669C` |
| **Zooggies** ("Powered by Genactiv® Colostrum") | Pet supplement line (colostrum + collagen) — also a food "dosmaczacz" (palatability topper). | Warm/playful, pet photography |
| **DERMO** | Cosmetics line using colostrum bovinum + mare's milk for mature / problematic / irritated skin. | Soft, clean, cosmetic |
| **Content / authority** | "Stan jelit Polaków" gut-health report; expert advisors (dietitian, immunologist, psychologist/trichologist); "Poradnik" blog; FAQ. | Editorial, credentialled |

**Channel:** Direct-to-consumer Shopify store (PLN), Poland-first with international shipping. Sells also through pharmacies. Social: Facebook, Instagram (`@genactiv_colostrum`), YouTube. Payments: Przelewy24, BLIK, Visa, Mastercard, Apple/Google Pay, cash-on-delivery. Delivery: DHL, InPost.

### The core product to recreate
For the purposes of this system the **storefront (Shopify marketing + commerce site)** is the single product surface. The UI kit recreates it: home/hero, product card grids, product detail, feature/benefit blocks, expert cards, and the cart drawer.

---

## 2. Files in this system  *(index / manifest)*

```
README.md                 ← you are here (context, content + visual foundations, iconography)
SKILL.md                  ← Agent-Skills entry point
colors_and_type.css       ← all color + type tokens (CSS vars) and semantic type classes
fonts/
  fonts.css               ← @font-face (self-hosted Montserrat woff2 — SUBSTITUTE, see Caveats)
  montserrat-*.woff2       ← variable woff2 (latin + latin-ext, roman + italic)
assets/
  logo-primary.png        ← full red lockup (mark + wordmark)
  logo-white.png          ← same, recolored white (for red/pink/photo backgrounds)
  logo-small.png / logo-130.png / logo-mark-white.png  ← square mark variants
  icon-smak / -naturalnosc / -forma .png  ← line-art benefit icons (hex frame)
  photo-colostrum-nr1.png ← hero: red bg, white jar, golden powder, "nr 1" badge
  photo-fiberbiom.jpg     ← pink bg, hand holding Fiberbiom box
  photo-zooggies.jpg      ← pet line product
  photo-dermo.webp        ← cosmetics line
  photo-raport-jelit.png  ← gut-health report social card
  expert-monika / -halasa / -magda .png  ← circular expert portraits
  pay-*.svg / ship-*.svg  ← Przelewy24, BLIK, cash-on-delivery, DHL, InPost glyphs
preview/                  ← Design System tab cards (swatches, specimens, tokens, components)
ui_kits/storefront/       ← high-fidelity interactive recreation of the Shopify storefront
  README.md, index.html, *.jsx
```

---

## 3. Content fundamentals  *(voice, tone, copy)*

The site is written in **Polish**, in a **warm, encouraging, second-person ("Ty")** voice. It is friendly and human, not clinical, but always backs claims with science/credentials. Sentences are short and punchy; benefit-first.

- **Person & address:** Speaks directly to *you* ("Twój plan na zdrowie", "Kiedy Twoje jelita łapią rytm…"), and uses **"we" ("my w Genactiv")** for brand intent. Inclusive, reassuring, slightly maternal ("Polecane przez mamy i lubiane przez dzieci").
- **Casing:** Headlines often **sentence case** ("Za co pokochasz nasze Colostrum?"), while **CTAs and small labels are UPPERCASE** ("KUP TERAZ", "ODKRYJ", "DOWIEDZ SIĘ WIĘCEJ", "POZNAJ", "SUPLEMENT DIETY"). The wordmark **GENACTIV®** is always uppercase + letter-spaced, always with the ® and an em-style brand period in the tagline.
- **Emphasis:** Liberal **bold** on the key phrase inside a sentence ("**unikalne połączenie**", "**rozpuszczalnego błonnika z kory modrzewia**"). Tagline set as its own line.
- **Emoji:** Yes — used sparingly in promotional/hero copy as warmth signals, typically trailing a line: 😍 💪 ❤️. Not used in nav, product specs, legal, or expert copy. Keep to 1 per line, heart/strength/love family.
- **Claims & rigor:** Marketing claims are footnoted with sources (IQVIA), and the site carries a real scientific **Bibliografia** (peer-reviewed citations) plus named experts with titles ("dr hab. n. med."). Tone = "natural but proven."
- **Recurring phrases / motifs:** "Twój plan na zdrowie", "Powered by Genactiv® Colostrum", "Synergia dwóch składników aktywnych", "czyste, nieprzetworzone, bez dodatków", "100% wierne naturze", "nr 1 w aptekach".
- **Commerce micro-copy:** urgency + reassurance — "Darmowa wysyłka od…", "GRATULACJE MASZ DARMOWĄ DOSTAWĘ", "Z wliczonym podatkiem", "Kup teraz". Free-shipping progress is a recurring device.
- **Vibe:** trustworthy Polish family-health brand; nature + science; warm red energy; confident but caring. Never edgy, never jargon-heavy, never cold.

**Example (verbatim) hero copy:**
> **Fiberbiom nadaje rytm Twoim jelitom** — Lekkość błonnika. Moc colostrum! 😍
> Fiberbiom to **unikalne połączenie** **rozpuszczalnego błonnika z kory modrzewia** i **Genactiv® Colostrum**. ❤️

---

## 4. Visual foundations

**Overall feel:** clean, warm, confident, retail-health. High-key product photography, generous whitespace, one assertive brand red doing most of the heavy lifting, soft warm-neutral section backgrounds, pill-shaped CTAs. Geometric, friendly, premium-but-accessible.

### Color
- **One dominant brand color: red `#F5333F`.** It's the theme color, the logo color, CTA color, and the background of hero/product photography. Used confidently and at large scale.
- **Secondary pink `#F5669C`** is the Fiberbiom / gut sub-brand color — used for that line's full-bleed backgrounds and accents.
- **Warm neutrals**, not cool greys: off-whites lean cream (`#F4F1EE`, `#FBEFE2`), text is a near-black warm ink `#1C1B1B`. Avoid blue-greys.
- **Colostrum gold/cream** appears as the powder color and in soft section fills.
- Semantic states (success/info/warning) exist but the storefront rarely shows them — keep them muted and warm.

### Type
- A single **geometric sans** family carries the brand (display + body). Headlines are **heavy (700–800)**, frequently mixing **upright + true italic** within one headline for rhythm ("Synergia *dwóch składników aktywnych*"). Body is regular/medium.
- **Eyebrows / labels / CTAs:** uppercase with wide tracking (~0.16em). The wordmark uses very wide tracking (~0.22em).
- Substitute face here = **Montserrat** (see Caveats). Pair display 800 / body 400–500.

### Backgrounds & imagery
- **Full-bleed solid-color photography** is the signature: a white product floating on a saturated **red** (or **pink** for Fiberbiom) field, often with airborne golden powder and a white outlined badge ("Colostrum nr 1 w aptekach"). Warm, bright, high-key, slightly punchy saturation — **no grain, no duotone, never b&w**.
- Alternating page sections: **white** ↔ **warm off-white / cream**. Sub-brand sections may go full-color (red/pink).
- No gradients as a brand device (avoid purple/blue gradients entirely). Color is flat and bold.
- Lifestyle shots (a hand holding the box, experts) are bright and natural-light.

### Shape, radius, borders, cards
- **Pill CTAs** (`border-radius: 999px`) are the primary button shape.
- **Cards** are white with **soft, diffuse, warm shadows** and medium radius (~14–22px); borders are subtle hairlines (`#D8D3D0`) when used at all. No heavy outlines, no colored left-border accent cards.
- The **hexagon / elongated-rhombus** is the core geometric motif: it's the logo container, the frame around benefit icons, and the shape of badges. Reuse it for emphasis.

### Elevation & shadow system
- Three diffuse warm-neutral steps (`--ga-shadow-sm/md/lg`) plus a **red glow** (`--ga-shadow-red`) reserved for the primary lifted CTA. Shadows are soft and low-contrast — never hard or blue.

### Motion, hover & press
- Subtle and quick. **Hover:** buttons darken (red → `#DB2A36`), cards lift slightly (shadow sm→md) and/or image zooms gently (~1.03 scale). Links go red on hover.
- **Press:** slight darken + a small scale-down (~0.98). No bouncy/springy physics.
- Transitions ~150–250ms ease-out. Hero uses a simple slideshow (fade/slide) with play/pause. Avoid flashy or elastic animation.

### Transparency & blur
- Used lightly: sticky header is white (optionally translucent with a small backdrop blur on scroll); promo bar is a solid red strip. Badges over photography are flat white line-art with no blur. No glassmorphism as a theme.

### Layout rules
- Centered container ~1240px with 24px gutters. **Sticky top promo bar** (red, free-shipping message) + **sticky white header** (logo center/left, nav, search, account, wishlist, cart). **Slide-out cart drawer** from the right with a free-shipping progress bar. Footer is dense: brand blurb, link columns, payment + delivery glyphs, social, newsletter, legal.
- Generous vertical rhythm between sections (64–96px).

---

## 5. Iconography

- **Benefit / feature icons** are **thin single-weight red line-art** (≈2px stroke, no fill) drawn **inside the brand's elongated-hexagon frame** — e.g. SMAK (grapes + banana), NATURALNOŚĆ, FORMY PODANIA. These are bespoke PNGs shipped by the theme; the real files are copied into `assets/` (`icon-smak.png`, `icon-naturalnosc.png`, `icon-forma.png`). **Reuse these rather than redrawing.** When you need a *new* icon in this style, use a thin-stroke outline set (see below) at the same weight, colored `--ga-red`, optionally inside the hex frame.
- **Brand mark** is a geometric red rhombus enclosing an interlocking ribbon (a stylized G/S). Square variants in `assets/`.
- **UI / system icons** (search, account, heart/wishlist, cart, hamburger, chevrons, close) are standard light-stroke line icons. The live theme uses its own inline SVGs; for recreation use **Lucide** (`https://unpkg.com/lucide@latest`) — same ~2px rounded-stroke outline style — to match. Documented in the UI kit. *(Substitute — flagged.)*
- **Payment / delivery glyphs** are real brand SVGs copied into `assets/` (`pay-przelewy24.svg`, `pay-blik.svg`, `pay-pobranie.svg`, `ship-dhl.svg`, `ship-inpost.svg`). Visa/Mastercard marks weren't retrievable — link the official brand SVGs or use Lucide `credit-card` as a placeholder.
- **Emoji** are used as expressive punctuation in marketing copy only (😍 💪 ❤️) — never as UI icons.
- **Unicode chars:** ® is part of the wordmark; bullets/arrows kept minimal.

---

## Caveats & substitutions
1. **Font is a substitute.** The exact licensed brand webfont could not be extracted from the Shopify theme; **Montserrat** (self-hosted) is used as a close geometric match. If you have the real face (likely Gilroy / Mont / Sofia Pro or similar geometric grotesque), drop the woff2s into `fonts/` and update `fonts/fonts.css`.
2. **UI icon set is a substitute** (Lucide via CDN) chosen to match the theme's stroke style; the bespoke *benefit* icons are the real assets.
3. **Palette beyond red/pink is inferred** from photography and packaging (cream, gold, warm neutrals) rather than a published token list.
4. Visa/Mastercard payment SVGs returned 404 at their versioned URLs and are not included.
5. Everything is reconstructed from the **public storefront only** — no internal codebase/Figma was available.

---
name: genactiv-design
description: Use this skill to generate well-branded interfaces and assets for Genactiv (Polish colostrum & mare's-milk supplement brand — Colostrum, Fiberbiom, Zooggies, Dermo), either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and a storefront UI kit for prototyping.
user-invocable: true
---

Read the `README.md` file within this skill, and explore the other available files (`colors_and_type.css`, `fonts/`, `assets/`, `preview/`, `ui_kits/storefront/`).

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and create static HTML files for the user to view. If working on production code, you can copy assets and read the rules here to become an expert in designing with this brand.

Key starting points:
- **Tokens:** `colors_and_type.css` (brand red `#F5333F`, Fiberbiom pink `#F5669C`, warm neutrals, Montserrat type scale, pill radii, warm shadows).
- **Fonts:** `fonts/fonts.css` (self-hosted Montserrat — a *substitute*; swap if you have the real brand face).
- **Assets:** `assets/` (real logo, benefit icons, product photography, expert portraits, payment/delivery glyphs).
- **UI kit:** `ui_kits/storefront/` — modular React components recreating the Shopify storefront (header, hero, product cards, cart drawer, footer).
- **Voice:** Polish, warm second-person ("Twój plan na zdrowie"), uppercase CTAs, sparing emoji (😍💪❤️), science-backed claims. See README › Content fundamentals.

If the user invokes this skill without any other guidance, ask them what they want to build or design, ask some questions, and act as an expert designer who outputs HTML artifacts _or_ production code, depending on the need.

# Genactiv — Storefront UI Kit

A high-fidelity, interactive recreation of the **Genactiv Shopify storefront** (genactiv.pl), built as modular React (in-browser Babel) components on top of the design-system tokens (`../../colors_and_type.css`, `../../fonts/fonts.css`).

> These are **cosmetic recreations** for prototyping/mockups — not production commerce code. Visuals, copy and interaction patterns mirror the live site; the cart/checkout are faked client-side.

## Run it
Open `index.html`. No build step — React 18 + Babel standalone load from CDN, then each `.jsx` is loaded in order. Components publish themselves to `window` (Babel scripts don't share scope otherwise).

## What it demonstrates (click-through)
- **Add to cart** from any product card (card or "Do koszyka" button) → cart drawer slides in, badge increments, toast confirms.
- **Cart drawer**: quantity steppers, remove, live subtotal, and the brand's **free-shipping progress bar** ("Jeszcze X zł do darmowej dostawy" → "Gratulacje!").
- **Search overlay** (header search icon) with suggestion chips.
- **Mobile nav** drawer (hamburger < 980px).
- **Hero slideshow**: auto-rotating slides with dots + play/pause.
- **Newsletter** inline success state.

## Components (files)
| File | Exports | Notes |
|---|---|---|
| `icons.jsx` | `Icon` | Inline SVG set, Lucide geometry (UI-icon substitute — see DS README) |
| `ui.jsx` | `Button`, `Stars`, `CartProvider`/`useCart`, `PRODUCTS`, `zl` | Atoms + cart store + product data |
| `header.jsx` | `PromoBar`, `Header`, `SearchOverlay` | Sticky translucent header, promo strip |
| `hero.jsx` | `Hero` | Two-column color-field slideshow |
| `sections.jsx` | `Benefits`, `BrandStatement`, `ProductSection`/`ProductCard`, `SubBrands`, `Experts`, `Newsletter` | Page sections |
| `cart.jsx` | `CartDrawer`, `Toast` | Slide-in cart + free-ship bar + toast |
| `footer.jsx` | `Footer` | Dense footer w/ payment + delivery glyphs |
| `app.jsx` | mounts `<App/>` | Composition + `MobileNav` |

## Reuse
Pull any component into a new design by copying the relevant `.jsx` + `kit.css` rules and the token files. `Button` variants: `primary` / `pink` / `ghost` / `white` (+ `size="sm|lg"`). Wrap interactive trees in `<CartProvider>` if they use `useCart`.

## Known substitutions
- **Font:** Montserrat (close geometric match — real brand face not extracted).
- **UI icons:** Lucide geometry. Benefit icons + payment/delivery glyphs are the **real** assets.
- Visa/Mastercard payment marks weren't retrievable.

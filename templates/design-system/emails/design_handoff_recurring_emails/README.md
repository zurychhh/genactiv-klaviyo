# Handoff: Genactiv — Recurring Purchase Email (3 wersje) → Klaviyo

## Cel paczki
Ten pakiet pozwala **Claude Code (połączonemu z Klaviyo przez MCP)** zakodować 3 wersje
maila „recurring purchase" (przypomnienie o ponownym zakupie, gdy kończy się poprzednie
opakowanie) jako **gotowe, responsywne szablony Klaviyo** — zgodnie ze standardem kodowania
maili Genactiv opisanym w `KLAVIYO_CODING_STANDARD.md`.

> **WAŻNE — czym są pliki w `design_reference/`:** to **makiety projektowe w HTML**
> (div/flex, React+Babel na płótnie), pokazujące docelowy wygląd i treść. **NIE są to
> produkcyjne maile do skopiowania 1:1.** Zadaniem jest **odtworzyć te projekty jako
> tabelaryczne, inline'owane szablony e-mail w Klaviyo** wg reguł z
> `KLAVIYO_CODING_STANDARD.md`. Render w kliencie pocztowym (Outlook, Gmail, Apple Mail,
> Klaviyo preview) musi wyglądać jak makieta.

## Fidelity
**High-fidelity.** Kolory, typografia, odstępy, radiusy i treść są finalne. Odtwórz
piksel-w-piksel w granicach możliwości HTML e-mail (patrz ograniczenia w standardzie).

## Co trzeba zbudować (3 szablony / Universal Content blocks)
Każda wersja = osobny szablon w Klaviyo (lub blok Universal Content), 600 px szerokości.

| ID | Nazwa robocza | Kierunek | Główne CTA |
|----|---------------|----------|------------|
| **A** | `genactiv_recurring_reminder` | Przypomnienie, pilny, czerwony | „ZAMÓW PONOWNIE" |
| **B** | `genactiv_recurring_subscription` | Konwersja na subskrypcję, –15% | „WŁĄCZ CYKLICZNĄ DOSTAWĘ" |
| **C** | `genactiv_recurring_editorial` | Premium, minimalistyczny, kremowy | „UZUPEŁNIJ ZAPAS" |

Rekomendowany flow: trigger **Placed Order** → time delay (np. 25–30 dni) lub
**Klaviyo „Expected date of next order"** (predykcja). A/B/C jako warianty w teście flow.

---

## Wspólne zasady (dla wszystkich 3)
- **Szerokość:** 600 px (kontener), pełna responsywność do ~320 px.
- **Tło maila (poza kontenerem):** `#F4F1EE` (ciepła biel) — A i B; `#FBEFE2` (krem) dla C tła wewn.
- **Font:** Montserrat z `<link>` + fallback `Arial, Helvetica, sans-serif`. Nagłówki 700–800,
  body 400–500. (Klienty bez web-fontów → Arial; layout musi działać na fallbacku.)
- **Przyciski:** pill (`border-radius: 999px`), bulletproof VML dla Outlooka. Czerwony
  `#F5333F`, tekst biały, UPPERCASE, `letter-spacing` ~0.1em, padding ~16px 34px.
- **Stopka:** ciemna `#1C1B1B` (wariant A) lub jasna `#F4F1EE` (B, C) — patrz makiety.
  Zawiera logo, social, „Wypisz się", dane spółki. Link wypisu = `{% unsubscribe %}`.
- **Preheader:** ukryty tekst podglądu (patrz teksty niżej).
- **Merge tagi:** patrz sekcja „Dynamiczne dane" w każdym mailu + standard kodowania.

---

## EMAIL A — `genactiv_recurring_reminder`

**Cel:** przypomnieć, że zapas się kończy i skłonić do ponownego zamówienia tego samego produktu.

**Preheader:** `Twój zapas dobiega końca — uzupełnij i nie trać rytmu 💪`

**Struktura (góra → dół):**
1. **Header bar** — tło `#F5333F`, padding 22px 40px, wyśrodkowane białe logo (h=30px).
2. **Hero** (padding 36px 40px):
   - Eyebrow: `PORA UZUPEŁNIĆ ZAPAS` — 12px / 700 / `#F5333F` / tracking .16em / UPPERCASE.
   - H1: `Kończy się Twoje Colostrum?` — Montserrat 800, 34px, line-height 1.1, `#1C1B1B`;
     słowo „Colostrum?" **kursywą**.
   - Body 15px/1.6 `#5C5757`: personalizacja imieniem + info „minął ~miesiąc od ostatniego
     zamówienia". Pogrubienie: „Nie rób przerwy w odporności".
3. **Supply meter** — karta `#FBEFE2`, radius 14px, padding 16/18:
   - wiersz: „Twój szacowany zapas" (13/700 `#3D3A3A`) ↔ „~5 porcji" (13/800 `#F5333F`)
   - pasek: tor `#FFFFFF` h=9 radius 999, wypełnienie `#F5333F` szer. ~14%.
   - *Dynamiczne:* % i liczba porcji z właściwości profilu/eventu, jeśli dostępne; inaczej tekst stały.
4. **Karta produktu** — tło `#F4F1EE`, radius 18, flex (obraz 110×110 radius 14 + treść):
   nazwa (17/700), meta UPPERCASE 12 `#8B8585`, gwiazdki `#E9B872` + liczba opinii, cena 20/800.
   *Dynamiczne:* z ostatnio kupionego produktu (katalog/feed).
5. **CTA** — przycisk pełnej szer., czerwony pill: `ZAMÓW PONOWNIE →`. Link = deep link do
   koszyka z produktem / strony produktu.
6. **Free-shipping nudge** — karta `#FFE7E8` radius 14, ikona ciężarówki `#F5333F` + tekst
   „Dorzuć drugi produkt i masz **darmową dostawę** — od 99 zł."
7. **Benefity** — sekcja `#F4F1EE`, nagłówek wyśrodkowany 15/800; 3 ikony (SMAK,
   NATURALNOŚĆ, FORMY PODANIA), obraz ~74px + label 11/700.
8. **Stopka ciemna** `#1C1B1B`.

**Dynamiczne dane (Klaviyo):**
- `{{ first_name|default:'Cześć' }}` — imię w body.
- Produkt: z eventu „Placed Order" (ostatnia pozycja) lub katalogu — `{{ event.extra.line_items... }}` / blok produktu.
- Dni od zakupu / liczba porcji: właściwość profilu lub stały tekst fallback.

---

## EMAIL B — `genactiv_recurring_subscription`

**Cel:** zamienić jednorazowy zakup na cykliczną dostawę (subskrypcja –15%).

**Preheader:** `Nie rób przerwy w odporności — i oszczędzaj 15% z każdą dostawą`

**Struktura:**
1. **Header jasny** — wiersz: logo czerwone (h=28) ↔ tag pill `#FFE7E8`/`#F5333F`
   z ikoną „refresh": `DOSTAWA CO 30 DNI`. Dolna linia `#ECE8E5`.
2. **Hero:** eyebrow `TWÓJ ZAPAS SIĘ KOŃCZY`; H1 `Zadbaj o ciągłość. Zaoszczędź 15%.`
   („Zaoszczędź 15%." kursywą); body o regularności i braku zobowiązań.
3. **Porównanie 2 kart** (flex gap 14):
   - Lewa „JEDNORAZOWO": border `#D8D3D0`, radius 16, cena `79,00 zł` (800/26), podpis „jedno opakowanie".
   - Prawa „Z SUBSKRYPCJĄ": tło `#F5333F`, biały tekst, shadow czerwony; badge `–15%` (tło `#1C1B1B`),
     cena `67,15 zł`, podpis „co 30 dni + darmowa dostawa".
   *Dynamiczne:* ceny z katalogu; rabat z konfiguracji subskrypcji.
4. **CTA:** pełnej szer. `WŁĄCZ CYKLICZNĄ DOSTAWĘ →` + link tekstowy „Wolę zamówić jednorazowo".
5. **Cytat eksperta:** karta `#FBEFE2` radius 18 — portret okrągły 64px (Monika) + cytat kursywą
   + podpis 12/700 `#F5333F` „Monika Stromkie-Złomaniec · Dietetyk".
6. **Stopka jasna** `#F4F1EE`.

**Uwaga subskrypcja:** jeśli Genactiv używa appki subskrypcyjnej (np. Recharge/Loop/Shopify
Subscriptions), CTA powinno linkować do flow włączenia subskrypcji dla danego produktu.

---

## EMAIL C — `genactiv_recurring_editorial`

**Cel:** spokojny, premium przekaz dla lojalnych klientów; jeden mocny CTA.

**Preheader:** `Twój plan na zdrowie nie lubi przerw — uzupełnij zapas`

**Struktura (wyśrodkowana, tło wewn. `#FBEFE2`):**
1. Logo czerwone wyśrodkowane (h=26), padding góra 30.
2. **Hero produktu:** karta radius 24, tło `#F5333F`, zdjęcie produktu kwadratowe (1:1),
   shadow miękki. Padding boczny 56px.
3. **Komunikat (center):** eyebrow `CZAS NA UZUPEŁNIENIE` 12/700 tracking .18em; H1 800/32
   `Twój plan na zdrowie nie lubi przerw.` („nie lubi przerw." kursywą); body 15/1.65 max-szer 360px.
4. **CTA:** czerwony pill `UZUPEŁNIJ ZAPAS` (auto-szer., wyśrodkowany).
5. **Linia zaufania:** górna kreska `#D8D3D0`; gwiazdki 16px; `COLOSTRUM NR 1 W APTEKACH W
   POLSCE` 13/700; podpis 11 `#8B8585` „na odporność* · zaufały nam tysiące rodzin".
6. **Stopka jasna** `#F4F1EE`.

---

## Design tokens (pełne wartości)
Patrz `design_reference/colors_and_type.css`. Najważniejsze:

| Token | Hex / wartość |
|---|---|
| Brand red | `#F5333F` (hover/pressed `#DB2A36`) |
| Red soft (tła/nudge) | `#FFE7E8` |
| Fiberbiom pink | `#F5669C` |
| Cream | `#FBEFE2` · ciepła biel sekcji `#F4F1EE` |
| Colostrum gold (gwiazdki) | `#E9B872` |
| Ink (tekst/stopka) | `#1C1B1B` · body `#5C5757` · muted `#8B8585` |
| Border | `#D8D3D0` · hairline `#ECE8E5` |
| Radius | przyciski 999px · karty 14–24px |
| Font | Montserrat (display 800 / body 400–500); fallback Arial, Helvetica |
| Tracking | eyebrow .16em · CTA .1em · wordmark .22em |

## Assets
Wszystkie w `design_reference/assets/` (prawdziwe pliki marki z CDN genactiv.pl):
- `logo-primary.png` (czerwone, na jasne tła), `logo-white.png` (białe, na czerwone/ciemne)
- `photo-colostrum-nr1.png` (hero produktu)
- `icon-smak.png`, `icon-naturalnosc.png`, `icon-forma.png` (benefity, line-art w heksagonie)
- `expert-monika.png` (portret do cytatu w mailu B)

> **Hosting obrazów:** Klaviyo wymaga **absolutnych URLi**. Wgraj assety do Klaviyo Image
> Library (lub firmowego CDN) i podmień `src` w szablonach. Każdy `<img>` musi mieć `alt`,
> jawne `width`, oraz `display:block`. Logo i ikony zapewnić w 2× dla retina.

## Pliki w paczce
- `KLAVIYO_CODING_STANDARD.md` — **standard kodowania maili Genactiv w Klaviyo (czytaj najpierw).**
- `design_reference/Recurring Purchase Emails.html` — płótno z 3 makietami (otwórz w przeglądarce).
- `design_reference/EmailA.jsx` / `EmailB.jsx` / `EmailC.jsx` — źródło layoutu (treść, struktura, style inline).
- `design_reference/parts.jsx` — wspólne (ikony, preheader, stopka).
- `design_reference/email.css` — klasy/wartości stylów (mapowanie na inline w mailu).
- `design_reference/colors_and_type.css` — tokeny marki.
- `design_reference/assets/` — obrazy.
- `design_reference/fonts/` — pliki Montserrat (referencja; w mailu użyj `<link>` web-font + fallback).

## Definition of Done
- 3 szablony Klaviyo, każdy renderuje się poprawnie w: Apple Mail, Gmail (web+app), Outlook
  (desktop/VML), Klaviyo preview, dark mode.
- Tabelaryczny HTML, inline CSS, bulletproof buttony, `{% unsubscribe %}`, preheader, alt-texty.
- Merge tagi z fallbackami (brak „Witaj ,"). Test renderu z pustymi i wypełnionymi danymi.
- Zgodność z `KLAVIYO_CODING_STANDARD.md`.

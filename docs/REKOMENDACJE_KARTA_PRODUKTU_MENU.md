# Rekomendacje: Karta produktu + Menu mobile — NOTOAGENCY

> **Data:** 2026-07-02 | **Kontekst:** Test A/B GEN-6 vs NOTOAGENCY (08-30.06.2026)
> **Cel:** Przebudowa karty produktu w nowym motywie NOTO, aby wyeliminowac spadek konwersji i wdrozyc caly motyw po re-tescie
> **Zrodla danych:** Intelligems API (28,195 visitors), GA4, Microsoft Clarity (czerwiec 2026), web research best practices

---

## PODSUMOWANIE SYTUACJI

Nowy motyw NOTOAGENCY wygrywa lub remisuje wszedzie **poza karta produktu**:
- Strona glowna: **+15%** konwersja
- Meta Ads (glowny budzet): **remis / +5%**
- Proszek (bez wyboru wariantu): **+9%**

Ale karta produktu z wyborem opakowania zabija konwersje:

| Problem | Spadek | Komentarz |
|---------|--------|-----------|
| **Kapsulki 60 szt. mobile** | **-63%** | Wybor opakowania przeladowuje strone |
| **Kapsulki 120 szt. mobile** | **-47%** | j.w. |
| **Add-to-cart ogolnie** | **-14%** | 5,45% -> 4,86% |
| **Mobile add-to-cart** | **-16%** | ~62% calego ruchu |
| **Abandoned checkout** | **+21%** | 32,2% -> 38,9% |
| **Szacowana strata** | **-55 000 PLN/mies.** | Przy pelnym wdrozeniu bez naprawy |

**Wniosek z prezentacji:** Motyw wdraza sie w calosci (nie da sie mieszac). Naprawiamy karte produktu w nowym motywie, re-test, wdrozenie calego motywu naraz.

### Dane Clarity potwierdzajace problemy (czerwiec 2026):

| Metryka Clarity | Wartosc | Problem |
|-----------------|---------|---------|
| Dead clicks "Dodaj do koszyka" | **553** | CTA nie reaguje — JS error |
| Dead clicks na nazwy produktow | **4,944** | Nazwy nie sa klikalne na listingach |
| Quick back homepage | **16%** | Co 6. sesja — natychmiast cofaja |
| Scroll depth homepage mobile | **27,6%** | Widza 1/4 strony |
| Srednia stron/sesje mobile | **1,65** | Bardzo niska eksploracja |
| Hamburger menu uzycie | **619 klik / ~40k sesji = 1,5%** | Menu jest niewidoczne |
| Rage clicks /products/colostrum-120 | **34** | Frustracja na karcie kapsulki |
| Script errors mobile | **6,7% sesji** | JS blokuje interakcje |

---

## STRUKTURA REKOMENDACJI

Kazda zmiana ma przypisanego wlasciciela:
- **GRAFIK** = projektant UI/UX (Figma/mockupy)
- **DEV** = developer Shopify (Liquid + JS + CSS)
- **GRAFIK + DEV** = wspolna praca

Priorytet: od najwyzszego wplywu na konwersje.

---

## PRIORYTET 1: WYELIMINOWAC PRZELADOWANIE STRONY PRZY ZMIANIE WARIANTU

> **Wlasciciel: DEV** | **Oczekiwany efekt: +25-40% add-to-cart** | **To jest JEDYNA przyczyna -47/-63% spadku**

### Problem
Na obecnej karcie NOTO, klikniecie wariantu (60 kaps. / 120 kaps. / dwupak) powoduje **pelne przeladowanie strony** (full page navigation). Na mobile przy srednim LTE to 2-4 sekundy bialego ekranu. Uzytkownik traci kontekst, scroll position, i czesto odpada.

Na starej karcie GEN-6 zmiana wariantu dziala **bez przeladowania** — dowod: proszek (1 wariant, bez wyboru) ma +9% na NOTO, a kapsulki z wyborem -47/-63%.

### Rozwiazanie techniczne: Shopify Section Rendering API

```
Uzytkownik klika wariant
    -> JavaScript przechwytuje event (preventDefault)
    -> fetch(`/products/${handle}?variant=${variantId}&sections=${sectionId}`)
    -> API zwraca JSON z renderowanym HTML sekcji
    -> JS podmienia elementy DOM: cena, zdjecia, dostepnosc, stan ATC
    -> history.pushState() aktualizuje URL bez nawigacji
```

**Wzorcowa implementacja:** Shopify Dawn theme
- `snippets/product-variant-picker.liquid` — web components `<variant-radios>`, `<variant-selects>`
- Custom element nasluchuje `change` event i wywoluje Section Rendering API
- Podmienia: cene, galerie, dostepnosc, stan przycisku ATC
- Transfer danych: ~2-5 KB vs ~200-500 KB przy pelnym reload

### Wymagania dla DEV:

| Wymaganie | Szczegol |
|-----------|----------|
| Zero page reload | Section Rendering API + `fetch()` + DOM swap |
| URL update | `history.pushState()` z parametrem `?variant=ID` |
| Aktualizacja ceny | Podmiana `innerHTML` elementu ceny z odpowiedzi sekcji |
| Aktualizacja galerii | Zdjecia tagowane do wariantow w Shopify admin; swap z odpowiedzi |
| Dostepnosc | Update tekstu "Dostepny" / "Brak" z odpowiedzi |
| Stan przycisku ATC | Enable/disable na podstawie dostepnosci wariantu |
| Fetch URL | Uzyc `/products/{handle}` (nie `/product/`), parametr `variant` (nie `variant_id`) |
| Czas reakcji | < 300ms od klikniecia do renderowania nowego stanu |

### Test akceptacyjny:
1. Otworz karte kapsulki 120 szt. na mobile (Chrome DevTools throttle: Fast 3G)
2. Kliknij "60 kapsulki" — strona **nie moze sie przeladowac**
3. Cena, zdjecie, URL musza sie zmienic w < 500ms
4. Scroll position musi pozostac bez zmian
5. Przycisk "Dodaj do koszyka" musi byc aktywny i klikalny

---

## PRIORYTET 2: NOWY DESIGN SELEKTORA WARIANTOW

> **Wlasciciel: GRAFIK** | **Oczekiwany efekt: +15-20% add-to-cart**

### Problem
Obecne dropdowny wymagaja **2 akcji** (tap aby otworzyc, tap aby wybrac). 28% sklepow e-commerce wciaz uzywa dropdownow mimo danych przeciwko nim (Baymard Institute).

### Wytyczne dla grafika — jak zaprojektowac selektor wariantow:

#### A) Przyciski-pastylki (pill buttons) zamiast dropdown

```
+--------------------------------------------------+
|  Wybierz opakowanie:                              |
|                                                    |
|  +------------------+  +-------------------+       |
|  |  60 kapsulek     |  | ★ 120 kapsulek   |       |
|  |  149 zl          |  |   249 zl          |       |
|  |  2,48 zl/kaps.   |  |   2,08 zl/kaps.   |       |
|  +------------------+  +-------------------+       |
|                         Najczesciej wybierane       |
+--------------------------------------------------+
```

#### B) Specyfikacja przyciskow-pastylek:

| Parametr | Wartosc |
|----------|---------|
| Minimalna wielkosc tap target | **48 x 48 px** (Google Material Design) |
| Odstep miedzy przyciskami | 8-12 px |
| Stan wybrany | Gruby border 2-3px + wypelnienie kolorem + opcjonalny checkmark |
| Stan niewybrany | Cienki border 1px, brak wypelnienia |
| Stan niedostepny (OOS) | Szary + przekreslenie ukosnna linia + "Powiadom" |
| Font etykiety | 14-16px minimum |
| Font ceny pod etykieta | 12-14px, kolor muted |
| Animacja zmiany | 150-200ms transition |
| Uklad | Poziomy wiersz; gdy > 4 opcje — scrollowalny poziomo |

#### C) Elementy obowiazkowe na kazdym przycisku wariantu:

1. **Nazwa wariantu** — "60 kapsulek" / "120 kapsulek" / "Dwupak"
2. **Cena** — bezposrednio pod nazwa, bez koniecznosci szukania
3. **Cena za jednostke** — "2,08 zl/kaps." — uzasadnia wieksza paczke
4. **Badge "Najczesciej wybierane"** na najpopularniejszym wariancie (120 kaps.)
5. **Pre-selekcja** — domyslnie wybrany najpopularniejszy wariant

#### D) Czego NIE robic:

- NIE uzywac dropdown / select
- NIE chowac ceny — cena musi byc widoczna BEZ klikania
- NIE wymagac scrollowania do ceny po wybraniu wariantu
- NIE pokazywac wariantow jako tekst bez wizualnego rozroznienia
- NIE zmieniac kolejnosci wariantow miedzy produktami

### Benchmark — jak robi to stara karta GEN-6 (baseline):
Na GEN-6 selektor wariantow to prosty, widoczny element z natychmiastowa reakcja. Nowa karta musi byc **co najmniej tak dobra**, plus dodac cene-za-jednostke i badge.

---

## PRIORYTET 3: STICKY "DODAJ DO KOSZYKA" NA MOBILE

> **Wlasciciel: GRAFIK (design) + DEV (implementacja)** | **Oczekiwany efekt: +8-15% add-to-cart**

### Problem
Przy scroll depth 41,5% na mobile, przycisk ATC jest poza viewport przez wiekszosc sesji.

### Wytyczne dla grafika:

```
+--------------------------------------------------+
|  Colostrum 120 kaps.   249 zl  [ DODAJ DO KOSZYKA ] |
+--------------------------------------------------+
^                                                    ^
|-- wysokosc: 56px min --|-- przycisk: 48px high --|
```

#### Specyfikacja sticky ATC bar:

| Parametr | Wartosc |
|----------|---------|
| Pozycja | Fixed bottom viewport |
| Wysokosc | **56px minimum** |
| Padding dolny (iOS safe area) | +34px na iPhone z home indicator |
| Tlo | Biale z cienkim cieniem gornym lub border-top 1px |
| Przycisk ATC | GenActiv Red `#F5333F`, tekst bialy, min 48px wysokosc |
| Kontrast | Min 4.5:1 przycisk vs tlo |
| Z-index | Nad calym contentem, pod modalami/drawerami |

#### Zawartosc sticky bar:

| Element | Widocznosc |
|---------|-----------|
| Przycisk "Dodaj do koszyka" | **ZAWSZE** — najwazniejszy element |
| Cena | **ZAWSZE** |
| Nazwa produktu (skrocona) | Opcjonalnie, jesli sie miesci |
| Wybrany wariant | Opcjonalnie ("120 kaps.") |

#### Zachowanie:

| Wydarzenie | Reakcja |
|------------|---------|
| Page load | **NIE wyswietlaj** (unikac duplikatu CTA) |
| Oryginalny ATC scrolluje poza viewport | Slide-up 250ms ease-out |
| Uzytkownik wraca na gore | Slide-down i schowaj |
| Zmiana wariantu powyzej | Sticky bar aktualizuje cene i etykiete |
| Klikniecie ATC w sticky | Dodaj do koszyka + animacja potwierdzenia (checkmark) |

### Wymagania dla DEV:

```javascript
// Intersection Observer na oryginalnym ATC
const atcButton = document.querySelector('.product-form__submit');
const stickyBar = document.querySelector('.sticky-atc-bar');

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    stickyBar.classList.toggle('visible', !entry.isIntersecting);
  });
}, { threshold: 0 });

observer.observe(atcButton);
```

---

## PRIORYTET 4: LAYOUT KARTY PRODUKTU MOBILE — ABOVE THE FOLD

> **Wlasciciel: GRAFIK** | **Oczekiwany efekt: +14-19% add-to-cart**

### Zasada 550 px
Na wspolczesnych smartfonach (iPhone 14/15, Samsung Galaxy S) uzyteczna przestrzen above-the-fold to ok. **390 x 550-600 px** (po odjeciu browser chrome).

### Blueprint — co MUSI byc widoczne bez scrollowania:

```
+------------------------------------------+
|                                          |  0-300px
|        [ZDJECIE PRODUKTU]                |
|        karuzela swipe, proporcje 4:3     |
|        kropki wskaznikowe pod spodem     |
|                                          |
+------------------------------------------+
|  Colostrum Bovinum GenActiv              |  300-330px
|  ★★★★★ (4.8) · 247 opinii              |
+------------------------------------------+
|  249 zl   ~~299 zl~~                     |  330-360px
+------------------------------------------+
|  [  60 kaps.  ]  [★ 120 kaps. ]         |  360-440px
|    149 zl          249 zl                |
|    2,48 zl/kaps.   2,08 zl/kaps.         |
+------------------------------------------+
|  [      DODAJ DO KOSZYKA      ]          |  440-490px
+------------------------------------------+
|  ✓ Darmowa dostawa od 300 zl             |  490-530px
|  ✓ Nr 1 w polskich aptekach              |
+------------------------------------------+
```

### Wytyczne dla grafika — hierarchia above-the-fold:

| Priorytet | Element | Specyfikacja |
|-----------|---------|-------------|
| 1 | Karuzela zdjec | Swipe, proporcje ~4:3, kropki-wskazniki. Pokazac skrawek nastepnego zdjecia po prawej. **BEZ auto-play.** |
| 2 | Tytul produktu | Duza, czytelna czcionka. Bez SKU, bez smieci. Max 2 linie. |
| 3 | Oceny + liczba opinii | Gwiazdki + "247 opinii" — klikalny link do sekcji opinii. |
| 4 | Cena | Wyraznie, duzy font. PLN bez miejsc dziesietnych. Jesli promocja: przekreslona stara cena. |
| 5 | Selektor wariantu | Pill buttons z cena (patrz Priorytet 2). |
| 6 | Przycisk ATC | Pelna szerokosc, min 48px wysokosc, GenActiv Red `#F5333F`. |
| 7 | Linia zaufania | 1-2 linie: darmowa dostawa, nr 1 w aptekach. |

### Czego NIE umieszczac above the fold:

- Dlugich opisow produktu (schowac w akordeon ponizej)
- Paskow informacyjnych / bannerow promocyjnych
- Wielu CTA (jeden przycisk ATC, nic wiecej)
- Ikon social share
- Breadcrumbsow (male, 1 linia max, albo w ogole nie)

### Below the fold (po scrollu):

| Sekcja | Format |
|--------|--------|
| 3 kluczowe korzysci | Ikona + krotki tekst (odpornosc, colostrum, jakosc apteczna) |
| Opis produktu | Akordeon "Czytaj wiecej" — poczatkowo 3-4 linie |
| Sklad / tabela odzywcza | Akordeon |
| Trust badges | Rzad ikon (apteka, badania kliniczne, polski produkt) |
| Opinie klientow | Pelna sekcja z filtrami |
| Powiazane produkty | Cross-sell (Fiberbiom, inne SKU GenActiv) |

---

## PRIORYTET 5: NAPRAWIC DEAD CLICKS NA "DODAJ DO KOSZYKA"

> **Wlasciciel: DEV** | **Oczekiwany efekt: eliminacja 553 straconych konwersji/miesiac**

### Problem
Clarity zarejestrował **553 dead clicks** na elemencie "Dodaj do koszyka" w czerwcu. To oznacza, ze przycisk nie reaguje na klikniecie — prawdopodobnie JS error blokuje event handler.

### Diagnoza dla DEV:

1. **Sprawdzic bledy JS w konsoli** na karcie produktu NOTO (mobile Chrome):
   - Clarity pokazuje 6,7% sesji mobile z script errors
   - 34 rage clicks na `/products/colostrum-genactiv-120-kapsulek` — ta strona

2. **Typowe przyczyny:**
   - Event listener nie jest podpiety (JS nie zaladowal sie w calosci)
   - Pandectes consent manager blokuje skrypt przed zaladowaniem
   - Konflikt miedzy Intelligems A/B a theme JS
   - Race condition: przycisk renderowany przed podpieciem handlera

3. **Fix:**
   - Upewnic sie, ze `product-form.js` laduje sie po DOM ready
   - Dodac fallback: jesli JS nie zaladowal w 3s, podpiac prosty handler
   - Przetestowac z wylaczonym Pandectes i wylaczonym Intelligems osobno

### Test akceptacyjny:
- 100 klikniec w "Dodaj do koszyka" na mobile (rozne produkty) = 0 dead clicks
- Sprawdzic na: Chrome Android, Safari iOS, Samsung Internet

---

## PRIORYTET 6: KLIKALNOSC NAZW PRODUKTOW NA LISTINGACH

> **Wlasciciel: DEV** | **Oczekiwany efekt: eliminacja 4,944 dead clicks/miesiac**

### Problem
Clarity: 3,526 dead clicks na "COLOSTRUM GENACTIV" + 1,418 na "COLOSTRUM Z MALINA" na listingach kolekcji. Uzytkownicy klikaja w nazwe produktu, ale linkiem jest tylko obrazek.

### Fix:
Opakowac nazwe produktu w `<a>` tag z `href` do karty produktu:

```liquid
<!-- BYLO: -->
<span class="product-card__title">{{ product.title }}</span>

<!-- MA BYC: -->
<a href="{{ product.url }}" class="product-card__title-link">
  {{ product.title }}
</a>
```

---

## PRIORYTET 7: NAWIGACJA MOBILE — BOTTOM NAV BAR

> **Wlasciciel: GRAFIK (design) + DEV (implementacja)** | **Oczekiwany efekt: +15-20% nawigacji**

### Problem
Hamburger menu: **619 klikniec / ~40,000 sesji = 1,5% uzycia**. Uzytkownicy go nie widza lub nie rozpoznaja. Jednoczesnie srednia stron/sesje to 1,65 — nawigacja nie zacheca do eksploracji.

### Rozwiazanie: Hybrydowy model (bottom nav + hamburger)

#### Sticky bottom tab bar (GRAFIK):

```
+--------+--------+--------+--------+--------+
|  Sklep |Produkty| Szukaj | Koszyk | Konto  |
|  [dom] | [grid] | [lupa] |[torba] |[osoba] |
+--------+--------+--------+--------+--------+
```

| Parametr | Wartosc |
|----------|---------|
| Wysokosc | 56-60px (rowna system nav bars) |
| Ikona | 24x24px |
| Font etykiety | 10-12px |
| Tap target per item | Min 48x48px |
| Tlo | Biale z subtelnym cieniem gornym |
| Stan aktywny | Kolorowa ikona + etykieta (Brand Blue `#0066CC`) |
| Stan nieaktywny | Szara ikona + etykieta |
| Padding dolny (iOS safe area) | +34px |
| Badge koszyka | Czerwona kropka z liczba produktow |

#### Zachowanie na karcie produktu:

| Scrollowanie | Widoczny element |
|-------------|-----------------|
| ATC widoczny na ekranie | Bottom navigation bar |
| ATC poza viewport | **Sticky ATC bar** (zamienia bottom nav) |
| Powrot na gore | Bottom navigation bar |

Transition: 250ms smooth animation.

#### Hamburger menu — role drugorzedna:

Hamburger zostaje, ale sluzy do:
- Pelnego drzewa kategorii
- Blog / edukacja
- O nas / kontakt
- FAQ
- Gdzie kupic (apteki)

### Wymagania dla DEV:

- Bottom nav: fixed bottom, z-index pod modalami
- Na PDP: Intersection Observer przelacza miedzy bottom nav a sticky ATC
- Badge koszyka: aktualizowany AJAX-em po dodaniu produktu
- Deep link: "Produkty" otwiera drawer/sheet z kategoriami (nie pelna nawigacje)

---

## PRIORYTET 8: HOMEPAGE ABOVE-THE-FOLD

> **Wlasciciel: GRAFIK** | **Oczekiwany efekt: redukcja 16% quick back rate**

### Problem
Scroll depth homepage mobile: **27,6%** — uzytkownicy widza 1/4 strony. Quick back: **16%** (co 6. sesja). Slideshow pochlanial ekran i nie komunikowal oferty.

### Wytyczne:
Homepage nowego motywu (ktory ma +15% konwersje vs GEN-6) jest juz dobra. Ale aby zredukowac quick back:

1. **Pierwszych 400px** musi odpowiedziec na: "Co tu kupie? Dlaczego tu?"
2. Zamiast duzego slideshow — kompaktowa sekcja hero (max 250px) z CTA
3. Pod hero: **3-4 kafelki top kategorii** (Colostrum, Fiberbiom, Dla dzieci, Dermokosmetyki) z ikonami
4. Kazdy kafelek to link do kolekcji — daje uzytkownikowi sciezke dalej

---

## PODSUMOWANIE DLA GRAFIKA — CHECKLIST MOCKUPOW

Grafik powinien przygotowac mockupy Figma dla:

### Mockup 1: Karta produktu mobile (PDP) — PRIORYTET GLOWNY

- [ ] Layout above-the-fold wg blueprintu z Priorytetu 4
- [ ] Selektor wariantow pill buttons wg specyfikacji z Priorytetu 2
- [ ] Wariant z 2 opcjami (60/120 kaps.) — wersja podstawowa
- [ ] Wariant z 3 opcjami (60/120/dwupak) — wersja rozszerzona
- [ ] Stan wybrany vs niewybrany vs niedostepny
- [ ] Badge "Najczesciej wybierane" na 120 kaps.
- [ ] Cena za kapsluke pod kazdy pill button
- [ ] Przycisk ATC pelna szerokosc, GenActiv Red
- [ ] Linia zaufania pod ATC

### Mockup 2: Sticky ATC bar

- [ ] Wersja z cena + ATC (minimum)
- [ ] Wersja z nazwa produktu + wariant + cena + ATC
- [ ] Animacja wejscia (slide-up)
- [ ] Stan po dodaniu do koszyka (checkmark + "Dodano!")

### Mockup 3: Bottom navigation bar

- [ ] 5 pozycji: Sklep, Produkty, Szukaj, Koszyk, Konto
- [ ] Stan aktywny vs nieaktywny
- [ ] Badge koszyka z liczba
- [ ] Transition: bottom nav -> sticky ATC (na PDP)

### Mockup 4: Listing kolekcji — karta produktu w siatce

- [ ] Nazwa produktu jako klikalny link (nie tylko obrazek)
- [ ] Cena widoczna na karcie
- [ ] Quick ATC button na karcie (opcjonalnie)

### Mockup 5: Homepage mobile above-the-fold

- [ ] Kompaktowy hero (max 250px) z CTA
- [ ] 3-4 kafelki kategorii pod hero
- [ ] Widoczna sciezka dalej w pierwszych 400px

---

## PODSUMOWANIE DLA DEVELOPERA — CHECKLIST IMPLEMENTACJI

### Etap 1 — Krytyczny (przed re-testem):

- [ ] **Section Rendering API** — zero reload na zmianie wariantu (Priorytet 1)
- [ ] **Fix dead clicks ATC** — debug JS errors, naprawa event handlera (Priorytet 5)
- [ ] **Pill buttons** — implementacja nowego selektora wariantow wg mockupu grafika (Priorytet 2)
- [ ] **Sticky ATC bar** — Intersection Observer + fixed bottom (Priorytet 3)

### Etap 2 — Wazny (przed re-testem):

- [ ] **Klikalnosc nazw produktow** na listingach (Priorytet 6)
- [ ] **Bottom navigation bar** — implementacja wg mockupu (Priorytet 7)

### Etap 3 — Po re-tescie, przy wdrozeniu:

- [ ] Homepage above-the-fold poprawki (Priorytet 8)
- [ ] Optymalizacja slabszych kolekcji (Colostrum -30%, Maseczki -31%)

---

## OCZEKIWANE EFEKTY PO WDROZENIU

| Zmiana | Oczekiwany lift | Zrodlo |
|--------|----------------|--------|
| Eliminacja reload na wariancie | **+25-40% add-to-cart** | Shopify Dev, Baymard |
| Pill buttons zamiast dropdown | **+15-20% add-to-cart** | EasyApps, Baymard Institute |
| Sticky ATC bar mobile | **+8-15% add-to-cart** | CartyLabs, GrowthRock, Traction MKT |
| Restructure above-the-fold | **+14-19% add-to-cart** | Sacha Goureau (1M sesji) |
| Bottom navigation bar | **+15-20% nawigacji** | AppMySite, UXPin |
| Per-capsule pricing | **+5-10% wieksze opakowanie** | Huel, Ritual pattern |
| Badge "Najczesciej wybierane" | **+3-5% wieksze opakowanie** | PagePilot case study |

**Scenariusz konserwatywny:** Jesli naprawimy tylko reload (Priorytet 1) + sticky ATC (Priorytet 3), spodziewamy sie **wyzerowania straty -20,9%** i przywrocenia konwersji NOTO do poziomu GEN-6.

**Scenariusz optymistyczny:** Pelen zestaw zmian (Priorytet 1-7) moze dac NOTO **przewage +10-15%** nad GEN-6, co w polaczeniu z +15% homepage oznacza **pelne wdrozenie nowego motywu z zyskiem**.

---

## BENCHMARKI — NAJLEPSZE SKLEPY SUPLEMENTOW NA SHOPIFY

| Marka | Co robia dobrze | Zastosowanie dla GenActiv |
|-------|-----------------|--------------------------|
| **Ritual** (ritual.com) | Minimalistyczny PDP, transparentnosc skladnikow, subskrypcja domyslna | Transparentnosc zrodla colostrum |
| **AG1** (drinkag1.com) | Silna hierarchia above-fold, benefit-led copy | Korzysci (odpornosc) przed cechami |
| **Vital Proteins** (vitalproteins.com) | Czyste selektory wariantow proszku, lifestyle imagery | Bezposredni wzorzec dla rozmiaru proszku |
| **Huel** (huel.com) | Per-serving pricing, multi-pack options | Cena za kapsluke, dwupaki |
| **Absolute Collagen** (absolutecollagen.com) | Dawkowanie w naglowku, timeline rezultatow | Dane kliniczne o colostrum |

### Kluczowe wzorce z top marek:

1. **Benefit-first headlines** — "Wzmocnij odpornosc" zamiast "Colostrum Bovinum 120 kaps."
2. **Per-unit pricing** — "2,08 zl/kaps." uzasadnia wieksza paczke
3. **Social proof above fold** — gwiazdki + liczba opinii w pierwszych 350px
4. **1 akcja = 1 klik** — selektor wariantow nigdy nie wymaga 2 interakcji
5. **Subskrypcja jako domyslna** — pre-selekcja "Kup co miesiac -15%"

---

## ZRODLA

- [Shopify Dev — Section Rendering API](https://shopify.dev/docs/api/ajax/section-rendering)
- [Baymard Institute — Use Buttons for Size Selection](https://baymard.com/blog/use-buttons-for-size-selection)
- [Sacha Goureau — Mobile Above-the-Fold (1M sesji)](https://www.sachagoureau.com/post/mobile-ecommerce-optimization-above-the-fold-how-layout-drives-add-to-cart)
- [CartyLabs — Shopify Mobile Conversion](https://cartylabs.com/blog/shopify-mobile-conversion-optimization/)
- [EasyApps — Variant Selector Guide](https://easyappsecom.com/guides/shopify-variant-selector-guide)
- [EasyApps — Sticky ATC Best Practices](https://easyappsecom.com/guides/sticky-add-to-cart-best-practices)
- [GrowthRock — Sticky ATC A/B Test](https://growthrock.co/sticky-add-to-cart-button-example/)
- [Traction MKT NZ — Sticky ATC +7.9%](https://tractionmarketing.nz/insights/unlocking-small-wins-that-scale-what-we-learned-from-testing-a-sticky-add-to-cart-button-on-mobile/)
- [ConvertCart — Above the Fold](https://www.convertcart.com/blog/above-the-fold-content)
- [AppMySite — Bottom Nav vs Hamburger](https://blog.appmysite.com/rethinking-hamburgers-for-ecommerce-know-why-bottom-navigation-bar-is-the-new-trend/)
- [Nielsen Norman Group — Products with Multiple Variants](https://www.nngroup.com/articles/products-with-multiple-variants/)
- [Nielsen Norman Group — Input Steppers](https://www.nngroup.com/articles/input-steppers/)
- [PagePilot — Shopify Variants vs Options](https://pagepilot.ai/blog/shopify-variants-vs-options)
- [Ilana Davis — Buttons as Better Shopping](https://www.ilanadavis.com/blogs/articles/buttons-prove-to-be-a-better-shopping-experience)
- [GitHub — Shopify/Dawn variant picker](https://github.com/Shopify/dawn/blob/main/snippets/product-variant-picker.liquid)
- Dane wlasne: Intelligems API (28,195 visitors), GA4, Clarity (projekt 3354986136401458)
- Prezentacja: "GenActiv - Test AB (standalone).html" — wnioski i decyzja, czerwiec 2026

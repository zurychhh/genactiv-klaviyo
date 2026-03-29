# 🎄 Szablon Świąteczny z 5 Produktami - Dokumentacja

## 📧 Informacje Podstawowe

**Nazwa szablonu:** `Swieta_2025_Pakiety_5produktow`
**Template ID:** `Y4cwDB`
**Typ:** Produktowy (e-commerce) - multi-product grid
**Kategoria:** Kampania świąteczna/promocyjna
**URL w Klaviyo:** https://www.klaviyo.com/email-editor/Y4cwDB/edit

---

## 🎨 Design System - Bazuje na Rzeczywistym Szablonie GenActiv

### Kolory (z prawdziwego szablonu):

| Element | Hex Code | Użycie w Szablonie |
|---------|----------|-------------------|
| **Primary Red** | `#EF3340` | Header background, footer background |
| **CTA Red** | `#f5333f` | Przyciski "KUP TERAZ" |
| **Gold Accent** | `#F8A230` | Badge "BESTSELLER", urgency banner |
| **Dark Text** | `#1a1818` / `#1a1a1a` | Nazwy produktów, teksty |
| **Gray Border** | `#e8e8e8` | Obramowania kafli produktowych |
| **Green Savings** | `#27ae60` | Tekst "Oszczędzasz X zł" |
| **Light Gray** | `#999` | Ceny przed rabatem (przekreślone) |
| **White** | `#FFFFFF` | Tło główne, tło kafli |

### Typografia (rzeczywista z GenActiv):

```css
Fonty: 'Branding', 'Branding-medium', Helvetica, Arial, sans-serif

H1 (Hero świąteczny):
- Font: Branding, Helvetica, Arial
- Size: 32px
- Weight: 700 (bold)
- Align: center
- Line-height: 1.2

Nazwy produktów (product-title):
- Font: Branding-medium, Helvetica, Arial
- Size: 15px
- Weight: 600
- Color: #1a1a1a
- Line-height: 1.3
- Align: center

Kategoria produktu:
- Size: 11px
- Color: #666
- Transform: UPPERCASE
- Letter-spacing: 0.5px

Cena (price-new):
- Font: Branding-medium
- Size: 18px
- Weight: bold
- Color: #EF3340

Cena przekreślona (price-old):
- Size: 13px
- Color: #999
- Decoration: line-through

Oszczędności (savings):
- Size: 11px
- Color: #27ae60
- Weight: 600
```

### Przyciski CTA (z oryginalnego szablonu):

```css
Background: #f5333f
Color: #fff
Font-family: 'Branding', Helvetica, Arial
Font-size: 13px (mini) / 16px (main)
Font-weight: 700
Padding: 10px 20px (mini) / 16px 40px (main)
Border-radius: 50px (zaokrąglone pigułki)
Text-transform: none
```

---

## 📦 Struktura Szablonu

### 1. Header z Logo
- **Background:** #EF3340 (czerwony GenActiv)
- **Logo:** 200px szerokości
- **Separator:** Biała linia 1px (#FFF)
- ✅ Identyczna jak w oryginalnym szablonie

### 2. Hero Świąteczny
```html
🎄 Świąteczne Pakiety Prezentowe 🎁
```
- Wyśrodkowany nagłówek
- Font: Branding (bold)
- Emoji świąteczne: 🎄 🎁 🎅 ❄️ 🐶 🌟

### 3. Intro Text z Personalizacją
```liquid
Cześć {{ first_name|default:"" }}! 👋

Przygotowaliśmy dla Ciebie wyjątkowe zestawy świąteczne
z najlepszym Colostrum w Polsce. Idealne prezenty dla całej rodziny! 🎅

✨ Darmowa dostawa na wszystkie pakiety ✨
```

### 4. Grid Produktowy (5 produktów)

**Layout:**
- Desktop: 2 kolumny (50% / 50%)
- Mobile: Stack (100% szerokości każdy)
- Odstępy: 10px między kaflami

**Struktura pojedynczego kafla:**
```
┌─────────────────────────┐
│  [Badge - opcjonalny]   │
│  ┌─────────────────┐    │
│  │   Zdjęcie       │    │
│  │   250x180px     │    │
│  └─────────────────┘    │
│                         │
│  NAZWA PRODUKTU 🎁      │
│  Kategoria/opis         │
│                         │
│  [999 zł] 749 zł       │
│  Oszczędzasz 150 zł     │
│                         │
│  [ KUP TERAZ ]         │
└─────────────────────────┘
```

#### Produkt 1: ZESTAW RODZINNY 🎁
```yaml
Zawartość: 2× Classic + 1× Junior
Cena przed: 899 zł
Cena: 749 zł
Oszczędność: 150 zł
Link: /zestawy-swiateczne/rodzinny
```

#### Produkt 2: ZESTAW PREMIUM 🌟 ⭐ BESTSELLER
```yaml
Badge: "⭐ BESTSELLER" (złoty #F8A230)
Zawartość: 3× Classic + Dermo + FiberBiom
Cena przed: 1299 zł
Cena: 999 zł
Oszczędność: 300 zł
Link: /zestawy-swiateczne/premium
```

#### Produkt 3: ZESTAW STARTOWY 🎄
```yaml
Zawartość: 1× Classic + 1× Junior
Cena przed: 499 zł
Cena: 399 zł
Oszczędność: 100 zł
Link: /zestawy-swiateczne/startowy
```

#### Produkt 4: ZESTAW DERMO ❄️
```yaml
Zawartość: 2× Dermo Krem + 1× Classic
Cena przed: 699 zł
Cena: 549 zł
Oszczędność: 150 zł
Link: /zestawy-swiateczne/dermo
```

#### Produkt 5: ZESTAW ZOOGGIES 🐶
```yaml
Zawartość: Dla pupili - 3× Colostrum Zooggies
Cena przed: 449 zł
Cena: 349 zł
Oszczędność: 100 zł
Link: /zestawy-swiateczne/zooggies
Position: Wyśrodkowany (single, max-width 300px)
```

### 5. Urgency Banner
```
Background: #F8A230 (złoty)
Border-radius: 8px
Text:
  ⏰ OFERTA ŚWIĄTECZNA
  Gwarancja dostawy przed Świętami do 20 grudnia
```

### 6. Główny CTA
```
Button: ZOBACZ WSZYSTKIE PAKIETY
Style: Jak oryginał (red #f5333f, rounded 100px)
Link: /zestawy-swiateczne
```

### 7. Footer Image
- Używa oryginalnego obrazka z GenActiv
- Full width (600px)

### 8. Social Media Footer
- **Background:** #EF3340 (czerwony)
- Ikony: Instagram, Facebook, YouTube, TikTok
- Size: 32px każda
- Style: Subtle inverse (białe na czerwonym)
- ✅ Identyczny jak w oryginalnym szablonie

---

## 🎁 Świąteczne Akcenty

### Emoji użyte w szablonie:
- 🎄 Choinka (nagłówek, Zestaw Startowy)
- 🎁 Prezent (nagłówek, Zestaw Rodzinny)
- 🎅 Święty Mikołaj (intro text)
- 🌟 Gwiazdka (Zestaw Premium)
- ⭐ Gwiazda (badge Bestseller)
- ❄️ Płatek śniegu (Zestaw Dermo)
- 🐶 Pies (Zestaw Zooggies)
- ⏰ Zegar (urgency banner)
- ✨ Iskry (darmowa dostawa)
- 👋 Pomachaj (powitanie)

### Świąteczny tone of voice:
- "Świąteczne Pakiety Prezentowe"
- "Idealne prezenty dla całej rodziny"
- "Podaruj zdrowie swoim bliskim"
- "Gwarancja dostawy przed Świętami"

---

## 📱 Responsive Design

### Desktop (>480px):
- 2 kolumny produktów (50% / 50%)
- Padding: 10px między kaflami
- Max width kafla: ~270px

### Mobile (<480px):
- Stack wszystkich produktów (100% width)
- Każdy kafel pełna szerokość
- Zachowane odstępy 10px górą/dołem
- Zdjęcia responsive (max-width: 250px)

### Media Queries (wbudowane):
```css
@media only screen and (max-width: 480px) {
  .kl-text {
    padding-right: 18px !important;
    padding-left: 18px !important;
  }
  div.kl-row.colstack div.kl-column {
    display: block !important;
    width: 100% !important;
  }
}
```

---

## 🖼️ Obrazy do Zastąpienia

### Placeholdery obecne w szablonie:

1. **Zestaw Rodzinny**
   ```
   Obecny: https://via.placeholder.com/250x180/ffffff/EF3340?text=Zestaw+Rodzinny
   Wymiary: 250x180px
   Alt: "Zestaw Rodzinny"
   ```

2. **Zestaw Premium** (z badge Bestseller)
   ```
   Obecny: https://via.placeholder.com/250x180/ffffff/EF3340?text=Zestaw+Premium
   Wymiary: 250x180px
   Alt: "Zestaw Premium"
   ```

3. **Zestaw Startowy**
   ```
   Obecny: https://via.placeholder.com/250x180/ffffff/EF3340?text=Zestaw+Startowy
   Wymiary: 250x180px
   Alt: "Zestaw Startowy"
   ```

4. **Zestaw Dermo**
   ```
   Obecny: https://via.placeholder.com/250x180/ffffff/EF3340?text=Zestaw+Dermo
   Wymiary: 250x180px
   Alt: "Zestaw Dermo"
   ```

5. **Zestaw ZOOGGIES**
   ```
   Obecny: https://via.placeholder.com/250x180/ffffff/EF3340?text=Zestaw+ZOOGGIES
   Wymiary: 250x180px
   Alt: "Zestaw ZOOGGIES"
   ```

### Wytyczne dla zdjęć produktów:

**Format:** JPG lub PNG
**Wymiary:** 250x180px (ratio 1.39:1)
**Rozmiar:** <30KB każde (optymalizacja!)
**Style:**
- Produkt na białym lub jasnym tle
- Dobrze oświetlony
- Wyśrodkowany
- Border-radius: 6px (zostanie zastosowany automatycznie)

**Sugestie kompozycji:**
- Zestaw Rodzinny: 2 duże opakowania Classic + 1 małe Junior, ustawione obok siebie
- Zestaw Premium: 3 opakowania Classic + tubka Dermo + FiberBiom (5 produktów)
- Zestaw Startowy: 1 Classic + 1 Junior w prostym układzie
- Zestaw Dermo: 2 tubki Dermo Krem + 1 Classic w tle
- Zestaw ZOOGGIES: 3 opakowania Zooggies dla psów

---

## 🔗 UTM Tracking

Wszystkie linki produktowe:
```
?utm_source=klaviyo
&utm_medium=email
&utm_campaign=swieta_2025
```

**URLs produktów:**
- `/zestawy-swiateczne/rodzinny`
- `/zestawy-swiateczne/premium`
- `/zestawy-swiateczne/startowy`
- `/zestawy-swiateczne/dermo`
- `/zestawy-swiateczne/zooggies`

**Main CTA:**
- `/zestawy-swiateczne` (strona przeglądowa)

---

## ✅ Checklist Przed Wysyłką

### Obrazy:
- [ ] Zamień 5 placeholderów produktowych na prawdziwe zdjęcia (250x180px)
- [ ] Optimize każde zdjęcie <30KB
- [ ] Sprawdź czy wszystkie obrazy się ładują
- [ ] Zweryfikuj alt text na wszystkich obrazach

### Treść:
- [ ] Sprawdź ceny wszystkich zestawów (899/1299/499/699/449 zł)
- [ ] Zweryfikuj oszczędności (150/300/100/150/100 zł)
- [ ] Sprawdź deadline urgency ("20 grudnia")
- [ ] Personalizacja `{{ first_name }}` działa

### Linki:
- [ ] 5 × CTA "KUP TERAZ" (mini buttons) działają
- [ ] 1 × główny CTA "ZOBACZ WSZYSTKIE PAKIETY" działa
- [ ] UTM tracking na wszystkich 6 linkach
- [ ] Social media links aktualne
- [ ] Unsubscribe link obecny ✅

### Testing:
- [ ] Preview w Klaviyo UI
- [ ] Test wysyłka do siebie
- [ ] Sprawdź na iPhone (Safari)
- [ ] Sprawdź na Android (Gmail app)
- [ ] Desktop: Chrome, Safari, Outlook
- [ ] Wszystkie 5 produktów wyświetla się poprawnie
- [ ] Grid układa się w 2 kolumny (desktop)
- [ ] Stack na mobile działa
- [ ] Badge "BESTSELLER" widoczny tylko na produkcie 2
- [ ] Spam score check

---

## 📧 Kampania - Setup

### Subject Lines (A/B/C Test):

**Wariant A (Emocjonalny + emoji):**
```
🎄 Świąteczne pakiety z Colostrum - oszczędź do 300 zł 🎁
```

**Wariant B (Pilny):**
```
⏰ Ostatnie dni! 5 zestawów prezentowych + darmowa dostawa
```

**Wariant C (Wartościowy):**
```
Podaruj zdrowie bliskim - zestawy świąteczne do -23% 🌟
```

### Preview Text:
```
"5 zestawów na prezent | Oszczędź do 300 zł | Dostawa przed Świętami do 20.12"
```

### From Name:
```
GENACTIV®
```

### From Email:
```
sklep@genactiv.pl
```

---

## 🎯 Segmentacja Kampanii

### Segment 1: VIP Early Access (10-12.12)
- Klienci z 3+ zamówieniami w historii
- Subject: "Tylko dla Ciebie: Wczesny dostęp do zestawów świątecznych 🎁"
- Dodatkowy bonus: "Zamów do 15.12 i otrzymaj dodatkową próbkę"

### Segment 2: Past Buyers (13-16.12)
- Kupili w ostatnich 12 miesiącach
- Subject: A/B test wariantów A i B
- Focus na urgency (deadline 20.12)

### Segment 3: Cart Abandoners (14-17.12)
- Produkt w koszyku ostatnie 30 dni
- Subject: "Dokończ zakupy i odbierz ZESTAW ŚWIĄTECZNY 🎄"
- Personalizacja: pokaż ich produkt + sugestia zestawu

### Segment 4: Main List (15-18.12)
- Wszyscy pozostali subscribed
- Subject: A/B/C test wszystkich 3 wariantów
- Split 33% / 33% / 34%

### Segment 5: Last Minute (19-20.12)
- Non-openers z poprzednich segmentów
- Subject: "OSTATNIE 48H! Zestawy świąteczne + ekspresowa dostawa 🚀"
- Highlight tylko 3 najpopularniejsze zestawy

---

## 📊 Projected Performance

**Based on GenActiv benchmarks + multi-product layout:**

| Metryka | Target | Reasoning |
|---------|--------|-----------|
| Open Rate | **30%+** | Świąteczny + 5 produktów = więcej value |
| Click Rate | **7%+** | 5 produktów = 5× więcej szans na klik |
| Conversion | **3.5%+** | Okres prezentowy + wybór + urgency |
| AOV | **600 zł** | Średnia cena zestawów (349-999 zł) |
| CTR per product | **1.5%** | 7% total / 5 produktów ≈ 1.4% każdy |
| Unsubscribe | **<0.2%** | Wartościowa oferta produktowa |

**Revenue projection (4,500 odbiorców):**
```
4,500 odbiorców
× 30% open rate = 1,350 opens
× 7% click rate = 315 clicks
× 3.5% conversion = ~158 orders
× 600 zł AOV = 94,800 zł revenue

Potential upside with segmentation: 110,000-120,000 zł
```

---

## 💡 Tips & Best Practices

### 1. Która oferta będzie sprzedawać najlepiej?
**Predykcja na podstawie danych GenActiv:**

1. **ZESTAW PREMIUM** (999 zł) - 35-40% sprzedaży
   - Badge "BESTSELLER" generuje trust
   - Największa oszczędność (300 zł)
   - Kompletny zestaw (Colostrum + Dermo + FiberBiom)

2. **ZESTAW RODZINNY** (749 zł) - 25-30% sprzedaży
   - Dobra wartość (150 zł taniej)
   - Praktyczny (2×Classic + Junior)

3. **ZESTAW STARTOWY** (399 zł) - 20-25% sprzedaży
   - Najniższa bariera wejścia
   - Idealny dla nowych klientów

4. **ZESTAW DERMO** (549 zł) - 10-15% sprzedaży
   - Niszowy (kosmetyki)
   - Dla obecnych fanów Dermo

5. **ZESTAW ZOOGGIES** (349 zł) - 5-10% sprzedaży
   - Bardzo niszowy (właściciele psów)
   - Ale wysoka konwersja w segmencie!

### 2. Jak zwiększyć sprzedaż?

**Taktyka 1: Dynamic Product Ordering**
- Pokaż najpierw produkty najbardziej prawdopodobne dla danego klienta
- Jeśli kupił ZOOGGIES w przeszłości → ZOOGGIES na pozycji #1

**Taktyka 2: Scarcity per Product**
- Dodaj: "Pozostało tylko 5 zestawów!" pod produktem

**Taktyka 3: Bundle Savings Highlight**
- W nagłówku: "Oszczędź do 300 zł kupując zestaw"

**Taktyka 4: Social Proof per Product**
- Dodaj gwiazdki ⭐⭐⭐⭐⭐ (5/5) pod nazwą produktu
- "127 osób kupiło ten zestaw w tym tygodniu"

### 3. A/B Testing Ideas

**Test 1: Layout**
- Wariant A: 2 kolumny (obecny)
- Wariant B: 1 kolumna (pełna szerokość każdy produkt)
- Hipoteza: Większe zdjęcia = wyższa konwersja

**Test 2: Product Order**
- Wariant A: Premium (#1), Rodzinny (#2)
- Wariant B: Rodzinny (#1), Premium (#2)
- Hipoteza: Pierwszy produkt dostaje 40% uwagi

**Test 3: CTA Text**
- Wariant A: "KUP TERAZ"
- Wariant B: "DODAJ DO KOSZYKA"
- Wariant C: "ZAMÓW PREZENT"

**Test 4: Urgency Placement**
- Wariant A: Banner pod produktami (obecny)
- Wariant B: Banner NAD produktami
- Hipoteza: Early urgency = wyższy CTR

---

## 🔄 Warianty Szablonu

### Wariant 1: Top 3 Only (dla mobile-first)
- Usuń produkty 4 i 5
- Zostaw tylko: Premium, Rodzinny, Startowy
- Szybsze ładowanie
- Mniej scroll
- Wyższy focus

### Wariant 2: Single Hero Product + 4 Secondary
- Produkt #1 (Premium): Pełna szerokość, duży
- Pozostałe 4: Mniejsze, 2×2 grid
- Highlight bestsellera

### Wariant 3: With Reviews
- Dodaj gwiazdki + review count pod każdym produktem
- "★★★★★ (127 opinii)"
- Social proof per item

### Wariant 4: With Countdown Timer
- Dodaj live countdown do urgency bannera
- "Oferta kończy się za: 23:45:12"
- Narzędzie: Motionmail lub Sendtric

---

## 📞 Support

**Template ID:** `Y4cwDB`
**Bazuje na:** Oryginalnym szablonie GenActiv (cart abandonment)
**Data utworzenia:** 2 grudnia 2025
**Wersja:** 1.0

**W razie pytań:**
- Klaviyo: https://www.klaviyo.com/email-editor/Y4cwDB/edit
- Dokumentacja GenActiv: ./CLAUDE.md
- Black Friday Report: ./black-friday-2024-2025-report.md

---

## 🎄 Happy Holidays from GenActiv! 🎁

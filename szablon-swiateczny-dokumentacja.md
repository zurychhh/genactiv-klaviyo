# 🎄 Szablon Świąteczny - Dokumentacja

## 📧 Informacje Podstawowe

**Nazwa szablonu:** `Swieta_Pakiety_Prezentowe_2025`
**Template ID:** `SUN9fn`
**Typ:** Produktowy (e-commerce)
**Kategoria:** Kampania świąteczna/promocyjna
**URL w Klaviyo:** https://www.klaviyo.com/email-editor/SUN9fn/edit

---

## 🎨 Design System - GenActiv.pl

### Kolory Brand (rzeczywiste z genactiv.pl):

| Element | Hex Code | Użycie |
|---------|----------|--------|
| **Primary Red** | `#f5333f` | CTA buttony, nagłówki, akcenty, obramowania |
| **Hover Red** | `#ffa9ad` | Stan hover dla przycisków |
| **Deep Red** | `#ea0b19` | Alternatywny hover |
| **Gold Accent** | `#F8A230` | Badge "Bestseller", urgency banner |
| **Dark Brown** | `#1a1818` | Teksty główne, nagłówki |
| **White** | `#ffffff` | Tło, tekst na kolorach |
| **Light Gray** | `rgba(26,24,24,0.05)` | Sekcje tła |
| **Product BG** | `rgba(245,51,63,0.05)` | Tło zdjęć produktów |

### Typografia:

```css
Font Family: 'Branding', Helvetica, Arial, sans-serif

H1 (Hero):
- Size: 37px
- Weight: 700
- Transform: UPPERCASE
- Letter-spacing: 0.05em
- Color: #ffffff (na czerwonym tle)

H2 (Produkty):
- Size: 23px
- Weight: 700
- Transform: UPPERCASE
- Letter-spacing: 0.1em
- Color: #1a1818

Body:
- Size: 14-16px
- Weight: 400
- Line-height: 1.5-1.6
- Color: #1a1818

CTA Buttons:
- Size: 14px
- Weight: 700
- Transform: UPPERCASE
- Letter-spacing: 0.05em
```

### Przyciski CTA:

**Primary (Red):**
```css
Background: #f5333f
Color: #ffffff
Padding: 16px 30px
Border-radius: 5px
Hover: #ffa9ad
```

**Secondary (Outline):**
```css
Border: 2px solid #f5333f
Color: #f5333f
Background: transparent
Border-radius: 5px
```

---

## 📦 Struktura Szablonu

### 1. Logo Header
- Logo GenActiv (180x60px)
- Padding: 30px
- Background: White

### 2. Hero Banner (Red)
```
Background: #f5333f
Text: White
Content:
  - "ŚWIĄTECZNE PAKIETY PREZENTOWE" (H1)
  - "Podaruj zdrowie swoim bliskim" (subtitle)
```

### 3. Intro Text
- Personalizacja: `{{ first_name|default:"" }}`
- Wycentrowany tekst
- 2-3 zdania wprowadzające

### 4. Produkty (3 zestawy)

#### Zestaw 1: RODZINNY
```yaml
Zawartość:
  - Colostrum Classic 500g x2
  - Colostrum Junior z Czarnym Bzem 150g x1
  - Darmowa dostawa
  - Eleganckie opakowanie

Ceny:
  - Przed: 899 zł (przekreślone)
  - Teraz: 749 zł (czerwony, duży)
  - Oszczędność: 150 zł

CTA: "KUP TERAZ" (red button)
Link: /zestawy-swiateczne/rodzinny
```

#### Zestaw 2: PREMIUM (Bestseller)
```yaml
Badge: "⭐ BESTSELLER" (złoty)

Zawartość:
  - Colostrum Classic 500g x3
  - Colostrum Dermo Krem 50ml x1
  - FiberBiom 200g x1
  - Darmowa dostawa ekspresowa
  - Luksusowe opakowanie + kartka

Ceny:
  - Przed: 1,299 zł
  - Teraz: 999 zł
  - Oszczędność: 300 zł

CTA: "KUP TERAZ"
Link: /zestawy-swiateczne/premium
```

#### Zestaw 3: STARTOWY
```yaml
Zawartość:
  - Colostrum Classic 500g x1
  - Colostrum Junior 150g x1
  - Darmowa dostawa
  - Świąteczna kartka

Ceny:
  - Przed: 499 zł
  - Teraz: 399 zł
  - Oszczędność: 100 zł

CTA: "KUP TERAZ"
Link: /zestawy-swiateczne/startowy
```

### 5. Urgency Banner
```
Background: #F8A230 (złoty)
Icon: ⏰
Text: "OFERTA OGRANICZONA CZASOWO"
Deadline: "Gwarancja dostawy przed Świętami do 20 grudnia"
```

### 6. Benefits Section (4 punkty)
- Darmowa dostawa
- Nr 1 w aptekach
- Gwarancja jakości
- Eleganckie pakowanie

Każdy z:
- Czerwonym checkmarkiem (okrągły)
- Bold nagłówkiem
- Opisem

### 7. Secondary CTA
```
Button: Outline (red border)
Text: "ZOBACZ WSZYSTKIE PRODUKTY"
Link: /produkty
```

### 8. Footer
- Social media icons (32x32px)
- Kontakt (email, tel)
- Legal links
- Unsubscribe link
- Background: #1a1818 (ciemny)

---

## 🔗 UTM Tracking

Wszystkie linki używają parametrów:
```
?utm_source=klaviyo
&utm_medium=email
&utm_campaign=swieta_pakiety_2025
```

**Produkty:**
- `/zestawy-swiateczne/rodzinny`
- `/zestawy-swiateczne/premium`
- `/zestawy-swiateczne/startowy`

**Browse:**
- `/produkty`

---

## 📱 Responsive Design

### Desktop (>600px):
- Max width: 600px
- Produkty: pełna szerokość
- Layout: 2 kolumny (cena + CTA)

### Mobile (<600px):
- Stack wszystkie elementy
- CTA buttons: full width
- Font size: zachowany (14px minimum)
- Touch targets: >44x44px ✅

---

## 🖼️ Obrazy do Zastąpienia

### 1. Logo GenActiv
```
Obecny: Placeholder (180x60px)
Format: PNG z przezroczystym tłem
Alt text: "GenActiv"
Lokalizacja: Header
```

### 2. Zestaw Rodzinny (Produkt 1)
```
Wymiary: 560x280px
Format: JPG/PNG
Optimize: <50KB
Sugestie:
  - 2x Colostrum Classic + 1x Junior
  - Świąteczne dekoracje w tle
  - Product shot na białym/jasnym tle
Alt text: "Zestaw Rodzinny Colostrum"
```

### 3. Zestaw Premium (Produkt 2)
```
Wymiary: 560x280px
Format: JPG/PNG
Optimize: <50KB
Sugestie:
  - 3x Colostrum + Dermo + FiberBiom
  - Luksusowe opakowanie
  - Badge "Bestseller" widoczny na zdjęciu
Alt text: "Zestaw Premium Colostrum"
```

### 4. Zestaw Startowy (Produkt 3)
```
Wymiary: 560x280px
Format: JPG/PNG
Optimize: <50KB
Sugestie:
  - 1x Colostrum Classic + 1x Junior
  - Proste, eleganckie
  - Idealny dla początkujących
Alt text: "Zestaw Startowy Colostrum"
```

### 5. Social Media Icons (3 sztuki)
```
Wymiary: 32x32px każdy
Format: PNG
Ikony: Facebook, Instagram, LinkedIn
Style: Czerwone (#f5333f) na przezroczystym
```

---

## ✅ Checklist Przed Wysyłką

### Treść:
- [ ] Zastąp wszystkie placeholdery obrazów prawdziwymi
- [ ] Zweryfikuj ceny produktów (899/749/399 zł)
- [ ] Sprawdź daty urgency ("do 20 grudnia")
- [ ] Dodaj rzeczywisty numer telefonu
- [ ] Zaktualizuj linki do produktów
- [ ] Sprawdź personalizację `{{ first_name }}`

### Obrazy:
- [ ] Logo GenActiv (180x60px)
- [ ] 3x zdjęcia produktów (560x280px każde)
- [ ] 3x ikony social media (32x32px)
- [ ] Optimize wszystkie <100KB total

### Linki:
- [ ] Wszystkie 3 CTA "KUP TERAZ" działają
- [ ] Secondary CTA "ZOBACZ WSZYSTKIE" działa
- [ ] UTM tracking na wszystkich linkach
- [ ] Social media links zaktualizowane
- [ ] Unsubscribe link obecny ✅

### Testing:
- [ ] Preview w Klaviyo
- [ ] Test wysyłka do siebie
- [ ] Sprawdź na mobile (iOS + Android)
- [ ] Sprawdź na desktop (Chrome, Safari, Outlook)
- [ ] Verify all images load
- [ ] Spam score check (<5/10)
- [ ] Click tracking włączony w Klaviyo

---

## 📧 Kampania - Setup Recommendations

### Subject Lines (A/B/C Test):

**Wariant A (Produktowy):**
```
🎁 Świąteczne pakiety Colostrum - oszczędź do 300 zł
```

**Wariant B (Pilny):**
```
⏰ Ostatnie dni! Zestawy prezentowe z darmową dostawą
```

**Wariant C (Emocjonalny):**
```
🎄 Podaruj zdrowie bliskim - pakiety świąteczne GenActiv
```

### Preview Text:
```
"3 zestawy na prezent | Darmowa dostawa | Gwarancja przed Świętami"
```

### Segmentacja:

#### Segment 1: VIP (wysłane 10-15.12)
- Klienci z 3+ zamówieniami
- Early access
- Subject: "Tylko dla Ciebie: Wczesny dostęp do zestawów świątecznych 🎁"

#### Segment 2: Past Buyers (wysłane 15-18.12)
- Kupili w ostatnich 12 miesiącach
- Remind o deadline
- Subject: "Podaruj Colostrum bliskim - pakiety do 20.12 🎄"

#### Segment 3: Main List (wysłane 16-20.12)
- Wszyscy pozostali
- A/B test 3 variants
- Urgency: "tylko do 20.12"

#### Segment 4: Last Minute (wysłane 18-20.12)
- Non-openers z poprzednich
- Subject: "Ostatnie 48h! Zestawy świąteczne GenActiv ⏰"

### Timing:
```
Najlepszy czas wysyłki:
- Wtorek-Czwartek
- 09:00-11:00 CET
- Unikaj: Piątek po 15:00, Weekend
```

---

## 📊 Projected Performance

**Based on GenActiv benchmarks + świąteczny season:**

| Metryka | Target | Reasoning |
|---------|--------|-----------|
| Open Rate | **32%+** | Świąteczny temat + produkty w subject |
| Click Rate | **6%+** | 3 produkty = więcej szans na klik |
| Conversion | **3%+** | Okres prezentowy + urgency |
| AOV | **650 zł** | Średnia cena zestawów (399-999 zł) |
| Unsubscribe | **<0.25%** | Wartościowa oferta |

**Revenue projection (4,500 odbiorców):**
```
4,500 × 32% open × 6% click × 3% conv = ~260 orders
260 orders × 650 zł AOV = 169,000 zł revenue
```

---

## 🔄 Warianty Szablonu (Możliwe Modyfikacje)

### Wariant 1: Single Product Focus
- Usuń 2 produkty
- Zostaw tylko "Zestaw Premium"
- Większe zdjęcie (600x400px)
- Więcej social proof

### Wariant 2: Early Bird
- Zmień urgency na "Early bird: zamów do 15.12"
- Dodaj countdown timer
- Extra bonus: darmowa kartka personalizowana

### Wariant 3: Last Minute
- Subject: "OSTATNIE 24H!"
- Hero banner: Czerwony z odliczaniem
- Tylko "Zestaw Startowy" (najszybsza dostawa)
- CTA: "ZAMÓW TERAZ - DOSTAWA JUTRO"

---

## 🛠️ Upload Obrazów (Tutorial)

### Przez Klaviyo API:

```python
# Upload logo
klaviyo_upload_image_from_file(
  file_path="/path/to/genactiv-logo.png",
  name="GenActiv Logo"
)

# Upload product photos
klaviyo_upload_image_from_file(
  file_path="/path/to/zestaw-rodzinny.jpg",
  name="Zestaw Rodzinny Produkt"
)
```

### Przez Klaviyo UI:
1. Otwórz szablon: https://www.klaviyo.com/email-editor/SUN9fn/edit
2. Kliknij na placeholder image
3. "Replace image" → Upload
4. Wybierz plik z komputera
5. Adjust positioning (center, cover)
6. Save

---

## 📞 Support & Kontakt

**W razie pytań:**
- Klaviyo Support: support@klaviyo.com
- GenActiv Marketing: kontakt@genactiv.pl
- Template ID do referencji: `SUN9fn`

**Dokumentacja:**
- [Klaviyo Email Templates Guide](https://help.klaviyo.com/hc/en-us/articles/115005249908)
- [GenActiv Brand Guidelines](./CLAUDE.md)
- [Black Friday Report](./black-friday-2024-2025-report.md)

---

**Data utworzenia:** 2 grudnia 2025
**Ostatnia aktualizacja:** 2 grudnia 2025
**Wersja:** 1.0

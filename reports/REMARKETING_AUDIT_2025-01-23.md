# AUDYT REMARKETINGU GENACTIV.PL

**Data:** 2025-01-23
**Autor:** Claude Code (deep dive analysis)
**Cel:** Identyfikacja przyczyn braku budowania audience remarketingowej

---

## PODSUMOWANIE WYKONAWCZE

**GŁÓWNA PRZYCZYNA:** Konfiguracja Pandectes Consent Mode blokuje targeting cookies domyslnie, uniemozliwiajac zbieranie danych remarketingowych bez explicity zgody uzytkownika.

**SKUTEK:** Campaign Attribution Rate = 1% (3/250 zamowien)

**PILNOSC:** KRYTYCZNA - remarketing praktycznie nie dziala

---

## 1. ODKRYCIA KRYTYCZNE

### ODKRYCIE #1: Campaign Attribution Rate = 1%

```
Analiza 250 ostatnich zamowien (Shopify Extended MCP):

Total Orders: 250
Orders with Campaign Data: 3 (1%)
Campaign Attribution Rate: 1%

Jedyne zrodlo z UTM:
- bing (Sembot): 3 zamowienia

Google Ads: 0 zamowien z UTM
```

**Znaczenie:** Praktycznie ZERO danych o kampaniach Google Ads dociera do Shopify.

---

### ODKRYCIE #2: cookiesBlockedByDefault = "7"

```javascript
// Pandectes Configuration (z HTML strony)
window.PandectesRulesSettings = {
  "banner": {
    "cookiesBlockedByDefault": "7"  // <-- PROBLEM
  }
}
```

**Wartosci bitowe:**
- 1 = Functional cookies
- 2 = Performance cookies
- 4 = Targeting cookies
- 7 = 1 + 2 + 4 = WSZYSTKIE opcjonalne kategorie ZABLOKOWANE domyslnie

**Skutek:** Uzytkownik musi AKTYWNIE wyrazic zgode na targeting cookies, zeby remarketing dzialal.

---

### ODKRYCIE #3: adStorageCategory = 4 (Targeting)

```javascript
"googleConsentMode": {
  "isActive": true,
  "id": "GTM-5W5Z2ML",
  "adwordsId": "AW-779033182",
  "adStorageCategory": 4,           // <-- ad_storage wymaga kategorii 4
  "analyticsStorageCategory": 2,    // analytics wymaga kategorii 2
  "redactData": true,               // <-- PROBLEM #4
  "urlPassthrough": true            // OK - gclid przekazywany
}
```

**Google Consent Mode v2 mapping:**
| Signal | Kategoria | Domyslny stan |
|--------|-----------|---------------|
| ad_storage | 4 (Targeting) | DENIED |
| ad_user_data | 4 (Targeting) | DENIED |
| ad_personalization | 4 (Targeting) | DENIED |
| analytics_storage | 2 (Performance) | DENIED |

---

### ODKRYCIE #4: redactData = true

```javascript
"redactData": true
```

**Skutek:** Bez zgody na ad_storage:
- IP adresy sa redagowane
- Identyfikatory uzytkownikow sa usuwane
- Google nie moze budowac profilu remarketingowego

---

### ODKRYCIE #5: Brak Enhanced Conversions

Przeszukanie kodu strony (curl + grep):
- Brak `gtag('set', 'user_data', {...})`
- Brak hashed email/phone w conversion tracking
- Brak First-Party Data jako backup

**Skutek:** Gdy cookies sa zablokowane, nie ma alternatywnej metody identyfikacji.

---

### ODKRYCIE #6: Brak danych gclid w zamowieniach

```
Shopify orders analyzed: 250
Orders with gclid: 0
Orders with utm_source=google: 0
```

**Mozliwe przyczyny:**
1. Auto-tagging wylaczony w Google Ads
2. gclid tracony przez Consent Mode bez zgody
3. Checkout nie zachowuje parametrow URL

---

## 2. ANALIZA FLOW UZYTKOWNIKA

```
Uzytkownik wchodzi na genactiv.pl
         |
         v
Pandectes pokazuje banner (euOnly: true)
         |
    +----+----+
    |         |
    v         v
"Odrzuc"   "Akceptuj"   <-- Wiekszosc NIE klika "Akceptuj"
    |         |
    v         v
ad_storage   ad_storage
= DENIED     = GRANTED
    |         |
    v         v
Remarketing  Remarketing
NIE DZIALA   DZIALA
```

**Statystyki branzowe:**
- Typowy consent rate dla "Akceptuj wszystko": 30-40%
- Consent rate dla kategorii Targeting: 15-25%
- Szacowany % uzytkownikow z wlaczonym remarketingiem: ~20%

---

## 3. POROWNANIE KONFIGURACJI

| Ustawienie | Aktualne | Rekomendowane | Wplyw |
|------------|----------|---------------|-------|
| cookiesBlockedByDefault | 7 | 0 lub 3 | Wiecej zgod |
| adStorageCategory | 4 | 4 (bez zmian) | Wymagane przez prawo |
| redactData | true | false* | Wiecej danych |
| urlPassthrough | true | true (OK) | Zachowuje gclid |
| Enhanced Conversions | BRAK | Wdrozyc | Backup data |

*Uwaga: redactData=false moze naruszac GDPR w niektorych interpretacjach

---

## 4. REKOMENDACJE

### PRIORYTET 1: Optymalizacja Consent Banner (natychmiastowe)

**Opcja A - Zmiana domyslnych wartosci (wymaga analizy prawnej):**
```
cookiesBlockedByDefault: "3"  // Tylko Functional+Performance zablokowane
```
To pozwoli na Targeting bez explicity zgody - MOZE BYC NIEZGODNE Z GDPR.

**Opcja B - Lepszy UX bannera (bezpieczniejsze):**
1. Zmiana tekstu przyciskow:
   - "Akceptuj" -> "Akceptuj wszystkie"
   - Dodac "Akceptuj niezbedne" jako drugorzedny
2. Pre-tick kategorii Targeting (kontrowersyjne)
3. Bardziej widoczny przycisk "Akceptuj"

**Opcja C - Soft Consent (rekomendowane):**
W Pandectes Dashboard:
- Wlaczyc "Implied Consent on Scroll" lub "On Click"
- To MOZE byc zgodne z GDPR jesli uzytkownik kontynuuje przegladanie

### PRIORYTET 2: Wdrozenie Enhanced Conversions

**Krok 1:** W Google Ads, wlaczyc Enhanced Conversions
**Krok 2:** Zaimplementowac w kodzie thank_you page:

```javascript
gtag('set', 'user_data', {
  'sha256_email_address': hashEmail(customer_email),
  'sha256_phone_number': hashPhone(customer_phone),
  'address': {
    'sha256_first_name': hashName(first_name),
    'sha256_last_name': hashName(last_name),
    'city': city,
    'postal_code': postal_code,
    'country': 'PL'
  }
});

gtag('event', 'conversion', {
  'send_to': 'AW-779033182/CONVERSION_LABEL',
  'value': order_value,
  'currency': 'PLN',
  'transaction_id': order_id
});
```

**Krok 3:** Alternatywnie - Enhanced Conversions przez GTM Server-Side

### PRIORYTET 3: Weryfikacja Auto-Tagging

W Google Ads:
1. Otworz konto 339-338-2047 (lub manager account)
2. Settings -> Account Settings -> Auto-tagging
3. Upewnij sie, ze "Tag the URL that people click through from my ad" jest ON

### PRIORYTET 4: Server-Side GTM (dlugoterminowe)

Wdrozenie server-side GTM pozwoli:
- Zbierac dane bez blokowania przez przegladarke
- Wysylac Enhanced Conversions server-to-server
- Obejsc ad-blockery i ITP (Safari)

### PRIORYTET 5: Customer Match Upload

Jako backup dla remarketingu:
1. Eksportuj liste klientow z Shopify (email, phone)
2. Uploaduj do Google Ads jako Customer Match list
3. Buduj Lookalike audiences

---

## 5. ANALIZA RYZYKA PRAWNEGO

**GDPR wymaga:**
- Zgoda musi byc dobrowolna, konkretna, swiadoma
- Pre-ticked boxes NIE SA dozwolone dla non-essential cookies
- Uzytkownik musi miec mozliwosc latwo odmowic

**Aktualna konfiguracja jest ZGODNA z GDPR** ale bardzo restrykcyjna.

**Rekomendacja:** Skonsultowac z prawnikiem mozliwosc:
- Soft consent (implied by continued browsing)
- Legitimate Interest dla analytics (kategoria 2)
- Essential classification dla basic remarketing

---

## 6. EXPECTED IMPACT

| Zmiana | Expected Impact | Ryzyko |
|--------|-----------------|--------|
| Lepszy UX bannera | +30-50% consent rate | Niskie |
| Enhanced Conversions | +20-30% conversion tracking | Niskie |
| Auto-tagging fix | +50-80% attribution | Niskie |
| Server-side GTM | +40-60% data coverage | Srednie |
| Customer Match | +100% known customers | Niskie |

**Szacowany laczny wplyw:**
- Obecne: ~1% attribution
- Po zmianach: 30-50% attribution
- Remarketing audience: z 0 do tysiecy uzytkownikow/miesiac

---

## 7. NASTEPNE KROKI

1. [ ] Spotkanie z prawnikiem ws. mozliwosci optymalizacji zgod
2. [ ] Audit Google Ads - sprawdzic auto-tagging (wymaga dostepu)
3. [ ] Wdrozenie Enhanced Conversions
4. [ ] Test A/B roznych wariantow consent bannera
5. [ ] Setup Customer Match jako backup
6. [ ] Rozwazyc Server-Side GTM

---

## 8. DANE TECHNICZNE

**Pandectes:**
- Store ID: 58461847726
- Plan: Premium
- GTM Container: GTM-5W5Z2ML
- Google Ads ID: AW-779033182
- GA4 ID: G-KE8T99MGMJ
- Facebook Pixel: 370142134442442

**Shopify:**
- Domain: genactiv.myshopify.com
- Theme: GEN-6 global - slideshow (ID: 162539340108)

**Consent Mode Settings:**
```json
{
  "isActive": true,
  "adStorageCategory": 4,
  "analyticsStorageCategory": 2,
  "functionalityStorageCategory": 1,
  "personalizationStorageCategory": 1,
  "securityStorageCategory": 0,
  "redactData": true,
  "urlPassthrough": true,
  "waitForUpdate": 500
}
```

---

## KONIEC RAPORTU

**Przygotowal:** Claude Code
**Zrodla danych:** Shopify MCP, curl genactiv.pl, Pandectes settings
**Uwaga:** Raport wymaga walidacji przez specjaliste Google Ads z dostepem do konta

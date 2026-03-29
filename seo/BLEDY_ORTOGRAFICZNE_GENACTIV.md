# Błędy ortograficzne i interpunkcyjne na genactiv.pl

**Data skanowania:** 2025-01-23
**Liczba przeskanowanych stron:** 31

---

## PODSUMOWANIE

| Typ błędu | Ilość wystąpień | Priorytet |
|-----------|-----------------|-----------|
| Podwójna spacja w nagłówku | Wszystkie strony | WYSOKI |
| Spacja przed kropką " ." | 12 stron | ŚREDNI |
| Spacja przed przecinkiem " ," | 8 stron | ŚREDNI |
| Podwójne kropki ".." | 1 strona | NISKI |
| Literówka "skutecznośc" | 3 strony | WYSOKI |

---

## 1. BŁĄD GLOBALNY - NAGŁÓWEK STRONY

**Problem:** Podwójna spacja w banerze "Darmowa dostawa"

**Obecny tekst:**
```
Darmowa dostawa od 300 zł. Darmowa dostawa  od 300 zł.
                                           ^^
                                     (podwójna spacja)
```

**Poprawka:**
```
Darmowa dostawa od 300 zł.
```

**Lokalizacja:** Prawdopodobnie w ustawieniach motywu lub sekcji nagłówka
**Dotyczy:** WSZYSTKICH stron na genactiv.pl

---

## 2. LITERÓWKA: "skutecznośc" → "skuteczność"

| Strona | Kontekst |
|--------|----------|
| /pages/co-to-jest-mleko-klaczy | "...zagwarantować zachowanie najwyższej **skutecznośc**i i jakości..." |
| /pages/badania-genactiv-colostrum | "...prowadzone są od wielu lat i dowodzą **skutecznośc**i w zapobieganiu..." |
| /pages/eksperci | "...prowadzone są od wielu lat i dowodzą **skutecznośc**i super substancji..." |

**Poprawka:** "skutecznośc" → "skuteczność"

---

## 3. SPACJA PRZED KROPKĄ " ."

| Strona | Fragment z błędem |
|--------|-------------------|
| / (strona główna) | "...narodziła się marka ZOOGGIES **.** Stworzona z miłości..." |
| /pages/co-to-jest-colostrum | "...Mol. Neurosci., 2001; 17: 379–389 (17) **.** Rak K., Bronkowska M..." |
| /pages/faq | "...otrzymanego suchego produktu **.** Proces liofilizacji jest..." |
| /pages/badania-genactiv-colostrum | "...grupie 158 studentów uczelni medycznej **.** Uczestnicy zostali..." |
| /pages/flora-jelitowa | "...oraz perystaltykę jelit **.** Właśnie dlatego lekarze..." |
| /pages/flora-bakteryjna | "...Mikrobiota przewodu pokarmowego. Red. **.** : PZWL Wydawnictwo..." |
| /pages/mikrobiota-jelitowa | "...szczelności jelita **.** Otóż centralną częścią..." |
| /pages/kazeina | "...jest więc jej termostabilność **.** Inną ważną funkcją..." |
| /pages/kwas-hialuronowy | "...w dermokosmetykach Genactiv **.** W połączeniu z bioaktywnym..." |
| /pages/egf-naskorkowy-czynnik-wzrostu | "...Nagrodą Nobla [1] **.** W ramach badań dowiedli..." |
| /pages/sibo | "...chorób towarzyszących objawom SIBO **.** Jakie badania może zlecić..." |
| /pages/ltryptofan-i-tryptofan | "...nastroju czyli serotoninę **.** Hormon ten odpowiada..." |

**Poprawka:** Usuń spację przed kropką

---

## 4. SPACJA PRZED PRZECINKIEM " ,"

| Strona | Fragment z błędem |
|--------|-------------------|
| / (strona główna) | "...Nutrition **,** 90, 111273..." |
| /pages/co-to-jest-colostrum | "...Siwicki A. **,** Laktoferyna..." |
| /pages/badania-genactiv-colostrum | "...250 składników aktywnych **,** zamkniętych w naturalnej..." |
| /pages/eksperci | "...160 nowych publikacji naukowych **,** które dotyczą..." |
| /pages/enzymy | "...Enzymy to substancje naturalne **,** które odpowiadają..." |
| /pages/alfa-laktoalbumina | "...frakcji białkowej mleka **,** Medycyna Wet. 2008..." |
| /pages/igf-1 | "...eliminacja z diety mleka krowiego **,** odżywek białkowych..." |
| /pages/sibo | "...powoduje objawy SIBO **,** np. biegunkę i wzdęcia..." |

**Poprawka:** Usuń spację przed przecinkiem

---

## 5. PODWÓJNE KROPKI ".."

| Strona | Fragment z błędem |
|--------|-------------------|
| / (strona główna) | "...niejadka, który odmawia jedzenia **..** Po prostu posyp..." |

**Poprawka:** ".." → "."

---

## PRIORYTETYZACJA NAPRAW

### Priorytet 1 (WYSOKI) - Wpływ na wizerunek marki
1. ✅ Napraw podwójną spację w nagłówku "Darmowa dostawa" (dotyczy wszystkich stron)
2. ✅ Popraw "skutecznośc" → "skuteczność" (3 strony)

### Priorytet 2 (ŚREDNI) - Błędy interpunkcyjne
3. Usuń spacje przed kropkami (12 wystąpień)
4. Usuń spacje przed przecinkami (8 wystąpień)

### Priorytet 3 (NISKI) - Drobne błędy
5. Popraw podwójne kropki (1 wystąpienie)

---

## GDZIE WPROWADZIĆ ZMIANY

| Błąd | Lokalizacja w Shopify |
|------|----------------------|
| Podwójna spacja w nagłówku | Theme → Customize → Header/Announcement bar |
| Literówki w treści stron | Online Store → Pages → [nazwa strony] → Edit |
| Błędy w opisach produktów | Products → [produkt] → Edit |

---

## UWAGI

1. **False positives pominięte:** Słowa jak "odpornościowego", "immunologicznego" są poprawne (odmiana przez przypadki)

2. **Powtarzający się wzorzec:** Wiele błędów interpunkcyjnych pochodzi z cytowań naukowych - mogą być celowe dla zachowania oryginalnego formatu bibliografii

3. **Zakres skanowania:** Przeskanowano 31 głównych stron informacyjnych. Nie skanowano:
   - Stron produktów (87 produktów)
   - Postów blogowych
   - Stron kolekcji

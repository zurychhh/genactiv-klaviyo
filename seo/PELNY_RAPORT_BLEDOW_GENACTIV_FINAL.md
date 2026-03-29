# Pełny raport błędów ortograficznych, gramatycznych i stylistycznych
# genactiv.pl

**Data skanowania:** 2026-01-28
**Łączna liczba przeskanowanych stron:** 179
**W tym:**
- Strony informacyjne: 47
- Strony produktowe: 63
- Kolekcje: 41
- Blog: 28

---

## PODSUMOWANIE OGÓLNE

| Kategoria | Liczba błędów | Priorytet |
|-----------|---------------|-----------|
| **Literówki ortograficzne** | 20 | 🔴 WYSOKI |
| **Błędy interpunkcyjne** | 532 | 🟡 ŚREDNI |
| **Błędy gramatyczne** | 3 | 🔴 WYSOKI |
| **ŁĄCZNIE BŁĘDÓW** | **555** | |

---

## 1. LITERÓWKI ORTOGRAFICZNE (20 wystąpień)

### Priorytet WYSOKI - wpływ na wizerunek marki

| Błędne słowo | Poprawka | Strona | Uwagi |
|--------------|----------|--------|-------|
| **GENACITV** | GENACTIV | Produkty FUREVER (12 stron) | Błąd w opisie składu |
| **prawidziwe** | prawdziwe | /products/mleko-klaczy-w-30-saszetkach | |
| **prawidziwe** | prawdziwe | /products/mleko-klaczy-genactiv-120-kapsulek | |
| **Jeydnym** | Jedynym | /products/maseczka-z-colostrum-50-ml | |
| **MASKA Z COLOSTRUM GENACITV** | MASKA Z COLOSTRUM GENACTIV | /products/maska-z-colostrum-genactiv-250-ml | Błąd w nazwie produktu |

### Szczegółowe wystąpienia literówki "GENACITV":
- /products/furever-horse-proszek-5500-g
- /products/furever-horse-proszek-2500-g
- /products/furever-dog-proszek-100-g
- /products/furever-dog-120-kapsulek
- /products/furever-dog-60-kapsulek
- /products/furever-cat-proszek-75g
- /products/furever-cat-90-kapsulek
- /products/furever-horse
- /products/furever-cat
- /products/furever-dog
- /products/all-furever-30-kapsulek
- /products/all-furever-90-kapsulek
- /products/all-furever-proszek-50-g
- /products/maska-z-colostrum-genactiv-250-ml (2x)

---

## 2. BŁĘDY INTERPUNKCYJNE (532 wystąpienia)

### Podsumowanie typów błędów:

| Typ błędu | Liczba | Priorytet |
|-----------|--------|-----------|
| Podwójna spacja | 196 | 🟡 ŚREDNI |
| Spacja przed przecinkiem | 137 | 🟡 ŚREDNI |
| Spacja przed kropką | 80 | 🟡 ŚREDNI |
| Podwójne kropki ".." | 64 | 🟢 NISKI |
| Brak spacji po średniku | 55 | 🟢 NISKI |

### Przykłady błędów (wybrane):

#### Podwójna spacja (196 wystąpień)
- Strona główna: "produkty, którym zaufały już tysiące ludzi.  Bo zdrowie..."
- FAQ: "Colostrum Genactiv  jest..."
- Poznaj Genactiv: "Napędzani pasją do Colostrum, tworzymy  rozwiązania..."

#### Spacja przed kropką (80 wystąpień)
- "/" : "narodziła się marka ZOOGGIES **.**"
- /pages/flora-jelitowa: "perystaltykę jelit **.**"
- /pages/sibo: "objawom SIBO **.**"
- /pages/kwas-hialuronowy: "dermokosmetykach Genactiv **.**"

#### Spacja przed przecinkiem (137 wystąpień)
- "/" : "Journal of Molecular Sciences **,**"
- /pages/co-to-jest-colostrum: "Siwicki A. **,** Laktoferyna..."
- /pages/enzymy: "substancje naturalne **,** które..."

#### Podwójne kropki (64 wystąpienia)
- "/" : "który odmawia jedzenia**..**"
- /products/kosmetyczka: "każdej przestrzeni**..**"
- Produkty FUREVER: "Suplementacja zwierzaka potrafi być trudna**...**"

---

## 3. BŁĘDY GRAMATYCZNE (3 wystąpienia)

| Strona | Błąd | Kontekst |
|--------|------|----------|
| /pages/kazeina | "to to" | "Czy kazeina i laktoza **to to** samo?" |
| /collections/zdrowe-dziecko | "to to" | "Najbardziej wartościowe colostrum **to to**, które..." |
| /blogs/poradnik/celiakia-co-to-jest | "I i" | "chorych na cukrzycę typu **I i** niedoczynność..." |

---

## 4. GLOBALNY BŁĄD - NAGŁÓWEK STRONY

**Problem wykryty na WSZYSTKICH stronach:**

Podwójna spacja w banerze informacyjnym:
```
"Darmowa dostawa od 300 zł. Darmowa dostawa  od 300 zł."
                                           ^^
                                    (podwójna spacja)
```

**Lokalizacja:** Theme → Customize → Header/Announcement bar

---

## STATYSTYKI PO TYPIE STRONY

| Typ strony | Przeskanowano | Z błędami | % z błędami |
|------------|---------------|-----------|-------------|
| Strony informacyjne | 47 | 38 | 81% |
| Produkty | 63 | 63 | 100% |
| Kolekcje | 41 | 41 | 100% |
| Blog | 28 | 28 | 100% |
| **RAZEM** | **179** | **170** | **95%** |

---

## PRIORYTETYZACJA NAPRAW

### 🔴 Priorytet 1 (NATYCHMIAST) - Wpływ na wizerunek marki
1. ✅ Literówka "GENACITV" → "GENACTIV" w 15 produktach FUREVER
2. ✅ Literówka "prawidziwe" → "prawdziwe" (2 strony)
3. ✅ Literówka "Jeydnym" → "Jedynym" (1 strona)
4. ✅ Nazwa produktu "MASKA Z COLOSTRUM GENACITV" → "GENACTIV"

### 🟡 Priorytet 2 (W CIĄGU TYGODNIA) - Profesjonalizm
5. Podwójna spacja w nagłówku (globalny fix)
6. Podwójne spacje w treściach (196 wystąpień)
7. Spacja przed kropką (80 wystąpień)
8. Spacja przed przecinkiem (137 wystąpień)

### 🟢 Priorytet 3 (PRZY OKAZJI) - Drobne poprawki
9. Podwójne kropki ".." (64 wystąpienia)
10. Brak spacji po średniku (55 wystąpień) - częściowo celowe w bibliografii

---

## GDZIE WPROWADZIĆ ZMIANY

| Typ błędu | Lokalizacja w Shopify |
|-----------|----------------------|
| Podwójna spacja w nagłówku | Theme → Customize → Header |
| Literówki w produktach | Products → [nazwa] → Edit |
| Błędy w opisach stron | Online Store → Pages → [nazwa] |
| Błędy w blogach | Online Store → Blog posts → [nazwa] |
| Błędy w kolekcjach | Products → Collections → [nazwa] |

---

## UWAGI TECHNICZNE

1. **Produkty FUREVER** - wszystkie mają literówkę "GENACITV" w opisie składu
2. **Strona /pages/regulaminy** - zawiera najwięcej błędów (78), głównie interpunkcyjnych
3. **Cytowania naukowe** - niektóre błędy interpunkcyjne mogą być celowe
4. **False positives** - pominięto wyrazy typu "odpornościowego", "immunologicznego"
5. **Automatyczne skanowanie** - zalecana ręczna weryfikacja przed wdrożeniem

---

## PODSUMOWANIE WYKONAWCZE

| Metryka | Wartość |
|---------|---------|
| Przeskanowane strony | 179 |
| Strony z błędami | 170 (95%) |
| **Łączna liczba błędów** | **555** |
| Błędy krytyczne (literówki) | 20 |
| Błędy średnie (interpunkcja) | 532 |
| Błędy gramatyczne | 3 |

**Rekomendacja:** Rozpocząć od naprawy 20 literówek ortograficznych, które mają największy wpływ na wizerunek marki. Następnie zająć się podwójną spacją w nagłówku (dotyczy wszystkich stron).

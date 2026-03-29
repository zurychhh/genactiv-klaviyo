# FAQ genactiv.pl - Analiza treści i propozycje poprawek

**Data:** 2025-01-23
**Źródło:** Schema JSON-LD widoczne dla Google na /pages/faq

---

## WPŁYW NA SEO

### Dlaczego to jest ważne?

FAQPage Schema to strukturalne dane, które Google wykorzystuje do:
- Wyświetlania **rich snippets** (rozwijane pytania w wynikach wyszukiwania)
- Oceny **jakości i wiarygodności** strony
- **Indeksowania** treści FAQ

### Problemy wykryte na stronie /pages/faq

| Problem | Wpływ na SEO |
|---------|--------------|
| **3 testowe wpisy FAQ** ("Test", "test", "test") | Google może wyświetlić "Test → odpowiedz" jako rich snippet w wynikach wyszukiwania. Obniża jakość Schema i sygnalizuje niską jakość treści. |
| **2 literówki w odpowiedziach** ("prawidziwe", "Jeydnym") | Błędy ortograficzne negatywnie wpływają na postrzeganie profesjonalizmu marki i mogą obniżać zaufanie użytkowników. |
| **4 duplikaty Schema** | Strona generuje 4 osobne FAQPage Schema zamiast jednego. Google to ogarnia, ale nie jest to optymalne. |

### Rekomendacja

**Priorytet WYSOKI:** Usunięcie testowych wpisów FAQ
- Google indeksuje obecnie 15 pytań zamiast 12 wartościowych
- Testowe wpisy mogą pojawić się w wynikach wyszukiwania jako rich snippets
- Obniża ogólną ocenę jakości strony przez algorytm Google

**Priorytet ŚREDNI:** Poprawienie literówek
- Błędy ortograficzne wpływają na profesjonalizm marki
- Mogą obniżać zaufanie użytkowników do treści

---

## PODSUMOWANIE

| Kategoria | Ilość |
|-----------|-------|
| Pytań ogółem | 15 |
| Pytań poprawnych | 10 |
| Pytań z błędami | 2 |
| Pytań TESTOWYCH (do usunięcia) | 3 |

---

## TABELA TREŚCI FAQ

### ✅ SEKCJA 1: O Colostrum (4 pytania - OK)

| # | Pytanie | Odpowiedź (skrót) | Status |
|---|---------|-------------------|--------|
| 1 | W jakim czasie od rozpoczęcia laktacji powinno być pozyskane colostrum, aby zachowało swoje wyjątkowe właściwości? | Colostrum wytwarzane jest w gruczołach mlecznych jedynie przez kilka pierwszych godzin po rozpoczęciu laktacji... Pozyskujemy colostrum bovinum najwyższej jakości wyłącznie w ciągu 1-2 godzin od rozpoczęcia laktacji. | ✅ OK |
| 2 | Czy colostrum firmy Genactiv zostało poddane przetwarzaniu? | Colostrum Genactiv jest czyste, nieprzetworzone, bez dodatków i w 100% wierne naturze. Jednym słowem prawdziwe. | ✅ OK |
| 3 | W jaki sposób przebiega proces suszenia colostrum? | Stosujemy metodę suszenia colostrum w niskich temperaturach, wykorzystując procesy zamrażania i liofilizacji. Dzięki temu nasze colostrum zachowuje pełną wartość produktu świeżego. | ✅ OK |
| 4 | Czy pobieranie siary lub mleka nie działa na szkodę cieląt? | Ilość colostrum wytwarzana przez krowę jest zazwyczaj większa niż cielę potrzebuje. W przypadku pozyskiwania siary wykorzystujemy jedynie jej nadwyżkę, której cielę nie jest w stanie wypić. | ✅ OK |

---

### ⚠️ SEKCJA 2: O mleku klaczy (3 pytania - 1 błąd)

| # | Pytanie | Odpowiedź (skrót) | Status |
|---|---------|-------------------|--------|
| 5 | Czy mleko klaczy firmy Genactiv zostało poddane przetwarzaniu? | Mleko klaczy Genactiv jest czyste, nieprzetworzone i w 100 % wierne naturze. Jednym słowem **prawidziwe**. | ⚠️ BŁĄD |
| 6 | W jaki sposób przebiega proces suszenia mleka klaczy? | Stosujemy metodę suszenia mleka kobylego w niskich temperaturach, wykorzystując procesy zamrażania i liofilizacji. Dzięki temu nasze mleko klaczy zachowuje pełną wartość produktu świeżego. | ✅ OK |
| 7 | Czy pobieranie mleka nie działa na szkodę źrebiąt? | Pozyskujemy mleko dopiero od drugiego miesiąca życia źrebięcia. W tym czasie źrebię pobiera już także pasze stałe i nie potrzebuje dużej ilości mleka matki. | ✅ OK |

**BŁĄD #5:** "prawidziwe" → **"prawdziwe"**

---

### ⚠️ SEKCJA 3: Dermokosmetyki Genactiv (5 pytań - 1 błąd)

| # | Pytanie | Odpowiedź (skrót) | Status |
|---|---------|-------------------|--------|
| 8 | Czy istnieją jakiekolwiek przeciwwskazania do stosowania dermokosmetyków z Colostrum i Mlekiem Klaczy? | Jedynym przeciwwskazaniem do stosowania dermokosmetyków jest alergia na jakikolwiek składnik produktu. Dokładne składy produktów znajdują się na opakowaniach oraz na kartach produktów na naszej stronie www. | ✅ OK |
| 9 | Czy osoby uczulone na białka mleka krowiego mogą stosować kosmetyki z Colostrum? | Nie ma jednoznacznej odpowiedzi na to pytanie. Alergia na białka mleka krowiego to złożona kwestia... Osoby uczulone na białka mleka krowiego, przed zastosowaniem kosmetyku z Colostrum powinny wykonać test na niewidocznym kawałku skóry (np. za uchem) i obserwować zmiany w tym miejscu. (?) | ✅ OK (ale jest "(?)" na końcu) |
| 10 | Czy kobiety w ciąży mogą stosować dermokosmetyki Genactiv? | Kobiety w ciąży i karmiące piersią mogą bezpiecznie stosować dermokosmetyki Genactiv. **Jeydnym** przeciwwskazaniem do stosowania jest alergia na jakikolwiek składnik produktu. | ⚠️ BŁĄD |
| 11 | W jaki sposób można stosować Maskę z Colostrum? | CODZIENNA PIELĘGNACJA - nanieść maskę na umyte włosy... KOMPRES DLA WŁOSÓW I SKÓRY GŁOWY - nałożyć maskę na wilgotne włosy... Stosować raz w tygodniu. Maska tylko do użytku zewnętrznego. | ✅ OK |
| 12 | Czy korzystanie z dermokosmetyków Genactiv jest bezpieczne? | Dbamy o to, by oferowane przez nas dermokosmetyki były odpowiednie nawet dla najwrażliwszych osób... Nasze produkty opierają się głównie na dwóch składnikach aktywnych: Colostrum i Mleku klaczy. | ✅ OK |

**BŁĄD #10:** "Jeydnym" → **"Jedynym"**

---

### ❌ SEKCJA 4: Test (3 pytania - DO USUNIĘCIA)

| # | Pytanie | Odpowiedź | Status |
|---|---------|-----------|--------|
| 13 | Test | odpowiedz | ❌ USUNĄĆ |
| 14 | test | test | ❌ USUNĄĆ |
| 15 | test | dasdasd | ❌ USUNĄĆ |

**AKCJA:** Usunąć całą sekcję "Test" z FAQ w Shopify Admin

---

## WYMAGANE POPRAWKI

### 1. Literówki do poprawienia (w Shopify Admin → Pages → FAQ)

| Lokalizacja | Błąd | Poprawka |
|-------------|------|----------|
| Sekcja "O mleku klaczy", pytanie 1 | "prawidziwe" | **"prawdziwe"** |
| Sekcja "Dermokosmetyki", pytanie 3 | "Jeydnym" | **"Jedynym"** |

### 2. Sekcja do usunięcia

| Sekcja | Akcja |
|--------|-------|
| "Test" (3 pytania testowe) | **USUNĄĆ CAŁĄ SEKCJĘ** |

---

## PEŁNE TREŚCI ODPOWIEDZI (do weryfikacji)

### FAQ #5 - Pełna odpowiedź (z błędem)
**Pytanie:** Czy mleko klaczy firmy Genactiv zostało poddane przetwarzaniu?

**Obecna odpowiedź:**
> Mleko klaczy, które zostało zmienione poprzez usunięcie któregokolwiek ze składników, wbrew opisom na opakowaniu produktów, nie jest już naturalnym mlekiem kobylim. Jego działania nie można utożsamiać z działaniem mleka o pełnym składzie, a więc takim, jakie w naturalnych warunkach daje najlepsze efekty. Mleko klaczy Genactiv jest czyste, nieprzetworzone i w 100 % wierne naturze. Jednym słowem **prawidziwe**.

**Poprawiona odpowiedź:**
> Mleko klaczy, które zostało zmienione poprzez usunięcie któregokolwiek ze składników, wbrew opisom na opakowaniu produktów, nie jest już naturalnym mlekiem kobylim. Jego działania nie można utożsamiać z działaniem mleka o pełnym składzie, a więc takim, jakie w naturalnych warunkach daje najlepsze efekty. Mleko klaczy Genactiv jest czyste, nieprzetworzone i w 100 % wierne naturze. Jednym słowem **prawdziwe**.

---

### FAQ #10 - Pełna odpowiedź (z błędem)
**Pytanie:** Czy kobiety w ciąży mogą stosować dermokosmetyki Genactiv?

**Obecna odpowiedź:**
> Kobiety w ciąży i karmiące piersią mogą bezpiecznie stosować dermokosmetyki Genactiv. **Jeydnym** przeciwwskazaniem do stosowania jest alergia na jakikolwiek składnik produktu.

**Poprawiona odpowiedź:**
> Kobiety w ciąży i karmiące piersią mogą bezpiecznie stosować dermokosmetyki Genactiv. **Jedynym** przeciwwskazaniem do stosowania jest alergia na jakikolwiek składnik produktu.

---

## DODATKOWE UWAGI

1. **Znak zapytania w FAQ #9** - Na końcu odpowiedzi jest "(?)". Sprawdzić czy to celowe czy błąd.

2. **Formatowanie** - Niektóre odpowiedzi mają nadmiarowe spacje przed kropkami (np. "produktu .Proces"). Można poprawić przy okazji.

3. **Duplikaty Schema** - Strona generuje 4 osobne FAQPage Schema (po jednym dla każdej sekcji + jeden zbiorczy). Google to ogarnia, ale można rozważyć optymalizację w przyszłości.

---

**Kto wykonuje poprawki:** Agencja / Admin Shopify
**Gdzie:** Shopify Admin → Online Store → Pages → FAQ → Edit

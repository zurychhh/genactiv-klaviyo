# Model Subskrypcyjny GenActiv.pl --- Finalna Rekomendacja
## Synteza trzech audytow eksperckich z rozstrzygnieciami konfliktow

**Data:** 2026-07-17
**Autor:** Senior Strategy Consultant (synteza automatyczna)
**Raporty zrodlowe:**
1. Audyt techniczny Shopify (`subscription-technical-audit-2026-07-17.md`)
2. Audyt Klaviyo (`klaviyo-subscription-audit-2026-07-17.md`)
3. Business case --- analiza sprzedazy (`subscription-business-case-genactiv.md`)

**Odbiorca:** Zespol decyzyjny GenActiv.pl
**Status:** Dokument wykonawczy --- gotowy do realizacji

---

## 1. STRESZCZENIE WYKONAWCZE

### Decyzja: SILNE TAK --- uruchomienie subskrypcji we wrzesniu 2026

GenActiv.pl posiada wyjatkowo silne fundamenty do wdrozenia modelu subskrypcyjnego. Trzy niezalezne audyty --- techniczny, marketingowy i biznesowy --- potwierdzaja zgodnosc: **87,8% przychodow pochodzi z suplementow konsumpcyjnych** o regularnym cyklu zuzycia, wskaznik powtarzalnosci zakupow wynosi 55%, a 248 klientow VIP generuje srednia wartosc zyciowa 5 421 PLN.

**Kluczowy bloker, ktory determinuje cala strategie:** Przelewy24 i BLIK NIE obsluguja platnosci cyklicznych na Shopify. Subskrypcje wymagaja karty platniczej (Visa/Mastercard/Apple Pay/Google Pay), co ogranicza dostepny rynek do ok. 25--30% polskich kupujacych online. Ten fakt, potwierdzony przez wszystkich trzech ekspertow, wymaga specyficznego podejscia --- prepaid jako kluczowy obieg alternatywny.

### Rozstrzygniecia kluczowych konfliktow

| Konflikt | Rozstrzygniecie |
|----------|----------------|
| Platforma | **Appstle** (start) z migracją do **Loop** przy MRR > 30K PLN --- nie Recharge |
| Typ modelu | **Subscribe & Save** (automatyczna dostawa co X dni z rabatem) + Prepaid kwartalny |
| Projekcja przychodow R1 | **162K PLN netto** (bazowy scenariusz po korekcie o bloker platnosci) |
| Waga blokera platnosci | **Powazny, ale nie krytyczny** --- mitigowany prepaidem i Apple Pay |
| Struktura rabatow | **10% ongoing + darmowa dostawa** (bez 15% na pierwsza zamowienie) |
| Timeline | **Wrzesien 2026** start (termin z roadmapy H2 2026), 168h effort, 5 miesiecy do pelnej automatyzacji |

### Metryki docelowe (grudzien 2026)

| KPI | Cel |
|-----|-----|
| Aktywni subskrybenci | 180--250 |
| Miesieczny przychod subskrypcyjny | 32--45K PLN |
| Udzial subskrypcji w przychodzie | 8--12% |
| Miesieczny churn | < 7% |
| Odzyskanie nieudanych platnosci | > 50% |

---

## 2. MODEL BIZNESOWY --- SZCZEGOLY

### 2.1 Jaki typ modelu subskrypcyjnego?

Istnieja trzy glowne typy subskrypcji w e-commerce:

| Typ | Opis | Przyklad | Dopasowanie do GenActiv |
|-----|------|---------|------------------------|
| **Subscribe & Save (Replenishment)** | Klient zamawia ten sam produkt cyklicznie, dostaje rabat za regularnosc | Dollar Shave Club, ARMRA Colostrum | **NAJLEPSZY** --- suplementy sa konsumowane regularnie, cykl 30/60 dni jest naturalny |
| Curation Box | Firma wybiera produkty-niespodzianki co miesiac | Birchbox, HelloFresh | NIE --- GenActiv ma 15-20 SKU, nie setki; klient wie co chce |
| Membership / Access | Klient placi za dostep do rabatow, tresci lub uslug | Amazon Prime, Costco | PRZYSZLOSC --- mozliwy jako warstwa nad Subscribe & Save (np. "GenActiv Club") |

**Rekomendowany model: Subscribe & Save (Subskrybuj i Oszczedz)** --- klient wybiera konkretny produkt, ustawia czestotliwosc dostaw, i otrzymuje go automatycznie co X dni z rabatem.

### 2.2 Jak to wyglada z perspektywy klienta?

**KROK 1: Wybor na karcie produktu (PDP)**

Klient wchodzi na strone np. FIBERBIOM - Blonnik + Colostrum (189 PLN). Widzi dwie opcje:

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│  FIBERBIOM - Blonnik + Colostrum                        │
│  30 saszetek                                             │
│                                                          │
│  ○ Kup jednorazowo                         189 PLN      │
│                                                          │
│  ● Subskrybuj i Oszczedz                   170 PLN      │
│    ✓ Oszczedzasz 10% na kazdej dostawie                 │
│    ✓ Darmowa dostawa                                     │
│    ✓ Zmien, pauzuj lub anuluj w dowolnym momencie       │
│                                                          │
│    Ile saszetek dziennie bierzesz?                       │
│    ● 2 saszetki (rano + wieczor)  → co 14 dni           │
│    ○ 1 saszetka                   → co 28 dni           │
│    ○ Inna ilosc: [___]            → obliczone           │
│                                                          │
│    ★ Wiekszosc klientow bierze 2 dziennie               │
│                                                          │
│    ℹ️ Platnosc karta lub Apple Pay                      │
│                                                          │
│  Lub: Plan kwartalny 435 PLN za 3 dostawy (-19%)       │
│       Mozesz zaplacic BLIK lub Przelewy24               │
│                                                          │
│  [DODAJ DO KOSZYKA]                                     │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

**Dlaczego pytamy o dawkowanie zamiast dawac selector "co X dni"?**

Klient nie wie, co 14 czy co 28 dni --- ale wie, ile saszetek bierze dziennie. Pytanie o dawkowanie:
1. Automatycznie oblicza trafny interwal (eliminuje zgadywanie)
2. Pozycjonuje GenActiv jako doradce zdrowotnego, nie sprzedawce
3. Daje dane do personalizacji (Klaviyo: dawkowanie -> segment -> tresci)

Dane z Shopify potwierdzaja: **77% klientow FIBERBIOM zuzywa paczke w <21 dni** (mediana 16 dni/30 saszetek). Domyslna odpowiedz "2 saszetki" odzwierciedla to zachowanie.

**KROK 2: Checkout**

Klient placi **karta platnicza** (Visa, Mastercard, Apple Pay, Google Pay). System tokenizuje karte --- zapisuje bezpieczny token, nie dane karty. Przy prepaid kwartalnym --- moze zaplacic BLIK lub Przelewy24, bo to jednorazowa platnosc za 3 dostawy.

**KROK 3: Pierwsza dostawa**

Normalne zamowienie Shopify. Klient dostaje paczke + email powitalny z instrukcja stosowania.

**KROK 4: Automatyczne odnowienie**

Po 30 dniach (lub wybranym interwale) system automatycznie:
1. Obciaza zapisana karte kwota 170 PLN
2. Tworzy nowe zamowienie w Shopify
3. Wysyla email "Twoja przesylka juz w drodze"

Klient NIE musi nic robic --- produkt przychodzi regularnie.

**KROK 5: Zarzadzanie subskrypcja (portal klienta)**

Klient moze w dowolnym momencie przez portal:
- **Pominac** jedna dostowe ("w tym miesiacu nie potrzebuje")
- **Przesunac** date nastepnej dostawy
- **Zmienic czestotliwosc** (np. z 30 na 45 dni bo gromadzi sie zapas)
- **Zmienic produkt** (np. z Fiberbiom original na Fiberbiom z Ananasem)
- **Dodac produkt** do subskrypcji (np. dolozyc Colostrum kapsulki)
- **Zapauzowac** (tymczasowe wstrzymanie bez anulowania)
- **Anulowac** (rezygnacja --- system zada pytanie "dlaczego?" i zaproponuje alternatywe)

### 2.3 Jak to wyglada z perspektywy firmy?

**PRZYCHOD:**

```
Klient jednorazowy:          Kupuje 1-2x w roku, srednio 1.8 zamowien
                             Roczny przychod: 1.8 × 245 = 441 PLN

Subskrybent (30 dni):        Kupuje automatycznie co 30 dni = 12x w roku
                             Roczny przychod: 12 × 170 = 2 040 PLN
                             (mimo 10% rabatu: 4.6x wiecej przychodu niz jednorazowy)

Subskrybent (60 dni):        Kupuje co 60 dni = 6x w roku
                             Roczny przychod: 6 × 170 = 1 020 PLN
                             (2.3x wiecej niz jednorazowy)
```

**MARZA:**

```
Cena suplementu (np. Fiberbiom):        189 PLN (jednorazowa) / 170 PLN (sub)
Szacowana marza brutto (~55%):          104 PLN / 93,5 PLN
Koszt dostawy (darmowa w sub):          -15 PLN
Prowizja platformy Appstle:             0 PLN (zero prowizji!)
Marza netto na zamowieniu sub:          ~78,5 PLN

Na 12 zamowien/rok:                     ~942 PLN marzy z jednego subskrybenta
vs jednorazowy (1.8 zam/rok):           ~187 PLN marzy

Subskrybent generuje 5x wieksza marze roczna niz jednorazowy klient.
```

**KOSZTY PROGRAMU:**

```
Platforma Appstle:            $0-30/mies (ok. 0-120 PLN)
Darmowa dostawa na sub:       ~15 PLN/zamowienie × liczba zamowien sub
Rabat 10%:                    ~19 PLN/zamowienie (utracony przychod)
Koszt Klaviyo flows:          Wliczony w istniejacy plan Klaviyo
Czas pracy CC (setup):        168h jednorazowo (5 miesiecy)
Czas pracy CC (ongoing):      ~4h/tydzien (monitoring, optymalizacja)
```

### 2.4 Warianty modelu w ofercie GenActiv

Model laczy trzy warianty zakupowe:

```
WARIANT A: SUBSCRIBE & SAVE (standard)
═══════════════════════════════════════
  Co to jest:  Automatyczna dostawa w interwale dopasowanym do dawkowania
  Interwal:    Obliczony z dawki (nie arbitralnie 30/60 dni!)
  Rabat:       -10% na kazda dostowe
  Dostawa:     Darmowa (zawsze)
  Platnosc:    Karta platnicza, Apple Pay, Google Pay
  Anulowanie:  W dowolnym momencie, jednym kliknieciem
  Dla kogo:    Klienci regularnie uzywajacy suplementow

  INTERWALY OPARTE NA DANYCH TRANSAKCYJNYCH SHOPIFY (3 026 zamowien):
  ┌─────────────────────────────────┬───────────┬───────────┬──────────┐
  │ Produkt                         │ Teoria    │ Dane      │ Default  │
  │                                 │(opakow.)  │(mediana)  │          │
  ├─────────────────────────────────┼───────────┼───────────┼──────────┤
  │ FIBERBIOM 30 saszetek           │ 30 dni    │ 16 dni    │ 14 dni   │
  │ FIBERBIOM Dwupak (60 saszetek)  │ 60 dni    │ ~32 dni   │ 28 dni   │
  │ Colostrum 60 kapsulek           │ 30 dni    │ 32 dni    │ 30 dni   │
  │ Colostrum 120 kapsulek          │ 60 dni    │ 35-41 dni │ 45 dni   │
  │ Colostrum proszek               │ 30 dni    │ 31 dni    │ 30 dni   │
  │ Colostrum zawiesina             │ 30 dni    │ 28 dni    │ 30 dni   │
  └─────────────────────────────────┴───────────┴───────────┴──────────┘
  Zrodlo: reports/reorder-interval-analysis-2026-07-17.md

  KLUCZOWE ODKRYCIE: FIBERBIOM --- 77% klientow zuzywa paczke
  w <21 dni (mediana 16 dni). Klienci biora 2 saszetki/dzien,
  nie 1 jak zakladano z opakowania. Default 30 dni prowadziłby
  do gromadzenia zapasu → rezygnacja z subskrypcji.

WARIANT B: PREPAID KWARTALNY
═══════════════════════════════════════
  Co to jest:  Jedna platnosc za 3 dostawy (w rytmie sub)
  Rabat:       -15% od ceny 3 sztuk
  Dostawa:     Darmowa (zawsze)
  Platnosc:    DOWOLNA (BLIK, Przelewy24, karta)
  Anulowanie:  Brak --- oplacone z gory, 3 dostawy gwarantowane
  Dla kogo:    Klienci preferujacy BLIK, chcacy wieksza oszczednosc

  Przyklad: FIBERBIOM 3-miesieczny (6 paczek, co 14 dni)
    6 × 189 PLN = 1 134 PLN (jednorazowe)
    Prepaid:     963 PLN (-15% / 171 PLN oszczednosci)
    Dostaje:     6 paczek, jedna co 14 dni przez 84 dni

  Przyklad: COLOSTRUM 120 kaps 3-miesieczny (2 opakowania, co 45 dni)
    2 × 189 PLN = 378 PLN (jednorazowe)
    Prepaid:     321 PLN (-15% / 57 PLN oszczednosci)
    Dostaje:     2 paczki, jedna co 45 dni przez 90 dni

WARIANT C: BUNDLE (zestaw subskrypcyjny)
═══════════════════════════════════════
  Co to jest:  2-3 produkty w jednym zamowieniu cyklicznym
  Rabat:       -12% (2 produkty) / -15% (3+ produkty)
  Dostawa:     Darmowa (AOV > 300 PLN = powyzej progu)
  Platnosc:    Karta, Apple Pay
  Anulowanie:  W dowolnym momencie
  Dla kogo:    Klienci uzywajacy wielu produktow GenActiv

  Przyklad: "Odpornosc + Blonnik"
    COLOSTRUM 120 kaps (189) + FIBERBIOM (189) = 378 PLN
    Bundle sub:  321 PLN (-15%)
    Interwal:    Wyznaczony przez produkt o krotszym cyklu (14 dni Fiberbiom)
    Dodatkowy COLOSTRUM: co 3. dostowe (co 42 dni ≈ 45-dniowy cykl)
```

### 2.5 System Inteligencji Interwalowej (kluczowy element programu)

**Dlaczego to jest tak wazne:** Cala obietnica subskrypcji brzmi "produkt przychodzi gdy go potrzebujesz". Jesli interwal jest zly, obietnica jest zlamana od pierwszej dostawy:
- Za krotki interwal → produkt sie pietrzy → "placę za cos czego nie potrzebuje" → rezygnacja
- Za dlugi interwal → klient zostaje bez produktu → kupuje w aptece → "subskrypcja jest bezuzyteczna" → rezygnacja

Dlatego program GenActiv wdraza trzywarstwowy system dopasowania interwalu:

```
WARSTWA 1: ANKIETA DAWKOWANIA (przy zakupie sub)
=================================================
  Cel: Trafny interwal od 1. dostawy
  Mechanizm: Pytanie na PDP "Ile saszetek/kapsulek dziennie bierzesz?"
  Kalkulacja: ilosc_w_opakowaniu / dawka_dzienna = interwal_dni
  Przyklad: Fiberbiom 30 saszetek / 2 dziennie = 15 dni → default 14 dni
  Fallback: Jesli klient nie odpowie, domyslny interwal z danych Shopify (mediana)

WARSTWA 2: ADAPTACYJNY FLOW PO 2. DOSTAWIE (Klaviyo)
=================================================
  Cel: Korekta interwalu na bazie doswiadczenia klienta
  Trigger: 2 dni po dostarczeniu 2. zamowienia sub
  Tresc emaila:

    "Cześć {{ first_name }},
    Właśnie wysłaliśmy Twoją drugą dostawę FIBERBIOM.
    Krótkie pytanie — jak trafiamy z terminem?

    [Idealnie — produkt kończy się właśnie teraz]
        → Bez zmian. System potwierdza: "Świetnie, kontynuujemy co {{ interval }} dni."

    [Za wcześnie — mam jeszcze zapas z poprzedniej dostawy]
        → Automatycznie wydluza interwal o 7 dni.
        → Email: "Przesunęliśmy Twoją następną dostawę na {{ new_date }}."

    [Za późno — skończył mi się produkt kilka dni temu]
        → Automatycznie skraca interwal o 5 dni.
        → Email: "Przyspieszyliśmy dostawy, następna {{ new_date }}."
    "

  Techniczny mechanizm: Click tracking → Zapier/webhook → Appstle API
  (zmiana interwalu w subscription contract)

WARSTWA 3: PROAKTYWNE MONITOROWANIE (ongoing)
=================================================
  Cel: Wczesne wykrywanie blednego interwalu ZANIM klient zrezygnuje
  Sygnaly:
    - Klient klika "Skip" 2x pod rzad → interwal jest za krotki
      → Akcja: Automatyczny email "Widzimy ze pomijasz dostawy. Chcesz
        zmienić częstotliwość na co {{ interval + 7 }} dni?"
    - Klient kupuje ten sam produkt jednorazowo MIEDZY dostawami sub
      → interwal jest za dlugi
      → Akcja: Klaviyo flow "Widzimy ze dokupujesz {{ product }} — chcesz
        przyspieszyć subskrypcje?"
    - Brak otwarcia emaila "Twoja przesylka w drodze" 3x z rzędu
      → klient moze juz nie uzywac produktu
      → Akcja: Health check flow (ankieta satysfakcji)
```

**Wplyw na retencje (estymacja):**

| Warstwa | Bez systemu | Z systemem | Roznica |
|---------|-----------|-----------|---------|
| Trafnosc interwalu w M1 | ~40% (zgadywanie) | ~75% (ankieta) | +35pp |
| Trafnosc interwalu w M3 | ~50% (czesc klientow sama zmienia) | ~85% (adaptacja po 2. dostawie) | +35pp |
| Churn z powodu zlego interwalu | ~25% wszystkich rezygnacji | ~8% | -17pp |
| Szacowany wplyw na miesieczny churn | 8% → 8% (bez zmian) | 8% → 5.5% | -2.5pp |

Ta roznica 2.5pp churnu kumuluje sie: w scenariuszu bazowym na M12 to roznica miedzy 220 a 280 aktywnych subskrybentow (+27%).

### 2.6 Ekonomia jednostkowa (unit economics) --- podsumowanie

```
                          JEDNORAZOWY     SUBSKRYBENT     SUBSKRYBENT
                          KUPUJACY        (1 produkt)     (bundle 2 prod.)
─────────────────────────────────────────────────────────────────────────
AOV                       245 PLN         170 PLN         321 PLN
Zamowien/rok              1.8             10-12           10-12
Roczny przychod/klienta   441 PLN         2 040 PLN       3 852 PLN
Marza brutto (55%)        243 PLN         1 122 PLN       2 119 PLN
Koszt darmowej dostawy    0 PLN           -180 PLN        -180 PLN
Marza netto/klienta/rok   243 PLN         942 PLN         1 939 PLN
─────────────────────────────────────────────────────────────────────────
Wskaznik wartosci         1x              3.9x            8.0x
LTV 3-letnia (marza)      ~350 PLN        ~2 800 PLN      ~5 800 PLN
```

**Kluczowy wniosek:** Nawet z rabatem 10% i darmowa dostawa, subskrybent generuje 4-8x wieksza wartosc niz klient jednorazowy, bo kupuje 6-10x czesciej.

### 2.6 Dlaczego wrzesien 2026? --- zrodlo terminow

Terminy w tym raporcie wynikaja z trzech zrodel:

| Termin | Zrodlo | Uzasadnienie |
|--------|--------|-------------|
| Wrzesien 2026 (launch) | Roadmapa H2 2026 (CLAUDE.md: "Sub launch (Aug)") + 4 tygodnie przygotowania (sierpien) | Sierpien to setup, wrzesien to soft launch --- zgodne z planem strategicznym |
| Fazy miesieczne (M1-M12) | Estymacja ekspertow Shopify (81-93h) i Klaviyo (5 miesiecy phased) | Hybrid: MVP w 6 tygodni, pelna automatyzacja w 5 miesiecy |
| Decision gates (M3, M6, M12) | Standardy branzowe DTC subscription + benchmarki churn suplementow | 3 miesiace to czas na zebranie statystycznie istotnych danych |
| BF kampania (listopad) | Roadmapa H2 2026: "Pre-BF +2K subs (Oct)" | Black Friday to naturalny moment konwersji jednorazowych na subskrybentow |
| Loop migracja (M6+) | Gate MRR >30K PLN | Appstle jest wystarczajace do ~150 sub; powyzej Loop daje retention tools warte dodatkowego kosztu |

**WAZNE:** Te terminy sa rekomendacja, nie zobowiazaniem. Faktyczny start zalezy od:
1. Decyzji go/no-go zespolu GenActiv
2. Dostepnosci deweloperskiej (8h na widget GEN-6)
3. Weryfikacji czy Shopify Payments (karty) jest aktywne obok Przelewy24

---

## 3. DECYZJA PLATFORMOWA (dawna sekcja 2)

### 2.1 Analiza konfliktu

Trzech ekspertow zaproponowalo trzy rozne rozwiazania:

| Ekspert | Rekomendacja | Cena (R1, est.) | Uzasadnienie |
|---------|-------------|-----------------|-------------|
| Shopify (tech) | **Appstle** ($30/mies) | ~1 440 PLN/rok | Zero prowizji, darmowy plan na start, najlepsza cena |
| Klaviyo (mktg) | **Recharge** ($99/mies + 1,49%) | ~21 000 PLN/rok | Najglebsza integracja z Klaviyo, 9+ eventow natywnych |
| Business | **Appstle -> Loop** | ~4 300 -> 14 000 PLN/rok | Appstle na walidacje, Loop na skale |

### 2.2 Argumenty za kazdym rozwiazaniem

**Za Recharge (ekspert Klaviyo):**
- Najlepsza natywna integracja z Klaviyo: 9+ metrk subskrypcyjnych, rc_* profile properties, Quick Actions URL
- Recharge kupil Skio za $105M --- konsolidacja rynku, pozycja lidera
- 20 000+ merchantow, battle-tested infrastruktura
- AI-powered dunning z 88% recovery rate

**Za Appstle (ekspert Shopify):**
- Zero prowizji transakcyjnych --- jedyny koszt to flat fee
- Darmowy plan do $500/mies sub revenue (wystarczajacy na walidacje)
- 5.0/5.0 na App Store (7 716 recenzji --- najwyzsza ocena)
- Najmniejszy bundle JS (~38KB) --- minimalny wplyw na PageSpeed
- Build-a-box, prepaid, cancel flows --- kompletny feature set

**Za Loop (ekspert biznesowy):**
- Najlepsze narzedzia retencyjne (gamified journeys, inteligentne cancel flows)
- Nizsze prowizje niz Recharge (1,0% vs 1,49%)
- Natywna integracja z Klaviyo (subscription events)
- CSM na planie Pro

### 2.3 Rozstrzygniecie: Appstle (start) -> Loop (skala)

**DECYZJA: Appstle Subscriptions na start. Migracja do Loop przy MRR > 30K PLN.**

**Uzasadnienie:**

1. **Koszt vs wartosc przy zerowej bazie subskrybentow.** Przy 0 subskrybentach, Recharge kosztuje $99/mies za sam dostep. Appstle = $0 do $500 MRR, potem $30/mies. Roznica w R1: **~19 500 PLN oszczednosci**. Przy niepewnosci adopcji na polskim rynku (bloker platnosci), minimalizacja kosztow stalych jest kluczowa.

2. **Integracja Klaviyo: "wystarczajaco dobra" vs "najlepsza".** Appstle obsluguje Klaviyo przez Zapier lub natywne webhooks. To wymaga wiecej setupu (2--3h ekstra), ale finalny efekt jest taki sam: eventy subskrypcyjne trafiaja do Klaviyo. Recharge'owe rc_* properties sa wygodne, ale Appstle tworzy rownowazne custom properties. Roznica: 3h setupu vs 19 500 PLN/rok.

3. **Dlaczego nie Recharge od razu.** Ekspert Klaviyo prawidlowo identyfikuje Recharge jako najglebsza integracje. Jednak:
   - Przy <200 subskrybentach nie wykorzystamy zaawansowanych funkcji Pro ($499/mies)
   - 1,49% prowizji + $0,19/zamowienie = ponad 3% przychodu sub na platforme
   - Po akwizycji Skio przyszlosc cennika Recharge jest niepewna

4. **Dlaczego Loop jako next step (a nie Recharge).** Loop oferuje:
   - Nizsza prowizje (1,0% vs 1,49%)
   - Lepsze retention tools (gamified cancel flows)
   - Porownywalna integracja z Klaviyo (natywne eventy)
   - Dedykowany CSM od planu Pro
   - Lepsza cena przy skali ($99 + 1,0% vs $99 + 1,49% + $0,19/order)

5. **Gate migracji: MRR > 30K PLN** (ok. 150+ aktywnych subskrybentow). Przy tym wolumenie:
   - Appstle = $30/mies (flat) = ok. 120 PLN/mies
   - Loop = $99 + 1,0% = ok. $99 + $75 = ok. 700 PLN/mies
   - Ale Loop daje retention tools, ktore przy 150+ sub umieja splacac roznice
   - Migracja z Appstle do Loop jest jednorazowym wysilkiem 1--2 dni (auto-migrate)

### 2.4 Kalkulacja kosztow platformy (porownanie R1)

```
                        Appstle (R1)    Recharge (R1)    Loop (R1)
Base fee:               $30/mies        $99/mies         $99/mies
Prowizja transakcyjna:  0%              1,49% + $0,19    1,0%
Koszt M1 (50 sub):      $30             $99+$13=$112     $99+$9=$108
Koszt M6 (180 sub):     $30             $99+$75=$174     $99+$37=$136
Koszt M12 (250 sub):    $30             $99+$102=$201    $99+$50=$149
Roczny koszt:           ~$360           ~$2 100          ~$1 560
W PLN:                  ~1 440          ~8 400           ~6 240
```

**Oszczednosc R1 z Appstle vs Recharge: ~7 000 PLN.**
**Oszczednosc R1 z Appstle vs Loop: ~4 800 PLN.**

---

## 4. STRATEGIA PLATNOSCI --- PODEJSCIE SPECYFICZNE DLA POLSKI

### 3.1 Skala problemu

Wszyscy trzej eksperci zgadzaja sie: BLIK i Przelewy24 nie obsluguja platnosci cyklicznych na Shopify. Rozbieznosc dotyczy wagi tego faktu:

| Ekspert | Ocena wagi | Wplyw na adopcje |
|---------|-----------|-----------------|
| Shopify (tech) | "Critical blocker" --- ogranicza do 25--30% kupujacych | -30--40% adopcji vs rynki z pelnym recurringiem |
| Klaviyo (mktg) | Wspomina, ale nie modeluje | Nie kwantyfikuje |
| Business | Akceptuje, modeluje 15--25% adopcji | Zaklada, ze klienci subskrypcyjni to inny segment |

### 3.2 Rozstrzygniecie: powazny, ale nie krytyczny

**Bloker platnosci jest powazny, ale ma trzy czynniki lagodzace specyficzne dla GenActiv:**

1. **Profil subskrybenta != profil sredni.** Subskrybent GenActiv to klient z 3+ zakupami, AOV 245 PLN, swiadoma decyzja zdrowotna. Ten segment ma istotnie wyzsze uzycie kart platniczych niz ogol populacji e-commerce. Szacujemy, ze 40--50% klientow subskrypcyjnego segmentu posiada i uzywa kart (vs 25--30% ogolu).

2. **Apple Pay/Google Pay rosna.** W Polsce adopcja Apple Pay/Google Pay wsrod 25--44 lat rosnie o ~15% rocznie. Obie metody dzialaja z subskrypcjami Shopify. Przy projections na M12, moze to dodac 5--10pp do dostepnego rynku.

3. **Prepaid rozwazuje problem.** Plany kwartalne (3 dostawy, jedna platnosc z gory) moga byc oplacone DOWOLNA metoda, wlacznie z BLIK i Przelewy24. To otwiera 100% rynku dla klientow gotowych zobowiazac sie na 3 miesiace.

### 3.3 Trzy-torowa strategia platnosci

```
TOR 1: KARTA (Visa/MC) --- STANDARD
  Cel: 60% subskrybentow
  Mechanizm: Standardowa subskrypcja recurring billing
  Doswiadczenie: Automatyczne obciazenie co 30/60 dni
  Adopcja: Klienci juz uzywajacy kart lub gotowi przejsc

TOR 2: APPLE PAY / GOOGLE PAY / SHOP PAY --- PRZYSPIESZONY
  Cel: 15% subskrybentow
  Mechanizm: Accelerated checkout + tokenizacja
  Doswiadczenie: Jeden touch/face ID co cykl (automatyczne)
  Adopcja: Mlodsi klienci (25-44), uzytkownicy iPhone/Android

TOR 3: PREPAID (BLIK/P24) --- OBIEG ALTERNATYWNY
  Cel: 25% subskrybentow
  Mechanizm: Jedna platnosc za 3 lub 6 miesiecy
  Doswiadczenie: Platnosc BLIK/P24 z gory, 3-6 dostaw automatycznych
  Adopcja: Klienci preferujacy BLIK/P24, gotowi na zobowiazanie
  Rabat: -15% (3 mies.) lub -19% (6 mies.) vs cena jednorazowa
```

### 3.4 Komunikacja na PDP (karta produktu)

Kluczowy insight z eksperta Shopify: platnosc karta musi byc jasno zakomunikowana PRZED wyborem subskrypcji, zeby nie frustrować klienta na checkoucie.

```
┌──────────────────────────────────────────────┐
│  ○ Kup jednorazowo                189 PLN    │
│  ● Subskrybuj i Oszczedz          170 PLN    │
│    Zaoszczedz 10% | Darmowa dostawa          │
│    ▼ Czestotliwosc: [Co 30 dni ▼]            │
│    ℹ️ Platnosc karta lub Apple Pay           │
│                                              │
│  Lub: Plan kwartalny (435 PLN za 3 dostawy)  │
│       Dowolna metoda platnosci               │
│       [Oszczedz 19%]                         │
│                                              │
│  [DODAJ DO KOSZYKA]                          │
└──────────────────────────────────────────────┘
```

---

## 5. SKORYGOWANE PROJEKCJE FINANSOWE

### 4.1 Dlaczego projekcje ekspertow sie roznia

| Parametr | Shopify (tech) | Business | Roznica |
|----------|---------------|----------|---------|
| Nowi sub/mies. (start) | 30 | 50 | Business 67% wyzej |
| Nowi sub/mies. (M12) | 50 | 50 | Zgodni |
| Churn miesieczny | 5--6% | 8% (kons.) / 6,5% (umiark.) | Business bardziej konserwatywny |
| Aktywni sub M12 | 180 | 334 (kons.) / 551 (umiark.) | Ogromna roznica |
| Przychod sub R1 | 200K PLN | 462K PLN (kons.) | Business 2,3x wyzej |
| Sub AOV | 180 PLN | 230 PLN | Business 28% wyzej |

**Zrodla rozbieznosci:**

1. **Seed subskrybentow (M1).** Ekspert biznesowy zaklada 50 subskrybentow w M1, technik 30. Przy ograniczeniu platnosci do kart i starcie od zera, 30 jest bardziej realistyczne. **Przyjmujemy 30.**

2. **Wzrost nowych subskrybentow.** Biznes zaklada przyrost od 35 do 50/mies. Przy blokadzie platnosci, realniejsze jest 25--40/mies. **Przyjmujemy 25 (start) -> 40 (M12).**

3. **Churn.** Ekspert Shopify zaklada 5--6% (optymistyczne dla nowego programu). Biznes 8% (kons.) --- bardziej realistyczne w pierwszych miesiącach. **Przyjmujemy 8% (M1-3) -> 6% (M7-12).**

4. **Sub AOV.** Technik zaklada 180 PLN (konserwatywne, bazowe na medianach). Biznes 230 PLN (z uplift od bundli). Realistyczna wartosc: 200 PLN (uwzglednia 10% rabat od sredniej 220 PLN, bez agresywnego uplift). **Przyjmujemy 200 PLN.**

### 4.2 Trzy scenariusze (skorygowane)

#### Scenariusz PESYMISTYCZNY (ograniczona adopcja kart)

Zalozenia: tylko 15% klientow powtarzajacych chce/moze platnic karta. Brak prepaid w M1--3. Churn 9%. Brak bundli.

```
Miesiac | Nowi  | Churn | Aktywni | Przychod sub | Kanibal. | Netto
--------|-------|-------|---------|-------------|----------|--------
  1     |  20   |   0   |    20   |    3 440    |  -1 376  |  2 064
  3     |  20   |   5   |    50   |    8 600    |  -3 440  |  5 160
  6     |  25   |   8   |    82   |   14 104    |  -5 642  |  8 462
  12    |  30   |  11   |   120   |   20 640    |  -8 256  | 12 384
--------|-------|-------|---------|-------------|----------|--------
ROK 1   |  295  |  103  |   120   |  142 000    | -56 800  | 85 200
```

**Przychod netto R1: 85 000 PLN.** Wynik niski, ale program jest cash-flow positive od M2 (koszty platformy Appstle: 30 USD/mies = 120 PLN).

#### Scenariusz BAZOWY (realistyczna adopcja + prepaid od M2)

Zalozenia: 30--40% segmentu subskrypcyjnego moze/chce platnic karta lub prepaid. Prepaid od M2 dodaje 15--20% do bazy. Churn 8% -> 6%. Sub AOV 200 PLN.

```
Miesiac | Nowi  | Churn | Aktywni | Przychod sub | Kanibal. | Netto
--------|-------|-------|---------|-------------|----------|--------
  1     |  30   |   0   |    30   |    5 160    |  -2 064  |  3 096
  3     |  30   |   6   |    78   |   13 416    |  -5 366  |  8 050
  6     |  35   |   9   |   130   |   22 360    |  -8 944  | 13 416
  9     |  38   |  10   |   180   |   30 960    | -12 384  | 18 576
  12    |  40   |  13   |   220   |   37 840    | -15 136  | 22 704
--------|-------|-------|---------|-------------|----------|--------
ROK 1   |  410  |  118  |   220   |  270 000    |-108 000  |162 000
```

**Przychod netto R1: 162 000 PLN.** Program pokrywa **ok. 17%** luki przychodowej (112K PLN/mies. gap do celu 334K).

**Na M12:** 22 700 PLN/mies netto = **20% luki przychodowej.**

#### Scenariusz OPTYMISTYCZNY (silna adopcja Apple Pay + prepaid + bundleý)

Zalozenia: Apple Pay/Google Pay rosna o 20% rocznie w Polsce. Prepaid 3-miesieczne pokrywaja klientow BLIK. Bundleý podnoszą sub AOV do 240 PLN. Churn 7% -> 5%. Silna konwersja istniejacych repeat buyers.

```
Miesiac | Nowi  | Churn | Aktywni | Przychod sub | Kanibal. | Netto
--------|-------|-------|---------|-------------|----------|--------
  1     |  45   |   0   |    45   |    9 288    |  -3 252  |  6 036
  3     |  50   |   7   |   120   |   24 768    |  -8 669  | 16 099
  6     |  55   |  12   |   210   |   43 344    | -15 170  | 28 174
  9     |  55   |  14   |   290   |   59 856    | -20 950  | 38 906
  12    |  60   |  16   |   360   |   74 304    | -26 006  | 48 298
--------|-------|-------|---------|-------------|----------|--------
ROK 1   |  645  |  125  |   360   |  460 000    |-161 000  |299 000
```

**Przychod netto R1: 299 000 PLN.** Na M12: 48 300 PLN/mies = **43% luki przychodowej.**

### 4.3 Podsumowanie scenariuszy

| Scenariusz | Aktywni sub M12 | Przychod sub R1 | Netto nowy R1 | % luki (M12) |
|-----------|----------------|----------------|-------------|-------------|
| Pesymistyczny | 120 | 142K PLN | 85K PLN | 11% |
| **Bazowy** | **220** | **270K PLN** | **162K PLN** | **20%** |
| Optymistyczny | 360 | 460K PLN | 299K PLN | 43% |

**Porownanie z oryginalnymi projekcjami ekspertow:**

| Ekspert | R1 przychod sub | R1 netto | Nasza korekta |
|---------|----------------|---------|--------------|
| Shopify (tech) | 200K PLN | brak | Nie uwzglednil kanibalizacji --- zbyt prosty model |
| Business (kons.) | 462K PLN | 277K PLN | Zawyzone nowe sub/mies. i sub AOV przy blokadzie platnosci |
| Business (umiark.) | 843K PLN | 548K PLN | Nierealistyczne przy polskich ograniczeniach platnosci |
| **Nasz bazowy** | **270K PLN** | **162K PLN** | Skorygowany o bloker platnosci + realistyczny seed |

### 4.4 Co lamie model? Co daje 2x?

**Co lamie model (powoduje spadek do pesymistycznego):**
- **Zle interwaly bez korekcji** --- produkt sie pietrzy (za czesto) lub klient zostaje bez (za rzadko). Bez ankiety dawkowania i adaptacyjnego flow po 2. dostawie, churn z powodu zlego interwalu moze stanowic 25% wszystkich rezygnacji
- Apple Pay/Google Pay nadal niszowe w Polsce (stagnacja adopcji)
- Prepaid plany kwartalne nie budza zainteresowania (klienci nie chca zobowiazywan)
- Churn > 10% miesieczny (slabe onboarding, brak edukacji)
- Problemy techniczne z GEN-6 theme (variant selector bug przenosi sie na subscription widget)

**Co daje 2x (przesuwa do optymistycznego i dalej):**
- Przelewy24 lub BLIK wdrazaja recurring na Shopify (game-changer: 100% rynku)
- GenActiv uruchamia program lojalnosciowy zintegrowany z subskrypcja (sticky)
- Bundleý 3-produktowe staja sie dominujaca forma sub (AOV > 300 PLN)
- ARMRA-style content marketing (influencerzy, TikTok) buduje popyt na subskrypcje

---

## 6. UJEDNOLICONA ROADMAPA WDROZENIA

### Faza 0: PRZYGOTOWANIE (Lipiec W3-4, 2026) --- 2 tygodnie

| Tydzien | Zadanie | Odpow. | Effort |
|---------|---------|--------|--------|
| W3 | Replenishment flow Klaviyo: 3 sciezki (Colostrum 120 kaps, 60 kaps, Fiberbiom) | CC | 6h |
| W3 | EDNO flow dla klientow po 1. zakupie | CC | 3h |
| W3 | Research finalny: Appstle free plan test na dev/staging | CC+DEV | 2h |
| W3 | **Eksport pelnej historii zamowien** (Shopify admin CSV, 12+ mies.) do walidacji interwalow | CC | 2h |
| W3 | **Ponowna analiza reorder intervals** na pelnych danych (365 dni) | CC | 4h |
| W4 | Subscription Upsell flow draft (nie aktywowac --- wymaga sub platformy) | CC | 4h |
| W4 | Decyzja go/no-go na Appstle (po testach) | BIZNES | -- |
| W4 | Weryfikacja Shopify Payments: karty wlaczone obok P24 | DEV | 1h |

**Total Faza 0: 22h**

### Faza 1: FUNDAMENT (Sierpien 2026) --- 4 tygodnie

| Tydzien | Zadanie | Odpow. | Effort |
|---------|---------|--------|--------|
| W1 | Instalacja Appstle Subscriptions (free tier) | CC | 15min |
| W1 | Selling Plan Group "Subskrybuj i Oszczedz": interwaly per produkt (14/21/28 Fiberbiom, 30/45/60 Colostrum) | CC | 3h |
| W1 | Rabat 10% na sub, darmowa dostawa na sub orders | CC | 1h |
| W1 | Podlaczenie 5 produktow Tier 1 do selling plans | CC | 2h |
| W2 | Widget subskrypcyjny na PDP z **ankieta dawkowania** (GEN-6 theme) | DEV | 10h |
| W2 | Price update JS (pokaz oszczednosc %) + dynamiczny interwal z ankiety | DEV | 4h |
| W2 | Cart line item: badge "Subskrypcja co {{ interval }} dni" (dynamiczny) | DEV | 2h |
| W2 | Tlumaczenie widgetu na polski | CC | 2h |
| W3 | Customer portal: pelne tlumaczenie PL + branding GenActiv | CC | 6h |
| W3 | Link "Moje Subskrypcje" w nawigacji konta | DEV | 1h |
| W3 | Appstle -> Klaviyo integracja (Zapier lub webhooks) | CC | 3h |
| W3 | 6 transakcyjnych emaili sub w szablonach GenActiv (PL) | CC | 6h |
| W4 | Cancel save flows: "Dlaczego rezygnujesz?" + pauza/skip/rabat | CC | 4h |
| W4 | Dunning retry schedule: Day 1, 3, 5, 7 | CC | 1h |
| W4 | QA end-to-end: subskrypcja, zarzadzanie, anulowanie, re-sub | CC+MAN | 6h |
| W4 | Testy z 10 wewnetrznymi uzytkownikami | MAN | 4h |

**Total Faza 1: 51h (~7 dni roboczych)**

### Faza 2: LAUNCH + AUTOMATYZACJA (Wrzesien 2026) --- 4 tygodnie

| Tydzien | Zadanie | Odpow. | Effort |
|---------|---------|--------|--------|
| W1 | **SOFT LAUNCH**: sub wlaczone na PDP dla Tier 1 (5 produktow) | CC+DEV | 2h |
| W1 | Kampania email do top 500 repeat buyers: "Subskrybuj i Oszczedz" | CC | 4h |
| W1 | Flow "Witamy w Subskrypcji" (4 emaile: powitanie, rytuał, efekty, FAQ) | CC | 8h |
| W2 | Flow "Przypomnienie o Zamowieniu" (3 dni przed obciazeniem) | CC | 3h |
| W2 | Flow "Nieudana Platnosc" (3 emaile w 48h + conditional split) | CC | 4h |
| W2 | Segmenty Klaviyo S1--S6 (core subscription segments) | CC | 3h |
| W3 | Flow "Subscription Upsell" (konwersja one-time -> sub, live) | CC | 4h |
| W3 | **Flow "Adaptacja Interwalu" po 2. dostawie** (za wczesnie/idealnie/za pozno → auto-zmiana) | CC | 5h |
| W3 | Flow "Ankieta po 30 dniach" (health check-in) | CC | 3h |
| W3 | Prepaid 3-miesieczne plany (Fiberbiom, Colostrum 120) | CC | 3h |
| W4 | Monitoring M1: conversion rate, payment success, churn | CC | 4h |
| W4 | Iteracja: widget copy, frequency defaults na bazie danych | CC | 3h |

**Total Faza 2: 41h (~6 dni roboczych)**

### Faza 3: RETENCJA + EKSPANSJA (Pazdziernik-Listopad 2026)

| Miesiac | Zadanie | Odpow. |
|---------|---------|--------|
| Paz W1 | Tier 2 produkty: Fiberbiom flavors, Colostrum brzoskwinia, zawiesina | CC |
| Paz W2 | Bundle "Fiberbiom Smakowy Mix" (3 smaki) | CC |
| Paz W2 | Bundle "Colostrum + Blonnik Codziennie" | CC |
| Paz W3 | Flow "Cancel Save + Winback" (5 emaili, routing wg powodu) | CC |
| Paz W3 | Flow "Pause Winback" (3 emaile, reaktywacja) | CC |
| Paz W4 | Flow "Cross-sell subskrybenta" (Colostrum -> Fiberbiom, odwrotnie) | CC |
| Lis W1 | Flow "Churn Risk Intervention" (proxy: skip 2+, frequency change) | CC |
| Lis W1 | Segmenty zaawansowane S7--S14 | CC |
| Lis W2 | Pre-BF: sub +5% extra rabat (15% total) na 3 miesiace | CC+BIZNES |
| Lis W3 | BF: kampania "Zasubskrybuj z -20% na 3 pierwsze miesiace" | CC |
| Lis W4 | Post-BF: konwersja jednorazowych BF kupujacych -> sub | CC |

### Faza 4: OPTYMALIZACJA (Grudzien 2026)

| Zadanie | Odpow. |
|---------|--------|
| Flow "Milestone" (3., 6., 12. cykl --- nagrody, recenzje) | CC |
| A/B testy: subject lines, timing, rabaty retencyjne | CC |
| RFM + Sub layer: Champions+ActiveSub = VIP, AtRisk+Sub = Churn Intervention | CC |
| SMS pilot subskrypcyjny (upcoming charge, dunning) --- po audycie RODO | CC+PRAWNIK |
| Ewaluacja migracji Appstle -> Loop (jesli MRR > 30K PLN) | CC+BIZNES |
| Roczna analiza: kohorty, retention, CLV, kanibalizacja | CC |

### 6.1 Podsumowanie effort i kosztow

| Faza | Timeline | Effort | Koszt platformy |
|------|----------|--------|----------------|
| Faza 0: Przygotowanie | Lipiec W3-4 | 16h | $0 |
| Faza 1: Fundament | Sierpien | 51h | $0 (free tier) |
| Faza 2: Launch | Wrzesien | 41h | $0 -> $30/mies |
| Faza 3: Retencja | Paz-Lis | ~40h | $30/mies |
| Faza 4: Optymalizacja | Grudzien | ~20h | $30/mies |
| **TOTAL** | **5 miesiecy** | **~168h** | **~$150 (R1)** |

---

## 7. ARCHITEKTURA FLOW I AUTOMATYZACJI

### 6.1 Zunifikowana mapa flow (najlepsze elementy obu ekspertow)

Ekspert Shopify zaproponowal 8 flow, ekspert Klaviyo 10 (wlacznie z pre-subscription). Zunifikowany plan laczy oba podejscia:

```
WARSTWA PRE-SUBSCRIPTION (wdrozyc PRZED sub launch)
====================================================
  Flow 0a: Replenishment (3 sciezki produktowe, timing 23-57 dni)
  Flow 0b: EDNO (predykcyjne, dla klientow po 1. zakupie)
  Flow 0c: Subscription Upsell (2+ zakupy, brak sub, 3 emaile)

WARSTWA LIFECYCLE SUBSKRYPCJI (wdrozyc z sub launch)
====================================================
  Flow 1: Sub Welcome (4 emaile: powitanie, rytuał, efekty, FAQ)
  Flow 2: Upcoming Charge (1 email + opcjonalnie 1 SMS, 3 dni przed)
  Flow 3: Charge Success (potwierdzenie + cross-sell CTA)
  Flow 4: Dunning / Payment Failed (3 emaile w 48h + SMS po Email 2)
  Flow 5: Cross-sell subskrybenta (po 2. cyklu, split wg produktu)
  Flow 6: Milestone (cykl 3, 6, 12 --- nagrody, recenzje, prezent)
  Flow 7: Churn Risk Intervention (proxy: skip 2+, churn > 66%)
  Flow 8: Pause Winback (3 emaile w 30 dni)
  Flow 9: Cancel Save + Winback (2 fazy: save 0-3 dni, winback 14-90 dni)
```

### 6.2 Priorytetyzacja wg wplywu na przychod

```
PRIORYTET 1 --- Revenue Protection (wdrozyc w M1):
  ┌────────────────────────────────────────────────┐
  │ Dunning (Flow 4)          → -20-40% inv. churn │
  │ Upcoming Charge (Flow 2)  → -15% vol. churn    │
  │ Sub Welcome (Flow 1)      → +20% 1st retention │
  │ Replenishment (Flow 0a)   → +30% repeat rate   │
  └────────────────────────────────────────────────┘

PRIORYTET 2 --- Revenue Growth (wdrozyc w M2):
  ┌────────────────────────────────────────────────┐
  │ Sub Upsell (Flow 0c)      → konwersja one-time │
  │ Cancel Save (Flow 9)      → +10-20% save rate  │
  │ Pause Winback (Flow 8)    → -38% vol. churn    │
  └────────────────────────────────────────────────┘

PRIORYTET 3 --- Revenue Expansion (wdrozyc w M3):
  ┌────────────────────────────────────────────────┐
  │ Cross-sell (Flow 5)       → +20% AOV sub       │
  │ Churn Risk (Flow 7)       → proaktywna retencja│
  │ Milestone (Flow 6)        → tenure +15%        │
  └────────────────────────────────────────────────┘
```

### 6.3 Integracja Appstle -> Klaviyo (specyfika)

Poniewaz Appstle nie ma tak natywnej integracji jak Recharge (rc_* properties), potrzebujemy:

| Element | Implementacja | Effort |
|---------|-------------|--------|
| Subscription Created event | Appstle webhook -> Zapier -> Klaviyo Track API | 1h |
| Subscription Cancelled event | Appstle webhook -> Zapier -> Klaviyo Track API | 1h |
| Payment Failed event | Appstle webhook -> Zapier -> Klaviyo Track API | 1h |
| Upcoming Charge event | Appstle webhook -> Zapier -> Klaviyo Track API | 30min |
| Custom profile property: active_sub_count | Zapier -> Klaviyo Profile API (update) | 30min |
| Custom profile property: next_charge_date | Zapier -> Klaviyo Profile API (update) | 30min |
| Custom profile property: sub_products | Zapier -> Klaviyo Profile API (update) | 30min |
| Custom property: cancellation_reason | Appstle cancel flow -> Zapier -> Klaviyo | 30min |

**Total setup: ~6h.** Po migracji do Loop, eventy beda natywne (eliminacja Zapier).

### 6.4 Segmenty Klaviyo --- zunifikowana lista

Ekspert Klaviyo zaproponowal 14 segmentow (S1--S14). Ekspert Shopify zaproponowal 5. Zunifikowana lista z priorytetami:

| # | Segment | Definicja | Priorytet | Faza |
|---|---------|-----------|----------|------|
| S1 | Aktywni subskrybenci | active_sub_count > 0 | P1 | Faza 2 |
| S2 | Kandydaci na sub | Placed Order >= 2 AND active_sub_count = 0 | P1 | Faza 0 |
| S3 | Sub 1. cykl | sub_charge_count = 1 AND active_sub_count > 0 | P1 | Faza 2 |
| S4 | Sub lojalni (6+) | sub_charge_count >= 6 | P2 | Faza 3 |
| S5 | Churn risk (sub) | Predicted churn > 66% AND active_sub_count > 0 | P2 | Faza 3 |
| S6 | Zapauzowani | Sub paused event in 90d AND active_sub_count = 0 | P2 | Faza 3 |
| S7 | Anulowani (winback) | Sub cancelled event in 90d | P2 | Faza 3 |
| S8 | High-value sub | active_sub_count > 0 AND Predicted CLV top 20% | P3 | Faza 4 |
| S9 | Sub: Colostrum only | sub_products contains "Colostrum" | P3 | Faza 3 |
| S10 | Sub: Fiberbiom only | sub_products contains "Fiberbiom" | P3 | Faza 3 |
| S11 | Multi-product sub | active_sub_count >= 2 | P3 | Faza 4 |

---

## 8. SEKWENCJA URUCHOMIENIA PRODUKTOW

### 7.1 Tier 1 --- Launch (wrzesien 2026)

| Produkt | Cena | Cena sub (-10%) | Kadencje (z danych) | Default | Uzasadnienie |
|---------|------|----------------|--------------------|---------|----|
| FIBERBIOM - Blonnik + Colostrum | 189 PLN | 170 PLN | **14 / 21 / 28 dni** | **14 dni** | Mediana zużycia 16 dni (2 sasz./dzien). 77% <21 dni |
| COLOSTRUM GENACTIV, 120 kapsulek | 189 PLN | 170 PLN | **30 / 45 / 60 dni** | **45 dni** | Mediana reorder 35-41 dni (3-4 kaps./dzien) |
| COLOSTRUM GENACTIV, 60 kapsulek | 105 PLN | 95 PLN | **21 / 30 / 45 dni** | **30 dni** | Mediana reorder 32 dni — potwierdzone |
| COLOSTRUM GENACTIV, proszek | 189 PLN | 170 PLN | **21 / 30 / 45 dni** | **30 dni** | Mediana reorder 31 dni — potwierdzone |

**Zrodlo interwalow:** Analiza 3 026 zamowien Shopify, 59-dniowe okno (reports/reorder-interval-analysis-2026-07-17.md).
**Ograniczenie:** Okno 59 dni nie pozwala obserwowac cyklow 60+ dni. Colostrum 120 kaps. wymaga weryfikacji po zebraniu 180+ dni danych.

**Uwaga do rozbieznosci cen:** Ekspert Shopify podaje ceny Fiberbiom jako 179 PLN, ekspert biznesowy jako 189 PLN. Roznica moze wynikac z aktualnej ceny vs cena w danych historycznych. **Nalezy uzyc aktualnej ceny z Shopify Admin.** Projekcje bazowe uzywaja 189 PLN.

### 7.2 Tier 2 --- Ekspansja + Bundleý (pazdziernik 2026)

| Produkt/Bundle | Cena | Cena sub | Kadencja |
|---------------|------|---------|----------|
| FIBERBIOM Z ANANASEM | 189 PLN | 170 PLN | 30/45 dni |
| FIBERBIOM Z CZARNA PORZECZKA | 189 PLN | 170 PLN | 30/45 dni |
| Colostrum z brzoskwinia, 60g | 115 PLN | 104 PLN | 30 dni |
| **Bundle: Fiberbiom Mix** (3 smaki) | 567 PLN | 482 PLN (-15%) | 30 dni |
| **Bundle: Colostrum + Blonnik** | 378 PLN | 321 PLN (-15%) | 30/60 dni |

### 7.3 Tier 3 --- Prepaid + Specialty (listopad-grudzien 2026)

| Produkt/Plan | Cena | Kadencja |
|-------------|------|----------|
| Prepaid FIBERBIOM 3-miesieczny | 435 PLN (-19% vs 3x 189) | 1 platnosc, 3 dostawy |
| Prepaid COLOSTRUM 3-miesieczny | 480 PLN (-15% vs 3x 189) | 1 platnosc, 3 dostawy |
| COLOSTRUM JUNIOR (saszetki) | wg ceny | 30 dni |
| FUREVER DOG/CAT | wg ceny | 30/60 dni |
| **Build-a-Box** (dowolne 2+) | -10/12/15% wg ilosci | 30/60 dni |

---

## 9. MACIERZ RYZYK (zaktualizowana po cross-walidacji)

| Ryzyko | Prawdop. | Wplyw | Mitygacja | Ekspert zrodlowy |
|--------|---------|-------|-----------|-----------------|
| **Nietrafiony interwal dostawy** | WYSOKA | WYSOKI | Ankieta dawkowania na PDP, adaptacyjny flow po 2. dostawie, monitoring skip rate. FIBERBIOM default 14 dni (nie 30!), Colostrum 120 kaps default 45 dni (nie 60) | Analiza reorder intervals |
| **Niska adopcja przez brak BLIK/P24** | WYSOKA | WYSOKI | Prepaid plany, Apple Pay/Shop Pay, jasna komunikacja na PDP | Wszyscy 3 |
| **Wysoki churn M1-3 (Order 2-3 drop-off)** | SREDNIA | WYSOKI | Onboarding email (4 emaile), 30-dniowy check-in, dawkowanie reminded, edukacja "4-8 tygodni do efektow" | Shopify + Klaviyo |
| **Konflikty widgetu sub z GEN-6 variant selector** | SREDNIA | SREDNI | Test A/B znalazl problem z variant change; subscription widget musi byc testowany z kazdym wariantem | Shopify |
| **Kanibalizacja istniejacych jednorazowych** | WYSOKA | NISKI | Kanibalizacja jest mechanizmem --- 10% rabat vs 5,7x czestotliwosc. Net positive nawet przy 40% kanibalizacji | Business |
| **Compliance RODO/UOKiK** | NISKA | WYSOKI | 14-dniowe prawo odstapienia per dostawa, prosty przycisk "Anuluj", brak price lock-in, KSeF integracja | Shopify |
| **KSeF e-faktura dla recurring billing** | SREDNIA | SREDNI | Appstle generuje dane do faktur; moze wymagac dedykowanego rozwiazania fakturowego | Shopify |
| **Erozja marzy od rabatow + darmowa dostawa** | SREDNIA | SREDNI | Start od 10% (nie 15-20%). Darmowa dostawa = ~15 PLN/order, offset przez 9-12% uplift adopcji | Business |
| **Over-attribution w Klaviyo** | NISKA | NISKI | Monitoruj RPR zamiast total revenue; uzywaj conversion rate do porownania flow | Klaviyo |
| **Platforma vendor risk (konsolidacja rynku)** | NISKA | SREDNI | Appstle (start) ma eksport danych; migracja do Loop jest 1-2 dniowa. Recharge kupil Skio | Shopify + Business |

---

## 10. KPI I DECISION GATES

### 9.1 KPI na kazdym etapie

| KPI | M1 | M3 | M6 | M12 | Akcja jesli ponizej |
|-----|-----|-----|-----|------|-------------------|
| Aktywni subskrybenci | 30 | 78 | 130 | 220 | < 50% M3: rewizja CTA/pricing |
| Sub conversion rate (PDP) | 2% | 3% | 4% | 5% | < 2% M3: A/B test widgetu |
| Payment success rate | 80% | 85% | 88% | 90% | < 80%: rewizja dunning flow |
| Miesieczny churn | < 10% | < 8% | < 7% | < 6% | > 10% M3: onboarding audit |
| Cancel save rate | -- | 10% | 15% | 20% | < 10% M3: rewizja cancel flows |
| Dunning recovery rate | -- | 30% | 40% | 50% | < 30% M6: dodaj SMS/telefon |
| Sub AOV | 180 PLN | 200 PLN | 210 PLN | 230 PLN | < 180: rewizja bundli |
| Prepaid % subskrybentow | 0% | 10% | 20% | 25% | < 10% M6: zmien pozycjonowanie |

### 9.2 Decision Gates

| Gate | Warunek | Decyzja |
|------|---------|---------|
| **Gate 1 (M3):** Czy kontynuowac? | > 50 aktywnych sub AND churn < 10% AND payment success > 80% | TAK -> Faza 3 (Tier 2 + bundleý). NIE -> pivot pricing/UX |
| **Gate 2 (M6):** Migracja platformy? | MRR sub > 30K PLN AND churn < 7% | TAK -> migracja Appstle -> Loop. NIE -> kontynuacja Appstle |
| **Gate 3 (M9):** Skalowanie? | > 200 aktywnych sub AND net churn < 5% | TAK -> Tier 3, ads na sub, Build-a-Box. NIE -> focus retencja |
| **Gate 4 (M12):** Roczny przeglad | Sub revenue > 10% total revenue | TAK -> ekspansja programu, loyalty integracja. NIE -> rewizja strategii |
| **STOP Gate:** Zamkniecie programu | Churn > 15% przez 3 miesiace OR sub conversion < 1% | Wycofanie subskrypcji, powrot do replenishment-only |

### 9.3 Raportowanie tygodniowe

| Raport | Zrodlo | Odbiorca |
|--------|--------|----------|
| Nowi subskrybenci (dziennie) | Appstle dashboard | Zespol ecom |
| Churn (voluntary + involuntary) | Appstle + Klaviyo dunning metrics | Zespol ecom |
| Payment failure rate | Shopify Payments + Stripe | DEV |
| Dunning recovery rate | Klaviyo flow analytics | CC |
| Top produkty subskrypcyjne | Appstle dashboard | BIZNES |
| Powody anulowania | Cancel flow analytics | BIZNES + CC |
| Sub AOV i basket size | Shopify + Appstle | BIZNES |
| Kohorty retencji (miesieczne) | Appstle/Loop + Klaviyo segmenty | CC |

---

## 11. APPENDIX: LOG ROZSTRZYGNIECIA KONFLIKTOW

### Konflikt 1: Platforma subskrypcyjna

| Argument | Za | Przeciw | Waga |
|----------|-----|--------|------|
| **Recharge** (Klaviyo ekspert) | Najlepsza integracja Klaviyo, 9+ eventow natywnych | $99+1.49%+$0.19/order = najdrozszy; nadmiarowy przy <500 sub | Odrzucony na start |
| **Appstle** (Shopify ekspert) | 0% prowizji, free tier, 5.0 ocena, smallest JS | Integracja Klaviyo przez Zapier (3h extra setup) | **Przyjety na start** |
| **Loop** (Business ekspert) | Najlepsze retention tools, 1.0% prowizji | $99 base = drogi przy starcie; overkill przy < 150 sub | **Przyjety na skale** |

**Rozstrzygniecie:** Appstle (start, $0-30/mies) -> Loop (>30K PLN MRR, ~$150/mies). Recharge tylko jesli Loop okazuje sie niewystarczajacy przy >2000 sub.

### Konflikt 2: Projekcje przychodow R1

| Ekspert | R1 netto | Kluczowe zalozenie | Problem |
|---------|---------|-------------------|---------|
| Shopify | ~200K brutto | 30 nowych/mies, 180 PLN AOV, 5% churn | Brak modelu kanibalizacji |
| Business | 277K netto | 50 nowych/mies, 230 PLN AOV, 8% churn | Zawyzone seed; bloker platnosci nie uwzglediony |

**Rozstrzygniecie:** Przyjeto scenariusz bazowy 162K PLN netto. Seed obnizone z 50 do 30, sub AOV z 230 do 200, churn z 8% startowego malejacy do 6%. Dodano trzy scenariusze (pesymistyczny 85K, bazowy 162K, optymistyczny 299K) --- szeroki spread odzwierciedla niepewnosc specyficzna dla polskiego rynku platnosci.

### Konflikt 3: Powaga blokera platnosci

| Ekspert | Ocena | Uzasadnienie |
|---------|-------|-------------|
| Shopify | "Critical blocker" | 70% polskiego e-commerce to BLIK/P24 |
| Business | Modeluje 15-25% adopcji | Segment subskrybentow jest inny niz ogol |

**Rozstrzygniecie:** Ekspert Shopify ma racje co do faktu (70% BLIK/P24), ale ekspert biznesowy ma racje co do segmentacji (subskrybent ≠ sredni kupujacy). Przyjeto pozycje kompromisowa: bloker jest powazny, ale nie krytyczny, bo (a) segment sub ma wyzsze uzycie kart, (b) prepaid omija problem, (c) Apple Pay rosnie. Wplyw: -30-40% adopcji vs rynki bez ograniczen (nie -70%).

### Konflikt 4: Struktura rabatow

| Ekspert | Propozycja |
|---------|-----------|
| Business | 10% ongoing + 15% first order |
| Klaviyo | 10/12/15% tiered wg ilosci produktow |
| Shopify | 10% flat + 15-19% prepaid |

**Rozstrzygniecie:** Odrzucono 15% na pierwsza zamowienie (ekspert biznesowy). Uzasadnienie: przy ograniczonej puli potencjalnych subskrybentow (bloker platnosci), dodatkowy 5% rabat na 1. zamowienie przynosi niewielki incremental uplift vs koszt marzy. Zamiast tego: **darmowa dostawa na wszystkie zamowienia sub** (~15 PLN/order) --- latwiejsza komunikacja, mniejszy perceived discount, silniejszy driver adopcji.

Przyjeta struktura:
- 1 produkt: -10%
- 2 produkty: -12% (wdrozyc od M3)
- 3+ produkty: -15% (wdrozyc od M3)
- Prepaid kwartalny: -15%
- Prepaid polroczny: -19%
- Darmowa dostawa: na wszystkie zamowienia sub

### Konflikt 5: Timeline i effort

| Ekspert | Timeline | Effort |
|---------|----------|--------|
| Shopify | 6-8 tygodni | 81-93h |
| Klaviyo | 5 miesiecy (phased) | nie podano |

**Rozstrzygniecie:** Oba podejscia sa poprawne --- ekspert Shopify podaje czas do MVP launch, ekspert Klaviyo podaje czas do pelnej automatyzacji. Przyjeto hybryda: MVP launch w 6 tygodniach (Faza 0+1 = 67h), pelna automatyzacja w 5 miesiecy (168h total). Timeline zgodny z roadmapa H2 2026: sub launch = sierpien/wrzesien.

---

*Raport stanowi ujednolicona rekomendacje na bazie trzech niezaleznych audytow. Wszelkie projekcje sa szacunkami --- faktyczne wyniki zaleza od egzekucji, warunkow rynkowych i tempa adopcji platnosci cyfrowych w Polsce. Rekomendujemy przeglad kwartalny (Decision Gates) z gotowoscia do pivotu.*

*Nastepny krok: decyzja go/no-go na spotkaniu zespolu, zatwierdzenie budżetu Fazy 0 (16h CC, 0 PLN platforma), instalacja testowa Appstle na staging.*

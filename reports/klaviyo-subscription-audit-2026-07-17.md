# Klaviyo Subscription Model Audit — GenActiv.pl

**Data:** 2026-07-17
**Autor:** Claude Code (audyt automatyczny)
**Kontekst:** Ewaluacja mozliwosci Klaviyo do obslugi modelu subskrypcyjnego dla GenActiv.pl
**Status:** Raport referencyjny dla decyzji platformowej (Retention / Sub / Lojalnosc — H2 2026)

---

## Spis tresci

1. [Streszczenie wykonawcze](#1-streszczenie-wykonawcze)
2. [Integracja Klaviyo z platformami subskrypcyjnymi](#2-integracja-klaviyo-z-platformami-subskrypcyjnymi)
3. [Flow subskrypcyjne — architektura](#3-flow-subskrypcyjne--architektura)
4. [Segmentacja subskrypcyjna](#4-segmentacja-subskrypcyjna)
5. [Analityka predykcyjna](#5-analityka-predykcyjna)
6. [SMS + Email — orkiestracja (Polska, RODO)](#6-sms--email--orkiestracja-polska-rodo)
7. [Raportowanie i atrybucja](#7-raportowanie-i-atrybucja)
8. [Best practices — branża suplementów](#8-best-practices--branża-suplementów)
9. [Rekomendacja platformy subskrypcyjnej](#9-rekomendacja-platformy-subskrypcyjnej)
10. [Roadmapa wdrozenia](#10-roadmapa-wdrozenia)
11. [Zrodla](#11-zrodla)

---

## 1. Streszczenie wykonawcze

### Stan obecny GenActiv

| Metryka | Wartosc | Cel H2 2026 |
|---------|---------|-------------|
| Sub adoption | 0% | 5% |
| Repeat purchase rate | 55% | 62% |
| Email revenue share | 5.1% | 12% |
| Lista email | ~7,900 | 14,000 |
| Aktywne flow | 5 | 14 |
| SMS baza | 0 | 3,500 |

### Kluczowe wnioski

1. **Klaviyo w pelni obsługuje model subskrypcyjny** — ale wymaga platformy posredniczącej (Recharge, Skio, lub Shopify native + Shopify Flow). Klaviyo sam nie zarzadza subscriptions — przetwarza eventy i automatyzuje komunikacje.

2. **Rekomendacja platformy: Recharge (plan Starter, $99/mies)** — najlepsza integracja z Klaviyo, najszerszy ekosystem, PLN przez Shopify Markets, 60-dniowy trial. Skio ($599/mies) jest nadmiarowa przy obecnym wolumenie GenActiv.

3. **9 flow subskrypcyjnych** mozliwych do zbudowania w Klaviyo od dnia 1 integracji, z czego 4 maja bezposredni wplyw na retencje przychodu (dunning, upcoming charge, cancellation save, churn risk).

4. **Predictive analytics Klaviyo (CLV, churn, EDNO)** dzialaja na obecnej bazie GenActiv — wymagania (500+ klientow, 180 dni historii, 3+ zakupy) sa spelnione.

5. **SMS w Polsce** jest mozliwy przez Klaviyo (PL na liscie obsługiwanych krajow), ale wymaga oddzielnej zgody RODO (osobny checkbox) i double opt-in.

6. **Replenishment flow** (przypomnienia o uzupelnieniu zapasow) powinien byc wdrozony **przed** subskrypcja — konwertuje jednorazowych w powtarzalnych, a potem w subskrybentow.

---

## 2. Integracja Klaviyo z platformami subskrypcyjnymi

### 2.1 Macierz integracji

| Platforma | Integracja z Klaviyo | Eventy subskrypcyjne | Profile properties | Churn risk score | Revenue separation | Cena (mies.) |
|-----------|---------------------|---------------------|-------------------|-----------------|-------------------|-------------|
| **Recharge** | Natywna | 9+ metrk | rc_* properties | Proxy (budowane) | Reczna | $99 + 1.49% |
| **Skio** | Natywna | 20+ metrk | skio* properties | Natywny | Natywna | $599 + 1.0% |
| **Bold** | API-based | Podstawowe | Ograniczone | Brak | Brak | $49.99 flat |
| **Shopify native** | Brak natywnej | Przez Shopify Flow | Brak natywnych | Brak | Brak | Wliczone w plan |

### 2.2 Recharge — szczegoly integracji z Klaviyo

**Metryki (eventy) wysylane do Klaviyo:**

| Metryka Recharge | Trigger | Zastosowanie w flow |
|-----------------|---------|-------------------|
| Subscription started on ReCharge | Nowa subskrypcja (checkout, portal, API) | Subscription Welcome flow |
| Subscription cancelled on ReCharge | Anulowanie przez portal | Cancellation Save / Winback |
| Recharge subscription reactivated | Reaktywacja anulowanej | Reactivation Confirmation |
| Subscription paused on ReCharge | Pauza subskrypcji | Pause Winback flow |
| Subscription SKU swapped on Recharge | Zmiana produktu | Swap Confirmation |
| Subscription next charge date changed | Zmiana daty obciazenia | Confirmation + reminder |
| Subscription frequency changed | Zmiana czestotliwosci | Confirmation |
| One-time product added/deleted | Dodanie/usuniecie produktu jednorazowego | Cross-sell confirmation |
| Charge processed | Pomyslne obciazenie | Order Confirmation |
| Charge failed | Nieudane obciazenie | Dunning flow |
| Order skipped | Pominiecie zamowienia | Skip Recovery |
| Upcoming charge | Nadchodzace obciazenie (3-5 dni) | Upcoming Order Notification |

**Wlasciwosci profilu (rc_* custom properties):**

| Property | Opis | Segmentacja |
|----------|------|-------------|
| `rc_active_subscription_count` | Liczba aktywnych subskrypcji | Aktywni subskrybenci (>0) |
| `rc_customer_charge_count` | Calkowita liczba obciazen | Tenure / lojalnosc |
| `rc_next_charge_date` | Data nastepnego obciazenia | Komunikacja pre-charge |
| `Recharge Subscriptions` | Lista produktow (auto-aktualizowana) | Subskrypcje produktowe |
| Cancellation reason | Powod anulowania | Winback personalizacja |

**Backfill:** Dane historyczne custom properties mozna backfillowac. Eventy historyczne NIE sa backfillowane — dostepne dopiero po pierwszym wystąpieniu danego eventu.

### 2.3 Skio — szczegoly integracji

Skio oferuje dwie unikalne funkcje w porownaniu z Recharge:

1. **Natywny churn risk score** — event w Klaviyo gdy ryzyko osiaga prog. Recharge wymaga budowania proxy z behavioral signals.
2. **Natywna separacja revenue** — subskrypcja vs jednorazowy zakup jako osobne metryki Klaviyo.

Dodatkowe Skio-specyficzne properties:
- `hasSurpriseDiscount` — boolean, Surprise & Delight rabat
- `hasSurpriseProduct` — boolean, darmowy prezent
- `isPrepaid` / `isPrepaidGift` — prepaid status
- `skioSubscriptionDaysUntilRenewal` — dni do odnowienia
- `cyclesCompleted` — liczba ukończonych cykli

### 2.4 Shopify Native Subscriptions

Shopify native (Selling Plans API) **nie ma natywnej integracji z Klaviyo** dla eventow subskrypcyjnych. Obejscie:

```
Shopify Subscription Event → Shopify Flow → Klaviyo Connector → Custom Event w Klaviyo
```

**Ograniczenia Shopify native:**
- Brak membership/loyalty tier integration
- Brak zaawansowanego customer portal
- Brak cancel flow / save offers
- Ograniczone analityki subskrypcyjne

**Wniosek:** Shopify native jest zbyt ograniczone dla GenActiv. Recharge lub Skio zapewnia pelna integracja z Klaviyo.

---

## 3. Flow subskrypcyjne — architektura

### 3.1 Pelna mapa flow (9 flow + 1 pre-subscription)

```
                    ┌─────────────────────────────────────────────────┐
                    │         PRE-SUBSCRIPTION LAYER                  │
                    │                                                 │
                    │  ┌──────────────┐    ┌─────────────────────┐   │
                    │  │ Replenishment│    │ Subscription Upsell │   │
                    │  │ Flow (30/60d)│───►│ Flow (po 2-3 zak.)  │   │
                    │  └──────────────┘    └─────────┬───────────┘   │
                    │                                │               │
                    └────────────────────────────────┼───────────────┘
                                                     │
                                                     ▼
┌────────────────────────────────────────────────────────────────────────────┐
│                     SUBSCRIPTION LIFECYCLE LAYER                          │
│                                                                           │
│  ┌─────────────┐                                                         │
│  │ 1. Sub      │  Trigger: Subscription started                         │
│  │ Welcome     │  3 emaile: powitanie → jak stosowac → czego oczekiwac  │
│  └─────┬───────┘                                                         │
│        │                                                                  │
│        ▼                                                                  │
│  ┌─────────────┐                                                         │
│  │ 2. Upcoming │  Trigger: Upcoming charge (3-5 dni przed)              │
│  │ Charge      │  1 email: co idzie, mozliwosc zmiany, Quick Actions    │
│  └─────┬───────┘                                                         │
│        │                                                                  │
│  ┌─────┼──────────────────────────────────────┐                          │
│  │     │                                      │                          │
│  │     ▼                                      ▼                          │
│  │ ┌─────────────┐                  ┌─────────────┐                     │
│  │ │ 3. Charge   │                  │ 4. Dunning  │                     │
│  │ │ Success     │                  │ (Payment    │                     │
│  │ │ Confirmation│                  │ Failed)     │                     │
│  │ └─────────────┘                  │ 3 emaile    │                     │
│  │                                  │ w 48h       │                     │
│  │                                  └─────────────┘                     │
│  │                                                                      │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐             │
│  │  │ 5. Cross-   │    │ 6. Mile-    │    │ 7. Churn    │             │
│  │  │ sell (dodaj │    │ stone       │    │ Risk        │             │
│  │  │ produkt)    │    │ Anniversary │    │ Intervention│             │
│  │  └─────────────┘    └─────────────┘    └─────────────┘             │
│  │                                                                      │
│  │  ┌─────────────┐    ┌─────────────┐                                │
│  │  │ 8. Pause    │    │ 9. Cancel   │                                │
│  │  │ Winback     │    │ Save +      │                                │
│  │  │             │    │ Winback     │                                │
│  │  └─────────────┘    └─────────────┘                                │
│  │                                                                      │
│  └──────────────────────────────────────────────────────────────────────┘
└────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Szczegoly kazdego flow

#### Flow 0: Replenishment (PRE-SUBSCRIPTION — wdrozyc PRZED subskrypcja)

**Cel:** Przypomnienie o uzupelnieniu zapasow. Konwersja jednorazowych w powtarzalnych.

```
Trigger: Placed Order (filtr: produkty konsumowalne)
Flow Filter: Placed Order = 0 since starting this flow (product-specific)
             AND rc_active_subscription_count = 0 (wykluczenie subskrybentow)

Sciezka A: Colostrum 120 kaps (60 dni zapas)
├── Day 52: Email 1 — "Twoje colostrum konczy się za tydzień"
├── Day 57: Email 2 — "Ostatnie dni zapasu — zamów z -10% na subskrypcję"
└── Day 65: Email 3 — "Twój codzienny rytuał — nie przerywaj go" + kod rabatowy

Sciezka B: Colostrum 60 kaps / Proszek (30 dni zapas)
├── Day 23: Email 1 — "Za tydzień skończy Ci się colostrum"
├── Day 27: Email 2 — "Zamów teraz — darmowa dostawa od 300 zł"
└── Day 35: Email 3 — "Wróć do rytuału" + -10% na subskrypcję

Sciezka C: Fiberbiom (30 dni zapas)
├── Day 23: Email 1 — "Czas na nowe Fiberbiom"
├── Day 27: Email 2 — "Kontynuuj wspieranie trawienia"
└── Day 35: Email 3 — rabat na subskrypcję
```

**Kluczowe:** Timing bazuje na ilosci produktu. Conditional split na SKU/nazwe produktu.

#### Flow 1: Subscription Welcome

**Cel:** Onboarding subskrybenta, budowanie nawyku, redukcja churn 1. cyklu.

```
Trigger: Subscription started on ReCharge
Flow Filter: rc_customer_charge_count = 1 (tylko pierwszy cykl)

Day 0: Email 1 — "Witaj w programie subskrypcji GenActiv!"
  Tresc: potwierdzenie, co dostajesz, kiedy nastepna dostawa,
         link do portalu klienta, korzyści subskrypcji (-10%)

Day 3: Email 2 — "Twój codzienny rytuał z colostrum"
  Tresc: instrukcja stosowania, dawkowanie, porady
  (reuse tresci z PurOnb2 — Ritual)

Day 7: Email 3 — "Czego oczekiwać w pierwszych tygodniach"
  Tresc: timeline efektow, social proof, link do FAQ
  (reuse tresci z PurOnb3 — Effects)

Day 14: Email 4 — "Masz pytania? Jestesmy tutaj"
  Tresc: CTA do customer service, survey satysfakcji
```

**Uwaga:** Jezeli profil przechodzi zarowno przez Post-Purchase Onboarding (Flow B) jak i Sub Welcome, nalezy wykluczyc duplikaty:
- Sub Welcome Flow Filter: nie dostal PurOnb1 w ostatnich 30 dni
- Lub: polacz Sub Welcome z Post-Purchase w jeden flow z conditional split na `rc_active_subscription_count > 0`

#### Flow 2: Upcoming Charge Notification

**Cel:** Transparentnosc, mozliwosc modyfikacji przed obciazeniem, redukcja churn.

```
Trigger: Upcoming charge on Recharge (3-5 dni przed)

Day 0: Email 1 — "Twoja subskrypcja odnawia się za 3 dni"
  Tresc:
  - Lista produktow w nadchodzacym zamowieniu
  - Kwota obciazenia (PLN, bez dziesiętnych)
  - Quick Actions: [Pomiń] [Zmień datę] [Zmień produkt] [Zarządzaj]
  - Link do portalu subskrypcji (Recharge Quick Actions URL)
```

**Wskazowka:** Quick Actions URL to dynamiczny link unikalny dla kazdego klienta, umozliwia zarzadzanie subskrypcja bez logowania. Skonfiguruj w Recharge.

**Dlaczego wazny:** Klienci, którzy czuja kontrole nad subskrypcja, anuluja rzadziej. 38% konsumentow woli zapauzowac niz anulowac (Recurly 2026).

#### Flow 3: Dunning (Payment Failed Recovery)

**Cel:** Odzyskanie nieudanych platnosci. Redukcja involuntary churn.

```
Trigger: Charge failed on Recharge

0-1h: Email 1 — "Problem z platnoscia — szybka aktualizacja"
  Ton: neutralny, bez winy
  CTA: [Zaktualizuj dane platnicze] — direct link
  Tresc: "Twoja ostatnia płatność nie poszła przez.
          To się zdarza — karty wygasają, limity się resetują.
          Kliknij poniżej, żeby zaktualizować dane i nie tracić swojej subskrypcji."

+24h: Email 2 — "Jeszcze jeden krok — Twoja subskrypcja czeka"
  Ton: lagodna pilnosc
  CTA: [Zaktualizuj kartę teraz]
  Tresc: wyjasnij co sie stanie jesli nie zaktualizuje (pauza/anulowanie)

+48h: Email 3 — "Ostatnia szansa na zachowanie subskrypcji"
  Ton: pilne, ale empatyczne
  CTA: [Ratuj swoją subskrypcję]
  Dodaj: numer telefonu / czat do pomocy
```

**Conditional split wg typu bledu:**
- Hard decline (karta wygasla, zablokowana) → informuj o koniecznosci nowej karty
- Soft decline (insufficient funds) → "spróbujemy ponownie za kilka dni"

**Statystyka:** Dunning flow zmniejsza involuntary churn o 20-40% w pierwszych 60 dniach.

#### Flow 4: Subscription Cross-sell (Dodaj produkt)

**Cel:** Zwiekszenie AOV subskrypcji, budowanie ekosystemu produktowego.

```
Trigger: Charge processed on Recharge (pomyslne obciazenie)
Flow Filter: rc_customer_charge_count >= 2 (nie przy 1. cyklu)
             AND rc_active_subscription_count = 1 (jeszcze nie ma 2+ sub)

Conditional Split: Jaki produkt subskrybuje?

Sciezka A: Subskrybuje Colostrum → Cross-sell Fiberbiom
Day 5: Email — "Colostrum + Fiberbiom = kompletna ochrona"
  Tresc: synergia produktow, social proof, CTA: [Dodaj do subskrypcji]
  Quick Actions URL z predefiniowanym Fiberbiom

Sciezka B: Subskrybuje Fiberbiom → Cross-sell Colostrum
Day 5: Email — "Uzupełnij swój rytuał o colostrum"
  Tresc: edukacja, dlaczego warto, CTA: [Dodaj do subskrypcji]

Sciezka C: Subskrybuje 1 format Colostrum → Upsell wiekszy format
Day 5: Email — "Dwupak = wieksza oszczednosc"
  Tresc: kalkulacja oszczednosci, wygoda
```

#### Flow 5: Milestone / Anniversary

**Cel:** Docenienie lojalnosci, wzmacnianie relacji, social proof.

```
Trigger: Charge processed on Recharge
Conditional Split na rc_customer_charge_count:

= 3 (3. cykl — ok. 3 miesiace):
  Email: "3 miesiące z GenActiv — gratulacje!"
  Tresc: podsumowanie, ile juz zuzyl, nauka, zacheta do recenzji
  CTA: [Zostaw opinie] → Judge.me/Loox

= 6 (pol roku):
  Email: "Pół roku zdrowia — dziękujemy!"
  Tresc: ekskluzywny rabat -15% na nastepne zamowienie
  CTA: [Twój prezent czeka]

= 12 (rocznica):
  Email: "Rok z GenActiv — jestes wyjatkowy!"
  Tresc: spersonalizowane podsumowanie, darmowy prezent
  CTA: [Odbierz prezent rocznicowy]
```

**Implementacja:** Trigger split na `rc_customer_charge_count` z warunkami equals 3, 6, 12.

#### Flow 6: Churn Risk Intervention

**Cel:** Proaktywna retencja zanim klient anuluje.

```
Wariant A (z Skio): Trigger: Churn Risk Score event (natywny)
Wariant B (z Recharge): Trigger: Segment-based (zbudowany z proxy)

Proxy churn risk (Recharge):
  - Pominagl 2+ zamowienia w ostatnich 90 dni
  - LUB zmienil czestotliwosc na dluzsza
  - LUB Klaviyo predicted churn > 66%

Day 0: Email 1 — "Chcemy się upewnić, że wszystko gra"
  Ton: osobisty, od zalożyciela
  Tresc: "Zauważyliśmy, że Twoja subskrypcja mogla się zmienić.
          Chcemy mieć pewność, że GenActiv Ci służy."
  CTA: [Opowiedz nam o swoim doswiadczeniu] → survey 3 pytania

Day 3: Email 2 — "Twoje opcje — dopasuj subskrypcje do siebie"
  Tresc: przedstaw opcje: zmien produkt, zmien czestotliwosc, pauzuj
  CTA: Quick Actions URLs do kazdej opcji

Day 7 (jeśli nie odpowiedzial): Email 3 — rabat retencyjny -20%
  CTA: [Zostań z -20% na nastepny cykl]
```

**Kluczowe:** Ten flow ma najwyzszy retention leverage — dociera do klienta ZANIM podejmie decyzje o anulowaniu.

#### Flow 7: Pause Winback

**Cel:** Reaktywacja zapauzowanych subskrypcji.

```
Trigger: Subscription paused on ReCharge

Day 0: Email 1 — "Twoja subskrypcja jest na pauzie"
  Tresc: potwierdzenie, przypomnienie o korzysciach, link do reaktywacji
  Ton: bez presji

Day 14: Email 2 — "Gotowy na powrót?"
  Tresc: "Twoje cialo potrzebuje regularnosci. Colostrum dziala najlepiej
          przy codziennym stosowaniu."
  CTA: [Reaktywuj subskrypcje] — Quick Actions URL

Day 30: Email 3 — "Wracaj z bomusem"
  Tresc: rabat reaktywacyjny -15%
  CTA: [Wznów i zaoszczedz]
```

#### Flow 8: Cancellation Save + Winback

**Cel:** Ostatnia szansa przed anulowaniem + winback po anulowaniu.

```
Trigger: Subscription cancelled on ReCharge

FAZA 1: SAVE (dzien 0-3)

Day 0: Email 1 — "Przykro nam, że odchodzisz"
  Conditional Split na cancellation reason:

  "Za drogo" → Email z kodem -20% na reaktywacje
  "Za duzo produktu" → Email z propozycja mniejszego formatu lub rzadszej dostawy
  "Nie widze efektow" → Email edukacyjny (timeline efektow, badania)
  "Inny powod" → Email z survey + osobisty kontakt CX

Day 3: Email 2 — "Twoje konto subskrypcji czeka"
  CTA: [Reaktywuj jednym kliknieciem] — Recharge Quick Actions

FAZA 2: WINBACK (dzien 14-90)

Day 14: Email 3 — "Tesknimy za Tobą"
  Tresc: social proof, nowe produkty/funkcje
  CTA: [Wróc do GenActiv]

Day 30: Email 4 — "Specjalny rabat powitalny -25%"
  CTA: [Reaktywuj z rabatem]

Day 60: Email 5 — Personalny email od załozycielki/eksperta
  Tresc: "Czy jest cos, co mozemy zrobic lepiej?"
  CTA: [Porozmawiaj z nami]

Day 90: Final — "Ostatnia wiadomosc od nas"
  Tresc: pożegnanie + link "gdybys zmienil zdanie"
```

**Routing do CX team:** Dla powodow "frustracja" lub "reklamacja" — trigger webhook do Teams/Slack z danymi klienta. CX dzwoni w ciagu 24h.

### 3.3 Flow subscription upsell (konwersja one-time → subscriber)

```
Trigger: Placed Order (Shopify)
Flow Filter:
  - Placed Order >= 2 since beginning (min. 2. zakup)
  - rc_active_subscription_count = 0 (nie jest subskrybentem)

Day 5: Email 1 — "Zaoszczedz 10% na kazdym zamowieniu"
  Tresc: kalkulator oszczednosci (12 mies × cena × 10% = PLN X zaoszczedzone)
  CTA: [Zasubskrybuj i oszczedzaj]

Day 12: Email 2 — "Dlatego 2000+ klientow wybiera subskrypcje"
  Tresc: social proof, testimoniale subskrybentow
  CTA: [Dolacz do nich]

Day 20: Email 3 — "Tylko dla Ciebie: -15% na pierwsza subskrypcje"
  Tresc: ekskluzywny rabat na start subskrypcji
  CTA: [Aktywuj -15%]
```

---

## 4. Segmentacja subskrypcyjna

### 4.1 Segmenty do stworzenia w Klaviyo

| # | Nazwa segmentu | Definicja (Klaviyo) | Zastosowanie |
|---|---------------|---------------------|-------------|
| S1 | Aktywni subskrybenci | `rc_active_subscription_count > 0` | Wykluczenie z replenishment, upsell do sub |
| S2 | Jednorazowi kupujacy (sub-ready) | Placed Order >= 2 AND `rc_active_subscription_count = 0` | Subscription upsell flow |
| S3 | Subskrybenci — 1. cykl | `rc_customer_charge_count = 1` AND `rc_active_subscription_count > 0` | Sub Welcome, early churn prevention |
| S4 | Subskrybenci — lojalni (6+ cykli) | `rc_customer_charge_count >= 6` | Milestone, referral ask, VIP |
| S5 | Churn risk (subskrypcja) | Predicted churn > 66% AND `rc_active_subscription_count > 0` | Churn Risk Intervention flow |
| S6 | Zapauzowani | `Subscription paused on ReCharge` in last 90 days AND `rc_active_subscription_count = 0` | Pause Winback flow |
| S7 | Anulowani (winback window) | `Subscription cancelled on ReCharge` in last 90 days | Cancel Winback flow |
| S8 | High-value subscribers | `rc_active_subscription_count > 0` AND Predicted CLV > top 20% | VIP treatment, early access |
| S9 | Sub: Colostrum only | `Recharge Subscriptions` contains "Colostrum" | Cross-sell Fiberbiom |
| S10 | Sub: Fiberbiom only | `Recharge Subscriptions` contains "Fiberbiom" | Cross-sell Colostrum |
| S11 | Sub tenure: 0-3 mies | `rc_customer_charge_count` between 1-3 | Early retention content |
| S12 | Sub tenure: 3-12 mies | `rc_customer_charge_count` between 4-12 | Loyalty building, referral |
| S13 | Sub tenure: 12+ mies | `rc_customer_charge_count >= 13` | Anniversary, ambassador program |
| S14 | Multi-product subscribers | `rc_active_subscription_count >= 2` | Highest value, VIP tier |

### 4.2 RFM w kontekscie subskrypcji

Obecny setup RFM GenActiv (custom MCP `klaviyo-mcp/server.py`, metryka `R6aTMS`) jest kompatybilny z segmentacja subskrypcyjna. Rozszerzenie:

```
RFM Standard (obecny)          +  Sub Layer (nowy)
───────────────────────           ─────────────────────
Champions                        Champions + Active Sub → VIP Ambassador
Champions                        Champions + No Sub → Sub Upsell Target
Loyal                            Loyal + Active Sub → Cross-sell
Loyal                            Loyal + No Sub → High-priority Sub Convert
At Risk                          At Risk + Active Sub → Churn Risk Intervention
At Risk                          At Risk + No Sub → Winback + Sub Offer
```

Kombinacja RFM group + subscription status tworzy precyzyjne segmenty z roznymi komunikatami i ofertami.

---

## 5. Analityka predykcyjna

### 5.1 Dostepne modele w Klaviyo

| Model | Wymagania | Status GenActiv | Zastosowanie sub |
|-------|-----------|----------------|-----------------|
| Predicted CLV | 500+ klientow, 180d historii, 3+ zakupy | Spelnione | LTV subskrybent vs jednorazowy |
| Churn Risk | Jak wyzej | Spelnione | Proaktywna retencja |
| Expected Date of Next Order (EDNO) | Jak wyzej | Spelnione | Replenishment timing |
| Predicted Gender | Email + name data | Spelnione | Personalizacja |
| Predicted AOV | Historyczne zamowienia | Spelnione | Upsell kalkulacja |

### 5.2 CLV: subskrybenci vs jednorazowi

Klaviyo automatycznie buduje model CLV i retrenuje go co najmniej raz w tygodniu. Po wdrozeniu subskrypcji:

- **Subskrybenci** beda mieli 2.5-3x wyzsze predicted CLV niz jednorazowi (benchmark branzy suplementowej)
- Mozna tworzyc segmenty: `Predicted CLV > PLN X AND rc_active_subscription_count > 0`
- Raportowanie: porownanie kohort subskrybentow vs nie-subskrybentow

### 5.3 Churn prediction — implementacja

Klaviyo klasyfikuje churn risk w 3 pasma:
- **Low:** < 33% prawdopodobienstwo braku zakupu w 90 dni
- **Medium:** 33-66%
- **High:** > 66%

Model retrenuje sie co najmniej raz w tygodniu.

**Flow na bazie churn:**
1. Segment: `Predicted churn risk = High AND rc_active_subscription_count > 0`
2. Flow trigger: profil wchodzi do segmentu (transition trigger)
3. Sekwencja: survey → opcje → rabat retencyjny

### 5.4 EDNO — zastosowanie hybrydowe

**Rekomendacja:** Uzyj EDNO dla klientow po 1. zakupie (brak wystarczajacych danych do replenishment timing), ale opieraj replenishment flow na znanych cyklach zuzycia produktu (30/60 dni) dla stałych klientow.

```
1. zakup → EDNO flow (Klaviyo predictive)
2+ zakupy → Product-specific replenishment flow (znany timing)
Subskrybent → Brak replenishment (subskrypcja obsluguje)
```

---

## 6. SMS + Email — orkiestracja (Polska, RODO)

### 6.1 Regulacje prawne

| Wymog | Szczegoly | Implementacja |
|-------|----------|--------------|
| RODO Art. 6(1)(a) | Zgoda dobrowolna, konkretna, swiadoma, jednoznaczna | Osobny checkbox SMS |
| RODO Art. 7 | Pre-ticked boxes zakazane, bundled consent zakazany | Oddzielne checkboxy email + SMS |
| Prawo Telekomunikacyjne Art. 398 | Zgoda uprzednia na marketing elektroniczny (email, SMS) | Double opt-in |
| UODO (2026 plan inspekcji) | Kontrole podmiotow marketingowych | Dokumentacja zgod |
| Kary | Do 3% przychodu (PL) lub 4% obrotu / 20M EUR (RODO) | Pelna compliance |

### 6.2 Implementacja SMS w Klaviyo (PL)

**Dostepnosc:** Polska jest na liscie krajow obsługiwanych przez Klaviyo SMS.

**Zbieranie zgod:**
```
Formularz zapisu (popup / checkout):

☐ Chce otrzymywac newslettery email od GenActiv
    (obowiazkowe dla email flow)

☐ Chce otrzymywac powiadomienia SMS od GenActiv
    (opcjonalne, osobny checkbox)
    "Wyrazam zgode na otrzymywanie wiadomosci SMS marketingowych
     od GenActiv sp. z o.o. Moge wycofac zgode w kazdej chwili
     odpowiadajac STOP. Regulamin: [link]"
```

**Double opt-in SMS:**
1. Uzytkownik zaznacza checkbox → wpisuje numer (+48...)
2. Klaviyo wysyla SMS potwierdzajacy: "Odpowiedz TAK aby potwierdzic"
3. Po potwierdzeniu: status = Subscribed (SMS)

### 6.3 SMS w cyklu subskrypcyjnym

| Flow | Email | SMS | Uzasadnienie |
|------|-------|-----|-------------|
| Sub Welcome | 4 emaile | 1 SMS (Day 0) | Potwierdzenie natychmiastowe |
| Upcoming Charge | 1 email | 1 SMS (Day -1) | Reminder, link do portalu |
| Dunning | 3 emaile | 1 SMS po Email 2 | Pilnosc, wyzszy open rate |
| Churn Risk | 3 emaile | 0 SMS | Zbyt agresywne przez SMS |
| Pause Winback | 3 emaile | 1 SMS (Day 30) | Rabat reaktywacyjny |
| Cancel Winback | 5 emaili | 1 SMS (Day 14) | Osobisty ton |
| Cross-sell | 1 email | 0 SMS | Zbyt promocyjne |
| Milestone | 1 email | 1 SMS | Celebracja |

**Uwaga:** SMS transakcyjne (potwierdzenie zamowienia subskrypcji, zmiana statusu) moga nie wymagac marketingowej zgody — ale rekomendujemy konsultacje z prawnikiem w kontekscie polskich przepisow.

### 6.4 SMS pilot — plan

Zgodnie z roadmapa (sierpien 2026):
1. **Cel:** 500 numerow, 15% CTR
2. **Start:** Porzucony koszyk SMS + flash sale
3. **Rozszerzenie:** Subskrypcyjne SMS po wdrozeniu Recharge (wrzesien)
4. **Compliance:** RODO audit przed startem, double opt-in, dokumentacja

---

## 7. Raportowanie i atrybucja

### 7.1 Natywne mozliwosci Klaviyo

| Raport | Opis | Ograniczenia |
|--------|------|-------------|
| Revenue per Flow | Przychod przypisany do kazdego flow | Sub revenue moze byc over-attributed |
| Revenue per Recipient (RPR) | Przychod / liczba odbiorcow | Kluczowa metryka cross-flow |
| Flow Conversion Rate | % odbiorcow, ktorzy kupili | Segmentowalny |
| CLV Dashboard | Predykcja + historyczne CLV | Wymaga KDP subscription ($) |
| Cohort Analysis | Grupowanie po dacie akwizycji | Reczne, wymaga segmentow |
| RFM Report | Rozkład klientow po RFM | Natywny w Klaviyo |

### 7.2 Znane ograniczenie: over-attribution subskrypcji

Klaviyo przypisuje 100% przychodu subskrypcyjnego z Recharge do flow, nawet jesli klient nie otworzyl emaila. To zawyza wyniki flow subskrypcyjnych.

**Obejscie:**
1. Monitoruj RPR zamiast totalnego revenue — znormalizowana metryka
2. Porownuj conversion rate (nie revenue) miedzy flow
3. Rozważ narzedzie external attribution (Attribution.com, Wicked Reports) do dokladnego trackingu recurring revenue

### 7.3 Kluczowe KPI subskrypcyjne do trackowania

| KPI | Definicja | Target GenActiv | Zrodlo danych |
|-----|----------|-----------------|---------------|
| Subscription conversion rate | % kupujacych → subskrybentow | 5% (gru 2026) | Recharge + Klaviyo |
| First-cycle retention | % subskrybentow utrzymanych po 1. cyklu | >80% | Recharge analytics |
| Involuntary churn rate | % utraconych przez platnosc | <5% | Recharge + dunning flow |
| Voluntary churn rate | % swiadomych anulowań | <8% | Recharge + cancel flow |
| Dunning recovery rate | % odzyskanych po payment failed | >40% | Klaviyo dunning flow metrics |
| Subscription AOV | Srednia wartosc zamowienia sub | PLN 150+ | Recharge |
| MRR (Monthly Recurring Revenue) | Miesieczny przychod subskrypcyjny | PLN 33K (baseline) | Recharge |
| Sub email revenue share | % przychodu email z sub flow | 8-15% | Klaviyo |

### 7.4 Kohortowa analiza subskrybentow

Klaviyo nie ma natywnego "subscription cohort" raportu. Implementacja:

1. **Segmenty kohortowe:** Twórz miesieczne segmenty "Sub started: August 2026", "Sub started: September 2026" etc.
2. **Custom reports:** Porownuj retention kazdej kohorty po 30, 60, 90, 180 dniach
3. **External:** Recharge dashboard ma natywna kohortowa analize retencji

---

## 8. Best practices — branza suplementow

### 8.1 Benchmark: ARMRA (colostrum, ~$150M/rok)

ARMRA — najwiekszy DTC brand colostrumowy na swiecie — stosuje:
- Subscribe & Save z -15% rabatem
- Formatowe warianty (stick packs, proszek) w ramach subskrypcji
- Content-driven acquisition (influencerzy, TikTok)
- Email edukacyjny > email promocyjny (stosunek 6:2)

### 8.2 Strategie subskrypcyjne dla suplementow konsumowanych

| Strategia | Opis | Wplyw |
|----------|------|-------|
| **Education-first onboarding** | 3 emaile edukacyjne przed 1. sub upsell | +20% first-cycle retention |
| **Replenishment before subscription** | Przypomnienia o uzupelnieniu buduja nawyk | +30-40% repeat |
| **Subscription as default, not add-on** | Subskrypcja = glowna oferta na PDP | +15-25% sub conversion |
| **Pause > Cancel** | Oferuj pauze przed opcja anulowania | -38% churn (Recurly 2026) |
| **Cancellation reason routing** | Rozne odpowiedzi wg powodu | +10-20% save rate |
| **Tiered discounts** | Sub 1 prod = -10%, 2 = -12%, 3+ = -15% | +25% AOV sub |
| **Milestone celebration** | Co 3 miesiace gratulacje + prezent | +15% tenure |
| **Cross-sell at cycle 2-3** | Nie przy 1. cyklu, poczekaj na zaufanie | +20% items/order |

### 8.3 Specyfika GenActiv — rekomendacje

| Produkt | Cykl zuzycia | Sub rabat | Cross-sell par |
|---------|-------------|-----------|---------------|
| Colostrum 120 kaps | 60 dni | -10% | + Fiberbiom |
| Colostrum 60 kaps | 30 dni | -10% | + Proszek (upgrade) |
| Colostrum Proszek | 30 dni | -10% | + Fiberbiom |
| Colostrum saszetki | 30 dni | -10% | + Kapsulki (upgrade) |
| Fiberbiom | 30 dni | -10% | + Colostrum |
| Dwupak Colostrum | 60 dni | -12% | + Fiberbiom |

**Kluczowe pary cross-sell:**
1. Colostrum + Fiberbiom (odpornosc + trawienie)
2. Kapsulki 60 → Kapsulki 120 (upsell na wiekszy format)
3. Dowolny Colostrum + dowolny Fiberbiom (rodzina produktow)

### 8.4 Propozycja struktury rabatowej

```
Jednorazowy zakup:         100% ceny
Subskrypcja 1 produkt:     -10% (standard)
Subskrypcja 2 produkty:    -12%
Subskrypcja 3+ produktow:  -15%

Sub + roczna platnosc:     -20% (prepaid annual)

Rabaty retencyjne (one-time):
  Churn risk:              -20% na nastepny cykl
  Pause > 30 dni:          -15% na reaktywacje
  Cancelled < 30 dni:      -20% na powrot
  Cancelled 30-90 dni:     -25% na powrot
```

---

## 9. Rekomendacja platformy subskrypcyjnej

### 9.1 Scoring decyzyjny

| Kryterium | Waga | Recharge | Skio | Bold | Shopify Native |
|-----------|------|----------|------|------|---------------|
| Integracja z Klaviyo | 25% | 9/10 | 10/10 | 5/10 | 3/10 |
| Cena (przy wolumenie GenActiv) | 20% | 9/10 | 4/10 | 8/10 | 10/10 |
| Customer Portal UX | 15% | 8/10 | 10/10 | 6/10 | 5/10 |
| Dunning / churn tools | 15% | 8/10 | 9/10 | 5/10 | 3/10 |
| PLN / Shopify Markets | 10% | 9/10 | 9/10 | 7/10 | 10/10 |
| Ekosystem / community | 10% | 10/10 | 7/10 | 6/10 | 8/10 |
| Skalowalnose | 5% | 10/10 | 9/10 | 6/10 | 5/10 |
| **TOTAL** | 100% | **8.8** | **8.1** | **5.9** | **5.8** |

### 9.2 Rekomendacja: Recharge (Starter Plan)

**Dlaczego Recharge:**

1. **Najlepsza natywna integracja z Klaviyo** — 9+ eventow subskrypcyjnych, rc_* profile properties, Quick Actions URLs
2. **Cena adekwatna do wolumenu** — $99/mies + 1.49% na start, 60-dniowy trial
3. **PLN support** — automatycznie przez Shopify Markets
4. **Najszerszy ekosystem** — najwiecej dokumentacji, community, agencji
5. **Skalowalnosc** — od $99 do custom enterprise
6. **Recharge kupilo Skio** — konsolidacja rynku, Recharge to bezpieczniejszy wybor dlugoterminowo

**Dlaczego nie Skio:**
- $599/mies to 6x wiecej niz Recharge przy zerowej bazie subskrybentow
- Natywny churn score i revenue separation sa wartoosciowe, ale mozna je emulowac w Recharge + Klaviyo
- Po akwizycji przez Recharge ($105M, kwiecien 2026) — przyszlosc platformy niepewna

**Dlaczego nie Bold:**
- Slaba integracja z Klaviyo (API-based, nie natywna)
- Brak churn tools, ograniczone analityki
- Mniejszy ekosystem

**Dlaczego nie Shopify Native:**
- Brak natywnej integracji z Klaviyo dla eventow subskrypcyjnych
- Brak cancel flow / save offers
- Brak zaawansowanego customer portal

### 9.3 Kalkulacja kosztow Recharge (GenActiv)

```
Zalozenia (6 mies po starcie):
  Subskrybenci: 200-300
  Zamowienia sub/mies: ~250
  Sredni AOV sub: PLN 150 (~$37 USD)

Koszt miesieczny:
  Base:        $99.00
  1.49%:       250 × $37 × 1.49% = $137.83
  $0.19/order: 250 × $0.19 = $47.50
  ────────────────────────────────────
  TOTAL:       ~$284/mies (~PLN 1,130/mies)

  vs przychod sub:     250 × PLN 150 = PLN 37,500/mies
  Koszt platformy:     3.0% przychodu sub
```

---

## 10. Roadmapa wdrozenia

### Faza 0: PRE-SUBSCRIPTION (Lipiec 2026 — TERAZ)

| Tydzien | Zadanie | Odpowiedzialnosc |
|---------|---------|-------------------|
| W3 (lip) | Replenishment flow setup (3 sciezki produktowe) | CC (Klaviyo) |
| W3 (lip) | EDNO flow dla 1-zakupowych | CC (Klaviyo) |
| W4 (lip) | Subscription Upsell flow (draft) | CC (Klaviyo) |
| W4 (lip) | Research Recharge — finalny go/no-go | CC+ (decyzja biznesowa) |

### Faza 1: FUNDAMENT (Sierpien 2026)

| Tydzien | Zadanie | Odpowiedzialnosc |
|---------|---------|-------------------|
| W1 (sie) | Instalacja Recharge + konfiguracja Shopify | DEV |
| W1 (sie) | Selling plans: top 3 produkty (120 kaps, Fiberbiom, Proszek) | DEV + BIZNES |
| W1 (sie) | Recharge ↔ Klaviyo integracja (enable + backfill) | CC |
| W2 (sie) | Sub Welcome flow (4 emaile) | CC |
| W2 (sie) | Upcoming Charge Notification flow | CC |
| W3 (sie) | Dunning flow (3 emaile) | CC |
| W3 (sie) | Segmenty S1-S6 (core subscription segments) | CC |
| W4 (sie) | QA + soft launch (top 100 klientow) | CC+ |

### Faza 2: RETENCJA (Wrzesien 2026)

| Tydzien | Zadanie | Odpowiedzialnosc |
|---------|---------|-------------------|
| W1 (wrz) | Subscription Upsell flow (live) | CC |
| W1 (wrz) | Pause Winback flow | CC |
| W2 (wrz) | Cancel Save + Winback flow | CC |
| W2 (wrz) | Cross-sell within subscription flow | CC |
| W3 (wrz) | Churn Risk Intervention flow (proxy-based) | CC |
| W3 (wrz) | Segmenty S7-S14 (advanced) | CC |
| W4 (wrz) | SMS pilot: sub notifications (upcoming charge, dunning) | CC + PRAWNIK |

### Faza 3: OPTYMALIZACJA (Pazdziernik-Grudzien 2026)

| Miesiac | Zadanie | Odpowiedzialnosc |
|---------|---------|-------------------|
| Paz | Milestone/Anniversary flow | CC |
| Paz | A/B testy: subject lines, timing, rabaty | CC |
| Paz | RFM + Sub layer segmentacja | CC |
| Lis | Pre-BF: sub +5% extra rabat | CC + BIZNES |
| Lis | Post-BF: konwersja jednorazowych → sub | CC |
| Gru | Loyalty launch integration | CC + DEV |
| Gru | Roczna analiza: kohorty, retention, CLV | CC |

### Priorytety (wplyw na przychod)

```
PRIORITY 1 (Revenue Protection — wdrozyc w 1. miesiacu):
  ┌────────────────────────────────────────────┐
  │ 1. Dunning flow          → -20-40% inv.churn │
  │ 2. Upcoming Charge       → -15% vol.churn    │
  │ 3. Sub Welcome           → +20% 1st retention│
  │ 4. Replenishment (pre-sub)→ +30% repeat      │
  └────────────────────────────────────────────┘

PRIORITY 2 (Revenue Growth — wdrozyc w 2. miesiacu):
  ┌────────────────────────────────────────────┐
  │ 5. Sub Upsell            → konwersja one-time │
  │ 6. Cancel Save/Winback   → +10-20% save rate  │
  │ 7. Pause Winback         → -38% vol.churn     │
  └────────────────────────────────────────────┘

PRIORITY 3 (Revenue Expansion — wdrozyc w 3. miesiacu):
  ┌────────────────────────────────────────────┐
  │ 8. Cross-sell             → +20% AOV sub      │
  │ 9. Churn Risk Intervention→ proaktywna retencja│
  │ 10. Milestone/Anniversary → tenure +15%        │
  └────────────────────────────────────────────┘
```

### Szacowany wplyw na KPI

| KPI | Bez subskrypcji (lip 2026) | Z subskrypcja (gru 2026) | Delta |
|-----|---------------------------|--------------------------|-------|
| Sub adoption | 0% | 5% | +5pp |
| MRR | PLN 0 | PLN 33K | +PLN 33K |
| Email revenue share | 5.1% | 12% | +6.9pp |
| Repeat rate | 55% | 62% | +7pp |
| Active flows | 5 | 14 | +9 |
| Dunning recovery | n/a | 40% | baseline |
| 1st-cycle retention | n/a | 80% | baseline |

---

## 11. Zrodla

### Integracje i platformy subskrypcyjne
- [Tribe Studio — Klaviyo Flows for Subscription Brands](https://tribe.studio/insights/best-practice-klaviyo-flows-for-subscription-brands)
- [Tribe Studio — Klaviyo Email Marketing for Subscription Brands](https://tribe.studio/insights/klaviyo-email-marketing-subscription-brands)
- [Skio — Klaviyo Integration](https://help.skio.com/hc/en-us/articles/16802652263323-Klaviyo-Integration)
- [Skio — Event and Profile Properties in Klaviyo](https://help.skio.com/docs/skio-event-and-profile-properties-in-klaviyo)
- [Recharge — Metrics and Klaviyo Flows](https://support.getrecharge.com/hc/en-us/articles/9828306941207-Recharge-metrics-and-Klaviyo-flows)
- [Recharge — Custom Properties in Klaviyo](https://support.getrecharge.com/hc/en-us/articles/19455777058583-Using-Recharge-custom-properties-in-Klaviyo-for-segmentation-and-campaigns)
- [Recharge — Klaviyo Use Cases](https://support.getrecharge.com/hc/en-us/articles/4405551381143-Recharge-and-Klaviyo-use-cases)
- [Klaviyo — Customer Hub Subscription Connection](https://help.klaviyo.com/hc/en-us/articles/39786250669083)
- [Eightx — Recharge vs Smartrr vs Skio Fee Comparison (2026)](https://eightx.co/blog/recharge-vs-smartrr-vs-skio-subscriptions)
- [Recharge — Pricing](https://getrecharge.com/pricing/)

### Dunning, flow i retencja
- [Ordergroove — Klaviyo Dunning Best Practices](https://help.ordergroove.com/hc/en-us/articles/35620338909971-Klaviyo-Dunning-Best-Practices)
- [Stay AI — Failed Billing Metrics in Klaviyo](https://help.retextion.com/en/articles/10150248-understanding-failed-billing-metrics-klaviyo)
- [GOSH Digital — Complete Klaviyo Guide for 2026](https://www.goshdigital.co/blog/klaviyo-2026-complete-guide)
- [Skio — Creating Winback Flows in Klaviyo](https://help.skio.com/docs/creating-winback-flows-in-klaviyo)

### Analityka predykcyjna
- [Klaviyo — Understanding Predictive Analytics](https://help.klaviyo.com/hc/en-us/articles/360020919731)
- [Klaviyo — CLV Dashboard](https://help.klaviyo.com/hc/en-us/articles/17797865070235)
- [Klaviyo — Churn Prediction Model](https://www.klaviyo.com/blog/predicting-churn-risk-our-new-model)
- [Stormy AI — Klaviyo Predictive Analytics CLV Strategy](https://stormy.ai/blog/klaviyo-predictive-analytics-clv-strategy)
- [Klaviyo — RFM Analysis Report](https://help.klaviyo.com/hc/en-us/articles/17797889315355)

### Replenishment
- [Klaviyo — How to Create a Replenishment Flow](https://help.klaviyo.com/hc/en-us/articles/360003195232)
- [Klaviyo Blog — Replenishment Email Flow](https://www.klaviyo.com/blog/the-email-automation-all-consumable-goods-brands-need-that-many-dont-yet-use)
- [BS&Co — Replenishment Flow Timing](https://bsandco.us/blog-post/replenishment-flow-klaviyo)

### SMS i RODO
- [Klaviyo — GDPR and SMS in Europe](https://help.klaviyo.com/hc/en-us/articles/18410569130779)
- [Recording Law — Poland Data Privacy Laws 2026](https://www.recordinglaw.com/world-laws/world-data-privacy-laws/poland-data-privacy-laws/)
- [GOSH Digital — Klaviyo Consent Management 2026](https://www.goshdigital.co/blog/klaviyo-consent-management)

### Branza suplementow
- [PATI Group — ARMRA Colostrum Revolution](https://www.patigroup.com/p/armras-colostrum-revolution-how-a)
- [ATTN Agency — Supplement Subscription Optimization](https://www.attnagency.com/blog/supplement-subscription-optimization)
- [AAKAR Studio — Supplement Retention Marketing Strategy](https://aakar.studio/blog/supplement-retention-marketing-strategy)
- [YOCTO Agency — Supplement Brand Email Revenue +368%](https://yocto.agency/case-studies/boosted-supplement-brands-email-revenue-in-4-months/)

### Raportowanie i atrybucja
- [Klaviyo — Revenue Attribution](https://help.klaviyo.com/hc/en-us/articles/115000713811)
- [Attribution — Klaviyo LTV Analytics](https://www.attributionapp.com/plans/klaviyo/)
- [Wicked Reports — Klaviyo Attribution](https://www.wickedreports.com/klaviyo)

---

*Raport wygenerowany automatycznie. Rekomendacje oparte na publicznie dostepnej dokumentacji i best practices. Konsultacja prawna (RODO/SMS) oraz biznesowa (pricing, product selection) wymagana przed wdrozeniem.*

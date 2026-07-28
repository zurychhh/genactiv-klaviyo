# Genactiv Onboarding — Plan emailowy

> Ostatnia aktualizacja: 2026-06-23
> Status: 20/20 szablonow v3 w Klaviyo + 2 flow Draft (UNETEK, R7q8bj) · audyt benchmarkowy wdrozony

---

## Spis tresci

1. [Architektura flow](#architektura-flow)
2. [Szablony Klaviyo — nazwy i ID](#szablony-klaviyo)
3. [Tytuly i preheadery](#tytuly-i-preheadery)
4. [Tresc maili — PUR (po zakupie)](#pur-po-zakupie)
5. [Tresc maili — NUR (bez zakupu)](#nur-bez-zakupu)
6. [Zasoby graficzne](#zasoby-graficzne)
7. [Logika techniczna](#logika-techniczna)

---

## Architektura flow

### v3: Dwa niezalezne flow (wdrozone przez API 2026-06-23)

```
FLOW B — Post-Purchase Onboarding v3 [ID: UNETEK]
https://www.klaviyo.com/flow/UNETEK/edit
Trigger: Metric "Placed Order"
Flow Filter: Placed Order = 1 (since beginning of time)
Re-entry: Once per profile | Smart Sending: ON | Rynek: PL/PLN

  Probka losowa 50/50 (sticky)
    /              \
  A(Bold)       B(Edit.)
    |               |
  Krok 1 (0)      Krok 1 (0)
  Krok 2 (+3d)    Krok 2 (+3d)
  Krok 3 (+4d)    Krok 3 (+4d)
  Krok 4 (+5d)    Krok 4 (+5d)
  Krok 5 (+7d)    Krok 5 (+7d)


FLOW A — Newsletter Nurture v3 [ID: R7q8bj]
https://www.klaviyo.com/flow/R7q8bj/edit
Trigger: Added to list "Shopify Newsletter" (VT3KTz)
Flow Filter: Placed Order = 0 (since beginning of time)
  → re-ewaluuje przy kazdym opoznieniu = kupujacy wypada
Conditional Split przed Krok 4 i 5:
  Placed Order since flow start = 0 → TAK: wyslij | NIE: skip to exit
Re-entry: Once per profile | Smart Sending: ON

  Probka losowa 50/50 (sticky)
    /              \
  A(Bold)       B(Edit.)
    |               |
  Krok 1 (0)      Krok 1 (0)
  Krok 2 (+1d)    Krok 2 (+1d)
  Krok 3 (+2d)    Krok 3 (+2d)
  [Split] ------> [Split]
  Krok 4 (+2d)    Krok 4 (+2d)
  [Split] ------> [Split]
  Krok 5 (+2d)    Krok 5 (+2d)
```

### Opoznienia miedzy krokami

**PUR (post-purchase):** 0 → +3 dni → +4 dni → +5 dni → +7 dni
**NUR (newsletter):** 0 → +1 dzien → +2 dni → +2 dni → +2 dni

### A/B test

- Wariant A = Bold (czerwony header, left-aligned, full-width CTA, ciemny footer)
- Wariant B = Editorial (jasny header, centered, inline CTA, jasny footer)
- Probka losowa 50/50, sticky (odbiorca zawsze dostaje ten sam wariant)
- Tytuly i preheadery identyczne w A i B — testujemy wylacznie layout

---

## Szablony Klaviyo

### PUR (po zakupie) — AKTUALNE (v3)

```
Onboarding | Krok 1 | Welcome (Bold) v3         → QUdmFC
Onboarding | Krok 1 | Welcome (Editorial) v3     → WpiLDb
Onboarding | Krok 2 | Ritual (Bold) v3           → VqkWwP
Onboarding | Krok 2 | Ritual (Editorial) v3      → UnLSdA
Onboarding | Krok 3 | Effects (Bold) v3          → TWN6qP
Onboarding | Krok 3 | Effects (Editorial) v3     → Ww5M8y
Onboarding | Krok 4 | Cross-sell (Bold) v3       → XJG8fD
Onboarding | Krok 4 | Cross-sell (Editorial) v3  → XvpBfP
Onboarding | Krok 5 | Loyalty (Bold) v3          → RQNrA3
Onboarding | Krok 5 | Loyalty (Editorial) v3     → UJB9Fk
```

### NUR (bez zakupu) — AKTUALNE (v3)

```
Onboarding NUR | Krok 1 | Welcome (Bold) v3         → UqrSmc
Onboarding NUR | Krok 1 | Welcome (Editorial) v3     → WV7iS4
Onboarding NUR | Krok 2 | Education (Bold) v3        → WWhNWL
Onboarding NUR | Krok 2 | Education (Editorial) v3   → Yfxqrf
Onboarding NUR | Krok 3 | Social Proof (Bold) v3     → URHUe9
Onboarding NUR | Krok 3 | Social Proof (Editorial) v3 → SSBKUH
Onboarding NUR | Krok 4 | Reminder (Bold) v3         → Xsc72A
Onboarding NUR | Krok 4 | Reminder (Editorial) v3    → UarBh3
Onboarding NUR | Krok 5 | Last Call (Bold) v3        → T6fgLV
Onboarding NUR | Krok 5 | Last Call (Editorial) v3   → VY3YSe
```

### Stare szablony v2 (do usuniecia — bledne ceny/tresc)

```
PUR: TbkrJT, XRz3kF, VUtTbL, WHkGxx, TAQHuL, V9Y5Zr, UCbxLy, Yb2iCZ, XXJMMG, WVzts7
NUR: WZHHPD, V22jtR, WP3t2G, UE5xY8, RxzyVm, Y8Sixx, WAVs7A, TB5HyJ, VPf8Qx, XcwJC4
```

### Stare szablony v1 (do usuniecia — blad `<link>`)

```
PUR: RwFzuN, U732hM, WS4XRc, XEVMcX, RSvQWy, Xp322g, RVHmbM, QWah35, WF9t2N, TVbvw8
NUR: TmXt8z, TzQe2e, SkpnPk, S97RY3, WwQskL, VYsE5x, R9yMPj, RpsyRv, UmSxic, SE5U97
```

---

## Tytuly i preheadery

Jeden tytul i preheader na krok (identyczny dla wariantu A i B).

### PUR

**Krok 1 — Welcome**
Tytul: Dobry wybor, {{ first_name|default:'' }}!
Preheader: Zamowienie przyjete — witaj w planie na zdrowie

**Krok 2 — Ritual**
Tytul: 3 kroki, by Colostrum dzialalo najlepiej
Preheader: Rano, na czczo, codziennie — tak dziala rytm

**Krok 3 — Effects**
Tytul: Twoje 8 tygodni z Colostrum
Preheader: Czego sie spodziewac tydzien po tygodniu

**Krok 4 — Cross-sell**
Tytul: Dodaj rytm swoim jelitom
Preheader: Colostrum dba o odpornosc. Czas zadbac o jelita

**Krok 5 — Loyalty**
Tytul: Zdrowie calej rodziny
Preheader: Poznaj caly plan na zdrowie — dla Ciebie, bliskich, skory i pupila

### NUR

**Krok 1 — Welcome**
Tytul: Twoj −15% na start
Preheader: Witaj w Genactiv — masz kod na pierwsze zamowienie

**Krok 2 — Education**
Tytul: Dlaczego colostrum?
Preheader: 250 aktywnych skladnikow w jednej substancji

**Krok 3 — Social Proof**
Tytul: Nr 1 w aptekach w Polsce
Preheader: Zaufaly nam tysiace polskich rodzin

**Krok 4 — Reminder**
Tytul: Twoj kod −15% wciaz czeka
Preheader: Zostalo 48 godzin — nie przegap START15

**Krok 5 — Last Call**
Tytul: Kod −15% znika dzis o polnocy
Preheader: Ostatnia szansa na START15 — zacznij swoj plan na zdrowie

---

## PUR (po zakupie)

### Krok 1 — Welcome

#### Wariant A (Bold) · `PurOnb1A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Order strip → CTA → Benefits → Footer ciemny

- Krok: 1 / 5
- Eyebrow: WITAJ W GENACTIV®
- H1: Dobry wybor, {{ first_name|default:'Czesc' }}!
- Body: Dziekujemy za zaufanie. Wlasnie dolaczasz do tysiecy rodzin, ktore codziennie wspieraja odpornosc z Colostrum nr 1 w aptekach*. Twoje zamowienie jest juz w drodze — a my pomozemy Ci wycisnac z niego maksimum.
- Przypis: *wg IQVIA Poland Pharmascope, kategoria odpornosc, MAT 12/2024
- Order strip: Zamowienie przyjete — jest juz w drodze / Dostawa w 1–2 dni robocze
- CTA: Poznaj swoj plan na zdrowie → (genactiv.pl/plan?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_1_welcome_bold)
- Sekcja benefitow: SMAK / NATURALNOSC / FORMY PODANIA (z ikonami)
- Social: Facebook, Instagram, YouTube

#### Wariant B (Editorial) · `PurOnb1B.html`

**Struktura:** Header jasny → Step Rail → Hero image → Eyebrow → H1 → Body → Ritual steps → CTA → Trust line → Footer jasny

- Krok: 1 / 5
- Eyebrow: CIESZYMY SIE, ZE TU JESTES
- H1: Twoj plan na zdrowie wlasnie sie zaczal.
- Body: Czesc {{ first_name|default:'' }}, dziekujemy za pierwszy zakup. Zanim paczka dotrze, pokazemy Ci, jak najlepiej korzystac z Colostrum — krok po kroku.
- Hero: zdjecie produktu na czerwonym tle (230px, rounded)
- Ritual steps:
  1. Odstaw w widocznym miejscu — Najlepiej blisko porannej kawy — latwiej o regularnosc.
  2. Wez pierwsza porcje jutro rano — Na czczo, popij woda. Szczegoly w kolejnym mailu.
  3. Daj naturze rytm — Pierwsze efekty zwykle po kilku tygodniach systematycznosci.
- CTA: Zacznij swoj plan (genactiv.pl/plan?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_1_welcome)
- Trust line: ★★★★★ COLOSTRUM NR 1 W APTEKACH W POLSCE* · na odpornosc · zaufaly nam tysiace rodzin
- Przypis: *wg IQVIA Poland Pharmascope, kategoria odpornosc, MAT 12/2024

---

### Krok 2 — Ritual

#### Wariant A (Bold) · `PurOnb2A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Dosage box → Ritual steps → CTA → Footer ciemny

- Krok: 2 / 5
- Eyebrow: JAK STOSOWAC
- H1: Twoj rytual z Colostrum
- Body: To naprawde proste. Najwazniejsza jest regularnosc — bo natura lubi rytm. Oto jak wlaczyc Colostrum w swoj dzien:
- Dosage box: 1–2 kapsulki dziennie | Rano na czczo | Woda popij chlodna
- Ritual steps:
  1. Rano, zanim zjesz — Pusty zoladek = lepsze przyswajanie cennych skladnikow colostrum.
  2. Popij chlodna woda — Unikaj goracych napojow — wysoka temperatura nie sluzy aktywnym skladnikom.
  3. Codziennie, bez przerw — Systematycznosc przez min. 4–8 tygodni daje najlepszy efekt.
- CTA: Zobacz pelny poradnik stosowania → (genactiv.pl/jak-stosowac?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_2_ritual_bold)

#### Wariant B (Editorial) · `PurOnb2B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Ritual steps → Expert quote → CTA → Footer jasny

- Krok: 2 / 5
- Eyebrow: TWOJ PORANNY RYTUAL
- H1: Najlepsze efekty lubia rytm.
- Body: Colostrum nie potrzebuje wiele — potrzebuje regularnosci. Trzy spokojne kroki, ktore wystarczy powtarzac kazdego ranka.
- Ritual steps:
  1. Obudz sie i nawodnij — Szklanka wody na dobry poczatek dnia.
  2. 1–2 kapsulki na czczo — Zanim siegniesz po sniadanie — popij chlodna woda.
  3. Powtarzaj codziennie — Po kilku tygodniach rytm stanie sie nawykiem.
- Expert: „Colostrum dziala najlepiej, gdy stosujemy je systematycznie. To nie kuracja na kilka dni — to element codziennego planu na zdrowie." — Zdaniem ekspertow · na podstawie wiedzy dietetycznej
- CTA: Pelny poradnik stosowania (genactiv.pl/jak-stosowac?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_2_ritual)

---

### Krok 3 — Effects

#### Wariant A (Bold) · `PurOnb3A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Timeline → Expert quote → CTA → Footer ciemny

- Krok: 3 / 5
- Eyebrow: CZEGO SIE SPODZIEWAC
- H1: Twoje 8 tygodni z Colostrum
- Body: Natura potrzebuje czasu i rytmu. Oto jak zwykle wyglada droga, gdy stosujesz Colostrum systematycznie — krok po kroku.
- Timeline:
  1. Tydzien 1–2 · Budujesz rytm — Organizm przyzwyczaja sie do codziennej porcji. Najwazniejszy etap — nie odpuszczaj.
  2. Tydzien 3–4 · Pierwsze sygnaly — Wiele osob zauwaza poprawe samopoczucia w ciagu dnia.
  3. Tydzien 6–8 · Pelna moc planu — Wsparcie odpornosci dziala najlepiej przy konsekwencji. To Twoj nowy standard.
- Expert: „Colostrum to naturalne wsparcie bariery odpornosciowej. Kluczem jest regularnosc — efekty buduja sie tygodniami, nie dniami." — Zdaniem ekspertow · na podstawie badan z zakresu immunologii
- CTA: Dowiedz sie wiecej o colostrum → (genactiv.pl/colostrum?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_3_effects_bold)

#### Wariant B (Editorial) · `PurOnb3B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Timeline → Tip box → CTA → Footer jasny

- Krok: 3 / 5
- Eyebrow: CIERPLIWOSC SIE OPLACA
- H1: Natura potrzebuje rytmu.
- Body: Nie szukaj efektow po dwoch dniach. Prawdziwa zmiana w odpornosci buduje sie tygodniami — i wlasnie dlatego warto.
- Timeline:
  1. Tydzien 1–2 · Budujesz rytm — Organizm przyzwyczaja sie do codziennej porcji. Najwazniejszy etap — nie odpuszczaj.
  2. Tydzien 3–4 · Pierwsze sygnaly — Wiele osob zauwaza poprawe samopoczucia w ciagu dnia.
  3. Tydzien 6–8 · Pelna moc planu — Wsparcie odpornosci dziala najlepiej przy konsekwencji. To Twoj nowy standard.
- Tip box: Wskazowka: zaznacz w kalendarzu date za 4 tygodnie. To moment, w ktorym najczesciej widac pierwsze efekty.
- CTA: Poznaj nauke o colostrum (genactiv.pl/colostrum?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_3_effects)

---

### Krok 4 — Cross-sell (Fiberbiom)

#### Wariant A (Bold) · `PurOnb4A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Product card → Synergy note → CTA → Footer ciemny

- Krok: 4 / 5
- Eyebrow: TWOJ NASTEPNY KROK
- H1: Dodaj rytm swoim jelitom
- Body: Colostrum buduje Twoja odpornosc. Fiberbiom idzie krok dalej — laczy rozpuszczalny blonnik z kory modrzewia z Genactiv® Colostrum, by zadbac o mikrobiom i bariere jelitowa.
- Product card: Genactiv® Fiberbiom / Blonnik + colostrum · 15 saszetek / 179 zl
- CTA: Odkryj Fiberbiom → (genactiv.pl/fiberbiom?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_4_fiberbiom_bold)

#### Wariant B (Editorial) · `PurOnb4B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Benefits list → CTA → Footer jasny

- Krok: 4 / 5
- Eyebrow: POZNAJ FIBERBIOM
- H1: Lekkosc blonnika. Moc colostrum.
- Body: Naturalne uzupelnienie Twojego planu. Fiberbiom laczy blonnik z kory modrzewia z Genactiv® Colostrum — dla jelit, ktore lapia rytm.
- Benefits:
  1. Wspiera mikrobiom — Rozpuszczalny blonnik karmi dobre bakterie jelitowe.
  2. Dba o bariere jelitowa — Colostrum naturalnie wspiera sluzowke jelit.
  3. Lekkosc kazdego dnia — Delikatna formula do codziennego stosowania.
- CTA: Poznaj Fiberbiom (genactiv.pl/fiberbiom?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_4_fiberbiom)

---

### Krok 5 — Loyalty (cala rodzina Genactiv)

#### Wariant A (Bold) · `PurOnb5A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Product grid 2x2 → CTA → Review nudge → Footer ciemny

- Krok: 5 / 5
- Eyebrow: TWOJ PLAN ROSNIE
- H1: Zdrowie calej rodziny
- Body: Colostrum to dopiero poczatek. Genactiv® to caly plan na zdrowie — dla Ciebie, Twoich bliskich, skory, a nawet pupila.
- Product grid:
  1. Fiberbiom — Blonnik + colostrum dla jelit i mikrobiomu. [Odkryj →]
  2. DERMO — Kosmetyki z colostrum i mlekiem klaczy. [Zobacz →]
  3. Zooggies — Colostrum + kolagen dla Twojego pupila. [Poznaj →]
  4. Colostrum Junior — Polecane przez mamy, lubiane przez dzieci. [Sprawdz →]
- CTA: Odkryj cala rodzine Genactiv → (genactiv.pl/?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_5_family_bold)
- Review nudge: Jak sprawdza sie Twoje Colostrum? / Podziel sie opinia i pomoz innym rodzinom wybrac dobrze. / Dodaj opinie →

#### Wariant B (Editorial) · `PurOnb5B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Product grid 1x2 → CTA → Review nudge → Footer jasny

- Krok: 5 / 5
- Eyebrow: CALA RODZINA GENACTIV
- H1: Jeden plan. Cale zdrowie.
- Body: Od odpornosci, przez jelita, po skore i pupila — Genactiv® rosnie razem z Twoimi potrzebami.
- Product grid:
  1. DERMO — Kosmetyki z colostrum i mlekiem klaczy. [Zobacz →]
  2. Zooggies — Colostrum + kolagen dla Twojego pupila. [Poznaj →]
- CTA: Zobacz wszystkie linie (genactiv.pl/?utm_source=klaviyo&utm_medium=email&utm_campaign=onboarding_5_family)
- Review nudge: Jak sprawdza sie Twoje Colostrum? / Podziel sie opinia i pomoz innym rodzinom wybrac dobrze. / Dodaj opinie →

---

## NUR (bez zakupu)

### Krok 1 — Welcome + kod rabatowy

#### Wariant A (Bold) · `NurOnb1A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Discount box → Product card → CTA → Shipping nudge → Benefits → Footer ciemny

- Krok: 1 / 5
- Eyebrow: WITAJ W GENACTIV®
- H1: Twoj −15% na start
- Body: Czesc{% if first_name %} {{ first_name }}{% endif %}! Milo, ze tu jestes. Na dobry poczatek mamy dla Ciebie rabat na pierwsze zamowienie Colostrum nr 1 w aptekach w Polsce*.
- Discount box: Twoj kod powitalny / START15 / −15% na caly koszyk · bez minimum
- Product card: Colostrum Genactiv, kapsulki / Suplement diety · 60 kapsulek / ★★★★★ / 105 zl
- CTA: Kup teraz z rabatem → (genactiv.pl/colostrum?...&discount=START15)
- Shipping: Darmowa dostawa od 300 zl
- Przypis: *wg IQVIA Poland Pharmascope, kategoria odpornosc, MAT 12/2024
- Benefits: Naturalny smak / 100% natury / Wygodna forma

#### Wariant B (Editorial) · `NurOnb1B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Discount box → Hero image → CTA → Trust line → Footer jasny

- Krok: 1 / 5
- Eyebrow: MILO CIE POZNAC
- H1: Zacznij swoj plan na zdrowie — taniej o 15%.
- Body: Dziekujemy za dolaczenie{% if first_name %}, {{ first_name }}{% endif %}. Oto Twoj kod powitalny na pierwsze odkrycie colostrum Genactiv®.
- Discount box: Twoj kod powitalny / START15 / −15% na caly koszyk · bez minimum
- CTA: Odkryj Colostrum (genactiv.pl/colostrum?...&discount=START15)
- Trust line: ★★★★★ Colostrum nr 1 w aptekach w Polsce

---

### Krok 2 — Education

#### Wariant A (Bold) · `NurOnb2A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Reason list → CTA → Discount reminder → Benefits → Footer ciemny

- Krok: 2 / 5
- Eyebrow: POZNAJ SKLADNIK
- H1: Dlaczego colostrum?
- Body: To pierwszy pokarm natury — 250 aktywnych skladnikow w jednej substancji. Czyste, nieprzetworzone, w 100% wierne naturze. Oto dlaczego dziala:
- Reasons:
  1. Immunoglobuliny — Naturalne przeciwciala wspierajace odpornosc kazdego dnia.
  2. Laktoferyna — Bialko o wlasciwosciach wspierajacych naturalna bariere organizmu.
  3. Czystosc i natura — Liofilizowane colostrum bez zbednych dodatkow — moc w czystej formie.
- CTA: Dowiedz sie wiecej → (genactiv.pl/colostrum?...onboarding_nur_2_education_bold)
- Discount reminder: Pamietaj — masz −15% z kodem START15.
- Benefits: Naturalny smak / 100% natury / Wygodna forma

#### Wariant B (Editorial) · `NurOnb2B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Expert quote → Reason list → CTA → Footer jasny

- Krok: 2 / 5
- Eyebrow: NATURA + NAUKA
- H1: Co to jest colostrum?
- Body: Colostrum (siara) to pierwszy pokarm, jaki natura przygotowuje dla noworodka — bogaty w skladniki wspierajace odpornosc od pierwszych chwil zycia.
- Expert: „Colostrum bovinum to jedno z najlepiej przebadanych naturalnych zrodel immunoglobulin. To natura wsparta nauka." — Zdaniem ekspertow · na podstawie badan naukowych
- Reasons:
  1. 250 aktywnych skladnikow — W jednej, naturalnej substancji.
  2. Liofilizacja — Delikatny proces, ktory zachowuje to, co najcenniejsze.
- CTA: Czytaj o colostrum (genactiv.pl/colostrum?...onboarding_nur_2_education)

---

### Krok 3 — Social Proof

#### Wariant A (Bold) · `NurOnb3A.html`

**Struktura:** Header czerwony → Step Rail → Eyebrow → H1 → Body → Trust badge → Reviews → Expert row → CTA → Disclaimer → Footer ciemny

- Krok: 3 / 5
- Eyebrow: ZAUFALY NAM TYSIACE
- H1: Nr 1 w aptekach w Polsce
- Body: Nie wierz nam na slowo. Colostrum Genactiv® to najczesciej wybierane colostrum w polskich aptekach w kategorii odpornosc.*
- Trust badge: ✓ Colostrum nr 1 w aptekach
- Review 1: ★★★★★ „Stosuje cala rodzina przez cala jesien. Wreszcie spokojny sezon — polecam kazdej mamie!" — Karolina
- Review 2: ★★★★★ „Kapsulki latwe do polkniecia, jakosc czuc od pierwszego opakowania. Zamawiam ponownie." — Tomasz
- Expert row: Monika Stromkie-Zlomaniec (Dietetyk) / dr hab. n. med. Maciej Halasa (Immunolog) / Magdalena Szymczak-Kepka (Psycholog, trycholog)
- CTA: Sprawdz, dlaczego nr 1 → (genactiv.pl/colostrum?...onboarding_nur_3_social_proof_bold)
- Disclaimer: *wg IQVIA, kategoria odpornosc, MAT 12/2024. Kod START15 wciaz aktywny.

#### Wariant B (Editorial) · `NurOnb3B.html`

**Struktura:** Header jasny → Step Rail → Pull quote → Trust badge → Expert row → CTA → Footer jasny

- Krok: 3 / 5
- Pull quote: ★★★★★ „Stosuje cala rodzina — wreszcie spokojny sezon." — Karolina
- Trust badge: ✓ Colostrum nr 1 w aptekach / wg IQVIA, kategoria odpornosc, MAT 12/2024
- Expert row: Monika Stromkie-Zlomaniec (Dietetyk) / dr hab. n. med. Maciej Halasa (Immunolog) / Magdalena Szymczak-Kepka (Psycholog, trycholog)
- CTA: Dolacz do nich (genactiv.pl/colostrum?...onboarding_nur_3_social_proof&discount=START15)

---

### Krok 4 — Reminder

#### Wariant A (Bold) · `NurOnb4A.html`

**Struktura:** Urgency bar → Header czerwony → Step Rail → Eyebrow → H1 → Body → Discount box → Product card → CTA → Shipping nudge → Footer ciemny

- Urgency bar: Twoj kod −15% wygasa za 48 godzin
- Krok: 4 / 5
- Eyebrow: NIE PRZEGAP
- H1: Twoj kod wciaz czeka
- Body: Twoj kod czeka — a szkoda byloby go nie wykorzystac. START15 to −15% na pierwsze odkrycie Colostrum nr 1 w aptekach*. Ale tylko przez najblizsze 48 godzin.
- Discount box: Twoj kod powitalny / START15 / −15% na caly koszyk · wazny jeszcze 48h
- Product card: Colostrum Genactiv, kapsulki / Bestseller · 60 kapsulek / ★★★★★ / ~~105 zl~~ 89 zl z kodem
- CTA: Wykorzystaj kod teraz → (genactiv.pl/colostrum?...onboarding_nur_4_reminder_bold&discount=START15)
- Shipping: Darmowa dostawa od 300 zl
- Przypis: *wg IQVIA Poland Pharmascope, kategoria odpornosc, MAT 12/2024

#### Wariant B (Editorial) · `NurOnb4B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Discount box → Hero image → CTA → Trust line → Footer jasny

- Krok: 4 / 5
- Eyebrow: DELIKATNE PRZYPOMNIENIE
- H1: Twoj plan na zdrowie wciaz czeka.
- Body: Bez pospiechu — ale Twoj kod powitalny ma swoj termin. Skorzystaj, zanim wygasnie.
- Discount box: Twoj kod powitalny / START15 / −15% · wazny jeszcze 48 godzin
- CTA: Zacznij teraz z −15% (genactiv.pl/colostrum?...onboarding_nur_4_reminder&discount=START15)
- Trust line: ★★★★★ Colostrum nr 1 w aptekach w Polsce

---

### Krok 5 — Last Call

#### Wariant A (Bold) · `NurOnb5A.html`

**Struktura:** Urgency bar → Header czerwony → Step Rail → Eyebrow → H1 → Body → Discount box → Product card → CTA → Shipping nudge → Footer ciemny

- Urgency bar: Ostatnia szansa — kod znika dzis o polnocy
- Krok: 5 / 5
- Eyebrow: OSTATNIE WOLANIE
- H1: Kod −15% znika dzis
- Body: To juz naprawde ostatni moment. Po polnocy START15 przestaje dzialac. Zacznij swoj plan na zdrowie z najlepszym colostrum w polskich aptekach — w najlepszej cenie.
- Discount box: Twoj kod powitalny / START15 / −15% · wygasa dzis o 23:59
- Product card: Colostrum Genactiv, kapsulki / Bestseller · 60 kapsulek / ★★★★★ / ~~105 zl~~ 89 zl z kodem
- CTA: Odbierz rabat, zanim zniknie → (genactiv.pl/colostrum?...onboarding_nur_5_last_call_bold&discount=START15)
- Shipping: Darmowa dostawa od 300 zl

#### Wariant B (Editorial) · `NurOnb5B.html`

**Struktura:** Header jasny → Step Rail → Eyebrow → H1 → Body → Product hero → Discount box → CTA → Trust line → Footer jasny

- Krok: 5 / 5
- Eyebrow: OSTATNIE PRZYPOMNIENIE
- H1: Zostawiamy to w Twoich rekach.
- Body: Nie chcemy naciskac. Ale Twoj kod powitalny wygasa dzis o polnocy — a dobre nawyki najlepiej zaczynac od dzis.
- Product hero: Genactiv Colostrum, kapsulki / ~~105 zl~~ 89 zl z kodem START15
- Discount box: Twoj kod (wygasa dzis) / START15 / −15% · do 23:59
- CTA: Skorzystaj z −15% (genactiv.pl/colostrum?...onboarding_nur_5_last_call&discount=START15)
- Trust line: ★★★★★ Colostrum nr 1 w aptekach w Polsce

---

## Zasoby graficzne

Wszystkie obrazki wgrane do Klaviyo CDN:

```
logo-primary (czerwone):
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/4184cd9f-e0e6-416e-bcb0-dc993d979024.png

logo-white (biale, na ciemne tlo):
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/871a18d8-3f4f-4c02-99d1-0160f3bdf4fb.png

photo-colostrum-nr1 (hero produktu):
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/a39c52d9-2970-4305-98f5-982533446768.png

icon-smak:
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/eab2c5ba-401a-4bad-8656-fc0cdd98e44e.png

icon-naturalnosc:
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/bb3ac92b-22de-48f1-a710-f76e8437db96.png

icon-forma:
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/d8528f60-79fd-4d36-9ff7-ce217d41a917.png

expert-monika (Monika Stromkie-Zlomaniec, Dietetyk):
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/c8c5267f-3568-43ff-99ca-190e126e1e2f.png

expert-halasa (dr hab. n. med. Maciej Halasa, Immunolog):
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/8363bcad-dc9c-4167-8deb-32bba380b6a0.png

expert-magda (Magdalena Szymczak-Kepka, Psycholog/trycholog):
https://d3k81ch9hvuctc.cloudfront.net/company/RSst7h/images/fcf6a0b4-35ff-4c91-b606-1f8df7f37f32.png
```

---

## Logika techniczna

### Personalizacja Klaviyo

```django
{{ first_name|default:'' }}              — Imie (puste jesli brak)
{{ first_name|default:'Czesc' }}         — Imie z fallbackiem (PurOnb1A)
{% unsubscribe 'Anuluj subskrypcje' %}   — Link wypisania (wymagany)
{% manage_preferences %}                  — Link preferencji
```

### Listy Klaviyo

```
Shopify Newsletter: VT3KTz (double_opt_in) — trigger flow
RODO: WMKx4B
SMS Subscribers: WrryaN
```

### Kodowanie HTML

- Inline CSS (bez flex/grid)
- `<table role="presentation">` layout
- 600px szerokosc, responsywnosc @media max-width:600px
- Font: Montserrat (via @import) + Arial fallback
- Bulletproof pill button (VML Outlook)
- Preheader ukryty w `<div>` z `display:none`
- Dark mode: `@media (prefers-color-scheme: dark)`
- Wszystkie linki z UTM: `?utm_source=klaviyo&utm_medium=email&utm_campaign=...`

### Kolory

```
Czerwony (CTA, akcenty):  #F5333F
Tekst glowny:             #1C1B1B
Tekst body:               #5C5757
Tekst meta:               #8B8585
Tlo body:                 #F4F1EE
Tlo biale:                #FFFFFF
Tlo kremowe (boxy):       #FBEFE2
Border/linia:             #ECE8E5
Inactive dot:             #D8D3D0
Footer ciemny bg:         #1C1B1B
```

### Roznice miedzy wariantami A i B

| Element | A (Bold) | B (Editorial) |
|---------|----------|---------------|
| Header | Czerwony (#F5333F), logo biale | Bialy, logo czerwone, dolna kreska |
| Wyrownanie | Left-aligned | Centered |
| CTA | Full-width block button | Inline pill button |
| Footer | Ciemny (#1C1B1B) | Jasny (#F4F1EE) |
| Ton | Bezposredni, mocny | Spokojny, narracyjny |
| Dodatkowe elementy | Dosage box, product cards, urgency bars | Expert quotes, tip boxes, trust lines |

### Stopka (wspolna tresc)

**PUR:** Otrzymujesz te wiadomosc, bo kupujesz Genactiv® Colostrum.
**NUR:** Otrzymujesz te wiadomosc, bo jest subskrypcja newslettera Genactiv®.

Genactiv Sp. z o.o. · ul. Polna 13/3, 62-070 Dabrowka · NIP 9721202218
(c) 2026 Genactiv. Twoj plan na zdrowie.

---

## Ekosystem flow Klaviyo (mapa + migracja)

### Inwentarz flow (stan na 2026-06-23)

```
LIVE:
  STdfpu  Shopify newsletter - welcome     Added to List   ← ZASTEPOWANY przez R7q8bj
  QT48jk  Cross-sell_19_05_2026            Metric          (osobny tor)
  RP24Kg  Review request                   Metric          (osobny tor)
  VfCSbb  Browse_test_10_12                Metric          (osobny tor)
  WCYsqW  Back In Stock Flow - Standard    Metric          (osobny tor)
  YkhmXm  Abandoned Cart Reminder          Metric          (osobny tor)

DRAFT (nasze v3):
  R7q8bj  Newsletter Nurture Onboarding v3 Added to List   ← NOWY NUR (upgrade STdfpu)
  UNETEK  Post-Purchase Onboarding v3      Metric          ← NOWY PUR (zastepuje UXajkz)

DRAFT (stare/do archiwizacji):
  UXajkz  ROC_Onboarding_draft             Added to List   ← ZASTAPIONY przez UNETEK
  TLdudj  Dzien Mamy                       Added to List   (osobny, sezonowy)
  WgXWvU  Post buy_refreshments            Metric          (replenishment — kolejny etap)

PUSTE DRAFTY (do usuniecia):
  RjR6ms  Essential Flow Recommendation_   Unconfigured
  UvyzDs  Essential Flow Recommendation_   Unconfigured
  X4f2iP  Essential Flow Recommendation_   Unconfigured
```

### Plan migracji (kolejnosc krytyczna — zero duplikatow!)

Flow A (NUR) to **upgrade STdfpu** z 1 maila na 5-mailowa serie:
Flow B (PUR) to **zastepstwo UXajkz** (podzial na 2 flow + poprawki tresci)

```
KROK 1 — QA na v3 Draft (teraz)
  Profil A: zapis do newslettera, brak zakupu → caly Flow A (5 maili)
  Profil B: zapis + zakup po Kroku 2 → wypada z Flow A, wchodzi Flow B
  Profil C: zakup bez newslettera → Flow B
  Profil D: 2. zakup → Flow B NIE startuje (filtr = 1)

KROK 2 — Przelaczenie (ATOMOWE, nie moze byc obu live naraz)
  1. STdfpu → status: Manual (zatrzymuje nowe wejscia)
  2. R7q8bj → status: Live (NUR przejmuje)
  3. UXajkz → status: archiwizacja
  4. UNETEK → status: Live (PUR startuje)
  Uwaga: STdfpu i R7q8bj maja ten sam trigger (Added to List VT3KTz)
  Jesli oba sa live — dubel welcome. Dlatego kolejnosc jest krytyczna.

KROK 3 — Sprzatanie
  - Archiwizacja/kasacja: RjR6ms, UvyzDs, X4f2iP (puste Unconfigured)
  - Archiwizacja: UXajkz (zastapiony przez UNETEK)
  - Archiwizacja: STdfpu (zastapiony przez R7q8bj) — dopiero po 30d obserwacji
  - Kasacja szablonow v1 (20 szt.) i v2 (20 szt.)
```

### Scorecard — benchmark vs. plan v3

```
#01 Welcome series zamiast 1 maila     ✅ Pokryte (Flow A = 5 maili NUR)
#02 Porzucony koszyk (YkhmXm)          ⬜ Poza zakresem (osobny flow)
#03 Plain-text list od eksperta         ❌ Luka (do rozważenia w Flow B)
#04 Replenishment (WgXWvU, AOV 285)    ⬜ Poza zakresem (kolejny build po v3)
#05 Browse abandonment (VfCSbb)        ⬜ Poza zakresem
#06 Oferta tierowana + reframing       ⚠️ Czesciowo (single START15)
#07 Gra/wspolnota zamiast rabatu       ⬜ Poza zakresem
#08 Stopka EU + sprzatanie draftow     ✅ Zbiezne z review
```

### Uwaga o consent

Flow A (NUR) triggeruje na "Added to List VT3KTz" (double_opt_in).
Sam trigger implikuje zgode — profil nie moze byc dodany do listy
double_opt_in bez potwierdzenia. Dodatkowy filtr consent nie jest wymagany.

### Nastepne kroki po v3 (poza zakresem)

1. **Replenishment** (WgXWvU) — najwyzszy potencjalny zwrot, Flow B (1. zakup)
   jest naturalnym wejsciem do replenishment (2. cykl)
2. **Plain-text expert letter** — opcjonalny mail w Flow B (PUR) miedzy
   Krok 2 a 3, podpisany przez Halase/Monike, format plain-text
3. **Oferta tierowana** — single −10% / zestaw −20% w NUR zamiast flat START15
   (decyzja biznesowa, nie copy)
4. **Urgency NUR4/NUR5** — benchmark potwierdza standard kategorii,
   zostawiamy (warunek: realna data wygasniecia kodu)

---

## Changelog

### v3 (2026-06-23) — poprawki tresci + flow przez API + audyt benchmarkowy

**Flow (API):**
- Stworzono Flow B (PUR): UNETEK — Post-Purchase Onboarding v3 (Draft)
- Stworzono Flow A (NUR): R7q8bj — Newsletter Nurture Onboarding v3 (Draft)
- Flow A zastepuje STdfpu (upgrade z 1 maila na 5-mailowa serie)
- Flow B zastepuje UXajkz (podzial na 2 niezalezne flow)
- Plan migracji: atomowe przelaczenie (STdfpu→Manual → R7q8bj→Live)

**Audyt benchmarkowy (2026-06-23):**
- Potwierdzony kierunek: welcome series, os czasu efektow, scoping 1. zakup
- Zidentyfikowane ryzyko duplikacji flow (rozwiazane planem migracji)
- Urgency NUR4/NUR5 zostawione (standard kategorii wg benchmarku)
- Dodano mape ekosystemu flow i scorecard 8 rekomendacji
- Zidentyfikowane kolejne kroki: replenishment, plain-text expert letter, oferta tierowana

**Globalne (szablony):**
- Ceny Colostrum zaktualizowane z Shopify live: 69 zl → 105 zl (pelna), 89 zl (po rabacie −15%)
- Fiberbiom: 30 saszetek/~~92~~ 79 zl → 15 saszetek / 179 zl (cena live)
- Darmowa dostawa: 99 zl → 300 zl (fakt)
- Formy zenskie ("dolaczyla", "zostawila") → bezosobowe ("dolaczasz", "Twoj kod czeka")
- Cytaty ekspertow → bezosobowe ("Zdaniem ekspertow · na podstawie...")
- "Colostrum nr 1 w aptekach" → dodany asterisk (*) + przypis IQVIA
- Usuniete liczniki opinii: (412), (128)
- Usuniete etykiety "zweryfikowany zakup"
- NUR stopka: "zapisalas sie" → "jest subskrypcja"
- NurOnb1A/1B: naprawiona personalizacja ({{ first_name }} → {% if first_name %})
- PurOnb4A: usuniety falszywy bundle "−15% w zestawie" (nie istnieje w Shopify)
- PurOnb3A/3B: zlagodzone health-claims ("wiecej energii" → "poprawe samopoczucia")
- NurOnb3A/3B: poprawione tytuly ekspertow (Magda/Farmaceuta → Magdalena Szymczak-Kepka/Psycholog, trycholog)
- Architektura flow: zmiana z 1 flow + conditional split na 2 niezalezne flow (PUR trigger: Placed Order = 1; NUR trigger: Added to list + Placed Order = 0)

### v2 (2026-06-22) — poprawka techniczna

- Naprawa bledu `<link>` → `@import url()` (Klaviyo odrzucal `<link>` jako "Nieznany wezel")
- Wszystkie 20 szablonow re-uploadowane

### v1 (2026-06-22) — poczatkowe wgranie

- 20 szablonow (10 PUR + 10 NUR) stworzonych i wgranych do Klaviyo
- Blad: uzycie `<link>` tagu odrzucanego przez Klaviyo

---

## Otwarte tematy (do decyzji)

1. **Kod START15 — statyczny vs dynamiczny:** Obecny copy w NUR4/NUR5 mowi o wygasaniu kodu (48h / polnoc). Jesli kod jest statyczny, to jest nieprawdziwe. Rozwiazanie: albo dynamiczny kupon Klaviyo (`{% coupon_code %}` z expiracją), albo zmiana copy na uczciwe ("skorzystaj teraz"). Benchmark potwierdza: urgency jest standardem kategorii (ARMRA, Seed, AG1 stosuja "ENDS TONIGHT", countdowny), wiec pilnosc zostawiamy — ale data musi byc realna.
2. **Prog darmowej dostawy 300 zl:** Przy cenie 105 zl za Colostrum, prog jest nieosiagalny z 1 produktu. Benchmark sugeruje rozwiazanie: **oferta tierowana** (single −10% / zestaw −20%) podbija koszyk w strone 300 zl. Alternatywa: reframing "juz od X zl dziennie" (cena / liczba porcji). Decyzja biznesowa.
3. **Cytaty ekspertow:** Zamienione na bezosobowe. Jesli uzyskamy autoryzacje — mozna przywrocic imienne. Benchmark (rec #03) mocno sugeruje **plain-text list od eksperta** (Halasa/Monika) jako dodatkowy mail w Flow B — wyzsze zaufanie i dostarczalnosc niz ciezki HTML.
4. **Replenishment (WgXWvU):** Benchmark wskazuje jako #1 brakujacy przychod (AOV ~285 PLN, draft lezy). Flow B (1. zakup, filtr = 1) jest naturalnym wejsciem — po onboardingu klient plynnie przechodzi do replenishment. Rekomendacja: kolejny build zaraz po v3.
5. **Sprzatanie Klaviyo:** Do archiwizacji po migracji: 3 puste drafty (RjR6ms, UvyzDs, X4f2iP), stary draft UXajkz, stary live STdfpu (po 30d obserwacji), 40 starych szablonow (v1 + v2).

# Genactiv Onboarding — Review i lista poprawek

> Autor: audyt MCP/e-commerce · Data: 2026-06-22
> Zakres: `ONBOARDING_PLAN.md` (20 szablonów, PUR + NUR) vs. faktyczny stan `genactiv.pl`
> Źródła weryfikacji: strona główna, `/products/fiberbiom-blonnik-colostrum`, kolekcja `/collections/colostrum`, koszyk (próg dostawy), wyszukiwarka (cena kapsułek, Colostrum Junior)

---

## 0. TL;DR — priorytety

**P0 — błędy faktyczne, które wyjdą z maila do klienta (naprawić przed publikacją):**

1. Fiberbiom: zła gramatura, zła cena, prawdopodobnie zmyślona promocja i liczba opinii (Krok 4 PUR).
2. Darmowa dostawa: w mailach „od 99 zł", na stronie **od 300 zł**.
3. Ekspertka „Magda (Farmaceuta)" — na stronie to **Magdalena Szymczak-Kępka, psycholog diagnosta, trycholog**. Zły zawód i błędne nazwisko.
4. Cena Colostrum kapsułki 69 zł — do weryfikacji, listingi zewnętrzne wskazują 75–89 zł (możliwe, że nieaktualna).
5. Twierdzenie „Nr 1 w aptekach" bez gwiazdki/źródła IQVIA w większości maili (compliance).

**P1 — logika flow i UX:**

6. **Brak obsługi: NUR kupuje w trakcie onboardingu** (główne pytanie) — dziś osoba dalej dostaje maile „kod wygasa / ostatnia szansa".
7. Treść PUR zakłada „świeży pierwszy zakup", a trigger to zapis do newslettera + „zamówienie kiedykolwiek" — copy bywa nieprawdziwe.
8. Mechanika kodu START15 (realna data wygaśnięcia vs. statyczny kod) — od tego zależy uczciwość urgency.

**P2 — ton, gramatyka, technikalia:**

9. Bugi personalizacji (`Czesc{{ first_name }}` bez spacji, `dołączyła{{ first_name }}`).
10. Formy żeńskie zakładające płeć odbiorcy.
11. Twarde urgency (Bold NUR) vs. spokojne, „naturalne" pozycjonowanie marki.

---

## A. Niespójności merytoryczne (plan vs. genactiv.pl)

### A1. Fiberbiom — Krok 4 PUR (P0)
Plan (PurOnb4A, product card): „**30 saszetek** · ~~92,00 zł~~ **79,00 zł** · ★★★★★ (128) · −15% w zestawie z Colostrum".

Stan faktyczny na stronie produktu:
- Gramatura: **15 saszetek** (nie 30).
- Cena: **179,00 zł** (cena regularna = cena sprzedaży, brak przekreślenia).
- Skład: błonnik = **Arabinogalaktan z kory modrzewia** (5000 mg) + liofilizat colostrum bovinum (1000 mg) — to akurat zgadza się z opisem.
- Sekcja „Opinie" na stronie jest **pusta** → liczba „(128)" jest niczym niepoparta.
- Promocji „−15% w zestawie z Colostrum" nie potwierdzono — wygląda na zmyśloną.

**Do zrobienia:** poprawić gramaturę (15 saszetek), cenę (179 zł), usunąć fałszywe przekreślenie i liczbę opinii, potwierdzić lub usunąć ofertę pakietową. Jeśli ma być realna promocja bundle — najpierw skonfigurować ją w Shopify, potem opisać.

### A2. Próg darmowej dostawy (P0)
Plan (NurOnb1A, NurOnb4A, NurOnb5A): „**Darmowa dostawa od 99 zł**".
Strona (pasek koszyka + karta Fiberbiom): „**Dostawa: od 300 zł darmowa**".

**Do zrobienia:** zmienić wszędzie na „od 300 zł". Uwaga UX: skoro pojedyncze Colostrum to ~69–89 zł, komunikat „darmowa dostawa od 300 zł" w mailu z jednym produktem działa zniechęcająco — rozważyć przesunięcie progu w komunikacji na cross-sell/bundle albo pominięcie.

### A3. Ekspertka „Magda" (P0)
Plan: ikona/podpis „**Magda (Farmaceuta)**" (Krok 3 NUR, expert row; oraz asset `expert-magda (Farmaceuta)`).
Strona: trzecia ekspertka to **Magdalena Szymczak-Kępka — psycholog diagnosta, trycholog** (nie farmaceuta).

**Do zrobienia:** poprawić nazwisko i tytuł, albo — jeśli psycholog/trycholog nie pasuje do narracji o odporności — zastąpić inną realną osobą z zespołu. Przypisywanie komuś nieistniejącego zawodu to ryzyko wizerunkowe.

### A4. Pozostali eksperci (P1)
- Plan: „Monika Stromkie-Zlomaniec, **Dietetyk kliniczny**" → strona: „Monika Stromkie-Złomaniec, **Dietetyk**" (dodano nieistniejące „kliniczny").
- Plan: „**dr hab. n. med. Halasa, Immunolog**" → strona: „**dr hab. n. med. Maciej Hałasa, specjalista immunolog**" (brak imienia, literówka bez „ł").

**Do zrobienia:** ujednolicić tytuły 1:1 ze stroną, dodać imię Hałasy, zadbać o polskie znaki w finalnym HTML.

### A5. Cytaty ekspertów (P0/compliance)
Plan wkłada w usta realnych, imiennie wskazanych osób cytaty (PUR2B i NUR2B — Hałasa; PUR2B — Monika), np. „Colostrum działa najlepiej, gdy stosujemy je systematycznie…".

**Ryzyko:** przypisywanie autentycznym ekspertom wypowiedzi, których nie autoryzowali = ryzyko prawne i wizerunkowe.
**Do zrobienia:** użyć wyłącznie cytatów realnie zatwierdzonych przez te osoby, albo przeredagować na bezosobowe („zdaniem ekspertów Genactiv…") bez imiennego przypisania.

### A6. Cena Colostrum kapsułki (P0 — do weryfikacji)
Plan: „60 kapsułek · **69,00 zł**", a z kodem −15% „58,65 zł".
Strona oficjalna renderuje cenę przez JS (nie udało się pobrać bezpośrednio), ale listingi zewnętrzne (Gemini, Ceneo, Allegro) wskazują **~75–89 zł**.

**Do zrobienia:** zweryfikować realną cenę w panelu Shopify i wstawić ją dynamicznie (event/feed), a nie na sztywno. Jeśli 69 zł jest nieaktualne, wszystkie kwoty „przed/po rabacie" w NUR są błędne.

### A7. Liczby opinii i recenzje imienne (P1)
Plan podaje „★★★★★ (412)" dla Colostrum i „(128)" dla Fiberbiom oraz imienne opinie („Karolina", „Tomasz" — „zweryfikowany zakup").

**Ryzyko:** na stronach produktów sekcje opinii są puste → liczby i cytaty wyglądają na zmyślone; etykieta „zweryfikowany zakup" przy nieistniejącej recenzji wprowadza w błąd.
**Do zrobienia:** podpiąć realne opinie (np. z systemu recenzji Shopify) albo usunąć liczniki i cudzysłowy. Nie używać „zweryfikowany zakup" bez pokrycia.

### A8. Dawkowanie (P1 — do weryfikacji)
Plan (PurOnb2A, dosage box): „**1–2 kapsułki dziennie**".
Źródła produktowe: „1–2 kapsułki, zwykle 2× dziennie, maks. 6 dziennie".

**Do zrobienia:** dopasować dawkowanie 1:1 do etykiety produktu (to też kwestia zgodności — komunikat o dawce ma być zgodny z opakowaniem).

### A9. Elementy zgodne — zostawić bez zmian
- Nazwa „Colostrum Junior" — **istnieje** (zawiesina/saszetki, czarny bez). OK.
- Linie DERMO (kosmetyki z colostrum + mleko klaczy) i Zooggies (colostrum + kolagen dla zwierząt) — OK.
- „250 składników aktywnych", „liofilizacja", „kora modrzewia" — zgodne ze stroną.
- Hasło „Twój plan na zdrowie", znak „Genactiv®", kolor `#F5333F` (= `theme-color` strony) — zgodne.
- Dane spółki (Genactiv Sp. z o.o., Polna 13/3, 62-070 Dąbrówka, NIP 9721202218) — zgodne.

---

## B. Niespójności tonacji i wizualne (vs. pozycjonowanie)

### B1. Twarde urgency vs. „natura lubi rytm" (P2)
Strona buduje narrację spokojną, naturalną, rodzinną („Twój plan na zdrowie", „natura potrzebuje rytmu", emotki, zaufanie). Warianty Bold w NUR4/NUR5 grają agresywnie: pasek „kod wygasa za 48 godzin", „Kod −15% znika dziś", „OSTATNIE WOŁANIE".

**Napięcie:** wysokopresyjny discount-marketing kłóci się z premium/aptecznym, „naturalnym" tonem marki (nr 1 w aptekach, nauka, eksperci). Wariant B jest dobrze wyważony („Nie chcemy naciskać") — Bold mniej.
**Do zrobienia:** złagodzić copy Bold (utrzymać deadline, zdjąć „wołanie/znika dziś") albo świadomie zostawić różnicę jako część testu A/B, ale pilnować spójności z głosem marki.

### B2. Niespójny poziom emoji (P2)
Strona główna intensywnie używa emoji (😍💪❤️). Plan maili — zero. To nie błąd, ale rozjazd w „osobowości" marki między www a mailem. Decyzja świadoma: albo dopuścić oszczędne emoji w nagłówkach NUR (bliżej tonu www), albo celowo trzymać maile „czyściej".

### B3. Czcionka i logo (P2 — weryfikacja)
- Plan: Montserrat (via `@import`). CLAUDE.md wskazuje font marki „Branding-medium". `@import` web-fontów w mailu jest zawodny (Outlook/Gmail go ignorują → fallback Arial). Zalecenie: traktować font marki jako warstwę „nice-to-have", projektować pod fallback systemowy.
- Logo w planie pochodzi z CDN Klaviyo (starsze uploady). Strona używa `logo-GA-podstawowe-RGB` / `logo_new2`. Sprawdzić, czy wgrane logo = aktualny znak marki.

### B4. Notka — rozjazd CLAUDE.md vs. strona (info)
CLAUDE.md podaje markowe kolory `#EF3340` (red) i `#0066CC` (blue). Realny `theme-color` strony to `#f5333f` — i plan słusznie używa `#F5333F`. To CLAUDE.md jest nieaktualny, nie plan. Warto zsynchronizować brand guide.

---

## C. Luki logiczne i braki we flow

### C1. GŁÓWNE: NUR kupuje w trakcie onboardingu (P1)
**Problem:** trigger = dodanie do listy „Shopify Newsletter", a podział warunkowy „Złożone zamówienie (kiedykolwiek)" liczony jest **raz, na wejściu**. Jeśli osoba z gałęzi NUR kupi w trakcie flow (np. wykorzysta START15 po Kroku 1), nadal dostaje maile „Twój kod wciąż czeka", „Ostatnia szansa", „kod znika dziś" — wygląda to na zepsuty system i potrafi dać kolejne rabaty już-klientowi.

**Rekomendowane rozwiązanie (Klaviyo):**
1. **Flow Filter na całym flow (lub na gałęzi NUR):** `Placed Order zero times since starting this flow`. Filtry flow są re-ewaluowane przy każdym time-delay, więc osoba, która kupi, zostanie **usunięta z flow** przy najbliższym kroku. To najczystsza, minimalna poprawka.
2. **Dodatkowo Conditional Split przed każdym mailem NUR** (`Placed Order since flow start = 0`) — twarde zabezpieczenie między opóźnieniami.
3. **Docelowo:** kupującego w trakcie NUR „przekazać" do właściwego post-purchase flow (osobny trigger na `Placed Order`/Shopify), zamiast wpychać go w PUR-onboarding w połowie. Onboarding NUR i powitanie po zakupie to dwie różne historie — nie sklejać ich w locie.

**Decyzja do podjęcia przez Ciebie:** czy po zakupie w NUR klient ma (a) po prostu wypaść z onboardingu i trafić do standardowego post-purchase flow, czy (b) dostać skrócone „dziękujemy + jak stosować" z gałęzi PUR. Rekomendacja: (a) — czyściej, bez duplikacji powitań.

### C2. PUR copy zakłada „świeży zakup", a trigger to newsletter (P1)
PUR Krok 1: „Twoje zamówienie jest już w drodze", „dziękujemy za pierwszy zakup", „Dostawa w 1–2 dni robocze". Ale wejście do flow = zapis do newslettera, a do gałęzi PUR kwalifikuje „zamówienie **kiedykolwiek**". Osoba, która kupiła pół roku temu i dziś zapisała się do newslettera, dostanie nieprawdziwe „paczka w drodze / dziękujemy za pierwszy zakup".

**Do zrobienia (jedna z dwóch dróg):**
- **A (zalecane):** rozdzielić — prawdziwy post-purchase onboarding trigerować na `Placed Order` (świeży zakup), a flow z triggerem „newsletter" niech traktuje PUR jako „witaj ponownie, jako nasz klient" bez fraz o paczce w drodze.
- **B:** zmiękczyć copy PUR, żeby nie zakładało świeżości zamówienia („skoro znasz już Colostrum…" zamiast „paczka w drodze").

### C3. Mechanika i wygaśnięcie kodu START15 (P1)
NUR4/NUR5 obiecują „kod wygasa za 48h / dziś o północy". Jeśli START15 jest **statycznym** kodem, to: (a) urgency jest nieprawdziwe, (b) kod działa dalej po „wygaśnięciu" → klient uczy się ignorować deadline'y. Czasowo same maile są spójne (dzień 5 → „48h", dzień 7 → „dziś"), ale to nie wystarcza bez realnej daty ważności.

**Do zrobienia:** użyć dynamicznego kuponu Klaviyo z czasem ważności per-profil (`{% coupon_code %}` z expiracją) zsynchronizowanym z timingiem maili. Wtedy deadline jest prawdziwy i egzekwowalny.

### C4. „Nr 1 w aptekach" bez przypisu (P0/compliance)
Twierdzenie „Colostrum nr 1 w aptekach" pojawia się w PUR1, NUR1, NUR4, NUR5 i innych — a gwiazdka ze źródłem IQVIA (MAT 12/2024) jest tylko przy NUR3. Strona konsekwentnie dokleja przypis przy każdym wystąpieniu.

**Do zrobienia:** wszędzie, gdzie pada „nr 1 w aptekach", dodać `*` i skrót źródła (IQVIA Poland Pharmascope, kat. odporność, MAT 12/2024). Rozważyć, czy dane sprzed 18 mies. są nadal aktualne — jeśli marka ma nowszy odczyt IQVIA, podmienić okres.

### C5. Stopka — powód otrzymania maila (P2)
PUR: „bo kupujesz Genactiv Colostrum", ale do flow wchodzi się przez zapis do newslettera. Jeśli ktoś trafił do PUR przez newsletter (a nie zakup), powód jest nieścisły. Dopasować formułę do realnego triggera (np. „bo zapisałeś/aś się do newslettera i jesteś naszym klientem").

### C6. Zgodność health-claims (P1/compliance)
Maile mówią o „wsparciu odporności", konkretnej osi czasu efektów („Twoje 8 tygodni", „więcej energii"). Dla suplementów w UE oświadczenia zdrowotne są regulowane (EFSA), a dla colostrum brak wielu autoryzowanych claimów. Strona jest tu ostrożniejsza („naturalne wsparcie bariery").

**Do zrobienia:** dociągnąć język maili do ostrożnego poziomu strony; unikać twardych obietnic efektu i sztywnych ram czasowych jako „pewnych". Najlepiej skonsultować z osobą od compliance.

---

## D. Bugi techniczne i personalizacja

### D1. Zepsута interpolacja imienia (P2)
- `Czesc{{ first_name|default:'' }}!` → bez imienia renderuje „Czesc!", z imieniem „CzescAnna!" (brak spacji). Powinno być `Czesc {{ first_name|default:'' }}!` z obsługą braku imienia.
- `dziękujemy, że dołączyła{{ first_name|default:'' }}` (NUR1B, NUR4B) → „…dołączyłaAnna" lub urwane „…dołączyła.". Zła konstrukcja — imię nie może być doklejane do czasownika.

**Do zrobienia:** rozdzielić zmienną od słów spacją; zaprojektować warianty „z imieniem / bez imienia" tak, by zdanie było poprawne w obu przypadkach.

### D2. Formy żeńskie zakładające płeć (P2)
„dołączyłaś", „Zostawiłaś go bez użycia", „dziękujemy, że dołączyła…". Dla mężczyzn to błąd gramatyczny.

**Do zrobienia:** użyć form neutralnych płciowo („dziękujemy za dołączenie", „Twój kod czeka") albo personalizacji po płci, jeśli Klaviyo ma to pole. Audyt skłania się do form bezosobowych — prościej i bezpiecznie.

### D3. Niezawodność `@import` fontu (P2)
Patrz B3 — `@import`/`<style>` web-fonty są usuwane przez część klientów. Projekt ma działać estetycznie na fallbacku (Arial/Helvetica) bez utraty hierarchii.

### D4. Stare szablony v1 (porządek)
Plan słusznie wskazuje 20 szablonów v1 do usunięcia (błąd `<link>`). Zadbać, by w Klaviyo nie zostały podpięte do żadnego live flow przed kasacją.

---

## E. Rekomendowana kolejność napraw

1. **P0 fakty** (A1 Fiberbiom, A2 dostawa, A3 Magda, A6 cena, C4 przypis IQVIA, A5 cytaty, A7 opinie) — zanim cokolwiek pójdzie live.
2. **P1 logika** (C1 NUR→zakup flow filter, C2 trigger vs. copy PUR, C3 dynamiczny kupon, C6 compliance claimów).
3. **P2 ton/technika** (B1 łagodzenie Bold, D1 bugi imienia, D2 płeć, B3/D3 font).
4. **Weryfikacja końcowa:** test render w Litmus/Email on Acid + wysyłka testowa z realnym profilem (sprawdzić personalizację, kupon, linki UTM), oraz przejście „NUR kupuje w kroku 2" na profilu testowym, by potwierdzić, że flow filter go wypycha.

---

## Załącznik — decyzje do podjęcia przez Ciebie

- **C1:** po zakupie w NUR → wypaść do standardowego post-purchase flow (zalecane) czy skrócony PUR?
- **C2:** rozdzielić PUR na osobny trigger `Placed Order` czy zmiękczyć copy?
- **A1:** czy bundle „Colostrum + Fiberbiom −15%" ma realnie powstać w Shopify (wtedy zostaje w mailu), czy usuwamy ofertę?
- **B1/B2:** jak mocno trzymać discount-urgency i emoji względem „naturalnego" tonu marki.

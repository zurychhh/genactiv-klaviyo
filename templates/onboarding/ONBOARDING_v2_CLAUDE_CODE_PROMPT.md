# Prompt do Claude Code — wdrożenie Onboarding v2 (Genactiv)

> Skopiuj całość poniżej do Claude Code w repo `genactiv-klaviyo`. Zawiera: przebudowę flow na 2 sekwencje, poprawki treści 20 szablonów (zweryfikowane fakty), QA i guardraile. Nic nie deployuje do produkcji bez Twojej zgody.

---

## ROLA I CEL

Jesteś agentem MCP/e-commerce w repo `genactiv-klaviyo`. Zadanie: wdrożyć **Onboarding v2** — rozbić obecny pojedynczy flow z podziałem warunkowym na **dwa niezależne flow rozdzielone triggerem** oraz nanieść poprawki merytoryczne na 20 istniejących szablonów. Masz do dyspozycji MCP: `klaviyo`, `shopify-extended`. Pracujesz po polsku, waluta PLN bez groszy, zachowujesz polskie znaki diakrytyczne w finalnym HTML.

Pełny kontekst projektu: `templates/onboarding/ONBOARDING_PLAN_v2.md` (architektura) oraz `templates/onboarding/ONBOARDING_REVIEW.md` (lista błędów). Ten prompt jest samowystarczalny — kluczowe fakty są poniżej.

---

## CZĘŚĆ 1 — Dwa flow w Klaviyo (konfiguracja, bez nowych maili)

20 istniejących szablonów mapuje się 1:1. Nie twórz nowych szablonów. Zbuduj 2 flow w trybie **Draft**, nie ruszaj v1 dopóki QA nie przejdzie.

### Flow B — Post-Purchase Onboarding (TYLKO pierwszy zakup)

- **Trigger:** Metric `Placed Order`.
- **Flow Filter:** `Placed Order` **equals 1** since the beginning of time. (Zdarzenie wyzwalające wlicza się jako 1 → pierwszozakupowy przechodzi, powracający ≥2 odpada.)
- **Re-entry:** Once per profile. **Smart Sending:** ON. Filtr rynku: PL/PLN.
- **Opóźnienia:** 0 → +3 dni → +4 → +5 → +7.
- **A/B:** 50/50 sticky split (Bold vs Editorial) wewnątrz flow.

| Krok | Delay | Bold (v2) | Editorial (v2) |
|---|---|---|---|
| 1 Welcome | 0 | TbkrJT | XRz3kF |
| 2 Ritual | +3 | VUtTbL | WHkGxx |
| 3 Effects | +4 | TAQHuL | V9Y5Zr |
| 4 Cross-sell | +5 | UCbxLy | Yb2iCZ |
| 5 Loyalty | +7 | XXJMMG | WVzts7 |

### Flow A — Newsletter Nurture (niekupujący)

- **Trigger:** Added to list `Shopify Newsletter` (ID `VT3KTz`).
- **Flow Filter:** `Placed Order` **zero times** since the beginning of time. (Robi podwójną robotę: wyklucza dotychczasowych klientów z sekwencji z kodem ORAZ wypycha każdego, kto kupi w trakcie — bo filtr re-ewaluuje przy każdym opóźnieniu.)
- **Conditional Split przed Krokiem 4 i 5:** `Placed Order since flow start = 0` → TAK: wyślij; NIE: pomiń do exit (twarde zabezpieczenie, by świeży kupujący nie dostał maila „kod wygasa").
- **Re-entry:** Once per profile. **Smart Sending:** ON.
- **Opóźnienia:** 0 → +1 dzień → +2 → +2 → +2.
- **A/B:** 50/50 sticky.

| Krok | Delay | Bold (v2) | Editorial (v2) |
|---|---|---|---|
| 1 Welcome+kod | 0 | WZHHPD | V22jtR |
| 2 Education | +1 | WP3t2G | UE5xY8 |
| 3 Social Proof | +2 | RxzyVm | Y8Sixx |
| 4 Reminder | +2 | WAVs7A | TB5HyJ |
| 5 Last Call | +2 | VPf8Qx | XcwJC4 |

---

## CZĘŚĆ 2 — Poprawki treści 20 szablonów (zweryfikowane fakty)

To są **edycje HTML/copy/danych**, nie nowy design. Nanieś dokładnie. Tam, gdzie podana cena może być nieaktualna — **pobierz live przez `shopify-extended` MCP**, nie wpisuj na sztywno.

### Tabela faktów (ground truth — genactiv.pl, 2026-06-22)

| Pole | Wartość poprawna |
|---|---|
| Darmowa dostawa | **od 300 zł** (NIE 99 zł) |
| Fiberbiom | **15 saszetek**, **179,00 zł**, brak przeceny; skład: arabinogalaktan z kory modrzewia 5000 mg + liofilizat colostrum bovinum 1000 mg; wysyłka 24h |
| Colostrum kapsułki 60 | **POBIERZ LIVE z Shopify** (listingi zewn. 75–89 zł; „69 zł" prawdopodobnie nieaktualne) |
| Ekspert 1 | Monika Stromkie-Złomaniec — **Dietetyk** (nie „kliniczny") |
| Ekspert 2 | **dr hab. n. med. Maciej Hałasa** — specjalista immunolog |
| Ekspert 3 | **Magdalena Szymczak-Kępka — psycholog diagnosta, trycholog** (NIE „Magda, Farmaceuta") |
| Colostrum Junior | istnieje (zawiesina 150 ml / saszetki czarny bez) — nazwa OK |
| Źródło „nr 1" | IQVIA Poland Pharmascope, kat. odporność (OTC3: 05F1 Immunostimulant Preparati, Molecule: Colostrum), **MAT 12/2024** |
| Dane spółki | Genactiv Sp. z o.o., Polna 13/3, 62-070 Dąbrówka, NIP 9721202218 |
| Kolor marki | `#F5333F` |

### Poprawki per szablon

**Wszystkie maile (globalnie):**
- Każde wystąpienie „**Colostrum nr 1 w aptekach**" musi mieć `*` i przypis źródła IQVIA (jak wyżej). Dziś jest tylko w NUR3.
- Polskie znaki diakrytyczne w treści. Link `{% unsubscribe 'Anuluj subskrypcję' %}` obecny. UTM na każdym linku.
- Formy żeńskie („dołączyłaś", „Zostawiłaś") → **bezosobowe** („dziękujemy za dołączenie", „Twój kod czeka").

**NUR — `NurOnb1A` / `NurOnb1B` (Welcome + kod):**
- Bug personalizacji: `Czesc{{ first_name|default:'' }}!` → dodaj spację: `Cześć {{ first_name|default:'' }}!` i zadbaj o poprawne zdanie bez imienia.
- `dziękujemy, że dołączyła{{ first_name }}` → przebuduj, imię nie może być doklejone do czasownika.
- „Darmowa dostawa od 99 zł" → **300 zł** (lub usuń, jeśli przy 1 produkcie próg jest nieosiągalny — patrz nota niżej).
- Product card: cena Colostrum **z Shopify live**.
- Liczba opinii „(412)": podłącz realne opinie albo **usuń licznik**.

**NUR — `NurOnb2A` / `NurOnb2B` (Education):**
- `NurOnb2B` cytat dr Hałasy: zostaw **tylko jeśli autoryzowany**; inaczej przeredaguj na bezosobowe („zdaniem ekspertów…").

**NUR — `NurOnb3A` / `NurOnb3B` (Social Proof):**
- Expert row: popraw tytuły wg tabeli (Magda → Magdalena Szymczak-Kępka, psycholog/trycholog; Monika „Dietetyk"; Hałasa pełne imię). Jeśli psycholog/trycholog nie pasuje do narracji o odporności — zaproponuj zamianę na realną osobę, nie zmyślaj zawodu.
- Opinie imienne („Karolina", „Tomasz" — „zweryfikowany zakup"): podłącz realne albo usuń etykietę „zweryfikowany zakup".
- Przypis IQVIA jest — zostaw.

**NUR — `NurOnb4A` / `NurOnb4B` (Reminder) i `NurOnb5A` / `NurOnb5B` (Last Call):**
- „Darmowa dostawa od 99 zł" → **300 zł**.
- Cena Colostrum **z Shopify live**; przelicz −15% od realnej ceny.
- **Mechanika kodu START15:** użyj dynamicznego kuponu Klaviyo z realną datą ważności per-profil (`{% coupon_code %}` z expiracją) zsynchronizowaną z timingiem (Krok 4 = „48h", Krok 5 = „dziś o północy"). Jeśli kod jest statyczny — copy o wygasaniu jest nieprawdziwe; albo zrób dynamiczny, albo zmień copy na uczciwe.

**PUR — `PurOnb1A` / `PurOnb1B` (Welcome):**
- Trigger to teraz `Placed Order`, więc „zamówienie jest już w drodze / dziękujemy za pierwszy zakup" jest poprawne — zostaw. Upewnij się, że nie koliduje z transakcyjnym potwierdzeniem Shopify (to osobny mail powitalny, nie potwierdzenie zamówienia).

**PUR — `PurOnb2A` / `PurOnb2B` (Ritual):**
- Dosage box „1–2 kapsułki dziennie" → dopasuj do etykiety produktu (zweryfikuj realne dawkowanie; źródła: 1–2 kaps., zwykle 2× dziennie, maks. 6/dobę).
- `PurOnb2B` cytat Moniki: autoryzowany albo bezosobowy.

**PUR — `PurOnb3A` / `PurOnb3B` (Effects):**
- Złagodź twarde health-claims („Twoje 8 tygodni", „więcej energii") do ostrożnego poziomu strony („naturalne wsparcie bariery"), bez sztywnych obietnic efektu. Cytat Hałasy — jak wyżej.

**PUR — `PurOnb4A` / `PurOnb4B` (Cross-sell Fiberbiom):**
- Product card: **15 saszetek**, **179,00 zł**, **usuń** przekreślenie „~~92,00~~ 79,00" i licznik „(128)".
- Oferta „−15% w zestawie z Colostrum": **potwierdź w Shopify, że istnieje**; jeśli nie — usuń. Nie obiecuj nieistniejącej promocji.

**PUR — `PurOnb5A` / `PurOnb5B` (Loyalty):**
- Nazwy linii OK (Fiberbiom, DERMO, Zooggies, Colostrum Junior). Zostaw, zweryfikuj tylko linki/UTM.

---

## CZĘŚĆ 3 — Kolejność prac

1. **Najpierw poprawki treści** (Część 2) na 20 szablonach przez `klaviyo` MCP (`klaviyo_update_email_template`), ceny z `shopify-extended`. Wymagane: pełny HTML z `<html>`/`<body>`, `{% unsubscribe %}`.
2. **Potem 2 flow** (Część 1) w Draft.
3. **QA** (niżej).
4. **Przełączenie** dopiero po Twojej akceptacji.

---

## CZĘŚĆ 4 — QA (kryteria akceptacji)

Na profilach testowych:
- **Profil A:** zapis do newslettera, brak zakupu → przechodzi cały Flow A (5 maili), kody/linki/UTM działają.
- **Profil B:** zapis do newslettera, **zakup po Kroku 2** → potwierdź, że (a) wypada z Flow A przy najbliższym kroku, (b) NIE dostaje maila „kod wygasa", (c) wchodzi do Flow B od Welcome.
- **Profil C:** zakup bez newslettera → wchodzi do Flow B.
- **Profil D:** drugi zakup tego samego profilu → Flow B **NIE** startuje (filtr „equals 1").
- Render: sprawdź w podglądzie Klaviyo dark/light, mobile <480px, brak złamań personalizacji (imię ze spacją, brak form żeńskich), ceny zgodne z live Shopify.

---

## GUARDRAILE

- Nie deployuj do produkcji ani nie kasuj v1/starych szablonów bez wyraźnej zgody. v1 zostaje aktywny do końca QA; dopiero potem Manual/Draft → archiwizacja → kasacja 20 szablonów v1 z błędem `<link>`.
- Nie zapisuj ani nie loguj sekretów/tokenów (Shopify, Klaviyo). Korzystaj z istniejącej konfiguracji MCP.
- Każdą cenę/promocję/dawkowanie bierz z systemu źródłowego (Shopify/etykieta), nie wpisuj na sztywno wartości, które mogły się zmienić.
- Nie wymyślaj opinii ani cytatów ekspertów — albo realne i autoryzowane, albo bezosobowe.

## NOTA decyzyjna (zapytaj użytkownika, jeśli blokuje)
- Próg darmowej dostawy 300 zł przy mailu z 1 produktem (~69–89 zł) jest nieosiągalny — zostawić komunikat, przenieść na cross-sell, czy pominąć?
- Czy istnieje realny bundle „Colostrum + Fiberbiom −15%"?
- Czy cytaty ekspertów są autoryzowane?

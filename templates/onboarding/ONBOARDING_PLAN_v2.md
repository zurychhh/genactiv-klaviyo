# Genactiv Onboarding v2 — architektura dwóch flow

> Data: 2026-06-22 · Status: projekt do wdrożenia
> Zmiana vs v1: jeden flow z podziałem „kupił kiedykolwiek?" → **dwa niezależne flow rozdzielone triggerem**.
> Zasada nadrzędna: jeden flow = jeden cel = jeden trigger. Zero zagnieżdżonej logiki ratunkowej, zero „onboarding-v2 dla NUR-który-kupił".

---

## 0. Cel i decyzja architektoniczna

**Problem v1:** podział warunkowy „Złożone zamówienie (kiedykolwiek)" liczył się raz, na wejściu. Osoba z gałęzi no-purchase, która kupiła w trakcie, dalej dostawała maile „kod wygasa / ostatnia szansa".

**Rozwiązanie v2 — dwa flow:**

```
Flow A — Newsletter Nurture          Flow B — Post-Purchase Onboarding
Trigger: Added to list               Trigger: Placed Order
         "Shopify Newsletter"        Flow Filter: TYLKO pierwszy zakup
Flow Filter: Placed Order            Cel: edukacja po pierwszym zakupie
  zero times (od początku)                (rytuał, efekty, cross-sell, loyalty)
Cel: konwersja niekupujących
```

**Kluczowa mechanika:** kto jest w Flow A i kupi (w tym z kodem START15), automatycznie wypada z Flow A (filtr `Placed Order zero times` re-ewaluuje się przy każdym opóźnieniu) i — ponieważ zakup sam odpala trigger `Placed Order` — wpada do Flow B jako pierwszozakupowy. **Nie potrzeba żadnej trzeciej sekwencji ani logiki przenoszenia.**

---

## 1. Flow B — Post-Purchase Onboarding (rdzeń decyzji: tylko pierwszy zakup)

### 1.1 Trigger i filtry

| Ustawienie | Wartość | Po co |
|---|---|---|
| Trigger | Metric: **Placed Order** | Realny zakup, nie zapis do listy |
| Flow Filter #1 | **Placed Order equals 1 since the beginning of time** | „Tylko pierwszy zakup". Zdarzenie wyzwalające liczy się jako 1 — klient powracający ma 2+, więc odpada |
| Flow Filter #2 (opcja) | Customer property: kraj = PL / waluta = PLN | Tylko rynek polski |
| Re-entry | **Once per profile** (bez ponownego wejścia) | Onboarding ma się odbyć raz |
| Smart Sending | ON | Bez zalewania nadawaniem |

> Uwaga do „equals 1": Klaviyo wlicza zdarzenie wyzwalające do licznika metryki w momencie ewaluacji filtra. Dlatego dla pierwszego zamówienia licznik = 1 (przechodzi), a dla każdego kolejnego ≥ 2 (odpada). To jest udokumentowany wzorzec „first-purchase flow".

> Drugie i kolejne zamówienia: **świadomie nie wyzwalają Flow B.** Powracający klienci to osobna historia (replenishment / win-back) — poza zakresem tego dokumentu.

### 1.2 Efekt uboczny — naprawia błąd z review (C2)

Skoro Flow B startuje w momencie zakupu, copy „Twoje zamówienie jest już w drodze / dziękujemy za pierwszy zakup" jest **prawdziwe**. W v1 (trigger = newsletter) bywało fałszywe. Przejście na trigger `Placed Order` rozwiązuje to bez zmiany treści.

### 1.3 Sekwencja (mapowanie istniejących szablonów PUR)

Opóźnienia bez zmian: 0 → +3 → +4 → +5 → +7 dni.

| Krok | Opóźnienie | Cel | Szablon A (Bold) | Szablon B (Editorial) |
|---|---|---|---|---|
| 1 Welcome | 0 (od zakupu) | Potwierdzenie, „co dalej" | `Onboarding \| Krok 1 \| Welcome (Bold) v2` (TbkrJT) | (XRz3kF) |
| 2 Ritual | +3 dni | Jak stosować | (VUtTbL) | (WHkGxx) |
| 3 Effects | +4 dni | Oś czasu efektów | (TAQHuL) | (V9Y5Zr) |
| 4 Cross-sell | +5 dni | Fiberbiom | (UCbxLy) | (Yb2iCZ) |
| 5 Loyalty | +7 dni | Cała rodzina Genactiv | (XXJMMG) | (WVzts7) |

A/B (Bold/Editorial) realizowany **wewnątrz** Flow B przez 50/50 sticky split — bez zmian.

---

## 2. Flow A — Newsletter Nurture (dawne NUR)

### 2.1 Trigger i filtry

| Ustawienie | Wartość | Po co |
|---|---|---|
| Trigger | Added to list **"Shopify Newsletter"** (VT3KTz) | Zapis do newslettera |
| Flow Filter | **Placed Order zero times since the beginning of time** | Robi podwójną robotę (niżej) |
| Re-entry | Once per profile | |
| Smart Sending | ON | |

**Dlaczego jeden filtr `Placed Order zero times (od początku)` wystarcza za cały split z v1:**

1. **Wyklucza dotychczasowych klientów** — ktoś, kto już kiedyś kupił i teraz zapisuje się do newslettera, ma licznik > 0 → nie dostaje sekwencji z kodem „−15% na pierwsze zamówienie" (która byłaby dla niego nietrafiona).
2. **Wypycha kupujących w trakcie** — filtry flow są re-ewaluowane przy każdym opóźnieniu; gdy ktoś kupi (np. z START15 po Kroku 1), licznik rośnie > 0 i przy najbliższym kroku osoba **wychodzi** z Flow A. Jednocześnie jej zakup odpala Flow B.

To jest sedno „ogrania w czysty sposób": stan zmienia się raz (zakup), a obie reakcje — wyjście z A i wejście do B — dzieją się automatycznie, bez ręcznych mostków.

### 2.2 Sekwencja (mapowanie istniejących szablonów NUR)

Opóźnienia bez zmian: 0 → +1 → +2 → +2 → +2 dni (dzień 0,1,3,5,7).

| Krok | Opóźnienie | Cel | Szablon A (Bold) | Szablon B (Editorial) |
|---|---|---|---|---|
| 1 Welcome + kod | 0 | Powitanie + START15 | `Onboarding NUR \| Krok 1 \| Welcome (Bold) v2` (WZHHPD) | (V22jtR) |
| 2 Education | +1 dzień | Dlaczego colostrum | (WP3t2G) | (UE5xY8) |
| 3 Social Proof | +2 dni | Nr 1 w aptekach, opinie | (RxzyVm) | (Y8Sixx) |
| 4 Reminder | +2 dni | Kod wygasa za 48h | (WAVs7A) | (TB5HyJ) |
| 5 Last Call | +2 dni | Kod znika dziś | (VPf8Qx) | (XcwJC4) |

### 2.3 Zabezpieczenie okna kolizji (między opóźnieniami)

Filtr re-ewaluuje przy opóźnieniach, więc teoretycznie między dwoma krokami świeży kupujący może złapać jeszcze jeden mail NUR zanim wypadnie. Zabezpieczenie minimalne, bez nowej sekwencji:

- **Conditional Split przed Krokami 4 i 5** (te z kodem/urgency): `Placed Order since flow start = 0` → TAK: wyślij; NIE: pomiń do exit. To gwarantuje, że nikt, kto już kupił, nie dostanie „ostatnia szansa na kod".

---

## 3. Pełny obraz przepływu osoby

```
Zapis do newslettera ──► Flow A (Newsletter Nurture)
                              │
                   ┌──────────┴───────────┐
                   │                      │
              nie kupuje              kupuje (np. START15)
                   │                      │
         dochodzi do Last Call    filtr „Placed Order zero" wypycha z Flow A
              i kończy A                  │
                                  Placed Order odpala ──► Flow B (jeśli 1. zakup)
                                                              │
                                                   Welcome → Ritual → Effects
                                                   → Cross-sell → Loyalty
```

Kupujący „od ulicy" (bez newslettera) wpada wprost do Flow B — bo trigger to zakup, nie lista. Spójnie dla wszystkich pierwszozakupowych.

---

## 4. Edge case'y i domyślne decyzje

| Sytuacja | Zachowanie v2 | Status |
|---|---|---|
| NUR kupuje w trakcie | Wypada z A, wpada do B (1. zakup) | Rozwiązane filtrami |
| Dotychczasowy klient zapisuje się do newslettera | Nie wchodzi do sekwencji z kodem (filtr A) | Domyślnie: brak osobnego flow. Opcjonalnie mini „welcome back" (1 mail) — patrz §6 |
| Kupujący bez newslettera | Wchodzi do B, omija A | Spójne |
| Drugi/kolejny zakup | Nie wyzwala B (filtr „equals 1") | Zgodne z „tylko pierwszy zakup" |
| Zakup dokładnie w oknie między krokami A | Conditional split przed Krok 4/5 blokuje mail z kodem | Zabezpieczone |
| Zwrot/anulacja 1. zamówienia | B już wystartował — rozważyć filtr na „Placed Order" netto | Do decyzji, niski priorytet |

---

## 5. Migracja v1 → v2 (kroki)

1. **Zbuduj równolegle.** Utwórz Flow A i Flow B w trybie Draft (nie ruszaj v1 live).
2. **Podłącz szablony v2** (te same 20 co teraz; treść poprawiamy wg `ONBOARDING_REVIEW.md` — osobny tor).
3. **Ustaw filtry** dokładnie jak w §1.1 i §2.1; re-entry „once per profile"; Smart Sending ON.
4. **QA na profilach testowych:**
   - profil A: zapis do newslettera, brak zakupu → przejście całego Flow A;
   - profil B: zapis do newslettera, **zakup po Kroku 2** → potwierdź wyjście z A i wejście do B;
   - profil C: zakup bez newslettera → wejście do B;
   - profil D: drugi zakup → potwierdź, że B się NIE odpala.
5. **Przełącz:** włącz A i B (Live), równocześnie ustaw v1 na Manual/Draft (stop wejść).
6. **Wygaszanie:** po potwierdzeniu, że nikt nie jest „w locie" w v1, zarchiwizuj v1 i skasuj 20 szablonów v1 z błędem `<link>` (lista w `ONBOARDING_PLAN.md`).

---

## 6. Otwarte decyzje (Twoje)

1. **Dotychczasowy klient + zapis do newslettera:** zostawiamy bez maila z A (domyślnie), czy dokładamy lekki „welcome back" (1 mail, bez kodu)? Rekomendacja: na start bez — trzymamy schludnie; dołożyć później, jeśli dane pokażą wolumen.
2. **Zwroty 1. zamówienia:** czy zabezpieczać Flow B filtrem na zwrot/anulację? Rekomendacja: pominąć w v2, niski wolumen, wysoki koszt komplikacji.
3. **Replenishment / 2. zakup:** osobny flow w przyszłości (poza zakresem v2).

---

## 7. Czego v2 świadomie NIE robi

- Nie tworzy „onboarding-v2 dla NUR-który-kupił" — to byłaby łatka mnożąca byty.
- Nie skleja NUR i PUR w jeden graf ze splitami — to wracało do nieczytelności v1.
- Nie dubluje powitań — kupujący dostaje JEDNĄ ścieżkę powitalną (Flow B), nie A+B równolegle.

Efekt na 5 kryteriach: schludność (1 flow = 1 cel), organizacja (rozdział wg triggera), skalowalność (B obsługuje wszystkich pierwszozakupowych), zarządzalność (edycja/pauza/analityka osobno), czytelność (dwa liniowe ciągi zamiast drzewa).

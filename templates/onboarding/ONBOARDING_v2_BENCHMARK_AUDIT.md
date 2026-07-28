# Audyt: benchmark e-mail vs. Onboarding v2

> Data: 2026-06-22 · Wejście: `benchmark-email-genactiv.html` (5 marek, ~94 maile) vs. `ONBOARDING_PLAN_v2.md` + `ONBOARDING_REVIEW.md`
> Pytanie: jak research ma się do tego, co już zaplanowaliśmy.

---

## 0. Wniosek nadrzędny (najważniejsze)

Benchmark **potwierdza kierunek** v2 (welcome jako seria, oś czasu efektów, scoping „tylko 1. zakup"), ale ujawnia rzecz, której plan v2 **nie uwzględniał: realny inwentarz istniejących flow i przychodów**. To rodzi jedno krytyczne ryzyko:

**Ryzyko duplikacji.** Research pokazuje, że już istnieje live welcome flow **`STdfpu`** (1 mail, ~273 tys. PLN/rok, 81% przychodu z flow, open 61%) oraz **draft onboardingu `UXajkz` (ROC_Onboarding)**. Nasz plan v2 opisuje budowę „Flow A (newsletter)" i „Flow B (post-purchase)" tak, jakby budować od zera. Jeśli Claude Code utworzy je jako **nowe** flow, powstaną **dwa welcome'y na tym samym subskrybencie**.

➡️ **Flow A nie jest nowym flow — to upgrade `STdfpu` z 1 maila do serii (dokładnie rekomendacja #01 z research). Flow B to dokończenie draftu `UXajkz`, nie nowy byt.** To trzeba dopisać do promptu dla Claude Code jako krok „discovery first" (`get_flows`, mapowanie, zero duplikatów). Szczegóły w §5.

---

## 1. Scorecard — 8 rekomendacji research vs. nasz plan

| # | Rekomendacja research | Status w naszym planie | Akcja |
|---|---|---|---|
| 01 | Welcome series zamiast 1 maila (źr. `STdfpu`, 273k PLN) | ✅ **Pokryte i przewyższone** — Flow A = 5 maili NUR z kodem | Podpiąć pod `STdfpu`, nie tworzyć nowego |
| 02 | Porzucony koszyk — przepisz copy + trik „Re:" (`YkhmXm`) | ⬜ Poza zakresem onboardingu (osobny flow) | Zostawić jako osobny tor; nie mieszać do v2 |
| 03 | List założyciela/eksperta + onboarding plain-text (IM8, ARMRA) | ❌ **Luka** — nasz PUR to ciężki HTML, brak plain-text i listu | **Dodać** do Flow B (mamy ekspertów: Hałasa/Monika) — §3 |
| 04 | Replenishment — uzupełnienie zapasu (`WgXWvU`, AOV 285 PLN) | ⬜ Świadomie poza zakresem v2 | Nasz filtr „tylko 1. zakup" **zostawia czystą drogę** pod replenishment — §3 |
| 05 | Browse abandonment — fix open 20% (`VfCSbb`) | ⬜ Poza zakresem | Osobny tor |
| 06 | Oferta tierowana + reframing ceny w welcome (IM8, Spacegoods) | ⚠️ Częściowo — mamy single START15 −15% | Rozważyć „single −10% / zestaw −20%" + „X zł dziennie" — §3 |
| 07 | Gra/wspólnota zamiast kolejnego rabatu (IM8, Spacegoods) | ⬜ Poza zakresem (kampanie) | Osobny tor |
| 08 | Wzorcowa stopka EU + sprzątanie martwych draftów (AG1) | ✅ **Zbieżne z review** (compliance, kasacja v1) | **Połączyć** z poprawkami z review — §4 |

Legenda: ✅ pokryte · ⚠️ częściowo · ❌ luka · ⬜ poza zakresem onboardingu.

---

## 2. Co research POTWIERDZA w naszym planie (nie zmieniamy)

- **Welcome jako seria z kodem** (rec #01) — 5/5 marek robi powitanie + 2–4 przypomnienia. Nasze Flow A dokładnie to realizuje. Kierunek słuszny.
- **Oś czasu efektów** — IM8 „Week 1: Energy. Week 2: Clarity" zarządza oczekiwaniami i tnie churn. Nasz **PUR Krok 3 „Twoje 8 tygodni"** to ten sam ruch — dobry pomysł (uwaga: łagodzić health-claims wg review, ale koncept zostaje).
- **Scoping „tylko pierwszy zakup" w Flow B** — okazuje się **trafny**: drugi+ zakup należy do replenishment (`WgXWvU`), nie do onboardingu. Nasz filtr `Placed Order equals 1` zostawia replenishment czysty lane. Architektura się broni.
- **Sticky A/B i jeden kod** — AG1 pokazuje dyscyplinę „jeden powtarzalny kod"; nasz START15 jest spójny (pod warunkiem realnej daty ważności z review).

---

## 3. Czego nasz plan NIE obejmuje, a research mocno sugeruje (do decyzji)

### 3a. Plain-text „list od eksperta" w onboardingu (rec #03) — rekomendowane
IM8 i ARMRA wstawiają w onboarding **osobisty plain-text** od nazwanej osoby (założyciel/lekarz), nie od „Brand®". Daje wyższe zaufanie i lepszą dostarczalność niż ciężki HTML. Mamy gotowe twarze: **dr hab. n. med. Maciej Hałasa** i **Monika Stromkie-Złomaniec**.
**Propozycja:** dołożyć do Flow B jeden mail plain-text (np. między Krok 2 a 3) — „Dlaczego warto dać colostrum czas" podpisany przez eksperta, nadawca = imię osoby. Niski koszt, wysoki zwrot na zaufaniu. (Uwaga z review A5: cytaty/treść muszą być autoryzowane.)

### 3b. Replenishment jako następny krok (rec #04) — najwyższy zwrot, poza v2
Research: to **#1 brakujący przychód** dla produktu konsumowalnego (AOV ~285 PLN, draft `WgXWvU` leży). Nie wciągamy go do v2 (słusznie), ale **Flow B pierwszozakupowy jest jego naturalnym wejściem**: po onboardingu klient płynnie przechodzi do replenishment przy 2. cyklu. Zarekomendować jako kolejny build zaraz po v2.

### 3c. Oferta tierowana + „X zł dziennie" w welcome (rec #06) — opcjonalne
Spacegoods: „Choose your offer" single −10% / zestaw −20%. IM8: „$6 dziennie". To **łączy się z problemem z review** (darmowa dostawa od 300 zł nieosiągalna przy 1 produkcie): **zestaw −20% podbija koszyk w stronę 300 zł** i czyni próg dostawy sensownym. Plus reframing ceny colostrum „już od X zł dziennie" (cena / liczba porcji).
**Propozycja:** rozważyć w NUR Krok 1 wariant single vs zestaw zamiast jednego START15 — ale to zmiana oferty, nie tylko copy; decyzja biznesowa.

---

## 4. Zbieżności z review do POŁĄCZENIA (jeden tor, nie dwa)

Rekomendacja #08 (research) i część `ONBOARDING_REVIEW.md` mówią to samo — scalić w jedno zadanie dla Claude Code:

- **Uniwersalna stopka EU** (AG1 wzorzec): oznaczenia zdrowotne, disclaimer „nie zastępuje zróżnicowanej diety…", adres (Polna 13/3, Dąbrówka), wypis. To realizuje też nasze uwagi z review o compliance i o stopce „powód otrzymania maila".
- **Sprzątanie**: research wskazuje 3 puste drafty `RjR6ms`, `UvyzDs`, `X4f2iP` (+ inne martwe) do archiwizacji — dorzucić do naszej listy kasacji 20 szablonów v1 z błędem `<link>`. Jeden przebieg porządkowy.

---

## 5. Rewizja JEDNEGO punktu z review (research zmienia ocenę)

**Review B1** sugerował łagodzenie twardego urgency w wariantach Bold NUR (jako możliwy zgrzyt z „naturalnym" tonem marki). **Benchmark to koryguje:** bezpośredni konkurenci w kategorii (ARMRA-colostrum, Seed, AG1) **wszyscy** stosują mocne urgency — „ENDS TONIGHT", „LAST CALL", countdowny, piętrzenie pilności. To **standard kategorii**, nie ekscentryzm.
➡️ **Korekta rekomendacji:** urgency w NUR4/NUR5 **zostawiamy** — problemem nie jest sama pilność, tylko spójność głosu i realna data wygaśnięcia kodu (to dalej obowiązuje z review C3). Zdejmuję B1 z listy „do złagodzenia".

---

## 6. Konkretne zmiany do dopisania w `ONBOARDING_v2_CLAUDE_CODE_PROMPT.md`

1. **Krok 0 — discovery (NOWY, na początku):** „Użyj klaviyo MCP `get_flows`. Zmapuj istniejące: welcome `STdfpu`, onboarding draft `UXajkz`, koszyk `YkhmXm`, replenishment `WgXWvU`, browse `VfCSbb`, puste drafty `RjR6ms/UvyzDs/X4f2iP`. **Flow A = rozbudowa `STdfpu` do serii, NIE nowy flow. Flow B = dokończenie `UXajkz`.** Zero duplikatów. Pokaż mapowanie, zanim cokolwiek utworzysz."
2. **Metryka konwersji:** w raportach flow użyć `Placed Order = R6aTMS`.
3. **Consent:** warunek wejścia Flow A musi zawierać „subscribed" (zgoda), nie samo dodanie do listy.
4. **(Opcja) plain-text expert letter** w Flow B — patrz §3a.
5. **Stopka EU + sprzątanie** — scalić z review (§4).
6. **Urgency NUR** — zostawić (§5), pilnować tylko realnej daty kodu.
7. **Nota dla właściciela:** replenishment (`WgXWvU`) i oferta tierowana (#06) jako kolejne kroki po v2 — nie w tym wdrożeniu.

---

## 7. Jednozdaniowo

Research nie wywraca v2 — **potwierdza go i ustawia w szerszym ekosystemie flow**; jedyna twarda poprawka to **podpięcie naszych dwóch flow pod istniejące `STdfpu`/`UXajkz` zamiast tworzenia duplikatów**, a największa wartość poza zakresem to **replenishment**, pod który v2 (1. zakup) już przygotował grunt.

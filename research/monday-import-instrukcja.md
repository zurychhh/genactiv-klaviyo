# Monday — import sprintu czerwiec 2026 + automatyzacje (status gating + codzienne powiadomienie)

> **Blokada:** Monday MCP jest podłączony, ale konto zwraca `MCP_AGENT_NOT_AUTHORIZED`.
> Admin musi włączyć uprawnienie **„Public Hosted MCP"** w monday.com (Admin → API / Integracje).
> Dopóki to nieaktywne, nie utworzę tablicy/automatyzacji z poziomu agenta. Po włączeniu — zrobię całość automatycznie.
> Link: https://support.monday.com/hc/en-us/articles/28588158981266

Źródło danych: Arkusz **„Genactiv — Sprint Czerwiec 2026"** (Google Sheets) / `sprint-czerwiec-2026-tasks.csv`.

---

## 1. Import CSV → tablica Monday

Tablica: **Genactiv — Sprint Czerwiec 2026**. Import CSV, mapowanie kolumn:

| Kolumna w CSV | Typ kolumny Monday |
|---|---|
| ID | Text (klucz do zależności) |
| Zadanie | Item Name |
| Sprint | Dropdown (W1–W5) |
| Daty | Timeline / Date |
| Stream | Dropdown (A/B/C/D/E/OPS) |
| Owner | Dropdown (CC / CC+ / MAN) |
| Priorytet | Status (P1=czerwony, P2=pomarańcz, P3=szary) |
| Estymacja | Text |
| Wplyw KPI | Text |
| Zaleznosci (ID) | → patrz pkt 2 (kolumna Dependency) |
| Status poczatkowy | **Status** (zestaw niżej) |
| Brama reczna | Dropdown (3 wartości) |
| Definition of Done | Long Text |
| Prompt Claude Code | Long Text |

**Zestaw statusów (kolumna Status):**
`Do zrobienia` · `Zablokowane (zależność)` · `W toku` · `Wymaga ręcznej interwencji` · `Czeka na weryfikację (CC done)` · `Done`

---

## 2. Zależności (kolumna Dependency)

Dodaj natywną kolumnę **Dependency** („Zależne od"). CSV trzyma zależności jako ID (np. `A2`, `B2, E1`).
Import Monday dopasowuje zależności po **nazwie itemu**, nie po ID — więc po imporcie ustaw zależności jednym z dwóch sposobów:

- **Ręcznie:** w każdym zadaniu wskaż item(y) z kolumny `Zaleznosci (ID)`.
- **Automatycznie (po włączeniu MCP):** podaję skrypt — przejdę po itemach, zmapuję ID→item_id i ustawię Dependency. Mapę zależności mam w `build_sprint_june.py`.

Pełny graf zależności (kolejność krytyczna):
```
A2 → A3 ; A1,A2 → A5 ; A1,E2 → A4 → A6 → A7
E1 → E2 → E3 ; B1 → B2 → B3 → B4
C1 → C2,C3,C4 ; D1 → D2,D3
B4,D3,A7 → OPS2 ; (wszystkie) → OPS1
```

---

## 3. Ask #2 — status „bramki ręcznej" przed Done (automatyzacje)

Cel: zadanie z gotowym outcome (CC), które wymaga **ręcznej weryfikacji**, albo zadanie wymagające **ręcznej interwencji przed startem**, nie może trafić do `Done` bez przejścia przez właściwy status.

**Automatyzacja A — weryfikacja przed Done** (dotyczy 17 zadań z `Brama ręczna = Weryfikacja ręczna przed Done`):
> When **Status** changes to **Done** and **Brama ręczna** is **„Weryfikacja ręczna przed Done"** and the item has not passed **„Czeka na weryfikację (CC done)"**, then **set Status back to „Czeka na weryfikację (CC done)"** and **notify** the weryfikatora.

Praktyczny flow: CC kończy → ustawia `Czeka na weryfikację (CC done)` (nie `Done`). Człowiek weryfikuje → ręcznie `Done`. Automatyzacja powyżej pilnuje, by nikt nie przeskoczył kroku.

**Automatyzacja B — interwencja przed startem** (dotyczy A6, A7, D3, OPS2 z `Brama ręczna = Wymaga ręcznej interwencji przed startem`):
> When **Status** changes to **„W toku"** and **Brama ręczna** is **„Wymaga ręcznej interwencji przed startem"** and brak potwierdzenia interwencji, then **set Status to „Wymaga ręcznej interwencji"** and **notify** ownera.

**Automatyzacja C — odblokowanie zależności (spójność z grafem):**
> When **all dependencies (Dependency) are Done**, then change **Status** from **„Zablokowane (zależność)"** to **„Do zrobienia"**.

---

## 4. Ask #3 — codzienne powiadomienie o zadaniach wymagających ręcznej ingerencji

**Wariant natywny (rekomendowany)** — automatyzacja czasowa Monday:
> **Every day at 09:00**, notify **[osoba]**: items where **Status** is any of `Wymaga ręcznej interwencji`, `Czeka na weryfikację (CC done)`, `Zablokowane (zależność)`.

Dodatkowo można zbudować **widok/dashboard „⚑ Wymaga człowieka"** z filtrem na te 3 statusy — szybki podgląd na żywo.

**Wariant przez Claude (gdy chcesz bogatszą treść powiadomienia)** — zadanie zaplanowane po stronie agenta (codziennie rano): pobiera itemy z board, grupuje na „przed startem" vs „do weryfikacji", liczy ile blokuje ścieżkę krytyczną i wysyła jedno powiadomienie Monday (`create_notification`) + opcjonalnie update na itemie. Wymaga włączonego MCP.

---

## 5. Co zrobię od razu po włączeniu „Public Hosted MCP"
1. Utworzę tablicę + kolumny (z zestawem statusów i Dependency).
2. Zaimportuję 23 zadania i **ustawię zależności po ID** (skrypt z mapą z `build_sprint_june.py`).
3. Skonfiguruję 3 automatyzacje statusów (pkt 3) + codzienne powiadomienie (pkt 4).
4. Zwrócę link do tablicy i potwierdzę test (przejście statusu blokowane zgodnie z bramką).

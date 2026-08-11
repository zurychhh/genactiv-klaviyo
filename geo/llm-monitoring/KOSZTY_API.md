# VIII-A3 · Dostępność i koszt API — brama decyzyjna

**Data analizy:** 2026-08-11
**Status:** czeka na decyzję (zgodnie z zadaniem: „NIE kupuj nic samodzielnie — zwróć koszt i czekaj na decyzję")

## Wniosek w jednym zdaniu

Pomiar da się uruchomić **za darmo** na Gemini (free tier w całości pokrywa nasze
zużycie), a dołożenie Perplexity kosztuje **ok. 0,45 zł miesięcznie** — brama budżetowa
z definicji zadania jest w praktyce bezprzedmiotowa. Realną przeszkodą nie jest koszt,
tylko **założenie kont i wygenerowanie kluczy**.

## Skala zużycia

Set kontrolny: **20 zapytań**, pomiar **raz w miesiącu**, na silnik.
To 20 wywołań API na silnik na miesiąc — 240 rocznie.

## Perplexity API

| Pozycja | Stawka | Nasze zużycie | Koszt / mies. |
|---|---|---|---|
| `sonar` input | $1 / 1M tok. | ~800 tok. | $0,0008 |
| `sonar` output | $1 / 1M tok. | ~10 000 tok. | $0,01 |
| Request fee (low context) | $5 / 1000 req. | 20 req. | $0,10 |
| **Razem** | | | **≈ $0,11 (~0,45 zł)** |

Rocznie: **≈ $1,32 (~5,40 zł)**.

- **Klucz:** perplexity.ai → Settings → API. Wymaga konta z kredytami (płatność kartą).
- **Uwaga:** stawka request fee rośnie z rozmiarem kontekstu wyszukiwania
  ($5–12/1000 dla `sonar`). Przy naszych krótkich zapytaniach to dolny próg.
- Droższe modele (`sonar-pro` $3/$15 za 1M) **nie są potrzebne** — mierzymy, czy marka
  pada w odpowiedzi, a nie jakość rozumowania.

## Gemini API

| Pozycja | Stawka | Nasze zużycie | Koszt / mies. |
|---|---|---|---|
| `gemini-2.5-flash` tokeny | $0,10–0,40 / 1M | ~11 000 tok. | < $0,01 |
| Grounding with Google Search | **1500 req./dzień gratis** (2.5) | 20 req./mies. | **$0** |
| **Razem** | | | **$0** |

- **Klucz:** aistudio.google.com → Get API key. **Darmowy**, bez karty.
- Nasze 20 zapytań miesięcznie to ułamek promila darmowego limitu — nawet gdyby free
  tier zniknął, koszt płatny to $0,28–0,70/mies.
- **Zastrzeżenie prywatności:** na darmowym tierze Google może wykorzystywać zapytania
  do trenowania modeli. Nasze zapytania to publiczne pytania zdrowotne (np. „czy błonnik
  pomaga na wzdęcia") — zero danych klienta, zero danych firmowych. Uznaję za akceptowalne.

## Czego te API NIE zmierzą

To jest ważniejsze niż koszt i trzeba to zapisać, zanim ktoś zaraportuje wynik jako
„widoczność w AI Overviews":

- **Gemini + grounding to nie są AI Overviews.** To inny system rankingowy, dostępny przez
  API. Traktujemy go jako *proxy*, a właściwy pomiar AI Overviews robimy ręcznie.
- **ChatGPT nie ma API** zwracającego cytowania w tym samym trybie, w jakim widzi je
  użytkownik w interfejsie. Też ręcznie.
- Stąd konstrukcja zadania: 2 silniki automatem + 2 ręcznie, na tym samym secie.

## Rekomendacja

**Wariant A (rekomendowany) — start na samym Gemini, teraz.**
Koszt zero, klucz darmowy i natychmiastowy, żadnej decyzji zakupowej. Daje baseline
sierpniowy dla jednego silnika automatycznego + dwóch ręcznych. Wystarczy, żeby domknąć
Definition of Done zadania.

**Wariant B — Gemini + Perplexity.**
Dokłada drugi, jakościowo najważniejszy silnik (Perplexity to realny produkt AI-search
z cytowaniami, najbliższy temu, co faktycznie mierzymy). Koszt ~0,45 zł/mies. Wymaga
konta z kredytami — czyli Twojej decyzji i karty.

**Czego nie robić:** nie kupować `sonar-pro` ani Deep Research. Do detekcji „czy marka
pada w odpowiedzi" to przepłacanie bez zysku pomiarowego.

## Co jest potrzebne ode mnie

Nic — skrypt jest gotowy i przetestowany. Po wpisaniu kluczy do głównego `.env`:

```
GEMINI_API_KEY=...
PERPLEXITY_API_KEY=...     # tylko w wariancie B
```

uruchomienie to `python3 geo/llm-monitoring/run.py --engines gemini` (lub `gemini,perplexity`).
Brak klucza = silnik pominięty, reszta pomiaru idzie dalej.

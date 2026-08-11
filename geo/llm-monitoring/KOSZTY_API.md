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

## Gemini API — ZWERYFIKOWANE NA ŻYWYM KLUCZU (2026-08-11)

**Pierwotne założenie „free tier wystarczy" NIE POTWIERDZIŁO SIĘ.** Przetestowane
na realnym kluczu z aistudio.google.com:

| Test | Wynik |
|---|---|
| `gemini-3.6-flash` — samo generowanie | **HTTP 200 OK** |
| `gemini-3.6-flash` — z `google_search` (grounding) | **HTTP 429 quota exceeded** |
| `gemini-3.1-flash-lite` — samo generowanie | HTTP 200 OK |
| `gemini-3.1-flash-lite` — z groundingiem | HTTP 429 quota exceeded |
| `gemini-2.5-flash` / `2.5-flash-lite` — cokolwiek | HTTP 404 „no longer available to new users" |

**Wniosek:** na czystym free tierze grounding jest niedostępny — darmowa pula
5000 wyszukiwań/mies. z cennika dotyczy tier płatnego (z podpiętym billingiem),
nie darmowego. Modele 2.5 są dla nowych kluczy wygaszone; aktualny model to `gemini-3.6-flash`.

**To dyskwalifikuje Gemini w wariancie darmowym.** Bez groundingu model nie zwraca
źródeł — mierzylibyśmy wtedy tylko, czy marka siedzi w wiedzy parametrycznej modelu,
a nie czy jest *cytowana* w AI-search. To inna metryka niż ta z Definition of Done.

| Pozycja | Stawka | Nasze zużycie | Koszt / mies. |
|---|---|---|---|
| `gemini-3.6-flash` tokeny | $1,50 / $7,50 za 1M | ~11 000 tok. | ~$0,08 |
| Grounding with Google Search | $14 / 1000 req., **5000/mies. gratis na tierze płatnym** | 20 req. | **$0** (w puli darmowej) |
| **Razem po włączeniu billingu** | | | **≈ $0,08 (~0,30 zł)** |

- **Co odblokowuje:** włączenie billingu (karta) na projekcie w AI Studio / Google Cloud.
  Po tym nasze 20 zapytań miesięcznie mieści się w darmowej puli 5000 — rachunek zostaje
  praktycznie zerowy, ale **karta jest wymagana**.
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

## Rekomendacja — PO WERYFIKACJI

Nie istnieje wariant „automat za zero złotych". **Każdy silnik zwracający cytowania
wymaga podpiętej karty** — Gemini przez billing na projekcie, Perplexity przez kredyty.
Same kwoty pozostają groszowe; barierą jest formalność, nie budżet.

**Wariant A′ — włącz billing na Gemini.** Klucz już mamy i działa; brakuje wyłącznie
billingu. Po włączeniu: ~0,30 zł/mies., grounding w darmowej puli 5000/mies.
Najmniejszy nakład, bo nie zakłada nowego konta.

**Wariant B — dołóż Perplexity (~0,45 zł/mies.).** Jakościowo najważniejszy silnik:
realny produkt AI-search z cytowaniami, najbliższy temu, co mierzymy. Osobne konto z kredytami.

**Wariant C — na razie sam pomiar ręczny.** ChatGPT + AI Overviews wg checklisty, zero kosztów
i zero kart. Daje baseline sierpniowy, ale bez części automatycznej — czyli bez powtarzalności
bez człowieka. Skrypt czeka gotowy.

**Czego nie robić:** nie kupować `sonar-pro` ani Deep Research. Do detekcji „czy marka
pada w odpowiedzi" to przepłacanie bez zysku pomiarowego. Nie uruchamiać też Gemini
bez groundingu „żeby coś zmierzyć" — to inna metryka i zafałszuje trend.

## Co jest potrzebne ode mnie

Nic — skrypt jest gotowy i przetestowany. Po wpisaniu kluczy do głównego `.env`:

```
GEMINI_API_KEY=...
PERPLEXITY_API_KEY=...     # tylko w wariancie B
```

uruchomienie to `python3 geo/llm-monitoring/run.py --engines gemini` (lub `gemini,perplexity`).
Brak klucza = silnik pominięty, reszta pomiaru idzie dalej.

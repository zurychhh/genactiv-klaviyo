# Co potrzebujemy do uruchomienia Senuto i Bing Ads w terminalu

> **Status na 2026-08-21:** Senuto — **URUCHOMIONE** (klucz dostarczony 2026-08-17).
> Bing Ads — nadal czeka na dane od klienta.

## 1. Senuto (SEO monitoring) — ✅ URUCHOMIONE 2026-08-17

**Co zyskujemy:** Widoczność domeny w Google, pozycje fraz kluczowych, analiza konkurencji, monitoring zmian pozycji — wszystko z poziomu terminala GenActiv Online.

**Wymagania — zamknięte:**

| Do zrobienia | Kto | Status |
|-------------|-----|--------|
| Plan Professional w Senuto | Klient | ✅ Aktywny (konto id 25830) |
| Wygenerować Bearer Token | Klient | ✅ Dostarczony 2026-08-17, ważny do **2026-09-17** |

**Co zostało wdrożone:**
- Klucz w głównym `.env` i podstawiony do `.mcp.json` — Senuto działa w lokalnym Claude Code.
- Klucz ustawiony na Railway + redeploy — Senuto działa też w terminalu GenActiv Online (produkcja miała martwy klucz od 2026-05-08, czyli konektor był tam nieczynny przez 3 miesiące).
- Pierwsze zadania na danych Senuto: mapa fraz dla 20 kart produktowych + gap analysis (`research/keyword-map-2026.csv`, `sprint-2026-06/W1/A1/artefakty/`) oraz priorytetyzacja setu zapytań GEO (`geo/llm-monitoring/queries.json` v1.0).

**⚠️ Rotacja tokena jest na razie RĘCZNA.** Token Senuto jest ważny 30 dni. Mechanizm auto-odnawiania (skrypt logujący się email+hasłem) **nie został zbudowany** — nie dostaliśmy danych logowania do konta, a sam token to za mało, żeby wygenerować kolejny.

**Do zrobienia przed 2026-09-17 — jedna z dwóch ścieżek:**
1. **Ręcznie:** klient generuje nowy token (panel Senuto → ustawienia API) i przekazuje nam; my aktualizujemy `.env` + Railway. Nakład: ~15 min raz w miesiącu.
2. **Automatycznie:** klient przekazuje email i hasło do konta Senuto — wtedy budujemy auto-odnawianie (~4h roboczo) i temat znika na stałe.

Objaw wygasłego tokena: wszystkie zapytania do Senuto zwracają pusty błąd `404`, a terminal odpowiada „brak danych" zamiast komunikatu o autoryzacji — dlatego nie da się tego zauważyć bez świadomego sprawdzenia.

---

## 2. Microsoft Advertising / Bing Ads (kampanie reklamowe)

**Co zyskujemy:** Zarządzanie kampaniami Bing Ads, raporty wydatków, ROAS, konwersje, słowa kluczowe — analogicznie do tego co mamy dla Google Ads.

**Wymagania:**

| Do zrobienia | Kto | Szczegóły |
|-------------|-----|-----------|
| Konto Microsoft Advertising z uprawnieniami Super Admin | Klient | ads.microsoft.com — jeśli konto już istnieje, potrzebujemy login Super Admina. |
| Zgoda na rejestrację aplikacji w Azure | Klient | Rejestrujemy aplikację w Azure Portal (portal.azure.com), żeby uzyskać dostęp API. To jednorazowa czynność. |
| Developer Token | Developer (my) | Wnioskujemy o niego w panelu Microsoft Ads. Wymaga zatwierdzenia przez Microsoft (zwykle w ciągu 1 dnia roboczego). |

**Co dostarczyć nam (developerom):**
1. Login i hasło do konta Microsoft Advertising (Super Admin) — potrzebne jednorazowo do wygenerowania tokenów OAuth
2. Zgoda na rejestrację aplikacji w Azure (możemy to zrobić wspólnie na screensharze)

**Koszt API:** Darmowy. Płacicie tylko za kliknięcia w reklamy (jak dotychczas). Sam dostęp do API nie kosztuje nic.

**Tokeny:** Access Token odnawiany automatycznie przez Refresh Token (tak samo jak mamy dla Google Ads). Nie wymaga ręcznej interwencji.

**Czas wdrożenia po otrzymaniu danych:** ~3-5 dni roboczych (większy zakres niż Senuto).

---

## Podsumowanie

| Konektor | Status | Co jeszcze potrzebujemy od klienta | Koszt dodatkowy |
|----------|--------|------------------------------------|-----------------|
| **Senuto** | ✅ Działa od 2026-08-17 | Nowy token do 2026-09-17 **albo** email+hasło do auto-odnawiania | ~29 EUR/mies |
| **Bing Ads** | ⏳ Czeka | Login Super Admin + zgoda na Azure app | 0 PLN (API darmowe) |

**Następny krok:** Bing Ads — zakres 3-5 dni roboczych po otrzymaniu dostępów.

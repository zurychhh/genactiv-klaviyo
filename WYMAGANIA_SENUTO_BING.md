# Co potrzebujemy do uruchomienia Senuto i Bing Ads w terminalu

## 1. Senuto (SEO monitoring)

**Co zyskujemy:** Widoczność domeny w Google, pozycje fraz kluczowych, analiza konkurencji, monitoring zmian pozycji — wszystko z poziomu terminala GenActiv Online.

**Wymagania:**

| Do zrobienia | Kto | Szczegóły |
|-------------|-----|-----------|
| Plan Professional w Senuto | Klient | Jedyny plan z dostępem do API. Koszt: ~29 EUR/mies. Dostępny 14-dniowy trial. |
| Wygenerować Bearer Token | Klient | Panel Senuto → ustawienia API → wygeneruj token. Token to ciąg znaków, który przekazujecie nam. |

**Ważna informacja o tokenie:** Token Senuto jest ważny 30 dni. Po tym czasie trzeba wygenerować nowy. Zbudujemy mechanizm auto-odnawiania (skrypt logujący się email+hasłem i generujący nowy token), więc po pierwszym ustawieniu nie trzeba będzie robić tego ręcznie.

**Co dostarczyć nam (developerom):**
1. Bearer Token z panelu Senuto
2. Email i hasło do konta Senuto (potrzebne do auto-odnawiania tokena)

**Czas wdrożenia po otrzymaniu danych:** ~1-2 dni robocze.

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

| Konektor | Co potrzebujemy od klienta | Koszt dodatkowy | Czas wdrożenia |
|----------|---------------------------|-----------------|----------------|
| **Senuto** | Plan Professional + Bearer Token + dane logowania | ~29 EUR/mies | 1-2 dni |
| **Bing Ads** | Login Super Admin + zgoda na Azure app | 0 PLN (API darmowe) | 3-5 dni |

**Rekomendacja:** Zaczynamy od Senuto — szybsze do wdrożenia i daje natychmiastową wartość SEO. Bing Ads robimy równolegle lub zaraz po.

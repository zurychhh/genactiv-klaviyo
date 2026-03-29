# Jak pozyskać Meta Access Token - Instrukcja krok po kroku

**Cel:** Utworzenie System User Access Token dla Meta Marketing API
**Czas:** ~30 minut
**Wymagania:** Dostęp Admin do Meta Business Manager

---

## ŚCIEŻKA SZYBKA (dla testów)

Jeśli chcesz tylko przetestować - użyj Graph API Explorer (token ważny 1-2h):
1. Idź do: https://developers.facebook.com/tools/explorer/
2. Wybierz swoją aplikację
3. Kliknij "Generate Access Token"
4. Skopiuj token

**UWAGA:** Ten token wygasa po 1-2h. Dla produkcji użyj System User Token (instrukcja poniżej).

---

## ŚCIEŻKA PRODUKCYJNA (System User Token)

### KROK 1: Utwórz Meta Developer App

1. **Otwórz:** https://developers.facebook.com/apps/

2. **Kliknij:** "Create App" (zielony przycisk)

3. **Wybierz Use Case:**
   - Kliknij "Other" → Next

4. **Wybierz App Type:**
   - Wybierz "Business" → Next

5. **Wypełnij dane:**
   - App name: `GenActiv Ads API` (lub dowolna nazwa)
   - App contact email: Twój email
   - Business Account: Wybierz konto GenActiv
   - Kliknij "Create App"

6. **Dodaj Marketing API:**
   - Na Dashboard aplikacji znajdź sekcję "Add products to your app"
   - Znajdź "Marketing API" i kliknij "Set Up"

7. **Przełącz na Live Mode:**
   - W górnym pasku przy nazwie aplikacji jest przełącznik "Development/Live"
   - Kliknij i przełącz na "Live"
   - (Może wymagać weryfikacji biznesu)

---

### KROK 2: Utwórz System User w Business Manager

1. **Otwórz:** https://business.facebook.com/settings/

2. **Nawiguj:** Users → System Users
   ```
   Business Settings
   └── Users
       └── System Users
   ```

3. **Kliknij:** "Add" (niebieski przycisk)

4. **Wypełnij:**
   - System User Name: `GenActiv-API-User`
   - System User Role: **Admin** (ważne!)
   - Kliknij "Create System User"

---

### KROK 3: Przypisz Assets do System User

1. **Zaznacz** utworzonego System User na liście

2. **Kliknij:** "Add Assets"

3. **W oknie "Add Assets":**

   **A) Dodaj Ad Account:**
   - Wybierz zakładkę "Ad Accounts"
   - Zaznacz konto reklamowe GenActiv
   - Poziom dostępu: **Full Control**
   - Kliknij "Save Changes"

   **B) Dodaj Pages (jeśli potrzebne):**
   - Wybierz zakładkę "Pages"
   - Zaznacz stronę GenActiv na Facebooku
   - Poziom dostępu: **Full Control**
   - Kliknij "Save Changes"

   **C) Dodaj App:**
   - Wybierz zakładkę "Apps"
   - Zaznacz aplikację `GenActiv Ads API` (utworzoną w Kroku 1)
   - Poziom dostępu: **Full Control**
   - Kliknij "Save Changes"

---

### KROK 4: Wygeneruj Access Token

1. **Wróć do:** Business Settings → Users → System Users

2. **Zaznacz** System User `GenActiv-API-User`

3. **Kliknij:** "Generate New Token"

4. **Wybierz aplikację:**
   - Select App: `GenActiv Ads API`

5. **Wybierz uprawnienia (WAŻNE!):**

   ☑️ **ads_read** - Odczyt danych reklamowych
   ☑️ **ads_management** - Zarządzanie kampaniami
   ☑️ **business_management** - Zarządzanie Business Manager
   ☑️ **pages_read_engagement** - Odczyt stron (opcjonalne)
   ☑️ **pages_show_list** - Lista stron (opcjonalne)

6. **Kliknij:** "Generate Token"

7. **SKOPIUJ TOKEN!**
   ```
   ⚠️ WAŻNE: Token wyświetla się TYLKO RAZ!
   Skopiuj go i zapisz w bezpiecznym miejscu.
   ```

---

## KROK 5: Zapisz Token bezpiecznie

### Opcja A: Plik .env (rekomendowane)

```bash
# Utwórz plik .env w projekcie
echo 'META_ACCESS_TOKEN=EAAG...' >> /Users/user/projects/genactiv-klaviyo/.env
```

### Opcja B: Zmienne środowiskowe

```bash
# Dodaj do ~/.zshrc lub ~/.bashrc
export META_ACCESS_TOKEN="EAAG..."
```

---

## WERYFIKACJA TOKENU

### Test w przeglądarce:

Wklej w przeglądarkę (zamień TOKEN na swój):
```
https://graph.facebook.com/v19.0/me?access_token=TOKEN
```

**Oczekiwany wynik:**
```json
{
  "name": "GenActiv-API-User",
  "id": "123456789"
}
```

### Test uprawnień:

```
https://graph.facebook.com/v19.0/me/adaccounts?access_token=TOKEN
```

**Oczekiwany wynik:** Lista kont reklamowych

---

## TROUBLESHOOTING

### Problem: "Invalid OAuth access token"
- Token wygasł lub jest nieprawidłowy
- Wygeneruj nowy token

### Problem: "User does not have permission"
- System User nie ma przypisanych Assets
- Wróć do Kroku 3 i dodaj Assets

### Problem: "App not in Live mode"
- Aplikacja jest w trybie Development
- Przełącz na Live w ustawieniach aplikacji

### Problem: "Business not verified"
- Meta wymaga weryfikacji biznesu dla niektórych uprawnień
- Idź do: Business Settings → Business Info → Verification

---

## WAŻNE INFORMACJE

| Element | Wartość |
|---------|---------|
| Ważność tokenu | **Permanent** (nie wygasa) |
| Odnowienie | Nie wymagane dla System User |
| Bezpieczeństwo | Traktuj jak hasło! |
| Limit API | 200 calls/user/hour (standard) |

---

## LINKI POMOCNICZE

- [Business Settings](https://business.facebook.com/settings/)
- [Meta Developers](https://developers.facebook.com/apps/)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)
- [Marketing API Docs](https://developers.facebook.com/docs/marketing-apis/)

---

## PO UZYSKANIU TOKENU

Wróć do Claude Code i uruchom instalację MCP:

```bash
pip install meta-ads-mcp

claude mcp add meta-ads -s user \
  -e META_ACCESS_TOKEN=TWOJ_TOKEN \
  -- python -m meta_ads_mcp
```

---

**KONIEC INSTRUKCJI**

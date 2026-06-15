# Jak przeniesc GenActiv na GitHub — instrukcja

Instrukcja krok po kroku: od utworzenia konta GitHub, przez rotacje tokenow, po klonowanie na nowej maszynie.

---

## Krok 1: Konto GitHub

Jesli nie masz konta:
1. Wejdz na https://github.com
2. Kliknij **Sign up** i postepuj wg instrukcji
3. Potwierdz email

Jesli masz konto — przejdz do kroku 2.

---

## Krok 2: Usuwanie starego repo (zurychhh/genactiv-klaviyo)

Stare repo zawiera wyciekniete tokeny w historii git. Nie da sie ich usunac — trzeba usunac cale repo.

1. Wejdz na https://github.com/zurychhh/genactiv-klaviyo
2. **Settings** (zakladka u gory) → przewin na sam dol
3. **Danger Zone** → **Delete this repository**
4. Wpisz nazwe repo (`zurychhh/genactiv-klaviyo`) i potwierdz

---

## Krok 3: Rotacja wyciekniętych tokenow

**KRYTYCZNE** — tokeny z historii git sa skompromitowane. Wygeneruj nowe:

### Meta (Facebook) Access Token
1. https://developers.facebook.com → Your App → **Settings** → **Basic**
2. Wygeneruj nowy **App Secret** (albo uzyj Graph API Explorer na nowy token)
3. Zapisz nowy token w `genactiv-online/.env` jako `META_ACCESS_TOKEN=...`

### Google Ads Developer Token
1. https://console.cloud.google.com → Twoj projekt
2. **APIs & Services** → **Credentials** — sprawdz czy token jest nadal aktywny
3. Developer Token: https://ads.google.com/aw/apicenter (konto MCC)
4. Jesli trzeba — wygeneruj nowy OAuth refresh token:
   ```bash
   cd google-ads-mcp && python generate_refresh_token.py
   ```

### Google OAuth Client Secret
1. https://console.cloud.google.com → **APIs & Services** → **Credentials**
2. Edytuj istniejacy OAuth 2.0 Client → **Reset secret**
3. Zaktualizuj `GOOGLE_OAUTH_CLIENT_SECRET` w `.env` i `genactiv-online/.env`

### Anthropic API Key
1. https://console.anthropic.com → **API Keys**
2. Wygeneruj nowy klucz, dezaktywuj stary
3. Zaktualizuj `ANTHROPIC_API_KEY` w `genactiv-online/.env`

### Shopify Access Token
1. https://admin.shopify.com → **Settings** → **Apps and sales channels** → **Develop apps**
2. Edytuj aplikacje → **API credentials** → wygeneruj nowy token
3. Zaktualizuj `SHOPIFY_ACCESS_TOKEN` w obu plikach `.env`

### Klaviyo API Key
1. https://www.klaviyo.com → **Settings** → **API Keys**
2. Wygeneruj nowy Private API Key, dezaktywuj stary
3. Zaktualizuj `KLAVIYO_API_KEY` w `genactiv-online/.env`

### TikTok App Secret
1. https://business-api.tiktok.com/portal/apps
2. Wygeneruj nowy App Secret
3. Zaktualizuj `TIKTOK_SECRET` w `.env`

### Baselinker Token
1. https://panel.baselinker.com → **Moje konto** → **API**
2. Wygeneruj nowy token
3. Zaktualizuj `BASELINKER_TOKEN` w `.env`

---

## Krok 4: Nowe repo na GitHub

1. https://github.com/new
2. **Repository name:** `genactiv-klaviyo`
3. **Visibility:** **Private** (wazne!)
4. NIE zaznaczaj "Add a README" (mamy juz pliki)
5. Kliknij **Create repository**

---

## Krok 5: Push lokalnego kodu

Na maszynie gdzie masz aktualny kod:

```bash
cd ~/projects/genactiv-klaviyo

# Usun stary remote (jesli istnieje)
git remote remove origin 2>/dev/null || true

# Dodaj nowy remote
git remote add origin git@github.com:zurychhh/genactiv-klaviyo.git

# Upewnij sie ze .mcp.json NIE jest w git
git rm --cached .mcp.json 2>/dev/null || true

# Sprawdz co bedzie commitowane
git status

# Commit + push
git add -A
git commit -m "Initial commit — clean repo (no secrets)"
git branch -M main
git push -u origin main
```

### Weryfikacja po push

Wejdz na https://github.com/zurychhh/genactiv-klaviyo i sprawdz:
- `.mcp.json` **NIE** istnieje w repo (jest w `.gitignore`)
- `.mcp.json.example` istnieje (szablon)
- `.env` **NIE** istnieje w repo (jest w `.gitignore`)
- `.env.example` istnieje (root + genactiv-online/)
- `generate_tiktok_token.py` **NIE** zawiera hardcoded secret

---

## Krok 6: Klonowanie na nowej maszynie

```bash
# 1. Klonuj
git clone git@github.com:zurychhh/genactiv-klaviyo.git
cd genactiv-klaviyo

# 2. Skopiuj pliki .env i uzupelnij tokeny
cp .env.example .env
cp genactiv-online/.env.example genactiv-online/.env
# Edytuj oba pliki i wpisz tokeny

# 3. Uruchom setup
chmod +x setup-claude.sh
./setup-claude.sh

# 4. Gotowe! Uruchom Claude Code
claude
```

---

## Krok 7: Railway (deploy produkcyjny)

Jesli korzystasz z Railway.app:

```bash
# Zaloguj sie
unset RAILWAY_TOKEN
railway login --browserless

# Ustaw zmienne srodowiskowe
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set KLAVIYO_API_KEY=pk_...
# ... (wszystkie zmienne z genactiv-online/.env)

# Deploy
railway up
```

---

## FAQ

**P: Czy moge uzyc HTTPS zamiast SSH do klonowania?**
T: Tak — zamiast `git@github.com:...` uzyj `https://github.com/zurychhh/genactiv-klaviyo.git`. GitHub bedzie pytal o haslo (lub Personal Access Token).

**P: Czy legacy katalogi (chat-ui/, dashboard-server/) powinny byc w repo?**
T: Tak — zostaja jako historia. Sa nieaktywne, nie przeszkadzaja.

**P: Co jesli zapomnialem zrotowac jakis token?**
T: GitHub automatycznie skanuje publiczne repo i powiadamia dostawcow (np. Anthropic uniewaznila klucz). Dla private repo — zrotuj wszystko recznie wg kroku 3.

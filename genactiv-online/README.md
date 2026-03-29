# GenActiv Online

Webowy terminal AI dla GenActiv.pl — dostęp do Klaviyo, Shopify i Meta Ads przez przeglądarkę.

## Szybki start (lokalnie)

```bash
cd genactiv-online
cp .env.example .env
# Uzupełnij .env kluczami API

# Wygeneruj hash hasła:
node -e "require('bcryptjs').hash('twoje-haslo', 10).then(console.log)"
# Wklej wynik do AUTH_PASSWORD_HASH w .env

npm install
npm run dev
# Otwórz http://localhost:3000
```

## Architektura

```
Przeglądarka → Express (auth + SSE) → Anthropic API ⇄ MCP servers
                                                      ├── Klaviyo
                                                      ├── Shopify Extended
                                                      ├── Shopify Standard
                                                      └── Meta Ads
```

## Deploy na Railway

1. Push do GitHub
2. Nowy projekt na Railway → "Deploy from GitHub"
3. Ustaw zmienne środowiskowe (patrz `.env.example`)
4. Railway automatycznie zbuduje z `Dockerfile`

## MCP Servers

| Serwer | Opis | Runtime |
|--------|------|---------|
| Klaviyo | Email marketing, kampanie, profile | Python (uvx) |
| Shopify Extended | Analytics, zamówienia, produkty | Node.js |
| Shopify Standard | Podstawowe operacje sklepowe | Node.js |
| Meta Ads | Facebook/Instagram reklamy | Python |

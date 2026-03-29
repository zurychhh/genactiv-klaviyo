# RESEARCH: Meta Ads MCP dla GenActiv

**Data:** 28 stycznia 2026
**Cel:** Integracja zarządzania Meta Ads (Facebook/Instagram) z Claude Code
**Analogia:** Jak obecny `google-ads-mcp` w projekcie

---

## 1. PODSUMOWANIE EXECUTIVE

Istnieją **3 gotowe rozwiązania MCP** dla Meta Ads, które można zintegrować z Claude Code analogicznie do Google Ads MCP. Rekomendacja: **pipeboard-co/meta-ads-mcp** (najlepsze dla produkcji) lub **gomarble-ai/facebook-ads-mcp-server** (najprostszy setup).

---

## 2. DOSTĘPNE ROZWIĄZANIA MCP

### 2.1 Pipeboard Meta Ads MCP ⭐ REKOMENDOWANY

| Cecha | Wartość |
|-------|---------|
| GitHub | https://github.com/pipeboard-co/meta-ads-mcp |
| PyPI | `pip install meta-ads-mcp` |
| Język | Python 3.10+ |
| Licencja | BSL 1.1 (free use, Apache 2.0 od 2029) |
| Tools | 25+ funkcji |

**Zalety:**
- Najlepsza dokumentacja
- Remote MCP (bez lokalnej instalacji) lub lokalna instalacja
- AI-powered campaign analysis
- Budget optimization
- Dynamic creative testing

**Wady:**
- Remote MCP płatny ($49/mies) - ale lokalna instalacja free
- Wymaga Meta Developer App dla lokalnej wersji

---

### 2.2 GoMarble Facebook Ads MCP ⭐ NAJPROSTSZY SETUP

| Cecha | Wartość |
|-------|---------|
| GitHub | https://github.com/gomarble-ai/facebook-ads-mcp-server |
| Instalacja | `npx @smithery/cli install @gomarble-ai/facebook-ads-mcp-server` |
| Język | Python |
| Licencja | MIT (pełna swoboda) |
| Tools | 20+ funkcji |

**Zalety:**
- One-click installation
- Automatyczne tworzenie tokenów (bez manual setup)
- Token przechowywany lokalnie (bezpieczeństwo)
- MIT License - pełna swoboda użycia

**Wady:**
- Mniej funkcji niż Pipeboard
- Brak AI-powered recommendations

---

### 2.3 brijr/meta-mcp (Node.js)

| Cecha | Wartość |
|-------|---------|
| GitHub | https://github.com/brijr/meta-mcp |
| Instalacja | `npm install -g meta-ads-mcp` |
| Język | Node.js/TypeScript |
| Licencja | Open source |
| Tools | 25 funkcji |

**Zalety:**
- Pełne zarządzanie kampaniami
- Custom & Lookalike audiences
- CSV/JSON export
- Multi-account support

**Wady:**
- Wymaga Node.js (nie Python jak reszta projektu)
- Więcej manualnej konfiguracji

---

## 3. PORÓWNANIE FUNKCJI

| Funkcja | Pipeboard | GoMarble | brijr/meta-mcp |
|---------|-----------|----------|----------------|
| **READ** |
| Lista kont reklamowych | ✅ | ✅ | ✅ |
| Kampanie | ✅ | ✅ | ✅ |
| Ad Sets | ✅ | ✅ | ✅ |
| Ads | ✅ | ✅ | ✅ |
| Insights/Analytics | ✅ | ✅ | ✅ |
| Creative preview | ✅ | ✅ | ✅ |
| **WRITE** |
| Tworzenie kampanii | ✅ | ❌ | ✅ |
| Tworzenie ad sets | ✅ | ❌ | ✅ |
| Tworzenie ads | ✅ | ❌ | ✅ |
| Upload obrazów | ✅ | ❌ | ✅ |
| Modyfikacja budżetu | ✅ | ❌ | ✅ |
| **ADVANCED** |
| AI recommendations | ✅ | ❌ | ❌ |
| A/B testing | ✅ | ❌ | ✅ |
| Custom audiences | ✅ | ❌ | ✅ |
| Lookalike audiences | ✅ | ❌ | ✅ |
| Interest targeting | ✅ | ❌ | ✅ |
| Geo targeting | ✅ | ❌ | ✅ |

---

## 4. WYMAGANIA TECHNICZNE

### 4.1 Meta Developer App (wymagane dla wszystkich)

1. **Utwórz aplikację:** https://developers.facebook.com/apps/
2. **Dodaj produkt:** Marketing API
3. **Uprawnienia wymagane:**
   - `ads_read` - odczyt danych reklamowych
   - `ads_management` - zarządzanie kampaniami
   - `business_management` - dostęp do Business Manager
   - `pages_read_engagement` - dla postów/stron

### 4.2 Access Token

| Typ tokenu | Ważność | Użycie |
|------------|---------|--------|
| Short-term | 1-2h | Tylko testy |
| Long-term User | 60 dni | Development |
| System User | Permanent* | **PRODUKCJA** |

*System User token wymaga Business Manager i odnowienia co 60 dni (automatyzowalne).

### 4.3 Business Manager

- **URL:** https://business.facebook.com/
- Wymagany dla: System User tokens, zarządzania uprawnieniami
- GenActiv prawdopodobnie już ma Business Manager

---

## 5. PLAN IMPLEMENTACJI

### Opcja A: Pipeboard (Remote MCP) - NAJSZYBSZA

**Czas:** 15 minut
**Koszt:** $49/mies lub free (lokalna)

```bash
# Dla Claude Desktop/Pro:
# 1. Idź do claude.ai/settings/integrations
# 2. Dodaj URL: https://mcp.pipeboard.co/meta-ads-mcp
# 3. Autoryzuj przez Facebook
```

### Opcja B: GoMarble (Lokalna) - REKOMENDOWANA DLA PROJEKTU

**Czas:** 30-60 minut
**Koszt:** FREE

```bash
# 1. Instalacja
cd /Users/user/projects/genactiv-klaviyo
npx -y @smithery/cli install @gomarble-ai/facebook-ads-mcp-server --client claude

# 2. Lub manualna konfiguracja w claude_desktop_config.json:
{
  "mcpServers": {
    "meta-ads": {
      "command": "python",
      "args": [
        "/path/to/server.py",
        "--fb-token",
        "YOUR_META_ACCESS_TOKEN"
      ]
    }
  }
}
```

### Opcja C: Pipeboard (Lokalna) - PEŁNE FUNKCJE

**Czas:** 60 minut
**Koszt:** FREE

```bash
# 1. Instalacja
pip install meta-ads-mcp

# 2. Konfiguracja w claude MCP settings
claude mcp add meta-ads -s user \
  -e META_ACCESS_TOKEN=YOUR_TOKEN \
  -e META_APP_ID=YOUR_APP_ID \
  -- python -m meta_ads_mcp
```

---

## 6. DOSTĘPNE NARZĘDZIA (TOOLS)

### 6.1 Analiza i Raportowanie
```
get_ad_accounts          - Lista kont reklamowych
get_account_info         - Szczegóły konta
get_insights             - Metryki wydajności (CTR, CPC, ROAS, etc.)
get_campaign_insights    - Wyniki kampanii
get_adset_insights       - Wyniki ad setów
get_ad_insights          - Wyniki pojedynczych reklam
compare_performance      - Porównanie A vs B
export_insights          - Export CSV/JSON
```

### 6.2 Zarządzanie Kampaniami
```
get_campaigns            - Lista kampanii
create_campaign          - Tworzenie kampanii
update_campaign          - Modyfikacja
pause_campaign           - Pauza
resume_campaign          - Wznowienie
delete_campaign          - Usunięcie
```

### 6.3 Ad Sets i Targeting
```
get_adsets               - Lista ad setów
create_adset             - Tworzenie z targetingiem
search_interests         - Wyszukiwanie zainteresowań
search_behaviors         - Wyszukiwanie zachowań
search_demographics      - Demografia
search_geo_locations     - Lokalizacje geograficzne
```

### 6.4 Reklamy i Kreacje
```
get_ads                  - Lista reklam
create_ad                - Tworzenie reklamy
create_ad_creative       - Tworzenie kreacji
upload_ad_image          - Upload obrazów
get_ad_preview           - Podgląd reklamy
```

### 6.5 Audiences (Remarketing!)
```
create_custom_audience   - Tworzenie custom audience
create_lookalike         - Lookalike audience
get_audience_size        - Szacowany zasięg
```

---

## 7. PRZYKŁADY UŻYCIA DLA GENACTIV

### 7.1 Remarketing na porzucone koszyki
```
"Utwórz custom audience z osób które odwiedziły /cart
w ostatnich 7 dniach ale nie kupiły.
Następnie stwórz kampanię remarketingową z 10% zniżką."
```

### 7.2 Analiza wydajności
```
"Pokaż mi wyniki wszystkich kampanii z ostatnich 30 dni.
Które mają najlepszy ROAS? Które należy wyłączyć?"
```

### 7.3 Lookalike audience
```
"Na podstawie klientów którzy kupili Colostrum 120 kapsułek,
stwórz lookalike audience 1% w Polsce."
```

### 7.4 A/B testing kreacji
```
"Stwórz A/B test dla kampanii 'Colostrum Odporność':
- Wariant A: zdjęcie produktu
- Wariant B: zdjęcie rodziny
Budżet 50 PLN/dzień, test przez 7 dni."
```

---

## 8. KOSZTY

| Element | Koszt |
|---------|-------|
| MCP Server (lokalna instalacja) | FREE |
| Meta Marketing API | FREE (limity) |
| Claude Pro (wymagany dla MCP) | $20/mies |
| Pipeboard Remote (opcjonalnie) | $49/mies |
| **RAZEM (minimum)** | **$20/mies** |

---

## 9. REKOMENDACJA KOŃCOWA

### Dla GenActiv rekomenduje: **GoMarble + Pipeboard lokalna**

**Faza 1 (teraz):** Zainstaluj GoMarble dla podstawowych funkcji READ
- Analiza kampanii
- Insights i raporty
- Audyty wydajności

**Faza 2 (później):** Dodaj Pipeboard lokalną dla funkcji WRITE
- Tworzenie kampanii
- Remarketing audiences
- Automatyzacja

### Następne kroki:

1. ☐ Sprawdź czy GenActiv ma Meta Business Manager
2. ☐ Utwórz Meta Developer App (jeśli nie istnieje)
3. ☐ Wygeneruj System User Access Token
4. ☐ Zainstaluj GoMarble MCP
5. ☐ Przetestuj podstawowe queries
6. ☐ Rozszerz o Pipeboard dla pełnych funkcji

---

## 10. ŹRÓDŁA

- [Pipeboard Meta Ads MCP](https://github.com/pipeboard-co/meta-ads-mcp)
- [GoMarble Facebook Ads MCP](https://github.com/gomarble-ai/facebook-ads-mcp-server)
- [brijr/meta-mcp](https://github.com/brijr/meta-mcp)
- [Facebook Python Business SDK](https://github.com/facebook/facebook-python-business-sdk)
- [Meta Marketing API Docs](https://developers.facebook.com/docs/marketing-apis/)
- [Meta Ads API Guide](https://admanage.ai/blog/meta-ads-api)

---

**KONIEC RAPORTU**

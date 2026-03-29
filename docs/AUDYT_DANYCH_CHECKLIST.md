# AUDYT DANYCH: Shopify jako Single Source of Truth

**Data utworzenia:** 2026-02-27
**Cel:** Zweryfikować, czy dane o ruchu, konwersjach i atrybucji ze WSZYSTKICH kanałów poprawnie trafiają do Shopify
**Status:** DO REALIZACJI

---

## KONTEKST TECHNICZNY

| Element | ID / Wartość |
|---------|-------------|
| Shopify | genactiv.myshopify.com |
| Google Ads (manager) | 253-832-8866 |
| Google Ads (konto) | 339-338-2047 |
| Google Ads Conversion ID | AW-779033182 |
| GA4 | G-KE8T99MGMJ |
| GTM Container | GTM-5W5Z2ML |
| Meta Pixel | 370142134442442 |
| Klaviyo | Zintegrowane z Shopify |
| Pandectes Consent | cookiesBlockedByDefault=7 |
| Payment Gateway | Przelewy24 |
| Baselinker | Zintegrowany (sync Payment ID) |

---

## FAZA 1: TAGOWANIE RUCHU (UTM)

### 1.1 Google Ads → Shopify

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 1.1.1 | Auto-tagging (gclid) włączony | Google Ads → Settings → Account Settings → Auto-tagging | [ ] |
| 1.1.2 | gclid przechodzi przez checkout | Kliknij reklamę → sprawdź URL na stronie → przejdź przez checkout → sprawdź order w Shopify (landing_site, referring_site) | [ ] |
| 1.1.3 | UTM parametry w kampaniach | Google Ads → Campaigns → URL options → sprawdź Final URL suffix / Tracking template | [ ] |
| 1.1.4 | UTM w zamówieniach Shopify | Shopify Admin → Orders → filtruj 10 ostatnich → sprawdź "Conversion summary" i "Landing page" | [ ] |
| 1.1.5 | Pandectes nie blokuje gclid | Sprawdź `urlPassthrough: true` w konfiguracji consent (JEST ✅ ale zweryfikować na żywo) | [ ] |

**Test manualny:** Kliknij własną reklamę Google Ads → dodaj produkt do koszyka → złóż testowe zamówienie → sprawdź w Shopify czy order ma gclid/utm_source=google.

---

### 1.2 Meta / Facebook Ads → Shopify

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 1.2.1 | Meta Pixel zainstalowany | Sprawdź w kodzie strony: `fbq('init', '370142134442442')` | [ ] |
| 1.2.2 | UTM w kampaniach Meta | Meta Ads Manager → Campaign → Ad → URL Parameters → czy jest `utm_source=facebook&utm_medium=cpc` | [ ] |
| 1.2.3 | fbclid przechodzi do Shopify | Kliknij reklamę FB → sprawdź URL → przejdź checkout → order w Shopify | [ ] |
| 1.2.4 | Meta CAPI (Conversions API) | Shopify Admin → Settings → Customer events → czy Meta jest skonfigurowane server-side | [ ] |
| 1.2.5 | Deduplication Pixel vs CAPI | Meta Events Manager → Test Events → czy purchase liczy się raz (nie podwójnie) | [ ] |

---

### 1.3 Klaviyo Email → Shopify

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 1.3.1 | UTM w kampaniach email | Klaviyo → Campaign → sprawdź linki → czy zawierają `utm_source=klaviyo&utm_medium=email&utm_campaign=[name]` | [ ] |
| 1.3.2 | UTM w flows (automations) | Klaviyo → Flows → Abandoned Cart / Browse Abandonment → sprawdź UTM w linkach CTA | [ ] |
| 1.3.3 | Atrybucja Klaviyo w Shopify | Shopify → Orders → filtruj zamówienia z `utm_source=klaviyo` → ile jest vs. co Klaviyo raportuje jako "Placed Order" | [ ] |
| 1.3.4 | Klaviyo attribution window | Klaviyo → Settings → Attribution → sprawdź okno (domyślnie 5 dni click / 24h open) | [ ] |

---

### 1.4 Organiczny / Direct / Inne źródła

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 1.4.1 | Ruch organiczny (SEO) | Shopify → Analytics → sprawdź czy "Google search" pojawia się jako source | [ ] |
| 1.4.2 | Ruch direct | Shopify → Analytics → jaki % zamówień nie ma żadnego source (to jest problem) | [ ] |
| 1.4.3 | Bing/Sembot | Shopify → Orders → sprawdź zamówienia z utm_source=bing (wiemy, że 3/250 miały) | [ ] |
| 1.4.4 | Referral traffic | Shopify → Analytics → czy linki z partnerów/blogów się poprawnie tagują | [ ] |

---

## FAZA 2: ŚLEDZENIE KONWERSJI (CONVERSION TRACKING)

### 2.1 Google Ads Conversions

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 2.1.1 | Conversion action istnieje | Google Ads → Tools → Conversions → szukaj "Purchase" | [ ] |
| 2.1.2 | Tag na thank you page | Sprawdź kod `order-status` / `thank_you` page → czy jest `gtag('event', 'conversion', {send_to: 'AW-779033182/...'})` | [ ] |
| 2.1.3 | Wartość konwersji (PLN) | Czy conversion tag przesyła `value` i `currency: 'PLN'` | [ ] |
| 2.1.4 | Transaction ID | Czy tag przesyła `transaction_id` (zapobiega duplikatom) | [ ] |
| 2.1.5 | Porównanie: GA konwersje vs Shopify zamówienia | Weź 7-dniowy okres → porównaj liczbę konwersji w Google Ads vs faktyczne zamówienia w Shopify | [ ] |
| 2.1.6 | Enhanced Conversions | Google Ads → Conversions → [action] → Enhanced Conversions → czy włączone | [ ] |
| 2.1.7 | Enhanced Conversions dane | Czy na thank_you page jest `gtag('set', 'user_data', {sha256_email_address: ...})` | [ ] |
| 2.1.8 | Consent Mode wpływ | Google Ads → Conversions → kolumna "Conversions" vs "All conv." → czy duża rozbieżność (= consent blokuje tracking) | [ ] |

---

### 2.2 Meta Conversions

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 2.2.1 | Purchase event w Pixelu | Meta Events Manager → pixel 370142134442442 → czy "Purchase" event się odpala | [ ] |
| 2.2.2 | Wartość purchase | Czy event przesyła `value` i `currency: PLN` | [ ] |
| 2.2.3 | Content_ids w evencie | Czy Purchase zawiera `content_ids` (product IDs) - potrzebne dla Dynamic Ads | [ ] |
| 2.2.4 | ViewContent event | Czy na stronach produktów odpala się ViewContent | [ ] |
| 2.2.5 | AddToCart event | Czy przy dodaniu do koszyka odpala się AddToCart | [ ] |
| 2.2.6 | InitiateCheckout event | Czy na stronie checkout odpala się InitiateCheckout | [ ] |
| 2.2.7 | CAPI vs Pixel match rate | Meta Events Manager → Event Match Quality → jaki score (cel: >6/10) | [ ] |
| 2.2.8 | Porównanie: Meta konwersje vs Shopify | Weź 7-dniowy okres → Meta raportuje X purchases → Shopify ma Y zamówień z utm_source=facebook → porównaj | [ ] |

---

### 2.3 GA4 E-commerce Tracking

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 2.3.1 | GA4 zainstalowane | Sprawdź w kodzie strony `gtag('config', 'G-KE8T99MGMJ')` | [ ] |
| 2.3.2 | E-commerce events | GA4 → Admin → DebugView → otwórz stronę → czy widać `page_view`, `view_item`, `add_to_cart`, `purchase` | [ ] |
| 2.3.3 | Purchase event dane | GA4 → Reports → Monetization → czy przychody się zgadzają z Shopify | [ ] |
| 2.3.4 | Cross-domain tracking | Czy przejście genactiv.pl → checkout.shopify.com zachowuje sesję GA4 | [ ] |
| 2.3.5 | GA4-Google Ads linking | GA4 → Admin → Google Ads Links → czy połączone z kontem 339-338-2047 | [ ] |
| 2.3.6 | GA4 attribution model | GA4 → Admin → Attribution Settings → jaki model (data-driven/last click) | [ ] |

---

## FAZA 3: CONSENT & PRYWATNOŚĆ

### 3.1 Pandectes Consent Banner

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 3.1.1 | Banner wyświetla się | Otwórz genactiv.pl w incognito → czy banner się pojawia | [ ] |
| 3.1.2 | Domyślne blokowanie | Sprawdź `cookiesBlockedByDefault` → aktualnie "7" (wszystko zablokowane) | [ ] |
| 3.1.3 | Consent rate | Pandectes Dashboard → Analytics → jaki % akceptuje "Wszystkie" | [ ] |
| 3.1.4 | Consent Mode v2 sygnały | Chrome DevTools → Console → szukaj `consent default` / `consent update` → czy sygnały się wysyłają | [ ] |
| 3.1.5 | ad_storage po akceptacji | Po kliknięciu "Akceptuj" → DevTools → czy `ad_storage` zmienia się na "granted" | [ ] |
| 3.1.6 | analytics_storage po akceptacji | Po kliknięciu "Akceptuj" → czy `analytics_storage` = "granted" | [ ] |
| 3.1.7 | Behavioral modeling | Google Ads → Conversions → czy widać "modeled conversions" (consent mode backup) | [ ] |

---

### 3.2 Wpływ Consent na dane

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 3.2.1 | % ruchu z consent | GA4 → porównaj "total users" bez consent mode vs z consent mode | [ ] |
| 3.2.2 | Utrata danych Google Ads | Porównaj kliknięcia Google Ads vs sesje w GA4 → jaka luka (wskazuje utratę przez consent) | [ ] |
| 3.2.3 | Utrata danych Meta | Meta Events Manager → Event Setup → sprawdź "Events lost" indicator | [ ] |

---

## FAZA 4: SHOPIFY JAKO AGREGATOR

### 4.1 Dane zamówień w Shopify

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 4.1.1 | Landing page zapisane | Shopify → Order → "Conversion details" → czy jest landing_page URL | [ ] |
| 4.1.2 | Referring site zapisane | Shopify → Order → czy jest referring_site (np. google.com) | [ ] |
| 4.1.3 | UTM parametry w zamówieniu | Shopify API: `GET /orders.json` → sprawdź `landing_site` field → czy zawiera UTM params | [ ] |
| 4.1.4 | Discount codes tracked | Shopify → Order → czy kody rabatowe (np. BF20) się poprawnie zapisują | [ ] |
| 4.1.5 | Customer tags z źródła | Czy klienci z Google Ads / Meta / Klaviyo mają odpowiednie tagi | [ ] |

---

### 4.2 Shopify Analytics vs. zewnętrzne źródła

| # | Task | Jak sprawdzić | Narzędzie | Status |
|---|------|---------------|-----------|--------|
| 4.2.1 | Shopify vs GA4: sesje | Porównaj "Online store sessions" (Shopify) vs "Sessions" (GA4) za 7 dni | Manual | [ ] |
| 4.2.2 | Shopify vs GA4: konwersje | Porównaj "Orders" (Shopify) vs "Purchases" (GA4) za 7 dni | Manual | [ ] |
| 4.2.3 | Shopify vs Google Ads: konwersje | Porównaj zamówienia z gclid vs "Conversions" w Google Ads | Manual | [ ] |
| 4.2.4 | Shopify vs Meta: konwersje | Porównaj zamówienia z fbclid vs "Purchases" w Meta Ads Manager | Manual | [ ] |
| 4.2.5 | Shopify vs Klaviyo: atrybucja | Porównaj zamówienia z utm_source=klaviyo vs "Placed Order" w Klaviyo | MCP | [ ] |
| 4.2.6 | Shopify vs Baselinker: zamówienia | Porównaj liczbę zamówień w obu systemach | Script | [ ] |

---

### 4.3 Audit zamówień - sampling

| # | Task | Opis | Status |
|---|------|------|--------|
| 4.3.1 | Sample 20 zamówień | Wylosuj 20 zamówień z ostatnich 30 dni | [ ] |
| 4.3.2 | Dla każdego sprawdź source | Czy ma utm_source / referring_site / gclid / fbclid | [ ] |
| 4.3.3 | Policz % bez atrybucji | Ile z 20 nie ma ŻADNEGO źródła (= "Direct") | [ ] |
| 4.3.4 | Porównaj z raportem remarketingu | Wcześniej było 1% attribution → czy się zmieniło | [ ] |

---

## FAZA 5: INTEGRACJE I SYNC

### 5.1 Shopify → Baselinker

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 5.1.1 | Zamówienia się syncują | Baselinker → zamówienia → porównaj z Shopify | [ ] |
| 5.1.2 | Payment ID sync | GitHub Actions → sync-payment-id → czy workflow działa | [ ] |
| 5.1.3 | Statusy zamówień | Czy zmiana statusu w Shopify → aktualizuje Baselinker | [ ] |

---

### 5.2 Shopify → Klaviyo

| # | Task | Jak sprawdzić | Status |
|---|------|---------------|--------|
| 5.2.1 | Placed Order event | Klaviyo → Metrics → Placed Order → czy odpala się per zamówienie | [ ] |
| 5.2.2 | Started Checkout event | Klaviyo → Metrics → Started Checkout → czy działa | [ ] |
| 5.2.3 | Viewed Product event | Klaviyo → Metrics → Viewed Product → czy się zbiera (potrzebne dla Browse Abandonment) | [ ] |
| 5.2.4 | Added to Cart event | Klaviyo → Metrics → Added to Cart → czy działa (potrzebne dla Abandoned Cart flow) | [ ] |
| 5.2.5 | Profile sync | Shopify customer → Klaviyo profile → czy dane się zgadzają | [ ] |

---

## FAZA 6: NARZĘDZIA DO WERYFIKACJI

### Automatyczne (Claude Code / MCP)

| Narzędzie | Co sprawdza | Komenda |
|-----------|-------------|---------|
| Shopify MCP Extended | UTM w zamówieniach, campaign performance | `get-traffic-source-analytics` |
| Shopify MCP Extended | Konwersje per źródło | `get-conversion-metrics` |
| Shopify MCP Extended | Campaign performance | `get-campaign-performance` |
| Google Ads MCP | Kliknięcia, konwersje, koszty | `run_gaql` |
| Klaviyo MCP | Events, campaign reports | `get_events`, `get_campaign_report` |

### Manualne (przeglądarka)

| Narzędzie | URL | Co sprawdza |
|-----------|-----|-------------|
| Google Ads | ads.google.com | Auto-tagging, conversions, audiences |
| Meta Events Manager | business.facebook.com/events_manager | Pixel events, CAPI, match quality |
| GA4 | analytics.google.com | E-commerce, sessions, attribution |
| Pandectes | app.pandectes.io | Consent rate, konfiguracja |
| Shopify Analytics | genactiv.myshopify.com/admin/analytics | Sessions, orders by source |
| GTM | tagmanager.google.com | Tagi, triggery, zmienne |
| Rich Results Test | search.google.com/test/rich-results | Schema validation (bonus) |
| Meta Pixel Helper | Chrome Extension | Pixel events na stronie |
| Google Tag Assistant | Chrome Extension | GTM/GA4/Ads tagi na stronie |

---

## PODSUMOWANIE: PRIORYTETYZACJA

### KRYTYCZNE (zrób najpierw)
1. **1.1.1** Auto-tagging Google Ads
2. **2.1.1-2.1.4** Conversion tracking Google Ads
3. **3.1.2-3.1.3** Consent banner config + rate
4. **4.3.1-4.3.4** Sample 20 zamówień - sprawdź atrybucję

### WAŻNE (zrób w drugim kroku)
5. **1.2.1-1.2.5** Meta Pixel / CAPI setup
6. **2.2.1-2.2.8** Meta conversions
7. **2.3.1-2.3.6** GA4 e-commerce
8. **4.2.1-4.2.6** Cross-platform comparison

### NICE TO HAVE (trzeci krok)
9. **1.3.1-1.3.4** Klaviyo UTM audit
10. **5.1-5.2** Integracje sync
11. **1.4.1-1.4.4** Organic / referral

---

## EXPECTED OUTCOME

Po ukończeniu audytu będziemy wiedzieć:

| Pytanie | Odpowiedź |
|---------|-----------|
| Ile % zamówień ma poprawną atrybucję? | Obecnie ~1%, cel >50% |
| Czy Google Ads widzi konwersje? | TAK/NIE + ile brakuje |
| Czy Meta widzi konwersje? | TAK/NIE + ile brakuje |
| Czy GA4 dane = Shopify dane? | Rozbieżność X% |
| Co jest root cause utraty danych? | Consent / brak tagów / błąd konfiguracji |
| Co naprawić najpierw? | Priorytetyzowana lista fixów |

---

**KONIEC DOKUMENTU**

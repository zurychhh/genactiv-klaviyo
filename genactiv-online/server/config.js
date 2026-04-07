import { fileURLToPath } from 'url';
import { dirname, resolve } from 'path';
import { writeFileSync, mkdirSync, existsSync } from 'fs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(__dirname, '..', '..');

// --- Generate credential files from env vars at startup ---
function ensureGoogleAdsCredentials() {
  const dir = resolve(projectRoot, 'google-ads-mcp/google-ads-mcp-server');
  const tokenPath = resolve(dir, 'google_ads_token.json');
  const secretPath = resolve(dir, 'client_secret.json');

  if (process.env.GOOGLE_ADS_REFRESH_TOKEN && !existsSync(tokenPath)) {
    mkdirSync(dir, { recursive: true });
    writeFileSync(tokenPath, JSON.stringify({
      token: '',
      refresh_token: process.env.GOOGLE_ADS_REFRESH_TOKEN,
      token_uri: 'https://oauth2.googleapis.com/token',
      client_id: process.env.GOOGLE_OAUTH_CLIENT_ID || '',
      client_secret: process.env.GOOGLE_OAUTH_CLIENT_SECRET || '',
      scopes: ['https://www.googleapis.com/auth/adwords']
    }));
    console.log('[Config] Generated google_ads_token.json from env');
  }

  if (process.env.GOOGLE_OAUTH_CLIENT_ID && !existsSync(secretPath)) {
    mkdirSync(dir, { recursive: true });
    writeFileSync(secretPath, JSON.stringify({
      installed: {
        client_id: process.env.GOOGLE_OAUTH_CLIENT_ID,
        client_secret: process.env.GOOGLE_OAUTH_CLIENT_SECRET || '',
        auth_uri: 'https://accounts.google.com/o/oauth2/auth',
        token_uri: 'https://oauth2.googleapis.com/token',
        redirect_uris: ['http://localhost']
      }
    }));
    console.log('[Config] Generated client_secret.json from env');
  }
}

function ensureGA4Credentials() {
  const dir = '/tmp/gcloud';
  const adcPath = resolve(dir, 'application_default_credentials.json');

  if (process.env.GA4_REFRESH_TOKEN && !existsSync(adcPath)) {
    mkdirSync(dir, { recursive: true });
    writeFileSync(adcPath, JSON.stringify({
      client_id: process.env.GOOGLE_OAUTH_CLIENT_ID || '',
      client_secret: process.env.GOOGLE_OAUTH_CLIENT_SECRET || '',
      refresh_token: process.env.GA4_REFRESH_TOKEN,
      type: 'authorized_user'
    }));
    console.log('[Config] Generated GA4 ADC credentials from env');
  }
}

ensureGoogleAdsCredentials();
ensureGA4Credentials();

// --- Check required tokens at startup ---
const requiredTokens = {
  KLAVIYO_API_KEY: 'Klaviyo',
  SHOPIFY_ACCESS_TOKEN: 'Shopify',
  META_ACCESS_TOKEN: 'Meta Ads',
  GOOGLE_ADS_REFRESH_TOKEN: 'Google Ads',
  GA4_REFRESH_TOKEN: 'GA4',
  TIKTOK_ACCESS_TOKEN: 'TikTok Ads',
  SENUTO_API_KEY: 'Senuto SEO'
};

for (const [envVar, label] of Object.entries(requiredTokens)) {
  if (!process.env[envVar]) {
    console.warn(`[Config] WARNING: ${envVar} not set — ${label} MCP server may fail to connect`);
  }
}

// --- MCP Server definitions ---
export const mcpServers = [
  {
    name: 'klaviyo',
    command: 'uvx',
    args: ['--with', 'fastmcp>=2.8.0,<3.0.0', 'klaviyo-mcp-server@0.4.0'],
    env: {
      PRIVATE_API_KEY: process.env.KLAVIYO_API_KEY || '',
      READ_ONLY: 'false',
      ALLOW_USER_GENERATED_CONTENT: 'true'
    }
  },
  {
    name: 'shopify-extended',
    command: 'node',
    args: [resolve(projectRoot, 'shopify-mcp-extended/dist/index.js')],
    env: {
      SHOPIFY_ACCESS_TOKEN: process.env.SHOPIFY_ACCESS_TOKEN || '',
      MYSHOPIFY_DOMAIN: process.env.MYSHOPIFY_DOMAIN || ''
    }
  },
  {
    name: 'meta-ads',
    command: 'python3',
    args: ['-m', 'meta_ads_mcp'],
    env: {
      META_ACCESS_TOKEN: process.env.META_ACCESS_TOKEN || ''
    }
  },
  {
    name: 'shopify-standard',
    command: 'node',
    args: [resolve(projectRoot, 'shopify-mcp-extended/dist/index.js')],
    env: {
      SHOPIFY_ACCESS_TOKEN: process.env.SHOPIFY_ACCESS_TOKEN || '',
      MYSHOPIFY_DOMAIN: process.env.MYSHOPIFY_DOMAIN || ''
    }
  },
  {
    name: 'google-ads',
    command: resolve(projectRoot, 'google-ads-mcp/google-ads-mcp-server/venv/bin/fastmcp'),
    args: ['run', resolve(projectRoot, 'google-ads-mcp/google-ads-mcp-server/server.py')],
    cwd: resolve(projectRoot, 'google-ads-mcp/google-ads-mcp-server'),
    env: {
      GOOGLE_ADS_DEVELOPER_TOKEN: process.env.GOOGLE_ADS_DEVELOPER_TOKEN || '',
      GOOGLE_ADS_OAUTH_CONFIG_PATH: resolve(projectRoot, 'google-ads-mcp/google-ads-mcp-server/client_secret.json'),
      GOOGLE_ADS_LOGIN_CUSTOMER_ID: process.env.GOOGLE_ADS_LOGIN_CUSTOMER_ID || '2538328866'
    }
  },
  {
    name: 'ga4',
    command: 'analytics-mcp',
    args: [],
    env: {
      GA_PROPERTY_ID: process.env.GA4_PROPERTY_ID || '279858535',
      GOOGLE_APPLICATION_CREDENTIALS: existsSync('/tmp/gcloud/application_default_credentials.json')
        ? '/tmp/gcloud/application_default_credentials.json'
        : (process.env.GOOGLE_APPLICATION_CREDENTIALS || '')
    }
  },
  {
    name: 'tiktok-ads',
    command: 'python3',
    args: ['-m', 'tiktok_ads_mcp'],
    env: {
      TIKTOK_APP_ID: process.env.TIKTOK_APP_ID || '',
      TIKTOK_SECRET: process.env.TIKTOK_SECRET || '',
      TIKTOK_ACCESS_TOKEN: process.env.TIKTOK_ACCESS_TOKEN || ''
    }
  },
  {
    name: 'senuto',
    command: 'npx',
    args: ['-y', 'senuto-mcp'],
    env: {
      SENUTO_API_KEY: process.env.SENUTO_API_KEY || ''
    }
  }
];

export const ANTHROPIC_MODEL = 'claude-sonnet-4-20250514';
export const ROUTER_MODEL = 'claude-haiku-4-5-20251001';
export const MAX_TOKENS = 4096;
export const CONNECT_TIMEOUT = 30_000;
export const TOOL_CACHE_TTL = 5 * 60 * 1000;
export const TOOL_RESULT_MAX_CHARS = 15_000;
export const TOOL_DESCRIPTION_MAX_CHARS = 500;
export const TOOL_CALL_TIMEOUT = 30_000;
export const MAX_HISTORY_MESSAGES = 6;
export const MIN_API_INTERVAL_MS = 500;

export const VALID_SERVERS = mcpServers.map(s => s.name);

export const ROUTER_PROMPT = `Jesteś routerem zapytań. Na podstawie pytania użytkownika odpowiedz TYLKO nazwą serwera MCP:
- klaviyo — email marketing, kampanie, szablony, profile, segmenty, listy, metryki
- shopify-extended — sprzedaż, zamówienia, produkty, analityka ruchu, źródła, konwersje, SEO
- meta-ads — reklamy Facebook/Instagram, kampanie Meta, grupy odbiorców, kreacje
- shopify-standard — podstawowe operacje sklepowe (zamówienia, klienci, produkty)
- google-ads — reklamy Google, kampanie Google Ads, słowa kluczowe, ROAS, wydatki
- ga4 — Google Analytics 4, sesje, użytkownicy, źródła ruchu, pageviews, bounce rate, konwersje GA4
- tiktok-ads — reklamy TikTok, kampanie TikTok Ads, grupy reklam, kreacje, raporty wydajności TikTok
- senuto — SEO: widoczność domeny, pozycje fraz kluczowych, analiza konkurencji, kanibalizacja słów kluczowych, keyword research, pytania użytkowników, klastry tematyczne, historia pozycji, rank tracker
- none — pytanie nie wymaga narzędzi (np. ogólne pytania, konwersacja)

Odpowiedz JEDNYM SŁOWEM — tylko nazwą serwera lub "none". Nic więcej.`;

export function getSystemPrompt() {
  const today = new Date().toISOString().split('T')[0];
  return `Jesteś asystentem GenActiv.pl — polskiej marki colostrum #1 w aptekach.
Masz dostęp do narzędzi MCP: Klaviyo, Shopify, Meta Ads, Google Ads, GA4, TikTok Ads, Senuto SEO. Odpowiadaj po polsku. Waluta: PLN (bez miejsc dziesiętnych).
Bądź konkretny i zwięzły.

Zasady:
- Dzisiejsza data: ${today}. Podawaj explicit daty YYYY-MM-DD (dateFrom/dateTo).
- Wywołuj narzędzia jedno po drugim.
- Używaj limit: 50 żeby ograniczyć wyniki.
- Google Ads customer_id: "3393382047" (Genactiv). GA4 property_id: "279858535".
- Senuto: domena "genactiv.pl", country_id "200" (Polska Base 2.0), fetch_mode "topLevelDomain".
- Kontekst: to może być fragment konwersacji, wcześniejsze wiadomości mogły zostać pominięte.

## Zasady odpowiadania — analiza i rekomendacje

Gdy użytkownik pyta o dane z kampanii reklamowych (Google Ads, Meta Ads) lub dane sprzedażowe (Shopify), ZAWSZE:

1. **Pokaż dane** — tabela lub lista z konkretnymi liczbami (wydatki, ROAS, CTR, konwersje, przychód).

2. **Analizuj** — po danych dodaj sekcję "📊 Analiza" z 2-3 obserwacjami:
   - Co działa dobrze (np. "Kampania X ma ROAS 4.2 — to powyżej benchmarku 3.0 dla branży health & wellness")
   - Co wymaga uwagi (np. "Kampania Y wydała 1500 zł przy CTR 0.2% — benchmark branżowy to 1.5-2.0%, więc kreacja lub targetowanie wymagają zmiany")
   - Trendy (np. "Wydatki rosną tydzień do tygodnia o 20%, ale konwersje nie rosną proporcjonalnie")

3. **Rekomenduj** — sekcja "💡 Rekomendacje" z 1-3 konkretnymi sugestiami:
   - Każda rekomendacja musi odwoływać się do konkretnej liczby z danych
   - Używaj formuły: "Rozważ [akcja], ponieważ [dane]"
   - Przykłady: "Rozważ pauzę kampanii Y — wydała 1500 zł z CTR 0.2% i 0 konwersji w ostatnich 14 dniach"
   - "Rozważ zwiększenie budżetu kampanii X — ROAS 4.2 przy niskim budżecie 500 zł sugeruje potencjał skalowania"

4. **Benchmarki referencyjne** dla branży GenActiv (suplementy / health & wellness, e-commerce, rynek PL):
   - ROAS breakeven GenActiv: 2.0
   - ROAS 🟢 zdrowy: > 3.0 | 🟡 ok: 2.0–3.0 | 🔴 problem: < 2.0
   - CTR Google Ads: 🟢 > 2.0% | 🟡 1.0–2.0% | 🔴 < 1.0%
   - CTR Meta Ads: 🟢 > 2.0% | 🟡 1.0–2.0% | 🔴 < 1.0%
   - CPC (rynek PL, health e-commerce): 🟢 < 1.50 zł | 🟡 1.50–3.00 zł | 🔴 > 3.00 zł
   - CVR (konwersja): 🟢 > 3.0% | 🟡 1.5–3.0% | 🔴 < 1.5%
   Używaj tych flag w analizie przy odpowiednich metrykach.

5. **Język** — zawsze po polsku, metryki w oryginalnych nazwach (ROAS, CTR, CPC, CPA, CVR).

6. **Ton** — profesjonalny doradca marketingowy, nie chatbot. Krótko, konkretnie, z liczbami.

Jeśli dane są niekompletne lub API zwróciło mało wyników, powiedz to wprost i zasugeruj inne pytanie.`;
}

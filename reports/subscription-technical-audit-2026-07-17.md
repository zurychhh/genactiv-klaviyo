# Subscription Model Technical Audit — GenActiv.pl

**Date:** 2026-07-17
**Store:** genactiv.myshopify.com
**Theme:** GEN-6 (ID: 199333609804)
**Payment Gateway:** Przelewy24 + Shopify Payments
**Market:** Poland (PLN)

---

## Executive Summary

GenActiv.pl has strong fundamentals for launching a subscription model: high-value consumable products (colostrum supplements, Fiberbiom fiber), a 55% repeat purchase rate, and an established customer base with 248 high-value customers averaging 12.7 orders and 5,421 PLN lifetime spend each. The Fiberbiom product line alone accounts for 19.1% of all orders and shows the highest reorder frequency (median 15-day interval), making it a natural subscription anchor.

**However, there is one critical blocker: Przelewy24 does NOT support recurring payments on Shopify.** Subscription billing must run through Shopify Payments (credit/debit card tokenization). This limits subscription-eligible payment methods to Visa/Mastercard — excluding BLIK and bank transfers, which together account for ~70% of Polish e-commerce payments. This is the single most important constraint shaping the entire implementation strategy.

**Recommended approach:** Start with **Appstle Subscriptions** (free tier, zero transaction fees, full feature set) on Shopify Payments card billing, with an initial focus on the Fiberbiom product line and Colostrum capsule replenishment. Estimated launch in 3-4 weeks.

---

## Table of Contents

1. [Shopify Subscription Architecture](#1-shopify-subscription-architecture)
2. [Payment Gateway Analysis — The Poland Problem](#2-payment-gateway-analysis--the-poland-problem)
3. [Third-Party App Comparison](#3-third-party-app-comparison)
4. [GenActiv Product-Market Fit Analysis](#4-genactiv-product-market-fit-analysis)
5. [Technical Implementation Requirements](#5-technical-implementation-requirements)
6. [Klaviyo Integration & Automation Flows](#6-klaviyo-integration--automation-flows)
7. [Polish Legal & Tax Compliance](#7-polish-legal--tax-compliance)
8. [Supplement Industry Benchmarks & Churn Strategy](#8-supplement-industry-benchmarks--churn-strategy)
9. [Implementation Roadmap & Effort Estimates](#9-implementation-roadmap--effort-estimates)
10. [Final Recommendation & Decision Matrix](#10-final-recommendation--decision-matrix)

---

## 1. Shopify Subscription Architecture

### 1.1 Native Subscription APIs (2026)

Shopify provides three core APIs for subscription commerce:

| API | Purpose | Key Objects |
|-----|---------|-------------|
| **Selling Plan API** | Define how products can be sold on a recurring basis | `SellingPlanGroup`, `SellingPlan`, policies |
| **Subscription Contract API** | Manage active subscription agreements | `SubscriptionContract`, `SubscriptionBillingAttempt`, `SubscriptionLine` |
| **Customer Payment Method API** | Store and charge vaulted payment methods | Tokenized card data, billing attempts |

**How it works:**

1. A subscription app creates **Selling Plan Groups** (e.g., "Subskrybuj i Oszczedz") with individual **Selling Plans** (e.g., "Co 30 dni", "Co 60 dni", "Co 90 dni").
2. Selling Plans are attached to products and variants.
3. At checkout, Shopify **vaults the customer's card** (tokenizes the PAN into a secure token).
4. After the initial purchase, the subscription app acts as a **scheduler** — it triggers `subscriptionBillingAttemptCreate` mutations on the billing date.
5. Shopify uses the vaulted token to process the charge, creates a new order, and sends confirmations.
6. The subscription contract tracks status transitions: `ACTIVE` -> `PAUSED` -> `CANCELLED` / `FAILED` / `EXPIRED`.

**Latest API version:** `2026-04`. Supports bulk operations for managing multiple contracts at scale.

**Critical detail:** Subscription contracts are **detached** from selling plans after creation. Updating a selling plan does NOT retroactively change existing contracts. Changes require explicit `subscriptionDraftUpdate` mutations.

### 1.2 Shopify Native Subscriptions App (Free)

Shopify's own first-party subscription app is free with no transaction fees. It covers basic replenishment needs.

**What it does well:**
- Free — zero monthly cost, zero transaction fees
- Native checkout integration (cleanest possible)
- Basic selling plan creation (delivery frequency options)
- Simple customer self-service (pause, skip, cancel)
- 1-2 day setup

**What it lacks (and why GenActiv should NOT use it):**
- No cancellation save flows (one-click cancel, no intervention)
- No dunning management beyond basic retry
- No build-a-box or bundle subscriptions
- No analytics dashboard (no MRR, churn, LTV tracking)
- No Klaviyo integration beyond standard Shopify events
- No loyalty/rewards integration
- No customer portal customization (cannot translate to Polish beyond basic themes)
- No prepaid subscription plans

**Verdict:** The native app is viable for validating demand (<100 orders/month), but GenActiv's repeat purchase patterns and product catalog complexity warrant a third-party solution from day one.

---

## 2. Payment Gateway Analysis — The Poland Problem

### 2.1 The Critical Constraint

| Payment Method | % of Polish E-com | Supports Shopify Subscriptions? |
|----------------|-------------------|---------------------------------|
| BLIK | ~60% | **NO** — explicitly unsupported |
| Przelewy24 (bank transfer) | ~15% | **NO** — explicitly unsupported |
| Credit/Debit Cards (Visa/MC) | 25-30% | **YES** — via Shopify Payments tokenization |
| PayU | ~5% | No (bank transfer) |
| Apple Pay / Google Pay | Growing | YES — via Shopify Payments |
| Shop Pay | Growing | YES — native |

**Source:** [Shopify Help — Przelewy24](https://help.shopify.com/en/manual/payments/shopify-payments/local-payment-methods/przelewy24), [Shopify Help — BLIK](https://help.shopify.com/en/manual/payments/shopify-payments/local-payment-methods/blik)

This means **only ~25-30% of Polish online shoppers can pay for subscriptions** using their preferred payment method. The remaining 70% who prefer BLIK or bank transfers would need to use a credit card specifically for the subscription.

### 2.2 Przelewy24's Recurring Payments — NOT Available on Shopify

Przelewy24 *does* offer recurring card payments and recurring BLIK as a standalone service (outside of Shopify). However, this recurring payment functionality **is not available through the Shopify integration**. The Shopify integration is limited to one-time, customer-authorized transactions.

**Source:** [Przelewy24 Recurring Payments](https://www.przelewy24.pl/en/payment-solutions/recurring-payments)

### 2.3 Mitigation Strategies

1. **Messaging:** Position subscription as a premium convenience feature. "Oszczedz 10% z subskrypcja — platnosc karta" (Save 10% with subscription — card payment). Make the card requirement clear upfront.

2. **Apple Pay / Google Pay:** These accelerated checkout methods work with Shopify Payments for subscriptions. Polish adoption is growing, especially among younger consumers.

3. **Shop Pay:** Shopify's own accelerated checkout stores card details and works with subscriptions. Push Shop Pay adoption through checkout UX.

4. **Prepaid Subscriptions:** Offer 3-month or 6-month prepaid options where customers pay a lump sum upfront (any payment method including BLIK/P24), and the store ships monthly. This sidesteps the recurring billing limitation entirely for the prepaid period.

5. **Future:** Monitor Przelewy24's Shopify integration updates. If/when they enable recurring BLIK tokens through Shopify, the addressable market expands dramatically.

### 2.4 Impact Assessment

For GenActiv specifically, the card-only restriction is **less severe** than for a typical Polish e-shop because:

- GenActiv's AOV is 245 PLN — high enough that customers are more likely to have and use credit cards (vs. impulse/low-value purchases where BLIK dominates).
- The target subscription audience (repeat buyers with 3+ orders) already has payment history and higher engagement.
- Supplement subscribers are making a health commitment — they are more motivated to set up card payments.
- The 10% subscription discount offsets the "friction" of card payment.

**Estimated conversion impact:** Expect 30-40% lower subscription adoption than would be possible with BLIK support. Plan for 5-8% of the customer base converting to subscription in year 1 (vs. 12-15% in markets with full recurring payment support).

---

## 3. Third-Party App Comparison

### 3.1 Comprehensive Feature & Pricing Matrix

| Feature | Appstle | Seal | Loop | Bold | Recharge | Skio |
|---------|---------|------|------|------|----------|------|
| **Monthly Fee** | Free - $100 | Free - $19.95 | $99 - $399 | $24.99 - $399.99 | $25 - $499+ | $599 |
| **Transaction Fee** | 0% | 0% | 0.75-1.0% | 1-2% | 1.34-1.49% + $0.19/order | 1% + $0.20/order |
| **Free Plan** | Yes (up to $500/mo sub rev) | Yes (up to 150 subs) | Yes (limited) | No (90-day trial) | 60-day trial | No |
| **Shopify App Store Rating** | 5.0 (7,716 reviews) | 4.9 (2,778 reviews) | 4.9 (650+ reviews) | 4.1 (596 reviews) | 4.8 (2,100+ reviews) | 4.8 (300+ reviews) |
| **Build-a-Box** | Yes | No | Yes | Yes (via Easy Bundles) | Yes | No |
| **Prepaid Subscriptions** | Yes | Yes | Yes | Yes | Yes | Yes |
| **Cancel Save Flows** | Yes | Basic | Yes (advanced) | Yes (ProsperStack) | Yes | Yes |
| **Dunning/Failed Payment** | Yes | Basic | Yes (smart) | Yes | Yes (88% recovery) | Yes |
| **Customer Portal** | Yes (customizable) | Yes (basic) | Yes (branded) | Yes | Yes (Affinity) | Yes (passwordless) |
| **Portal Polish Translation** | Manual via settings | Full text customization | Manual via Text settings | Manual | Manual via Copy & Translations | Manual |
| **Klaviyo Integration** | Yes (via Zapier/native) | Limited | Yes (native events) | Limited (manual API) | Yes (deepest integration) | Yes (via webhooks) |
| **Analytics** | Yes (good) | Basic | Yes (MRR, churn, LTV) | Yes | Yes (best at Pro tier) | Yes |
| **Bundle/Widget Size** | Small | Minimal | ~38KB gzipped | Medium | ~71KB gzipped | ~52KB gzipped |
| **Support** | 24/7, <2 min response | EU hours | Dedicated CSM (Pro) | Email, chat | Email (priority on Pro) | Email, onboarding |
| **Migration Support** | Yes (free) | N/A | Yes (white-glove, free) | Yes (free) | Yes | Yes |

### 3.2 Cost Projection for GenActiv

Assuming Year 1 targets: 150 active subscribers, ~300 subscription orders/month, ~75,000 PLN (~$18,750 USD) monthly subscription revenue.

| App | Monthly Cost (Y1 Estimate) | Annual Cost |
|-----|---------------------------|-------------|
| **Appstle** | $30/mo (Business plan) | **$360** |
| **Seal** | $7.95/mo (750 subs) | **$95** |
| **Loop** | $99 + $187 (1%) = $286/mo | **$3,436** |
| **Bold** | $49.99 + $187 (1%) = $237/mo | **$2,849** |
| **Recharge** | $99 + $279 (1.49%) + $57 ($0.19x300) = $435/mo | **$5,220** |
| **Skio** | $599 + $187 (1%) + $60 ($0.20x300) = $846/mo | **$10,152** |

### 3.3 App-by-App Deep Dive

#### Appstle Subscriptions — RECOMMENDED

**Why it fits GenActiv:**
- **Zero transaction fees** at any tier — the only cost is the flat monthly fee
- Free plan covers the first $500/mo in subscription revenue (enough to validate)
- Business plan ($30/mo) covers up to $30,000/mo — sufficient for year 1 and beyond
- Built on Shopify's official Subscription APIs — native checkout, no redirects
- Build-a-box feature for creating Colostrum + Fiberbiom wellness bundles
- Prepaid plan support (critical for the BLIK/P24 workaround — see Section 2.3)
- 24/7 support with <2 minute response time
- Full portal text customization (can translate all customer-facing text to Polish)
- Churn control: pause, skip, swap, cancellation flows
- Smallest widget bundle size — minimal impact on Core Web Vitals

**Source:** [Appstle on Shopify App Store](https://apps.shopify.com/subscriptions-by-appstle)

#### Seal Subscriptions — BUDGET ALTERNATIVE

**Why to consider:**
- Cheapest serious option: $7.95/mo for up to 750 subscriptions, 0% transaction fees
- Full text customization for Polish translation
- Covers basics well: recurring orders, prepaid, customer portal, automated swaps

**Why to skip:**
- Basic save flows (no multi-step pause/swap interception)
- Thin analytics layer — no MRR/churn/LTV dashboards
- No build-a-box
- No deep Klaviyo integration

#### Loop Subscriptions — STRONG CONTENDER

**Why to consider:**
- Best retention toolkit (gamified journeys, intelligent cancel flows)
- Lowest widget size (~38KB) — best for PageSpeed
- No per-order fees (only % based)
- Native Klaviyo integration with subscription event syncing
- Dedicated CSM on Pro plan

**Why to wait:**
- $99/mo base + 1% transaction fees — expensive at low volume
- API access requires Pro plan ($399/mo)
- Customer portal UI less customizable than competitors
- Overkill for launch phase; better suited after subscription channel matures

#### Recharge — ENTERPRISE OPTION

**Why it is the industry leader:**
- Deepest Klaviyo integration (subscription-specific events, Quick Actions, pre-built flows)
- Most comprehensive bundle architecture
- AI-powered dunning (88% failed payment recovery)
- 20,000+ merchants, battle-tested infrastructure
- Now owns Skio (acquired May 2026 for $105M)

**Why NOT for GenActiv now:**
- Most expensive: $99+/mo + 1.49% + $0.19/order
- Advanced analytics require $499/mo Pro plan
- Overpowered for <500 active subscribers
- Dashboard has a learning curve

**When to migrate:** If subscription revenue exceeds $100K/mo and GenActiv needs enterprise-grade Klaviyo flows, dunning AI, and concierge SMS.

---

## 4. GenActiv Product-Market Fit Analysis

### 4.1 Data from Shopify Order Analysis

Based on the existing `subscription_analysis_data.json` (1,500 orders, 25-day window, June-July 2026):

**Order summary:**
- Total orders analyzed: 1,500
- Total revenue: 368,303 PLN
- Average order value: 245.54 PLN
- Total unique customers: 1,435
- Repeat purchase rate (in 25-day window): 4.0%

**Top subscription candidates (by order frequency and reorder data):**

| Product | Orders | % of All Orders | Reorders | Avg Reorder Interval |
|---------|--------|-----------------|----------|---------------------|
| FIBERBIOM - Blonnik + Colostrum | 287 | 19.1% | 8 repeat buyers | 12 days (median 15) |
| KREM Z COLOSTRUM GENACTIV | 145 | 9.7% | 4 repeat buyers | — |
| COLOSTRUM GENACTIV, proszek | 139 | 9.3% | — | — |
| COLOSTRUM GENACTIV, 120 kapsulek | 127 | 8.5% | — | — |
| FIBERBIOM Z ANANASEM | 99 | 6.6% | — | — |
| FIBERBIOM Z CZARNA PORZECZKA | 79 | 5.3% | — | — |
| COLOSTRUM GENACTIV, 60 kapsulek | 78 | 5.2% | — | — |

**Key product combinations (basket analysis):**

| Combination | Co-purchase Count |
|-------------|------------------|
| FIBERBIOM Z ANANASEM + FIBERBIOM Z CZARNA PORZECZKA | 42x |
| KREM Z COLOSTRUM + MASECZKA Z COLOSTRUM 50ml | 20x |
| FIBERBIOM + FIBERBIOM Z ANANASEM | 17x |
| FIBERBIOM + FIBERBIOM Z CZARNA PORZECZKA | 15x |
| MASKA Z COLOSTRUM + SZAMPON Z COLOSTRUM | 12x |

**High-value customers (3+ orders):**
- Count: 248 customers
- Average orders per customer: 12.7
- Average lifetime spend: 5,421.21 PLN
- Total spend from this segment: 1,344,459 PLN

### 4.2 Subscription Model Recommendations

#### Tier 1 — Launch Products (Week 1-2)

**"Subskrybuj i Oszczedz" (Subscribe & Save) — Simple Replenishment:**

| Product | Price | Sub Price (-10%) | Suggested Cadences |
|---------|-------|-------------------|-------------------|
| FIBERBIOM - Blonnik + Colostrum (30 saszetek) | 179 PLN | 161 PLN | Co 30 / 45 / 60 dni |
| FIBERBIOM Z ANANASEM (30 saszetek) | 179 PLN | 161 PLN | Co 30 / 45 / 60 dni |
| FIBERBIOM Z CZARNA PORZECZKA (30 saszetek) | 179 PLN | 161 PLN | Co 30 / 45 / 60 dni |
| COLOSTRUM GENACTIV, 120 kapsulek | 189 PLN | 170 PLN | Co 30 / 60 / 90 dni |
| COLOSTRUM GENACTIV, 60 kapsulek | 105 PLN | 95 PLN | Co 30 / 60 dni |

**Rationale:** Fiberbiom has the highest order volume (19.1% of all orders) and the shortest reorder interval (median 15 days). Colostrum capsules are the core product with well-established dosing patterns.

#### Tier 2 — Bundles (Week 3-4)

**"Zestaw Wellness" (Wellness Bundle) — Build-a-Box:**

| Bundle | Contents | Price | Sub Price (-15%) |
|--------|----------|-------|-------------------|
| Blonnik Mix | Pick 2x FIBERBIOM flavors | 320 PLN (2x 179 = 358) | 272 PLN |
| Odpornosc + Blonnik | 1x COLOSTRUM 120 kaps + 1x FIBERBIOM | 331 PLN (189+179 = 368) | 281 PLN |
| Pelna Regeneracja | 1x COLOSTRUM 120 kaps + 1x MLEKO KLACZY 120 kaps | 335 PLN (189+183 = 372) | 285 PLN |

**Rationale:** The basket analysis shows FIBERBIOM flavors are frequently purchased together (42x co-purchases), and FIBERBIOM + COLOSTRUM combinations appear 7x. Bundles increase AOV toward the 305 PLN target.

#### Tier 3 — Prepaid Plans (Month 2)

**"Plan Kwartalny" (Quarterly Plan):**

| Plan | Details | Price | Savings |
|------|---------|-------|---------|
| FIBERBIOM 3-miesieczny | 3 deliveries prepaid | 435 PLN (vs. 537 one-time) | -19% |
| COLOSTRUM 3-miesieczny | 3 deliveries prepaid | 480 PLN (vs. 567 one-time) | -15% |

**Rationale:** Prepaid plans solve the BLIK/P24 problem — customers pay once with any payment method, and the store fulfills monthly. They also dramatically reduce churn during the prepaid period (2.5x better retention at month 12).

---

## 5. Technical Implementation Requirements

### 5.1 Theme Modifications (GEN-6)

The current GEN-6 theme (`product-template.liquid`) has **minimal subscription support**. The only existing reference is a conditional CSS class check on `product.selling_plan_groups == empty` (line 291 of the template). No subscription widget, no selling plan selector, and no cart integration exist.

**Required theme changes:**

| Component | Description | Effort |
|-----------|-------------|--------|
| **Selling Plan Selector** | Add a frequency picker (radio buttons: "Kup jednorazowo" / "Subskrybuj co 30/45/60 dni") above the Add to Cart button | 4-8 hours |
| **Price Update Logic (JS)** | JavaScript to update displayed price when subscription is selected (show savings %) | 2-4 hours |
| **Cart Line Item Display** | Show "Subskrypcja: co 30 dni" badge on subscription items in cart | 2-3 hours |
| **Variant Handling** | Ensure selling plan selector updates when variant changes (60 vs 120 capsules) — critical given the A/B test finding that variant changes cause issues on GEN-6 | 4-6 hours |
| **App Block Integration** | Most subscription apps provide a Theme Editor app block — install and position it | 1-2 hours |

**Total theme work estimate:** 13-23 hours (2-3 developer days)

**Important note:** Most modern subscription apps (Appstle, Loop, Recharge) inject their own widget via Shopify Theme Editor app blocks for Online Store 2.0 themes. If GEN-6 supports OS 2.0 app blocks in the product template, the app's auto-injection will handle the selling plan selector with minimal manual code. Manual Liquid integration is only needed if the theme does NOT support app blocks in the product section.

### 5.2 Customer Portal

All subscription apps provide a hosted customer portal accessible via `/account` or a dedicated URL. Required customization:

| Task | Description | Effort |
|------|-------------|--------|
| **Polish Translation** | Translate all portal strings: buttons, labels, messages, error states | 4-6 hours |
| **Branding** | Apply GenActiv brand colors (#0066CC, #F5333F) and typography (Branding-medium/Montserrat) | 2-4 hours |
| **Navigation Link** | Add "Moje Subskrypcje" link to account page and main navigation | 1 hour |
| **Email Notifications** | Configure Polish-language subscription emails (upcoming order, payment failed, shipped) | 4-6 hours |

### 5.3 Shopify Payments Configuration

GenActiv currently uses Przelewy24. To support subscriptions:

1. **Verify Shopify Payments is active** for card processing in Poland. Shopify Payments supports Poland since 2025.
2. **Ensure card payments (Visa/Mastercard) are enabled** alongside Przelewy24.
3. **Enable Apple Pay and Google Pay** through Shopify Payments for accelerated checkout.
4. No changes to Przelewy24 needed — it continues working for one-time purchases.

### 5.4 Subscription App Setup

| Step | Description | Effort |
|------|-------------|--------|
| Install app from Shopify App Store | One-click install | 5 min |
| Create Selling Plan Groups | Define "Subskrybuj i Oszczedz" with 30/45/60/90 day frequencies | 1-2 hours |
| Attach plans to products | Link selling plans to Tier 1 products (5-7 products) | 1-2 hours |
| Configure discounts | Set 10% subscribe-and-save, 15% for bundles, 19% prepaid | 1 hour |
| Set up dunning rules | Configure retry schedule (Day 1, 3, 5, 7), failed payment emails | 2 hours |
| Configure cancel flows | Set up "Why are you cancelling?" with pause/skip/discount offers | 3-4 hours |
| Test end-to-end | Place test subscription, verify billing cycle, portal access | 4-6 hours |

---

## 6. Klaviyo Integration & Automation Flows

### 6.1 Subscription Event Integration

Subscription apps fire lifecycle events to Klaviyo that enable targeted automation. The depth of integration varies significantly by app:

| Event | Recharge | Loop | Appstle | Bold |
|-------|----------|------|---------|------|
| Subscription Created | Native metric | Native event | Via Zapier/native | Manual API |
| Upcoming Order | Native metric | Native event | Via Zapier | Manual |
| Order Processed | Native metric | Native event | Native | Native |
| Payment Failed | Native metric | Native event | Via Zapier | Manual |
| Subscription Skipped | Native metric | Native event | Via Zapier | Manual |
| Subscription Paused | Native metric | Native event | Via Zapier | Manual |
| Subscription Cancelled (with reason) | Native metric | Native event | Via Zapier | Manual |
| Customer Portal Visit | No | No | No | No |

**Recharge has the deepest Klaviyo integration.** It passes subscription-specific event data as native Klaviyo metrics, enables Quick Action URLs in emails (one-click skip, swap, reactivate), and offers pre-built flow templates.

**Loop has strong native integration** with direct event syncing and custom profile properties (active subscriptions count, products subscribed, next order date).

**Appstle** supports Klaviyo through Zapier workflows or direct API — functional but requires more setup.

### 6.2 Recommended Klaviyo Flows for GenActiv

| Flow | Trigger | Content (Polish) | Expected Impact |
|------|---------|-------------------|-----------------|
| **Witamy w Subskrypcji** | Subscription Created | Welcome, how to take supplements, what to expect in weeks 1-4 | Reduce Order 2 churn by 20% |
| **Przypomnienie o Zamowieniu** | 3 days before billing | "Twoja przesylka za 3 dni. Zmien, pauza, dodaj produkty." | Reduce passive churn by 10% |
| **Nieudana Platnosc** | Payment Failed | "Platnosc nie powiodla sie. Zaktualizuj karte." (3-touch sequence over 7 days) | Recover 30-40% of failed payments |
| **Ankieta po 30 dniach** | 30 days after first subscription order | "Jak sie czujesz? Colostrum potrzebuje 4-8 tygodni." | Reduce "no results" churn by 15% |
| **Ostrzezenie o Rezygnacji** | Subscription Cancelled | Cancel-reason branching: offer skip, pause, discount, or swap | Save 17-25% of cancellations |
| **Win-Back Subskrybenta** | 30 days after cancellation | "Wracaj z 15% rabatem na 3 miesiace" | Recapture 10-15% of churned subs |
| **Milestone Reward** | After order #3, #6, #12 | "Gratulacje! Jestes z nami od 3 miesiecy. Oto bonus." | Reduce churn at critical thresholds |
| **Cross-sell Subskrybenta** | 14 days after first sub order | "Uzupelnij rutyne o FIBERBIOM" (if subscribed to Colostrum) | Increase subscription AOV by 15-20% |

### 6.3 Klaviyo Segment Strategy

| Segment | Definition | Use Case |
|---------|------------|----------|
| Active Subscribers | Has active subscription contract | Exclude from standard promotional campaigns |
| At-Risk Subscribers | Skipped 2+ orders in last 90 days | Trigger proactive retention flow |
| High-Value Subscribers | Subscription LTV > 1,000 PLN | VIP treatment, early access to new products |
| Subscription Candidates | 3+ orders, NOT subscriber, bought FIBERBIOM or Colostrum kapsulki | Targeted subscription conversion campaigns |
| Churned Subscribers | Had active subscription, now cancelled | Win-back flow + periodic re-engagement |

---

## 7. Polish Legal & Tax Compliance

### 7.1 Consumer Protection — 14-Day Withdrawal Right

Under the **Consumer Rights Act** (*Ustawa o prawach konsumenta*, transposing EU Directive 2011/83/EU), Polish consumers have a **14-day right of withdrawal** from distance contracts without providing any reason.

**For subscription supplements specifically:**

| Scenario | Withdrawal Right? | Notes |
|----------|-------------------|-------|
| First subscription order (unopened) | **YES** — 14 days from delivery | Customer can return for full refund |
| First subscription order (opened) | **DEPENDS** — sealed health products exemption may apply | Supplements in sealed packaging may be exempt once seal is broken (Art. 38 pkt 5) |
| Subsequent recurring orders | **YES** — each delivery restarts the 14-day period | Each shipment is treated as a separate delivery |
| Prepaid subscription (bulk) | **YES** for unopened packages in the batch | Opened packages may be exempt |

**Required information at checkout (pre-contract):**
- Clear statement that the product is sold on a subscription basis with recurring charges
- Total price per billing cycle, including taxes and delivery
- Billing frequency and duration (if fixed-term)
- How to cancel (must be as easy as subscribing)
- Right of withdrawal instructions and template withdrawal form

### 7.2 Subscription-Specific Regulations (2026)

Poland's UOKiK (consumer protection office) has been actively enforcing subscription fairness rules:

- **Price changes require explicit consent.** Unilateral price increases on recurring subscriptions are prohibited. If GenActiv raises the subscription price, existing subscribers must actively opt in to the new price.
- **Cancellation must be as easy as subscribing.** The EU Digital Fairness Act (transposed June 2026) requires a clear cancellation mechanism (e.g., "Anuluj Subskrypcje" button in the customer portal). Dark patterns or convoluted cancellation processes are prohibited.
- **Auto-renewal transparency.** If the subscription auto-renews, this must be clearly communicated, including renewal terms and costs.
- **Free trial disclosure.** If offering a trial period, the transition to paid billing must be clearly communicated before the first charge.

**Sources:** [UOKiK — Subscription Terms](https://uokik.gov.pl/en/change-in-subscription-terms-only-with-your-permission), [Biznes.gov.pl — Consumer Rights](https://www.biznes.gov.pl/en/portal/004510), [EU Consumer Rights Directive](https://eur-lex.europa.eu/EN/legal-content/summary/consumer-information-right-of-withdrawal-and-other-consumer-rights.html)

### 7.3 VAT & E-Invoicing

**VAT rate for dietary supplements in Poland:** Standard 23% rate applies (supplements are not classified as food for reduced VAT purposes in most cases; classification depends on specific product category — verify with a tax advisor).

**KSeF (National e-Invoice System):**
- Mandatory since **1 April 2026** for standard taxpayers
- Grace period until 31 December 2026 (no penalties for non-compliance)
- Subscription invoices must be issued through KSeF in structured XML format
- Each billing cycle generates a separate invoice

**Key considerations for subscription billing:**
- VAT is triggered at each billing/delivery cycle, not at subscription creation
- Invoices must be issued by the 15th of the month following delivery
- Split payment mechanism (PLN 15,000+ gross B2B invoices) is unlikely to apply to B2C supplement subscriptions but should be monitored
- The PLN 240,000 annual VAT exemption threshold was raised in January 2026 — GenActiv almost certainly exceeds this and is already VAT-registered

**Source:** [Poland VAT Guide 2026](https://www.vatcalc.com/poland/poland-vat-country-guide/)

---

## 8. Supplement Industry Benchmarks & Churn Strategy

### 8.1 Industry Churn Benchmarks

| Metric | Industry Average | Top Performers | GenActiv Target |
|--------|-----------------|----------------|-----------------|
| Monthly churn rate | 5-8% | <4% | 5% |
| Order 2 retention | 30-40% | 55-65% | 50% |
| Order 6 retention | 15-20% | 35-45% | 30% |
| Failed payment recovery | 40-50% | 80-88% | 70% |
| Cancel save rate | 10-15% | 25-35% | 20% |

**Source:** [Supplement Subscription Churn Benchmarks 2026](https://eightx.co/blog/supplement-subscription-churn-rate-benchmark), [Skio — Why 70% Churn After Order 2](https://skio.com/blog/why-70-of-supplement-subscribers-churn-after-order-2)

### 8.2 The Order 2-3 Churn Problem

Supplement subscribers churn massively around orders 2-3 due to five converging pressures:

1. **Efficacy gap:** Colostrum and fiber supplements take 4-8 weeks to show noticeable results. By order 2-3, customers haven't felt the benefit yet.
2. **Memory fade:** Customers forget the health problem that motivated the subscription.
3. **Price shock:** First order often has a discount; full price at order 2-3 feels expensive.
4. **Routine failure:** Inconsistent daily intake means the product doesn't work, confirming the "it doesn't work" belief.
5. **Paradox of improvement:** If it IS working, customers feel better and think they no longer need it.

### 8.3 GenActiv-Specific Churn Prevention Strategy

| Intervention | Timing | Mechanism | Expected Impact |
|-------------|--------|-----------|-----------------|
| **Onboarding email sequence** | Day 0-30 | 5-email drip: dosing guide, what to expect, testimonials, "4-8 weeks to feel it" | -20% order 2 churn |
| **Dosing reminder (SMS/email)** | Daily/every other day for first 30 days | "Czy wzielas/wziales dzis colostrum?" push notification | +30% adherence |
| **30-day check-in** | Day 30 | Survey: energy, digestion, sleep, skin. Compare to baseline. | -15% "no results" churn |
| **Cadence flexibility** | At order 2 | Proactive: "Masz jeszcze zapas? Przesun dostowe o 2 tygodnie." | -20% stockpiling churn |
| **Milestone rewards** | Orders 3, 6, 12 | Free sample (new flavor), 5% additional discount, exclusive content | -10% fatigue churn |
| **Cancel flow** | On cancellation | Reason capture -> conditional offer (skip 1 month / pause / swap flavor / 15% off 3 months) | Save 20-25% of cancellations |

### 8.4 Financial Model

**Conservative scenario (Year 1):**

| Metric | Month 1 | Month 3 | Month 6 | Month 12 |
|--------|---------|---------|---------|----------|
| New subscribers | 30 | 40 | 50 | 50 |
| Active subscribers | 30 | 85 | 140 | 180 |
| Monthly churn | — | 6% | 5.5% | 5% |
| Sub revenue | 5,400 PLN | 15,300 PLN | 25,200 PLN | 32,400 PLN |
| Subscription share of total revenue | 1.5% | 4.1% | 6.8% | 8.8% |
| Incremental AOV lift | — | +5 PLN | +10 PLN | +15 PLN |

**Assumptions:** Average subscription order = 180 PLN, 10% discount applied, 30-day cadence, 5-6% monthly churn stabilizing by month 6. Monthly total revenue baseline = 370,000 PLN.

**Annual subscription revenue (Year 1):** ~200,000 PLN
**Annual app cost (Appstle Business):** ~1,440 PLN ($360)
**ROI:** 139:1

---

## 9. Implementation Roadmap & Effort Estimates

### 9.1 Phase 1 — Foundation (Weeks 1-2)

| Task | Owner | Effort | Dependencies |
|------|-------|--------|-------------|
| Install Appstle Subscriptions app | CC | 15 min | None |
| Verify Shopify Payments card processing active | MAN | 30 min | Shopify admin access |
| Create Selling Plan Group "Subskrybuj i Oszczedz" | CC | 1 hour | App installed |
| Configure 3 frequencies: 30/45/60 days | CC | 30 min | Selling Plan Group |
| Set 10% subscription discount | CC | 15 min | Selling Plan Group |
| Attach selling plans to 5 Tier 1 products | CC | 1 hour | Products identified |
| Add subscription widget to GEN-6 product page | DEV | 4-8 hours | App installed, theme access |
| Translate widget text to Polish | CC | 2 hours | Widget configured |
| Configure customer portal (Polish text) | CC | 4 hours | App configured |
| Add "Moje Subskrypcje" link to account page | DEV | 1 hour | Portal configured |
| Test: subscribe, manage, cancel, re-subscribe | CC+MAN | 4 hours | All above |

**Total Phase 1:** 14-22 hours (2-3 days dev work + 1 day QA)

### 9.2 Phase 2 — Automation (Weeks 3-4)

| Task | Owner | Effort | Dependencies |
|------|-------|--------|-------------|
| Connect Appstle to Klaviyo (Zapier or native) | CC | 2-3 hours | Both apps active |
| Build "Witamy w Subskrypcji" Klaviyo flow (5 emails) | CC | 8 hours | Klaviyo integration |
| Build "Nieudana Platnosc" dunning flow (3 emails) | CC | 4 hours | Klaviyo integration |
| Build "Przypomnienie o Zamowieniu" flow | CC | 3 hours | Klaviyo integration |
| Configure cancel save flows in app | CC | 3-4 hours | App configured |
| Configure dunning retry schedule | CC | 1 hour | App configured |
| Create Klaviyo segments (subscribers, at-risk, candidates) | CC | 3 hours | Klaviyo integration |
| Set up subscription conversion campaign (targeting 3+ order customers) | CC | 4 hours | Segments created |
| Polish-language subscription email templates (6 transactional) | CC | 6 hours | Design system |

**Total Phase 2:** 34-38 hours (5-6 days)

### 9.3 Phase 3 — Bundles & Optimization (Month 2)

| Task | Owner | Effort | Dependencies |
|------|-------|--------|-------------|
| Create bundle selling plans (Blonnik Mix, Odpornosc+Blonnik) | CC | 4 hours | Phase 1 live |
| Configure build-a-box if available | CC+DEV | 8 hours | App supports it |
| Create prepaid 3-month plans | CC | 3 hours | Phase 1 validated |
| Build "Ankieta po 30 dniach" Klaviyo flow | CC | 3 hours | Phase 2 flows |
| Build "Win-Back Subskrybenta" Klaviyo flow | CC | 3 hours | Phase 2 flows |
| Build "Cross-sell Subskrybenta" Klaviyo flow | CC | 4 hours | Phase 2 flows |
| Analytics review: churn analysis, conversion funnel | CC | 4 hours | 30 days of data |
| A/B test subscription widget position/copy | CC+DEV | 4 hours | 30 days of data |

**Total Phase 3:** 33 hours (5 days)

### 9.4 Total Implementation Summary

| Phase | Timeline | Effort | Cost |
|-------|----------|--------|------|
| Phase 1: Foundation | Weeks 1-2 | 14-22 hours | App: Free (launch on free tier) |
| Phase 2: Automation | Weeks 3-4 | 34-38 hours | App: Free -> $30/mo when >$500 sub rev |
| Phase 3: Optimization | Month 2 | 33 hours | App: $30/mo |
| **Total** | **6-8 weeks** | **81-93 hours** | **$30/mo ongoing** |

---

## 10. Final Recommendation & Decision Matrix

### 10.1 Recommended Stack

| Component | Choice | Rationale |
|-----------|--------|-----------|
| **Subscription App** | Appstle Subscriptions | Zero transaction fees, free tier for validation, full features, best support, smallest bundle size |
| **Payment Method** | Shopify Payments (Visa/MC/Apple Pay/Google Pay) | Only method supporting recurring billing in Poland on Shopify |
| **Klaviyo Integration** | Appstle -> Zapier -> Klaviyo (upgrade to Loop/Recharge when sub rev >$50K/mo) | Functional for launch; deeper integration available at scale |
| **Prepaid Workaround** | 3-month prepaid plans payable via BLIK/P24 | Addresses the 70% of Polish shoppers who prefer non-card payments |
| **Initial Products** | Fiberbiom (3 flavors) + Colostrum capsules (60/120) | Highest order volume, strongest reorder patterns |

### 10.2 Decision Matrix — When to Choose Each App

| Criteria | Choose Appstle | Choose Loop | Choose Recharge |
|----------|---------------|-------------|-----------------|
| Subscription revenue | <$30K/mo | $30K-$100K/mo | >$100K/mo |
| Active subscribers | <500 | 500-2,000 | 2,000+ |
| Budget sensitivity | High | Medium | Low |
| Klaviyo depth needed | Basic flows | Advanced events | Enterprise automation |
| Build-a-box needed | Yes (available) | Yes (available) | Yes (most advanced) |
| Developer resources | Minimal | Some | Dedicated |
| Migration effort | N/A (start) | 1-2 days (auto-migrate) | 3-5 days |

### 10.3 Risk Register

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Low subscription adoption due to card-only billing | **High** | **High** | Prepaid plans (BLIK/P24), clear messaging, 10% discount incentive |
| High early churn (Order 2-3 drop-off) | **Medium** | **High** | Onboarding email sequence, 30-day check-in, dosing reminders |
| Theme widget conflicts with GEN-6 variant selector | **Medium** | **Medium** | Test thoroughly; GEN-6 has known variant change issues from A/B test |
| Polish regulatory compliance gaps | **Low** | **High** | Implement 14-day withdrawal for each delivery, clear cancellation button, UOKiK-compliant pricing transparency |
| KSeF e-invoice integration for recurring billing | **Medium** | **Medium** | Verify subscription app generates proper invoice data; may need separate invoicing solution |

### 10.4 Success Metrics (6-Month Targets)

| KPI | Target | How to Measure |
|-----|--------|---------------|
| Active subscribers | 150+ | Subscription app dashboard |
| Monthly subscription revenue | 25,000+ PLN | Shopify + app analytics |
| Subscription share of revenue | >6% | Revenue reporting |
| Monthly churn rate | <6% | App analytics |
| Failed payment recovery | >60% | Dunning reports |
| Cancel save rate | >15% | Cancel flow analytics |
| Subscription AOV | >280 PLN | Include bundles in calculation |
| Repeat purchase rate (overall) | 58%+ (from 55%) | Shopify customer analytics |
| Overall AOV | 290+ PLN (toward 305 target) | Shopify analytics |

---

## Appendix A: Shopify Product Catalog (Active, Subscription-Eligible)

| Product | Price (PLN) | Variants | Subscription Priority |
|---------|------------|----------|----------------------|
| FIBERBIOM - Blonnik + Colostrum | 179 | 30 saszetek | **P1** — highest volume |
| FIBERBIOM Z ANANASEM | 179 | 30 saszetek | **P1** |
| FIBERBIOM Z CZARNA PORZECZKA | 179 | 30 saszetek | **P1** |
| COLOSTRUM GENACTIV, 120 kapsulek | 189 | 120 kaps | **P1** — core product |
| COLOSTRUM GENACTIV, 60 kapsulek | 105 | 60 kaps | **P1** — entry tier |
| COLOSTRUM GENACTIV, proszek | 189 | 60g | P2 |
| COLOSTRUM Z BANANEM, 30 saszetek | 115 | 30 saszetek | P2 |
| COLOSTRUM Z CZARNA PORZECZKA | 183 | 30 saszetek | P2 |
| MLEKO KLACZY, 120 kapsulek | 183 | 120 kaps | P2 |
| COLOSTRUM I MLEKO KLACZY, proszek 200g | 399 | 200g | P3 — premium |
| KREM Z COLOSTRUM | 55 | 40ml | P3 — cosmetic |
| SERUM Z COLOSTRUM | 179 | 100ml | P3 — cosmetic |
| MASECZKA Z COLOSTRUM 50ml | 90 | 50ml | P3 — cosmetic |
| MASECZKA Z COLOSTRUM 150ml | 195 | 150ml | P3 — cosmetic |
| SZAMPON Z COLOSTRUM | 89 | 150ml | P3 — cosmetic |
| MASKA Z COLOSTRUM | 159 | 250ml | P3 — cosmetic |

## Appendix B: Key Sources

- [Shopify Subscription API Documentation](https://shopify.dev/docs/apps/build/purchase-options/subscriptions)
- [Shopify Selling Plans](https://shopify.dev/docs/apps/build/purchase-options/subscriptions/selling-plans)
- [Shopify Payments Poland](https://help.shopify.com/en/manual/payments/shopify-payments/supported-countries/poland)
- [Przelewy24 Shopify Limitations](https://help.shopify.com/en/manual/payments/shopify-payments/local-payment-methods/przelewy24)
- [BLIK Shopify Limitations](https://help.shopify.com/en/manual/payments/shopify-payments/local-payment-methods/blik)
- [Przelewy24 Recurring Payments (standalone)](https://www.przelewy24.pl/en/payment-solutions/recurring-payments)
- [Appstle Subscriptions](https://apps.shopify.com/subscriptions-by-appstle)
- [Recharge Pricing](https://getrecharge.com/pricing/)
- [Loop Subscriptions Pricing](https://www.loopwork.co/pricing)
- [Skio Pricing](https://skio.com/pricing)
- [Bold Subscriptions Pricing](https://support.boldcommerce.com/hc/en-us/articles/360050564071)
- [Seal Subscriptions](https://apps.shopify.com/seal-subscriptions)
- [Recharge + Klaviyo Integration](https://support.getrecharge.com/hc/en-us/articles/1500010170061)
- [Loop + Klaviyo Integration](https://help.loopwork.co/en/articles/12733266-klaviyo)
- [Recharge Acquired Skio ($105M)](https://www.loopwork.co/blog/recharge-payments-vs-skio-subscriptions)
- [Supplement Subscription Churn Benchmarks](https://eightx.co/blog/supplement-subscription-churn-rate-benchmark)
- [Why 70% Churn After Order 2](https://skio.com/blog/why-70-of-supplement-subscribers-churn-after-order-2)
- [Poland Consumer Rights (UOKiK)](https://uokik.gov.pl/en/change-in-subscription-terms-only-with-your-permission)
- [Poland VAT Rates 2026](https://www.vatcalc.com/poland/poland-vat-country-guide/)
- [EU Consumer Rights Directive](https://eur-lex.europa.eu/EN/legal-content/summary/consumer-information-right-of-withdrawal-and-other-consumer-rights.html)
- [Shopify Native vs Third-Party Subscriptions 2026](https://craftshift.com/shopify-native-subscriptions-vs-third-party-apps-2026/)
- [Supplement Subscription Best Practices](https://www.attnagency.com/blog/supplement-subscription-optimization)

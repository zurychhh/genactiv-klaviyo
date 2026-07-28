# PRICING VERIFICATION REPORT: Dwupak Savings Claims

**Date:** 2026-07-06
**Agent:** Pricing Verification Agent
**Source:** Shopify REST Admin API (live data)

---

## 1. FULL PRICING TABLE

| # | Product | Shopify ID | Price (PLN) | Compare-at Price | SKU |
|---|---------|-----------|-------------|-----------------|-----|
| 1 | FIBERBIOM Z ANANASEM (single) | 15850903961932 | 179.00 | (none) | - |
| 2 | FIBERBIOM Z ANANASEM DWUPAK | 15853802783052 | 299.00 | (none) | - |
| 3 | FIBERBIOM Z CZARNA PORZECZKA (single) | 15850938106188 | 179.00 | (none) | - |
| 4 | FIBERBIOM Z CZARNA PORZECZKA DWUPAK | 15853446922572 | 299.00 | (none) | - |
| 5 | Genactiv Colostrum A2, kapsulki (single) | 15557953651020 | 135.00 | (none) | CGA2_60KAP |
| 6 | Genactiv Colostrum A2, kapsulki Dwupak | 15856105980236 | 229.00 | (none) | A2KAPSULKIX2 |
| 7 | Genactiv Colostrum A2, proszek (single) | 15557942051148 | 245.00 | (none) | CGA2_45G |
| 8 | Genactiv Colostrum A2, proszek dwupak | 15856113320268 | 419.00 | (none) | A2PROSZEKX2 |

**NOTE:** None of the products have a compare-at price set.

---

## 2. DWUPAK SAVINGS CALCULATIONS

Formula: `savings_pct = (2 * single_price - dwupak_price) / (2 * single_price) * 100`

### FIBERBIOM Z ANANASEM
- 2 x 179.00 = **358.00 PLN**
- Dwupak price = **299.00 PLN**
- Savings = 358.00 - 299.00 = **59.00 PLN**
- **Savings % = 16.48%**

### FIBERBIOM Z CZARNA PORZECZKA
- 2 x 179.00 = **358.00 PLN**
- Dwupak price = **299.00 PLN**
- Savings = 358.00 - 299.00 = **59.00 PLN**
- **Savings % = 16.48%**

### Genactiv Colostrum A2, kapsulki
- 2 x 135.00 = **270.00 PLN**
- Dwupak price = **229.00 PLN**
- Savings = 270.00 - 229.00 = **41.00 PLN**
- **Savings % = 15.19%**

### Genactiv Colostrum A2, proszek
- 2 x 245.00 = **490.00 PLN**
- Dwupak price = **419.00 PLN**
- Savings = 490.00 - 419.00 = **71.00 PLN**
- **Savings % = 14.49%**

---

## 3. CRITICAL FINDING: "10% SAVINGS" CLAIM IS WRONG

| Product pair | Actual savings | Proposed claim | Verdict |
|-------------|---------------|----------------|---------|
| FIBERBIOM Ananas | **16.48%** | "oszczedz 10%" | WRONG (understates savings) |
| FIBERBIOM Czarna Porzeczka | **16.48%** | "oszczedz 10%" | WRONG (understates savings) |
| Colostrum A2 kapsulki | **15.19%** | "oszczedz 10%" | WRONG (understates savings) |
| Colostrum A2 proszek | **14.49%** | "oszczedz 10%" | WRONG (understates savings) |

**Conclusion:** The "10%" figure is factually incorrect for ALL dwupak products. Actual savings range from **14.49% to 16.48%**. The claim understates the actual discount.

### Recommended corrected claims:
- FIBERBIOM dwupak: "oszczedz ok. 16%" or "oszczedz 59 zl" (exact)
- Colostrum A2 kapsulki dwupak: "oszczedz ok. 15%" or "oszczedz 41 zl" (exact)
- Colostrum A2 proszek dwupak: "oszczedz ok. 14%" or "oszczedz 71 zl" (exact)
- Generic safe claim: "oszczedz ponad 14%" (true for all dwupak products)

---

## 4. SACHET COUNT VERIFICATION (FIBERBIOM)

### Current SEO meta descriptions:

| Product | Meta description sachet claim | Actual sachets | Correct? |
|---------|------------------------------|---------------|----------|
| FIBERBIOM Ananas SINGLE | "15 saszetek" | 15 szt. | YES |
| FIBERBIOM Ananas DWUPAK | **"15 saszetek"** | **30 saszetek (2x15)** | **NO - BUG** |
| FIBERBIOM Czarna Porzeczka SINGLE | "15 saszetek" | 15 szt. | YES |
| FIBERBIOM Czarna Porzeczka DWUPAK | **"15 saszetek"** | **30 saszetek (2x15)** | **NO - BUG** |

**CRITICAL BUG:** Both FIBERBIOM dwupak products have the SAME meta description as the single products, claiming "15 saszetek" when the dwupak contains 30 saszetek.

### Evidence from product body HTML:
- Dwupak Ananas: "Fiberbiom z ananasem, dwupak to **30 saszetek (2 opakowania po 15)**"
- Dwupak Czarna Porzeczka: "Fiberbiom z czarna porzeczka, dwupak to **30 saszetek (2 opakowania po 15)**"

### Full current SEO meta descriptions:
- FIBERBIOM Ananas single: `FIBERBIOM z ANANASEM Genactiv (15 saszetek) -- rozpuszczalny blonnik z kory modrzewia i colostrum. Wsparcie mikrobioty i jelit. Zamow w Genactiv!`
- FIBERBIOM Ananas DWUPAK: `FIBERBIOM z ANANASEM Genactiv (15 saszetek) -- rozpuszczalny blonnik z kory modrzewia i colostrum. Wsparcie mikrobioty i jelit. Zamow w Genactiv!` **(IDENTICAL to single!)**
- FIBERBIOM Czarna Porzeczka single: `FIBERBIOM Z CZARNA PORZECZKA Genactiv (15 saszetek) -- rozpuszczalny blonnik z kory modrzewia i colostrum. Wsparcie mikrobioty i jelit. Zamow w Genactiv!`
- FIBERBIOM Czarna Porzeczka DWUPAK: `FIBERBIOM Z CZARNA PORZECZKA Genactiv (15 saszetek) -- rozpuszczalny blonnik z kory modrzewia i colostrum. Wsparcie mikrobioty i jelit. Zamow w Genactiv!` **(IDENTICAL to single!)**

---

## 5. SEO META TITLE STATUS

| Product | Current SEO Title |
|---------|------------------|
| FIBERBIOM Ananas single | (not set - uses product title) |
| FIBERBIOM Ananas DWUPAK | (not set - uses product title) |
| FIBERBIOM Czarna Porzeczka single | (not set - uses product title) |
| FIBERBIOM Czarna Porzeczka DWUPAK | (not set - uses product title) |
| Colostrum A2 kapsulki single | Kapsulki z Colostrum Genactiv A2 60 kapsulek -- Genactiv |
| Colostrum A2 kapsulki Dwupak | Kapsulki z Colostrum Genactiv A2 60 kapsulek dwupak -- Genactiv |
| Colostrum A2 proszek single | Colostrum Genactiv A2, proszek, puszka 45 g -- Genactiv |
| Colostrum A2 proszek dwupak | Colostrum Genactiv A2, proszek, puszka 45 g dwupak -- Genactiv |

---

## 6. SUMMARY OF ISSUES FOUND

1. **FACTUAL ERROR:** "oszczedz 10%" claim is wrong for all dwupak products. Actual savings = 14.49%-16.48%.
2. **SEO BUG:** FIBERBIOM dwupak meta descriptions say "15 saszetek" -- should say "30 saszetek (2x15)".
3. **DUPLICATE META:** FIBERBIOM dwupak meta descriptions are identical copies of single-product descriptions.
4. **MISSING META TITLES:** All 4 FIBERBIOM products have no custom SEO title set.
5. **NO COMPARE-AT PRICES:** None of the products use Shopify's compare_at_price field for crossed-out pricing.

---

## 7. RECOMMENDED FIXES

### For FIBERBIOM dwupak meta descriptions (immediate):
- Ananas DWUPAK: `FIBERBIOM z ANANASEM Genactiv DWUPAK (30 saszetek, 2x15) -- oszczedz 59 zl! Rozpuszczalny blonnik z kory modrzewia i colostrum. Zamow w Genactiv!`
- Czarna Porzeczka DWUPAK: `FIBERBIOM Z CZARNA PORZECZKA Genactiv DWUPAK (30 saszetek, 2x15) -- oszczedz 59 zl! Rozpuszczalny blonnik z kory modrzewia i colostrum. Zamow w Genactiv!`

### For meta titles with savings claims:
- Use "oszczedz 59 zl" (absolute) or "oszczedz ponad 16%" instead of "oszczedz 10%"
- Or use a safe generic: "w korzystnej cenie" without specifying percentage

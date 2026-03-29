# GenActiv SEO - ZWERYFIKOWANY PLAN IMPLEMENTACJI

**Data weryfikacji:** 2025-01-22
**Źródło danych:** Shopify GraphQL API + curl genactiv.pl
**Status:** Gotowy do implementacji po akceptacji

---

## 1. WYNIKI WERYFIKACJI

| Element | Status | Źródło |
|---------|--------|--------|
| Kolekcje bez meta | 27 z 44 | Shopify API |
| Produkty bez meta | 8 z 87 | Shopify API |
| FAQPage Schema | ❌ BRAK | curl /pages/faq |
| BreadcrumbList Schema | ❌ BRAK | curl /products/* |
| Product Schema | ✅ DZIAŁA | curl /products/* |
| AggregateRating | ✅ DZIAŁA | curl /products/* |

---

## 2. KOLEKCJE BEZ META DESCRIPTION (27 szt.)

**Zweryfikowane z Shopify GraphQL API:**

| ID | Nazwa | Do zrobienia |
|----|-------|--------------|
| 278965190830 | Nowości | ✅ TAK |
| 278965223598 | Najlepiej sprzedające się produkty | ✅ TAK |
| 613251940684 | Zestawy Świąteczne z Colostrum Genactiv | ✅ TAK |
| 618803134796 | Colostrum i Mleko Klaczy Genactiv | ✅ TAK |
| 621474414924 | Colostrum tabletki do ssania | ✅ TAK |
| 621474808140 | Colostrum proszek | ✅ TAK |
| 621475070284 | Colostrum kapsułki | ✅ TAK |
| 621708247372 | COLOSTRUM JUNIOR CZARNY BEZ GENACTIV | ✅ TAK |
| 624721625420 | omnibus-label-omnibus-compliant | ❌ POMINĄĆ (tech) |
| 624721658188 | omnibus-label-omnibus-not-compliant | ❌ POMINĄĆ (tech) |
| 624721690956 | omnibus-label-omnibus-not-on-sale | ❌ POMINĄĆ (tech) |
| 627600589132 | Back2school | ✅ TAK |
| 630708076876 | Akcesoria | ✅ TAK |
| 652905185612 | Maseczki z Colostrum | ✅ TAK |
| 652905251148 | Kremy z Colostrum | ✅ TAK |
| 652905382220 | Skóra głowy i włosy | ✅ TAK |
| 659312509260 | Genactiv Colostrum Junior z Czarnym Bzem | ✅ TAK |
| 659488211276 | Colostrum dla dzieci | ✅ TAK |
| 659488670028 | Colostrum dla dorosłych | ✅ TAK |
| 659938640204 | Buduj odporność dziecka z Genactiv® Colostrum | ✅ TAK |
| 662434939212 | Colostrum A2 | ✅ TAK |
| 664150933836 | Colostrum dla zwierząt | ✅ TAK |
| 664211882316 | Colostrum dla psów | ✅ TAK |
| 664212111692 | Colostrum dla kotów | ✅ TAK |
| 664213619020 | Colostrum dla koni | ✅ TAK |
| 668385509708 | Wszystkie produktu | ✅ TAK |
| 670751654220 | -20% z kodem "FERIE" | ✅ TAK |

**RAZEM DO ZROBIENIA: 24 kolekcje** (27 - 3 techniczne)

---

## 3. PRODUKTY BEZ META DESCRIPTION (8 szt.)

**Zweryfikowane z Shopify GraphQL API:**

1. KREM Z COLOSTRUM GENACTIV, 40 ml - dwupak
2. Colostrum dla pięknej skóry - Maseczka z Colostrum
3. COLOSTRUM Z BANANEM GENACTIV saszetki i COLOSTRUM
4. Colostrum dla pięknej skóry - Maseczka z Colostrum (duplikat?)
5. Zabawka myszka dla kota
6. Drapak dla Kota
7. FUREVER CAT proszek 75 g
8. TEST

**UWAGA:** 79 z 87 produktów MA meta description - problem dotyczy głównie akcesoriów.

---

## 4. FAQ PAGE - WERYFIKACJA

- **URL:** https://genactiv.pl/pages/faq
- **Status HTTP:** 200 OK
- **Obecne Schema:** Organization (tylko)
- **FAQPage Schema:** ❌ BRAK
- **Sekcja FAQ w HTML:** TAK (istnieje)

---

## 5. BREADCRUMBLIST - WERYFIKACJA

Sprawdzone na:
- `/products/colostrum-genactiv-120-kapsulek` → ❌ BRAK
- `/collections/colostrum-kapsulki` → ❌ BRAK

---

## 6. CO DZIAŁA (zweryfikowane)

Na stronie produktu obecne Schema:
- ✅ Product
- ✅ Offer
- ✅ AggregateRating (jeśli są recenzje)
- ✅ Review (jeśli są recenzje)
- ✅ Organization
- ✅ Rating
- ✅ Person

---

## 7. API DOSTĘP

```python
SHOP = "genactiv.myshopify.com"
TOKEN = "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"
API_VERSION = "2024-01"
THEME_ID = "162539340108"
```

**Testy wykonane 2025-01-22:**
- ✅ collectionUpdate - DZIAŁA
- ✅ productUpdate - DZIAŁA
- ✅ Theme API read - DZIAŁA
- ✅ Theme API write - DZIAŁA

---

## 8. PLAN DZIAŁANIA

| Priorytet | Zadanie | Ilość |
|-----------|---------|-------|
| 1 | Meta descriptions dla kolekcji | 24 szt. |
| 2 | FAQPage Schema | 1 plik |
| 3 | BreadcrumbList Schema | 1 plik |

---

## 9. IMPLEMENTACJA

### 9.1 Meta descriptions (GraphQL)

```python
mutation = """
mutation collectionUpdate($input: CollectionInput!) {
  collectionUpdate(input: $input) {
    collection { id title }
    userErrors { field message }
  }
}
"""

variables = {
    "input": {
        "id": "gid://shopify/Collection/ID_TUTAJ",
        "seo": {
            "description": "Meta description tutaj"
        }
    }
}
```

### 9.2 FAQPage Schema (Theme API)

Plik: `snippets/faq-schema.liquid`

```liquid
{% if template.suffix == 'faq' %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [...]
}
</script>
{% endif %}
```

### 9.3 BreadcrumbList Schema (Theme API)

Plik: `snippets/breadcrumb-schema.liquid`

```liquid
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [...]
}
</script>
```

---

## 10. PLIKI

```
seo/
├── SEO_IMPLEMENTATION_PLAN.md      # Ten plik
├── SEO_PLAN_ZWERYFIKOWANY.docx     # Do feedbacku
└── ...
```

---

**KONIEC - Wszystkie dane zweryfikowane z API/strony.**

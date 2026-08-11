# Szablon artykułu w standardzie GEO — blog Poradnik

Wzorzec odtworzony z opublikowanego i przepuszczonego przez QA artykułu
`/blogs/poradnik/ozempic-mounjaro-glp1-odchudzanie` (28.07.2026). To jest kanon domu —
nie wymyślamy własnej struktury.

Blog docelowy: **Poradnik**, id `82593448110`, handle `poradnik`.
Autor (byline): **Dominik Operacz** — główny autor merytoryczny (używany w większości
z 112 artykułów; pozostali: Magdalena Habuz-Falińska, Michalina Hasiak, Natalia Chamska,
Piotr Chrzan).

## Struktura tekstu

| Kolejność | Element | Zasada |
|---|---|---|
| 1 | **Akapit odpowiedzi** (bez nagłówka) | Odpowiedź na pytanie tytułowe w **pierwszym zdaniu**. Bez rozbiegu, bez „w dzisiejszych czasach". Podmiot nazwany wprost |
| 2 | H2 × 4–6 | **Sformułowane jako pytania.** Każdy H2 = jedno pytanie, na które akapit pod spodem odpowiada od razu |
| 3 | H3 pod wybranymi H2 | Doprecyzowanie, gdy sekcja ma podproblem |
| 4 | H2 „Gdzie w tym miejscu jest \<produkt\>?" | Jedyne miejsce z twardą sprzedażą. Skład + gramatury + dane 73%/70% + zastrzeżenia |
| 5 | H2 „Najczęstsze pytania" | 4–6 × H3 z pytaniem, każde z akapitem odpowiedzi. To zasila FAQPage |
| 6 | H2 „Podsumowanie" | Krótkie, konkretne |
| 7 | H3 „Źródła" | `<ol>` z pozycjami literatury + linki PMC/PubMed |

Długość: **800–1200 słów** (referencyjny artykuł ma 1888 — górna granica jest miękka).

## Reguły GEO (pod AI-search)

- **Odpowiedź najpierw.** Modele cytują fragmenty, które samodzielnie odpowiadają na pytanie.
  Akapit, który zaczyna się od kontekstu, nie zostanie wycięty jako cytat.
- **Front-load każdego akapitu** — wniosek w pierwszym zdaniu, uzasadnienie dalej.
- **Jeden akapit = jedna myśl.** Krótkie akapity są cytowalne, długie nie.
- **H2 jako pytania** — mapują się 1:1 na zapytania użytkowników.
- **Twarde konkrety zamiast ogólników.** „arabinogalaktan z kory modrzewia, 5000 mg
  w saszetce" jest cytowalne; „bogaty w błonnik" nie jest.
- **Podmiot nazwany wprost** w kluczowych zdaniach — „Fiberbiom zawiera…", nie „produkt
  zawiera…". Model musi móc wyciąć zdanie z kontekstu i nadal wiedzieć, o czym mowa.
- **Sekcja FAQ** — najczęściej cytowany fragment w AI Overviews.

## JSON-LD — UWAGA, motyw już emituje część schematu

Zweryfikowane na żywej stronie 2026-08-11 (`ozempic-mounjaro-glp1-odchudzanie`):
strona zwraca **5 bloków JSON-LD**, w tym **3× `Article`** i **2× `BreadcrumbList`**.

| Blok | Źródło | Typ |
|---|---|---|
| 1 | motyw (header) | `Organization` |
| 2 | motyw (`snippets/breadcrumbs.liquid`) | `BreadcrumbList` |
| 3 | **body artykułu** | `BreadcrumbList` + `Article` + `FAQPage` |
| 4 | motyw (sekcja artykułu) | `Article` |
| 5 | motyw (stopka artykułu) | `Article` |

**Wniosek dla nowych artykułów: w body umieszczamy WYŁĄCZNIE `FAQPage`.**
`Article` i `BreadcrumbList` motyw generuje sam — dokładanie ich w treści tworzy
sprzeczne encje (różne `dateModified`, różne `publisher.logo`) i pogłębia istniejący defekt.

`FAQPage` jest jedynym typem, którego motyw **nie** emituje — i to jest ten, który
realnie pracuje na AI Overviews.

> **Osobny dług techniczny do zgłoszenia:** motyw duplikuje `Article` (2×) niezależnie
> od naszych treści. To defekt do naprawy w motywie, nie w artykułach. Nie blokuje
> publikacji klastra, ale powinien trafić na listę zadań technicznych.

### Blok do wklejenia na końcu body

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "PYTANIE 1 — dokładnie jak w H3",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "ODPOWIEDŹ — treść zgodna z akapitem pod H3, bez HTML."
      }
    }
  ]
}
</script>
```

Zasady: pytania w `FAQPage` muszą brzmieć **dosłownie tak jak H3** w sekcji „Najczęstsze
pytania", a odpowiedzi odpowiadać treści akapitu. Rozjazd między schematem a widoczną
treścią to naruszenie wytycznych Google.

## Linkowanie wewnętrzne

Wzorzec z artykułu referencyjnego (8 linków):

- **2–3 linki do innych artykułów Poradnika** — kontekstowo, w treści (np. „mikrobiotę"
  → `/blogs/poradnik/colostrum-a-probiotyki`)
- **1–2 linki produktowe** — tylko w sekcji produktowej i tylko tam, gdzie jest podparta
  podstawa (błonnik / wzdęcia / regularność)
- **linki do LP jako źródło danych** — `/pages/plaski-brzuch`,
  `/pages/fiberbiom-regularne-wyproznianie` przy liczbach 73%/70%, podane jako pełny URL

## Meta

Uzupełniane jako metafields przez `metafieldsSet` (`single_line_text_field`):

| Pole | Limit | Zasada |
|---|---|---|
| `global.title_tag` | ≤ 60 znaków | Fraza główna z przodu, wariant marki na końcu |
| `global.description_tag` | ≤ 155 znaków | Odpowiedź, nie zachęta. Ma streszczać, nie kusić |

## HTML — konwencje

Czysty HTML bez klas CSS. Używane tagi: `<p>`, `<h2>`, `<h3>`, `<ul>/<li>`, `<ol>/<li>`,
`<strong>`, `<a>`, `<table>` (rzadko). Bez `<img>` w body — grafika idzie przez
featured image artykułu. Bez inline style.

## Checklista przed publikacją

- [ ] Pierwsze zdanie odpowiada na pytanie z tytułu
- [ ] 4–6 H2, sformułowane jako pytania
- [ ] Sekcja „Gdzie w tym miejscu jest Fiberbiom?" z gramaturami i zastrzeżeniami
- [ ] Sekcja „Najczęstsze pytania" — 4–6 H3
- [ ] `FAQPage` JSON-LD, pytania **dosłownie** jak H3
- [ ] **Brak** `Article` i `BreadcrumbList` w body (motyw je generuje)
- [ ] Byline: Dominik Operacz
- [ ] `global.title_tag` ≤ 60 zn., `global.description_tag` ≤ 155 zn.
- [ ] 2–3 linki wewnętrzne + link produktowy tylko przy podpartej podstawie
- [ ] Sekcja „Źródła" z odnośnikami PMC/PubMed
- [ ] Przeszła checklista z `health-claims-pl.md`
- [ ] Sprawdzone, że temat nie kanibalizuje istniejącego artykułu

#!/usr/bin/env python3
"""
Full site spelling and grammar checker for genactiv.pl
Scans all pages including products, collections, blog posts, and info pages
"""

import requests
from bs4 import BeautifulSoup
import re
import json
import time
from collections import defaultdict
from datetime import datetime

# All URLs to scan
PRODUCTS = [
    "https://genactiv.pl/products/colostrum-i-mleko-klaczy-200g",
    "https://genactiv.pl/products/mleko-klaczy-150g",
    "https://genactiv.pl/products/colostrum-z-malina-genactiv-tabletki-do-ssania-60-sztuk",
    "https://genactiv.pl/products/malinowa-odpornosc-tabletki-do-ssania",
    "https://genactiv.pl/products/colostrum-genactiv-60-kapsulek",
    "https://genactiv.pl/products/potrojna-odpornosc",
    "https://genactiv.pl/products/dwupak-colostrum-z-bananem-200g",
    "https://genactiv.pl/products/krem-z-colostrum-genactiv-dwupak",
    "https://genactiv.pl/products/serum-z-colostrum-genactiv-100-ml",
    "https://genactiv.pl/products/mleko-klaczy-w-30-saszetkach",
    "https://genactiv.pl/products/maseczka-z-colostrum-genactiv-150ml",
    "https://genactiv.pl/products/colostrum-z-bananem-genactiv-30-saszetek",
    "https://genactiv.pl/products/colostrum-genactiv-120-kapsulek-dwupak",
    "https://genactiv.pl/products/bloker-z-colostrum-genactiv-90-ml",
    "https://genactiv.pl/products/szampon-z-colostrum-genactiv-150-ml",
    "https://genactiv.pl/products/maska-z-colostrum-genactiv-250-ml",
    "https://genactiv.pl/products/mega-odpornosc-colostrum-z-bananem-genactiv",
    "https://genactiv.pl/products/maseczka-z-colostrum-50-ml",
    "https://genactiv.pl/products/colostrum-z-czarna-porzeczka-genactiv-30-saszetek",
    "https://genactiv.pl/products/podwojna-regeneracja-colostrum-genactiv-i-mleko-klaczy-genactiv",
    "https://genactiv.pl/products/wzmocniona-kondycja-dwupak-colostrum-i-mleko-klaczy-genactiv-200g",
    "https://genactiv.pl/products/krem-z-colostrum-genactiv",
    "https://genactiv.pl/products/mleko-klaczy-genactiv-120-kapsulek",
    "https://genactiv.pl/products/colostrum-z-bananem-genactiv-proszek-200g",
    "https://genactiv.pl/products/colostrum-genactiv-120-kapsulek",
    "https://genactiv.pl/products/dwupak-colostrum-z-czarna-porzeczka-genactiv",
    "https://genactiv.pl/products/krem-z-mlekiem-klaczy-genactiv",
    "https://genactiv.pl/products/colostrum-i-mleko-klaczy-genactiv-180-kapsulek",
    "https://genactiv.pl/products/dwupak-colostrum-i-mleko-klaczy-genactiv-180-kapsulek",
    "https://genactiv.pl/products/colostrum-genactiv-zawiesina",
    "https://genactiv.pl/products/colostrum-genactiv-proszek",
    "https://genactiv.pl/products/colostrum-junior-z-czarnym-bzem-genactiv-proszek",
    "https://genactiv.pl/products/colostrum-junior-z-czarnym-bzem-genactiv-tabletki-do-ssania",
    "https://genactiv.pl/products/colostrum-junior-z-czarnym-bzem-genactiv-zawiesina",
    "https://genactiv.pl/products/torba-na-ramie-genactiv",
    "https://genactiv.pl/products/butelka-junior",
    "https://genactiv.pl/products/butelka-termiczna",
    "https://genactiv.pl/products/kosmetyczka",
    "https://genactiv.pl/products/zestaw_zdrowa-rutyna",
    "https://genactiv.pl/products/colostrum-junior-z-czarnym-bzem-genactiv-proszek-dwupak",
    "https://genactiv.pl/products/colostrum-junior-z-czarnym-bzem-genactiv-zawiesina-dwupak",
    "https://genactiv.pl/products/colostrum-junior-z-czarnym-bzem-genactiv-tabletki-do-ssania-dwupak",
    "https://genactiv.pl/products/colostrum-genactiv-proszek-dwupak",
    "https://genactiv.pl/products/colostrum-genactiv-kapsulki-dwupak",
    "https://genactiv.pl/products/colostrum-z-bananem-genactiv-proszek-dwupak",
    "https://genactiv.pl/products/colostrum-genactiv-zawiesina-plyn-dwupak",
    "https://genactiv.pl/products/colostrum-z-malina-genactiv-tabletki-do-ssania-dwupak",
    "https://genactiv.pl/products/fiberbiom-blonnik-colostrum",
    "https://genactiv.pl/products/furever-horse-proszek-5500-g",
    "https://genactiv.pl/products/furever-horse-proszek-2500-g",
    "https://genactiv.pl/products/furever-dog-proszek-100-g",
    "https://genactiv.pl/products/furever-dog-120-kapsulek",
    "https://genactiv.pl/products/furever-dog-60-kapsulek",
    "https://genactiv.pl/products/furever-cat-proszek-75g",
    "https://genactiv.pl/products/furever-cat-90-kapsulek",
    "https://genactiv.pl/products/furever-horse",
    "https://genactiv.pl/products/furever-cat",
    "https://genactiv.pl/products/furever-dog",
    "https://genactiv.pl/products/all-furever-30-kapsulek",
    "https://genactiv.pl/products/all-furever-90-kapsulek",
    "https://genactiv.pl/products/all-furever-proszek-50-g",
    "https://genactiv.pl/products/colostrum-i-mleko-klaczy-genactiv-proszek-50-g",
    "https://genactiv.pl/products/colostrum-od-juniora-do-seniora-zawiesina",
]

COLLECTIONS = [
    "https://genactiv.pl/collections/colosregen",
    "https://genactiv.pl/collections/colostrum",
    "https://genactiv.pl/collections/mleko-klaczy",
    "https://genactiv.pl/collections/suplementy",
    "https://genactiv.pl/collections/dermokosmetyki",
    "https://genactiv.pl/collections/nowosci",
    "https://genactiv.pl/collections/bestsellery",
    "https://genactiv.pl/collections/zestawy",
    "https://genactiv.pl/collections/odpornosc",
    "https://genactiv.pl/collections/zdrowe-jelita",
    "https://genactiv.pl/collections/zdrowe-wlosy",
    "https://genactiv.pl/collections/porost-wlosow",
    "https://genactiv.pl/collections/zdrowa-skore",
    "https://genactiv.pl/collections/zdrowe-dziecko",
    "https://genactiv.pl/collections/new-collection",
    "https://genactiv.pl/collections/best-selling-collection",
    "https://genactiv.pl/collections/promocje",
    "https://genactiv.pl/collections/colostrum-na-nowy-rok-szkolny",
    "https://genactiv.pl/collections/zestawy-swiateczne",
    "https://genactiv.pl/collections/colostrum-w-plynie",
    "https://genactiv.pl/collections/colostrum-i-mleko-klaczy-genactiv",
    "https://genactiv.pl/collections/colostrum-tabletki-do-ssania",
    "https://genactiv.pl/collections/colostrum-proszek",
    "https://genactiv.pl/collections/colostrum-kapsulki",
    "https://genactiv.pl/collections/colostrum-junior-czarny-bez-genactiv",
    "https://genactiv.pl/collections/back2school",
    "https://genactiv.pl/collections/akcesoria",
    "https://genactiv.pl/collections/maseczki-z-colostrum",
    "https://genactiv.pl/collections/kremy-z-colostrum",
    "https://genactiv.pl/collections/skora-glowy-i-wlosy",
    "https://genactiv.pl/collections/genactiv-colostrum-junior-z-czarnym-bzem",
    "https://genactiv.pl/collections/produkty-dla-dzieci",
    "https://genactiv.pl/collections/colostrum-dla-doroslych",
    "https://genactiv.pl/collections/buduj-odpornosc-dziecka-z-genactiv%C2%AEcolostrum",
    "https://genactiv.pl/collections/colostrum-a2",
    "https://genactiv.pl/collections/colostrum-dla-zwierzat",
    "https://genactiv.pl/collections/colostrum-dla-psow",
    "https://genactiv.pl/collections/colostrum-dla-kotow",
    "https://genactiv.pl/collections/colostrum-dla-koni",
    "https://genactiv.pl/collections/wszystkie-produktu",
    "https://genactiv.pl/collections/ferie-z-colostrum",
]

BLOG_POSTS = [
    "https://genactiv.pl/blogs/poradnik/jak-dysbioza-jelitowa-wplywa-na-caly-organizm",
    "https://genactiv.pl/blogs/poradnik/w-jaki-sposob-jelita-wplywaja-na-nastroj-i-poziomy-energii",
    "https://genactiv.pl/blogs/poradnik/zyj-w-zgodzie-ze-swoim-wewnetrznym-lokatorem",
    "https://genactiv.pl/blogs/poradnik/czym-jest-mikrobiom",
    "https://genactiv.pl/blogs/poradnik/celiakia-jakie-sa-objawy-i-przyczyny-tego-schorzenia",
    "https://genactiv.pl/blogs/poradnik/sibo-diagnostyka-i-profilaktyka",
    "https://genactiv.pl/blogs/poradnik/5-sposobow-na-zdrowe-wlosy-latem",
    "https://genactiv.pl/blogs/poradnik/sibo-zespol-rozrostu-bakteryjnego-jelita-cienkiego-objawy-leczenie-przyczyny",
    "https://genactiv.pl/blogs/poradnik/celiakia-co-to-jest-objawy-przyczyny",
    "https://genactiv.pl/blogs/poradnik/jak-zadbac-o-zdrowie-jelit-na-wakacjach-poznaj-5-sposobow",
    "https://genactiv.pl/blogs/poradnik/najczestsze-problemy-skory-glowy-dziecka-sprawdz-jak-sobie-radzic-z-ciemieniucha-i-podrazniona-skora-glowy",
    "https://genactiv.pl/blogs/poradnik/jak-myc-skore-glowy-i-wlosy-dziecku-najczestsze-bledy-i-polecane-sposoby-okiem-trychologa",
    "https://genactiv.pl/blogs/poradnik/sucha-skora-glowy-problem-ktory-mozna-latwo-wyeliminowac-sprawdz-jak",
    "https://genactiv.pl/blogs/poradnik/wiesz-ze-sa-dwa-rodzaje-lupiezu-sprawdz-ktory-ma-twoje-dziecko-i-dobierz-pielegnacje",
    "https://genactiv.pl/blogs/poradnik/co-ma-wspolnego-kimchi-z-naszymi-wlosami-sprawdz-jak-duza-role-w-poroscie-wlosow-odgrywaja-jelita",
    "https://genactiv.pl/blogs/poradnik/jak-wzmocnic-odpornosc-organizmu",
    "https://genactiv.pl/blogs/poradnik/choroby-jelit-jak-je-rozpoznac-i-jak-leczyc",
    "https://genactiv.pl/blogs/poradnik/jak-uniknac-zaparc-wzdec-i-biegunek-na-wakacjach-praktyczny-poradnik-urlopowicza",
    "https://genactiv.pl/blogs/poradnik/ferrytyna-a-leczenie-tradziku",
    "https://genactiv.pl/blogs/poradnik/wypadanie-wlosow-a-niski-poziom-ferrytyny",
    "https://genactiv.pl/blogs/poradnik/ferrytyna-a-ciaza",
    "https://genactiv.pl/blogs/poradnik/ferrytyna-a-zmeczenie-czy-niski-poziom-ferrytyny-moze-byc-przyczyna-chronicznego-zmeczenia",
    "https://genactiv.pl/blogs/poradnik/ferrytyna-u-dzieci-jak-zadbac-o-odpowiedni-poziom-ferrytyny-u-najmlodszych",
    "https://genactiv.pl/blogs/poradnik/ferrytyna-a-stres-czy-dlugotrwaly-stres-moze-obnizyc-poziom-ferrytyny",
    "https://genactiv.pl/blogs/poradnik/ferrytyna-u-sportowcow-jak-poziomy-zelaza-i-ferrytyny-wplywaja-na-wydolnosc-fizyczna",
    "https://genactiv.pl/blogs/poradnik/niskie-poziomy-ferrytyny-objawy-przyczyny-i-skutki-dla-zdrowia",
    "https://genactiv.pl/blogs/poradnik/ferrytyna-a-anemia-jaka-role-odgrywa-ferrytyna-w-zapobieganiu-i-leczeniu-anemii",
    "https://genactiv.pl/blogs/poradnik/falszywy-mit-igg-w-colostrum",
]

PAGES = [
    "https://genactiv.pl/",
    "https://genactiv.pl/pages/poznajgenactiv",
    "https://genactiv.pl/pages/faq",
    "https://genactiv.pl/pages/co-to-jest-colostrum",
    "https://genactiv.pl/pages/formy-platnosci",
    "https://genactiv.pl/pages/formy-dostawy",
    "https://genactiv.pl/pages/zwroty",
    "https://genactiv.pl/pages/reklamacje",
    "https://genactiv.pl/pages/regulaminy",
    "https://genactiv.pl/pages/polityka-prywatnosci",
    "https://genactiv.pl/pages/liofilizacja-co-to-znaczy",
    "https://genactiv.pl/pages/laktoferyna",
    "https://genactiv.pl/pages/lizozym",
    "https://genactiv.pl/pages/immunoglobuliny-a",
    "https://genactiv.pl/pages/immunoglobuliny-m-i-g",
    "https://genactiv.pl/pages/igf-1-co-to-jest-i-jaka-funkcje-pelni-w-organizmie",
    "https://genactiv.pl/pages/mlodziwo",
    "https://genactiv.pl/pages/flora-jelitowa",
    "https://genactiv.pl/pages/sibo",
    "https://genactiv.pl/pages/immunomodulatory",
    "https://genactiv.pl/pages/hormony-wzrostu",
    "https://genactiv.pl/pages/limfocyty",
    "https://genactiv.pl/pages/enzymy",
    "https://genactiv.pl/pages/co-to-jest-mleko-klaczy",
    "https://genactiv.pl/pages/gdzie-kupic",
    "https://genactiv.pl/pages/kontakt",
    "https://genactiv.pl/pages/ekspert-nr-1",
    "https://genactiv.pl/pages/ekspert-nr-2",
    "https://genactiv.pl/pages/ekspert-nr-3",
    "https://genactiv.pl/pages/zapytaj-eksperta",
    "https://genactiv.pl/pages/flora-bakteryjna",
    "https://genactiv.pl/pages/egf-naskorkowy-czynnik-wzrostu",
    "https://genactiv.pl/pages/kwas-hialuronowy",
    "https://genactiv.pl/pages/aminokwasy",
    "https://genactiv.pl/pages/ph-skory",
    "https://genactiv.pl/pages/dr-hab-n-med-maciej-halasa",
    "https://genactiv.pl/pages/monika-stromkie-zlomaniec",
    "https://genactiv.pl/pages/alfa-laktoalbumina",
    "https://genactiv.pl/pages/badania-genactiv-colostrum",
    "https://genactiv.pl/pages/kazeina",
    "https://genactiv.pl/pages/ltryptofan-i-tryptofan-wlasciwosci-niedobor-dawkowanie",
    "https://genactiv.pl/pages/opinie-o-colostrum",
    "https://genactiv.pl/pages/eksperci",
    "https://genactiv.pl/pages/mikrobiota-jelitowa-co-to-jest-i-jej-wplyw-na-organizm-czlowieka",
    "https://genactiv.pl/pages/czarny-bez",
    "https://genactiv.pl/pages/fiberbiom",
    "https://genactiv.pl/pages/raport-o-stanie-jelit-polakow",
]

# Error patterns - kategoryzacja
ERROR_PATTERNS = {
    # LITEROWKI - spelling errors
    "literowki": [
        (r'\bskutecznośc\b', 'skuteczność', 'literówka'),
        (r'\bprwadziwe\b', 'prawdziwe', 'literówka'),
        (r'\bprawidziwe\b', 'prawdziwe', 'literówka'),
        (r'\bJeydnym\b', 'Jedynym', 'literówka'),
        (r'\bpełnić\s+w\s+organiźmie\b', 'pełnić w organizmie', 'literówka'),
        (r'\borganiźmie\b', 'organizmie', 'literówka'),
        (r'\bodpornościowy\s+organzim\b', 'odpornościowy organizm', 'literówka'),
        (r'\borganzim\b', 'organizm', 'literówka'),
        (r'\bsuplemet\b', 'suplement', 'literówka'),
        (r'\bsuplemenr\b', 'suplement', 'literówka'),
        (r'\bsuplementó\b', 'suplementów', 'literówka'),
        (r'\bsuplemety\b', 'suplementy', 'literówka'),
        (r'\bdermokosmetykó\b', 'dermokosmetyków', 'literówka'),
        (r'\bColostrumm\b', 'Colostrum', 'literówka'),
        (r'\bcolostrumm\b', 'colostrum', 'literówka'),
        (r'\bGENACITV\b', 'GENACTIV', 'literówka'),
        (r'\bGenacitv\b', 'Genactiv', 'literówka'),
        (r'\bgenacitv\b', 'genactiv', 'literówka'),
        (r'\bMASKA Z COLOSTRUM GENACITV\b', 'MASKA Z COLOSTRUM GENACTIV', 'literówka w nazwie produktu'),
        (r'\bwłaściwośći\b', 'właściwości', 'literówka'),
        (r'\bwłaściwośći\b', 'właściwości', 'literówka'),
        (r'\borganizumu\b', 'organizmu', 'literówka'),
        (r'\bimmunoglobuiny\b', 'immunoglobuliny', 'literówka'),
        (r'\blaktoferynę\s+,\b', 'laktoferynę,', 'literówka'),
        (r'\biodpornośći\b', 'odporności', 'literówka'),
    ],

    # INTERPUNKCJA - punctuation errors
    "interpunkcja": [
        (r'\s+\.(?!\.\.)(?!\d)', ' [SPACJA PRZED KROPKA].', 'spacja przed kropką'),
        (r'\s+,', ' [SPACJA PRZED PRZECINKIEM],', 'spacja przed przecinkiem'),
        (r'\.\.(?!\.)', '..[PODWOJNE KROPKI]', 'podwójne kropki'),
        (r'\s{2,}', '  [PODWOJNA SPACJA]', 'podwójna spacja'),
        (r'(?<=[a-ząćęłńóśźż])\s*;\s*(?=[a-ząćęłńóśźż])', '; [BRAK SPACJI]', 'brak spacji po średniku'),
    ],

    # GRAMATYKA - grammar errors
    "gramatyka": [
        (r'\bktóre które\b', 'które', 'powtórzenie słowa'),
        (r'\bi i\b', 'i', 'powtórzenie słowa'),
        (r'\bw w\b', 'w', 'powtórzenie słowa'),
        (r'\bdo do\b', 'do', 'powtórzenie słowa'),
        (r'\bna na\b', 'na', 'powtórzenie słowa'),
        (r'\bz z\b', 'z', 'powtórzenie słowa'),
        (r'\bże że\b', 'że', 'powtórzenie słowa'),
        (r'\bjest jest\b', 'jest', 'powtórzenie słowa'),
        (r'\bto to\b', 'to', 'powtórzenie słowa'),
        (r'\bsię się\b', 'się', 'powtórzenie słowa'),
    ],

    # STYLISTYKA - style errors
    "stylistyka": [
        (r'\bGenActiv\b', 'Genactiv', 'niezgodność z brand guidelines (powinno być Genactiv)'),
        (r'\bGENACTIV\s+GENACTIV\b', 'GENACTIV', 'powtórzenie marki'),
        (r'\bGenactiv\s+Genactiv\b', 'Genactiv', 'powtórzenie marki'),
        (r',\s*,', ',', 'podwójny przecinek'),
        (r'\.\s*\.(?!\.)', '.', 'podwójne kropki'),
    ],
}

# Known false positives to ignore
FALSE_POSITIVES = [
    'odpornościowego',
    'immunologicznego',
    'enzymatycznego',
    'terapeutycznego',
    'kosmetycznego',
    'dermatologicznego',
    '(17) .',  # references format
    'Mol. Neurosci.',
    'Medycyna Wet.',
]


def get_page_content(url):
    """Fetch and parse page content"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        # Remove script and style elements
        for element in soup(['script', 'style', 'noscript', 'meta', 'link']):
            element.decompose()

        # Get main content areas
        main_content = soup.find('main') or soup.find('article') or soup.find('body')

        if main_content:
            text = main_content.get_text(separator=' ', strip=True)
        else:
            text = soup.get_text(separator=' ', strip=True)

        # Also get title
        title = soup.find('title')
        title_text = title.get_text(strip=True) if title else ""

        return {
            'text': text,
            'title': title_text,
            'html': str(soup)
        }
    except Exception as e:
        return {'text': '', 'title': '', 'html': '', 'error': str(e)}


def check_errors(text, url):
    """Check text for various error types"""
    errors = defaultdict(list)

    for category, patterns in ERROR_PATTERNS.items():
        for pattern, replacement, description in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE if category != 'literowki' else 0)
            for match in matches:
                found_text = match.group()

                # Skip false positives
                is_false_positive = False
                for fp in FALSE_POSITIVES:
                    if fp.lower() in text[max(0, match.start()-20):match.end()+20].lower():
                        is_false_positive = True
                        break

                if not is_false_positive:
                    # Get context
                    start = max(0, match.start() - 40)
                    end = min(len(text), match.end() + 40)
                    context = text[start:end].replace('\n', ' ').strip()

                    errors[category].append({
                        'found': found_text,
                        'should_be': replacement,
                        'description': description,
                        'context': f"...{context}...",
                        'url': url
                    })

    return errors


def scan_all_pages():
    """Scan all pages and collect errors"""
    all_errors = {
        'literowki': [],
        'interpunkcja': [],
        'gramatyka': [],
        'stylistyka': []
    }

    pages_scanned = 0
    pages_with_errors = 0

    all_urls = [
        ('Strona główna i strony informacyjne', PAGES),
        ('Produkty', PRODUCTS),
        ('Kolekcje', COLLECTIONS),
        ('Blog', BLOG_POSTS),
    ]

    stats = {
        'pages': {'scanned': 0, 'with_errors': 0},
        'products': {'scanned': 0, 'with_errors': 0},
        'collections': {'scanned': 0, 'with_errors': 0},
        'blog': {'scanned': 0, 'with_errors': 0},
    }

    for category_name, urls in all_urls:
        print(f"\n{'='*60}")
        print(f"Skanowanie: {category_name} ({len(urls)} stron)")
        print('='*60)

        stat_key = category_name.lower().replace(' główna i strony informacyjne', '').replace('strona ', '').strip()
        if 'strony' in category_name.lower() or 'główna' in category_name.lower():
            stat_key = 'pages'
        elif 'produkt' in category_name.lower():
            stat_key = 'products'
        elif 'kolekcj' in category_name.lower():
            stat_key = 'collections'
        elif 'blog' in category_name.lower():
            stat_key = 'blog'

        for i, url in enumerate(urls):
            print(f"  [{i+1}/{len(urls)}] {url.split('/')[-1][:50]}...", end=' ')

            content = get_page_content(url)

            if content.get('error'):
                print(f"BŁĄD: {content['error']}")
                continue

            errors = check_errors(content['text'], url)

            error_count = sum(len(e) for e in errors.values())
            if error_count > 0:
                print(f"Znaleziono {error_count} błędów")
                stats[stat_key]['with_errors'] += 1
                pages_with_errors += 1
            else:
                print("OK")

            for cat, errs in errors.items():
                all_errors[cat].extend(errs)

            stats[stat_key]['scanned'] += 1
            pages_scanned += 1

            time.sleep(0.3)  # Be nice to the server

    return all_errors, stats, pages_scanned, pages_with_errors


def generate_report(all_errors, stats, pages_scanned, pages_with_errors):
    """Generate markdown report"""

    total_errors = sum(len(e) for e in all_errors.values())

    report = f"""# Pełny raport błędów ortograficznych, gramatycznych i stylistycznych
# genactiv.pl

**Data skanowania:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Łączna liczba przeskanowanych stron:** {pages_scanned}
**Strony z błędami:** {pages_with_errors}

---

## PODSUMOWANIE OGÓLNE

| Typ strony | Przeskanowano | Z błędami |
|------------|---------------|-----------|
| Strony informacyjne | {stats['pages']['scanned']} | {stats['pages']['with_errors']} |
| Produkty | {stats['products']['scanned']} | {stats['products']['with_errors']} |
| Kolekcje | {stats['collections']['scanned']} | {stats['collections']['with_errors']} |
| Blog | {stats['blog']['scanned']} | {stats['blog']['with_errors']} |
| **RAZEM** | **{pages_scanned}** | **{pages_with_errors}** |

---

## PODSUMOWANIE BŁĘDÓW

| Typ błędu | Liczba wystąpień | Priorytet |
|-----------|------------------|-----------|
| Literówki (ortograficzne) | {len(all_errors['literowki'])} | WYSOKI |
| Błędy interpunkcyjne | {len(all_errors['interpunkcja'])} | ŚREDNI |
| Błędy gramatyczne | {len(all_errors['gramatyka'])} | WYSOKI |
| Błędy stylistyczne | {len(all_errors['stylistyka'])} | NISKI |
| **ŁĄCZNIE** | **{total_errors}** | |

---

"""

    # LITERÓWKI
    if all_errors['literowki']:
        report += """## 1. LITERÓWKI (BŁĘDY ORTOGRAFICZNE)

| Strona | Błędne słowo | Poprawka | Kontekst |
|--------|--------------|----------|----------|
"""
        for err in all_errors['literowki']:
            page = err['url'].replace('https://genactiv.pl/', '/')
            report += f"| {page[:40]} | **{err['found']}** | {err['should_be']} | {err['context'][:60]}... |\n"
        report += "\n---\n\n"

    # INTERPUNKCJA
    if all_errors['interpunkcja']:
        report += """## 2. BŁĘDY INTERPUNKCYJNE

| Strona | Typ błędu | Kontekst |
|--------|-----------|----------|
"""
        # Group by type
        by_type = defaultdict(list)
        for err in all_errors['interpunkcja']:
            by_type[err['description']].append(err)

        for error_type, errors in by_type.items():
            for err in errors[:20]:  # Limit per type
                page = err['url'].replace('https://genactiv.pl/', '/')
                report += f"| {page[:35]} | {error_type} | {err['context'][:50]}... |\n"

        # Summary
        report += f"\n**Podsumowanie błędów interpunkcyjnych:**\n"
        for error_type, errors in by_type.items():
            report += f"- {error_type}: {len(errors)} wystąpień\n"
        report += "\n---\n\n"

    # GRAMATYKA
    if all_errors['gramatyka']:
        report += """## 3. BŁĘDY GRAMATYCZNE

| Strona | Błąd | Poprawka | Kontekst |
|--------|------|----------|----------|
"""
        for err in all_errors['gramatyka']:
            page = err['url'].replace('https://genactiv.pl/', '/')
            report += f"| {page[:35]} | **{err['found']}** | {err['should_be']} | {err['context'][:50]}... |\n"
        report += "\n---\n\n"

    # STYLISTYKA
    if all_errors['stylistyka']:
        report += """## 4. BŁĘDY STYLISTYCZNE (BRAND GUIDELINES)

| Strona | Błąd | Poprawka | Opis |
|--------|------|----------|------|
"""
        for err in all_errors['stylistyka']:
            page = err['url'].replace('https://genactiv.pl/', '/')
            report += f"| {page[:35]} | **{err['found']}** | {err['should_be']} | {err['description']} |\n"
        report += "\n---\n\n"

    # PRIORYTETYZACJA
    report += """## PRIORYTETYZACJA NAPRAW

### Priorytet 1 (WYSOKI) - Wpływ na wizerunek marki i SEO
- Wszystkie literówki i błędy ortograficzne
- Błędy gramatyczne (powtórzenia słów)
- Błędy w nazwach produktów

### Priorytet 2 (ŚREDNI) - Profesjonalizm
- Błędy interpunkcyjne (spacje przed kropkami/przecinkami)
- Podwójne spacje

### Priorytet 3 (NISKI) - Brand consistency
- Niezgodności z brand guidelines (GenActiv vs Genactiv)
- Drobne błędy stylistyczne

---

## GLOBALNY BŁĄD - NAGŁÓWEK STRONY

**Problem wykryty na wszystkich stronach:**
Podwójna spacja w banerze "Darmowa dostawa od 300 zł. Darmowa dostawa  od 300 zł."

**Lokalizacja:** Theme → Customize → Header/Announcement bar

---

## UWAGI

1. Raport wygenerowany automatycznie - zalecana ręczna weryfikacja
2. Niektóre "błędy" w cytowaniach naukowych mogą być celowe
3. False positives zostały wykluczone gdzie to możliwe
"""

    return report


def main():
    print("="*60)
    print("PEŁNE SKANOWANIE GENACTIV.PL")
    print("Literówki, błędy gramatyczne, interpunkcyjne, stylistyczne")
    print("="*60)

    all_errors, stats, pages_scanned, pages_with_errors = scan_all_pages()

    print("\n" + "="*60)
    print("GENEROWANIE RAPORTU")
    print("="*60)

    report = generate_report(all_errors, stats, pages_scanned, pages_with_errors)

    # Save report
    report_path = '/Users/user/projects/genactiv-klaviyo/seo/PELNY_RAPORT_BLEDOW_GENACTIV.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nRaport zapisany: {report_path}")

    # Save JSON for detailed analysis
    json_path = '/Users/user/projects/genactiv-klaviyo/seo/bledy_szczegoly.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump({
            'stats': stats,
            'errors': {k: v for k, v in all_errors.items()},
            'total_pages': pages_scanned,
            'pages_with_errors': pages_with_errors
        }, f, ensure_ascii=False, indent=2)
    print(f"Szczegóły JSON: {json_path}")

    # Summary
    total_errors = sum(len(e) for e in all_errors.values())
    print(f"\n{'='*60}")
    print("PODSUMOWANIE")
    print(f"{'='*60}")
    print(f"Przeskanowano stron: {pages_scanned}")
    print(f"Stron z błędami: {pages_with_errors}")
    print(f"Łączna liczba błędów: {total_errors}")
    print(f"  - Literówki: {len(all_errors['literowki'])}")
    print(f"  - Interpunkcja: {len(all_errors['interpunkcja'])}")
    print(f"  - Gramatyka: {len(all_errors['gramatyka'])}")
    print(f"  - Stylistyka: {len(all_errors['stylistyka'])}")


if __name__ == '__main__':
    main()

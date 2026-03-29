#!/usr/bin/env python3
"""
Dodaje meta descriptions do wszystkich kolekcji bez meta.
Poprawki:
- Genactiv (nie GenActiv)
- Bez "do napojów i koktajli"
- Maseczki do skóry twarzy (nie włosów)
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SHOP = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

# Poprawione meta descriptions dla wszystkich 23 kolekcji
COLLECTIONS_META = {
    # ID: (nazwa, meta_description)
    "278965190830": ("Nowości", "Odkryj najnowsze produkty Genactiv z colostrum bovinum. Sprawdź nowości wspierające odporność, regenerację i piękną skórę."),
    "278965223598": ("Najlepiej sprzedające się produkty", "Najpopularniejsze produkty Genactiv z colostrum bovinum. Zobacz bestsellery wybierane przez tysiące zadowolonych klientów."),
    "613251940684": ("Zestawy Świąteczne z Colostrum Genactiv", "Świąteczne zestawy prezentowe Genactiv z colostrum. Podaruj zdrowie i odporność bliskim w wyjątkowej cenie."),
    "618803134796": ("Colostrum i Mleko Klaczy Genactiv", "Colostrum bovinum i mleko klaczy Genactiv. Naturalne wsparcie odporności i regeneracji dla całej rodziny."),
    "621474414924": ("Colostrum tabletki do ssania", "Colostrum Genactiv w tabletkach do ssania. Wygodna forma dla dzieci i dorosłych - smaczne i skuteczne wsparcie odporności."),
    "621474808140": ("Colostrum proszek", "Colostrum Genactiv w proszku. Najwyższa biodostępność składników aktywnych - idealne dla wymagających."),
    "621475070284": ("Colostrum kapsułki", "Colostrum Genactiv w kapsułkach. Wygodna codzienna suplementacja dla osób dorosłych wspierająca odporność."),
    "621708247372": ("COLOSTRUM JUNIOR CZARNY BEZ GENACTIV", "Colostrum Junior z czarnym bzem Genactiv. Pyszne tabletki do ssania dla dzieci wzmacniające odporność."),
    "627600589132": ("Back2school", "Przygotuj dziecko na powrót do szkoły z Genactiv Colostrum. Wspieraj odporność malucha naturalnym colostrum."),
    "652905185612": ("Maseczki z Colostrum", "Maseczki do twarzy z colostrum Genactiv. Intensywna regeneracja i nawilżenie skóry twarzy dzięki naturalnym składnikom."),
    "652905251148": ("Kremy z Colostrum", "Kremy z colostrum Genactiv dla pięknej skóry. Naturalna pielęgnacja wspierająca regenerację i nawilżenie."),
    "652905382220": ("Skóra głowy i włosy", "Kosmetyki Genactiv z colostrum do pielęgnacji skóry głowy i włosów. Naturalne wzmocnienie i regeneracja."),
    "659312509260": ("Genactiv Colostrum Junior z Czarnym Bzem", "Colostrum Junior z czarnym bzem - pyszne tabletki do ssania dla dzieci. Naturalne wsparcie odporności od Genactiv."),
    "659488211276": ("Colostrum dla dzieci", "Colostrum Genactiv dla dzieci - naturalne wsparcie odporności maluchów. Bezpieczne produkty w smacznych formach."),
    "659488670028": ("Colostrum dla dorosłych", "Colostrum Genactiv dla dorosłych. Kapsułki, tabletki i proszek wspierające odporność i regenerację organizmu."),
    "659938640204": ("Buduj odporność dziecka z Genactiv Colostrum", "Wzmocnij odporność dziecka naturalnym colostrum Genactiv. Sprawdzone produkty dla najmłodszych."),
    "662434939212": ("Colostrum A2", "Colostrum A2 Genactiv z mleka krów A2. Premium colostrum dla osób wrażliwych na białko A1."),
    "664150933836": ("Colostrum dla zwierząt", "Colostrum Genactiv dla zwierząt. Naturalne wsparcie odporności i zdrowia Twojego pupila."),
    "664211882316": ("Colostrum dla psów", "Colostrum Genactiv dla psów. Wspieraj zdrowie i odporność swojego psa naturalnym colostrum bovinum."),
    "664212111692": ("Colostrum dla kotów", "Colostrum Genactiv dla kotów. Naturalne wsparcie odporności i zdrowia Twojego kota."),
    "664213619020": ("Colostrum dla koni", "Colostrum Genactiv dla koni. Profesjonalne wsparcie odporności i regeneracji dla koni sportowych i hodowlanych."),
    "668385509708": ("Wszystkie produktu", "Pełna oferta produktów Genactiv z colostrum bovinum. Suplementy, kosmetyki i produkty dla zwierząt."),
    "670751654220": ("-20% z kodem FERIE", "Promocja zimowa Genactiv! Odbierz 20% rabatu na produkty z colostrum z kodem FERIE. Wspieraj odporność w niższej cenie."),
}

def update_collection_meta(collection_id, meta_description):
    """Aktualizuje meta description kolekcji przez GraphQL API"""
    url = f"https://{SHOP}/admin/api/{API_VERSION}/graphql.json"

    mutation = """
    mutation collectionUpdate($input: CollectionInput!) {
      collectionUpdate(input: $input) {
        collection {
          id
          title
          seo {
            description
          }
        }
        userErrors {
          field
          message
        }
      }
    }
    """

    variables = {
        "input": {
            "id": f"gid://shopify/Collection/{collection_id}",
            "seo": {
                "description": meta_description
            }
        }
    }

    headers = {
        "X-Shopify-Access-Token": TOKEN,
        "Content-Type": "application/json"
    }

    response = requests.post(
        url,
        json={"query": mutation, "variables": variables},
        headers=headers
    )

    return response.json()

def main():
    print("=" * 60)
    print("DODAWANIE META DESCRIPTIONS DO KOLEKCJI GENACTIV")
    print("=" * 60)
    print(f"\nLiczba kolekcji do zaktualizowania: {len(COLLECTIONS_META)}")
    print()

    success_count = 0
    error_count = 0

    for collection_id, (name, meta) in COLLECTIONS_META.items():
        print(f"[{success_count + error_count + 1}/{len(COLLECTIONS_META)}] {name}...")

        result = update_collection_meta(collection_id, meta)

        if "errors" in result:
            print(f"   ❌ BŁĄD: {result['errors']}")
            error_count += 1
        elif result.get("data", {}).get("collectionUpdate", {}).get("userErrors"):
            errors = result["data"]["collectionUpdate"]["userErrors"]
            print(f"   ❌ BŁĄD: {errors}")
            error_count += 1
        else:
            print(f"   ✅ OK")
            success_count += 1

        # Pauza między requestami
        time.sleep(0.5)

    print()
    print("=" * 60)
    print(f"PODSUMOWANIE:")
    print(f"  Sukces: {success_count}")
    print(f"  Błędy: {error_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()

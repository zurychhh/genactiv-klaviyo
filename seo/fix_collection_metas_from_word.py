#!/usr/bin/env python3
"""
Wgrywa ORYGINALNE meta descriptions z dokumentu Word
z 3 poprawkami:
1. GenActiv → Genactiv
2. Usunięcie "do napojów i koktajli"
3. Maseczki do włosów → do twarzy
"""

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

SHOP = os.environ.get("SHOPIFY_DOMAIN", "genactiv.myshopify.com")
TOKEN = os.environ.get("SHOPIFY_ACCESS_TOKEN", "")
API_VERSION = os.environ.get("SHOPIFY_API_VERSION", "2024-01")

# Oryginalne treści z Word + poprawki
COLLECTIONS_META = {
    "278965190830": "Odkryj nowości Genactiv – najnowsze produkty z colostrum bovinum. Naturalne suplementy diety wspierające odporność i zdrowie.",
    "278965223598": "Bestsellery Genactiv – najpopularniejsze produkty z colostrum wybierane przez klientów. Sprawdź, co polecają inni.",
    "613251940684": "Świąteczne zestawy Genactiv z colostrum – idealny prezent na zdrowie. Oszczędzaj kupując produkty w zestawach promocyjnych.",
    "618803134796": "Colostrum i mleko klaczy Genactiv – unikalne połączenie dla zdrowia. 100% naturalne, liofilizowane, zachowujące pełną wartość.",
    "621474414924": "Colostrum Genactiv w tabletkach do ssania – wygodna i smaczna forma suplementacji dla dzieci i dorosłych. Idealne w podróży.",
    # POPRAWKA: usunięte "do napojów i koktajli"
    "621474808140": "Colostrum Genactiv w proszku – czysta siara bydlęca. Łatwe dozowanie, najwyższa jakość liofilizatu.",
    "621475070284": "Colostrum Genactiv w kapsułkach – wygodna codzienna suplementacja. Czyste, niemodyfikowane colostrum wspierające odporność.",
    "621708247372": "Colostrum Junior z czarnym bzem – naturalne wsparcie odporności dla dzieci. Smaczne tabletki do ssania o owocowym smaku.",
    "627600589132": "Wróć do szkoły z Genactiv – colostrum wspierające odporność i koncentrację u dzieci. Naturalna ochrona w sezonie szkolnym.",
    "630708076876": "Akcesoria Genactiv – praktyczne dodatki do suplementacji colostrum. Miarki, pojemniki i inne przydatne produkty.",
    # POPRAWKA: "do włosów" → "do twarzy", zmieniona treść
    "652905185612": "Maseczki do twarzy z colostrum Genactiv – intensywna regeneracja i odżywienie skóry. Naturalna pielęgnacja dla pięknej cery.",
    "652905251148": "Kremy z colostrum Genactiv – naturalna pielęgnacja skóry. Nawilżenie, regeneracja i ochrona dla każdego typu cery.",
    "652905382220": "Kosmetyki Genactiv do skóry głowy i włosów – colostrum dla zdrowych, mocnych włosów. Naturalna regeneracja i pielęgnacja.",
    "659312509260": "Colostrum Junior z czarnym bzem Genactiv – wsparcie odporności dla dzieci. Smaczne tabletki wzmacniające naturalną ochronę.",
    "659488211276": "Colostrum Genactiv dla dzieci – naturalne wsparcie odporności i rozwoju. Bezpieczne suplementy w smacznych formach dla maluchów.",
    "659488670028": "Colostrum Genactiv dla dorosłych – naturalne wsparcie odporności, regeneracji i witalności. Suplementy w kapsułkach i proszku.",
    "659938640204": "Buduj odporność dziecka z colostrum Genactiv – naturalne wsparcie układu immunologicznego. Sprawdzone produkty dla dzieci.",
    "662434939212": "Colostrum A2 Genactiv – siara z białkiem A2, łatwiejsza w trawieniu. Naturalna alternatywa dla osób wrażliwych na białko A1.",
    "664150933836": "Colostrum Genactiv dla zwierząt – naturalne wsparcie odporności i zdrowia pupili. Suplementy dla psów, kotów i koni.",
    "664211882316": "Colostrum Genactiv dla psów – naturalne wsparcie odporności i witalności czworonoga. Sprawdzone suplementy dla Twojego psa.",
    "664212111692": "Colostrum Genactiv dla kotów – naturalne wsparcie zdrowia i odporności kota. Suplementy w formie proszku dla Twojego pupila.",
    "664213619020": "Colostrum Genactiv dla koni – naturalne wsparcie odporności i regeneracji. Suplementy dla zdrowia i witalności Twojego konia.",
    "668385509708": "Wszystkie produkty Genactiv – pełna oferta colostrum i suplementów. Kapsułki, proszki, tabletki i dermokosmetyki w jednym miejscu.",
    "670751654220": "Promocja zimowa Genactiv – 20% rabatu z kodem FERIE. Skorzystaj z okazji na produkty z colostrum w niższych cenach.",
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
    print("=" * 70)
    print("WGRYWANIE ORYGINALNYCH META DESCRIPTIONS Z WORDA (Z POPRAWKAMI)")
    print("=" * 70)
    print("\nPoprawki zastosowane:")
    print("  1. GenActiv → Genactiv")
    print("  2. Usunięte 'do napojów i koktajli' (proszek)")
    print("  3. Maseczki 'do włosów' → 'do twarzy'")
    print()
    print(f"Liczba kolekcji: {len(COLLECTIONS_META)}")
    print()

    success_count = 0
    error_count = 0

    for collection_id, meta in COLLECTIONS_META.items():
        result = update_collection_meta(collection_id, meta)

        if "errors" in result:
            print(f"❌ ID {collection_id}: {result['errors']}")
            error_count += 1
        elif result.get("data", {}).get("collectionUpdate", {}).get("userErrors"):
            errors = result["data"]["collectionUpdate"]["userErrors"]
            print(f"❌ ID {collection_id}: {errors}")
            error_count += 1
        else:
            title = result["data"]["collectionUpdate"]["collection"]["title"]
            print(f"✅ {title}")
            success_count += 1

        time.sleep(0.3)

    print()
    print("=" * 70)
    print(f"PODSUMOWANIE: Sukces: {success_count}, Błędy: {error_count}")
    print("=" * 70)

if __name__ == "__main__":
    main()

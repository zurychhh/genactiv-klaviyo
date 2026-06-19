# -*- coding: utf-8 -*-
import json

# Nowe meta title (<=60) dla kolekcji bez tytułu (+ Colosregen: poprawa)
TITLE = {
 "278638461102": "Dermokosmetyki z colostrum – Genactiv",
 "278638493870": "Nowości – suplementy z colostrum | Genactiv",
 "278638526638": "Bestsellery – colostrum Genactiv",
 "278965190830": "Nowości Genactiv – colostrum bovinum",
 "278965223598": "Bestsellery Genactiv – najpopularniejsze produkty",
 "279171006638": "Promocje – colostrum Genactiv",
 "607298388300": "Nowy rok szkolny z colostrum – Genactiv",
 "613251940684": "Zestawy świąteczne z colostrum – Genactiv",
 "618803134796": "Colostrum i mleko klaczy – Genactiv",
 "621474414924": "Colostrum tabletki do ssania – Genactiv",
 "621474808140": "Colostrum w proszku – Genactiv",
 "621475070284": "Colostrum w kapsułkach – Genactiv",
 "621708247372": "Colostrum Junior z czarnym bzem – Genactiv",
 "627600589132": "Back to school z colostrum – Genactiv",
 "630708076876": "Akcesoria Genactiv",
 "652905185612": "Maseczki z colostrum – Genactiv",
 "652905251148": "Kremy z colostrum – Genactiv",
 "652905382220": "Skóra głowy i włosy – kosmetyki Genactiv",
 "659312509260": "Colostrum Junior z czarnym bzem – Genactiv",
 "659488211276": "Colostrum dla dzieci – Genactiv",
 "659488670028": "Colostrum dla dorosłych – Genactiv",
 "659938640204": "Buduj odporność dziecka z colostrum – Genactiv",
 "662434939212": "Colostrum A2 – siara z białkiem A2 | Genactiv",
 "664150933836": "Colostrum dla zwierząt – Genactiv",
 "664211882316": "Colostrum dla psów – Genactiv",
 "664212111692": "Colostrum dla kotów – Genactiv",
 "664213619020": "Colostrum dla koni – Genactiv",
 "668385509708": "Wszystkie produkty Genactiv – colostrum",
 "678550274380": "Wsparcie jelit z colostrum – Genactiv",
 "680500134220": "Książki o colostrum – Genactiv",
 "682938630476": "Colostrum dla mamy – Genactiv",
 "683168366924": "Błonnik z colostrum – Genactiv",
 "278475047086": "Colosregen – serum na porost włosów | Genactiv",
}

# Nowe/wydłużone meta description (120-160) — brakujące lub za krótkie
NEW_DESC = {
 "278638493870": "Sprawdź najnowsze produkty Genactiv z colostrum – suplementy diety i dermokosmetyki wspierające odporność i zdrowie. Zobacz nowości w sklepie!",
 "278638526638": "Bestsellery Genactiv – najczęściej wybierane produkty z colostrum. Sprawdź, po co najchętniej sięgają nasi klienci, i zamów w sklepie!",
 "279171006638": "Promocje Genactiv – produkty z colostrum w niższych cenach. Zadbaj o odporność i zdrowie, oszczędzając. Sprawdź aktualne oferty w sklepie!",
 "607298388300": "Przygotuj dziecko na nowy rok szkolny z colostrum Genactiv – naturalne wsparcie odporności w sezonie infekcyjnym. Sprawdź ofertę w sklepie!",
 "678550274380": "Wsparcie jelit z colostrum i błonnikiem Genactiv – produkty wspierające mikrobiotę i prawidłową kondycję jelit. Sprawdź ofertę w sklepie!",
 "680500134220": "Książki o colostrum w sklepie Genactiv – poznaj właściwości siary bydlęcej z rzetelnych źródeł. Wiedza, która wspiera świadome zdrowie!",
 "682938630476": "Colostrum dla mamy Genactiv – naturalne wsparcie odporności i kondycji w codziennej rutynie. Sprawdź produkty dla mam w naszym sklepie!",
 "683168366924": "Błonnik z colostrum Genactiv – produkty FIBERBIOM wspierające mikrobiotę i prawidłową pracę jelit. Sprawdź ofertę błonnika w sklepie!",
 "278475047086": "Produkty z linii Colosregen Genactiv – serum i kosmetyki na porost i kondycję włosów z colostrum. Sprawdź naturalną pielęgnację w sklepie!",
}

# load current SEO (zachowanie istniejących opisów dla kolekcji, gdzie dodaję tylko tytuł)
coll = json.load(open("altfix/collections_seo.json"))
CUR = {c["id"].split("/")[-1]: (c["seo"].get("description") or "") for c in coll["collections"]["nodes"]}

OMNIBUS = {"624721625420","624721658188","624721690956"}

items=[]
for cid in TITLE:
    if cid in OMNIBUS: continue
    desc = NEW_DESC.get(cid) or CUR.get(cid,"")
    items.append({"id":cid,"type":"collection","metaTitle":TITLE[cid],"metaDescription":desc})

# walidacja
bt=bd=0
for it in items:
    if len(it["metaTitle"])>60: bt+=1; print("TITLE>60", len(it["metaTitle"]), it["id"], it["metaTitle"])
    if it["id"] in NEW_DESC:
        n=len(it["metaDescription"])
        if not(120<=n<=160): bd+=1; print("NEWDESC POZA", n, it["id"])
print(f"itemów: {len(items)} | tytuły>60: {bt} | nowe-desc poza: {bd}")
# ile zachowanych opisów jest pustych (nie powinno; te z brakiem desc mają NEW_DESC)
empty=[it["id"] for it in items if not it["metaDescription"]]
print("itemy z pustym opisem:", empty)
json.dump(items, open("altfix/coll_items.json","w"), ensure_ascii=False)
print("zapisano coll_items.json")

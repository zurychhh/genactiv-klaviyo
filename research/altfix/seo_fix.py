# -*- coding: utf-8 -*-
import json, re
sc = json.load(open("altfix/seo_content.json"))
MT = sc["META_TITLE"]; MD = sc["META_DESC"]

# Nowe meta description (120-160) dla produktów, którym wyzerowano opis (lub brakowało)
MD2 = {
 "15745399095628": "FIBERBIOM Genactiv – dwupak (2 x 15 saszetek): rozpuszczalny błonnik z kory modrzewia i colostrum. Wsparcie mikrobioty i jelit. Zamów w Genactiv!",
 "8678171705676": "Zestaw promocyjny Back2School Genactiv – produkty z colostrum wspierające odporność całej rodziny na start roku szkolnego. Zamów w Genactiv!",
 "7700656816302": "Zestaw Mocne włosy: maska z colostrum i Colostrum Genactiv 120 kapsułek. Wsparcie włosów słabych i wypadających. Zamów w sklepie Genactiv!",
 "9362070241612": "Zestaw Zdrowa rutyna Genactiv – praktyczne akcesoria z recyklingu na co dzień. Wygoda, styl i troska o zdrowie. Zamów w sklepie Genactiv!",
 "8662581936460": "Colostrum i mleko klaczy Genactiv – 180 kapsułek w promocji (krótsza data przydatności). Wsparcie odporności i kondycji. Zamów w Genactiv!",
 "9279378161996": "Torba na ramię Genactiv – pojemny shopper w 100% z recyklingu, na zakupy, siłownię i miasto. Lekka i wygodna. Zamów w sklepie Genactiv!",
 "8875601133900": "Maseczka do twarzy z Colostrum Genactiv (Colostrigen R), 50 ml – odżywczo-rewitalizująca dla każdego typu skóry. Zamów w sklepie Genactiv!",
 "9300666679628": "Butelka Junior Genactiv – kompaktowy bidon dla dzieci do szkoły i na wycieczki. Zachęca do nawadniania. Zamów w sklepie Genactiv już dziś!",
 "7365301338286": "Colostrum Genactiv kapsułki – trójpak (180 kapsułek). Wartościowe wsparcie odporności na dłużej, w korzystnej cenie. Zamów w Genactiv!",
 "14927422095692": "Colostrum Junior z czarnym bzem Genactiv – tabletki do ssania, dwupak (120 szt.). Codzienne wsparcie diety dzieci. Zamów w Genactiv!",
 "8959067029836": "Colostrum Junior z czarnym bzem Genactiv – 60 tabletek do ssania. Smaczne, codzienne wsparcie diety dzieci. Zamów w sklepie Genactiv!",
 "14927421636940": "Colostrum Junior z czarnym bzem Genactiv – zawiesina, dwupak (2 x 300 ml). Codzienne wsparcie diety dzieci. Zamów w sklepie Genactiv!",
 "14927420784972": "Colostrum Junior z czarnym bzem Genactiv – proszek w saszetkach, dwupak (60 szt.). Wsparcie diety dzieci. Zamów w sklepie Genactiv!",
 "7365298094254": "Colostrum z maliną Genactiv – tabletki do ssania, trójpak (180 szt.). Smaczne wsparcie codziennej odporności. Zamów w sklepie Genactiv!",
 "7782326632622": "Colostrum i mleko klaczy Genactiv – 180 kapsułek. Wartościowe wsparcie odporności i kondycji organizmu. Zamów w sklepie Genactiv!",
 "7418110705838": "Colostrum i mleko klaczy Genactiv – proszek, dwupak (400 g). Wartościowe uzupełnienie codziennej diety. Zamów w sklepie Genactiv!",
 "7365316313262": "Mleko klaczy Genactiv – 30 saszetek liofilizowanego mleka klaczy. Wartościowe uzupełnienie diety. Zamów w sklepie Genactiv już dziś!",
 "7782370279598": "Colostrum i mleko klaczy Genactiv – dwupak (360 kapsułek). Wsparcie odporności i kondycji na dłużej. Zamów w sklepie Genactiv!",
 "7647040962734": "Krem do stóp z Colostrum Genactiv, 75 ml – regeneracja i pielęgnacja przesuszonej skóry stóp. Zamów w sklepie Genactiv już dziś!",
 "8358508691788": "Colostrum Junior Genactiv – zawiesina, dwupak (2 x 150 ml). Smaczne, codzienne wsparcie diety najmłodszych. Zamów w sklepie Genactiv!",
 "7365307170990": "Zestaw Silne włosy: serum z colostrum i Colostrum Genactiv 120 kapsułek. Wsparcie włosów słabych i wypadających. Zamów w Genactiv!",
 "14930242568524": "Mleko klaczy Genactiv – proszek w saszetkach, dwupak (60 szt.). Wartościowe uzupełnienie codziennej diety. Zamów w sklepie Genactiv!",
 "8678264504652": "Colostrum Junior Genactiv – zawiesina, trójpak (3 x 150 ml). Smaczne, codzienne wsparcie diety najmłodszych. Zamów w sklepie Genactiv!",
 "15091398934860": "FIBERBIOM Genactiv (15 saszetek) – rozpuszczalny błonnik z kory modrzewia i colostrum. Wsparcie mikrobioty i jelit. Zamów w Genactiv!",
 "7418100089006": "Colostrum Genactiv 120 kapsułek i mleko klaczy Genactiv 120 kapsułek – podwójne wsparcie odporności. Zamów w sklepie Genactiv już dziś!",
 "9353901408588": "Kosmetyczka Genactiv – poręczna, wykonana w 100% z recyklingu. Na kosmetyki, suplementy i codzienne drobiazgi. Zamów w sklepie Genactiv!",
 "7666916819118": "Zestaw: Colostrum Junior Genactiv zawiesina i colostrum z maliną tabletki do ssania. Wsparcie odporności dzieci. Zamów w Genactiv!",
 "7418120863918": "Zestaw Trzy kroki do pięknych włosów Genactiv – kompleksowa pielęgnacja włosów słabych i wypadających. Zamów w sklepie Genactiv!",
 "7365304582318": "Zestaw Wzmocniona odporność: Colostrum Genactiv 120 kapsułek i colostrum z maliną 60 tabletek. Zamów w sklepie Genactiv już dziś!",
 "9331608748364": "Butelka termiczna Genactiv – utrzymuje temperaturę napojów gorących i zimnych. Stylowe akcesorium na co dzień. Zamów w sklepie Genactiv!",
}
# Furever Cat 75 g – title wyzerowany przy poprzednim zapisie, przywracam (desc już ma z MD)
TITLE_FIX = {"15338216882508": "Furever Cat proszek 75 g – Genactiv"}

# walidacja
bad=0
for k,v in MD2.items():
    n=len(v)
    if not(120<=n<=160): bad+=1; print("DESC POZA ZAKRESEM", n, k, v)
for k,v in TITLE_FIX.items():
    if len(v)>60: bad+=1; print("TITLE ZA DŁUGI", len(v), k)
print("MD2:", len(MD2), "| TITLE_FIX:", len(TITLE_FIX), "| problemy:", bad)

# zbuduj itemy: oba pola zawsze. metaTitle z META_TITLE (live), desc z MD2.
items=[]
for pid, desc in MD2.items():
    items.append({"id":pid,"type":"product","metaTitle":MT[pid],"metaDescription":desc})
# Furever Cat: title fix + zachowaj jego desc (MD)
items.append({"id":"15338216882508","type":"product","metaTitle":TITLE_FIX["15338216882508"],"metaDescription":MD["15338216882508"]})
print("itemów do korekty:", len(items))
b1,b2=items[:25],items[25:]
json.dump({"b1":b1,"b2":b2}, open("altfix/seo_fix_batches.json","w"), ensure_ascii=False)
print("B1:", len(b1), "B2:", len(b2))

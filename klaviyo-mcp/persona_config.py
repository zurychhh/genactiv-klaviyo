"""Konfiguracja person LP GenActiv — jedno zrodlo prawdy.

PRIORYTET (1 = najwyzszy) rozstrzyga konflikty przy przypisaniu MECE.
Zasada: od intencji najbardziej specyficznej / najbardziej rozlacznej
do najogolniejszej. Persona o nizszym numerze wygrywa.

SYGNALY, w kolejnosci sily:
  1. LP  — wizyta na konkretnym landing page'u (Active on Site -> `page`).
           Jedyny sygnal, ktory rozroznia persony dzielace te same produkty
           (Fiberbiom: odchudzanie / plaski brzuch / regularnosc;
            Mleko klaczy: silversi / skin&gut).
  2. PRODUKT — zakup (cala historia) lub obejrzenie karty (365 dni).

DECYZJA KLIENTA 10.09.2026: maksymalne pokrycie bazy. Grupy produktowe
wieloznaczne sa dopisywane do najszerszej pasujacej persony:
  - Fiberbiom bez sygnalu LP        -> REGULARNOSC (prio 8)
  - Colostrum dorosly bez sygnalu LP -> GUT FIXER  (prio 9)
Te przypisania sa ZALOZENIEM, nie faktem — dlatego kazdy profil niesie
`persona_lp_zrodlo` = 'lp' | 'produkt'. Do pomiaru skutecznosci przekazu
zawsze rozbijaj wynik po tym polu.
"""

LP_DAYS = 365       # okno dla wizyty na LP
VIEW_DAYS = 365     # okno dla obejrzenia karty produktu
# zakup: cala historia (alltime)

# --------------------------------------------------------------------------
# SYGNALY PRODUKTOWE — definicje niezalezne od person.
# `key` odpowiada nazwie segmentu "SYG | PRODUKT <key>" w Klaviyo.
# --------------------------------------------------------------------------
PRODUCT_SIGNALS = {
    "junior": {
        "sku": ["CZCB", "CJZ", "CZM", "BANMALJUN", "CGZJCGZ"],
        "url": ["junior", "colostrum-z-malina", "malinowa-odpornosc",
                "back2school", "odpornosc-dla-najmlodszych"],
    },
    "wlosy": {
        "sku": ["SERUM", "MASKA", "SZAMPON", "BLOKER"],
        "url": ["serum-z-colostrum", "maska-z-colostrum", "szampon",
                "bloker", "wlosow", "wlosy"],
    },
    "glow": {
        "sku": ["MASECZKA", "KREM"],
        "url": ["maseczka", "krem-z-", "krem-do-stop", "pieknej-skory"],
    },
    "silversi": {
        "sku": ["MK", "CIMK", "CGIMK"],
        "url": ["mleko-klaczy", "podwojna-regeneracja", "wzmocniona-kondycja"],
    },
    # Wieloznaczne — patrz DECYZJA KLIENTA w naglowku.
    "rez_fiberbiom": {
        "sku": ["FIBER"],
        "url": ["fiberbiom"],
    },
    "rez_odpornosc": {
        "sku": ["CG", "CZB", "CZCP", "A2", "KSIAZKA"],
        "url": ["colostrum-genactiv", "colostrum-z-bananem",
                "colostrum-z-czarna-porzeczka", "potrojna-odpornosc",
                "wzmocniona-odpornosc", "colostrum-dla-doroslych"],
    },
    "rez_zwierzeta": {
        "sku": ["FUREVER", "VET-", "VAT-"],
        "url": ["furever", "dla-kota", "dla-kotow", "dla-psow", "zwierzat"],
    },
}

# --------------------------------------------------------------------------
# 9 PERSON Z LANDING PAGE'AMI
# `produkt` = klucz sygnalu produktowego zasilajacego te persone (albo None).
# --------------------------------------------------------------------------
PERSONAS = [
    {
        "prio": 1, "key": "junior", "name": "JUNIOR | Rodzic dziecka 3-7 lat",
        "lp": "/pages/colostrum-dla-juniora", "produkt": "junior",
        "opis": "Rodzic kupujacy dla dziecka. Odpornosc, sezon infekcji, przedszkole.",
        "dlaczego_prio": "Kupuje dla kogos innego niz on sam — intencja calkowicie "
                         "rozlaczna z reszta. Produkty juniorskie sa unikalne.",
    },
    {
        "prio": 2, "key": "wlosy", "name": "WŁOSY | Wypadanie i skóra głowy",
        "lp": "/pages/kosmetyki-wypadanie-i-lagodzenie", "produkt": "wlosy",
        "opis": "Wypadanie wlosow, swedzenie i suchosc skory glowy, trychologia.",
        "dlaczego_prio": "Unikalne SKU (szampon/maska/serum/bloker), zaden inny "
                         "segment po nie nie siega.",
    },
    {
        "prio": 3, "key": "glow", "name": "GLOW | Kosmetyki do twarzy, nawilżenie",
        "lp": "/pages/glow-nawilzenie", "produkt": "glow",
        "opis": "Matowa, odwodniona, wrazliwa skora twarzy. Efekt glow, kremy i maseczki.",
        "dlaczego_prio": "Unikalne SKU kosmetyczne (krem/maseczka). Nizej niz wlosy, "
                         "bo kolekcje dermo lacza oba typy — wlosy maja pierwszenstwo.",
    },
    {
        "prio": 4, "key": "skingut", "name": "SKIN&GUT | Skóra od środka",
        "lp": "/pages/skin-and-gut-connector", "produkt": None,
        "opis": "Zdrowa skora zaczyna sie w jelitach. Suplement (nie kosmetyk) na cere, "
                "wlosy i paznokcie przez os jelito-skora.",
        "dlaczego_prio": "Dzieli produkty z Silversi w 100% — rozroznia je WYLACZNIE LP. "
                         "Wyzej, bo intencja wezsza; Silversi zostaje domyslnym domem "
                         "dla kupujacych mleko klaczy bez sygnalu LP.",
    },
    {
        "prio": 5, "key": "silversi", "name": "SILVERSI | 50+, mleko klaczy",
        "lp": "/pages/silversi", "produkt": "silversi",
        "opis": "Osoby 50+, zmieniona praca jelit, nietolerancja mleka krowiego, "
                "lagodne formuly z mlekiem klaczy.",
        "dlaczego_prio": "Domyslny dom dla kupujacych mleko klaczy bez sygnalu LP.",
    },
    {
        "prio": 6, "key": "odchudzanie", "name": "ODCHUDZANIE | Fiberbiom w redukcji",
        "lp": "/pages/fiberbiom-w-odchudzaniu", "produkt": None,
        "opis": "Dieta i deficyt kaloryczny, napady glodu, sytosc, zaparcia przy redukcji.",
        "dlaczego_prio": "Najbardziej odrebna komercyjnie intencja sposrod trzech "
                         "person Fiberbiomu — dlatego wymaga sygnalu LP, nie zgadujemy jej.",
    },
    {
        "prio": 7, "key": "plaski_brzuch", "name": "PŁASKI BRZUCH | Wzdęcia",
        "lp": "/pages/plaski-brzuch", "produkt": None,
        "opis": "Wzdecia po posilkach, gazy, uczucie napietego brzucha.",
        "dlaczego_prio": "Objawowa, wezsza niz ogolna regularnosc — tez wymaga LP.",
    },
    {
        "prio": 8, "key": "regularnosc", "name": "REGULARNOŚĆ | Wypróżnianie",
        "lp": "/pages/fiberbiom-regularne-wyproznianie", "produkt": "rez_fiberbiom",
        "opis": "Zaparcia, dni bez wyproznienia, naturalny rytm jelit.",
        "dlaczego_prio": "Najogolniejsza obietnica Fiberbiomu — dlatego to ona przejmuje "
                         "kupujacych Fiberbiom bez sygnalu LP (decyzja klienta 10.09.2026).",
    },
    {
        "prio": 9, "key": "gutfixer", "name": "GUT FIXER | Bariera jelitowa",
        "lp": "/pages/gutfixer", "produkt": "rez_odpornosc",
        "opis": "Nieszczelna bariera jelitowa, stany zapalne, mikrobiota, stres i trawienie.",
        "dlaczego_prio": "Najszersza propozycja jelitowa. LP Gut Fixer promuje dokladnie "
                         "te SKU co colostrum dla doroslych (proszek, 120 kaps.), wiec "
                         "przejmuje te grupe — dopasowanie wynika z tresci LP.",
    },
]

# --------------------------------------------------------------------------
# REZYDUA — domykaja MECE.
# --------------------------------------------------------------------------
RESIDUALS = [
    {
        "prio": 10, "key": "rez_zwierzeta", "name": "REZ | Zwierzęta (Furever)",
        "lp": None, "produkt": "rez_zwierzeta",
        "opis": "Colostrum dla psow, kotow i koni. Zupelnie inny odbiorca i przekaz.",
        "dlaczego_prio": "Ostatni w kolejce: kto kupuje i dla siebie, i dla zwierzaka, "
                         "trafia do swojej persony ludzkiej.",
    },
]

# Profile bez zadnego z powyzszych sygnalow NIE dostaja wlasciwosci `persona_lp`.
# Segment "REZ | Bez sygnalu" = `persona_lp is not set` — domyka podzial na cala baze.
PROPERTY = "persona_lp"
PROPERTY_SOURCE = "persona_lp_zrodlo"   # 'lp' albo 'produkt'
PROPERTY_DATE = "persona_lp_data"

ALL_BUCKETS = PERSONAS + RESIDUALS

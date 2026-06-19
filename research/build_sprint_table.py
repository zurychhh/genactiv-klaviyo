# -*- coding: utf-8 -*-
"""
Eksport sprintu czerwiec 2026 do CSV (import do Monday / Google Sheets).
Reużywa danych z build_sprint_june.py i dokłada Status + Brama ręczna.
Uruchom: python3 build_sprint_table.py  ->  sprint-czerwiec-2026-tasks.csv
"""
import csv
from build_sprint_june import TASKS, WEEKS, STREAMS, BOT, GATE, GATE_LABEL, _init_status

OUT = "sprint-czerwiec-2026-tasks.csv"
WK = {w["id"]: w for w in WEEKS}
OWNER = {"cc": "CC / Claude Code", "hy": "CC+ / Hybryda", "hu": "MAN / Ręcznie"}
GATE_TXT = {"start": "Wymaga ręcznej interwencji przed startem",
            "verify": "Weryfikacja ręczna przed Done", "": "—"}

HEADERS = ["ID", "Sprint", "Daty", "Stream", "Stream nazwa", "Zadanie", "Owner",
           "Priorytet", "Estymacja", "Wplyw KPI", "Zaleznosci (ID)", "Status poczatkowy",
           "Brama reczna", "Definition of Done", "Prompt Claude Code"]

def run():
    rows = []
    for t in TASKS:
        wk = WK[t["week"]]
        rows.append([
            t["id"], f'{wk["label"]} ({t["week"]})', wk["dates"],
            t["stream"], STREAMS[t["stream"]][0], t["title"], OWNER[t["owner"]],
            t["pri"], t["est"], t["kpi"], t["dep"], _init_status(t),
            GATE_TXT[GATE[t["id"]]], t["dod"], t["prompt"] or "",
        ])
    with open(OUT, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        wr.writerow(HEADERS)
        wr.writerows(rows)
    print("OK ->", OUT, "| wierszy:", len(rows))
    # podsumowanie bramek
    starts = [t["id"] for t in TASKS if GATE[t["id"]] == "start"]
    verifs = [t["id"] for t in TASKS if GATE[t["id"]] == "verify"]
    print("Przed startem (ręczna interwencja):", ", ".join(starts))
    print("Weryfikacja przed Done:", ", ".join(verifs))

if __name__ == "__main__":
    run()

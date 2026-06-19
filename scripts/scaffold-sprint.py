#!/usr/bin/env python3
"""
scaffold-sprint.py — Tworzy drzewo katalogow sprintu z CSV.

Czyta research/sprint-czerwiec-2026-tasks.csv (24 zadania) i generuje:
  sprint-2026-06/
    W1/
      A1/
        task.md       — seedowany z CSV
        artefakty/    — pusty katalog na output
        status.txt    — "pending"
      A2/
        ...
    W2/
      ...
    INDEX.md          — spis tresci

Idempotentny: nie nadpisuje istniejacych plikow.
"""

import csv
import os
import sys
from pathlib import Path
from datetime import date

REPO_ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = REPO_ROOT / "research" / "sprint-czerwiec-2026-tasks.csv"
SPRINT_DIR = REPO_ROOT / "sprint-2026-06"

# Mapowanie nazw tygodni z CSV na katalogi
WEEK_MAP = {
    "Tydzień 1 (W1)": "W1",
    "Tydzień 2 (W2)": "W2",
    "Tydzień 3 (W3)": "W3",
    "Tydzień 4 (W4)": "W4",
    "Domknięcie (W5)": "W5",
}


def read_tasks(csv_path: Path) -> list[dict]:
    """Czyta CSV i zwraca liste zadan."""
    tasks = []
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks


def make_task_md(task: dict) -> str:
    """Generuje tresc task.md z danych CSV."""
    lines = [
        f"# {task['ID']} — {task['Zadanie']}",
        "",
        f"**Sprint:** {task['Sprint']}",
        f"**Daty:** {task['Daty']}",
        f"**Stream:** {task['Stream']} — {task['Stream nazwa']}",
        f"**Owner:** {task['Owner']}",
        f"**Priorytet:** {task['Priorytet']}",
        f"**Estymacja:** {task['Estymacja']}",
        f"**Wplyw KPI:** {task['Wplyw KPI']}",
        f"**Zaleznosci:** {task.get('Zaleznosci (ID)', '—') or '—'}",
        f"**Status poczatkowy:** {task['Status poczatkowy']}",
        f"**Brama reczna:** {task.get('Brama reczna', '—') or '—'}",
        "",
        "## Definition of Done",
        "",
        task.get("Definition of Done", "—") or "—",
        "",
        "## Prompt Claude Code",
        "",
        task.get("Prompt Claude Code", "—") or "—",
        "",
    ]
    return "\n".join(lines)


def scaffold(tasks: list[dict]) -> dict:
    """Tworzy drzewo katalogow. Zwraca statystyki."""
    stats = {"created": 0, "skipped": 0, "weeks": set()}

    for task in tasks:
        task_id = task["ID"]
        sprint_raw = task["Sprint"]
        week = WEEK_MAP.get(sprint_raw, sprint_raw.split("(")[-1].rstrip(")").strip())

        stats["weeks"].add(week)

        task_dir = SPRINT_DIR / week / task_id
        artefakty_dir = task_dir / "artefakty"
        task_md_path = task_dir / "task.md"
        status_path = task_dir / "status.txt"

        # Tworzenie katalogu (zawsze, bo mkdir jest idempotentne)
        artefakty_dir.mkdir(parents=True, exist_ok=True)

        # task.md — nie nadpisuj
        if not task_md_path.exists():
            task_md_path.write_text(make_task_md(task), encoding="utf-8")
            stats["created"] += 1
        else:
            stats["skipped"] += 1

        # status.txt — nie nadpisuj
        if not status_path.exists():
            status_path.write_text("pending\n", encoding="utf-8")

        # .gitkeep w artefakty/ zeby git sledzil pusty katalog
        gitkeep = artefakty_dir / ".gitkeep"
        if not gitkeep.exists():
            gitkeep.touch()

    return stats


def generate_index(tasks: list[dict]) -> str:
    """Generuje INDEX.md — spis tresci sprintu."""
    lines = [
        "# Sprint Czerwiec 2026 — Index",
        "",
        f"Wygenerowano: {date.today().isoformat()}",
        "",
    ]

    current_week = None
    for task in tasks:
        sprint_raw = task["Sprint"]
        week = WEEK_MAP.get(sprint_raw, sprint_raw.split("(")[-1].rstrip(")").strip())

        if week != current_week:
            current_week = week
            lines.append(f"## {sprint_raw}")
            lines.append("")

        status = task["Status poczatkowy"]
        owner = task["Owner"]
        priority = task["Priorytet"]
        task_id = task["ID"]
        name = task["Zadanie"]
        deps = task.get("Zaleznosci (ID)", "") or ""

        dep_str = f" (zal: {deps})" if deps else ""
        lines.append(
            f"- [{task_id}]({week}/{task_id}/task.md) "
            f"[{priority}] {name} — {owner}{dep_str}"
        )

    lines.append("")
    return "\n".join(lines)


def main():
    if not CSV_PATH.exists():
        print(f"BLAD: Brak pliku CSV: {CSV_PATH}", file=sys.stderr)
        sys.exit(1)

    tasks = read_tasks(CSV_PATH)
    print(f"Wczytano {len(tasks)} zadan z {CSV_PATH.name}")

    stats = scaffold(tasks)
    print(
        f"Utworzono {stats['created']} task.md, "
        f"pominieto {stats['skipped']} (juz istnialy)"
    )
    print(f"Tygodnie: {', '.join(sorted(stats['weeks']))}")

    # INDEX.md — zawsze nadpisuj (generowany automatycznie)
    index_path = SPRINT_DIR / "INDEX.md"
    index_path.write_text(generate_index(tasks), encoding="utf-8")
    print(f"Zapisano {index_path}")


if __name__ == "__main__":
    main()

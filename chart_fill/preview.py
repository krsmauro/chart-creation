"""Printing the chart in the terminal, the way GitHub would show it."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date, timedelta

from chart_fill import dates, shading
from chart_fill.settings import GAP

COLORS = [236, 22, 28, 34, 40]  # 256-color terminal codes close to GitHub's dark theme


def describe_fit(tape: list[str]) -> str:
    period = len(tape[0])
    width = period - GAP
    if width + period <= dates.CHART_WEEKS:
        fits = "one full copy is always in view"
    else:
        fits = "it won't always be fully in view; shorten the text or lower GAP"
    return f"The text is {width} weeks wide and repeats every {period} weeks, so {fits}."


def show(counts: Counter[date], today: date) -> None:
    """Print the chart GitHub would show on `today` for these contributions per day."""
    start = dates.chart_start(today)
    busiest = max((counts[d] for d in dates.days(start, today)), default=0)
    if not busiest:
        print("Nothing to preview.")
        return

    color = sys.stdout.isatty()

    def cell(level: int) -> str:
        return f"\x1b[38;5;{COLORS[level]}m■\x1b[0m " if color else "·░▒▓█"[level] + " "

    print()
    weeks = (today - start).days // 7 + 1
    for row, name in enumerate(["", "Mon", "", "Wed", "", "Fri", ""]):
        line = []
        for week in range(weeks):
            day = start + timedelta(weeks=week, days=row)
            line.append(cell(shading.level_of(counts[day], busiest)) if day <= today else "  ")
        print(f"{name:<4}" + "".join(line))
    print(f"\n{' ' * (4 + 2 * weeks - 20)}Less {''.join(cell(level) for level in range(5))}More")

"""Printing the chart in the terminal, the way GitHub would show it."""

from __future__ import annotations

import sys
from collections import Counter
from datetime import date, timedelta

from chart_fill import dates

COLORS = [236, 22, 28, 34, 40]  # 256-color terminal codes close to GitHub's dark theme


def level_of(count: int, busiest: int) -> int:
    """Shade GitHub gives a day, 0 (empty) to 4 (brightest). It splits 0..your busiest
    day into four equal bands; worked out from your own chart, where with a busiest
    day of 13, days with 1-3 contributions got shade 1, 4-6 shade 2, 7-9 shade 3."""
    return -(-4 * count // busiest)  # ceil(4 * count / busiest)


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
            line.append(cell(level_of(counts[day], busiest)) if day <= today else "  ")
        print(f"{name:<4}" + "".join(line))
    print(f"\n{' ' * (4 + 2 * weeks - 20)}Less {''.join(cell(level) for level in range(5))}More")

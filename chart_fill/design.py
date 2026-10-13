"""Where the text goes on the timeline, and how many commits each day needs."""

from __future__ import annotations

import random
from collections import Counter
from datetime import date

from chart_fill import dates, font, shading
from chart_fill.settings import ANCHOR, GAP

STYLES = ("solid", "random")
SEED = "chart-fill"  # only used by the "random" style


def build_tape(text: str) -> list[str]:
    """One repeat of the drawing as 7 rows (Sunday..Saturday), one column per
    week: the letters on Monday..Friday, then GAP empty columns."""
    rows = [row + "." * GAP for row in font.render(text)]
    blank = "." * len(rows[0])
    return [blank, *rows, blank]


def level_for(day: date, tape: list[str], style: str) -> int:
    """Shade of this day's square, 0 (empty) to 4 (brightest)."""
    week = (day - ANCHOR).days // 7  # weeks since ANCHOR; the tape repeats both ways
    if tape[dates.row_of(day)][week % len(tape[0])] != "#":
        return 0
    # Predictable on purpose: seeded per day, so --dry-run shows exactly what a real run makes.
    return random.Random(f"{SEED}:{day}").randint(2, 4) if style == "random" else 4  # NOSONAR


def plan(tape: list[str], style: str, since: date, today: date, drawn: Counter[date]) -> dict[date, int]:
    """Commits to make per day: lit squares that don't have generated commits yet."""
    planned = {}
    for day in dates.days(since, today):
        n = shading.commits_for(level_for(day, tape, style))
        if n and not drawn[day]:
            planned[day] = n
    return planned

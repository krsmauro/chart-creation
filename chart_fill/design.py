"""Where the text goes on the chart, and how many commits each square gets."""

from __future__ import annotations

from datetime import date, timedelta

from chart_fill import ChartError, dates, font
from chart_fill.repo import PUSH_LIMIT


def plan(text: str, today: date) -> dict[date, int]:
    """Commits to make per day. The text ends in last week's column, so it stays
    on the chart as long as possible, and every lit square gets the same number
    of commits: as many as fit in one push."""
    rows = font.render(text)
    width = len(rows[0])
    last_week = dates.sunday_of(today) - timedelta(weeks=1)
    first_week = last_week - timedelta(weeks=width - 1)
    if first_week <= dates.chart_start(today):  # the chart's first column can be cut off
        raise ChartError(f"{text!r} is {width} weeks wide, but only {dates.CHART_WEEKS - 2} fit. Shorten TEXT.")
    lit = sorted(first_week + timedelta(weeks=col, days=row + 1)  # row 0 is Monday
                 for row, line in enumerate(rows) for col, pixel in enumerate(line) if pixel == "#")
    if not lit:
        raise ChartError("TEXT has nothing to draw.")
    return dict.fromkeys(lit, PUSH_LIMIT // len(lit))

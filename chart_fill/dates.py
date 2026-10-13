"""Calendar math for the chart grid: weeks are columns, weekdays are rows."""

from __future__ import annotations

from datetime import date, timedelta

CHART_WEEKS = 53  # columns on the profile chart, the last one being the current week


def row_of(day: date) -> int:
    """Row on the chart: Sunday = 0 ... Saturday = 6."""
    return (day.weekday() + 1) % 7


def chart_start(today: date) -> date:
    """First square of the profile chart: the Sunday about a year ago."""
    start = today - timedelta(weeks=52)
    return start - timedelta(days=row_of(start))


def days(first: date, last: date) -> list[date]:
    """Every day from first to last, both included."""
    return [first + timedelta(days=i) for i in range((last - first).days + 1)]

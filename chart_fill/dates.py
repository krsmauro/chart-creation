"""Calendar math for the chart grid: weeks are columns (starting on Sunday), weekdays are rows."""

from __future__ import annotations

from datetime import date, timedelta

CHART_WEEKS = 53  # columns on the profile chart, the last one being the current week


def sunday_of(day: date) -> date:
    """First day of the day's column."""
    return day - timedelta(days=(day.weekday() + 1) % 7)


def chart_start(today: date) -> date:
    """First square of the profile chart: the Sunday about a year ago."""
    return sunday_of(today) - timedelta(weeks=CHART_WEEKS - 1)


def days(first: date, last: date) -> list[date]:
    """Every day from first to last, both included."""
    return [first + timedelta(days=i) for i in range((last - first).days + 1)]

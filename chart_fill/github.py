"""Your real contributions, read from GitHub through the gh CLI."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from datetime import date

QUERY = ("query { viewer { contributionsCollection { contributionCalendar"
         " { weeks { contributionDays { date contributionCount } } } } } }")


def contributions() -> Counter[date]:
    """Contributions per day over the last year, across all your repos.
    Empty if gh isn't installed or logged in."""
    try:
        result = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"],
                                capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.TimeoutExpired):
        return Counter()
    if result.returncode != 0:
        return Counter()
    calendar = json.loads(result.stdout)["data"]["viewer"]["contributionsCollection"]["contributionCalendar"]
    return Counter({date.fromisoformat(d["date"]): d["contributionCount"]
                    for week in calendar["weeks"] for d in week["contributionDays"] if d["contributionCount"]})

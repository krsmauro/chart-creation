#!/usr/bin/env python3
"""Draw text on the GitHub contribution chart with backdated empty commits.

The text (chart_fill/settings.py) is written once in a pixel font 5 squares
tall, one week per column, ending in last week's column. The chart moves one
column left every week, so the text slowly slides off; when it does, delete
and recreate the GitHub repo and draw it again.

This file only wires the steps together; the work happens in chart_fill/.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date, timedelta

from chart_fill import ChartError, design, github, preview, repo, settings


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dry-run", action="store_true",
                        help="preview the chart, including your real GitHub activity, without committing")
    args = parser.parse_args()

    today = date.today()
    planned = design.plan(settings.TEXT, today)
    total = sum(planned.values())
    first = min(planned)
    print(f"{settings.TEXT!r}: {len(planned)} squares from {first} to {max(planned)}, "
          f"{planned[first]} commits each, {total} in all.")
    print(f"It stays whole on the chart until about {first + timedelta(days=365)}.")
    problems = repo.problems(total)

    if args.dry_run:
        for problem in problems:
            print(f"\nWarning: {problem}")
        real = github.contributions()
        if not real:
            print("\n(Couldn't read your real contributions with gh; showing the drawing only.)")
        preview.show(real + Counter(planned), today)
        return

    if problems:
        raise ChartError("\n\n".join(problems))
    print("Committing...")
    repo.commit(planned)
    repo.push()
    print(f"Pushed {total} commits. GitHub can take a few minutes to show them.")


if __name__ == "__main__":
    try:
        main()
    except ChartError as error:
        sys.exit(str(error))

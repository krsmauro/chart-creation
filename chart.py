#!/usr/bin/env python3
"""Draw text on the GitHub contribution chart with backdated empty commits.

The text (chart_fill/settings.py) is written in a pixel font 5 squares tall,
one week per column, and repeats along the whole timeline. The chart moves one
column left every week, so the text scrolls by like a very slow ticker.

Days that already have generated commits are skipped, so it is safe to run as
often as you like: run it once to draw the past year, then again (by hand or
from launchd, see install-daily.sh) to keep drawing the new days.

This file only wires the steps together; the work happens in chart_fill/.
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import date, datetime

from chart_fill import ChartError, dates, design, github, preview, repo, settings


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", type=date.fromisoformat, metavar="YYYY-MM-DD",
                        help="first day to draw (default: first square of the chart, about a year ago)")
    parser.add_argument("--dry-run", action="store_true",
                        help="preview the chart, including your real GitHub activity, without committing")
    parser.add_argument("--text", help="with --dry-run: try other text instead of TEXT")
    parser.add_argument("--style", choices=design.STYLES,
                        help="with --dry-run: try another style instead of STYLE")
    parser.add_argument("--as-of", type=date.fromisoformat, metavar="YYYY-MM-DD",
                        help="with --dry-run: preview how the chart will look on that date")
    parser.add_argument("--no-push", action="store_true", help="commit locally but don't push")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.dry_run and (args.text or args.style or args.as_of):
        raise ChartError("--text, --style and --as-of only work with --dry-run. To draw for real, edit\n"
                         "chart_fill/settings.py, so the daily job keeps drawing the same thing.")
    if settings.ANCHOR.weekday() != 6:
        raise ChartError(f"ANCHOR ({settings.ANCHOR}) in chart_fill/settings.py must be a Sunday.")

    now = datetime.now().astimezone().replace(microsecond=0)
    today = args.as_of or now.date()
    since = args.since or dates.chart_start(today)
    if since > today:
        raise ChartError("--since is in the future; this only draws days up to today.")

    tape = design.build_tape(args.text or settings.TEXT)
    drawn = repo.drawn_days()
    planned = design.plan(tape, args.style or settings.STYLE, since, today, drawn)
    print(f"[{now:%Y-%m-%d %H:%M}] {len(planned)} day(s) to draw between {since} and {today}, "
          f"{sum(planned.values())} commit(s).")

    if args.dry_run:
        show_preview(tape, drawn, planned, today)
        return
    problems = repo.problems()
    if problems:
        raise ChartError("\n\n".join(problems))
    repo.commit(planned, now)
    created = sum(planned.values())
    if created:
        print(f"Created {created} commit(s).")
    if created > 1000:
        repo.pack()
    if not args.no_push:
        repo.push()


def show_preview(tape: list[str], drawn: Counter[date], planned: dict[date, int], today: date) -> None:
    print(preview.describe_fit(tape))
    for problem in repo.problems():
        print(f"\nWarning: {problem}")
    real = github.contributions()
    if not real:
        print("\n(Couldn't read your real contributions with gh; showing generated commits only.)")
    # real already includes any generated commits that were pushed, so take the larger of the two
    shown = Counter({d: max(real[d], drawn[d]) for d in real.keys() | drawn.keys()})
    shown.update(planned)
    preview.show(shown, today)


if __name__ == "__main__":
    try:
        main()
    except ChartError as error:
        sys.exit(str(error))

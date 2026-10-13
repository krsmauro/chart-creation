"""Everything that touches git: which days are drawn, committing, pushing."""

from __future__ import annotations

import os
import subprocess
import time
from collections import Counter
from datetime import date, datetime
from pathlib import Path

from chart_fill import ChartError

REPO = Path(__file__).resolve().parents[1]
MARKER = "chart-fill:"  # every generated commit message starts with this


def git(*args: str, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], cwd=REPO, env=env, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise ChartError(f"git {args[0]} failed:\n{result.stderr.strip()}")
    return result


def drawn_days() -> Counter[date]:
    """How many generated commits each day already has."""
    if git("rev-parse", "--verify", "--quiet", "HEAD", check=False).returncode != 0:
        return Counter()  # no commits yet
    log = git("log", f"--grep=^{MARKER}", "--format=%ad", "--date=short").stdout
    return Counter(date.fromisoformat(line) for line in log.split())


def problems() -> list[str]:
    """Reasons committing now would fail or go wrong."""
    found = []
    if not git("config", "user.email", check=False).stdout.strip():
        found.append(
            "No git email configured. GitHub only counts commits whose email is linked to your account:\n"
            '  git config --global user.name "Your Name"\n'
            '  git config --global user.email "an-email-on-your-github-account@example.com"'
        )
    if git("symbolic-ref", "--quiet", "HEAD", check=False).returncode != 0:
        found.append("HEAD is not on a branch (detached, or mid-rebase). Check out your default branch first.")
    if git("diff", "--cached", "--quiet", check=False).returncode != 0:
        found.append("There are staged changes. Commit or unstage them first, or they'd end up inside a generated commit.")
    return found


def commit_time(day: date, now: datetime) -> datetime:
    """Noon local time, or now if noon hasn't happened yet (today, morning).

    GitHub places a commit by its author date in the commit's own time zone,
    so noon keeps it well inside the right day."""
    noon = datetime(day.year, day.month, day.day, 12).astimezone()
    return min(noon, now)


def commit(planned: dict[date, int], now: datetime) -> None:
    """Make the planned empty commits, oldest day first."""
    for day, n in planned.items():
        if day.day == 1:
            print(f"  {day:%Y-%m}...", flush=True)
        stamp = commit_time(day, now).isoformat()
        env = {**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
        for i in range(1, n + 1):
            # --no-verify / --no-gpg-sign: skip hooks and signing, which would run thousands of times
            git("commit", "--allow-empty", "--no-verify", "--no-gpg-sign", "--quiet",
                "-m", f"{MARKER} {day} ({i}/{n})", env=env)


def pack() -> None:
    """Bundle the loose commit files in .git into one pack file. Git does this by
    itself only past ~6,700 loose objects; a year of drawing is about 3,600."""
    git("gc", "--quiet")


def push() -> None:
    """Push to origin, retrying while the network comes up."""
    if git("remote", "get-url", "origin", check=False).returncode != 0:
        print("No 'origin' remote, skipping push.")
        return
    for attempt in range(3):
        result = git("push", "--quiet", "origin", "HEAD", check=False)
        if result.returncode == 0:
            print("Pushed to origin.")
            return
        if attempt < 2:
            time.sleep(30)  # right after login the network is often not up yet
    raise ChartError(f"Push failed; the commits stay local and the next run retries.\n{result.stderr.strip()}")

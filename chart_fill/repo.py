"""Everything that touches git: checks, committing, pushing."""

from __future__ import annotations

import os
import subprocess
from datetime import date, datetime
from pathlib import Path

from chart_fill import ChartError

REPO = Path(__file__).resolve().parents[1]
MARKER = "chart-fill:"  # every generated commit message starts with this
# GitHub only credits the newest 1,000 commits of a push (undocumented, seen on this
# repo: a 2,752-commit push showed up as exactly 1,000), so the drawing stays within it.
PUSH_LIMIT = 1000

REDRAW = """\
The text is already drawn ({} generated commits in this repo's history).
To draw it again where the chart is now:
  1. Delete the repo on GitHub and create it again, empty.
  2. Start a fresh local history (your files stay, the old drawing goes):
       git checkout --orphan fresh
       git commit -m 'Start over'
       git branch -M main
       git push -u origin main
  3. Run ./chart.py again."""


def git(*args: str, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(["git", *args], cwd=REPO, env=env, capture_output=True, text=True)
    if check and result.returncode != 0:
        raise ChartError(f"git {args[0]} failed:\n{result.stderr.strip()}")
    return result


def count(*args: str) -> int:
    """Number of commits git rev-list finds, 0 if there are no commits yet."""
    if git("rev-parse", "--verify", "--quiet", "HEAD", check=False).returncode != 0:
        return 0
    return int(git("rev-list", "--count", *args).stdout)


def problems(new_commits: int) -> list[str]:
    """Reasons drawing now would fail or go wrong."""
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
    if git("remote", "get-url", "origin", check=False).returncode != 0:
        found.append("No 'origin' remote. Create the repo on GitHub, then: git remote add origin <its URL>")
    drawn = count(f"--grep=^{MARKER}", "HEAD")
    unpushed = count("HEAD", "--not", "--remotes=origin")
    if drawn:
        found.append(REDRAW.format(drawn))
    elif unpushed + new_commits > PUSH_LIMIT:
        found.append(f"{unpushed} commit(s) aren't pushed yet, and with the drawing that's over the "
                     f"{PUSH_LIMIT} GitHub counts per push. Run git push first.")
    return found


def commit(planned: dict[date, int]) -> None:
    """Make the planned empty commits, oldest day first, at noon local time.
    GitHub places a commit by its author date in its own time zone, so noon
    keeps it well inside the right day."""
    for day, n in planned.items():
        stamp = datetime(day.year, day.month, day.day, 12).astimezone().isoformat()
        env = {**os.environ, "GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp}
        for i in range(1, n + 1):
            # --no-verify / --no-gpg-sign: skip hooks and signing, which would run hundreds of times
            git("commit", "--allow-empty", "--no-verify", "--no-gpg-sign", "--quiet",
                "-m", f"{MARKER} {day} ({i}/{n})", env=env)


def push() -> None:
    """Push everything in one go."""
    result = git("push", "--quiet", "origin", "HEAD", check=False)
    if result.returncode != 0:
        raise ChartError("Push failed, so the commits are only local. Fix the problem below, "
                         f"then run: git push\n{result.stderr.strip()}")

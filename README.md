# chart-creation

An experiment: write text on my GitHub contribution chart with backdated,
empty commits.

The text is drawn in a pixel font 5 squares tall, one week per column, and
repeats along the timeline. The chart moves one column left every week, so the
text scrolls by like a very slow ticker. "MAURO" is 25 weeks wide and repeats
every 28, so one full copy is always on screen.

## Usage

```sh
./chart.py --dry-run                      # preview with my real activity, commit nothing
./chart.py --dry-run --text "HI" --style random   # try other designs
./chart.py --dry-run --as-of 2027-03-01   # see where the ticker will be then
./chart.py --since 2026-10-06 --no-push   # small local test, check `git log`
./chart.py                                # draw the last year and push
```

The real design lives in `chart_fill/settings.py` (`TEXT`, `STYLE`, `GAP`,
`ANCHOR`, `PEAK`); the daily job uses those. Days that already have generated
commits are skipped, so running it again only draws new days.

`chart.py` only wires the steps together; each module in `chart_fill/` does
one job (font, dates, shading, design, git, GitHub, preview), listed in
`chart_fill/__init__.py`.

**Pick the design before the first real run.** Squares already drawn stay
drawn, so changing it later garbles the picture until the GitHub repo is
deleted and recreated.

## Keep it drawing

Either run `./chart.py` now and then, or install a macOS LaunchAgent that runs
it at login and daily at noon:

```sh
./install-daily.sh               # runs once immediately, then at login + noon
./install-daily.sh --uninstall
tail -f ~/Library/Logs/chart-fill.log
```

## How GitHub counts these

- The commit email must be one linked to the GitHub account.
- Commits must be on the default branch of a non-fork repo; private repos only
  show if private contributions are enabled on the profile.
- The day is the commit's author date in its own time zone; commits are stamped
  at noon local time.
- Shades are relative: 0 to your busiest day is split into four equal bands.
  Lit squares get `PEAK` commits so real activity mostly shows up dimmer.

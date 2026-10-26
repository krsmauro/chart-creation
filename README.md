# chart-creation

An experiment: write text on my GitHub contribution chart with backdated,
empty commits.

The text is drawn once in a pixel font 5 squares tall, one week per column,
ending in last week's column. The chart moves one column left every week, so
the text slowly slides off the left edge; when it does, I redraw it.

## Usage

Set the text in `chart_fill/settings.py`, then:

```sh
./chart.py --dry-run   # preview with my real activity, commit nothing
./chart.py             # make the commits and push them
```

The output says until when the text stays whole on the chart.

## Redraw

Running it again refuses while the old drawing is in the history. To redraw:

1. Delete the repo on GitHub and create it again, empty.
2. Start a fresh local history (the files stay, the old drawing goes):
   ```sh
   git checkout --orphan fresh
   git commit -m 'Start over'
   git branch -M main
   git push -u origin main
   ```
3. Run `./chart.py`.

## How GitHub counts these

- Only the newest 1,000 commits of a push count. This isn't documented, but
  a 2,752-commit push here showed up as exactly 1,000. So every lit square
  gets the same number of commits, as many as fit in 1,000, and it all goes up
  in one push. Fewer lit squares (shorter text) means more commits each.
- Shades are relative: 0 to the busiest day is split into four equal bands.
  Real activity on busy days can show up as bright as the text.
- The commit email must be one linked to the GitHub account.
- Commits must be on the default branch of a non-fork repo; private repos only
  show if private contributions are enabled on the profile.
- The day is the commit's author date in its own time zone; commits are stamped
  at noon local time.

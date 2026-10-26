"""Draw text on the GitHub contribution chart. chart.py is the entry point.

    settings  what to draw (the part you edit)
    font      text -> rows of pixels
    dates     calendar math for the chart grid
    design    which day gets how many commits
    repo      everything that touches git
    github    your real contributions, through the gh CLI
    preview   printing the chart in the terminal
"""


class ChartError(Exception):
    """A problem to show the user (bad settings, git refusing), not a bug."""

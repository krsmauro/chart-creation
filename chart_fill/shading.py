"""How GitHub picks a square's shade.

It splits 0..your busiest day into four equal bands, one per shade. Worked out
from your own chart: with a busiest day of 13, days with 1-3 contributions got
shade 1, 4-6 shade 2, 7-9 shade 3 and 11-13 shade 4.
"""

from chart_fill.settings import PEAK


def commits_for(level: int) -> int:
    """Commits that give a square this shade (0 = empty .. 4 = brightest).
    Aims for the middle of each band so small changes in your max don't flip it."""
    if level in (0, 4):
        return PEAK * level // 4
    return round(PEAK * (2 * level - 1) / 8)


def level_of(count: int, busiest: int) -> int:
    """Shade GitHub gives a day with `count` contributions."""
    return -(-4 * count // busiest)  # ceil(4 * count / busiest)

"""What to draw. Edit these, then preview with ./chart.py --dry-run.

Settle them before the first real run. Squares already drawn stay, so changing
TEXT, STYLE, GAP or ANCHOR afterwards garbles the picture until you delete the
GitHub repo and start over.
"""

from datetime import date

TEXT = "MAURO ᗧ • •"
STYLE = "solid"  # "solid", or "random" for letters in random shades of green
GAP = 3  # empty columns before the text repeats
ANCHOR = date(2025, 10, 12)  # a Sunday: the first copy of the text starts in this week's column
PEAK = 32  # commits on the brightest squares; keep it well above your real busiest day

"""Lay every color out along a single Archimedean spiral.

Colors are ordered by hue first and lightness second, so traversing the spiral
from the center outward walks through the whole hue wheel, and within each hue
the ranked (dark to light) members wind outward in sequence. Near-neutral greys
have no hue, so they trail at the very end of the spiral.

Because every color occupies one equal step along the spiral, families with more
names simply take up a longer arc -- which is exactly the "our words clump"
story, expressed as spiral geometry.
"""

import math


def compute_spiral(records, cx=380.0, cy=380.0, r0=46.0, rmax=332.0, turns=6.5):
    """Return a new list of records with ``x`` and ``y`` spiral coordinates.

    The input *records* are dictionaries from ``color_features.build_records``.
    Ordering is (hue, lightness) for chromatic colors, then lightness for greys.
    """
    chromatic = sorted(
        (r for r in records if r["family"] != "grey"),
        key=lambda r: (r["hue"], r["lightness"]),
    )
    neutral = sorted(
        (r for r in records if r["family"] == "grey"),
        key=lambda r: r["lightness"],
    )
    ordered = chromatic + neutral

    n = len(ordered)
    placed = []
    for i, rec in enumerate(ordered):
        frac = i / (n - 1)
        theta = frac * turns * 2 * math.pi
        radius = r0 + (rmax - r0) * frac
        point = dict(rec)
        point["x"] = round(cx + radius * math.cos(theta), 1)
        point["y"] = round(cy + radius * math.sin(theta), 1)
        placed.append(point)
    return placed

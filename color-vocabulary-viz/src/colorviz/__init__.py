"""colorviz - turn the xkcd Color Survey into two visualizations.

A tiny, dependency-free visualization library. After ``pip install`` you can::

    import colorviz

    colorviz.family_counts()               # {'red': 93, 'orange': 150, ...}
    colorviz.drip_chart("drips.html")      # write the static paint chart
    colorviz.spiral_chart("spiral.html")   # write the interactive spiral

Both chart functions return the path they wrote, so you can open it in a browser.

Internals are split into small, single-purpose modules:

    parse           read the bundled ``name (#hex)`` list into pairs
    color_features  turn each hex into hue / lightness / saturation + a family
    spiral          lay every color out along an Archimedean spiral
    build           render the CSVs and both HTML charts
"""

from pathlib import Path

from .parse import parse_colors, parse_default, default_data_path
from .color_features import build_records, assign_family, hex_to_hls, FAMILIES
from .spiral import compute_spiral

__all__ = [
    "load_colors",
    "family_counts",
    "drip_chart",
    "spiral_chart",
    "parse_colors",
    "parse_default",
    "default_data_path",
    "build_records",
    "assign_family",
    "hex_to_hls",
    "compute_spiral",
    "FAMILIES",
]

__version__ = "0.1.0"


def load_colors():
    """Return the 954 colors as feature dictionaries (name, hex, hue, ... family)."""
    return build_records(parse_default())


def family_counts():
    """Return a ``{family: count}`` dict over the 954 named colors."""
    from collections import Counter

    counts = Counter(r["family"] for r in load_colors())
    return {fam: counts.get(fam, 0) for fam in FAMILIES + ["grey"]}


def drip_chart(path="color-vocabulary-drips.html"):
    """Write the static dripping-paint chart to *path*; return the path."""
    from .build import render_drip_html

    Path(path).write_text(render_drip_html(load_colors()), encoding="utf-8")
    return path


def spiral_chart(path="color-vocabulary-spiral.html"):
    """Write the interactive hue spiral to *path*; return the path."""
    from .build import render_spiral_html

    Path(path).write_text(render_spiral_html(load_colors()), encoding="utf-8")
    return path

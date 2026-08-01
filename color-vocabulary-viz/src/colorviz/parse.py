"""Read the raw xkcd color list into tidy (name, hex) pairs.

The raw file is the published list of the 954 most common color names from the
xkcd Color Survey. Each entry looks like ``forest green  (#06470c)``; several may
share a line separated by pipes. We don't care about the layout, only the
``name (#hex)`` pattern, so a single regular expression pulls every pair out.

A copy of the data is bundled *inside* the installed package
(``colorviz/xkcd_rgb.txt``), so the library works after ``pip install`` without
needing the repository checkout. ``parse_default()`` reads that bundled copy;
``parse_colors(path)`` reads any file you point it at.
"""

import re
from importlib.resources import files

# name  -> lowercase letters, spaces, slashes and apostrophes (e.g. "robin's egg blue")
# hex   -> exactly six hex digits inside "(#......)"
COLOR_RE = re.compile(r"([a-z][a-z /'\u2019]*?)\s*\(#([0-9a-fA-F]{6})\)")

DATA_FILENAME = "xkcd_rgb.txt"


def _parse_text(text):
    """Return ``(name, hex)`` tuples parsed from raw *text*."""
    return [(name.strip(), hx.lower()) for name, hx in COLOR_RE.findall(text)]


def parse_colors(path):
    """Parse ``(name, hex)`` pairs from the file at *path*."""
    with open(path, encoding="utf-8") as fh:
        return _parse_text(fh.read())


def default_data_path():
    """Filesystem path to the color list bundled inside the package."""
    return str(files("colorviz").joinpath(DATA_FILENAME))


def parse_default():
    """Parse the color list bundled inside the installed package."""
    text = files("colorviz").joinpath(DATA_FILENAME).read_text(encoding="utf-8")
    return _parse_text(text)


if __name__ == "__main__":
    pairs = parse_default()
    print(f"parsed {len(pairs)} colors; first: {pairs[0]}")

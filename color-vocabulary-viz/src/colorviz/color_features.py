"""Turn a hex color into perceptual features and a hue family.

Everything here is built on the standard-library ``colorsys`` module, which
converts RGB into HLS (hue, lightness, saturation). Hue is what lets us group
colors into families; lightness lets us rank colors within a family; saturation
lets us peel off the near-neutral greys, blacks and whites that have no
meaningful hue.
"""

import colorsys

# The twelve chromatic families, one per 30-degree slice of the hue wheel,
# in order starting at red. Near-neutral colors fall into a thirteenth
# "grey" bucket handled separately.
FAMILIES = [
    "red", "orange", "yellow", "chartreuse", "green", "teal",
    "cyan", "azure", "blue", "violet", "magenta", "rose",
]


def hex_to_hls(hx):
    """Convert a 6-digit hex string (no ``#``) to (hue0-360, lightness, saturation)."""
    r = int(hx[0:2], 16) / 255
    g = int(hx[2:4], 16) / 255
    b = int(hx[4:6], 16) / 255
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return h * 360, l, s


def assign_family(h, l, s):
    """Return the family name for a color given its hue/lightness/saturation.

    Low-saturation or near-black / near-white colors are treated as ``grey``
    because their hue is not perceptually meaningful. Everything else is binned
    into one of the twelve 30-degree hue families.
    """
    if s < 0.12 or l < 0.06 or l > 0.96:
        return "grey"
    return FAMILIES[int(h // 30) % 12]


def build_records(pairs):
    """Turn ``(name, hex)`` pairs into a list of feature dictionaries."""
    records = []
    for name, hx in pairs:
        h, l, s = hex_to_hls(hx)
        records.append({
            "name": name,
            "hex": "#" + hx,
            "hue": round(h, 2),
            "lightness": round(l, 3),
            "saturation": round(s, 3),
            "family": assign_family(h, l, s),
        })
    return records

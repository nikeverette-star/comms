# color-vocabulary-viz

A tiny, dependency-free Python **visualization library** built from the
**xkcd Color Survey** (954 crowd-sourced color names). It produces two
visualizations that show how human color vocabulary clumps around a few
favorite hues instead of spreading evenly across the spectrum.

Import name: `colorviz`  ·  Distribution name: `color-vocabulary-viz-nikeverette`

## Install

From TestPyPI (used for the class demo):

```bash
pip install -i https://test.pypi.org/simple/ color-vocabulary-viz-nikeverette
```

...or once it's on the real PyPI:

```bash
pip install color-vocabulary-viz-nikeverette
```

...or straight from a local checkout (editable, for development):

```bash
pip install -e .
```

## Use

```python
import colorviz

colorviz.family_counts()
# {'red': 93, 'orange': 150, 'yellow': 112, ... 'grey': 24}

colorviz.drip_chart("drips.html")     # writes the static paint chart
colorviz.spiral_chart("spiral.html")  # writes the interactive spiral
```

Each chart function returns the path it wrote; open that HTML file in a browser.
There's also a console command that writes both at once:

```bash
colorviz-build
```

The library has **no runtime dependencies** — only the Python standard library —
and the color data is bundled inside the package, so it works immediately after
`pip install`.

## The one-paragraph summary

The dataset is the **xkcd Color Survey**, run by Randall Munroe in 2010, in which
roughly 200,000 participants were shown random color swatches and asked to name
them, producing over five million responses distilled into 954 commonly-named
colors, each paired with a representative sRGB value. Its goal was to map how
everyday people — not designers or specialists — actually perceive and name
color. The goal of these visualizations is to reveal a counterintuitive finding
hiding in that data: although we feel like we name a smooth, continuous rainbow,
our color words actually clump hard around a few favorite hues (oranges, yellows,
greens, and roses) while blues and violets get comparatively few distinct names.
The dripping-paint chart makes that imbalance land instantly through the length
of each color's run, and the spiral lets a viewer explore the same clumping hue
by hue.

## The two visualizations

- **`outputs/color-vocabulary-drips.html`** — the static hero. Each hue family
  hangs from a rail as a column of its real surveyed colors; column length = how
  many names fall in that family, with a dashed trend line through the true
  counts. Loads with a pour animation; hover a color to isolate it.
- **`outputs/color-vocabulary-spiral.html`** — the interactive companion. All 954
  names spiral outward by hue; hover any dot for its name and hex, or click a
  family chip to filter.

## Project structure

```
color-vocabulary-viz/
├── README.md
├── LICENSE                       # MIT (code only; data is CC BY-NC — see below)
├── pyproject.toml                # package metadata; makes it pip-installable
├── requirements.txt              # runtime: none; dev/publish: build, twine
├── .gitignore
├── index.html                    # landing page linking both visualizations
├── VIDEO_SCRIPT.md               # 2-minute demo script + publishing steps
├── data/
│   ├── raw/xkcd_rgb.txt           # the 954 name -> hex list (provenance copy)
│   └── processed/
│       ├── color_families.csv     # name, hex, hue, lightness, saturation, family
│       └── family_counts.csv      # family, count
├── src/
│   └── colorviz/
│       ├── __init__.py            # public API: family_counts, drip_chart, ...
│       ├── xkcd_rgb.txt           # bundled data (ships inside the wheel)
│       ├── parse.py               # raw text -> (name, hex) pairs
│       ├── color_features.py      # hex -> hue / lightness / saturation + family
│       ├── spiral.py              # spiral coordinates for every color
│       └── build.py               # render the CSVs and both HTML files
├── outputs/
│   ├── color-vocabulary-drips.html
│   └── color-vocabulary-spiral.html
└── docs/
    └── data-viz-checklist.md      # how the pieces meet the grading rubric
```

## Reproduce the data + charts

```bash
cd src && python -m colorviz.build
```

This reparses `data/raw/xkcd_rgb.txt`, rewrites both CSVs in `data/processed/`,
and regenerates both HTML files in `outputs/`.

## Build & publish (summary — full steps in VIDEO_SCRIPT.md)

```bash
python -m pip install build twine
python -m build                     # creates dist/*.whl and dist/*.tar.gz
python -m twine check dist/*
python -m twine upload --repository testpypi dist/*   # TestPyPI first
python -m twine upload dist/*                          # real PyPI (optional)
```

> PyPI names must be globally unique. If `color-vocabulary-viz-nikeverette` is
> taken, change `name` in `pyproject.toml` and rebuild.

## Data source and license

- **Data:** xkcd Color Survey by Randall Munroe — <https://xkcd.com/color/> —
  released under **Creative Commons Attribution-NonCommercial (CC BY-NC)**.
  Included with attribution for a non-commercial academic project.
- **Code:** MIT License (see `LICENSE`), which covers the code only, not the data.

> Update the name/year in `LICENSE` and the author in `pyproject.toml` if needed.

"""Small matplotlib visualization library with modern aesthetics for pandas data."""
import colorsys
import warnings

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# Validated categorical palette (fixed order = CVD-safe; do not reorder/cycle).
CATEGORICAL = {
    "light": ["#2a78d6", "#eb6834", "#1baf7a", "#eda100",
              "#e87ba4", "#008300", "#4a3aa7", "#e34948"],
    "dark":  ["#3987e5", "#d95926", "#199e70", "#c98500",
              "#d55181", "#008300", "#9085e9", "#e66767"],
}
SEQUENTIAL = {"light": ["#cde2fb", "#3987e5", "#0d366b"],
              "dark":  ["#184f95", "#5598e7", "#cde2fb"]}
DIVERGING = {"light": ["#e34948", "#f0efec", "#2a78d6"],
             "dark":  ["#e66767", "#383835", "#3987e5"]}
CHROME = {
    "light": dict(surface="#fcfcfb", ink="#0b0b0b", ink2="#52514e",
                   muted="#898781", grid="#e1e0d9", axis="#c3c2b7"),
    "dark":  dict(surface="#1a1a19", ink="#ffffff", ink2="#c3c2b7",
                   muted="#898781", grid="#2c2c2a", axis="#383835"),
    "pastel": dict(surface="#ffffff", ink="#2b2b2b", ink2="#6b6a67",
                   muted="#a5a4a0", grid="#ededeb", axis="#dcdbd6"),
}
OTHER_COLOR = "#b3b1a8"
MAX_SERIES = 8        # categorical slots before folding to "Other"
MAX_SCATTER_HUE = 3   # all-pairs CVD-safe limit for scatter (see palette.md)


def _mode(dark):
    return "dark" if dark else "light"


def pastel_wheel(n, lightness=0.82, saturation=0.55):
    """n evenly-spaced pastel hues around the color wheel, as hex."""
    return ["#%02x%02x%02x" % tuple(round(255 * v) for v in
            colorsys.hls_to_rgb(i / max(n, 1), lightness, saturation)) for i in range(n)]


def palette(n, dark=False):
    """First n categorical colors in fixed order; extras fall back to a neutral gray."""
    colors = CATEGORICAL[_mode(dark)]
    if n <= len(colors):
        return colors[:n]
    return colors + [OTHER_COLOR] * (n - len(colors))


def _series(df, cols, dark):
    """Yield (label, values, color) per series, folding any overflow past
    MAX_SERIES into a single gray 'Other' (row-wise sum) so no two series
    ever share a color."""
    cols = list(cols)
    if len(cols) <= MAX_SERIES:
        for color, col in zip(palette(len(cols), dark), cols):
            yield col, df[col], color
        return
    warnings.warn(
        f"{len(cols)} series exceeds {MAX_SERIES}; folding the last "
        f"{len(cols) - MAX_SERIES + 1} into 'Other'", stacklevel=3)
    keep = cols[:MAX_SERIES - 1]
    for color, col in zip(CATEGORICAL[_mode(dark)], keep):
        yield col, df[col], color
    yield "Other", df[cols[MAX_SERIES - 1:]].sum(axis=1), OTHER_COLOR


def apply_theme(dark=False):
    """Set base rcParams (typography, surface, tick/text ink — the last covers colorbars)."""
    c = CHROME[_mode(dark)]
    plt.rcParams.update({
        "figure.facecolor": c["surface"],
        "axes.facecolor": c["surface"],
        "savefig.facecolor": c["surface"],
        "font.family": "sans-serif",
        "font.size": 11,
        "text.color": c["ink"],
        "xtick.color": c["muted"],
        "ytick.color": c["muted"],
        "legend.fontsize": 10,
    })


def _finish(ax, theme, title=None, legend=False, grid="y"):
    c = CHROME[theme if isinstance(theme, str) else _mode(theme)]
    ax.set_facecolor(c["surface"])
    ax.figure.set_facecolor(c["surface"])
    for side in ("bottom", "left"):
        ax.spines[side].set_color(c["axis"])
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if grid:
        ax.grid(True, axis=grid, color=c["grid"], linewidth=0.8)
    else:
        ax.grid(False)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, colors=c["muted"], labelcolor=c["muted"])
    ax.xaxis.label.set_color(c["ink2"])
    ax.yaxis.label.set_color(c["ink2"])
    if title:
        ax.set_title(title, pad=12, loc="left", fontweight="bold", color=c["ink"])
    if legend and len(ax.get_legend_handles_labels()[0]) > 1:
        leg = ax.legend(loc="upper left", bbox_to_anchor=(1.0, 1.0), frameon=False)
        for text in leg.get_texts():
            text.set_color(c["ink2"])
    return ax


def line(df, x=None, y=None, ax=None, dark=False, title=None):
    """Line chart: one line per column in y (default: all numeric columns)."""
    apply_theme(dark)
    ax = ax or plt.gca()
    xs = df[x] if x else df.index
    cols = y if y else [c for c in df.select_dtypes("number").columns if c != x]
    for label, vals, color in _series(df, cols, dark):
        ax.plot(xs, vals, color=color, linewidth=2, solid_capstyle="round", label=label)
    return _finish(ax, dark, title, legend=True)


def bar(df, x, y, ax=None, dark=False, title=None, horizontal=False):
    """Bar chart: one bar per row of x, one series per column in y."""
    apply_theme(dark)
    ax = ax or plt.gca()
    cols = y if isinstance(y, (list, tuple)) else [y]
    series = list(_series(df, cols, dark))
    n = len(series)
    width = 0.8 / n
    positions = range(len(df))
    for i, (label, vals, color) in enumerate(series):
        offset = (i - (n - 1) / 2) * width
        pos = [p + offset for p in positions]
        if horizontal:
            ax.barh(pos, vals, height=width * 0.92, color=color, label=label)
        else:
            ax.bar(pos, vals, width=width * 0.92, color=color, label=label)
    axis = ax.set_yticks if horizontal else ax.set_xticks
    axis(list(positions))
    labels = ax.set_yticklabels if horizontal else ax.set_xticklabels
    labels(df[x])
    return _finish(ax, dark, title, legend=True, grid="x" if horizontal else "y")


def scatter(df, x, y, hue=None, ax=None, dark=False, title=None):
    """Scatter plot, optionally colored by a categorical column `hue`."""
    apply_theme(dark)
    ax = ax or plt.gca()
    if hue:
        groups = list(df[hue].unique())
        if len(groups) > MAX_SCATTER_HUE:
            raise ValueError(
                f"scatter hue supports at most {MAX_SCATTER_HUE} categories "
                f"(got {len(groups)}); beyond that the palette is not colorblind-safe "
                "for scatter — facet into small multiples or add a marker-shape encoding")
        for color, g in zip(palette(len(groups), dark), groups):
            sub = df[df[hue] == g]
            ax.scatter(sub[x], sub[y], color=color, s=36, alpha=0.9,
                       edgecolors=CHROME[_mode(dark)]["surface"], linewidths=0.5, label=g)
    else:
        ax.scatter(df[x], df[y], color=palette(1, dark)[0], s=36, alpha=0.9,
                   edgecolors=CHROME[_mode(dark)]["surface"], linewidths=0.5)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    return _finish(ax, dark, title, legend=bool(hue))


def heatmap(df, ax=None, dark=False, title=None, diverging=False):
    """Heatmap of a numeric DataFrame; sequential by default, diverging if signed."""
    apply_theme(dark)
    ax = ax or plt.gca()
    ramp = DIVERGING[_mode(dark)] if diverging else SEQUENTIAL[_mode(dark)]
    cmap = LinearSegmentedColormap.from_list("ramp", ramp)
    vmax = df.abs().to_numpy().max() if diverging else None
    vmin = -vmax if diverging else None
    im = ax.imshow(df.to_numpy(), cmap=cmap, aspect="auto", vmin=vmin, vmax=vmax)
    ax.set_xticks(range(len(df.columns)))
    ax.set_xticklabels(df.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(df.index)))
    ax.set_yticklabels(df.index)
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    return _finish(ax, dark, title, grid=None)


def histogram(df, columns=None, bins=20, ax=None, title=None, alpha=0.8):
    """Overlaid histogram of numeric columns: pastel color wheel on a white ground."""
    apply_theme(False)
    ax = ax or plt.gca()
    cols = list(columns) if columns is not None else list(df.select_dtypes("number").columns)
    for color, col in zip(pastel_wheel(len(cols)), cols):
        ax.hist(df[col].dropna(), bins=bins, color=color, alpha=alpha,
                edgecolor="#9b9a97", linewidth=0.8, label=col)
    ax.set_ylabel("count")
    return _finish(ax, "pastel", title, legend=len(cols) > 1)


def save(fig, path, dark=False, dpi=200):
    """Save a figure with the theme background baked in; `dark` may be a theme key."""
    theme = dark if isinstance(dark, str) else _mode(dark)
    fig.savefig(path, dpi=dpi, facecolor=CHROME[theme]["surface"], bbox_inches="tight")

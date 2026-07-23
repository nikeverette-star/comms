"""Six vizlib examples, all built from pandas DataFrames under the same criteria:
modern minimal styling, a colorblind-safe palette, and light/dark parity."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import vizlib as vz

rng = np.random.default_rng(0)


def make_examples(fig, dark):
    axes = fig.subplots(3, 2).ravel()

    # 1. Multi-series line — a monthly time series.
    ts = pd.DataFrame({
        "month": pd.date_range("2026-01-01", periods=12, freq="MS"),
        "revenue": rng.normal(100, 8, 12).cumsum(),
        "cost": rng.normal(60, 5, 12).cumsum(),
        "profit": rng.normal(40, 6, 12).cumsum(),
    })
    vz.line(ts, x="month", y=["revenue", "cost", "profit"], ax=axes[0],
            dark=dark, title="Monthly performance")

    # 2. Grouped bar — one group of bars per category.
    sales = pd.DataFrame({
        "region": ["North", "South", "East", "West", "Central"],
        "q1": rng.integers(50, 150, 5),
        "q2": rng.integers(50, 150, 5),
    })
    vz.bar(sales, x="region", y=["q1", "q2"], ax=axes[1],
           dark=dark, title="Sales by region")

    # 3. Horizontal bar — a ranking, largest at top.
    ranking = pd.DataFrame({
        "product": ["Alpha", "Beta", "Gamma", "Delta", "Epsilon"],
        "units": rng.integers(200, 900, 5),
    }).sort_values("units")
    vz.bar(ranking, x="product", y="units", ax=axes[2],
           dark=dark, title="Units sold", horizontal=True)

    # 4. Scatter with hue — up to three colorblind-safe groups.
    points = pd.DataFrame({
        "x": rng.normal(0, 1, 90),
        "y": rng.normal(0, 1, 90),
        "cohort": rng.choice(["A", "B", "C"], 90),
    })
    vz.scatter(points, x="x", y="y", hue="cohort", ax=axes[3],
               dark=dark, title="Cohorts")

    # 5. Sequential heatmap — magnitude on a single-hue ramp.
    activity = pd.DataFrame(
        rng.integers(0, 100, (5, 7)),
        index=["Team " + s for s in "ABCDE"],
        columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    vz.heatmap(activity, ax=axes[4], dark=dark, title="Weekly activity")

    # 6. Diverging heatmap — a correlation matrix, gray at zero.
    corr = pd.DataFrame(rng.normal(0, 1, (30, 5)), columns=list("VWXYZ")).corr()
    vz.heatmap(corr, ax=axes[5], dark=dark, title="Correlation", diverging=True)


for dark in (False, True):
    fig = plt.figure(figsize=(13, 14))
    make_examples(fig, dark)
    fig.tight_layout(pad=2.5)
    path = "demo_dark.png" if dark else "demo_light.png"
    vz.save(fig, path, dark=dark)
    print("Saved", path)

# 7. Histogram — its own aesthetic: a pastel color wheel on a lighter (white)
# background, distinct from the CVD-safe theme the six charts above share.
scores = pd.DataFrame({
    "control":   rng.normal(50, 10, 600),
    "variant A": rng.normal(58, 12, 600),
    "variant B": rng.normal(46, 8, 600),
})
fig = plt.figure(figsize=(8, 4.5))
vz.histogram(scores, ax=fig.subplots(), title="Score distribution")
fig.tight_layout()
vz.save(fig, "demo_histogram.png", dark="pastel")
print("Saved demo_histogram.png")

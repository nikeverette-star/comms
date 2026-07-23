"""Demo of vizlib against pandas DataFrames."""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import vizlib as vz

rng = np.random.default_rng(0)

# Line chart: time series with multiple columns.
ts = pd.DataFrame({
    "month": pd.date_range("2026-01-01", periods=12, freq="MS"),
    "revenue": rng.normal(100, 8, 12).cumsum(),
    "cost": rng.normal(60, 5, 12).cumsum(),
})

# Bar chart: categories x one series.
sales = pd.DataFrame({
    "region": ["North", "South", "East", "West", "Central"],
    "q1": rng.integers(50, 150, 5),
    "q2": rng.integers(50, 150, 5),
})

# Scatter: two numeric columns colored by a category.
points = pd.DataFrame({
    "x": rng.normal(0, 1, 90),
    "y": rng.normal(0, 1, 90),
    "group": rng.choice(["A", "B", "C"], 90),
})

# Heatmap: correlation matrix.
corr = pd.DataFrame(rng.normal(0, 1, (6, 4)),
                     columns=list("WXYZ")).corr().iloc[:4]

fig, axes = plt.subplots(2, 2, figsize=(11, 8))

vz.line(ts, x="month", y=["revenue", "cost"], ax=axes[0, 0], title="Revenue vs Cost")
vz.bar(sales, x="region", y=["q1", "q2"], ax=axes[0, 1], title="Sales by Region")
vz.scatter(points, x="x", y="y", hue="group", ax=axes[1, 0], title="Clusters")
vz.heatmap(corr, ax=axes[1, 1], title="Correlation", diverging=True)

fig.tight_layout()
vz.save(fig, "demo_light.png")

fig2, ax2 = plt.subplots(figsize=(7, 4))
vz.line(ts, x="month", y=["revenue", "cost"], ax=ax2, dark=True, title="Revenue vs Cost (dark)")
fig2.tight_layout()
vz.save(fig2, "demo_dark.png", dark=True)

print("Saved demo_light.png and demo_dark.png")

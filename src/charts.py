import matplotlib.pyplot as plt
import pandas as pd


def _empty_chart(message):
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.text(0.5, 0.5, message, ha="center", va="center", transform=ax.transAxes)
    ax.set_axis_off()
    fig.tight_layout()
    return fig


def production_trend(df):
    if df.empty or df["production"].dropna().empty:
        return _empty_chart("No production values available")
    grouped = df.groupby("year", as_index=False)["production"].sum(min_count=1).sort_values("year")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(grouped["year"], grouped["production"], marker="o")
    ax.set_title("Total recorded production by year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Production (source units)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def yield_trend(df):
    if df.empty or "yield" not in df or df["yield"].dropna().empty:
        return _empty_chart("Yield unavailable: check positive area and compatible units")
    grouped = df.groupby("year", as_index=False)["yield"].mean().sort_values("year")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(grouped["year"], grouped["yield"], marker="o")
    ax.set_title("Mean record-level yield by year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Production / area (source units)")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    return fig


def region_comparison(df):
    if df.empty or df["production"].dropna().empty:
        return _empty_chart("No production values available")
    grouped = df.groupby("region")["production"].sum().sort_values(ascending=False).head(12)
    fig, ax = plt.subplots(figsize=(8, 4))
    grouped.sort_values().plot(kind="barh", ax=ax)
    ax.set_title("Production by region (selected records)")
    ax.set_xlabel("Production (source units)")
    ax.set_ylabel("Region")
    fig.tight_layout()
    return fig

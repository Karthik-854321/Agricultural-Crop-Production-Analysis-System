import numpy as np
import pandas as pd


def calculate_yield(df):
    data = df.copy()
    area = pd.to_numeric(data["cultivated_area"], errors="coerce")
    production = pd.to_numeric(data["production"], errors="coerce")
    area_units = data.get("area_unit", pd.Series("unspecified", index=data.index)).astype(str).str.strip().str.lower()
    production_units = data.get("production_unit", pd.Series("unspecified", index=data.index)).astype(str).str.strip().str.lower()
    # Only calculate yield when both measurement units are explicitly provided.
    # Units need not be identical: the result is production-unit per area-unit.
    units_known = (
        area_units.ne("") & area_units.ne("unspecified") &
        production_units.ne("") & production_units.ne("unspecified")
    )
    data["yield"] = np.where(
        (area > 0) & production.notna() & units_known,
        production / area,
        np.nan,
    )
    return data


def build_summary(df):
    data = calculate_yield(df)
    grouped = data.groupby(["crop", "region"], dropna=False).agg(
        years_observed=("year", "nunique"),
        first_year=("year", "min"),
        last_year=("year", "max"),
        total_production=("production", "sum"),
        total_area=("cultivated_area", "sum"),
        mean_record_yield=("yield", "mean"),
        mean_rainfall=("rainfall", "mean"),
    ).reset_index()
    return grouped.sort_values(["crop", "region"])


def yearly_comparison(df):
    data = calculate_yield(df)
    grouped = data.groupby(["crop", "region", "year"], dropna=False).agg(
        production=("production", "sum"),
        cultivated_area=("cultivated_area", "sum"),
        mean_record_yield=("yield", "mean"),
        mean_rainfall=("rainfall", "mean"),
        records=("year", "size"),
    ).reset_index()
    grouped = grouped.sort_values(["crop", "region", "year"])
    grouped["production_change_pct"] = grouped.groupby(["crop", "region"])["production"].pct_change() * 100
    grouped["yield_change_pct"] = grouped.groupby(["crop", "region"])["mean_record_yield"].pct_change() * 100
    return grouped

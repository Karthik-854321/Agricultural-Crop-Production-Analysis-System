import pandas as pd
from src.validation import validate_records, normalize_columns
from src.analysis import calculate_yield, yearly_comparison


def test_valid_row_is_accepted():
    df = pd.DataFrame([{
        "crop": "Rice", "region": "North", "year": 2022,
        "cultivated_area": 10, "production": 25, "rainfall": 800,
        "area_unit": "hectare", "production_unit": "tonne", "rainfall_unit": "mm"
    }])
    checked, issues = validate_records(df)
    assert bool(checked.iloc[0]["is_valid"])
    assert issues.empty


def test_zero_area_is_flagged():
    df = pd.DataFrame([{
        "crop": "Rice", "region": "North", "year": 2022,
        "cultivated_area": 0, "production": 25
    }])
    checked, issues = validate_records(df)
    assert not bool(checked.iloc[0]["is_valid"])
    assert "Zero cultivated area" in checked.iloc[0]["validation_notes"]


def test_yield_not_calculated_for_zero_area():
    df = pd.DataFrame([{
        "crop": "Rice", "region": "North", "year": 2022,
        "cultivated_area": 0, "production": 25,
        "area_unit": "hectare", "production_unit": "tonne"
    }])
    result = calculate_yield(df)
    assert pd.isna(result.iloc[0]["yield"])


def test_alias_columns_are_normalized():
    df = pd.DataFrame([{
        "crop_name": "Rice", "region_name": "North", "year": 2022,
        "area": 10, "production": 25
    }])
    checked, _ = validate_records(normalize_columns(df))
    assert bool(checked.iloc[0]["is_valid"])

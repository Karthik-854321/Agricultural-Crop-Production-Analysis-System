import numpy as np
import pandas as pd

REQUIRED = ["crop", "region", "year", "cultivated_area", "production"]
OPTIONAL_DEFAULTS = {
    "rainfall": np.nan,
    "area_unit": "unspecified",
    "production_unit": "unspecified",
    "rainfall_unit": None,
}
QUALITY_COLUMNS = ["row_number", "issue", "details"]


def normalize_columns(df):
    result = df.copy()
    result.columns = [str(c).strip().lower().replace(" ", "_").replace("-", "_") for c in result.columns]
    aliases = {
        "crop_name": "crop",
        "region_name": "region",
        "cultivation_area": "cultivated_area",
        "area": "cultivated_area",
        "production_quantity": "production",
        "rainfall_mm": "rainfall",
        "year_of_record": "year",
    }
    result = result.rename(columns={c: aliases[c] for c in result.columns if c in aliases})
    return result


def validate_records(df):
    data = normalize_columns(df)
    missing = [column for column in REQUIRED if column not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    for column, default in OPTIONAL_DEFAULTS.items():
        if column not in data.columns:
            data[column] = default

    data["crop"] = data["crop"].astype("string").str.strip()
    data["region"] = data["region"].astype("string").str.strip()
    for col in ["year", "cultivated_area", "production", "rainfall"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data["area_unit"] = data["area_unit"].fillna("unspecified").astype(str).str.strip()
    data["production_unit"] = data["production_unit"].fillna("unspecified").astype(str).str.strip()
    data["rainfall_unit"] = data["rainfall_unit"].where(data["rainfall_unit"].notna(), None)

    notes = []
    valid_flags = []
    issue_rows = []

    for idx, row in data.iterrows():
        row_notes = []
        row_no = idx + 2
        if pd.isna(row["crop"]) or not str(row["crop"]).strip() or str(row["crop"]).lower() == "<na>":
            row_notes.append("Missing crop")
        if pd.isna(row["region"]) or not str(row["region"]).strip() or str(row["region"]).lower() == "<na>":
            row_notes.append("Missing region")
        if pd.isna(row["year"]) or row["year"] % 1 != 0 or not (1000 <= row["year"] <= 2100):
            row_notes.append("Year must be a whole number between 1000 and 2100")
        if pd.isna(row["cultivated_area"]):
            row_notes.append("Cultivated area is missing or non-numeric")
        elif row["cultivated_area"] < 0:
            row_notes.append("Cultivated area cannot be negative")
        elif row["cultivated_area"] == 0:
            row_notes.append("Zero cultivated area: yield cannot be calculated")
        if pd.isna(row["production"]):
            row_notes.append("Production is missing or non-numeric")
        elif row["production"] < 0:
            row_notes.append("Production cannot be negative")
        if pd.notna(row["rainfall"]) and row["rainfall"] < 0:
            row_notes.append("Rainfall cannot be negative")
        if not row_notes:
            valid_flags.append(True)
        else:
            valid_flags.append(False)
            for note in row_notes:
                issue_rows.append({"row_number": row_no, "issue": note, "details": f"Crop={row['crop']}; Region={row['region']}"})
        notes.append("; ".join(row_notes))

    data["is_valid"] = valid_flags
    data["validation_notes"] = notes
    issues = pd.DataFrame(issue_rows, columns=QUALITY_COLUMNS)
    return data, issues

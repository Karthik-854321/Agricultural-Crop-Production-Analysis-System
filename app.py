import io
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from src.database import init_db, save_records, load_records, get_connection
from src.validation import normalize_columns, validate_records, QUALITY_COLUMNS
from src.analysis import build_summary, yearly_comparison, calculate_yield
from src.charts import production_trend, yield_trend, region_comparison

st.set_page_config(page_title="Crop Production Analysis", page_icon="🌾", layout="wide")

st.title("Crop Production Analysis System")
st.caption("Explore historical crop production, cultivated area, rainfall, and yield. Descriptive analysis only.")

with st.sidebar:
    st.header("Database")
    st.write("Configure MySQL in `.env` or environment variables.")
    if st.button("Initialize database"):
        try:
            init_db()
            st.success("Database tables are ready.")
        except Exception as exc:
            st.error(f"Database initialization failed: {exc}")

tab_upload, tab_dashboard, tab_data, tab_about = st.tabs(
    ["Upload data", "Dashboard & reports", "Data explorer", "About"]
)

with tab_upload:
    st.subheader("Upload a historical dataset")
    st.markdown(
        "Upload a CSV or Excel file. Required columns: **crop, region, year, cultivated_area, production**. "
        "`rainfall` is optional. Column names such as `Crop_Name`, `Area`, and `Yield` are not assumed; "
        "use the documented column names or rename them before upload."
    )
    uploaded = st.file_uploader("Choose CSV or Excel file", type=["csv", "xlsx", "xls"])
    if uploaded:
        try:
            raw = pd.read_csv(uploaded) if uploaded.name.lower().endswith(".csv") else pd.read_excel(uploaded)
            st.write("Preview", raw.head(10))
            normalized = normalize_columns(raw)
            checked, issues = validate_records(normalized)
            st.subheader("Validation summary")
            c1, c2, c3 = st.columns(3)
            c1.metric("Rows received", len(raw))
            c2.metric("Valid rows", int(checked["is_valid"].sum()))
            c3.metric("Rows needing review", int((~checked["is_valid"]).sum()))
            if not issues.empty:
                st.dataframe(issues, width="stretch")
                st.download_button(
                    "Download validation issues",
                    issues.to_csv(index=False).encode("utf-8"),
                    "validation_issues.csv",
                    "text/csv",
                )
            st.dataframe(checked, width="stretch")
            valid = checked[checked["is_valid"]].copy()
            if st.button("Save valid rows to MySQL", type="primary", disabled=valid.empty):
                try:
                    init_db()
                    inserted = save_records(valid)
                    st.success(f"Saved {inserted} valid records.")
                except Exception as exc:
                    st.error(f"Could not save records: {exc}")
            st.download_button(
                "Download normalized data",
                checked.drop(columns=["is_valid", "validation_notes"], errors="ignore").to_csv(index=False).encode("utf-8"),
                "normalized_crop_data.csv",
                "text/csv",
            )
        except Exception as exc:
            st.error(f"Could not read this file: {exc}")

with tab_dashboard:
    st.subheader("Historical dashboard")
    source = st.radio("Data source", ["MySQL database", "Upload a file for this session"], horizontal=True)
    df = pd.DataFrame()
    if source == "MySQL database":
        if st.button("Load database records"):
            st.session_state["db_loaded"] = True
        if st.session_state.get("db_loaded"):
            try:
                df = load_records()
            except Exception as exc:
                st.error(f"Could not load database records: {exc}")
    else:
        session_file = st.file_uploader("Choose a CSV or Excel file for analysis", type=["csv", "xlsx", "xls"], key="dashboard_upload")
        if session_file:
            try:
                raw = pd.read_csv(session_file) if session_file.name.lower().endswith(".csv") else pd.read_excel(session_file)
                clean, _ = validate_records(normalize_columns(raw))
                df = clean[clean["is_valid"]].drop(columns=["is_valid", "validation_notes"], errors="ignore")
            except Exception as exc:
                st.error(f"Could not analyze this file: {exc}")

    if not df.empty:
        df = calculate_yield(df)
        crops = sorted(df["crop"].dropna().unique().tolist())
        regions = sorted(df["region"].dropna().unique().tolist())
        years = sorted(df["year"].dropna().astype(int).unique().tolist())
        a, b, c = st.columns(3)
        selected_crops = a.multiselect("Crops", crops, default=crops)
        selected_regions = b.multiselect("Regions", regions, default=regions)
        selected_years = c.multiselect("Years", years, default=years)
        filtered = df[
            df["crop"].isin(selected_crops)
            & df["region"].isin(selected_regions)
            & df["year"].isin(selected_years)
        ].copy()

        if filtered.empty:
            st.warning("No records match the selected filters.")
        else:
            total_prod = filtered["production"].sum(min_count=1)
            total_area = filtered["cultivated_area"].sum(min_count=1)
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Records", f"{len(filtered):,}")
            m2.metric("Total production", f"{total_prod:,.2f}" if pd.notna(total_prod) else "N/A")
            m3.metric("Cultivated area", f"{total_area:,.2f}" if pd.notna(total_area) else "N/A")
            valid_yield = filtered["yield"].dropna()
            m4.metric("Mean record yield", f"{valid_yield.mean():,.3f}" if not valid_yield.empty else "N/A")

            st.pyplot(production_trend(filtered), width="stretch")
            left, right = st.columns(2)
            with left:
                st.pyplot(yield_trend(filtered), width="stretch")
            with right:
                st.pyplot(region_comparison(filtered), width="stretch")

            st.subheader("Crop-wise and region-wise report")
            summary = build_summary(filtered)
            st.dataframe(summary, width="stretch")
            st.download_button("Download summary CSV", summary.to_csv(index=False).encode("utf-8"), "crop_region_summary.csv", "text/csv")

            st.subheader("Year comparison")
            comparison = yearly_comparison(filtered)
            st.dataframe(comparison, width="stretch")
            st.download_button("Download year comparison CSV", comparison.to_csv(index=False).encode("utf-8"), "year_comparison.csv", "text/csv")
    else:
        st.info("Load records from MySQL or upload a dataset to view the dashboard.")

with tab_data:
    st.subheader("Data explorer")
    try:
        if st.button("Refresh database table"):
            st.session_state["explorer_loaded"] = True
        if st.session_state.get("explorer_loaded"):
            records = load_records()
            if records.empty:
                st.info("The database has no records yet.")
            else:
                st.dataframe(records, width="stretch")
                st.download_button("Export database records", records.to_csv(index=False).encode("utf-8"), "crop_records.csv", "text/csv")
    except Exception as exc:
        st.info(f"Database is not available yet: {exc}")

with tab_about:
    st.subheader("Project scope")
    st.markdown("""
    - Describes historical production and yield patterns.
    - Yield is calculated as production divided by cultivated area only when area is positive and units are compatible.
    - Missing, zero, negative, and non-numeric values are flagged instead of silently repaired.
    - Rainfall is displayed as an optional historical field; correlation is not treated as causation.
    - Comparisons should use consistent production and area units and comparable time periods.
    """)
    st.code("crop,region,year,cultivated_area,production,rainfall\\nRice,Region A,2022,1200,3600,850")

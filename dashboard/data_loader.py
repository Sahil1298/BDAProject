from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_data():
    output_dir = Path(__file__).resolve().parent.parent / "output"
    result_files = {
        "MapReduce": (
            output_dir / "output_aqi_bucket.csv",
            output_dir / "output_avg_pm25.csv",
        ),
        "PySpark": (
            output_dir / "pyspark_aqi_bucket.csv",
            output_dir / "pyspark_avg_pm25.csv",
        ),
    }
    results = {}

    for method, (aqi_path, pm25_path) in result_files.items():
        aqi = pd.read_csv(aqi_path)
        pm25 = pd.read_csv(pm25_path)

        aqi.columns = aqi.columns.str.strip()
        pm25.columns = pm25.columns.str.strip()
        aqi = aqi.rename(
            columns={
                "date": "Date",
                "AQI_Bucket": "AQI_Category",
                "count": "Count",
            }
        )
        pm25 = pm25.rename(columns={"StationId": "Station_ID"})

        required_columns = (
            ("AQI", aqi, {"Date", "AQI_Category", "Count"}, aqi_path),
            ("PM2.5", pm25, {"Station_ID", "Avg_PM25"}, pm25_path),
        )
        for label, frame, required, path in required_columns:
            missing = required.difference(frame.columns)
            if missing:
                raise ValueError(
                    f"{label} result at {path} is missing columns: "
                    f"{', '.join(sorted(missing))}"
                )
            if frame.empty:
                raise ValueError(f"{label} result file is empty: {path}")

        aqi["Date"] = pd.to_datetime(aqi["Date"], errors="coerce")
        aqi["AQI_Category"] = aqi["AQI_Category"].astype("string").str.strip()
        aqi["Count"] = pd.to_numeric(aqi["Count"], errors="coerce")
        aqi = aqi.dropna(subset=["Date", "AQI_Category", "Count"])

        pm25["Station_ID"] = pm25["Station_ID"].astype("string").str.strip()
        pm25["Avg_PM25"] = pd.to_numeric(pm25["Avg_PM25"], errors="coerce")
        pm25 = pm25.dropna(subset=["Station_ID", "Avg_PM25"])

        if aqi.empty or pm25.empty:
            raise ValueError(f"{method} result files contain no usable rows.")

        results[method] = (aqi, pm25)

    return results

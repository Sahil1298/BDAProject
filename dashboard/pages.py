import streamlit as st

from dashboard.charts import (
    aqi_category_summary_chart,
    aqi_composition_chart,
    aqi_distribution_chart,
    aqi_trend_chart,
    pm25_distribution_chart,
    top_stations_chart,
)
from dashboard.data_loader import load_data


def _configure_page():
    st.set_page_config(
        page_title="Air Quality Analytics",
        page_icon="",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(
        """
        <style>
        .stApp { background-color: #f5f7fb; }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1400px;
        }
        section[data-testid="stSidebar"] { background-color: #111827; }
        section[data-testid="stSidebar"] * { color: #e5e7eb; }
        .main-title {
            font-size: 34px;
            font-weight: 700;
            color: #111827;
            margin-bottom: 5px;
        }
        .sub-title {
            font-size: 15px;
            color: #6b7280;
            margin-bottom: 30px;
        }
        .section-title {
            font-size: 23px;
            font-weight: 650;
            color: #111827;
            margin-top: 20px;
            margin-bottom: 18px;
        }
        .metric-card {
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            min-height: 120px;
        }
        .metric-label {
            font-size: 12px;
            font-weight: 600;
            color: #6b7280;
            margin-bottom: 8px;
        }
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #111827;
        }
        .metric-small {
            font-size: 12px;
            color: #9ca3af;
            margin-top: 5px;
        }
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        header { background-color: transparent; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_sidebar():
    with st.sidebar:
        st.markdown(
            """
            <div style="
                font-size:25px;
                font-weight:700;
                color:white;
                margin-bottom:4px;
            ">
            Air Quality
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="
                font-size:13px;
                color:#9ca3af;
                margin-bottom:30px;
            ">
            India · 2015–2020
            </div>
            """,
            unsafe_allow_html=True,
        )
        page = st.radio(
            "Navigation",
            ["Dashboard", "AQI Trends", "PM2.5 Analysis"],
        )
        analysis_method = st.radio("Results source", ["MapReduce", "PySpark"])
        st.markdown("---")
        st.caption("Air Quality Data in India")
    return page, analysis_method


def _render_header(analysis_method):
    st.markdown(
        '<div class="main-title">Air Quality Analytics</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="sub-title">'
        "India air quality analysis using MapReduce and PySpark"
        "</div>",
        unsafe_allow_html=True,
    )
    st.caption(f"Showing {analysis_method} results")


def _render_processing_method(analysis_method):
    if analysis_method == "MapReduce":
        st.subheader("MapReduce Processing")
        st.write("Mapper → Shuffle/Sort → Reducer")
        st.caption(
            "Results are loaded from output/output_aqi_bucket.csv and "
            "output/output_avg_pm25.csv."
        )
    else:
        st.subheader("PySpark Processing")
        st.write("Spark DataFrame → groupBy/aggregation")
        st.caption(
            "Results are loaded from output/pyspark_aqi_bucket.csv and "
            "output/pyspark_avg_pm25.csv."
        )


def _render_dashboard(aqi, pm25, analysis_method):
    total_stations = pm25["Station_ID"].nunique() if "Station_ID" in pm25.columns else 0
    total_dates = aqi["Date"].nunique() if "Date" in aqi.columns else 0
    if "Avg_PM25" in pm25.columns:
        average_pm25 = pm25["Avg_PM25"].mean()
    else:
        average_pm25 = 0

    c1, c2, c3, c4 = st.columns(4)
    metrics = (
        (c1, "AQI RECORDS COUNTED", f'{int(aqi["Count"].sum()):,}', f"{analysis_method} result"),
        (c2, "MONITORING STATIONS", f"{total_stations:,}", "Stations analyzed"),
        (c3, "DATES ANALYZED", f"{total_dates:,}", "Daily observations"),
        (c4, "AVERAGE PM2.5", f"{average_pm25:.2f}", "Across monitoring stations"),
    )
    for column, label, value, detail in metrics:
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-small">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("")
    st.markdown(
        '<div class="section-title">AQI Distribution Over Time</div>',
        unsafe_allow_html=True,
    )
    if {"Date", "AQI_Category", "Count"}.issubset(aqi.columns):
        daily_aqi = (
            aqi.groupby(["Date", "AQI_Category"], as_index=False)["Count"]
            .sum()
        )
        st.plotly_chart(aqi_distribution_chart(daily_aqi), width="stretch")

    left, right = st.columns(2)
    with left:
        st.markdown(
            '<div class="section-title">Highest PM2.5 Stations</div>',
            unsafe_allow_html=True,
        )
        if {"Station_ID", "Avg_PM25"}.issubset(pm25.columns):
            top_stations = (
                pm25.sort_values("Avg_PM25", ascending=False)
                .head(10)
                .sort_values("Avg_PM25")
            )
            st.plotly_chart(
                top_stations_chart(top_stations, height=430, yaxis_title=""),
                width="stretch",
            )

    with right:
        st.markdown(
            '<div class="section-title">AQI Category Composition</div>',
            unsafe_allow_html=True,
        )
        if {"AQI_Category", "Count"}.issubset(aqi.columns):
            category_summary = (
                aqi.groupby("AQI_Category", as_index=False)["Count"].sum()
            )
            st.plotly_chart(
                aqi_composition_chart(category_summary),
                width="stretch",
            )

    if {"Station_ID", "Avg_PM25"}.issubset(pm25.columns) and not pm25.empty:
        highest_row = pm25.loc[pm25["Avg_PM25"].idxmax()]
        st.info(
            f"Highest station average: {highest_row['Station_ID']} — "
            f"{highest_row['Avg_PM25']:.2f} PM2.5"
        )


def _render_aqi_trends(aqi):
    st.markdown(
        '<div class="section-title">AQI Trends</div>',
        unsafe_allow_html=True,
    )
    st.write("Analyze AQI category frequency across different time periods.")

    aqi = aqi.copy()
    aqi["Year"] = aqi["Date"].dt.year
    available_years = sorted(aqi["Year"].dropna().unique())
    if not available_years:
        st.warning("No valid dates were found in the AQI dataset.")
        st.stop()

    c1, c2 = st.columns(2)
    with c1:
        selected_year = st.selectbox("Select Year", available_years)

    filtered_year = aqi[aqi["Year"] == selected_year].copy()
    available_categories = sorted(
        filtered_year["AQI_Category"].dropna().unique()
    )
    with c2:
        selected_category = st.selectbox(
            "Select AQI Category",
            ["All"] + list(available_categories),
        )

    if selected_category != "All":
        filtered_data = filtered_year[
            filtered_year["AQI_Category"] == selected_category
        ].copy()
    else:
        filtered_data = filtered_year.copy()

    trend_data = (
        filtered_data.groupby(
            ["Date", "AQI_Category"], as_index=False
        )["Count"]
        .sum()
    )
    st.plotly_chart(aqi_trend_chart(trend_data), width="stretch")

    st.markdown(
        '<div class="section-title">AQI Category Summary</div>',
        unsafe_allow_html=True,
    )
    summary = (
        filtered_data.groupby("AQI_Category", as_index=False)["Count"]
        .sum()
        .sort_values("Count", ascending=False)
    )
    st.plotly_chart(aqi_category_summary_chart(summary), width="stretch")

    with st.expander("View processed AQI data"):
        table_data = filtered_data.copy()
        if "Date" in table_data.columns:
            table_data["Date"] = table_data["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(table_data, width="stretch", hide_index=True)


def _render_pm25_analysis(pm25):
    st.markdown(
        '<div class="section-title">PM2.5 Analysis</div>',
        unsafe_allow_html=True,
    )
    st.write("Compare average PM2.5 concentration across monitoring stations.")

    station_limit = st.slider(
        "Number of stations",
        min_value=5,
        max_value=30,
        value=10,
    )
    top_stations = (
        pm25.sort_values("Avg_PM25", ascending=False)
        .head(station_limit)
        .sort_values("Avg_PM25")
    )
    st.plotly_chart(
        top_stations_chart(
            top_stations,
            height=550,
            yaxis_title="Monitoring Station",
        ),
        width="stretch",
    )

    highest_pm25 = pm25["Avg_PM25"].max()
    average_pm25 = pm25["Avg_PM25"].mean()
    lowest_pm25 = pm25["Avg_PM25"].min()
    c1, c2, c3 = st.columns(3)
    metrics = (
        (c1, "HIGHEST PM2.5", highest_pm25, "Maximum station average"),
        (c2, "OVERALL AVERAGE", average_pm25, "Across all stations"),
        (c3, "LOWEST PM2.5", lowest_pm25, "Minimum station average"),
    )
    for column, label, value, detail in metrics:
        with column:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value:.2f}</div>
                    <div class="metric-small">{detail}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<div class="section-title">PM2.5 Distribution</div>',
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        pm25_distribution_chart(pm25),
        width="stretch",
    )

    st.markdown(
        '<div class="section-title">Station Lookup</div>',
        unsafe_allow_html=True,
    )
    station_list = sorted(pm25["Station_ID"].dropna().unique())
    selected_station = st.selectbox("Select Monitoring Station", station_list)
    station_result = pm25[pm25["Station_ID"] == selected_station]
    st.dataframe(station_result, width="stretch", hide_index=True)


def run_app():
    _configure_page()
    try:
        results = load_data()
    except Exception as error:
        st.error("Unable to load the project data.")
        st.error(str(error))
        st.stop()

    page, analysis_method = _render_sidebar()
    aqi, pm25 = results[analysis_method]
    _render_header(analysis_method)
    _render_processing_method(analysis_method)

    if page == "Dashboard":
        _render_dashboard(aqi, pm25, analysis_method)
    elif page == "AQI Trends":
        _render_aqi_trends(aqi)
    elif page == "PM2.5 Analysis":
        _render_pm25_analysis(pm25)

    st.markdown("---")
    st.markdown(
        """
        <div style="
            text-align:center;
            color:#9ca3af;
            font-size:12px;
            padding:10px;
        ">
        Air Quality Analytics · India 2015–2020
        </div>
        """,
        unsafe_allow_html=True,
    )

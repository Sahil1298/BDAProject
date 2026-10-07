from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Air Quality Analytics",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .stApp {
        background-color: #f5f7fb;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    section[data-testid="stSidebar"] {
        background-color: #111827;
    }

    section[data-testid="stSidebar"] * {
        color: #e5e7eb;
    }

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

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background-color: transparent;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    output_dir = Path(__file__).resolve().parent / "output"
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


# ============================================================
# LOAD FILES
# ============================================================

try:
    results = load_data()

except Exception as e:
    st.error("Unable to load the project data.")
    st.error(str(e))
    st.stop()


# ============================================================
# SIDEBAR
# ============================================================

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
        unsafe_allow_html=True
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
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Dashboard",
            "AQI Trends",
            "PM2.5 Analysis"
        ]
    )

    analysis_method = st.radio(
        "Results source",
        ["MapReduce", "PySpark"],
    )

    st.markdown("---")

    st.caption("Air Quality Data in India")

aqi, pm25 = results[analysis_method]


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="main-title">Air Quality Analytics</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'India air quality analysis using MapReduce and PySpark'
    '</div>',
    unsafe_allow_html=True
)
st.caption(f"Showing {analysis_method} results")


# ============================================================
# DASHBOARD
# ============================================================

if page == "Dashboard":

    # Basic statistics

    if "Station_ID" in pm25.columns:
        total_stations = pm25["Station_ID"].nunique()
    else:
        total_stations = 0

    if "Date" in aqi.columns:
        total_dates = aqi["Date"].nunique()
    else:
        total_dates = 0

    if "Avg_PM25" in pm25.columns:
        average_pm25 = pm25["Avg_PM25"].mean()
        maximum_pm25 = pm25["Avg_PM25"].max()
    else:
        average_pm25 = 0
        maximum_pm25 = 0

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    AQI RECORDS COUNTED
                </div>
                <div class="metric-value">
                    {int(aqi["Count"].sum()):,}
                </div>
                <div class="metric-small">
                    {analysis_method} result
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    MONITORING STATIONS
                </div>
                <div class="metric-value">
                    {total_stations:,}
                </div>
                <div class="metric-small">
                    Stations analyzed
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    DATES ANALYZED
                </div>
                <div class="metric-value">
                    {total_dates:,}
                </div>
                <div class="metric-small">
                    Daily observations
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c4:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    AVERAGE PM2.5
                </div>
                <div class="metric-value">
                    {average_pm25:.2f}
                </div>
                <div class="metric-small">
                    Across monitoring stations
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")

    # --------------------------------------------------------
    # AQI DISTRIBUTION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">AQI Distribution Over Time</div>',
        unsafe_allow_html=True
    )

    if (
        "Date" in aqi.columns
        and "AQI_Category" in aqi.columns
        and "Count" in aqi.columns
    ):

        daily_aqi = (
            aqi
            .groupby(
                ["Date", "AQI_Category"],
                as_index=False
            )["Count"]
            .sum()
        )

        fig = px.area(
            daily_aqi,
            x="Date",
            y="Count",
            color="AQI_Category",
            template="plotly_white"
        )

        fig.update_layout(
            height=430,
            margin=dict(
                l=20,
                r=20,
                t=20,
                b=20
            ),
            xaxis_title="Date",
            yaxis_title="Observations",
            legend_title=""
        )

        st.plotly_chart(
            fig,
            width="stretch"
        )

    # --------------------------------------------------------
    # TWO CHARTS
    # --------------------------------------------------------

    left, right = st.columns(2)

    # Highest PM2.5 stations

    with left:

        st.markdown(
            '<div class="section-title">Highest PM2.5 Stations</div>',
            unsafe_allow_html=True
        )

        if (
            "Station_ID" in pm25.columns
            and "Avg_PM25" in pm25.columns
        ):

            top_stations = (
                pm25
                .sort_values(
                    "Avg_PM25",
                    ascending=False
                )
                .head(10)
                .sort_values("Avg_PM25")
            )

            fig = px.bar(
                top_stations,
                x="Avg_PM25",
                y="Station_ID",
                orientation="h",
                color="Avg_PM25",
                color_continuous_scale=[
                    "#fee2e2",
                    "#f87171",
                    "#dc2626"
                ],
                template="plotly_white"
            )

            fig.update_layout(
                height=430,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                ),
                xaxis_title="Average PM2.5",
                yaxis_title="",
                coloraxis_showscale=False
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

    # AQI composition

    with right:

        st.markdown(
            '<div class="section-title">AQI Category Composition</div>',
            unsafe_allow_html=True
        )

        if (
            "AQI_Category" in aqi.columns
            and "Count" in aqi.columns
        ):

            category_summary = (
                aqi
                .groupby(
                    "AQI_Category",
                    as_index=False
                )["Count"]
                .sum()
            )

            fig = px.pie(
                category_summary,
                names="AQI_Category",
                values="Count",
                hole=0.55,
                template="plotly_white"
            )

            fig.update_layout(
                height=430,
                margin=dict(
                    l=20,
                    r=20,
                    t=20,
                    b=20
                ),
                legend_title=""
            )

            st.plotly_chart(
                fig,
                width="stretch"
            )

    # --------------------------------------------------------
    # HIGHEST POLLUTION STATION
    # --------------------------------------------------------

    if (
        "Station_ID" in pm25.columns
        and "Avg_PM25" in pm25.columns
        and len(pm25) > 0
    ):

        highest_row = pm25.loc[
            pm25["Avg_PM25"].idxmax()
        ]

        highest_station = highest_row["Station_ID"]
        highest_value = highest_row["Avg_PM25"]

        st.info(
            f"Highest station average: "
            f"{highest_station} — "
            f"{highest_value:.2f} PM2.5"
        )


# ============================================================
# AQI TRENDS
# ============================================================

elif page == "AQI Trends":

    st.markdown(
        '<div class="section-title">AQI Trends</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Analyze AQI category frequency across different time periods."
    )

    # --------------------------------------------------------
    # CREATE YEAR COLUMN
    # --------------------------------------------------------

    aqi["Year"] = aqi["Date"].dt.year

    available_years = sorted(
        aqi["Year"]
        .dropna()
        .unique()
    )

    if len(available_years) == 0:

        st.warning("No valid dates were found in the AQI dataset.")

        st.stop()

    # --------------------------------------------------------
    # FILTERS
    # --------------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:

        selected_year = st.selectbox(
            "Select Year",
            available_years
        )

    filtered_year = aqi[
        aqi["Year"] == selected_year
    ].copy()

    available_categories = sorted(
        filtered_year["AQI_Category"]
        .dropna()
        .unique()
    )

    with c2:

        selected_category = st.selectbox(
            "Select AQI Category",
            ["All"] + list(available_categories)
        )

    if selected_category != "All":

        filtered_data = filtered_year[
            filtered_year["AQI_Category"]
            == selected_category
        ].copy()

    else:

        filtered_data = filtered_year.copy()

    # --------------------------------------------------------
    # DAILY TREND
    # --------------------------------------------------------

    trend_data = (
        filtered_data
        .groupby(
            ["Date", "AQI_Category"],
            as_index=False
        )["Count"]
        .sum()
    )

    fig = px.line(
        trend_data,
        x="Date",
        y="Count",
        color="AQI_Category",
        template="plotly_white"
    )

    fig.update_layout(
        height=480,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        xaxis_title="Date",
        yaxis_title="Observations",
        legend_title=""
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # --------------------------------------------------------
    # YEAR SUMMARY
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">AQI Category Summary</div>',
        unsafe_allow_html=True
    )

    summary = (
        filtered_data
        .groupby(
            "AQI_Category",
            as_index=False
        )["Count"]
        .sum()
        .sort_values(
            "Count",
            ascending=False
        )
    )

    fig = px.bar(
        summary,
        x="AQI_Category",
        y="Count",
        color="AQI_Category",
        template="plotly_white"
    )

    fig.update_layout(
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        xaxis_title="AQI Category",
        yaxis_title="Observations",
        legend_title=""
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # --------------------------------------------------------
    # DATA TABLE
    # --------------------------------------------------------

    with st.expander("View processed AQI data"):

        table_data = filtered_data.copy()

        if "Date" in table_data.columns:

            table_data["Date"] = table_data[
                "Date"
            ].dt.strftime("%Y-%m-%d")

        st.dataframe(
            table_data,
            width="stretch",
            hide_index=True
        )


# ============================================================
# PM2.5 ANALYSIS
# ============================================================

elif page == "PM2.5 Analysis":

    st.markdown(
        '<div class="section-title">PM2.5 Analysis</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Compare average PM2.5 concentration across monitoring stations."
    )

    # --------------------------------------------------------
    # STATION COUNT FILTER
    # --------------------------------------------------------

    station_limit = st.slider(
        "Number of stations",
        min_value=5,
        max_value=30,
        value=10
    )

    top_stations = (
        pm25
        .sort_values(
            "Avg_PM25",
            ascending=False
        )
        .head(station_limit)
        .sort_values(
            "Avg_PM25"
        )
    )

    # --------------------------------------------------------
    # STATION CHART
    # --------------------------------------------------------

    fig = px.bar(
        top_stations,
        x="Avg_PM25",
        y="Station_ID",
        orientation="h",
        color="Avg_PM25",
        color_continuous_scale=[
            "#fee2e2",
            "#f87171",
            "#dc2626"
        ],
        template="plotly_white"
    )

    fig.update_layout(
        height=550,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        xaxis_title="Average PM2.5",
        yaxis_title="Monitoring Station",
        coloraxis_showscale=False
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # --------------------------------------------------------
    # STATISTICS
    # --------------------------------------------------------

    highest_pm25 = pm25["Avg_PM25"].max()
    average_pm25 = pm25["Avg_PM25"].mean()
    lowest_pm25 = pm25["Avg_PM25"].min()

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    HIGHEST PM2.5
                </div>
                <div class="metric-value">
                    {highest_pm25:.2f}
                </div>
                <div class="metric-small">
                    Maximum station average
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c2:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    OVERALL AVERAGE
                </div>
                <div class="metric-value">
                    {average_pm25:.2f}
                </div>
                <div class="metric-small">
                    Across all stations
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with c3:

        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-label">
                    LOWEST PM2.5
                </div>
                <div class="metric-value">
                    {lowest_pm25:.2f}
                </div>
                <div class="metric-small">
                    Minimum station average
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # --------------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">PM2.5 Distribution</div>',
        unsafe_allow_html=True
    )

    fig = px.histogram(
        pm25,
        x="Avg_PM25",
        nbins=35,
        template="plotly_white",
        color_discrete_sequence=["#2563eb"]
    )

    fig.update_layout(
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20
        ),
        xaxis_title="Average PM2.5",
        yaxis_title="Number of Stations"
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )

    # --------------------------------------------------------
    # STATION LOOKUP
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">Station Lookup</div>',
        unsafe_allow_html=True
    )

    station_list = sorted(
        pm25["Station_ID"]
        .dropna()
        .unique()
    )

    selected_station = st.selectbox(
        "Select Monitoring Station",
        station_list
    )

    station_result = pm25[
        pm25["Station_ID"] == selected_station
    ]

    st.dataframe(
        station_result,
        width="stretch",
        hide_index=True
    )


# ============================================================
# FOOTER
# ============================================================

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
    unsafe_allow_html=True
)

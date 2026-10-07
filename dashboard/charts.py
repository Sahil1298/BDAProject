import plotly.express as px


def aqi_distribution_chart(data):
    fig = px.area(
        data,
        x="Date",
        y="Count",
        color="AQI_Category",
        template="plotly_white",
    )
    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Date",
        yaxis_title="Observations",
        legend_title="",
    )
    return fig


def top_stations_chart(data, height, yaxis_title):
    fig = px.bar(
        data,
        x="Avg_PM25",
        y="Station_ID",
        orientation="h",
        color="Avg_PM25",
        color_continuous_scale=["#fee2e2", "#f87171", "#dc2626"],
        template="plotly_white",
    )
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Average PM2.5",
        yaxis_title=yaxis_title,
        coloraxis_showscale=False,
    )
    return fig


def aqi_composition_chart(data):
    fig = px.pie(
        data,
        names="AQI_Category",
        values="Count",
        hole=0.55,
        template="plotly_white",
    )
    fig.update_layout(
        height=430,
        margin=dict(l=20, r=20, t=20, b=20),
        legend_title="",
    )
    return fig


def aqi_trend_chart(data):
    fig = px.line(
        data,
        x="Date",
        y="Count",
        color="AQI_Category",
        template="plotly_white",
    )
    fig.update_layout(
        height=480,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Date",
        yaxis_title="Observations",
        legend_title="",
    )
    return fig


def aqi_category_summary_chart(data):
    fig = px.bar(
        data,
        x="AQI_Category",
        y="Count",
        color="AQI_Category",
        template="plotly_white",
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="AQI Category",
        yaxis_title="Observations",
        legend_title="",
    )
    return fig


def pm25_distribution_chart(data):
    fig = px.histogram(
        data,
        x="Avg_PM25",
        nbins=35,
        template="plotly_white",
        color_discrete_sequence=["#2563eb"],
    )
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis_title="Average PM2.5",
        yaxis_title="Number of Stations",
    )
    return fig

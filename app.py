import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px
import matplotlib.pyplot as plt
import json
import os
import copy

from data_cleaning import load_and_clean


# PAGE CONFIG
# Sets the browser tab title, forces wide layout, and keeps the sidebar open by default
st.set_page_config(
    page_title="Luxembourg Labour Market Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GLOBAL STYLES
# Injects custom CSS via a hidden markdown block:
#   - DM Sans / DM Mono from Google Fonts for a clean, modern typographic feel
#   - Metric cards get a white background, subtle border and shadow
#   - .map-legend and .legend-gradient are used below the choropleth map
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e6e6e6;
        padding: 14px 18px;
        border-radius: 12px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }

    div[data-testid="metric-container"] label {
        font-size: 0.72rem;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        color: #888;
    }

    div[data-testid="metric-container"] div[data-testid="metric-value"] {
        font-size: 1.6rem;
        font-weight: 600;
        color: #1a1a2e;
    }

    /* Legend bar shown below the pydeck map */
    .map-legend {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-top: 8px;
        font-size: 0.75rem;
        color: #666;
        font-family: 'DM Mono', monospace;
    }

    /* Matches the YlOrRd matplotlib colormap used on the choropleth */
    .legend-gradient {
        width: 140px;
        height: 10px;
        border-radius: 5px;
        background: linear-gradient(to right, #ffffb2, #fecc5c, #fd8d3c, #f03b20, #bd0026);
    }
    </style>
    """,
    unsafe_allow_html=True
)


# SIDEBAR — ETL PIPELINE TRIGGER
# Allows the user to re-run the data cleaning pipeline on demand.
# The cleaned CSV is the single source of truth for the rest of the dashboard.
st.sidebar.title("Data Pipeline")

run_etl = st.sidebar.button("Run Data Cleaning Pipeline")

if run_etl:
    with st.spinner("Running ETL pipeline..."):
        load_and_clean(
            input_path="data/datasc-skills-vacancies-2025-2027.csv",
            output_path="data/cleaned_dataset.csv"
        )
    st.success("Dataset successfully updated")

# Quick status indicator so the user knows whether cleaned data exists
st.sidebar.metric(
    "Dataset Ready",
    os.path.exists("data/cleaned_dataset.csv")
)


# DATA LOADING
# @st.cache_data prevents reloading the CSV on every Streamlit rerun.
# Columns are stripped of whitespace to guard against inconsistent CSV exports.
@st.cache_data
def load_data():
    if not os.path.exists("data/cleaned_dataset.csv"):
        st.warning("Cleaned dataset not found. Please run the pipeline first.")
        return pd.DataFrame()
    df = pd.read_csv("data/cleaned_dataset.csv")
    df.columns = df.columns.str.strip()
    return df


df = load_data()

# Hard stop if there is nothing to display — avoids downstream KeyErrors
if df.empty:
    st.stop()


# GEOJSON LOADING
# Canton boundaries for Luxembourg loaded once and cached.
# geo_key is the property name inside each GeoJSON feature that holds the canton name,
# used to join spatial data with the aggregated job counts.
@st.cache_data
def load_geojson():
    with open("data/luxembourg_cantons.geojson") as f:
        return json.load(f)


geojson = load_geojson()
geo_key = "NAME_2"   # GeoJSON property that matches df["canton"]


# TITLE
st.title("Luxembourg Labour Market Dashboard")
st.caption("Jobs, skills, occupations and regional distribution")


# FILTERS
# Two cascading dropdowns: selecting a NACE sector narrows the occupation list.
# Placing them in columns keeps the UI compact on wide screens.
col1, col2 = st.columns(2)

with col1:
    nace_options = sorted(df["nace_label"].unique())
    selected_nace = st.selectbox("NACE Sector", nace_options)

# Narrow the occupation options to only those present in the chosen sector
df_nace = df[df["nace_label"] == selected_nace]

with col2:
    role_options = ["All"] + sorted(df_nace["occupation_label"].unique())
    selected_role = st.selectbox("Occupation", role_options)

# Apply the occupation filter (or keep the full sector slice if "All" is chosen)
if selected_role == "All":
    df_filtered = df_nace.copy()
else:
    df_filtered = df_nace[df_nace["occupation_label"] == selected_role]


# KPI METRICS
# Four headline numbers derived from the current filter state.
# Occupations counts from df_nace (sector level) so it doesn't collapse to 1
# when a specific occupation is selected.
st.divider()

k1, k2, k3, k4 = st.columns(4)
k1.metric("Job Postings", len(df_filtered))
k2.metric("Unique Skills", df_filtered["skill"].nunique())
k3.metric("Occupations", df_nace["occupation_label"].nunique())
k4.metric("Active Cantons", df_filtered["canton"].nunique())


# CANTON-LEVEL AGGREGATION
# Count job postings per canton, then compute each canton's share of the total.
canton_counts = (
    df_filtered["canton"]
    .value_counts()
    .reset_index()
)
canton_counts.columns = ["canton", "jobs"]

total_jobs = canton_counts["jobs"].sum()

# Percentage share of total postings; guard against division by zero
canton_counts["percentage"] = (
    canton_counts["jobs"] / total_jobs * 100
    if total_jobs > 0 else 0
)

# Left-join against all cantons present in the GeoJSON so that cantons with
# zero postings still appear on the map (filled with the "low" color)
all_cantons = [f["properties"][geo_key] for f in geojson["features"]]
full = pd.DataFrame({"canton": all_cantons})
canton_counts = full.merge(canton_counts, on="canton", how="left").fillna(0)

# Top-10 skills for the bar chart in the right panel
top_skills = df_filtered["skill"].value_counts().head(10)


# TWO-COLUMN LAYOUT
# Left: choropleth map  |  Right: occupation pie + skills bar
st.divider()
col_map, col_right = st.columns([1, 1])


# MAP — YlOrRd COLOR-GRADED CHOROPLETH
with col_map:
    st.subheader("Regional Job Distribution")

    # Use matplotlib's YlOrRd colormap (yellow → orange → red) to map
    # job-share percentages to RGBA colors.
    cmap = plt.get_cmap("YlOrRd")

    # Normalise against the actual maximum so the full color range is always used,
    # even when the highest canton only holds e.g. 30% of postings.
    max_pct = canton_counts["percentage"].max()
    if max_pct == 0:
        max_pct = 1  # fallback to avoid divide-by-zero when the filter returns nothing

    # Deep-copy the cached GeoJSON so that successive Streamlit reruns don't
    # accumulate stale fill_color values on the shared cached object.
    geojson_copy = copy.deepcopy(geojson)

    # Inject per-feature data: job count, percentage, pre-formatted label, and RGBA color.
    # pydeck tooltip templates are plain HTML — they do NOT support Python format specs
    # like {value:.1f}, so percentage_label is pre-formatted here in Python.
    for feature in geojson_copy["features"]:
        name  = feature["properties"][geo_key]
        match = canton_counts[canton_counts["canton"] == name]

        if not match.empty:
            jobs = float(match["jobs"].values[0])
            pct  = float(match["percentage"].values[0])
        else:
            # Canton exists in GeoJSON but has no postings under current filter
            jobs = 0.0
            pct  = 0.0

        feature["properties"]["jobs"]             = int(jobs)   # cast avoids "42.0" in tooltip
        feature["properties"]["percentage"]       = pct
        feature["properties"]["percentage_label"] = f"{pct:.1f}%"  # pre-formatted for tooltip

        # Normalise percentage to [0, 1] and look up the RGBA tuple from the colormap
        norm = pct / max_pct
        r, g, b, _ = cmap(norm)
        feature["properties"]["fill_color"] = [
            int(r * 255),
            int(g * 255),
            int(b * 255),
            210   # alpha: slight transparency so the base map remains visible
        ]

    # GeoJsonLayer reads fill_color directly from each feature's properties.
    # This is more reliable than pydeck expression strings, which don't support arithmetic.
    layer = pdk.Layer(
        "GeoJsonLayer",
        geojson_copy,
        pickable=True,       # enables hover tooltip
        stroked=True,
        filled=True,
        extruded=False,      # flat 2-D map (no 3-D extrusion)
        line_width_min_pixels=1,
        get_fill_color="properties.fill_color",  # [R, G, B, A] stored per feature
        get_line_color=[120, 120, 120, 255],      # neutral grey canton borders
    )

    # Centre the viewport over Luxembourg
    view_state = pdk.ViewState(
        latitude=49.8,
        longitude=6.1,
        zoom=8.5,
        pitch=0   # top-down view
    )

    # Tooltip shown on hover.
    # Uses {percentage_label} (a pre-formatted string) instead of {percentage:.1f}%
    # because pydeck does not evaluate Python format specs inside tooltip templates.
    tooltip = {
        "html": (
            "<b style='font-family:DM Sans,sans-serif'>{NAME_2}</b><br/>"
            "Jobs: <b>{jobs}</b><br/>"
            "Share: <b>{percentage_label}</b>"
        ),
        "style": {
            "backgroundColor": "white",
            "color": "#1a1a2e",
            "fontSize": "13px",
            "borderRadius": "8px",
            "padding": "8px 12px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.15)"
        }
    }

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style="light"   # light basemap prevents the dark-tile bleed-through issue
    )

    st.pydeck_chart(deck, use_container_width=True)

    # Colour scale legend — CSS gradient mirrors the YlOrRd colormap stops
    st.markdown(
        """
        <div class="map-legend">
            <span>Low</span>
            <div class="legend-gradient"></div>
            <span>High</span>
            &nbsp;· job share (%)
        </div>
        """,
        unsafe_allow_html=True
    )


# RIGHT PANEL — OCCUPATIONS + SKILLS
with col_right:

    # LUXEMBOURG-THEMED COLOR PALETTE
    # Derived from the Luxembourg flag: red (#EF3340), white (#FFFFFF), light blue (#00A3E0).
    # Extended with intermediate tones so both the donut and bar chart have enough
    # distinct colors for up to 10 segments/bars.
    LUX_DISCRETE = [
        "#EF3340",  # flag red
        "#00A3E0",  # flag light blue
        "#B71C2A",  # deep red
        "#0077A8",  # deep blue
        "#F47B7B",  # soft red
        "#66C8ED",  # soft blue
        "#C0392B",  # brick red
        "#1A8CB0",  # steel blue
        "#FF7F7F",  # light coral
        "#4DB8D8",  # pale cyan
    ]

    # Continuous scale for the skills bar chart: white → flag red,
    # gives a clean gradient that reads as "intensity" without clashing with the map.
    LUX_CONTINUOUS = [
        [0.0, "#FFFFFF"],
        [0.3, "#F47B7B"],
        [0.6, "#EF3340"],
        [1.0, "#B71C2A"],
    ]

    if selected_role == "All":
        # When no occupation filter is active, show the top-10 occupation breakdown
        # for the selected sector as a donut chart.
        # Uses the discrete Luxembourg palette so each slice gets a flag-inspired color.
        st.subheader("Top 10 Occupations")

        occupation_counts = (
            df_nace["occupation_label"]
            .value_counts()
            .head(10)
            .reset_index()
        )
        occupation_counts.columns = ["occupation", "count"]

        fig_pie = px.pie(
            occupation_counts,
            names="occupation",
            values="count",
            hole=0.45,   # donut style
            color_discrete_sequence=LUX_DISCRETE  # Luxembourg flag palette
        )
        fig_pie.update_layout(
            height=300,
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(font=dict(size=11))
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        # When a specific occupation is selected, show a simple focus label
        # (could be extended with occupation-specific KPIs or trend charts)
        st.subheader("Occupation Focus View")
        st.info(f"Filtered analysis for: **{selected_role}**")

    # Horizontal bar chart of the top 10 most-demanded skills.
    # The white-to-red continuous scale (LUX_CONTINUOUS) encodes frequency as intensity —
    # higher bars are deeper red, lower bars fade toward white.
    st.subheader("Top Skills")

    # Solid steel blue — clean, neutral, pleasant, and distinct from both the
    # map (YlOrRd) and the donut chart (Luxembourg red/blue discrete palette).
    # Minimum display width ensures even count=1 bars are always visible;
    # real counts shown as outside labels so the axis stays accurate.
    skill_values = top_skills.values
    MIN_DISPLAY = max(float(skill_values.max()), 0.5) * 0.05
    MIN_DISPLAY = max(MIN_DISPLAY, 0.5)
    display_values = [max(float(v), MIN_DISPLAY) for v in skill_values]

    fig_skills = px.bar(
        x=display_values,
        y=top_skills.index,
        orientation="h",
        text=skill_values,  # real count as label, not the padded display value
    )
    fig_skills.update_traces(
        marker_color="#4A90D9",       # pleasant steel blue
        marker_line_color="#2C6FAC",  # slightly darker border for definition
        marker_line_width=1,
        textposition="outside",
        textfont_size=11,
    )
    fig_skills.update_layout(
        height=320,
        xaxis_title=None,
        yaxis_title=None,
        xaxis=dict(range=[0, max(display_values) * 1.25]),  # headroom for outside labels
        coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_skills, use_container_width=True)


# DATASET INSPECTOR
# Collapsed by default; lets analysts quickly verify the rows behind the visuals
with st.expander("Inspect dataset"):
    st.dataframe(df_filtered)

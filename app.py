import streamlit as st
import pandas as pd
import plotly.express as px
import json
import os

from data_cleaning import load_and_clean

# Configure Streamlit page layout and global UI settings
st.set_page_config(
    page_title="Luxembourg Labour Market Intelligence",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS styling to improve dashboard readability and spacing
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-left: 3rem;
        padding-right: 3rem;
    }

    div[data-testid="metric-container"] {
        background-color: #161b22;
        border: 1px solid #2a2f3a;
        padding: 12px;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar section used to trigger the ETL (data cleaning) pipeline
st.sidebar.title("Data Pipeline")

run_etl = st.sidebar.button("Run Data Cleaning Pipeline")

# Execute ETL pipeline when user triggers the button
if run_etl:
    with st.spinner("Running ETL pipeline..."):
        load_and_clean(
            input_path="data/datasc-skills-vacancies-2025-2027.csv",
            output_path="data/cleaned_dataset.csv"
        )
    st.success("Dataset successfully updated")

# Display dataset availability status in the sidebar
st.sidebar.metric(
    "Dataset Ready",
    os.path.exists("data/cleaned_dataset.csv")
)

# Load cleaned dataset with caching to improve dashboard performance
@st.cache_data
def load_data():

    # Ensure dataset exists before loading
    if not os.path.exists("data/cleaned_dataset.csv"):
        st.warning("Cleaned dataset not found. Please run the pipeline first.")
        return pd.DataFrame()

    df = pd.read_csv("data/cleaned_dataset.csv")
    df.columns = df.columns.str.strip()

    return df


df = load_data()

# Stop execution if dataset is not available
if df.empty:
    st.stop()

# Load GeoJSON file containing Luxembourg canton boundaries for map visualization
with open("data/luxembourg_cantons.geojson") as f:
    geojson = json.load(f)

geo_key = "NAME_2"

# Dashboard header and description
st.title("Luxembourg Labour Market Intelligence Dashboard")
st.caption("Analysis of jobs, skills, occupations and regional distribution")

# Filters allowing dynamic exploration of NACE sectors and occupations
col1, col2 = st.columns(2)

with col1:
    nace_options = sorted(df["nace_label"].unique())
    selected_nace = st.selectbox("NACE Sector", nace_options)

# Filter dataset based on selected NACE sector
df_nace = df[df["nace_label"] == selected_nace]

with col2:
    role_options = ["All"] + sorted(df_nace["occupation_label"].unique())
    selected_role = st.selectbox("Occupation", role_options)

# Apply occupation filter if a specific role is selected
if selected_role == "All":
    df_filtered = df_nace.copy()
else:
    df_filtered = df_nace[df_nace["occupation_label"] == selected_role]

# Display high-level KPIs summarizing the filtered dataset
st.divider()

k1, k2, k3, k4 = st.columns(4)

k1.metric("Job Postings", len(df_filtered))
k2.metric("Unique Skills", df_filtered["skill"].nunique())
k3.metric("Occupations", df_nace["occupation_label"].nunique())
k4.metric("Active Cantons", df_filtered["canton"].nunique())

# Aggregate job postings by canton for geospatial visualization
canton_counts = (
    df_filtered["canton"]
    .value_counts()
    .reset_index()
)

canton_counts.columns = ["canton", "jobs"]

total_jobs = canton_counts["jobs"].sum()

# Convert job counts into percentages for choropleth scaling
canton_counts["percentage"] = (
    canton_counts["jobs"] / total_jobs * 100
    if total_jobs > 0 else 0
)

# Remove cantons with no job postings and sort by relevance
canton_counts = canton_counts[canton_counts["jobs"] > 0]
canton_counts = canton_counts.sort_values("percentage", ascending=False)

# Filter GeoJSON to include only cantons present in dataset
filtered_geojson = {
    "type": "FeatureCollection",
    "features": [
        feature for feature in geojson["features"]
        if feature["properties"][geo_key] in canton_counts["canton"].values
    ]
}

# Compute top skills for visualization
top_skills = df_filtered["skill"].value_counts().head(10)

# Define main layout with balanced split between map and analytics panels
st.divider()

col_map, col_right = st.columns([1, 1])

# Choropleth map showing regional job distribution across Luxembourg cantons
with col_map:

    st.subheader("Regional Job Distribution")

    fig_map = px.choropleth(
        canton_counts,
        geojson=filtered_geojson,
        locations="canton",
        featureidkey=f"properties.{geo_key}",
        color="percentage",
        hover_name="canton",
        hover_data={"jobs": True, "percentage": ":.2f"},
        color_continuous_scale="Blues"
    )

    # Remove map axes and fit view to available data
    fig_map.update_geos(
        visible=False,
        fitbounds="locations"
    )

    # Adjust map size and margins for cleaner UI presentation
    fig_map.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(fig_map, use_container_width=True)

# Right panel containing occupation and skills analytics
with col_right:

    # Show occupation distribution only when no specific occupation filter is applied
    if selected_role == "All":

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
            hole=0.45
        )

        fig_pie.update_layout(height=300)

        st.plotly_chart(fig_pie, use_container_width=True)

    else:
        st.subheader("Occupation Focus View")
        st.info(f"Filtered analysis for: {selected_role}")

    # Display top skills distribution as horizontal bar chart
    st.subheader("Top Skills")

    fig_skills = px.bar(
        x=top_skills.values,
        y=top_skills.index,
        orientation="h"
    )

    # Remove axis labels for cleaner dashboard presentation
    fig_skills.update_layout(
        height=300,
        xaxis_title=None,
        yaxis_title=None,
        margin=dict(l=10, r=10, t=10, b=10)
    )

    st.plotly_chart(fig_skills, use_container_width=True)

# Expandable section for raw dataset inspection and debugging
with st.expander("Inspect dataset"):
    st.dataframe(df_filtered)

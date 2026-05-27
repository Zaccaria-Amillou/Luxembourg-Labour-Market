# Luxembourg Labour Market Dashboard

An interactive Streamlit dashboard for analysing job vacancies in Luxembourg, with a full ETL pipeline, translation system for labour market taxonomies, and geospatial visualisation of employment distribution across cantons.

---

## 🚀 Project Overview

This project transforms raw labour market data into an analytical dashboard that enables exploration of:

- Regional job distribution across Luxembourg cantons
- Demand for skills and occupations
- Sectoral analysis using NACE classification
- Labour market concentration by geography

The system is built as a full **data pipeline + analytics application**, from raw CSV ingestion to interactive choropleth map and charts.

---

## 📁 Project Structure

```
├── app.py
├── build_mappings.py
├── data
│   ├── cleaned_dataset.csv
│   ├── datasc-skills-vacancies-2025-2027.csv
│   ├── gadm41_LUX_3.json
│   ├── luxembourg_cantons.geojson
│   ├── nace_mapping.json
│   └── occupation_mapping.json
├── data_cleaning.py
├── helpers
│   ├── check.py
│   ├── convert_json.py
│   ├── data_exploration.py
│   └── inspect_geodata.py
├── README.md
└── requirements.txt
```

---

## ⚙️ ETL Pipeline

The project follows a two-step ETL process:

### 1. Build Translation Mappings

Extracts unique categorical values and generates translation dictionaries.

```bash
python build_mappings.py
```

Outputs:
- `nace_mapping.json`
- `occupation_mapping.json`

---

### 2. Data Cleaning Pipeline

Processes the raw dataset into an analysis-ready format.

```bash
python data_cleaning.py
```

This step:
- Cleans missing and inconsistent values
- Normalises text fields
- Applies precomputed translations
- Produces `cleaned_dataset.csv`

The pipeline can also be triggered directly from the dashboard sidebar without leaving the browser.

---

## 📊 Streamlit Dashboard

Run the dashboard locally:

```bash
streamlit run app.py
```

### Features

- **Sidebar ETL trigger** — re-run the cleaning pipeline on demand and see a live dataset status indicator
- **Cascading filters** — NACE sector selection narrows the occupation dropdown to only relevant roles
- **KPI metrics row** — headline counts for job postings, unique skills, occupations, and active cantons, updated instantly on filter change
- **Choropleth map** — pydeck `GeoJsonLayer` with per-canton colour grading using the `YlOrRd` colormap; tooltip shows canton name, job count, and percentage share on hover
- **Colour scale legend** — inline Low → High gradient bar below the map matching the YlOrRd palette
- **Occupation donut chart** — top 10 occupations for the selected sector, coloured with a Luxembourg flag-inspired palette (red `#EF3340` / blue `#00A3E0`)
- **Top skills bar chart** — horizontal bars in steel blue (`#4A90D9`) with outside count labels and a minimum bar width so even single-posting skills remain visible
- **Dataset inspector** — collapsible raw data table for the current filter state

---

## 🗺️ Geospatial Layer

The dashboard integrates Luxembourg administrative boundaries using GeoJSON files:

- `luxembourg_cantons.geojson` — primary canton boundaries used by the choropleth
- `gadm41_LUX_3.json` — higher-resolution GADM source for reference

### Choropleth implementation notes

- Job-share percentages are normalised against the current filter's maximum, so the full colour range is always utilised
- Each GeoJSON feature receives a precomputed `[R, G, B, A]` `fill_color` property; pydeck reads this directly via `get_fill_color="properties.fill_color"` — more reliable than pydeck expression strings, which don't support arithmetic
- The cached GeoJSON is deep-copied on each rerun to prevent stale colour values accumulating across filter changes
- Tooltip values are pre-formatted in Python (`percentage_label = f"{pct:.1f}%"`) because pydeck tooltip templates do not evaluate Python format specs like `{value:.1f}`
- Cantons with zero postings under the current filter are filled with the lowest colour rather than disappearing, using a left-join against all features in the GeoJSON

---

## 🧠 Design Principles

### ETL Separation

The pipeline is designed to:
- Avoid runtime API calls during dashboard use
- Improve reproducibility across environments
- Ensure fast dashboard performance through pre-cleaned data

### Translation Strategy

Instead of translating row-by-row at runtime:
- Unique values are extracted once
- Translated and stored in mapping files
- Applied as a lookup during cleaning

This guarantees consistency, speed, and deterministic outputs.

### Colour Strategy

The dashboard uses three intentionally distinct palettes to avoid visual confusion between layers:

| Component | Palette | Rationale |
|---|---|---|
| Choropleth map | `YlOrRd` (matplotlib) | Continuous intensity scale for geographic data |
| Occupation donut | Luxembourg flag discrete (red + blue tones) | Categorical distinction, national identity |
| Skills bar chart | Solid steel blue `#4A90D9` | Clean, neutral, always visible regardless of data distribution |

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

### Core dependencies

- `streamlit` — dashboard framework
- `pandas` — data manipulation
- `pydeck` — WebGL-powered choropleth map
- `plotly` — interactive charts
- `matplotlib` — colormap computation for the choropleth
- `deep-translator` — translation of labour market taxonomy labels

---

## 🚀 Future Improvements

- Time-series analysis of job trends across quarters
- Multilingual dashboard (FR / EN toggle)
- Improved geospatial matching logic for edge-case canton names
- Deployment to Streamlit Cloud or Render
- Predictive modelling for job demand forecasting
- PowerBI integration for enterprise reporting

---

## 📄 License

This project is released under the **MIT License**, allowing free use, modification, and distribution for personal and commercial purposes with attribution.

You are free to:
- Use the code in personal or commercial projects
- Modify and adapt the pipeline
- Distribute copies or derivatives

Condition:
- Attribution to the original author is required

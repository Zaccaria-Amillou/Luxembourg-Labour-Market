# Luxembourg Labour Market Dashboard

An interactive Streamlit dashboard for analysing job vacancies in Luxembourg, with a full ETL pipeline, translation system for labour market taxonomies, and geospatial visualisation of employment distribution across cantons.

---

## 🚀 Project Overview

This project transforms raw labour market data into an analytical dashboard that enables exploration of:

- Regional job distribution across Luxembourg
- Demand for skills and occupations
- Sectoral analysis using NACE classification
- Labour market concentration by geography

The system is built as a full **data pipeline + analytics application**, from raw CSV ingestion to interactive dashboard.

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

Processes raw dataset into an analysis-ready format.

```bash
python data_cleaning.py
```

This step:
- Cleans missing and inconsistent values
- Normalises text fields
- Applies precomputed translations
- Produces `cleaned_dataset.csv`

---

## 📊 Streamlit Dashboard

Run the dashboard locally:

```bash
streamlit run app.py
```

### Features

- Interactive filtering by:
  - NACE sector
  - Occupation
- Choropleth map of Luxembourg cantons
- Job distribution by region
- Top skills analysis
- Occupation breakdown (pie chart)
- Dataset inspection tool

---

## 🗺️ Geospatial Layer

The dashboard integrates Luxembourg administrative boundaries using GeoJSON files:

- `luxembourg_cantons.geojson`
- `gadm41_LUX_3.json`

Enables:
- Canton-level aggregation
- Percentage-based choropleth visualisation
- Filtered spatial analysis

---

## 🧠 Design Principles

### ETL Separation
The pipeline is designed to:
- Avoid runtime API calls
- Improve reproducibility
- Ensure fast dashboard performance

### Translation Strategy
Instead of translating row-by-row:
- Unique values are extracted
- Translated once
- Stored in mapping files

This guarantees:
- Consistency
- Speed
- Deterministic outputs

---

## 📦 Installation

```bash
pip install -r requirements.txt
```

### Core dependencies:
- streamlit
- pandas
- plotly
- deep-translator

---

## 🚀 Future Improvements

- Time-series analysis of job trends
- Multilingual dashboard (FR / EN toggle)
- Improved geospatial matching logic
- Deployment (Streamlit Cloud / Render)
- Predictive modelling for job demand
- Integration of PowerBI for dashboard

---

## 📄 License

This project is released under the **MIT License**, allowing free use, modification, and distribution for personal and commercial purposes with attribution.

You are free to:
- Use the code in personal or commercial projects
- Modify and adapt the pipeline
- Distribute copies or derivatives

Condition:
- Attribution to the original author is required

---

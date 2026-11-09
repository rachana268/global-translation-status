import json
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from shapely.geometry import shape, mapping


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Global Bible Translation Project",
    layout="wide"
)


# --------------------------------------------------
# PAGE DESIGN
# --------------------------------------------------

st.markdown(
    """
    <style>
    .stApp { background-color: #02070D; }
    [data-testid="stHeader"] { background: transparent; }
    [data-testid="stMainBlockContainer"] {
        padding-top: 0.25rem;
        padding-left: 1.1rem;
        padding-right: 1.1rem;
        max-width: 100%;
    }
    h1, p, label { color: white !important; }
    .jp-header {
        display:flex; align-items:center; gap:16px;
        min-height:78px; padding:8px 30px;
        margin:0 -1.1rem 14px;
        background:linear-gradient(90deg,#03121c,#00101a);
        border-bottom:1px solid #00bfc5;
        color:#fff; white-space:nowrap; overflow:hidden;
    }
    .jp-globe-icon { color:#00e5e5; font-size:42px; line-height:1; }
    .jp-title { font-size:32px; font-weight:800; letter-spacing:-.5px; }
    .jp-header-divider { height:42px; width:1px; background:#00bfc5; margin:0 16px; flex-shrink:0; }
    .jp-subtitle { font-size:19px; color:#d6e1e8; overflow:hidden; text-overflow:ellipsis; }
    @media(max-width:1000px) {
      .jp-header { min-height:60px; padding:8px 15px; gap:8px; }
      .jp-title { font-size:22px; }
      .jp-globe-icon { font-size:30px; }
      .jp-subtitle { display:none; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="jp-header">
      <span class="jp-globe-icon">◎</span>
      <span class="jp-title">Global Bible Translation Project</span>
      <span class="jp-header-divider"></span>
      <span class="jp-subtitle">Explore countries, languages, people groups, and Bible translation progress.</span>
    </div>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# FILE PATHS
# --------------------------------------------------

geojson_path = Path("data/countries.geojson")
csv_path = Path("data/joshua_countries.csv")


# --------------------------------------------------
# LOAD JOSHUA PROJECT DATA
# --------------------------------------------------

if not csv_path.exists():
    st.error("Could not find data/joshua_countries.csv")
    st.stop()

try:
    country_df = pd.read_csv(csv_path, dtype=str)
    country_df.columns = country_df.columns.str.strip()
except Exception as error:
    st.error(f"Could not read the Joshua Project CSV: {error}")
    st.stop()

required_columns = ["Ctry", "ISO3", "PercentChristianity"]
missing_columns = [
    column for column in required_columns
    if column not in country_df.columns
]

if missing_columns:
    st.error("Missing required CSV columns: " + ", ".join(missing_columns))
    st.stop()

country_df["Ctry"] = country_df["Ctry"].fillna("").str.strip()
country_df["ISO3"] = (
    country_df["ISO3"].fillna("").str.strip().str.upper()
)

country_df = country_df[
    (country_df["Ctry"] != "") &
    (country_df["ISO3"] != "")
].copy()

country_df = country_df.drop_duplicates(subset=["ISO3"], keep="first")

if country_df.empty:
    st.error("No valid country records were found in the CSV.")
    st.stop()


# --------------------------------------------------
# LOAD GEOJSON
# --------------------------------------------------

if not geojson_path.exists():
    st.error("Could not find data/countries.geojson")
    st.stop()

try:
    with open(geojson_path, "r", encoding="utf-8") as file:
        geojson_data = json.load(file)
except Exception as error:
    st.error(f"Could not read the GeoJSON file: {error}")
    st.stop()

features = geojson_data.get("features", [])

if not features:
    st.error("The GeoJSON file contains no geographic features.")
    st.stop()


# --------------------------------------------------
# MATCH GEOJSON WITH JOSHUA PROJECT USING ISO3
# --------------------------------------------------

joshua_iso3_codes = set(country_df["ISO3"].tolist())

matched_features = []
matched_rows = []
country_centers = {}

SIMPLIFY_TOLERANCE = 0.04

for feature in features:
    properties = feature.get("properties", {})
    geojson_iso3 = str(
        properties.get("ISO3166-1-Alpha-3", "")
    ).strip().upper()

    if geojson_iso3 not in joshua_iso3_codes:
        continue

    try:
        original_geometry = shape(feature["geometry"])

        # Use a representative point from the largest land polygon.
        # This avoids averaging unevenly spaced coastline vertices and
        # avoids selecting an ocean point for countries with many islands.
        if original_geometry.geom_type == "MultiPolygon":
            main_polygon = max(original_geometry.geoms, key=lambda polygon: polygon.area)
        else:
            main_polygon = original_geometry

        center_point = main_polygon.representative_point()
        country_centers[geojson_iso3] = {
            "lon": float(center_point.x),
            "lat": float(center_point.y)
        }

        simplified_geometry = original_geometry.simplify(
            SIMPLIFY_TOLERANCE,
            preserve_topology=True
        )

        matched_features.append({
            "type": "Feature",
            "properties": properties,
            "geometry": mapping(simplified_geometry)
        })

        joshua_row = country_df[
            country_df["ISO3"] == geojson_iso3
        ].iloc[0]

        matched_rows.append(joshua_row.to_dict())

    except Exception:
        continue

if not matched_rows:
    st.error(
        "No countries in the Joshua Project dataset matched "
        "the GeoJSON ISO-3 codes."
    )
    st.stop()

matched_df = pd.DataFrame(matched_rows)
matched_df = matched_df.sort_values(
    "Ctry",
    key=lambda column: column.str.lower()
).reset_index(drop=True)


# --------------------------------------------------
# FIND CSV FIELDS (FIELD NAMES CAN VARY)
# --------------------------------------------------

def find_column(possible_names):
    normalized_columns = {
        column.lower().replace("_", "").replace(" ", ""): column
        for column in matched_df.columns
    }

    for name in possible_names:
        normalized_name = (
            name.lower().replace("_", "").replace(" ", "")
        )
        if normalized_name in normalized_columns:
            return normalized_columns[normalized_name]

    return None


population_column = find_column([
    "Population", "PopulationTotal", "Population2024", "Population2025"
])

language_count_column = find_column([
    "CntPrimaryLanguages", "CntLanguages", "LanguageCount", "Languages"
])

people_group_column = find_column([
    "CntPeoples", "PeopleGroups", "PeopleGroupCount"
])

major_language_column = find_column([
    "PrimaryLanguage", "MajorLanguage", "Language", "PrimaryLanguages"
])

translation_needed_column = find_column(["TranslationNeeded"])
translation_started_column = find_column(["TranslationStarted"])
translation_unspecified_column = find_column(["TranslationUnspecified"])
bible_portions_column = find_column(["BiblePortions"])
bible_new_testament_column = find_column(["BibleNewTestament"])
bible_complete_column = find_column(["BibleComplete"])


# --------------------------------------------------
# DATA FORMATTING
# --------------------------------------------------

def safe_value(row, column):
    if not column:
        return "—"

    value = row.get(column, "")

    if pd.isna(value):
        return "—"

    value = str(value).strip()

    if value == "" or value.lower() in ["nan", "none", "null"]:
        return "—"

    return value


def format_number(value):
    if value == "—":
        return value

    try:
        number = float(str(value).replace(",", ""))
        if number.is_integer():
            return f"{int(number):,}"
        return f"{number:,.1f}"
    except (ValueError, TypeError):
        return value


def get_bible_status(row):
    status_parts = []

    if safe_value(row, bible_complete_column) not in ["—", "0"]:
        status_parts.append("Bible complete")

    if safe_value(row, bible_new_testament_column) not in ["—", "0"]:
        status_parts.append("New Testament")

    if safe_value(row, bible_portions_column) not in ["—", "0"]:
        status_parts.append("Bible portions")

    if safe_value(row, translation_started_column) not in ["—", "0"]:
        status_parts.append("Translation started")

    if safe_value(row, translation_needed_column) not in ["—", "0"]:
        status_parts.append("Translation needed")

    if safe_value(row, translation_unspecified_column) not in ["—", "0"]:
        status_parts.append("Status unspecified")

    if not status_parts:
        return "No status information available"

    return " • ".join(status_parts)


# --------------------------------------------------
# PREPARE COUNTRY RECORDS
# --------------------------------------------------

country_records = []

for _, row in matched_df.iterrows():
    country_records.append({
        "name": str(row["Ctry"]),
        "iso3": str(row["ISO3"]).strip().upper(),
        "christianity": safe_value(row, "PercentChristianity"),
        "population": format_number(safe_value(row, population_column)),
        "language_count": format_number(safe_value(row, language_count_column)),
        "people_groups": format_number(safe_value(row, people_group_column)),
        "major_language": safe_value(row, major_language_column),
        "bible_status": get_bible_status(row),
        "translation_needed": safe_value(row, translation_needed_column),
        "translation_started": safe_value(row, translation_started_column),
        "translation_unspecified": safe_value(row, translation_unspecified_column),
        "bible_portions": safe_value(row, bible_portions_column),
        "bible_new_testament": safe_value(row, bible_new_testament_column),
        "bible_complete": safe_value(row, bible_complete_column)
    })


# --------------------------------------------------
# PREPARE SAFE JSON STRINGS
# --------------------------------------------------

filtered_geojson = {
    "type": "FeatureCollection",
    "features": matched_features
}

geojson_json = json.dumps(
    filtered_geojson,
    ensure_ascii=False
).replace("</", "<\\/")

country_records_json = json.dumps(
    country_records,
    ensure_ascii=False
).replace("</", "<\\/")

country_centers_json = json.dumps(
    country_centers,
    ensure_ascii=False
).replace("</", "<\\/")

country_count = len(country_records)


# --------------------------------------------------
# INTERACTIVE COMPONENT
# --------------------------------------------------
# This HTML is deliberately NOT a Python f-string.
# JSON values are inserted with replace() at the bottom,
# so JavaScript braces won't cause Python f-string syntax errors.

html_code = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>

<style>
* { box-sizing: border-box; }

html, body {
    margin: 0;
    padding: 0;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: #02070D;
    color: #FFFFFF;
    font-family: Arial, Helvetica, sans-serif;
}

 .dashboard {
    display: grid;
    grid-template-columns: 250px minmax(0, 1fr);
    gap: 14px;
    width: 100%;
    height: 100%;
    min-height: 0;
    max-height: 100%;
    overflow: hidden;
}

.country-panel {
    background: #071522;
    border: 1px solid #18303D;
    border-radius: 16px;
    padding: 14px;
    display: flex;
    flex-direction: column;
    min-height: 0;
    height: 100%;
    overflow: hidden;
}

.panel-heading {
    font-size: 22px;
    font-weight: 800;
    margin-bottom: 7px;
}

.panel-subheading {
    color: #91A5B4;
    font-size: 14px;
    margin-bottom: 12px;
}

.search-box {
    width: 100%;
    background: #0D202D;
    border: 1px solid #29404D;
    border-radius: 9px;
    color: #FFFFFF;
    padding: 12px;
    font-size: 16px;
    margin-bottom: 12px;
    outline: none;
}

.country-list {
    overflow-y: auto;
    overscroll-behavior: contain;
    flex: 1 1 0;
    min-height: 0;
    height: auto;
    padding-right: 5px;
}

.country-list::-webkit-scrollbar { width: 7px; }
.country-list::-webkit-scrollbar-track { background: #071522; }
.country-list::-webkit-scrollbar-thumb {
    background: #29404D;
    border-radius: 8px;
}

.country-item {
    padding: 12px 12px;
    margin-bottom: 5px;
    border-radius: 8px;
    color: #C6D4DF;
    cursor: pointer;
    font-size: 20px;
    line-height: 1.25;
    border: 1px solid transparent;
    transition: background 0.12s ease;
}

.country-item:hover {
    background: #14313D;
    color: #FFFFFF;
}

.country-item.active {
    background: #0D3038;
    border-color: #00D5D5;
    color: #FFFFFF;
    font-weight: 700;
}

 .main-panel {
    position: relative;
    display: grid;
    grid-template-columns: minmax(0, 58fr) minmax(300px, 42fr);
    grid-template-rows: 76px minmax(0, 1fr);
    column-gap: 12px;
    min-width: 0;
    min-height: 0;
    height: 100%;
    overflow: hidden;
}

.main-panel .country-header {
    grid-column: 1 / -1;
    grid-row: 1;
    margin-bottom: 8px;
}

.country-header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 14px;
    min-width: 0;
    min-height: 76px;
    padding: 10px 16px;
    background: #0D3038;
    border-radius: 16px;
}

.header-country { display: flex; align-items: center; gap: 12px; min-width: 0; }
.target-icon { width: 34px; height: 34px; flex-shrink: 0; }
.country-name {
    color: #FFFFFF; font-size: 26px; font-weight: 800;
    text-transform: uppercase; letter-spacing: .5px; overflow-wrap: anywhere;
}
.percent-circle { display: none; }

.globe-wrapper {
    position: relative;
    grid-column: 1;
    grid-row: 2;
    width: 100%;
    height: 100%;
    min-width: 0;
    min-height: 0;
    overflow: hidden;
    isolation: isolate;
}

#globe { position: absolute; inset: 0; width: 100%; height: 100%; }

 .main-panel .globe-wrapper { grid-column: 1; grid-row: 2; }

.info-overlay {
    display: flex;
    min-width: 0;
    min-height: 0;
    width: 100%;
    height: 100%;
    grid-column: 2;
    grid-row: 2;
    align-items: stretch;
    justify-content: stretch;
    padding: 0;
    background: transparent;
    pointer-events: none;
    overflow: hidden;
}

.info-overlay.open { display: flex; grid-column: 2; grid-row: 2; }

.info-card {
    position: relative;
    width: 100%;
    max-width: none;
    height: 100%;
    max-height: 100%;
    margin: 0;
    overflow-y: auto;
    background: linear-gradient(145deg, #0B1D2B, #06111B);
    border: 1px solid rgba(122, 218, 178, 0.62);
    border-radius: 16px;
    padding: 16px;
    box-shadow: 0 12px 44px rgba(0, 0, 0, 0.48), 0 0 22px rgba(101, 224, 173, 0.20);
    pointer-events: auto;
}

/* Tablet layout: retain the two-column country browser and compact main area. */
@media (max-width: 900px) and (min-width: 621px) {
    .dashboard {
        grid-template-columns: 210px minmax(0, 1fr);
        gap: 10px;
    }
    .main-panel {
        grid-template-columns: minmax(0, 1fr);
        grid-template-rows: 64px minmax(300px, 1fr) minmax(300px, auto);
        row-gap: 10px;
    }
    .main-panel .country-header { grid-column: 1; grid-row: 1; }
    .main-panel .globe-wrapper { grid-column: 1; grid-row: 2; min-height: 300px; }
    .main-panel .info-overlay.open { grid-column: 1; grid-row: 3; padding: 0; }
    .country-item { font-size: 15px; }
    .info-card { width: 100%; max-height: none; }
}

/* Phone layout: stack the country browser, globe and overview vertically. */
@media (max-width: 620px) {
    html, body {
        height: auto;
        min-height: 100%;
        overflow-x: hidden;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
    }
    .dashboard {
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        grid-template-rows: 290px auto;
        gap: 12px;
        width: 100%;
        height: auto;
        min-height: 0;
        max-height: none;
        overflow: visible;
        padding-bottom: 18px;
    }
    .country-panel {
        grid-row: 1;
        height: 290px;
        min-height: 290px;
        padding: 10px;
        border-radius: 12px;
    }
    .panel-heading { font-size: 17px; }
    .panel-subheading { font-size: 12px; margin-bottom: 8px; }
    .search-box { padding: 10px 12px; font-size: 16px; margin-bottom: 8px; }
    .country-list {
        flex: 1 1 auto;
        min-height: 0;
        height: auto;
        overflow-y: auto;
        -webkit-overflow-scrolling: touch;
        overscroll-behavior: contain;
    }
    .country-item { padding: 9px 10px; margin-bottom: 3px; font-size: 15px; }
    .main-panel {
        grid-row: 2;
        display: grid;
        grid-template-columns: minmax(0, 1fr);
        grid-template-rows: 58px 310px auto auto;
        row-gap: 10px;
        width: 100%;
        height: auto;
        min-height: 0;
        overflow: visible;
    }
    .main-panel .country-header { grid-column: 1; grid-row: 1; min-height: 58px; padding: 8px 12px; margin: 0; }
    .target-icon { width: 28px; height: 28px; }
    .country-name { font-size: 18px; }
    .main-panel .globe-wrapper {
        grid-column: 1;
        grid-row: 2;
        width: 100%;
        height: 310px;
        min-height: 310px;
        overflow: hidden;
    }
    #globe { position: absolute; inset: 0; width: 100%; height: 100%; }
    .main-panel .info-overlay,
    .main-panel .info-overlay.open {
        grid-column: 1;
        grid-row: 3;
        display: flex;
        position: relative;
        width: 100%;
        height: auto;
        min-height: 0;
        padding: 0;
        overflow: visible;
        align-items: stretch;
    }
    .info-card {
        width: 100%;
        max-width: none;
        height: auto;
        max-height: none;
        overflow: visible;
        padding: 12px;
        border-radius: 12px;
    }
    .global-overview { height: auto; min-height: 0; }
    .global-kpis { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; margin: 10px 0; }
    .global-kpi { min-height: 72px; padding: 10px; }
    .global-kpi-label { font-size: 11px; line-height: 1.3; }
    .global-kpi-value { font-size: 19px; }
    .global-panels { grid-template-columns: minmax(0, 1fr); gap: 10px; }
    .global-panel { padding: 11px; }
    .global-panel-title { font-size: 14px; }
    .need-chart-row { grid-template-columns: minmax(65px, 82px) minmax(0, 1fr) 38px; gap: 6px; font-size: 11px; }
    .need-chart-value { font-size: 11px; }
    .insight-shell { min-height: 155px; }
    .insight-text { font-size: 13px; }
    .info-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
    .info-cell {
        grid-template-columns: 1fr;
        grid-template-rows: auto auto auto;
        gap: 6px;
        min-height: 112px;
        padding: 11px;
        text-align: left;
    }
    .info-icon { grid-column: 1; grid-row: 1; font-size: 25px; }
    .info-label { font-size: 12px; line-height: 1.3; }
    .info-value { font-size: 20px; }
    .status-chart-panel { padding: 10px; }
    .status-chart-title { font-size: 14px; }
    .status-chart-legend { font-size: 11px; }
    .footer-note { font-size: 12px; line-height: 1.45; }
}

.info-close {
    position: absolute;
    top: 12px;
    right: 15px;
    border: 1px solid #365344;
    background: #10281B;
    color: #E7F4EA;
    border-radius: 9px;
    width: 38px;
    height: 38px;
    font-size: 24px;
    cursor: pointer;
}

.status-chart-panel {
    margin: 8px 0 0;
    width: 100%;
    flex: 0 0 auto;
    min-height: 0;
    background: linear-gradient(145deg, #0B1D2B, #06111B);
    border: 1px solid #00BFC5;
    border-radius: 16px;
    padding: 12px 14px;
    box-shadow: 0 10px 32px rgba(0, 0, 0, 0.3);
}
.status-chart-title {
    color: #EAF4EC;
    font-size: 16px;
    font-weight: 800;
    margin-bottom: 6px;
}
#statusChart { display: block; width: 100%; min-width: 0; overflow: hidden; }
#statusChart svg { display: block; width: 100% !important; max-width: none !important; margin: 0 !important; }
.status-chart-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 7px 14px;
    margin-top: 7px;
    color: #DCE8EF;
    font-size: 12px;
}
.legend-entry { display: flex; align-items: center; gap: 7px; }
.legend-swatch { width: 13px; height: 13px; border-radius: 3px; }

.global-overview {
    display: flex;
    flex-direction: column;
    height: 100%;
    min-height: 0;
}
.info-card.global-mode .info-close { display: none; }
.global-overview .global-panels {
    flex: 1 1 auto;
    min-height: 0;
    align-items: stretch;
}
.global-overview .global-panel {
    min-height: 0;
    height: 100%;
    overflow: hidden;
}
.global-overview .insight-shell { min-height: 0; }
.global-overview .footer-note { margin-top: auto; padding-top: 12px; }
.global-overview[hidden], .country-overview[hidden] { display: none !important; }
.global-kpis { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 14px 0; }
.global-kpi { min-width: 0; min-height: 78px; padding: 14px 16px; border: 1px solid #147B83; border-radius: 12px; background: linear-gradient(145deg, #0D2935, #071923); }
.global-kpi-label { color: #DCE8EF; font-size: 13px; margin-bottom: 6px; }
.global-kpi-value { color: #FFFFFF; font-size: 23px; font-weight: 800; overflow-wrap: anywhere; }
.global-panels { display: grid; grid-template-columns: minmax(0, 1fr); gap: 12px; }
.global-panel { min-width: 0; padding: 14px; border: 1px solid #147B83; border-radius: 12px; background: #071923; }
.global-panel-title { color: #EAF4EC; font-size: 16px; font-weight: 800; margin-bottom: 10px; }
.need-chart-row { display: grid; grid-template-columns: minmax(72px, 95px) minmax(0, 1fr) 44px; gap: 8px; align-items: center; min-height: 23px; margin: 6px 0; font-size: 12px; color: #DCE8EF; }
.need-chart-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.need-chart-track { height: 13px; background: #18303D; border-radius: 6px; overflow: hidden; }
.need-chart-bar { height: 100%; background: #00CFCF; border-radius: 5px; }
.need-chart-value { text-align: right; font-size: 12px; }
.insight-shell { min-height: 170px; display: flex; flex-direction: column; justify-content: space-between; }
.insight-heading { color: #00E5E5; font-size: 17px; font-weight: 800; margin-bottom: 10px; }
.insight-text { color: #DCE8EF; font-size: 14px; line-height: 1.6; }
.insight-controls { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 12px; }
.insight-button { border: 1px solid #147B83; background: #0D2935; color: #EAF4EC; border-radius: 7px; padding: 5px 9px; cursor: pointer; }
.insight-count { color: #91A5B4; font-size: 11px; }
@media (min-width: 901px) { .global-panels { grid-template-columns: repeat(2, minmax(0, 1fr)); } }

.info-title {
    color: #00E5E5;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 14px;
    letter-spacing: 0.3px;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.info-cell {
    display: grid;
    grid-template-columns: 52px minmax(0, 1fr);
    grid-template-rows: auto auto;
    align-items: center;
    gap: 5px 12px;

    min-width: 0;
    min-height: 112px;
    padding: 18px;

    text-align: left;
    background: linear-gradient(145deg, #0D2935, #071923);
    border: 1px solid #147B83;
    border-radius: 14px;
}

.info-icon {
    grid-column: 1;
    grid-row: 1 / 3;

    color: #00E5E5;
    font-size: 32px;
    line-height: 1;
    margin: 0;

    filter: drop-shadow(0 0 7px rgba(0, 229, 229, 0.2));
}
.info-label {
    color: #DCE8EF;
    font-size: 15px;
    margin-bottom: 0;
    text-transform: none;
    letter-spacing: 0;
}
.info-value {
    color: #FFFFFF;
    font-size: 24px;
    font-weight: 800;
    overflow-wrap: anywhere;
}
.status-row {
    border-top: 1px solid #18303D;
    margin-top: 18px;
    padding-top: 15px;
}

.status-label {
    color: #8FA6B7;
    font-size: 14px;
    margin-bottom: 7px;
    text-transform: uppercase;
}

.status-value {
    color: #DCE8EF;
    font-size: 16px;
    line-height: 1.6;
}

.footer-note {
    color: #8195A5;
    font-size: 14px;
    margin-top: 12px;
}

</style>
</head>

<body>
<div class="dashboard">

    <aside class="country-panel">
        <div class="panel-heading">Search by Country</div>
        <div class="panel-subheading">__COUNTRY_COUNT__ countries and territories</div>

        <input
            id="countrySearch"
            class="search-box"
            type="text"
            placeholder="Type a country name..."
        >

        <div id="countryList" class="country-list"></div>
    </aside>

    <main class="main-panel">

        <div class="country-header">
            <div class="header-country">

                <svg class="target-icon"
                     viewBox="0 0 40 40"
                     xmlns="http://www.w3.org/2000/svg">
                    <circle cx="20" cy="20" r="13"
                            fill="none"
                            stroke="#00F5F5"
                            stroke-width="2.5"/>
                    <circle cx="20" cy="20" r="5"
                            fill="none"
                            stroke="#00F5F5"
                            stroke-width="2.5"/>
                    <path d="M20 1 V9 M20 31 V39 M1 20 H9 M31 20 H39"
                          stroke="#00F5F5"
                          stroke-width="2.5"
                          stroke-linecap="round"/>
                </svg>

                <div id="countryName" class="country-name">SELECT A COUNTRY</div>
            </div>

                   </div>

        <div class="globe-wrapper">
            <div id="globe"></div>
        </div>

        <div id="infoOverlay" class="info-overlay" role="dialog" aria-modal="true" aria-label="Country overview">
        <section class="info-card global-mode">
            <button class="info-close" id="infoClose" aria-label="Close country overview">×</button>

            <div id="globalOverview" class="global-overview">
                <div class="info-title">GLOBAL OVERVIEW</div>
                <div class="global-kpis">
                    <div class="global-kpi"><div class="global-kpi-label">Population represented</div><div id="globalPopulation" class="global-kpi-value">—</div></div>
                    <div class="global-kpi"><div class="global-kpi-label">Primary language counts*</div><div id="globalLanguages" class="global-kpi-value">—</div></div>
                    <div class="global-kpi"><div class="global-kpi-label">People groups</div><div id="globalPeopleGroups" class="global-kpi-value">—</div></div>
                    <div class="global-kpi"><div class="global-kpi-label">Groups needing translation</div><div id="globalTranslationNeed" class="global-kpi-value">—</div></div>
                </div>
                <div class="global-panels">
                    <section class="global-panel">
                        <div class="global-panel-title">Top 10 Countries with Highest Translation Need</div>
                        <div id="translationNeedChart"></div>
                    </section>
                    <section class="global-panel insight-shell">
                        <div>
                            <div class="global-panel-title">Global Key Insights</div>
                            <div id="insightHeading" class="insight-heading">Loading insight…</div>
                            <div id="insightText" class="insight-text">Insights are calculated from the country dataset.</div>
                        </div>
                        <div class="insight-controls">
                            <button class="insight-button" id="insightPrev" aria-label="Previous insight">‹</button>
                            <span id="insightCount" class="insight-count">1 / 1 · changes every 20 seconds</span>
                            <button class="insight-button" id="insightNext" aria-label="Next insight">›</button>
                        </div>
                    </section>
                </div>
                <div class="footer-note">*Language counts are summed from country-level records and may not represent unique languages worldwide.</div>
            </div>

            <div id="countryOverview" class="country-overview" hidden>
            <div class="info-title">COUNTRY OVERVIEW</div>

            <div class="info-grid">
                <div class="info-cell">
                    <div class="info-icon">👥</div><div class="info-label">Total Population</div>
                    <div id="population" class="info-value">—</div>
                </div>

                <div class="info-cell">
                    <div class="info-icon">🌐</div><div class="info-label">Primary Languages</div>
                    <div id="languageCount" class="info-value">—</div>
                </div>

                <div class="info-cell">
                    <div class="info-icon">🧩</div><div class="info-label">People Groups</div>
                    <div id="peopleGroups" class="info-value">—</div>
                </div>

                <div class="info-cell">
                    <div class="info-icon">✝</div><div class="info-label">Christian Adherent Population</div>
                    <div id="christianity" class="info-value">—</div>
                </div>
            </div>

            <section class="status-chart-panel" aria-label="Bible translation status chart">
                <div class="status-chart-title">People Groups by Bible Translation Status</div>
                <div id="statusChart"></div>
                <div id="statusChartLegend" class="status-chart-legend"></div>
            </section>
            </div>

        </section>
        </div>

        <div class="footer-note">
            Hover to preview a country. Click a country to open its overview; click it again or close the card to return to the centered globe.
        </div>

    </main>
</div>

<script>
const geojson = __GEOJSON_DATA__;
const countries = __COUNTRY_DATA__;
const countryCenters = __COUNTRY_CENTERS__;

const countryByCode = {};
countries.forEach(country => {
    countryByCode[country.iso3] = country;
});

let selectedCode = null;
let hoveredCode = null;
let overviewHovered = false;

function displayValue(value) {
    if (
        value === null ||
        value === undefined ||
        value === "" ||
        value === "—"
    ) {
        return "—";
    }
    return value;
}

const statusDefinitions = [
    { key: "bible_complete", label: "Bible complete", color: "#31B36B" },
    { key: "bible_new_testament", label: "New Testament", color: "#2587E8" },
    { key: "bible_portions", label: "Bible portions", color: "#22B8C5" },
    { key: "translation_started", label: "Translation started", color: "#F2B21B" },
    { key: "translation_needed", label: "Translation needed", color: "#E85D59" },
    { key: "translation_unspecified", label: "Status unspecified", color: "#8C70D5" }
];

function numericCount(value) {
    if (value === null || value === undefined || value === "—" || value === "") return 0;
    const parsed = Number(String(value).replace(/,/g, "").trim());
    return Number.isFinite(parsed) && parsed > 0 ? parsed : 0;
}

function renderStatusChart(code) {
    const country = countryByCode[code];
    const chart = document.getElementById("statusChart");
    const legend = document.getElementById("statusChartLegend");
    if (!country || !chart || !legend) return;

    const statuses = statusDefinitions.map(item => ({
        ...item,
        count: numericCount(country[item.key])
    }));
    const total = statuses.reduce((sum, item) => sum + item.count, 0);
    // Use the actual panel width so the stacked bar spans the full chart area.
    const width = Math.max(300, Math.floor(chart.getBoundingClientRect().width || 300));
    const barHeight = 42;
    const height = 54;

    if (total <= 0) {
        chart.innerHTML = '<div style="color:#91A5B4;padding:18px 0">Translation status counts are not available for this country.</div>';
        legend.innerHTML = "";
        return;
    }

    let x = 0;
    let segments = "";
    statuses.forEach(item => {
        if (!item.count) return;
        const segmentWidth = width * item.count / total;
        const pct = (item.count / total * 100).toFixed(1);
        segments += `<rect x="${x}" y="5" width="${segmentWidth}" height="${barHeight}" fill="${item.color}"/>`;
        if (segmentWidth >= 58) {
            segments += `<text x="${x + segmentWidth/2}" y="23" text-anchor="middle" fill="#FFFFFF" font-size="18" font-weight="700">${item.count.toLocaleString()}</text>`;
            segments += `<text x="${x + segmentWidth/2}" y="39" text-anchor="middle" fill="#FFFFFF" font-size="13">${pct}%</text>`;
        }
        x += segmentWidth;
    });

    chart.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="People groups by Bible translation status; total ${total.toLocaleString()}" style="display:block;width:100%;max-width:none;height:66px;margin:0"><defs><clipPath id="statusBarClip"><rect x="0" y="6" width="${width}" height="${barHeight}" rx="10"/></clipPath></defs><g clip-path="url(#statusBarClip)">${segments}</g></svg><div style="color:#91A5B4;font-size:13px;margin-top:6px">Total people groups with status counts: ${total.toLocaleString()}</div>`;
    legend.innerHTML = statuses.filter(item => item.count > 0).map(item =>
        `<div class="legend-entry"><span class="legend-swatch" style="background:${item.color}"></span><span>${item.label}: <b>${item.count.toLocaleString()}</b></span></div>`
    ).join("");
}

let globeResizeFrame = null;
let lastGlobeWidth = 0;
let lastGlobeHeight = 0;

function resizeGlobeAfterLayoutChange(force = false) {
    // Resize only when the OUTER wrapper has genuinely changed dimensions.
    // Observing the wrapper avoids feedback from Plotly changing its own SVG size.
    if (globeResizeFrame !== null) cancelAnimationFrame(globeResizeFrame);
    globeResizeFrame = requestAnimationFrame(() => {
        globeResizeFrame = null;
        const wrapper = document.querySelector(".globe-wrapper");
        const globe = document.getElementById("globe");
        if (!wrapper || !globe || !globe.data || !globe.data.length) return;

        const width = Math.round(wrapper.clientWidth);
        const height = Math.round(wrapper.clientHeight);
        if (width < 2 || height < 2) return;

        // Ignore tiny 1px layout fluctuations that can cause repeated redraws.
        if (!force && Math.abs(width - lastGlobeWidth) < 2 && Math.abs(height - lastGlobeHeight) < 2) return;
        lastGlobeWidth = width;
        lastGlobeHeight = height;
        const fitScale = Math.min(1, (height / width) * 1.65);
        Plotly.relayout(globe, {
            width: width,
            height: height,
            "geo.domain.x": [0.04, 0.96],
            "geo.domain.y": [0.04, 0.96],
            "geo.projection.scale": fitScale
        });
    });
}

function openCountryOverview() {
    if (!selectedCode) return;
    document.querySelector(".info-card").classList.remove("global-mode");
    document.getElementById("globalOverview").hidden = true;
    document.getElementById("countryOverview").hidden = false;
    document.getElementById("infoOverlay").classList.add("open");
}
function closeCountryOverview() {
    document.querySelector(".info-card").classList.add("global-mode");
    document.getElementById("countryOverview").hidden = true;
    document.getElementById("globalOverview").hidden = false;
    document.getElementById("infoOverlay").classList.add("open");
    overviewHovered = false;
    document.getElementById("countryName").textContent = "SELECT A COUNTRY";
    selectedCode = null;
    hoveredCode = null;
    document.querySelectorAll(".country-item").forEach(item => item.classList.remove("active"));
    updateGlobeHighlight(null);
}

const overviewCard = document.querySelector(".info-card");
overviewCard.addEventListener("mouseenter", () => {
    overviewHovered = true;
});
overviewCard.addEventListener("mouseleave", () => {
    overviewHovered = false;
});

function parseMetric(value) {
    if (value === null || value === undefined || value === "—" || value === "") return null;
    const parsed = Number(String(value).replace(/,/g, "").replace(/%/g, "").trim());
    return Number.isFinite(parsed) ? parsed : null;
}

function formatMetric(value) {
    if (value === null || value === undefined || !Number.isFinite(value)) return "—";
    return Math.round(value).toLocaleString();
}

function renderGlobalOverview() {
    const populationSum = countries.reduce((sum, country) => sum + (parseMetric(country.population) || 0), 0);
    const languageSum = countries.reduce((sum, country) => sum + (parseMetric(country.language_count) || 0), 0);
    const peopleGroupSum = countries.reduce((sum, country) => sum + (parseMetric(country.people_groups) || 0), 0);
    const translationNeedSum = countries.reduce((sum, country) => sum + (parseMetric(country.translation_needed) || 0), 0);

    document.getElementById("globalPopulation").textContent = formatMetric(populationSum);
    document.getElementById("globalLanguages").textContent = formatMetric(languageSum);
    document.getElementById("globalPeopleGroups").textContent = formatMetric(peopleGroupSum);
    document.getElementById("globalTranslationNeed").textContent = formatMetric(translationNeedSum);

    const ranked = countries.map(country => ({
        name: country.name,
        count: parseMetric(country.translation_needed) || 0
    })).filter(country => country.count > 0).sort((a, b) => b.count - a.count).slice(0, 10);
    const chart = document.getElementById("translationNeedChart");
    if (!ranked.length) {
        chart.innerHTML = '<div class="insight-text">Translation-needed counts are not available in this dataset.</div>';
    } else {
        const maxCount = ranked[0].count;
        chart.innerHTML = ranked.map(country => `
            <div class="need-chart-row" title="${country.name}: ${formatMetric(country.count)}">
                <div class="need-chart-name">${country.name}</div>
                <div class="need-chart-track"><div class="need-chart-bar" style="width:${Math.max(1, country.count / maxCount * 100)}%"></div></div>
                <div class="need-chart-value">${formatMetric(country.count)}</div>
            </div>`).join("");
    }

    const populated = countries.map(country => ({ country, value: parseMetric(country.population) })).filter(item => item.value !== null);
    const grouped = countries.map(country => ({ country, value: parseMetric(country.people_groups) })).filter(item => item.value !== null);
    const needed = countries.map(country => ({ country, value: parseMetric(country.translation_needed) })).filter(item => item.value !== null);
    const started = countries.map(country => ({ country, value: parseMetric(country.translation_started) })).filter(item => item.value !== null);
    const complete = countries.map(country => ({ country, value: parseMetric(country.bible_complete) })).filter(item => item.value !== null);

    const insights = [];
    const topPopulation = populated.sort((a, b) => b.value - a.value)[0];
    const topGroups = grouped.sort((a, b) => b.value - a.value)[0];
    const topNeeded = needed.sort((a, b) => b.value - a.value)[0];
    const topStarted = started.sort((a, b) => b.value - a.value)[0];

    if (topPopulation) insights.push({ title: "Most Populated Country", text: `${topPopulation.country.name} has the largest recorded population in this country dataset (${formatMetric(topPopulation.value)}).` });
    if (topGroups) insights.push({ title: "Highest Number of People Groups", text: `${topGroups.country.name} has the highest recorded number of people groups (${formatMetric(topGroups.value)}).` });
    if (topNeeded) insights.push({ title: "Highest Translation Need", text: `${topNeeded.country.name} has the highest recorded translation-needed count (${formatMetric(topNeeded.value)} groups).` });
    if (topStarted) insights.push({ title: "Most Translation Started", text: `${topStarted.country.name} has the highest recorded number of groups with translation started (${formatMetric(topStarted.value)}).` });

    if (complete.length) {
        const zeroComplete = complete.filter(item => item.value === 0).map(item => item.country.name);
        if (zeroComplete.length) {
            const names = zeroComplete.slice(0, 5).join(", ");
            const more = zeroComplete.length > 5 ? ` and ${zeroComplete.length - 5} more` : "";
            insights.push({ title: "No Complete Bible Count Recorded", text: `${zeroComplete.length} countries have a recorded complete-Bible count of zero: ${names}${more}. This describes the dataset's records, not a claim that no Bible materials exist.` });
        }
    }

    if (!insights.length) insights.push({ title: "Global Key Insights", text: "The country dataset does not contain enough numeric values to generate these insights." });
    globalInsights = insights;
    insightIndex = 0;
    renderCurrentInsight();
}

let globalInsights = [];
let insightIndex = 0;
let insightTimer = null;

function renderCurrentInsight() {
    if (!globalInsights.length) return;
    const insight = globalInsights[insightIndex];
    document.getElementById("insightHeading").textContent = insight.title;
    document.getElementById("insightText").textContent = insight.text;
    document.getElementById("insightCount").textContent = `${insightIndex + 1} / ${globalInsights.length} · changes every 20 seconds`;
}

function moveInsight(direction) {
    if (!globalInsights.length) return;
    insightIndex = (insightIndex + direction + globalInsights.length) % globalInsights.length;
    renderCurrentInsight();
}

document.getElementById("insightPrev").addEventListener("click", () => moveInsight(-1));
document.getElementById("insightNext").addEventListener("click", () => moveInsight(1));
document.querySelector(".insight-shell").addEventListener("mouseenter", () => {
    if (insightTimer) clearInterval(insightTimer);
});
document.querySelector(".insight-shell").addEventListener("mouseleave", () => {
    if (insightTimer) clearInterval(insightTimer);
    insightTimer = setInterval(() => moveInsight(1), 20000);
});

function formatChristianityPercent(value) {
    if (value === "—" || value === null || value === undefined || value === "") return "—";
    // Source values may already include commas or a percent sign. Normalize before formatting.
    const normalized = String(value).trim().replace(/,/g, "").replace(/%/g, "");
    const numeric = Number(normalized);
    return Number.isFinite(numeric) ? `${numeric.toFixed(2)}%` : "—";
}

function setCountryInfo(code) {
    const country = countryByCode[code];
    if (!country) return;

    document.getElementById("countryName").textContent =
        country.name.toUpperCase();

    document.getElementById("population").textContent =
        displayValue(country.population);

    document.getElementById("languageCount").textContent =
        displayValue(country.language_count);

    document.getElementById("peopleGroups").textContent =
        displayValue(country.people_groups);

    document.getElementById("christianity").textContent =
        formatChristianityPercent(country.christianity);

    renderStatusChart(code);
}

function updateGlobeHighlight(code) {
    // Keep the existing Plotly trace intact. Updating the choropleth z-values
    // alone avoids Plotly restyle errors that can blank the globe.
    const zValues = countries.map(country => code && country.iso3 === code ? 1 : 0);
    const globe = document.getElementById("globe");
    if (!globe || !globe.data || !globe.data.length) return;
    Plotly.restyle(globe, { z: [zValues] }, [0]).catch(error => {
        console.error("Could not update country highlight:", error);
    });
}

function renderCountryList(filterText = "") {
    const list = document.getElementById("countryList");
    list.innerHTML = "";
    list.scrollTop = 0;

    const filteredCountries = countries.filter(country =>
        country.name.toLowerCase().includes(filterText.toLowerCase())
    );

    filteredCountries.forEach(country => {
        const item = document.createElement("div");
        item.className = "country-item";
        item.textContent = country.name;
        item.dataset.code = country.iso3;

        if (country.iso3 === selectedCode) {
            item.classList.add("active");
        }

        item.addEventListener("mouseenter", () => {
            hoveredCode = country.iso3;
            setCountryInfo(country.iso3);
            
            document.querySelectorAll(".country-item").forEach(otherItem => {
                otherItem.classList.toggle(
                    "active",
                    otherItem.dataset.code === selectedCode
                );
            });

            updateGlobeHighlight(country.iso3);
        });

        item.addEventListener("mouseleave", () => {
            hoveredCode = null;
            if (selectedCode) {
                setCountryInfo(selectedCode);
                openCountryOverview();
            } else if (!overviewHovered) {
                closeCountryOverview();
                document.getElementById("countryName").textContent = "SELECT A COUNTRY";
                document.getElementById("christianityPercent").textContent = "—";
            }

            document.querySelectorAll(".country-item").forEach(otherItem => {
                otherItem.classList.toggle(
                    "active",
                    otherItem.dataset.code === selectedCode
                );
            });

            updateGlobeHighlight(selectedCode);
        });

        item.addEventListener("click", () => {
            setActiveCountry(country.iso3, true);
        });

        list.appendChild(item);
    });
}

function setActiveCountry(code, scrollToItem = false, showOverview = true) {
    if (!countryByCode[code]) return;

    // Clicking the currently selected country toggles selection off.
    if (selectedCode === code) {
        selectedCode = null;
        hoveredCode = null;
        closeCountryOverview();
        document.getElementById("countryName").textContent = "SELECT A COUNTRY";
        document.getElementById("christianityPercent").textContent = "—";
        document.querySelectorAll(".country-item").forEach(item => item.classList.remove("active"));
        updateGlobeHighlight(null);
        return;
    }

    selectedCode = code;



    setCountryInfo(code);

    document.querySelectorAll(".country-item").forEach(item => {
        const isActive = item.dataset.code === code;
        item.classList.toggle("active", isActive);

        if (isActive && scrollToItem) {
            item.scrollIntoView({
                block: "nearest",
                behavior: "smooth"
            });
        }
    });

    updateGlobeHighlight(code);
    rotateCountryToFront(code);
    if (showOverview) openCountryOverview();
}

document.getElementById("infoClose").addEventListener("click", closeCountryOverview);
document.getElementById("infoOverlay").addEventListener("click", event => {
    if (event.target.id === "infoOverlay") closeCountryOverview();
});
document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeCountryOverview();
});

document.getElementById("countrySearch").addEventListener(
    "input",
    event => renderCountryList(event.target.value)
);


// --------------------------------------------------
// PLOTLY GLOBE
// --------------------------------------------------

// Rotate the selected country toward the front of the globe.
// Keep the projection centre fixed so the globe itself never pans off-screen.
// Use the selected geographic focus coordinates directly for Plotly rotation.
function rotateCountryToFront(code) {
    const center = countryCenters[code];
    const globe = document.getElementById("globe");

    if (!center || !globe || !globe.data || !globe.data.length) {
        console.warn("No country focus point or initialized globe found for:", code);
        return;
    }

    // Change only the projection rotation. Do not change geo.center, width,
    // height, or the globe wrapper dimensions during country selection.
    Plotly.relayout(globe, {
        "geo.projection.rotation.lon": center.lon,
        "geo.projection.rotation.lat": center.lat,
        "geo.projection.rotation.roll": 0
    }).catch(error => {
        console.error("Could not rotate globe to selected country:", error);
    });
}

const locations = countries.map(country => country.iso3);
const countryNames = countries.map(country => country.name);
const zValues = locations.map(code => code === selectedCode ? 1 : 0);

const trace = {
    type: "choropleth",
    geojson: geojson,
    locations: locations,
    z: zValues,
    featureidkey: "properties.ISO3166-1-Alpha-3",
    text: countryNames,
    customdata: locations,

    colorscale: [
        [0.0, "#174A2B"],
        [0.49, "#174A2B"],
        [0.5, "#800000"],
        [1.0, "#800000"]
    ],

    zmin: 0,
    zmax: 1,
    showscale: false,

    marker: {
        line: {
            color: "#B8DCC0",
            width: 0.8
        }
    },

    hovertemplate: "<b>%{text}</b><extra></extra>"
};

const layout = {
    autosize: true,

    margin: {
        l: 0,
        r: 0,
        t: 0,
        b: 0
    },

    paper_bgcolor: "rgba(2,7,13,0)",
    plot_bgcolor: "rgba(2,7,13,0)",

    font: {
        color: "#FFFFFF"
    },

    geo: {
        // Keep the sphere slightly inside the plotting area to prevent clipping.
        domain: {
            x: [0.04, 0.96],
            y: [0.04, 0.96]
        },

        projection: {
            type: "orthographic",
            scale: 0.95,
            rotation: {
                lon: 0,
                lat: 0,
                roll: 0
            }
        },

        showland: true,
        landcolor: "#12331F",

        showocean: true,
        oceancolor: "#04172A",

        showlakes: true,
        lakecolor: "#061522",

        showcountries: false,

        showcoastlines: true,
        coastlinecolor: "#8AB99A",
        coastlinewidth: 1.0,

        bgcolor: "rgba(2,7,13,0)"
    }
};

// Wait for Streamlit's iframe and CSS grid to finish their first layout pass.
// Give Plotly explicit dimensions so autosize does not oscillate during startup.
const globeWrapper = document.querySelector(".globe-wrapper");
const initialGlobeWidth = Math.max(320, Math.round(globeWrapper?.clientWidth || 800));
const initialGlobeHeight = Math.max(320, Math.round(globeWrapper?.clientHeight || 650));
layout.autosize = false;
layout.width = initialGlobeWidth;
layout.height = initialGlobeHeight;
lastGlobeWidth = initialGlobeWidth;
lastGlobeHeight = initialGlobeHeight;

requestAnimationFrame(() => requestAnimationFrame(() => Plotly.newPlot(
    "globe",
    [trace],
    layout,
    {
        displayModeBar: true,
        scrollZoom: true,
        responsive: false
    }
).then(() => {
    renderCountryList();
    renderGlobalOverview();
    document.querySelector(".info-card").classList.add("global-mode");
    document.getElementById("globalOverview").hidden = false;
    document.getElementById("countryOverview").hidden = true;
    document.getElementById("infoOverlay").classList.add("open");
    insightTimer = setInterval(() => moveInsight(1), 20000);

    // Globe rotation is disabled. The view stays fixed.

    // Let Streamlit's iframe grow to the full stacked mobile dashboard height.
    // This prevents the country overview and lower chart from being clipped.
    function notifyStreamlitFrameHeight() {
        const isPhone = window.matchMedia("(max-width: 620px)").matches;
        if (!isPhone) return;
        const contentHeight = Math.max(
            document.documentElement.scrollHeight,
            document.body.scrollHeight
        );
        window.parent.postMessage({
            isStreamlitMessage: true,
            type: "streamlit:setFrameHeight",
            height: contentHeight + 24
        }, "*");
    }
    requestAnimationFrame(() => requestAnimationFrame(notifyStreamlitFrameHeight));
    const pageHeightObserver = new ResizeObserver(notifyStreamlitFrameHeight);
    pageHeightObserver.observe(document.body);
    window.addEventListener("resize", notifyStreamlitFrameHeight);

    // Watch only the wrapper's real dimensions. Do not let Plotly's own redraws
    // trigger another resize, and do not resize the globe on every window event.
    const globeWrapperObserver = new ResizeObserver(() => {
        resizeGlobeAfterLayoutChange(false);
    });
    globeWrapperObserver.observe(document.querySelector(".globe-wrapper"));

    window.addEventListener("resize", () => {
        const code = selectedCode || hoveredCode || (countries.length ? countries[0].iso3 : null);
        if (code) renderStatusChart(code);
        resizeGlobeAfterLayoutChange(false);
    });

    document.getElementById("globe").on(
        "plotly_hover",
        eventData => {
            if (!eventData || !eventData.points || !eventData.points.length) {
                return;
            }

            const code = eventData.points[0].location;
            if (!countryByCode[code]) return;

            hoveredCode = code;
            setCountryInfo(code);
            

            document.querySelectorAll(".country-item").forEach(item => {
                const isActive = item.dataset.code === code;
                item.classList.toggle("active", isActive);

            });

            updateGlobeHighlight(code);
        }
    );

    document.getElementById("globe").on(
        "plotly_unhover",
        () => {
            hoveredCode = null;
          if (selectedCode) {
    setCountryInfo(selectedCode);
} else if (!overviewHovered) {
                closeCountryOverview();
                document.getElementById("countryName").textContent = "SELECT A COUNTRY";
                document.getElementById("christianityPercent").textContent = "—";
            }

            document.querySelectorAll(".country-item").forEach(item => {
                item.classList.toggle(
                    "active",
                    item.dataset.code === selectedCode
                );
            });

            updateGlobeHighlight(selectedCode);
        }
    );

    document.getElementById("globe").on(
        "plotly_click",
        eventData => {
            if (!eventData || !eventData.points || !eventData.points.length) {
                return;
            }

            const code = eventData.points[0].location;
            setActiveCountry(code, true);
        }
    );
})));
</script>

</body>
</html>
"""

# Inject serialized data without Python f-string parsing of JavaScript braces.
html_code = (
    html_code
    .replace("__GEOJSON_DATA__", geojson_json)
    .replace("__COUNTRY_DATA__", country_records_json)
    .replace("__COUNTRY_CENTERS__", country_centers_json)
    .replace("__COUNTRY_COUNT__", str(country_count))
)


# --------------------------------------------------
# DISPLAY COMPONENT
# --------------------------------------------------

components.html(
    html_code,
    height=900,
    scrolling=True
)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------



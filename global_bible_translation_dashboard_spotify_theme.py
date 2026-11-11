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
    /* Custom navigation buttons: no native radio indicators. */
    .st-key-gbtp-top-nav [data-testid="stHorizontalBlock"] {
        gap: 8px;
        align-items: center;
        flex-wrap: nowrap;
    }
    .st-key-gbtp-top-nav [data-testid="stButton"] > button {
        width: 100%;
        min-height: 42px;
        padding: 8px 13px;
        border: 1px solid #28505D;
        border-radius: 12px;
        background: linear-gradient(145deg,#0B1D2B,#06111B);
        color: #DCE8EF;
        font-weight: 700;
        white-space: nowrap;
        transition: all .18s ease;
    }
    .st-key-gbtp-top-nav [data-testid="stButton"] > button:hover {
        border-color: #00E5E5;
        color: #FFFFFF;
        background: linear-gradient(145deg,#0D3038,#08232D);
    }
    .st-key-gbtp-top-nav [data-testid="stButton"] > button[kind="primary"] {
        border: 1px solid #00E5E5;
        color: #FFFFFF;
        background: linear-gradient(145deg,#07343B,#06232D);
        box-shadow: 0 0 9px rgba(0,229,229,.65),
                    inset 0 0 10px rgba(0,229,229,.12);
    }
    @media(max-width:1000px) {
        .st-key-gbtp-top-nav [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
        }
    }
    @media(max-width:1000px) {
      .jp-header { min-height:60px; padding:8px 15px; gap:8px; }
      .jp-title { font-size:22px; }
      .jp-globe-icon { font-size:30px; }
      .jp-subtitle { display:none; }
      .gbtp-top-nav [data-testid="stRadio"] > div { justify-content:flex-start; flex-wrap:wrap; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

header_col, nav_col = st.columns([3.2, 1.8], vertical_alignment="center")
with header_col:
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
# PROJECT OVERVIEW NAVIGATION (ADDITIVE FEATURE)
# --------------------------------------------------

# Additive navigation only: the existing Global Explorer code below is preserved.
st.markdown(
    '''
    <style>
    .gbtp-overview-shell {
        color: #EAF4EC;
        background: linear-gradient(145deg, #071923, #020D16);
        border: 1px solid #147B83;
        border-radius: 18px;
        padding: clamp(16px, 3vw, 30px);
        margin: 8px 0 18px;
    }
    .gbtp-overview-eyebrow {
        color: #00E5E5; font-size: 12px; font-weight: 800;
        letter-spacing: 2px; margin-bottom: 8px;
    }
    .gbtp-overview-title {
        color: #FFFFFF; font-size: clamp(25px, 4vw, 38px);
        line-height: 1.15; font-weight: 800; margin: 0 0 8px;
    }
    .gbtp-overview-subtitle {
        color: #B9CBD5; font-size: clamp(14px, 2vw, 17px);
        line-height: 1.55; margin: 0;
    }
    .gbtp-overview-grid {
        display: grid; grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 16px; margin: 18px 0 8px;
    }
    .gbtp-overview-card {
        min-width: 0; min-height: 180px;
        padding: clamp(16px, 2.4vw, 24px);
        border: 1px solid #147B83; border-radius: 15px;
        background: linear-gradient(145deg, #0D2935, #071923);
        box-shadow: 0 8px 24px rgba(0,0,0,.18);
    }
    .gbtp-overview-card-number {
        color: #00E5E5; font-size: 12px; font-weight: 800;
        letter-spacing: 1.5px; margin-bottom: 12px;
    }
    .gbtp-overview-card-title {
        color: #FFFFFF; font-size: clamp(17px, 2.2vw, 21px);
        font-weight: 800; line-height: 1.3; margin-bottom: 9px;
    }
    .gbtp-overview-card-text {
        color: #C6D4DF; font-size: clamp(13px, 1.7vw, 15px);
        line-height: 1.6;
    }
    .gbtp-overview-footnote {
        color: #91A5B4; font-size: 12px;
        text-align: center; margin-top: 18px;
    }
    @media (max-width: 700px) {
        .gbtp-overview-grid { grid-template-columns: minmax(0, 1fr); gap: 11px; }
        .gbtp-overview-card { min-height: 0; padding: 17px; }
        .gbtp-overview-shell { padding: 16px; border-radius: 13px; }
    }
    </style>
    ''',
    unsafe_allow_html=True
)

if "gbtp_main_view" not in st.session_state:
    st.session_state["gbtp_main_view"] = "🌐  Global Explorer"
if "gbtp_overview_page" not in st.session_state:
    st.session_state["gbtp_overview_page"] = 1

with nav_col:
    with st.container(key="gbtp-top-nav"):
        global_col, overview_col = st.columns(2, gap="small")
        with global_col:
            if st.button(
                "🌐  Global Explorer",
                key="gbtp_nav_global",
                type="primary" if st.session_state["gbtp_main_view"] == "🌐  Global Explorer" else "secondary",
                use_container_width=True
            ):
                st.session_state["gbtp_main_view"] = "🌐  Global Explorer"
                st.rerun()
        with overview_col:
            if st.button(
                "📖  Project Overview",
                key="gbtp_nav_overview",
                type="primary" if st.session_state["gbtp_main_view"] == "📖  Project Overview" else "secondary",
                use_container_width=True
            ):
                st.session_state["gbtp_main_view"] = "📖  Project Overview"
                st.rerun()

if st.session_state["gbtp_main_view"] == "📖  Project Overview":
    overview_pages = {
        1: {
            "eyebrow": "PROJECT FOUNDATION",
            "heading": "Understanding the Project",
            "subtitle": "Purpose, challenge, objectives and information sources behind the Global Bible Translation Project.",
            "cards": [
                ("01", "Project Overview",
                 "An interactive data analytics dashboard for exploring global people groups, languages, populations and available Bible translation information."),
                ("02", "Problem Statement",
                 "Relevant information is distributed across country pages and people-group profiles. Finding, compiling and comparing it manually can be time-consuming."),
                ("03", "Project Objectives",
                 "Consolidate relevant information, simplify geographical exploration, understand language communities and make translation-status indicators easier to analyse."),
                ("04", "Data Sources",
                 "Joshua Project is the primary source being explored, including its country information, people-group profiles, definitions and available API data."),
            ],
        },
        2: {
            "eyebrow": "TECHNOLOGY & IMPLEMENTATION",
            "heading": "How the Project Is Built",
            "subtitle": "The tools, workflow, current dashboard capabilities and opportunities for future development.",
            "cards": [
                ("05", "Technology Stack",
                 "Python for application logic and data processing; Streamlit for the dashboard; Plotly for geographical visualisation; HTML, CSS and JavaScript for interface elements and interactions; JSON for structured API data."),
                ("06", "Project Workflow",
                 "Source exploration → Data extraction → Data cleaning → Data transformation → Dashboard integration → Visualisation → Testing."),
                ("07", "Features & Scope",
                 "The dashboard brings together an interactive world globe, country navigation, country-level indicators, people-group information, language associations and available Bible translation status."),
                ("08", "Future Vision",
                 "Potential extensions include advanced filters, country comparisons, automated data updates, AI-assisted insights and analytical support for identifying areas for further research."),
            ],
        },
    }

    page_number = st.session_state["gbtp_overview_page"]
    page = overview_pages[page_number]
    cards_html = "".join(
        f'''
        <section class="gbtp-overview-card">
            <div class="gbtp-overview-card-number">SECTION {number}</div>
            <div class="gbtp-overview-card-title">{title}</div>
            <div class="gbtp-overview-card-text">{description}</div>
        </section>
        '''
        for number, title, description in page["cards"]
    )

    st.markdown(
        f'''
        <div class="gbtp-overview-shell">
            <div class="gbtp-overview-eyebrow">{page["eyebrow"]}</div>
            <div class="gbtp-overview-title">{page["heading"]}</div>
            <p class="gbtp-overview-subtitle">{page["subtitle"]}</p>
            <div class="gbtp-overview-grid">{cards_html}</div>
            <div class="gbtp-overview-footnote">
                GLOBAL BIBLE TRANSLATION PROJECT · PAGE {page_number} OF 2
            </div>
        </div>
        ''',
        unsafe_allow_html=True
    )

    previous_col, page_col, next_col = st.columns([1, 2, 1])
    with previous_col:
        if st.button("← Previous", disabled=(page_number == 1),
                     key="gbtp_overview_previous", use_container_width=True):
            st.session_state["gbtp_overview_page"] = max(1, page_number - 1)
            st.rerun()
    with page_col:
        st.caption(f"Page {page_number} of 2 · Four sections per page")
    with next_col:
        if st.button("Next →", disabled=(page_number == 2),
                     key="gbtp_overview_next", use_container_width=True):
            st.session_state["gbtp_overview_page"] = min(2, page_number + 1)
            st.rerun()

    st.info("Select **Global Explorer** above to open the existing interactive globe dashboard.")
    st.stop()

# --------------------------------------------------
# END ADDITIVE PROJECT OVERVIEW FEATURE
# --------------------------------------------------


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
religion_primary_column = find_column(["ReligionPrimary", "PrimaryReligion"])
official_language_column = find_column(["OfficialLang", "OfficialLanguage"])


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
        "region": safe_value(row, find_column(["RegionName"])),
        "christianity": safe_value(row, "PercentChristianity"),
        "religion_primary": safe_value(row, religion_primary_column),
        "official_language": safe_value(row, official_language_column),
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

# Keep every country in alphabetical order for both desktop and mobile selectors.
country_records.sort(key=lambda country: country["name"].casefold())

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
    overflow: visible;
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
    display: flex;
    flex-direction: column;
    gap: 10px;
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
        grid-template-rows: 154px auto;
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
        height: 154px;
        min-height: 154px;
        padding: 9px 10px;
        border-radius: 12px;
        gap: 0;
    }
    .panel-heading { font-size: 16px; margin-bottom: 3px; }
    .panel-subheading { font-size: 11px; margin-bottom: 6px; }
    .search-box { padding: 8px 10px; font-size: 16px; margin-bottom: 7px; flex: 0 0 auto; }
    .country-list {
        display: flex;
        flex: 0 0 42px;
        flex-direction: row;
        align-items: stretch;
        gap: 7px;
        min-width: 0;
        min-height: 42px;
        width: 100%;
        height: 42px;
        padding: 0 0 5px;
        overflow-x: auto;
        overflow-y: hidden;
        white-space: nowrap;
        -webkit-overflow-scrolling: touch;
        overscroll-behavior-x: contain;
        scrollbar-width: thin;
        scrollbar-color: #29404D #071522;
    }
    .country-list::-webkit-scrollbar { width: auto; height: 5px; }
    .country-item {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex: 0 0 auto;
        min-height: 34px;
        padding: 7px 12px;
        margin: 0;
        border-radius: 18px;
        font-size: 13px;
        line-height: 1;
    }
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
    margin-bottom: 4px;
}
.status-chart-subtitle { color:#91A5B4; font-size:11px; margin-bottom:8px; }
.chart-note { color:#718A98; font-size:10px; line-height:1.35; margin-top:5px; }
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

.global-overview,
.country-overview {
    display: flex;
    flex-direction: column;
    flex: 0 0 auto;
    min-height: 0;
}
.global-overview[hidden],
.country-overview[hidden] { display: none !important; }
.info-card.global-mode .info-close { display: none; }

.global-overview .global-panels {
    display: block;
    flex: 0 0 auto;
    min-height: 0;
}
.global-overview .footer-note { margin-top: 10px; padding-top: 8px; }
.global-kpis { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; margin: 12px 0; }
.global-kpi { min-width: 0; min-height: 70px; padding: 12px 14px; border: 1px solid #147B83; border-radius: 12px; background: linear-gradient(145deg, #0D2935, #071923); }
.global-kpi-label { color: #DCE8EF; font-size: 13px; margin-bottom: 6px; }
.global-kpi-value { color: #FFFFFF; font-size: 23px; font-weight: 800; overflow-wrap: anywhere; }

.chatbot-panel {
    position: relative;
    display: flex;
    flex-direction: column;
    width: 100%;
    height: auto !important;
    min-height: max-content;
    flex: 0 0 auto;
    flex-shrink: 0;
    box-sizing: border-box;
    overflow: visible;
    align-self: stretch;
    padding: 14px 14px 16px;
    margin-bottom: 2px;
    border: 1px solid #147B83;
    border-radius: 14px;
    background: linear-gradient(145deg, #071923, #06111B);
}
.chatbot-heading {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    margin-bottom: 5px;
}
.chatbot-title { color: #EAF4EC; font-size: 16px; font-weight: 800; }
.chatbot-status {
    color: #A8D8B8; font-size: 10px; letter-spacing: .5px;
    border: 1px solid #286348; border-radius: 20px; padding: 4px 8px;
    white-space: nowrap;
}
.chatbot-description { color: #91A5B4; font-size: 11px; line-height: 1.45; margin-bottom: 10px; }
.chat-messages {
    flex: 0 0 auto;
    min-height: 110px;
    max-height: 220px;
    overflow-y: auto;
    overscroll-behavior: contain;
    padding: 9px;
    border: 1px solid #18303D;
    border-radius: 10px;
    background: rgba(2, 7, 13, .48);
    scrollbar-width: thin;
    scrollbar-color: #315565 #071522;
}
.chat-messages::-webkit-scrollbar { width: 6px; }
.chat-messages::-webkit-scrollbar-thumb { background: #315565; border-radius: 8px; }
.chat-message { max-width: 94%; margin: 0 0 10px; padding: 9px 11px; border-radius: 11px; font-size: 12px; line-height: 1.55; white-space: pre-wrap; overflow-wrap: anywhere; }
.chat-message.assistant { margin-right: auto; background: #102B35; border: 1px solid #1B4D56; color: #E1EDF0; }
.chat-message.user { margin-left: auto; background: #173D4A; border: 1px solid #247080; color: #FFFFFF; }
.chat-message-label { display: block; color: #78D8D5; font-size: 10px; font-weight: 800; margin-bottom: 3px; }
.chat-answer-table-wrap { width:100%; overflow-x:auto; margin:8px 0; }
.chat-answer-table { width:100%; border-collapse:collapse; min-width:520px; color:#E1EDF0; font-size:11px; }
.chat-answer-table th { background:#123742; color:#7FE4E2; text-align:left; font-weight:800; padding:8px 9px; border:1px solid #28606B; }
.chat-answer-table td { padding:7px 9px; border:1px solid #244653; vertical-align:top; }
.chat-answer-table tr:nth-child(even) td { background:rgba(18,55,66,.42); }
.question-picker { position: relative; z-index: 30; margin: 8px 0 9px; }
.question-picker-label { display:block; color:#91A5B4; font-size:10px; font-weight:700; margin:0 0 5px 2px; }
.question-picker-row { display:flex; gap:7px; align-items:stretch; width:100%; min-width:0; }
.question-dropdown { position:relative; flex:1 1 0; min-width:0; width:0; }
.question-picker-select {
    display:flex;
    align-items:center;
    justify-content:space-between;
    gap:10px;
    flex:1 1 auto;
    min-width:0;
    width:100%;
    box-sizing:border-box;
    color:#DCE8EF;
    background:#0D202D;
    border:1px solid #28606B;
    border-radius:9px;
    padding:9px 10px;
    font-size:14px;
    line-height:1.3;
    text-align:left;
    outline:none;
    cursor:pointer;
}
.question-picker-select:focus { border-color:#00D5D5; }
.question-dropdown-trigger { min-height:40px; }
.question-dropdown-trigger #questionDropdownValue {
    display:block;
    min-width:0;
    overflow:hidden;
    white-space:nowrap;
    text-overflow:ellipsis;
}
.question-dropdown-chevron { flex:0 0 auto; font-size:18px; line-height:1; color:#DCE8EF; }
.question-dropdown-menu {
    position:absolute;
    left:0;
    right:0;
    bottom:calc(100% + 6px);
    width:100%;
    max-width:100%;
    max-height:252px;
    overflow-y:auto;
    overflow-x:hidden;
    box-sizing:border-box;
    border:1px solid #28606B;
    border-radius:10px;
    background:#0D202D;
    box-shadow:0 12px 28px rgba(0,0,0,.55);
    z-index:1000;
    scrollbar-width:thin;
    scrollbar-color:#315565 #071522;
}
.question-dropdown-menu[hidden] { display:none !important; }
.question-dropdown-group-label {
    position:sticky;
    top:0;
    z-index:1;
    padding:7px 10px;
    color:#00E5E5;
    background:#071923;
    font-size:11px;
    font-weight:800;
    letter-spacing:.25px;
}
.question-dropdown-option {
    display:block;
    width:100%;
    box-sizing:border-box;
    padding:8px 10px;
    border:0;
    border-radius:0;
    background:#0D202D;
    color:#EAF4EC;
    font-size:12px;
    line-height:1.35;
    text-align:left;
    white-space:normal;
    overflow-wrap:anywhere;
    cursor:pointer;
}
.question-dropdown-option:hover,
.question-dropdown-option:focus {
    background:#16404A;
    color:#FFFFFF;
    outline:none;
}
.question-dropdown-option[aria-selected="true"] {
    background:#123742;
    color:#FFFFFF;
}
.question-ask { flex:0 0 auto; border:1px solid #16828A; border-radius:9px; background:#0D5962; color:#fff; padding:0 12px; font-size:14px; font-weight:700; cursor:pointer; }
.question-ask:hover { background:#11717B; }
.chat-input-row { display: flex; gap: 7px; align-items: stretch; margin-top: 2px; }
.chat-input {
    flex: 1 1 auto; min-width: 0; background: #0D202D; border: 1px solid #29404D;
    border-radius: 9px; color: #FFFFFF; padding: 10px; font-size: 14px; outline: none;
}
.chat-input:focus { border-color: #00BFC5; }
.chat-send {
    flex: 0 0 auto; border: 1px solid #16828A; border-radius: 9px;
    background: #0D5962; color: white; padding: 0 13px; font-weight: 700; cursor: pointer;
}
.chat-send:hover { background: #11717B; }
.chat-disclaimer { color: #718A98; font-size: 10px; line-height: 1.4; margin-top: 7px; }
.chatbot-panel > * { position: relative; z-index: 1; }
.chatbot-panel::after { content: none; }
@media (max-width: 620px) {
    .global-kpis { gap: 8px; margin: 9px 0; }
    .global-kpi { min-height: 66px; padding: 9px; }
    .global-kpi-label { font-size: 11px; }
    .global-kpi-value { font-size: 19px; }
    .chatbot-panel { min-height: 0; padding: 11px; }
    .chat-messages { min-height: 110px; max-height: 220px; }
    .question-dropdown-menu { max-height: 252px; }
}


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



/* --------------------------------------------------
   PROFESSIONAL DARK / TEAL UI THEME
   Visual-only overrides: preserve existing layout and interactions.
-------------------------------------------------- */
:root {
    --ui-bg: #03090D;
    --ui-panel: #07151B;
    --ui-panel-2: #0A2028;
    --ui-panel-3: #0D2A33;
    --ui-border: #17616B;
    --ui-border-bright: #20D9D2;
    --ui-cyan: #22E6DF;
    --ui-cyan-soft: #8CEBE6;
    --ui-text: #F1F7F8;
    --ui-muted: #9BB3BB;
    --ui-gold: #F2B544;
    --ui-gold-deep: #A87518;
    --ui-purple: #B77CE8;
}

html, body {
    background: radial-gradient(ellipse at 50% 35%, #071820 0%, #03090D 68%, #020609 100%) !important;
    color: var(--ui-text) !important;
}

.dashboard {
    background: transparent;
    gap: 14px;
}

.country-panel {
    background: linear-gradient(160deg, rgba(8,29,36,.98), rgba(3,13,18,.99)) !important;
    border: 1px solid rgba(32,217,210,.42) !important;
    border-radius: 18px !important;
    box-shadow: 0 12px 36px rgba(0,0,0,.30), inset 0 1px 0 rgba(255,255,255,.035);
    padding: 16px !important;
}

.panel-heading {
    color: #F4FAFB !important;
    letter-spacing: -.25px;
    font-size: 21px !important;
}
.panel-subheading { color: var(--ui-muted) !important; }

.search-box {
    background: rgba(10,35,43,.92) !important;
    border: 1px solid #28616A !important;
    border-radius: 11px !important;
    color: var(--ui-text) !important;
    box-shadow: inset 0 1px 5px rgba(0,0,0,.24);
}
.search-box:focus {
    border-color: var(--ui-cyan) !important;
    box-shadow: 0 0 0 2px rgba(34,230,223,.12), 0 0 16px rgba(34,230,223,.10);
}

.country-list::-webkit-scrollbar-track { background: #06141A !important; }
.country-list::-webkit-scrollbar-thumb { background: #24616A !important; }
.country-item {
    color: #D7E5E8 !important;
    border: 1px solid transparent !important;
    border-radius: 10px !important;
    transition: background .16s ease, border-color .16s ease, box-shadow .16s ease;
}
.country-item:hover {
    background: linear-gradient(90deg, rgba(16,75,83,.72), rgba(9,43,52,.72)) !important;
    border-color: rgba(32,217,210,.30) !important;
    color: #FFFFFF !important;
}
.country-item.active {
    background: linear-gradient(100deg, rgba(242,181,68,.20), rgba(164,111,24,.12)) !important;
    border: 1px solid var(--ui-gold) !important;
    color: #FFF4D8 !important;
    box-shadow: 0 0 0 1px rgba(242,181,68,.13), 0 0 18px rgba(242,181,68,.13), inset 0 0 16px rgba(242,181,68,.06);
}

.country-header {
    background: linear-gradient(100deg, #0A2730, #0A2029) !important;
    border: 1px solid rgba(32,217,210,.32);
    box-shadow: inset 0 1px 0 rgba(255,255,255,.035);
}
.country-name { color: #F4FAFB !important; }

.globe-wrapper {
    background: radial-gradient(circle at 50% 48%, rgba(13,76,83,.16), rgba(2,8,12,0) 67%);
    border-radius: 18px;
}
#globe { filter: drop-shadow(0 0 15px rgba(20,221,211,.13)); }

.info-card {
    background: linear-gradient(155deg, rgba(8,27,34,.98), rgba(3,13,18,.99)) !important;
    border: 1px solid rgba(32,217,210,.48) !important;
    border-radius: 18px !important;
    box-shadow: 0 14px 38px rgba(0,0,0,.34), 0 0 22px rgba(20,200,194,.07), inset 0 1px 0 rgba(255,255,255,.035) !important;
}
.info-title { color: var(--ui-cyan) !important; letter-spacing: .65px !important; }

.global-kpi, .info-cell {
    background: linear-gradient(145deg, #0B2932, #071A22) !important;
    border: 1px solid rgba(32,217,210,.36) !important;
    border-radius: 14px !important;
    box-shadow: inset 0 1px 0 rgba(255,255,255,.035), 0 7px 20px rgba(0,0,0,.15);
}
.global-kpi:nth-child(2) {
    background: linear-gradient(145deg, #211A31, #101622) !important;
    border-color: rgba(183,124,232,.48) !important;
}
.global-kpi:nth-child(4) {
    background: linear-gradient(145deg, #302718, #171B1A) !important;
    border-color: rgba(242,181,68,.48) !important;
}
.global-kpi-label, .info-label { color: #BFD1D5 !important; }
.global-kpi-value, .info-value { color: #FFFFFF !important; }
.info-icon { filter: drop-shadow(0 0 8px rgba(34,230,223,.24)); }

.status-chart-panel {
    background: linear-gradient(145deg, #0A222B, #06141B) !important;
    border: 1px solid rgba(32,217,210,.43) !important;
    border-radius: 15px !important;
    box-shadow: 0 9px 26px rgba(0,0,0,.22), inset 0 1px 0 rgba(255,255,255,.025);
}
.status-chart-title { color: #F1F7F8 !important; }
.status-chart-subtitle, .chart-note { color: var(--ui-muted) !important; }
.status-chart-legend { color: #D7E5E8 !important; }

.chatbot-panel {
    background: linear-gradient(145deg, #081E26, #041117) !important;
    border: 1px solid rgba(32,217,210,.62) !important;
    border-radius: 16px !important;
    box-shadow: 0 10px 30px rgba(0,0,0,.22), 0 0 18px rgba(20,200,194,.07), inset 0 1px 0 rgba(255,255,255,.035);
}
.chatbot-title { color: #F4FAFB !important; }
.chatbot-status {
    color: #9BE8D9 !important;
    border-color: rgba(32,217,210,.42) !important;
    background: rgba(13,57,57,.24);
}
.chatbot-description, .question-picker-label { color: #9BB3BB !important; }
.chat-messages {
    background: rgba(2,10,14,.58) !important;
    border-color: rgba(32,217,210,.22) !important;
}
.chat-message.assistant {
    background: linear-gradient(145deg, #102F38, #0B242D) !important;
    border-color: #245B64 !important;
}
.chat-message.user {
    background: linear-gradient(145deg, #12434A, #0C3038) !important;
    border-color: #287D83 !important;
}
.question-picker-select, .question-dropdown-menu, .question-dropdown-option {
    background-color: #0A222B !important;
    border-color: #28616A !important;
    color: #E8F2F4 !important;
}
.question-dropdown-group-label { background: #071820 !important; color: var(--ui-cyan) !important; }
.question-dropdown-option:hover, .question-dropdown-option:focus,
.question-dropdown-option[aria-selected="true"] {
    background: #12414A !important;
    color: #FFFFFF !important;
}
.question-ask, .chat-send {
    background: linear-gradient(135deg, #087F83, #07545F) !important;
    border: 1px solid #20D9D2 !important;
    color: #FFFFFF !important;
    box-shadow: 0 0 12px rgba(32,217,210,.12);
}
.question-ask:hover, .chat-send:hover {
    background: linear-gradient(135deg, #0B9C9D, #08717B) !important;
    box-shadow: 0 0 16px rgba(32,217,210,.22);
}
.chat-input {
    background: #0A222B !important;
    border-color: #28616A !important;
}
.chat-input:focus { border-color: var(--ui-cyan) !important; box-shadow: 0 0 0 2px rgba(32,217,210,.10); }
.chat-disclaimer, .footer-note { color: #8FA9B2 !important; }
.info-close {
    background: #0D3034 !important;
    border-color: #287D83 !important;
    color: #EAF7F7 !important;
}
.info-close:hover { border-color: var(--ui-cyan) !important; box-shadow: 0 0 12px rgba(32,217,210,.18); }

@media (max-width: 620px) {
    .country-panel, .info-card, .chatbot-panel { border-radius: 13px !important; }
}


/* ==========================================================
   STREAMLIT SPOTIFY-INSPIRED THEME
   Theme-only overrides. Existing dashboard structure,
   globe behaviour, analytics and assistant logic are retained.
========================================================== */
:root {
    --sp-green: #1DB954;
    --sp-green-hover: #1ED760;
    --sp-bg: #121212;
    --sp-surface: #181818;
    --sp-surface-raised: #242424;
    --sp-surface-hover: #2A2A2A;
    --sp-border: #343434;
    --sp-text: #FFFFFF;
    --sp-muted: #B3B3B3;
}

html, body {
    background: var(--sp-bg) !important;
    color: var(--sp-text) !important;
}

.dashboard {
    background: var(--sp-bg) !important;
}

.jp-header {
    background: #121212 !important;
    border-bottom: 1px solid #282828 !important;
}

.jp-globe-icon,
.jp-overview-eyebrow,
.info-title {
    color: var(--sp-green) !important;
}

.jp-header-divider {
    background: #343434 !important;
}

.jp-subtitle,
.panel-subheading,
.chatbot-description,
.chat-disclaimer,
.footer-note {
    color: var(--sp-muted) !important;
}

/* Country navigation panel */
.country-panel {
    background: #181818 !important;
    border: 1px solid #303030 !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,.28) !important;
}

.search-box {
    background: #242424 !important;
    border: 1px solid #3A3A3A !important;
    color: #FFFFFF !important;
}
.search-box:focus {
    border-color: var(--sp-green) !important;
    box-shadow: 0 0 0 1px var(--sp-green) !important;
}

.country-item {
    color: #E7E7E7 !important;
    border-color: transparent !important;
}
.country-item:hover {
    background: #282828 !important;
    border-color: #3A3A3A !important;
    color: #FFFFFF !important;
}
/* Retain the previously approved gold selected-country treatment */
.country-item.active {
    background: rgba(242,181,68,.16) !important;
    border: 1px solid #F2B544 !important;
    color: #FFE7B0 !important;
    box-shadow: 0 0 12px rgba(242,181,68,.12) !important;
}

.country-header {
    background: #181818 !important;
    border: 1px solid #343434 !important;
    box-shadow: none !important;
}
.country-name,
.panel-heading {
    color: #FFFFFF !important;
}

/* Overview surface and KPI cards */
.info-card {
    background: #181818 !important;
    border: 1px solid #303030 !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,.24) !important;
}

.global-kpi,
.info-cell {
    background: #242424 !important;
    border: 1px solid #353535 !important;
    border-radius: 12px !important;
    box-shadow: none !important;
}
.global-kpi:nth-child(2),
.global-kpi:nth-child(4) {
    background: #242424 !important;
    border-color: #3A3A3A !important;
}
.global-kpi-label,
.info-label {
    color: #B3B3B3 !important;
}
.global-kpi-value,
.info-value {
    color: #FFFFFF !important;
}

/* Keep translation-status segment colours meaningful */
.status-chart-panel {
    background: #181818 !important;
    border: 1px solid #303030 !important;
    border-radius: 14px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.22) !important;
}
.status-chart-title {
    color: #FFFFFF !important;
}
.status-chart-subtitle,
.chart-note {
    color: #B3B3B3 !important;
}
.status-chart-legend {
    color: #D0D0D0 !important;
}

/* Bible Intelligence Assistant */
.chatbot-panel {
    background: #181818 !important;
    border: 1px solid #343434 !important;
    border-radius: 14px !important;
    box-shadow: 0 10px 28px rgba(0,0,0,.25) !important;
}
.chatbot-title {
    color: #FFFFFF !important;
}
.chatbot-status {
    color: #1ED760 !important;
    border-color: rgba(29,185,84,.45) !important;
    background: rgba(29,185,84,.10) !important;
}
.chat-messages {
    background: #121212 !important;
    border-color: #343434 !important;
}
.chat-message.assistant {
    background: #242424 !important;
    border-color: #3A3A3A !important;
    color: #F1F1F1 !important;
}
.chat-message.user {
    background: #183D28 !important;
    border-color: #1DB954 !important;
    color: #FFFFFF !important;
}
.chat-message-label {
    color: #1ED760 !important;
}
.chat-answer-table th {
    background: #242424 !important;
    color: #1ED760 !important;
    border-color: #3A3A3A !important;
}
.chat-answer-table td {
    border-color: #3A3A3A !important;
}
.chat-answer-table tr:nth-child(even) td {
    background: #1E1E1E !important;
}

.question-picker-select,
.question-dropdown-menu,
.question-dropdown-option {
    background: #242424 !important;
    border-color: #3A3A3A !important;
    color: #FFFFFF !important;
}
.question-dropdown-group-label {
    background: #181818 !important;
    color: #1ED760 !important;
}
.question-dropdown-option:hover,
.question-dropdown-option:focus,
.question-dropdown-option[aria-selected="true"] {
    background: #303030 !important;
    color: #FFFFFF !important;
}

.question-ask,
.chat-send {
    background: #1DB954 !important;
    border: 1px solid #1DB954 !important;
    color: #000000 !important;
    box-shadow: none !important;
    font-weight: 800 !important;
}
.question-ask:hover,
.chat-send:hover {
    background: #1ED760 !important;
    border-color: #1ED760 !important;
    color: #000000 !important;
}

.chat-input {
    background: #242424 !important;
    border-color: #3A3A3A !important;
    color: #FFFFFF !important;
}
.chat-input:focus {
    border-color: #1DB954 !important;
    box-shadow: 0 0 0 1px #1DB954 !important;
}

/* Top navigation controls */
.st-key-gbtp-top-nav [data-testid="stButton"] > button {
    background: #242424 !important;
    border: 1px solid #3A3A3A !important;
    color: #FFFFFF !important;
    box-shadow: none !important;
}
.st-key-gbtp-top-nav [data-testid="stButton"] > button:hover {
    background: #303030 !important;
    border-color: #1DB954 !important;
    color: #1ED760 !important;
}
.st-key-gbtp-top-nav [data-testid="stButton"] > button[kind="primary"] {
    background: #1DB954 !important;
    border-color: #1DB954 !important;
    color: #000000 !important;
    box-shadow: none !important;
}

/* Native Streamlit controls used in the app */
.stApp,
[data-testid="stAppViewContainer"] {
    background: #121212 !important;
    color: #FFFFFF !important;
}
[data-testid="stHeader"] {
    background: rgba(18,18,18,.92) !important;
}
button[kind="primary"] {
    background: #1DB954 !important;
    border-color: #1DB954 !important;
    color: #000000 !important;
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

        <div id="infoOverlay" class="info-overlay" aria-label="Global or country overview">
        <section class="info-card">
            <button class="info-close" id="infoClose" aria-label="Clear country selection">×</button>

            <div id="globalOverview" class="global-overview">
                <div class="info-title">GLOBAL OVERVIEW</div>
                <div class="global-kpis">
                    <div class="global-kpi"><div class="global-kpi-label">Population represented</div><div id="globalPopulation" class="global-kpi-value">—</div></div>
                    <div class="global-kpi"><div class="global-kpi-label">Primary language counts*</div><div id="globalLanguages" class="global-kpi-value">—</div></div>
                    <div class="global-kpi"><div class="global-kpi-label">People groups</div><div id="globalPeopleGroups" class="global-kpi-value">—</div></div>
                    <div class="global-kpi"><div class="global-kpi-label">Groups needing translation</div><div id="globalTranslationNeed" class="global-kpi-value">—</div></div>
                </div>
                <section class="status-chart-panel" aria-label="Global translation progress chart">
                    <div class="status-chart-title">Global Translation Progress</div>
                    <div class="status-chart-subtitle">People groups by recorded Bible translation status</div>
                    <div id="globalStatusChart"></div>
                    <div id="globalStatusChartLegend" class="status-chart-legend"></div>
                    <div id="globalStatusChartNote" class="chart-note"></div>
                </section>
                <div class="footer-note">*Language counts are summed from country-level records and may not represent unique languages worldwide.</div>
            </div>

            <div id="countryOverview" class="country-overview" hidden>
                <div class="info-title" id="countryOverviewTitle">COUNTRY OVERVIEW</div>
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
                <section class="status-chart-panel" aria-label="Country translation progress chart">
                    <div class="status-chart-title">Country Translation Progress</div>
                    <div class="status-chart-subtitle">People groups by recorded Bible translation status</div>
                    <div id="countryStatusChart"></div>
                    <div id="countryStatusChartLegend" class="status-chart-legend"></div>
                    <div id="countryStatusChartNote" class="chart-note"></div>
                </section>
            </div>

            <section class="chatbot-panel" aria-label="Bible Intelligence Assistant">
                <div class="chatbot-heading">
                    <div class="chatbot-title">Bible Intelligence Assistant</div>
                    <div class="chatbot-status">ASSISTANT PREVIEW</div>
                </div>
                <div class="chatbot-description">
                    Ask questions about countries, people groups, languages and recorded translation indicators.
                </div>
                <div id="chatMessages" class="chat-messages" aria-live="polite">
                    <div class="chat-message assistant">
                        <span class="chat-message-label">BIBLE INTELLIGENCE ASSISTANT</span>
                        Hello! I can help you explore the country-level information currently available in this dashboard. Try asking for a country overview, a comparison, or an explanation of a Joshua Project indicator.
                    </div>
                </div>
                <div class="question-picker">
                    <label class="question-picker-label" for="questionDropdownTrigger">Choose a question to explore</label>
                    <div class="question-picker-row">
                        <div class="question-dropdown" id="questionDropdown">
                            <button id="questionDropdownTrigger" class="question-picker-select question-dropdown-trigger"
                                    type="button" aria-haspopup="listbox" aria-expanded="false">
                                <span id="questionDropdownValue">Select a question...</span>
                                <span class="question-dropdown-chevron" aria-hidden="true">⌄</span>
                            </button>
                            <div id="questionDropdownMenu" class="question-dropdown-menu" role="listbox"
                                 aria-label="Suggested questions" hidden></div>
                        </div>
                        <button id="askSelectedQuestion" class="question-ask" type="button">Ask</button>
                    </div>
                </div>
                <form id="chatForm" class="chat-input-row">
                    <input id="chatInput" class="chat-input" type="text" autocomplete="off"
                           placeholder="Ask about countries or translation data..." aria-label="Ask the assistant">
                    <button class="chat-send" type="submit">Send</button>
                </form>
                <div class="chat-disclaimer">
                    Prototype mode: responses use the country records loaded in this dashboard and basic built-in explanations. Gemini API integration will be connected separately.
                </div>
            </section>
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

// The dropdown keeps both question groups available. The selected country's
// questions are moved above the global questions when a country is active.
const GLOBAL_QUESTIONS = [
    "Which countries have the highest concentration of people groups needing translation?",
    "Which countries have the highest proportion of unspecified Bible status?",
    "Which countries have many people groups but relatively few with Bible completion?",
    "Which countries show the greatest variation in Bible translation status?",
    "Which countries combine high recorded translation need with a lower Christian adherent percentage?",
    "Which countries have the highest number of ongoing translation projects?"
];

const COUNTRY_QUESTIONS = [
    "Which is the most followed religion in {country}?",
    "What is the official language of {country}?",
    "How does {country} compare with countries having a similar number of people groups in terms of Christian adherent population and Bible completion?"
];

let selectedSuggestedQuestion = "";

function closeQuestionDropdown() {
    const menu = document.getElementById("questionDropdownMenu");
    const trigger = document.getElementById("questionDropdownTrigger");
    if (menu) menu.hidden = true;
    if (trigger) trigger.setAttribute("aria-expanded", "false");
}

function renderQuestionOptions() {
    const menu = document.getElementById("questionDropdownMenu");
    const valueLabel = document.getElementById("questionDropdownValue");
    if (!menu || !valueLabel) return;

    const selectedCountry = selectedCode && countryByCode[selectedCode]
        ? countryByCode[selectedCode].name
        : null;

    menu.innerHTML = "";
    selectedSuggestedQuestion = "";
    valueLabel.textContent = "Select a question...";

    function addGroup(label, questions, countryName) {
        const groupLabel = document.createElement("div");
        groupLabel.className = "question-dropdown-group-label";
        groupLabel.textContent = label;
        menu.appendChild(groupLabel);

        questions.forEach(template => {
            // Country suggestions are templates. Insert the currently selected
            // country's actual display name each time the menu is rendered.
            const question = countryName
                ? template.replaceAll("{country}", countryName)
                : template;

            const option = document.createElement("button");
            option.type = "button";
            option.className = "question-dropdown-option";
            option.setAttribute("role", "option");
            option.setAttribute("aria-selected", "false");
            option.textContent = question;
            option.dataset.question = question;
            option.addEventListener("click", () => {
                selectedSuggestedQuestion = question;
                valueLabel.textContent = question;
                document.getElementById("chatInput").value = question;
                closeQuestionDropdown();
            });
            menu.appendChild(option);
        });
    }

    if (selectedCountry) {
        addGroup(selectedCountry.toUpperCase() + " — COUNTRY EXPLORATION", COUNTRY_QUESTIONS, selectedCountry);
        addGroup("GLOBAL EXPLORATION", GLOBAL_QUESTIONS, null);
    } else {
        addGroup("GLOBAL EXPLORATION", GLOBAL_QUESTIONS, null);
    }
}

let hoveredCode = null;

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

function sumStatusValues(records) {
    const totals = {};
    statusDefinitions.forEach(item => { totals[item.key] = 0; });
    records.forEach(record => {
        statusDefinitions.forEach(item => {
            totals[item.key] += numericCount(record[item.key]);
        });
    });
    return totals;
}

function renderStatusChartData(statusValues, chartId, legendId, noteId, scopeLabel) {
    const chart = document.getElementById(chartId);
    const legend = document.getElementById(legendId);
    const note = document.getElementById(noteId);
    if (!chart || !legend) return;

    const statuses = statusDefinitions.map(item => ({
        ...item,
        count: numericCount(statusValues[item.key])
    }));
    const total = statuses.reduce((sum, item) => sum + item.count, 0);
    const width = Math.max(260, Math.floor(chart.getBoundingClientRect().width || 300));
    const barHeight = 42;
    const height = 54;

    if (total <= 0) {
        chart.innerHTML = '<div style="color:#91A5B4;padding:16px 0">Translation status counts are not available for this view.</div>';
        legend.innerHTML = "";
        if (note) note.textContent = "";
        return;
    }

    let x = 0;
    let segments = "";
    statuses.forEach(item => {
        if (!item.count) return;
        const segmentWidth = width * item.count / total;
        const pct = (item.count / total * 100).toFixed(1);
        segments += `<rect x="${x}" y="5" width="${segmentWidth}" height="${barHeight}" fill="${item.color}"/>`;
        if (segmentWidth >= 42) {
            segments += `<text x="${x + segmentWidth/2}" y="22" text-anchor="middle" fill="#FFFFFF" font-size="15" font-weight="700">${item.count.toLocaleString()}</text>`;
            segments += `<text x="${x + segmentWidth/2}" y="39" text-anchor="middle" fill="#FFFFFF" font-size="11">${pct}%</text>`;
        }
        x += segmentWidth;
    });

    chart.innerHTML = `<svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${scopeLabel} translation status; total recorded status count ${total.toLocaleString()}" style="display:block;width:100%;max-width:none;height:62px;margin:0"><defs><clipPath id="${chartId}Clip"><rect x="0" y="5" width="${width}" height="${barHeight}" rx="9"/></clipPath></defs><g clip-path="url(#${chartId}Clip)">${segments}</g></svg><div style="color:#91A5B4;font-size:12px;margin-top:4px">Total recorded status counts: ${total.toLocaleString()}</div>`;
    legend.innerHTML = statuses.filter(item => item.count > 0).map(item =>
        `<div class="legend-entry"><span class="legend-swatch" style="background:${item.color}"></span><span>${item.label}: <b>${item.count.toLocaleString()}</b></span></div>`
    ).join("");
    if (note) {
        note.textContent = scopeLabel === "Global"
            ? "Aggregated from country-level records; shared or cross-border groups may appear in more than one country."
            : "Percentages show each category's share of the summed recorded status counts. Confirm source definitions before treating categories as mutually exclusive.";
    }
}

function renderCountryStatusChart(code) {
    const country = countryByCode[code];
    if (!country) return;
    renderStatusChartData(
        country,
        "countryStatusChart",
        "countryStatusChartLegend",
        "countryStatusChartNote",
        "Country"
    );
}

function renderGlobalStatusChart() {
    const totals = sumStatusValues(countries);
    renderStatusChartData(
        totals,
        "globalStatusChart",
        "globalStatusChartLegend",
        "globalStatusChartNote",
        "Global"
    );
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
        Plotly.relayout(globe, {
            width: width,
            height: height,
            "geo.domain.x": [0.08, 0.92],
            "geo.domain.y": [0.08, 0.92]
        });
    });
}

function showCountryOverview(code) {
    if (!code || !countryByCode[code]) return;
    setCountryInfo(code);
    document.getElementById("globalOverview").hidden = true;
    document.getElementById("countryOverview").hidden = false;
    document.getElementById("infoClose").style.display = "block";
    document.getElementById("infoOverlay").classList.add("open");
    renderQuestionOptions();
}

function showGlobalOverview() {
    document.getElementById("countryOverview").hidden = true;
    document.getElementById("globalOverview").hidden = false;
    document.getElementById("infoClose").style.display = "none";
    document.getElementById("infoOverlay").classList.add("open");
    document.getElementById("countryName").textContent = "SELECT A COUNTRY";
    renderQuestionOptions();
}

function closeCountryOverview() {
    selectedCode = null;
    hoveredCode = null;
    document.querySelectorAll(".country-item").forEach(item => item.classList.remove("active"));
    updateGlobeHighlight(null);
    showGlobalOverview();
}

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
    renderGlobalStatusChart();
}

// --------------------------------------------------
// CHATBOT PREVIEW
// This is a lightweight front-end prototype. It does not expose an API key.
// Gemini will be connected through a Python backend in the next implementation step.
// --------------------------------------------------

function renderChatAnswer(container, message) {
    const lines = String(message || "").split("\n");
    let paragraph = [];
    let tableRows = [];

    function flushParagraph() {
        if (!paragraph.length) return;
        const p = document.createElement("div");
        p.textContent = paragraph.join("\n");
        container.appendChild(p);
        paragraph = [];
    }
    function flushTable() {
        if (!tableRows.length) return;
        flushParagraph();
        const wrap = document.createElement("div");
        wrap.className = "chat-answer-table-wrap";
        const table = document.createElement("table");
        table.className = "chat-answer-table";
        tableRows.forEach((cells, rowIndex) => {
            const tr = document.createElement("tr");
            cells.forEach(value => {
                const cell = document.createElement(rowIndex === 0 ? "th" : "td");
                cell.textContent = value;
                tr.appendChild(cell);
            });
            table.appendChild(tr);
        });
        wrap.appendChild(table);
        container.appendChild(wrap);
        tableRows = [];
    }

    lines.forEach(line => {
        const trimmed = line.trim();
        if (trimmed.startsWith("|") && trimmed.endsWith("|")) {
            const cells = trimmed.slice(1, -1).split("|").map(cell => cell.trim());
            if (cells.every(cell => /^:?-{3,}:?$/.test(cell))) return;
            flushParagraph();
            tableRows.push(cells);
        } else {
            flushTable();
            if (trimmed) paragraph.push(line);
            else flushParagraph();
        }
    });
    flushTable();
    flushParagraph();
}

function addChatMessage(role, message) {
    const messages = document.getElementById("chatMessages");
    const bubble = document.createElement("div");
    bubble.className = `chat-message ${role}`;

    const label = document.createElement("span");
    label.className = "chat-message-label";
    label.textContent = role === "user" ? "YOU" : "BIBLE INTELLIGENCE ASSISTANT";

    const body = document.createElement("div");
    body.className = "chat-message-body";
    renderChatAnswer(body, message);

    bubble.appendChild(label);
    bubble.appendChild(body);
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
}

function findCountryFromQuestion(question) {
    const normalized = question.toLowerCase();
    return countries.find(country => normalized.includes(country.name.toLowerCase())) || null;
}

function answerFromLoadedData(question) {
    const q = question.toLowerCase();
    const mentionedCountry = findCountryFromQuestion(question);

    const metricFields = [
        ["Bible complete", "bible_complete"],
        ["New Testament", "bible_new_testament"],
        ["Bible portions", "bible_portions"],
        ["Translation started", "translation_started"],
        ["Translation needed", "translation_needed"],
        ["Status unspecified", "translation_unspecified"]
    ];
    const number = value => parseMetric(value);
    const pct = value => `${value.toFixed(1)}%`;
    const rowsWith = (countKey, denominatorKey = "people_groups") => countries.map(country => {
        const count = number(country[countKey]);
        const denominator = number(country[denominatorKey]);
        return { country, count, denominator, share: count !== null && denominator > 0 ? count / denominator : null };
    }).filter(row => row.count !== null && row.denominator !== null && row.denominator > 0);
    const ranked = (countKey, mode = "count", minimumGroups = 1) => rowsWith(countKey)
        .filter(row => row.denominator >= minimumGroups && (mode === "count" ? row.count > 0 : row.share !== null))
        .sort((a, b) => mode === "count" ? b.count - a.count : b.share - a.share);
    const listRanked = (items, mode, countLabel, limit = 5) => {
        if (!items.length) return "The loaded country records do not contain enough comparable data for this calculation.";
        return items.slice(0, limit).map((row, index) => {
            const value = mode === "count" ? formatMetric(row.count) : pct(row.share * 100);
            return `${index + 1}. ${row.country.name}: ${value} (${formatMetric(row.count)} of ${formatMetric(row.denominator)} people groups)`;
        }).join("\n");
    };
    const countryStatus = country => metricFields.map(([label, key]) => ({ label, count: number(country[key]) }))
        .filter(item => item.count !== null);
    const sum = values => values.reduce((total, value) => total + value, 0);
    const average = values => values.length ? sum(values) / values.length : null;

    // Country-level analytical questions take precedence when a country is named.
    if (mentionedCountry) {
        const country = mentionedCountry;
        const groupCount = number(country.people_groups);
        const need = number(country.translation_needed);
        const unspecified = number(country.translation_unspecified);
        const complete = number(country.bible_complete);
        const needShare = need !== null && groupCount > 0 ? need / groupCount * 100 : null;
        const unspecifiedShare = unspecified !== null && groupCount > 0 ? unspecified / groupCount * 100 : null;
        const completeShare = complete !== null && groupCount > 0 ? complete / groupCount * 100 : null;

        if (q.includes("most followed religion") || q.includes("religion")) {
            return `MOST FOLLOWED RECORDED RELIGION — ${country.name}\n\nPrimary religion recorded: ${displayValue(country.religion_primary)}\nChristian adherent percentage: ${displayValue(country.christianity)}\n\nThis answer uses the primary-religion field available in the country record.`;
        }

        if (q.includes("official language") || q.includes("official languages")) {
            return `OFFICIAL LANGUAGE — ${country.name}\n\nOfficial language recorded: ${displayValue(country.official_language)}\n\nThis reflects the official-language field in the loaded country record.`;
        }

        if (q.includes("similar number") || q.includes("similar people-group") || q.includes("similar people group")) {
            const peers = countries.map(item => {
                const groups = number(item.people_groups);
                const pop = number(item.population);
                const christian = number(item.christianity);
                const completeCount = number(item.bible_complete);
                return {
                    country: item, groups, completeCount,
                    estimatedChristian: pop !== null && christian !== null ? pop * christian / 100 : null,
                    completeShare: groups > 0 && completeCount !== null ? completeCount / groups * 100 : null
                };
            }).filter(item => item.groups !== null && groupCount !== null &&
                item.country.iso3 !== country.iso3 &&
                Math.abs(item.groups - groupCount) <= Math.max(5, groupCount * 0.2) &&
                item.completeCount !== null)
              .sort((a,b) => Math.abs(a.groups-groupCount)-Math.abs(b.groups-groupCount))
              .slice(0, 6);
            const selectedPopulation = number(country.population);
            const selectedChristianPct = number(country.christianity);
            const selectedEstimatedChristian = selectedPopulation !== null && selectedChristianPct !== null
                ? selectedPopulation * selectedChristianPct / 100 : null;
            const selectedCompleteShare = groupCount > 0 && complete !== null ? complete / groupCount * 100 : null;
            if (groupCount === null || complete === null || !peers.length) {
                return `SIMILAR PEOPLE-GROUP COUNT COMPARISON — ${country.name}\n\nThere are not enough comparable country records to build this table.`;
            }
            const rows = [{
                country, groups: groupCount, estimatedChristian: selectedEstimatedChristian,
                completeCount: complete, completeShare: selectedCompleteShare
            }, ...peers];
            const table = [
                "| Country | People groups | Estimated Christian adherent population | Bible-complete groups | Bible complete (%) |",
                "|---|---:|---:|---:|---:|",
                ...rows.map(item => `| ${item.country.name} | ${formatMetric(item.groups)} | ${item.estimatedChristian === null ? "Unavailable" : formatMetric(item.estimatedChristian)} | ${item.completeCount === null ? "Unavailable" : formatMetric(item.completeCount)} | ${item.completeShare === null ? "Unavailable" : pct(item.completeShare)} |`)
            ].join("\n");
            return `SIMILAR PEOPLE-GROUP COUNT COMPARISON — ${country.name}\n\n${table}\n\nComparison set: up to six other countries within ±20% of ${country.name}'s recorded people-group count (minimum tolerance: five groups), ordered by closest match. Christian adherent population is estimated as total population × recorded Christian adherent percentage; it is not a directly reported headcount. Bible-complete percentage is Bible-complete count divided by total people groups. These are descriptive comparisons, not evidence of causation.`;
        }

        if (q.includes("global average") || q.includes("global picture") || q.includes("compare") && (q.includes("global") || q.includes("world"))) {
            const metrics = [
                ["People groups", "people_groups"], ["Primary languages", "language_count"],
                ["Translation needed", "translation_needed"], ["Translation started", "translation_started"],
                ["Bible complete", "bible_complete"], ["Status unspecified", "translation_unspecified"]
            ];
            const lines = metrics.map(([label, key]) => {
                const vals = countries.map(item => number(item[key])).filter(value => value !== null);
                const avg = average(vals);
                const val = number(country[key]);
                if (avg === null || val === null) return `${label}: not enough data for comparison.`;
                const direction = val > avg ? "above" : val < avg ? "below" : "equal to";
                return `${label}: ${formatMetric(val)} in ${country.name}; unweighted country-record average ${formatMetric(avg)} (${direction} average).`;
            });
            return `COUNTRY-TO-GLOBAL COMPARISON — ${country.name}\n\n${lines.join("\n")}\n\nThese are comparisons with the unweighted average of country records, not population-weighted global rates. Summed country records may include shared or cross-border people groups.`;
        }

        if (q.includes("biggest gap") || q.includes("translation need") || q.includes("unspecified") || q.includes("status category") || q.includes("largest share")) {
            const statuses = countryStatus(country).sort((a, b) => (b.count || 0) - (a.count || 0));
            const lines = statuses.map(item => `${item.label}: ${formatMetric(item.count)}`).join("\n");
            return `RECORDED TRANSLATION INDICATORS — ${country.name}\n\n${lines || "No status counts are available in this country record."}\n\nPeople groups recorded: ${groupCount === null ? "not available" : formatMetric(groupCount)}\nTranslation needed as a share of recorded people groups: ${needShare === null ? "not calculable" : pct(needShare)}\nStatus unspecified as a share of recorded people groups: ${unspecifiedShare === null ? "not calculable" : pct(unspecifiedShare)}\nBible complete as a share of recorded people groups: ${completeShare === null ? "not calculable" : pct(completeShare)}\n\nThese are descriptive ratios of country-level counts. Status categories are retained as separate source indicators; they should not be assumed to be mutually exclusive.`;
        }

        if (q.includes("people group") && q.includes("language")) {
            return `PEOPLE GROUPS AND PRIMARY LANGUAGES — ${country.name}\n\nPeople groups: ${displayValue(country.people_groups)}\nPrimary languages: ${displayValue(country.language_count)}\n\nThe two figures describe different units. A people group is an ethnic or cultural community; a primary language is a language associated with the country's records. They are not interchangeable, and the ratio should not be interpreted as a one-to-one mapping.`;
        }

        if (q.includes("unusual") || q.includes("similar number")) {
            const peers = countries.map(item => ({ country: item, groups: number(item.people_groups), complete: number(item.bible_complete) }))
                .filter(item => item.groups !== null && groupCount !== null && item.groups > 0 && Math.abs(item.groups - groupCount) <= Math.max(5, groupCount * 0.2))
                .map(item => ({ ...item, completionShare: item.complete === null ? null : item.complete / item.groups }))
                .filter(item => item.completionShare !== null)
                .sort((a, b) => b.completionShare - a.completionShare);
            const countryShare = completeShare === null ? null : completeShare / 100;
            if (countryShare === null || !peers.length) return `There are not enough comparable completion records to assess ${country.name} against countries with a similar number of people groups.`;
            return `SIMILAR-SIZE COUNTRY COMPARISON — ${country.name}\n\n${country.name}: ${pct(countryShare * 100)} recorded Bible-complete count relative to its people-group count (${formatMetric(complete)} of ${formatMetric(groupCount)}).\n\nCountries with a similar people-group count (within approximately 20%, with a minimum tolerance of five groups):\n${peers.slice(0, 5).map(item => `${item.country.name}: ${pct(item.completionShare * 100)} (${formatMetric(item.complete)} of ${formatMetric(item.groups)})`).join("\n")}\n\nThis is a rough descriptive comparison, not a measure of individual language access or translation quality.`;
        }

        if (q.includes("stand out") || q.includes("investigate") || q.includes("what should")) {
            return `COUNTRY SNAPSHOT — ${country.name}\n\nRegion: ${displayValue(country.region)}\nPopulation: ${displayValue(country.population)}\nPrimary languages: ${displayValue(country.language_count)}\nPeople groups: ${displayValue(country.people_groups)}\nChristian adherent percentage: ${displayValue(country.christianity)}\nTranslation needed: ${displayValue(country.translation_needed)}${needShare === null ? "" : ` (${pct(needShare)} of recorded people groups)`}\nTranslation started: ${displayValue(country.translation_started)}\nBible portions: ${displayValue(country.bible_portions)}\nNew Testament: ${displayValue(country.bible_new_testament)}\nBible complete: ${displayValue(country.bible_complete)}\nStatus unspecified: ${displayValue(country.translation_unspecified)}\n\nUseful follow-up checks: inspect the underlying people-group and language profiles, verify the definitions and date of each source indicator, and check whether cross-border groups are represented in multiple country records. The current CSV does not contain individual profile-level details.`;
        }

        return `COUNTRY OVERVIEW — ${country.name}\n\nPopulation: ${displayValue(country.population)}\nRegion: ${displayValue(country.region)}\nPrimary languages: ${displayValue(country.language_count)}\nPeople groups: ${displayValue(country.people_groups)}\nChristian adherent percentage: ${displayValue(country.christianity)}\nTranslation needed: ${displayValue(country.translation_needed)}\nTranslation started: ${displayValue(country.translation_started)}\nBible portions: ${displayValue(country.bible_portions)}\nNew Testament: ${displayValue(country.bible_new_testament)}\nBible complete: ${displayValue(country.bible_complete)}\nStatus unspecified: ${displayValue(country.translation_unspecified)}\n\nThis summary uses the country-level records loaded in the dashboard; it does not include individual language or people-group profiles.`;
    }

    // 1. Highest translation need: provide both absolute counts and proportions.
    if ((q.includes("concentration") || q.includes("proportion") || q.includes("percentage") || q.includes("highest") || q.includes("need")) && (q.includes("translation") || q.includes("people group")) && !q.includes("ongoing") && !q.includes("projects") && !q.includes("christian") && !q.includes("adherent")) {
        const byShare = ranked("translation_needed", "share");
        const byCount = ranked("translation_needed", "count");
        const table = ["| Country | People groups | Groups needing translation | Translation need (%) |",
            "|---|---:|---:|---:|",
            ...byShare.slice(0, 7).map(row => `| ${row.country.name} | ${formatMetric(row.denominator)} | ${formatMetric(row.count)} | ${pct(row.share * 100)} |`)].join("\n");
        return `COUNTRIES WITH THE HIGHEST RECORDED TRANSLATION NEED\n\n${table}\n\nRanked by the proportion of recorded people groups marked as needing translation. Absolute counts are included to avoid misleading small-denominator rankings. These are country-level source counts, not active project counts.`;;
    }

    // Recorded gaps: show separate indicators rather than collapsing them into one score.
    if (q.includes("biggest gaps")) {
        const need = ranked("translation_needed", "count");
        const unspecified = ranked("translation_unspecified", "count");
        const completion = countries.map(country => {
            const groups = number(country.people_groups), complete = number(country.bible_complete);
            return { country, groups, complete, share: groups > 0 && complete !== null ? complete / groups : null };
        }).filter(row => row.groups >= 20 && row.share !== null).sort((a,b)=>a.share-b.share).slice(0,5);
        return `WHERE THE LARGEST RECORDED GAPS APPEAR\n\nHighest translation-needed counts:\n${need.slice(0,5).map((row,i)=>`${i+1}. ${row.country.name}: ${formatMetric(row.count)} of ${formatMetric(row.denominator)} people groups (${pct(row.share*100)})`).join("\n")}\n\nHighest unspecified-status counts:\n${unspecified.slice(0,5).map((row,i)=>`${i+1}. ${row.country.name}: ${formatMetric(row.count)} of ${formatMetric(row.denominator)} people groups (${pct(row.share*100)})`).join("\n")}\n\nLowest Bible-complete count relative to people-group count (countries with at least 20 groups):\n${completion.map((row,i)=>`${i+1}. ${row.country.name}: ${pct(row.share*100)} (${formatMetric(row.complete)} of ${formatMetric(row.groups)})`).join("\n")}\n\nThese are three distinct descriptive views, not one combined gap score. The Bible-complete ratio is a screening proxy and does not prove that all other groups lack Scripture.`;
    }

    // 2. Unspecified status rankings.
    if (q.includes("unspecified")) {
        const byShare = ranked("translation_unspecified", "share");
        const byCount = ranked("translation_unspecified", "count");
        const table = ["| Country | People groups | Status unspecified | Unspecified (%) |",
            "|---|---:|---:|---:|",
            ...byShare.slice(0, 7).map(row => `| ${row.country.name} | ${formatMetric(row.denominator)} | ${formatMetric(row.count)} | ${pct(row.share * 100)} |`)].join("\n");
        return `COUNTRIES WITH THE HIGHEST UNSPECIFIED-STATUS PROPORTIONS\n\n${table}\n\nThe percentage uses the total recorded people-group count as its denominator. Unspecified status should not be interpreted as proof that translation work is absent.`;;
    }

    // 3. High group counts with relatively low Bible-complete counts.
    if (q.includes("many people groups") || (q.includes("people groups") && q.includes("completion"))) {
        const rows = countries.map(country => {
            const groups = number(country.people_groups), complete = number(country.bible_complete);
            return { country, groups, complete, share: groups > 0 && complete !== null ? complete / groups : null };
        }).filter(row => row.groups !== null && row.groups >= 20 && row.share !== null)
          .sort((a, b) => a.share - b.share || b.groups - a.groups).slice(0, 7);
        const table = ["| Country | People groups | Bible-complete groups | Bible complete (%) |",
            "|---|---:|---:|---:|",
            ...rows.map(row => `| ${row.country.name} | ${formatMetric(row.groups)} | ${formatMetric(row.complete)} | ${pct(row.share * 100)} |`)].join("\n");
        return `COUNTRIES WITH MANY PEOPLE GROUPS AND LOWER RECORDED BIBLE COMPLETION\n\n${rows.length ? table : "There are not enough records meeting the comparison threshold."}\n\nFor this screening comparison, “many” means at least 20 recorded people groups. Bible-complete percentage is the recorded Bible-complete count divided by country people-group count. Status indicators may not be mutually exclusive or exhaustive.`;;
    }

    // 4. Regional comparison.
    if (q.includes("region") || q.includes("world region")) {
        const groups = {};
        countries.forEach(country => {
            const region = country.region && country.region !== "—" ? country.region : "Region not recorded";
            if (!groups[region]) groups[region] = { region, countries: 0, people: 0, need: 0, started: 0, portions: 0, nt: 0, complete: 0, unspecified: 0, denominatorRecords: 0 };
            const row = groups[region]; row.countries += 1;
            const people = number(country.people_groups);
            if (people !== null) { row.people += people; row.denominatorRecords += 1; }
            [["translation_needed", "need"], ["translation_started", "started"], ["bible_portions", "portions"], ["bible_new_testament", "nt"], ["bible_complete", "complete"], ["translation_unspecified", "unspecified"]].forEach(([key, target]) => { const value = number(country[key]); if (value !== null) row[target] += value; });
        });
        const ordered = Object.values(groups).sort((a, b) => (b.need / Math.max(1,b.people)) - (a.need / Math.max(1,a.people)));
        return `RECORDED BIBLE-TRANSLATION INDICATORS BY WORLD REGION\n\n${ordered.map(row => `${row.region} (${row.countries} country records; ${formatMetric(row.people)} people groups)\n  Translation needed: ${formatMetric(row.need)} (${row.people ? pct(row.need / row.people * 100) : "not calculable"} of people-group count)\n  Translation started: ${formatMetric(row.started)}\n  Bible portions: ${formatMetric(row.portions)}\n  New Testament: ${formatMetric(row.nt)}\n  Bible complete: ${formatMetric(row.complete)}\n  Status unspecified: ${formatMetric(row.unspecified)}`).join("\n\n")}\n\nRegional figures are sums of country-level records. Shared or cross-border people groups may be represented in more than one country. Status categories are separate indicators and should not be added together as if they were mutually exclusive.`;
    }

    // 5. Translation need alongside Christian adherent percentage.
    if (q.includes("christian") || q.includes("adherent")) {
        const christianValues = countries.map(country => number(country.christianity)).filter(value => value !== null);
        const medianChristian = [...christianValues].sort((a,b)=>a-b)[Math.floor(christianValues.length / 2)];
        const needRows = countries.map(country => {
            const need = number(country.translation_needed), groups = number(country.people_groups), christian = number(country.christianity);
            return { country, need, groups, christian, needShare: need !== null && groups > 0 ? need / groups : null };
        }).filter(row => row.needShare !== null && row.christian !== null && row.christian <= medianChristian)
          .sort((a,b)=>b.needShare-a.needShare).slice(0,7);
        const table = ["| Country | People groups | Groups needing translation | Translation need (%) | Christian adherent (%) |",
            "|---|---:|---:|---:|---:|",
            ...needRows.map(row => `| ${row.country.name} | ${formatMetric(row.groups)} | ${formatMetric(row.need)} | ${pct(row.needShare * 100)} | ${pct(row.christian)} |`)].join("\n");
        return `COUNTRIES COMBINING TRANSLATION NEED WITH LOWER CHRISTIAN ADHERENCE\n\nDataset median Christian adherent percentage: ${medianChristian === undefined ? "not available" : pct(medianChristian)}. Countries at or below the median with the highest translation-needed proportions:\n\n${table}\n\nThis is a descriptive screen using country-level percentages, not a measure of individual spiritual engagement, demand, or recommended resource allocation.`;;
    }

    // TranslationStarted is the available country-level indicator for translation work that has started.
    if (q.includes("ongoing translation") || q.includes("translation projects") || q.includes("translation started")) {
        const rows = countries.map(country => {
            const groups = number(country.people_groups);
            const started = number(country.translation_started);
            return { country, groups, started, share: groups > 0 && started !== null ? started / groups * 100 : null };
        }).filter(row => row.started !== null && row.groups !== null)
          .sort((a,b) => b.started - a.started).slice(0, 10);
        const table = [
            "| Country | People groups | Translation started (recorded count) | Translation started (% of people groups) |",
            "|---|---:|---:|---:|",
            ...rows.map(row => `| ${row.country.name} | ${formatMetric(row.groups)} | ${formatMetric(row.started)} | ${row.share === null ? "Unavailable" : pct(row.share)} |`)
        ].join("\n");
        return `COUNTRIES WITH THE HIGHEST RECORDED TRANSLATION-STARTED COUNTS\n\n${table}\n\nThis ranking uses the TranslationStarted column. The result is labelled as a translation-started count, not as a verified count of active projects, unless the source documentation confirms that definition.`;
    }

    // 6. Variation in recorded status categories.
    if (q.includes("variation") || q.includes("vary across") || q.includes("distribution")) {
        const rows = countries.map(country => {
            const values = metricFields.map(([,key]) => number(country[key])).filter(value => value !== null);
            const total = sum(values);
            const shares = total > 0 ? values.map(value => value / total).filter(value => value > 0) : [];
            const entropy = shares.length > 1 ? -sum(shares.map(value => value * Math.log(value))) : 0;
            const evenness = shares.length > 1 ? entropy / Math.log(shares.length) : 0;
            return { country, total, evenness, dominantShare: shares.length ? Math.max(...shares) * 100 : null };
        }).filter(row => row.total > 0 && row.dominantShare !== null).sort((a,b)=>b.evenness-a.evenness).slice(0,7);
        const table = ["| Country | Status-distribution evenness | Largest category share | Sum of recorded status counts |",
            "|---|---:|---:|---:|",
            ...rows.map(row => `| ${row.country.name} | ${pct(row.evenness * 100)} | ${pct(row.dominantShare)} | ${formatMetric(row.total)} |`)].join("\n");
        return `COUNTRIES WITH THE GREATEST VARIATION IN RECORDED STATUS COUNTS\n\n${table}\n\nMethod: the six status counts are converted into shares of their sum, then a normalized Shannon-entropy score is calculated. Higher evenness means the recorded counts are spread more evenly across non-zero categories; it does not mean greater translation progress. Categories may not be mutually exclusive or exhaustive.`;;
    }

    // 7. Global overview.
    if (q.includes("overview") || q.includes("global landscape") || q.includes("worldwide")) {
        const totals = [
            ["Population represented (sum of country records)", "population"], ["Primary-language counts (summed)", "language_count"],
            ["People-group counts (summed)", "people_groups"], ["Translation needed", "translation_needed"],
            ["Translation started", "translation_started"], ["Bible portions", "bible_portions"],
            ["New Testament", "bible_new_testament"], ["Bible complete", "bible_complete"],
            ["Status unspecified", "translation_unspecified"]
        ];
        const lines = totals.map(([label,key]) => `${label}: ${formatMetric(sum(countries.map(country => number(country[key])).filter(value => value !== null)))}`);
        const regions = new Set(countries.map(country => country.region).filter(value => value && value !== "—")).size;
        return `GLOBAL BIBLE-TRANSLATION LANDSCAPE — LOADED COUNTRY DATA\n\nCountry and territory records: ${countries.length}\nRegions represented: ${regions}\n${lines.join("\n")}\n\nInterpretation: these are sums of the available country-level records, not guaranteed unique global totals. Primary-language counts may include the same language in multiple countries, and cross-border people groups may be counted more than once. The six status indicators are separate source fields and should not be summed into a single progress total.`;
    }

    if (q.includes("people group") && q.includes("language")) {
        return "A people group is an ethnic or cultural community, while a language is a means of communication. They are related but not interchangeable: one people group may use more than one language, and one language may be shared by multiple people groups.";
    }
    if (q.includes("hello") || q === "hi" || q.includes("what can you do")) {
        return "I can analyse the country-level records currently loaded: rank translation-needed or unspecified counts and proportions, compare Bible-complete counts with people-group totals, compare regions, examine translation need alongside Christian adherent percentages, describe variation across recorded status indicators, and summarise the global dataset. I will state when the available data does not support a requested conclusion.";
    }
    return "I couldn't confidently match that question to one of the available analyses. Try asking about translation need, unspecified status, Bible completion, regional comparisons, Christian adherent percentages, status variation, or the global overview. I won't invent an answer when the question cannot be mapped to the loaded data.";
}
function submitChatQuestion(question) {
    const cleaned = (question || "").trim();
    if (!cleaned) return;

    addChatMessage("user", cleaned);
    const answer = answerFromLoadedData(cleaned);
    addChatMessage("assistant", answer);
}

document.getElementById("chatForm").addEventListener("submit", event => {
    event.preventDefault();
    const input = document.getElementById("chatInput");
    submitChatQuestion(input.value);
    input.value = "";
    input.focus();
});

document.getElementById("questionDropdownTrigger").addEventListener("click", () => {
    const menu = document.getElementById("questionDropdownMenu");
    const trigger = document.getElementById("questionDropdownTrigger");
    if (!menu || !trigger) return;
    const willOpen = menu.hidden;
    if (willOpen) {
        menu.hidden = false;
        trigger.setAttribute("aria-expanded", "true");
    } else {
        closeQuestionDropdown();
    }
});

document.getElementById("askSelectedQuestion").addEventListener("click", () => {
    if (!selectedSuggestedQuestion) return;
    submitChatQuestion(selectedSuggestedQuestion);
    selectedSuggestedQuestion = "";
    document.getElementById("questionDropdownValue").textContent = "Select a question...";
    document.getElementById("chatInput").value = "";
    closeQuestionDropdown();
});

document.addEventListener("click", event => {
    const dropdown = document.getElementById("questionDropdown");
    if (dropdown && !dropdown.contains(event.target)) closeQuestionDropdown();
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeQuestionDropdown();
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
    document.getElementById("countryOverviewTitle").textContent =
        `COUNTRY OVERVIEW — ${country.name.toUpperCase()}`;

    document.getElementById("population").textContent =
        displayValue(country.population);

    document.getElementById("languageCount").textContent =
        displayValue(country.language_count);

    document.getElementById("peopleGroups").textContent =
        displayValue(country.people_groups);

    document.getElementById("christianity").textContent =
        formatChristianityPercent(country.christianity);

    renderCountryStatusChart(code);
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
            showCountryOverview(country.iso3);
            updateCountryListHighlight();
            updateGlobeHighlight(country.iso3);
        });

        item.addEventListener("mouseleave", () => {
            hoveredCode = null;
            restoreOverviewAfterHover();
        });

        item.addEventListener("click", () => {
            setActiveCountry(country.iso3, true);
        });

        list.appendChild(item);
    });
}

function updateCountryListHighlight() {
    document.querySelectorAll(".country-item").forEach(item => {
        item.classList.toggle("active", item.dataset.code === selectedCode);
        item.classList.toggle("preview", !selectedCode && item.dataset.code === hoveredCode);
    });
}

function restoreOverviewAfterHover() {
    const codeToShow = selectedCode || null;
    if (codeToShow) {
        showCountryOverview(codeToShow);
    } else {
        showGlobalOverview();
    }
    updateCountryListHighlight();
    updateGlobeHighlight(selectedCode);
}

function setActiveCountry(code, scrollToItem = false) {
    if (!countryByCode[code]) return;

    // Clicking the currently selected country toggles the selection off.
    if (selectedCode === code) {
        closeCountryOverview();
        return;
    }

    selectedCode = code;
    hoveredCode = null;
    setCountryInfo(code);
    showCountryOverview(code);
    updateCountryListHighlight();
    updateGlobeHighlight(code);
    rotateCountryToFront(code);

    if (scrollToItem) {
        const activeItem = document.querySelector(`.country-item[data-code="${code}"]`);
        if (activeItem) activeItem.scrollIntoView({ block: "nearest", inline: "nearest", behavior: "smooth" });
    }
}

document.getElementById("infoClose").addEventListener("click", closeCountryOverview);
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
        "geo.projection.rotation.lat": 0,
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
        [0.0, "#0B3B3D"],
        [0.49, "#0B3B3D"],
        [0.5, "#F2B544"],
        [1.0, "#F2B544"]
    ],

    zmin: 0,
    zmax: 1,
    showscale: false,

    marker: {
        line: {
            color: "#45E6D0",
            width: 1.1
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
        
        projection: {
            type: "orthographic",
            scale: 0.5,
            rotation: {
                lon: 0,
                lat: 0,
                roll: 0
            }
        },

        showland: true,
        landcolor: "#0B3B3D",

        showocean: true,
        oceancolor: "#04172A",

        showlakes: true,
        lakecolor: "#061522",

        showcountries: false,

        showcoastlines: true,
        coastlinecolor: "#45E6D0",
        coastlinewidth: 1.2,

        bgcolor: "rgba(2,7,13,0)"
    }
};

// Wait until the globe wrapper has its real layout dimensions before creating Plotly.
// The earlier double-requestAnimationFrame approach ran too soon and measured
// the wrapper at 2px wide. Require a usable size that remains stable for 3 frames.
function waitForStableGlobeSize() {
    return new Promise(resolve => {
        const wrapper = document.querySelector(".globe-wrapper");
        let previousWidth = 0;
        let previousHeight = 0;
        let stableFrames = 0;

        const observer = new ResizeObserver(() => {
            // The observer wakes the measurement loop when the CSS grid changes.
        });
        observer.observe(wrapper);

        function checkSize() {
            const rect = wrapper.getBoundingClientRect();
            const width = Math.round(rect.width);
            const height = Math.round(rect.height);

            if (width >= 100 && height >= 100) {
                if (
                    Math.abs(width - previousWidth) <= 1 &&
                    Math.abs(height - previousHeight) <= 1
                ) {
                    stableFrames += 1;
                } else {
                    stableFrames = 0;
                }

                previousWidth = width;
                previousHeight = height;

                if (stableFrames >= 3) {
                    observer.disconnect();
                    resolve({ width, height });
                    return;
                }
            } else {
                stableFrames = 0;
                previousWidth = width;
                previousHeight = height;
            }

            requestAnimationFrame(checkSize);
        }

        requestAnimationFrame(checkSize);
    });
}

const globeWrapper = document.querySelector(".globe-wrapper");

waitForStableGlobeSize().then(({ width, height }) => {
    // Explicitly initialize Plotly at the wrapper's final measured dimensions.
    layout.autosize = false;
    layout.width = width;
    layout.height = height;

    console.log("Initializing Plotly globe at stable wrapper size:", width, height);

    Plotly.newPlot(
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
renderQuestionOptions();
    showGlobalOverview();

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

    // Keep Plotly synchronized with the globe wrapper itself. This also catches
    // CSS-grid changes that do not produce a window resize event.
    let lastAppliedGlobeWidth = width;
    let lastAppliedGlobeHeight = height;
    let globeResizeFrame = null;

    const globeDimensionObserver = new ResizeObserver(() => {
        if (globeResizeFrame !== null) cancelAnimationFrame(globeResizeFrame);
        globeResizeFrame = requestAnimationFrame(() => {
            globeResizeFrame = null;
            const wrapper = document.querySelector(".globe-wrapper");
            const globe = document.getElementById("globe");
            if (!wrapper || !globe || !globe.data || !globe.data.length) return;

            const rect = wrapper.getBoundingClientRect();
            const nextWidth = Math.round(rect.width);
            const nextHeight = Math.round(rect.height);
            if (nextWidth < 100 || nextHeight < 100) return;

            if (
                Math.abs(nextWidth - lastAppliedGlobeWidth) > 1 ||
                Math.abs(nextHeight - lastAppliedGlobeHeight) > 1
            ) {
                lastAppliedGlobeWidth = nextWidth;
                lastAppliedGlobeHeight = nextHeight;
                Plotly.relayout(globe, { width: nextWidth, height: nextHeight });
            }
        });
    });
    globeDimensionObserver.observe(globeWrapper);

    window.addEventListener("resize", () => {
        if (selectedCode || hoveredCode) {
            renderCountryStatusChart(selectedCode || hoveredCode);
        } else {
            renderGlobalStatusChart();
        }
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
            showCountryOverview(code);
            updateCountryListHighlight();
            updateGlobeHighlight(code);
        }
    );

    document.getElementById("globe").on(
        "plotly_unhover",
        () => {
            hoveredCode = null;
            restoreOverviewAfterHover();
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
    });
});
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



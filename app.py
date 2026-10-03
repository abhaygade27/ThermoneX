import streamlit as st
import pandas as pd
import folium
import geopandas as gpd
from shapely.ops import transform
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Mumbai Heat-Health Intelligence",
    page_icon="🌡️",
    layout="wide"
)

# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("🌡️ Mumbai Heat-Health Intelligence")
st.caption("Localized Heat-Health Early Warning System")

# --------------------------------------------------
# FILES
# --------------------------------------------------

WARD_FILE = "mumbai_ward_utci_5day_005.csv"
GEOJSON_FILE = "data/Mumbai_BMC_Wards.geojson"

# --------------------------------------------------
# LOAD UTCI DATA
# --------------------------------------------------

df = pd.read_csv(WARD_FILE)

df["ward"] = df["Name"].astype(str).str.strip()
df["datetime"] = pd.to_datetime(df["datetime"])

# --------------------------------------------------
# LOAD WARD BOUNDARIES
# --------------------------------------------------

wards = gpd.read_file(GEOJSON_FILE)

# The source GeoJSON has latitude/longitude reversed.
# Correct it for display in Folium.

def swap_xy(geometry):
    return transform(
        lambda x, y, z=None: (y, x),
        geometry
    )

wards["geometry"] = wards["geometry"].apply(swap_xy)

wards = wards.set_crs(
    "EPSG:4326",
    allow_override=True
)

wards["ward"] = wards["Name"].astype(str).str.strip()

# --------------------------------------------------
# DATE / TIME
# --------------------------------------------------

available_dates = sorted(
    df["datetime"].dt.date.unique()
)

selected_date = st.selectbox(
    "Forecast Date",
    available_dates
)

date_data = df[
    df["datetime"].dt.date == selected_date
]

available_times = sorted(
    date_data["datetime"].unique()
)

selected_time = st.selectbox(
    "Forecast Time",
    available_times
)

map_data = df[
    df["datetime"] == selected_time
].copy()

# --------------------------------------------------
# MERGE UTCI WITH WARD GEOMETRY
# --------------------------------------------------

map_gdf = wards.merge(
    map_data,
    on="ward",
    how="left"
)

# --------------------------------------------------
# MAP
# --------------------------------------------------

mumbai_map = folium.Map(
    location=[19.0760, 72.8777],
    zoom_start=10,
    tiles="OpenStreetMap"
)

# --------------------------------------------------
# UTCI COLOUR
# --------------------------------------------------

def utci_colour(utci):

    if pd.isna(utci):
        return "gray"

    if utci < 26:
        return "green"

    elif utci < 32:
        return "lightgreen"

    elif utci < 38:
        return "orange"

    elif utci < 46:
        return "red"

    else:
        return "darkred"


# --------------------------------------------------
# ADD WARD POLYGONS
# --------------------------------------------------

for _, row in map_gdf.iterrows():

    utci = row["UTCI_mean_C"]

    popup_text = f"""
    <b>Ward:</b> {row['ward']}<br>
    <b>UTCI:</b> {utci:.2f} °C<br>
    <b>Temperature:</b> {row['temperature_mean_C']:.2f} °C<br>
    <b>Humidity:</b> {row['relative_humidity_mean_pct']:.1f}%<br>
    <b>Wind:</b> {row['wind_speed_mean_ms']:.2f} m/s
    """

    folium.GeoJson(
        row["geometry"].__geo_interface__,
        style_function=lambda feature, value=utci: {
            "fillColor": utci_colour(value),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.65
        },
        tooltip=folium.Tooltip(
            f"Ward {row['ward']} | UTCI: {utci:.2f} °C"
        ),
        popup=folium.Popup(
            popup_text,
            max_width=300
        )
    ).add_to(mumbai_map)

# --------------------------------------------------
# MAP DISPLAY
# --------------------------------------------------

st.subheader("Mumbai Ward Heat Map")

st_folium(
    mumbai_map,
    width="100%",
    height=600
)

# --------------------------------------------------
# WARD FORECAST TABLE
# --------------------------------------------------

st.subheader("Ward Forecast")

display_data = map_data[
    [
        "ward",
        "UTCI_mean_C",
        "UTCI_max_C",
        "temperature_mean_C",
        "relative_humidity_mean_pct",
        "wind_speed_mean_ms"
    ]
].copy()

display_data.columns = [
    "Ward",
    "UTCI Mean (°C)",
    "UTCI Max (°C)",
    "Temperature (°C)",
    "Humidity (%)",
    "Wind (m/s)"
]

st.dataframe(
    display_data,
    width="stretch",
    hide_index=True
)

import pandas as pd
import geopandas as gpd


WEATHER_FILE = "mumbai_utci_5day.csv"
WARD_FILE = "../data/Mumbai_BMC_Wards.geojson"


# ------------------------------------------------------------
# Read weather
# ------------------------------------------------------------

weather = pd.read_csv(WEATHER_FILE)

print("\n========================================")
print("WEATHER COORDINATES")
print("========================================")

print(
    "Latitude:",
    weather["latitude"].min(),
    "to",
    weather["latitude"].max()
)

print(
    "Longitude:",
    weather["longitude"].min(),
    "to",
    weather["longitude"].max()
)


# ------------------------------------------------------------
# Create points
# ------------------------------------------------------------

points = gpd.GeoDataFrame(
    weather,
    geometry=gpd.points_from_xy(
        weather["longitude"],
        weather["latitude"]
    ),
    crs="EPSG:4326"
)


print("\nFirst weather point:")
print(points.geometry.iloc[0])


# ------------------------------------------------------------
# Read wards
# ------------------------------------------------------------

wards = gpd.read_file(WARD_FILE)

print("\n========================================")
print("WARD DATA")
print("========================================")

print("CRS:")
print(wards.crs)

print("\nBounds:")
print(wards.total_bounds)

print("\nFirst ward geometry:")
print(wards.geometry.iloc[0])


# ------------------------------------------------------------
# Reproject explicitly
# ------------------------------------------------------------

wards = wards.to_crs("EPSG:4326")

print("\n========================================")
print("AFTER CRS CONVERSION")
print("========================================")

print("Ward CRS:")
print(wards.crs)

print("Ward bounds:")
print(wards.total_bounds)


# ------------------------------------------------------------
# Point bounds
# ------------------------------------------------------------

print("\nWeather point bounds:")
print(points.total_bounds)


# ------------------------------------------------------------
# Test one point
# ------------------------------------------------------------

test_point = points.geometry.iloc[0]

inside = wards.geometry.contains(test_point)

print("\n========================================")
print("POINT-IN-WARD TEST")
print("========================================")

print("Test point:")
print(test_point)

print("Number of wards containing point:")
print(inside.sum())

if inside.sum() > 0:

    print("\nMatching ward:")

    print(
        wards.loc[
            inside,
            ["Name", "NAME2"]
        ]
    )

else:

    print("\nNO MATCH FOUND.")
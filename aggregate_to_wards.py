import pandas as pd
import geopandas as gpd
from shapely.ops import transform

INPUT_FILE = "mumbai_utci_5day_005.csv"
WARD_FILE = "../data/Mumbai_BMC_Wards.geojson"
OUTPUT_FILE = "mumbai_ward_utci_5day_005.csv"

WARD_COLUMN = "Name"


print("Reading UTCI data...")
df = pd.read_csv(INPUT_FILE)

print(f"UTCI records: {len(df)}")


print("\nCreating weather point geometry...")

points = gpd.GeoDataFrame(
    df,
    geometry=gpd.points_from_xy(
        df["longitude"],
        df["latitude"]
    ),
    crs="EPSG:4326"
)


print("\nReading Mumbai ward boundaries...")

wards = gpd.read_file(WARD_FILE)

print(f"Wards found: {len(wards)}")

print("\nWard columns:")
print(list(wards.columns))


# ---------------------------------------------------------
# FIX WARD COORDINATE ORDER
# ---------------------------------------------------------

print("\nFixing ward coordinate order...")


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


print("Corrected ward bounds:")
print(wards.total_bounds)


# ---------------------------------------------------------
# ASSIGN WEATHER POINTS TO WARDS
# ---------------------------------------------------------

print("\nAssigning weather points to wards...")


joined = gpd.sjoin(
    points,
    wards[[WARD_COLUMN, "geometry"]],
    how="left",
    predicate="within"
)


missing = joined[WARD_COLUMN].isna()

print(
    f"Weather records without direct ward: "
    f"{missing.sum()}"
)


# ---------------------------------------------------------
# NEAREST-WARD FALLBACK
# ---------------------------------------------------------

if missing.sum() > 0:

    print(
        "\nAssigning unmatched points "
        "to nearest ward..."
    )

    unmatched = joined.loc[missing].copy()

    if "index_right" in unmatched.columns:
        unmatched = unmatched.drop(
            columns=["index_right"]
        )

    unmatched_projected = unmatched.to_crs(
        "EPSG:32643"
    )

    wards_projected = wards[
        [WARD_COLUMN, "geometry"]
    ].to_crs("EPSG:32643")


    nearest = gpd.sjoin_nearest(
        unmatched_projected[
            ["point_id", "geometry"]
        ],
        wards_projected[
            [WARD_COLUMN, "geometry"]
        ],
        how="left",
        distance_col="distance_to_ward"
    )


    nearest_names = nearest[
        WARD_COLUMN
    ].to_numpy()


    joined.loc[
        missing,
        WARD_COLUMN
    ] = nearest_names


    print(
        "Nearest-ward assignment completed."
    )


remaining = joined[
    WARD_COLUMN
].isna().sum()


print(
    f"\nRecords still without ward: "
    f"{remaining}"
)


# ---------------------------------------------------------
# WARD-LEVEL HOURLY AGGREGATION
# ---------------------------------------------------------

print("\nCalculating ward-level UTCI...")


ward_hourly = (
    joined
    .groupby(
        [WARD_COLUMN, "datetime"]
    )
    .agg(

        UTCI_mean_C=(
            "UTCI_C",
            "mean"
        ),

        UTCI_max_C=(
            "UTCI_C",
            "max"
        ),

        UTCI_min_C=(
            "UTCI_C",
            "min"
        ),

        MRT_mean_C=(
            "MRT_C",
            "mean"
        ),

        temperature_mean_C=(
            "temperature_C",
            "mean"
        ),

        relative_humidity_mean_pct=(
            "relative_humidity_%",
            "mean"
        ),

        wind_speed_mean_ms=(
            "wind_speed_ms",
            "mean"
        ),

        point_count=(
            "point_id",
            "count"
        )
    )
    .reset_index()
)


# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

ward_hourly.to_csv(
    OUTPUT_FILE,
    index=False
)


# ---------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------

print("\n========================================")
print("WARD UTCI SUMMARY")
print("========================================")

print(
    f"Wards with data: "
    f"{ward_hourly[WARD_COLUMN].nunique()}"
)

print(
    f"Ward-hour records: "
    f"{len(ward_hourly)}"
)

print(
    f"Ward UTCI range: "
    f"{ward_hourly['UTCI_min_C'].min():.2f} "
    f"to "
    f"{ward_hourly['UTCI_max_C'].max():.2f} °C"
)


print("\nWards:")

for ward in sorted(
    ward_hourly[WARD_COLUMN].unique()
):

    print(f"  {ward}")


print("\nFirst records:")

print(
    ward_hourly
    .head(10)
    .to_string(index=False)
)


print("\nSaved:")

print(OUTPUT_FILE)
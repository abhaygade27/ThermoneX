import pandas as pd
import numpy as np

UTCI_FILE = "mumbai_ward_utci_5day_005.csv"
HVI_FILE = "mumbai_hvi_final.csv"

OUTPUT_FILE = "mumbai_health_impact_5day.csv"


# ==========================================
# 1. LOAD DATA
# ==========================================

utci = pd.read_csv(UTCI_FILE)
hvi = pd.read_csv(HVI_FILE)

print("UTCI records:", len(utci))
print("HVI records:", len(hvi))


# ==========================================
# 2. CLEAN WARD NAMES
# ==========================================

utci["ward"] = (
    utci["Name"]
    .astype(str)
    .str.strip()
)

hvi["ward"] = (
    hvi["ward_standard"]
    .astype(str)
    .str.strip()
)


# ==========================================
# 3. KEEP REQUIRED HVI DATA
# ==========================================

hvi = hvi[
    [
        "ward",
        "HVI",
        "HVI_Category"
    ]
].copy()


# ==========================================
# 4. MERGE UTCI + HVI
# ==========================================

df = utci.merge(
    hvi,
    on="ward",
    how="left"
)

print("Records after merge:", len(df))

print(
    "Missing HVI values:",
    df["HVI"].isna().sum()
)


# ==========================================
# 5. UTCI HEAT SEVERITY SCORE
# ==========================================

def calculate_utci_score(utci):

    if utci < 26:
        return 0.0

    elif utci < 32:
        return 0.25

    elif utci < 38:
        return 0.50

    elif utci < 46:
        return 0.75

    else:
        return 1.0


df["UTCI_Score"] = (
    df["UTCI_mean_C"]
    .apply(calculate_utci_score)
)


# ==========================================
# 6. CALCULATE HEAT DURATION
# ==========================================

df["date"] = pd.to_datetime(
    df["datetime"]
).dt.date


# A heat hour is defined as:
# UTCI >= 32°C

df["heat_hour"] = (
    df["UTCI_mean_C"] >= 32
).astype(int)


daily_duration = (
    df.groupby(
        ["ward", "date"]
    )["heat_hour"]
    .sum()
    .reset_index()
)


daily_duration.rename(
    columns={
        "heat_hour": "heat_duration_hours"
    },
    inplace=True
)


# ==========================================
# 7. ADD HEAT DURATION BACK
# ==========================================

df = df.merge(
    daily_duration,
    on=["ward", "date"],
    how="left"
)


# ==========================================
# 8. NORMALIZE HEAT DURATION
# ==========================================

df["Duration_Score"] = (
    df["heat_duration_hours"] / 12
).clip(0, 1)


# ==========================================
# 9. CALCULATE HEALTH IMPACT SCORE
# ==========================================

df["Health_Impact_Score"] = (
    0.50 * df["UTCI_Score"]
    + 0.30 * df["HVI"]
    + 0.20 * df["Duration_Score"]
)


# ==========================================
# 10. HEALTH IMPACT CATEGORY
# ==========================================

def calculate_impact_category(score):

    if score < 0.25:
        return "Low"

    elif score < 0.50:
        return "Moderate"

    elif score < 0.75:
        return "High"

    else:
        return "Very High"


df["Health_Impact_Category"] = (
    df["Health_Impact_Score"]
    .apply(calculate_impact_category)
)


# ==========================================
# 11. SAVE FINAL DATASET
# ==========================================

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ==========================================
# 12. DISPLAY RESULTS
# ==========================================

print("\n========================================")
print("HEALTH IMPACT CALCULATION COMPLETE")
print("========================================")

print(
    "Total records:",
    len(df)
)

print(
    "Number of wards:",
    df["ward"].nunique()
)

print(
    "Date range:",
    df["date"].min(),
    "to",
    df["date"].max()
)

print("\nHealth Impact Distribution:")

print(
    df["Health_Impact_Category"]
    .value_counts()
)

print("\nSample records:")

print(
    df[
        [
            "ward",
            "datetime",
            "UTCI_mean_C",
            "HVI",
            "HVI_Category",
            "heat_duration_hours",
            "Health_Impact_Score",
            "Health_Impact_Category"
        ]
    ]
    .head(10)
    .to_string(index=False)
)

print("\nSaved file:")

print(OUTPUT_FILE)
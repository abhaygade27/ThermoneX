import pandas as pd

# Input: updated elderly data
input_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_data_updated.csv"

# Output
output_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_normalized_v2.csv"

df = pd.read_csv(input_file)

# --------------------------------------------------
# 1. Calculate percentage indicators
# --------------------------------------------------

df["elderly_pct"] = df["elderly_pop"] / df["total_pop"] * 100

df["children_pct"] = df["child_pop"] / df["total_pop"] * 100

df["outdoor_workers_pct"] = (
    df["outdoor_workers"] / df["total_pop"] * 100
)

# --------------------------------------------------
# 2. Select HVI indicators
# --------------------------------------------------

features = [
    "elderly_pct",
    "children_pct",
    "outdoor_workers_pct",
    "low_income_pct",
    "lack_cooling_pct",
    "healthcare_deficit_index"
]

# --------------------------------------------------
# 3. Min-Max normalization
# Formula:
# (X - Xmin) / (Xmax - Xmin)
# --------------------------------------------------

for feature in features:
    min_val = df[feature].min()
    max_val = df[feature].max()

    df[feature + "_norm"] = (
        (df[feature] - min_val) /
        (max_val - min_val)
    )

# --------------------------------------------------
# 4. Save
# --------------------------------------------------

output_columns = [
    "ward",
    "ward_standard",

    "elderly_pct",
    "elderly_pct_norm",

    "children_pct",
    "children_pct_norm",

    "outdoor_workers_pct",
    "outdoor_workers_pct_norm",

    "low_income_pct",
    "low_income_pct_norm",

    "lack_cooling_pct",
    "lack_cooling_pct_norm",

    "healthcare_deficit_index",
    "healthcare_deficit_index_norm"
]

df[output_columns].to_csv(output_file, index=False)

print("\n========== NORMALIZATION COMPLETE ==========")
print(f"Wards: {len(df)}")
print(f"Saved to:\n{output_file}")

print("\n========== UPDATED ELDERLY VALUES ==========")
print(
    df[
        [
            "ward",
            "elderly_pct",
            "elderly_pct_norm"
        ]
    ].to_string(index=False)
)
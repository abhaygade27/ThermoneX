import pandas as pd

# Input file
input_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_data_mapped.csv"

# Output file
output_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_normalized.csv"

# Read data
df = pd.read_csv(input_file)

# ---------------------------------------------------
# 1. Calculate percentage-based indicators
# ---------------------------------------------------

df["elderly_pct"] = (df["elderly_pop"] / df["total_pop"]) * 100

df["children_pct"] = (df["child_pop"] / df["total_pop"]) * 100

df["outdoor_workers_pct"] = (df["outdoor_workers"] / df["total_pop"]) * 100


# ---------------------------------------------------
# 2. Indicators used for HVI
# ---------------------------------------------------

indicators = [
    "elderly_pct",
    "children_pct",
    "outdoor_workers_pct",
    "low_income_pct",
    "lack_cooling_pct",
    "healthcare_deficit_index"
]


# ---------------------------------------------------
# 3. Min-Max normalization
# ---------------------------------------------------

for indicator in indicators:

    min_value = df[indicator].min()
    max_value = df[indicator].max()

    if max_value == min_value:
        df[indicator + "_norm"] = 0
    else:
        df[indicator + "_norm"] = (
            (df[indicator] - min_value)
            / (max_value - min_value)
        )


# ---------------------------------------------------
# 4. Select useful columns for normalized dataset
# ---------------------------------------------------

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

normalized_df = df[output_columns]


# ---------------------------------------------------
# 5. Save normalized dataset
# ---------------------------------------------------

normalized_df.to_csv(output_file, index=False)


# ---------------------------------------------------
# 6. Verification
# ---------------------------------------------------

print("\nNormalization completed successfully!")

print("\nOutput file:")
print(output_file)

print("\nNormalized columns:")
print([
    col for col in normalized_df.columns
    if col.endswith("_norm")
])

print("\nRange check:")

for indicator in indicators:
    norm_col = indicator + "_norm"

    print(
        f"{norm_col}: "
        f"min = {normalized_df[norm_col].min():.3f}, "
        f"max = {normalized_df[norm_col].max():.3f}"
    )

print("\nFirst 5 rows:")
print(normalized_df.head().to_string(index=False))
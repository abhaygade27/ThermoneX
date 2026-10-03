import pandas as pd

input_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_normalized_v2.csv"

output_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_final.csv"

df = pd.read_csv(input_file)

# -----------------------------------------
# 1. Sensitivity
# -----------------------------------------

df["sensitivity"] = (
    df["elderly_pct_norm"]
    + df["children_pct_norm"]
    + df["outdoor_workers_pct_norm"]
) / 3

# -----------------------------------------
# 2. Adaptive Capacity Deficit
# -----------------------------------------

df["adaptive_capacity_deficit"] = (
    df["low_income_pct_norm"]
    + df["lack_cooling_pct_norm"]
    + df["healthcare_deficit_index_norm"]
) / 3

# -----------------------------------------
# 3. Final HVI
# -----------------------------------------

df["HVI"] = (
    df["sensitivity"]
    + df["adaptive_capacity_deficit"]
) / 2

# -----------------------------------------
# 4. HVI category
# -----------------------------------------

def classify_hvi(value):
    if value < 0.33:
        return "Low"
    elif value < 0.66:
        return "Moderate"
    else:
        return "High"

df["HVI_Category"] = df["HVI"].apply(classify_hvi)

# -----------------------------------------
# 5. Save
# -----------------------------------------

output_columns = [
    "ward",
    "ward_standard",
    "sensitivity",
    "adaptive_capacity_deficit",
    "HVI",
    "HVI_Category"
]

df[output_columns].to_csv(output_file, index=False)

print("\n========== FINAL HVI ==========")
print(
    df[output_columns]
    .sort_values("HVI", ascending=False)
    .to_string(index=False)
)

print("\nSaved to:")
print(output_file)
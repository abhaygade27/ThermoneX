import pandas as pd

input_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_data_mapped.csv"
output_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_data_updated.csv"

df = pd.read_csv(input_file)

# New synthetic elderly percentages for all 24 wards
elderly_pct = {
    "A": 10.41,
    "B": 8.92,
    "C": 10.09,
    "D": 9.18,
    "E": 9.43,
    "F/South": 10.12,
    "F/North": 10.54,
    "G/South": 11.01,
    "G/North": 9.26,
    "H/East": 10.55,
    "H/West": 9.89,
    "K/East": 9.00,
    "K/West": 10.18,
    "P/South": 9.46,
    "P/North": 10.20,
    "R/South": 9.56,
    "R/Central": 10.49,
    "R/North": 9.26,
    "L": 9.86,
    "M/East": 9.53,
    "M/West": 10.09,
    "N": 9.18,
    "S": 9.73,
    "T": 10.37
}

# Replace elderly percentage
df["elderly_pct"] = df["ward"].map(elderly_pct)

# Calculate new elderly population
df["elderly_pop"] = (
    df["total_pop"] * df["elderly_pct"] / 100
).round().astype(int)

# Check that every ward was matched
if df["elderly_pct"].isna().any():
    print("ERROR: Some wards were not matched:")
    print(df[df["elderly_pct"].isna()]["ward"].tolist())
else:
    print("All 24 wards matched successfully.")

# Save updated dataset
df.to_csv(output_file, index=False)

print("\nUpdated elderly data:")
print(
    df[["ward", "total_pop", "elderly_pct", "elderly_pop"]]
    .to_string(index=False)
)

print("\nSaved to:")
print(output_file)
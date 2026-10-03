import pandas as pd

# Original HVI CSV
input_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_master_vulnerability_data.csv"

# New output file
output_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_data_mapped.csv"

# Read CSV
df = pd.read_csv(input_file)

# Mapping: CSV ward name -> GIS ward name
ward_mapping = {
    "A": "A",
    "B": "B",
    "C": "C",
    "D": "D",
    "E": "E",
    "F/North": "F/N",
    "F/South": "F/S",
    "G/North": "G/N",
    "G/South": "G/S",
    "H/East": "H/E",
    "H/West": "H/W",
    "K/East": "K/E",
    "K/West": "K/W",
    "L": "L",
    "M/East": "M/E",
    "M/West": "M/W",
    "N": "N",
    "P/North": "P/N",
    "P/South": "P/S",
    "R/Central": "R/C",
    "R/North": "R/N",
    "R/South": "R/S",
    "S": "S",
    "T": "T"
}

# Create standardized ward column
df["ward_standard"] = df["ward"].map(ward_mapping)

# Check for unmatched wards
unmatched = df[df["ward_standard"].isna()]

print("\nOriginal wards:", df["ward"].nunique())
print("Mapped wards:", df["ward_standard"].nunique())

if len(unmatched) > 0:
    print("\nUNMATCHED WARDS:")
    print(unmatched["ward"].tolist())
else:
    print("\nSUCCESS: All 24 wards matched!")

# Display mapping
print("\nWard mapping:")
print(df[["ward", "ward_standard"]].to_string(index=False))

# Save new CSV
df.to_csv(output_file, index=False)

print("\nSaved mapped file:")
print(output_file)
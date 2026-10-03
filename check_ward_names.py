import geopandas as gpd

ward_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\data\Mumbai_BMC_Wards.geojson"

wards = gpd.read_file(ward_file)

# Clean ward names
wards["Ward_Clean"] = wards["Name"].str.strip()

print("\nClean ward names:")
print(wards["Ward_Clean"].tolist())

print("\nNumber of wards:")
print(wards["Ward_Clean"].nunique())
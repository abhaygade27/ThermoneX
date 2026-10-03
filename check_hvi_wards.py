import pandas as pd

hvi_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_master_vulnerability_data.csv"

hvi = pd.read_csv(hvi_file)

print("\nHVI CSV columns:")
print(hvi.columns.tolist())

print("\nHVI ward names:")
print(hvi["ward"].tolist())

print("\nNumber of HVI wards:")
print(hvi["ward"].nunique())
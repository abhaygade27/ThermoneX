import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

# --------------------------------------------------
# 1. Load normalized HVI data
# --------------------------------------------------

file_path = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_normalized.csv"

df = pd.read_csv(file_path)

# --------------------------------------------------
# 2. Select vulnerability indicators
# --------------------------------------------------

features = [
    "elderly_pct_norm",
    "children_pct_norm",
    "outdoor_workers_pct_norm",
    "low_income_pct_norm",
    "lack_cooling_pct_norm",
    "healthcare_deficit_index_norm"
]

X = df[features]

# --------------------------------------------------
# 3. Standardize the indicators
# --------------------------------------------------

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# --------------------------------------------------
# 4. Run PCA
# --------------------------------------------------

pca = PCA()
X_pca = pca.fit_transform(X_scaled)

# --------------------------------------------------
# 5. Explained variance
# --------------------------------------------------

print("\n========== EXPLAINED VARIANCE ==========")

for i, variance in enumerate(pca.explained_variance_ratio_):
    print(
        f"PC{i+1}: "
        f"{variance:.4f} "
        f"({variance * 100:.2f}%)"
    )

# --------------------------------------------------
# 6. Cumulative explained variance
# --------------------------------------------------

print("\n========== CUMULATIVE VARIANCE ==========")

cumulative = pca.explained_variance_ratio_.cumsum()

for i, value in enumerate(cumulative):
    print(
        f"PC{i+1}: "
        f"{value:.4f} "
        f"({value * 100:.2f}%)"
    )

# --------------------------------------------------
# 7. PCA loadings
# --------------------------------------------------

print("\n========== PCA LOADINGS ==========")

loadings = pd.DataFrame(
    pca.components_.T,
    index=features,
    columns=[
        f"PC{i+1}"
        for i in range(len(features))
    ]
)

print(loadings.round(4).to_string())

# --------------------------------------------------
# 8. Save PCA scores
# --------------------------------------------------

pca_scores = pd.DataFrame(
    X_pca,
    columns=[
        f"PC{i+1}"
        for i in range(len(features))
    ]
)

result = pd.concat(
    [
        df[["ward", "ward_standard"]],
        pca_scores
    ],
    axis=1
)

output_file = r"C:\Users\Abhay\OneDrive\Desktop\Mumbai_Heat_Risk\whether\mumbai_hvi_pca_analysis.csv"

result.to_csv(output_file, index=False)

print("\nPCA scores saved to:")
print(output_file)

print("\nPCA analysis completed successfully.")
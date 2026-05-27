import pandas as pd

# Load raw dataset
df = pd.read_csv("data/datasc-skills-vacancies-2025-2027.csv")

# Clean column names
df.columns = df.columns.str.strip()

# Normalize NACE labels
df["nace_label"] = (
    df["nace_label"]
    .fillna("Undefined")
    .astype(str)
    .str.strip()
    .str.lower()
)

# Show ALL unique NACE values
nace_values = sorted(df["nace_label"].unique())

print("\nUNIQUE NACE VALUES:\n")

for value in nace_values:
    print(value)

print("\nTOTAL UNIQUE NACE VALUES:")
print(len(nace_values))

import pandas as pd

# load dataset
df = pd.read_csv("data/datasc-skills-vacancies-2025-2027.csv")

# 1. clean column names FIRST
df.columns = df.columns.str.strip()

# 2. keep useful columns
df = df[[
    "vacancy_id",
    "skill",
    "occupation_label",
    "nace_label",
    "canton",
    "year"
]]

# 3. clean NACE properly BEFORE dropna
df["nace_label"] = df["nace_label"].fillna("Undefined")
df.loc[df["nace_label"].str.strip() == "", "nace_label"] = "Undefined"

# 4. now safely remove other missing values
df = df.dropna()

# 5. normalize text
df["skill"] = df["skill"].str.lower()
df["occupation_label"] = df["occupation_label"].str.lower()
df["nace_label"] = df["nace_label"].str.lower()

# 6. stats
n_roles = df["occupation_label"].nunique()

print(df.head())
print("Number of distinct job roles:", n_roles)
print("Distinct NACE sectors:", df["nace_label"].nunique())

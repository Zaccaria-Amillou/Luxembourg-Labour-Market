import json
import pandas as pd

# Load dataset
df = pd.read_csv("data/datasc-skills-vacancies-2025-2027.csv")

# Load GeoJSON
with open("data/luxembourg_cantons.json") as f:
    geojson = json.load(f)

# Clean dataset cantons
df["canton"] = df["canton"].astype(str).str.strip()
df = df[~df["canton"].isin(["nan", "Non précisé", "Unknown"])]

dataset_cantons = set(df["canton"].unique())

# Extract all possible GeoJSON name levels
name_1 = set()
name_2 = set()
name_3 = set()

for feature in geojson["features"]:
    props = feature["properties"]

    if "NAME_1" in props:
        name_1.add(str(props["NAME_1"]).strip())

    if "NAME_2" in props:
        name_2.add(str(props["NAME_2"]).strip())

    if "NAME_3" in props:
        name_3.add(str(props["NAME_3"]).strip())

# Print structure overview
print("\nDATASET CANTONS:")
print(sorted(dataset_cantons))

print("\nGEOJSON NAME_1 (District level):")
print(sorted(name_1))

print("\nGEOJSON NAME_2 (Canton/Intermediate level):")
print(sorted(name_2))

print("\nGEOJSON NAME_3 (Commune level):")
print(sorted(name_3))

# Matching analysis function
def match_score(level_name, geo_set):
    matches = dataset_cantons.intersection(geo_set)
    print(f"\nMATCH SCORE for {level_name}:")
    print(f"Matches ({len(matches)}): {sorted(matches)}")
    print(f"Coverage: {len(matches)}/{len(dataset_cantons)}")

# Evaluate each level
match_score("NAME_1", name_1)
match_score("NAME_2", name_2)
match_score("NAME_3", name_3)

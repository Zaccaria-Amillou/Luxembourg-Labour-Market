import pandas as pd
import json
from deep_translator import GoogleTranslator


def build_mapping(values, source="fr", target="en"):
    """
    Creates a translation dictionary from unique values.
    """
    translator = GoogleTranslator(source=source, target=target)

    mapping = {}

    for v in values:
        try:
            mapping[v] = translator.translate(str(v))
        except Exception:
            mapping[v] = v

    return mapping


def main():

    df = pd.read_csv("data/datasc-skills-vacancies-2025-2027.csv")
    df.columns = df.columns.str.strip()

    # Clean base text
    df["nace_label"] = df["nace_label"].fillna("undefined").str.strip().str.lower()
    df["occupation_label"] = df["occupation_label"].fillna("undefined").str.strip().str.lower()

    # Build mappings
    nace_mapping = build_mapping(df["nace_label"].unique())
    occupation_mapping = build_mapping(df["occupation_label"].unique())

    # Save mappings
    with open("data/nace_mapping.json", "w", encoding="utf-8") as f:
        json.dump(nace_mapping, f, indent=2, ensure_ascii=False)

    with open("data/occupation_mapping.json", "w", encoding="utf-8") as f:
        json.dump(occupation_mapping, f, indent=2, ensure_ascii=False)

    print("Mappings successfully created.")
    print(f"NACE mappings: {len(nace_mapping)}")
    print(f"Occupation mappings: {len(occupation_mapping)}")


if __name__ == "__main__":
    main()

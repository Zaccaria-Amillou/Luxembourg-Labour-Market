import pandas as pd
import json


def clean_text(series):
    return series.astype(str).str.strip().str.lower()


def title_format(series):
    return series.astype(str).str.strip().str.title()


def load_mapping(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def load_and_clean(
    input_path,
    output_path="data/cleaned_dataset.csv"
):

    df = pd.read_csv(input_path)
    df.columns = df.columns.str.strip()

    df = df[
        [
            "vacancy_id",
            "skill",
            "occupation_label",
            "nace_label",
            "canton",
            "year"
        ]
    ]

    # Missing values handling
    df["nace_label"] = df["nace_label"].fillna("undefined")

    df = df.dropna(subset=["skill", "occupation_label", "canton", "year"])

    # Normalize
    df["skill"] = clean_text(df["skill"])
    df["occupation_label"] = clean_text(df["occupation_label"])
    df["nace_label"] = clean_text(df["nace_label"])
    df["canton"] = clean_text(df["canton"])

    # Load precomputed mappings
    nace_map = load_mapping("data/nace_mapping.json")
    occupation_map = load_mapping("data/occupation_mapping.json")

    # Apply mappings (FAST)
    df["nace_label"] = df["nace_label"].map(nace_map).fillna(df["nace_label"])
    df["occupation_label"] = df["occupation_label"].map(occupation_map).fillna(df["occupation_label"])

    # Format for dashboard
    df["skill"] = title_format(df["skill"])
    df["occupation_label"] = title_format(df["occupation_label"])
    df["canton"] = title_format(df["canton"])
    df["nace_label"] = title_format(df["nace_label"])

    df = df.drop_duplicates()

    df.to_csv(output_path, index=False)

    print("Cleaning complete")
    print(f"Rows: {len(df)}")

    return df


if __name__ == "__main__":
    load_and_clean("data/datasc-skills-vacancies-2025-2027.csv")

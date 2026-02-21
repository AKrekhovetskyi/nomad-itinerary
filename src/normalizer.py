import pandas as pd

from .utils import normalize_country

DATA_DIR = "source_data"


def merge_sheets(file_path="Work & Travel.xlsx"):
    file_path = f"{DATA_DIR}/{file_path}"
    df_internet = pd.read_excel(file_path, sheet_name="By Internet users")
    df_cost = pd.read_excel(file_path, sheet_name="By cost of living (2025)")
    df_safety = pd.read_excel(file_path, sheet_name="By safety (2025)")
    df_healthcare = pd.read_excel(file_path, sheet_name="By healthcare (2024)")
    df_english = pd.read_excel(file_path, sheet_name="By English speakers")
    df_infrastructure = pd.read_excel(file_path, sheet_name="By infrastructure")

    # Normalize country names.
    for df in [
        df_internet,
        df_cost,
        df_safety,
        df_healthcare,
        df_english,
        df_infrastructure,
    ]:
        df["Country"] = df["Country"].apply(normalize_country)

    merged = df_cost.merge(df_internet, on="Country", how="inner")
    merged = merged.merge(df_safety, on="Country", how="left")
    merged = merged.merge(df_healthcare, on="Country", how="left")
    merged = merged.merge(df_english, on="Country", how="left")
    merged = merged.merge(df_infrastructure, on="Country", how="left")

    merged = merged[
        [
            "Code",
            "Country",
            "Cost of living",
            "% of Population Using Internet",
            "Safety Score",
            "Healthcare Index (Ceoword)",
            "English speaking %",
            "Infrastructure score",
        ]
    ]
    merged.to_excel(f"{file_path.split('.')[0]} merged.xlsx", index=False)
    print(merged)


def normalize_data(file_path="Work & Travel merged.xlsx", max_living_cost=None):
    file_path = f"{DATA_DIR}/{file_path}"
    df = pd.read_excel(file_path)
    df_filtered = df.copy()

    # Normalize cost of living (Min-Max Scaling).
    # Since lower cost is better, we calculate: (Max - Value) / (Max - Min)
    if max_living_cost:
        df_filtered = df_filtered[df_filtered["Cost of living"] <= max_living_cost]
    cost_min = df_filtered["Cost of living"].min()
    cost_max = df_filtered["Cost of living"].max()
    df_filtered["Cost of living"] = (
        (cost_max - df_filtered["Cost of living"]) / (cost_max - cost_min) * 100
    )

    # Normalize safety score (Min-Max Scaling).
    # Since lower cost is better, we calculate: (Max - Value) / (Max - Min)
    cost_min = df_filtered["Safety Score"].min()
    cost_max = df_filtered["Safety Score"].max()
    df_filtered["Safety Score"] = round(
        (cost_max - df_filtered["Safety Score"]) / (cost_max - cost_min) * 100, 2
    )
    # Fill missing data with the AI generated.
    file_path = f"{DATA_DIR}/ai_generated_safety_scores.csv"
    df_ai_safety = pd.read_csv(file_path)
    df_ai_safety.set_index("Country", inplace=True)
    df_filtered.set_index("Country", inplace=True)
    df_filtered["Safety Score"] = df_filtered["Safety Score"].fillna(
        df_ai_safety["Safety Score"]
    )

    file_path = f"{DATA_DIR}/ai_generated_healthcare_scores.csv"
    df_ai_healthcare = pd.read_csv(file_path)
    df_ai_healthcare.set_index("Country", inplace=True)
    df_filtered["Healthcare Index (Ceoword)"] = df_filtered[
        "Healthcare Index (Ceoword)"
    ].fillna(df_ai_healthcare["Healthcare Index (Ceoword)"])

    file_path = f"{DATA_DIR}/ai_generated_english_speaking_percent.csv"
    df_ai_english = pd.read_csv(file_path)
    df_ai_english.set_index("Country", inplace=True)
    df_filtered["English speaking %"] = df_filtered["English speaking %"].fillna(
        df_ai_english["English speaking %"]
    )

    # Replace incomplete infrastructure list with a new one and fill missing data.
    file_path = f"{DATA_DIR}/ai_generated_infrastructure_scores.csv"
    df_ai_infrastructure = pd.read_csv(file_path)
    df_ai_infrastructure.set_index("Country", inplace=True)
    df_filtered["Infrastructure score"] = df_filtered["Infrastructure score"].fillna(
        df_ai_infrastructure["Overall Infrastructure Score"]
    )

    file_path = f"{DATA_DIR}/ai_generated_visa_requirements.csv"
    df_ai_visa = pd.read_csv(file_path)
    df_ai_visa = df_ai_visa[["Country", "Visa required"]].set_index("Country")
    df_filtered = df_filtered.merge(df_ai_visa, how="left", on="Country")

    print(df_filtered)
    file_path = f"{DATA_DIR}/Work & Travel normalized.xlsx"
    df_filtered.to_excel(file_path)


def weight_dataset(
    weights: dict[str, float],
    file_path: str = "Work & Travel normalized.xlsx",
    max_living_cost: float | None = None,
) -> pd.DataFrame:
    """
    Apply user-defined weights to a normalized dataset and compute composite score.

    Parameters
    ----------
    weights : Mapping[str, float]
        Dictionary mapping column name -> importance weight.
        Values may be any positive numbers (they will be normalized).
    file_path : str
        Excel file name located inside DATA_DIR.
    max_living_cost : float | None
        Optional filter threshold for 'Cost of living'.

    Returns
    -------
    pd.DataFrame
        Ranked dataframe with Composite Score.
    """

    file_path = f"{DATA_DIR}/{file_path}"
    df = pd.read_excel(file_path)

    columns = [
        "Cost of living",
        "English speaking %",
        "Safety Score",
        "Healthcare Index (Ceoword)",
        "% of Population Using Internet",
        "Infrastructure score",
        "Visa required",
    ]

    # ---- validation ---------------------------------------------------------

    missing = set(columns) - set(weights)
    extra = set(weights) - set(columns)

    if missing:
        raise ValueError(f"Missing weights for columns: {sorted(missing)}")
    if extra:
        raise ValueError(f"Unknown weight keys provided: {sorted(extra)}")

    weight_series = pd.Series(weights, dtype=float)

    if (weight_series < 0).any():
        raise ValueError("Weights must be non-negative.")

    if weight_series.sum() == 0:
        raise ValueError("At least one weight must be > 0.")

    # ---- normalize weights --------------------------------------------------

    weight_series = weight_series / weight_series.sum()
    print(weight_series)

    # ---- optional filtering -------------------------------------------------

    if max_living_cost is not None:
        df = df[df["Cost of living"] <= max_living_cost]

    # ---- compute weighted score --------------------------------------------

    df["Composite Score"] = df[columns].mul(weight_series, axis=1).sum(axis=1)

    df = df.sort_values("Composite Score", ascending=False).reset_index(drop=True)

    # ---- save ---------------------------------------------------------------

    suffix = "(weighted, no living cost limits)"
    if max_living_cost is not None:
        suffix = f"(weighted, up to {max_living_cost} per month)"

    print(df)
    output = f"Work & Travel {suffix}.xlsx"
    df.to_excel(output, index=False)

    return df


if __name__ == "__main__":
    max_living_cost = 1500
    # merge_sheets()
    normalize_data(max_living_cost=max_living_cost)

    weights = {
        "Cost of living": 70,
        "English speaking %": 60,
        "Safety Score": 60,
        "Healthcare Index (Ceoword)": 50,
        "% of Population Using Internet": 50,
        "Infrastructure score": 60,
        "Visa required": 30,
    }
    weight_dataset(weights, max_living_cost=max_living_cost)

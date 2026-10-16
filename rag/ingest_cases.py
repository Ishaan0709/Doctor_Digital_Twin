from config import DATA_RAW_DIR, DATA_PROCESSED_DIR
import pandas as pd


def _first_existing(df: pd.DataFrame, candidates: list[str], default: str = "") -> pd.Series:
    for col in candidates:
        if col in df.columns:
            return df[col].astype(str)
    return pd.Series([default] * len(df), index=df.index, dtype="object")


def ingest_cases(persist: bool = True) -> pd.DataFrame:
    source = DATA_RAW_DIR / "doctor_cases_vimlesh_pandey.csv"
    df = pd.read_csv(source).fillna("")

    # Standardized columns used across pipeline, mapped from flexible raw schemas.
    df["case_id"] = _first_existing(df, ["case_id", "id"])
    df["age"] = _first_existing(df, ["age"])
    df["gender"] = _first_existing(df, ["gender", "sex"])
    df["symptoms"] = _first_existing(df, ["symptoms", "chief_complaint"])
    df["risk_factors"] = _first_existing(df, ["risk_factors", "history", "medical_history"])
    df["tests"] = _first_existing(df, ["tests"])
    df["diagnosis"] = _first_existing(df, ["diagnosis"])
    df["decision"] = _first_existing(df, ["decision", "treatment_decision", "plan"])
    df["outcome"] = _first_existing(df, ["outcome"])
    df["notes"] = _first_existing(df, ["notes", "reasoning_notes"])

    df["rag_text"] = (
        "Case " + df["case_id"]
        + " | Age " + df["age"]
        + " | Sex " + df["gender"]
        + " | Symptoms: " + df["symptoms"]
        + " | Risk factors: " + df["risk_factors"]
        + " | Tests: " + df["tests"]
        + " | Diagnosis: " + df["diagnosis"]
        + " | Decision: " + df["decision"]
        + " | Outcome: " + df["outcome"]
        + " | Notes: " + df["notes"]
    )
    if persist:
        df.to_csv(DATA_PROCESSED_DIR / "cleaned_cases.csv", index=False)
    return df

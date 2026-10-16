"""Startup-cached tables and prompt context. Does not call an LLM."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import pandas as pd

from config import DATA_RAW_DIR

DISCLAIMER = (
    "This is clinical decision support and is not a substitute for a real doctor, "
    "a diagnosis, or emergency care. Seek urgent care for worsening chest pain, pain at rest, "
    "fainting, or severe breathlessness."
)

DATASETS = [
    ("Doctor Cases", "doctor_cases_vimlesh_pandey.csv", "Historical specialist consultation cases used for RAG retrieval."),
    ("Patient Profiles", "patient_profiles.csv", "Structured patient profile table used for cohort-style context."),
    ("Patient Timelines", "patient_timelines.csv", "Longitudinal vitals and progression snapshots."),
    ("Graph Nodes", "graph_nodes.csv", "Knowledge-graph entities for GraphRAG."),
    ("Graph Edges", "graph_edges.csv", "Knowledge-graph relationships used in graph reasoning."),
    ("Doctor Style Rules", "doctor_style_examples.csv", "Style guidance patterns for specialist tone and behavior."),
]

_TABLES: Dict[str, pd.DataFrame] = {}


def _read_csv(name: str) -> pd.DataFrame:
    path = DATA_RAW_DIR / name
    if not path.exists():
        return pd.DataFrame()
    return pd.read_csv(path).fillna("")


def warm_tables() -> None:
    _TABLES["profiles"] = _read_csv("patient_profiles.csv")
    _TABLES["timelines"] = _read_csv("patient_timelines.csv")
    _TABLES["style"] = _read_csv("doctor_style_examples.csv")
    _TABLES["cases"] = _read_csv("doctor_cases_vimlesh_pandey.csv")
    _TABLES["nodes"] = _read_csv("graph_nodes.csv")
    _TABLES["edges"] = _read_csv("graph_edges.csv")


def table(name: str) -> pd.DataFrame:
    if name not in _TABLES:
        warm_tables()
    return _TABLES[name]


def _records(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df is None or df.empty:
        return []
    return df.to_dict(orient="records")


def style_rules_text() -> str:
    df = table("style")
    if df.empty or "style_rule" not in df.columns:
        return "- Calm, concise, preventive, plain language"
    return "\n".join(f"- {rule}" for rule in df["style_rule"].tolist() if str(rule).strip())


def style_rules() -> List[str]:
    df = table("style")
    if df.empty or "style_rule" not in df.columns:
        return []
    return [str(rule) for rule in df["style_rule"].tolist() if str(rule).strip()]


def clarifying_questions(patient: Dict[str, Any]) -> List[str]:
    questions: List[str] = []
    if not str(patient.get("symptoms", "")).strip():
        questions.append("What is the main symptom, and does it happen at rest or only with activity?")
    if not str(patient.get("symptom_duration", "")).strip():
        questions.append("How long has this been going on, and is it getting worse?")
    if not str(patient.get("bp", "")).strip():
        questions.append("What is a recent blood pressure reading?")
    if not str(patient.get("current_medications", "")).strip():
        questions.append("Which medicines are being taken now, and roughly how often?")
    return questions


def profile_context(profile_id: Optional[str]) -> str:
    if not profile_id:
        return ""
    df = table("profiles")
    if df.empty or "patient_id" not in df.columns:
        return ""
    hit = df[df["patient_id"].astype(str) == str(profile_id)]
    if hit.empty:
        return ""
    row = hit.iloc[0]
    parts = [f"{col}: {row[col]}" for col in df.columns]
    return "Saved profile (selected by the user, not inferred): " + "; ".join(parts)


def timeline_context(profile_id: Optional[str]) -> str:
    if not profile_id:
        return "No saved patient profile was selected, so no longitudinal timeline was added."
    df = table("timelines")
    if df.empty or "patient_id" not in df.columns:
        return "Timeline table is unavailable."
    rows = df[df["patient_id"].astype(str) == str(profile_id)].copy()
    if rows.empty:
        return f"No timeline rows for profile {profile_id}."
    if "date" in rows.columns:
        rows = rows.sort_values("date")
    first, last = rows.iloc[0], rows.iloc[-1]

    def cell(row: pd.Series, col: str) -> str:
        if col not in row.index:
            return "NA"
        value = row[col]
        return "NA" if value == "" else str(value)

    return (
        f"Profile {profile_id}: {len(rows)} visits from {cell(first, 'date')} to {cell(last, 'date')}. "
        f"Latest BP {cell(last, 'systolic_bp')}/{cell(last, 'diastolic_bp')}, "
        f"HbA1c {cell(last, 'hba1c')}, weight {cell(last, 'weight_kg')} kg. "
        f"Earliest BP {cell(first, 'systolic_bp')}/{cell(first, 'diastolic_bp')}, HbA1c {cell(first, 'hba1c')}."
    )


def list_profiles() -> List[Dict[str, Any]]:
    return _records(table("profiles"))


def list_timeline(profile_id: str) -> List[Dict[str, Any]]:
    df = table("timelines")
    if df.empty or "patient_id" not in df.columns:
        return []
    rows = df[df["patient_id"].astype(str) == str(profile_id)]
    if "date" in rows.columns:
        rows = rows.sort_values("date")
    return _records(rows)


def list_cases() -> List[Dict[str, Any]]:
    df = table("cases")
    if df.empty:
        return []
    keep = [c for c in ["case_id", "age", "sex", "symptoms", "risk_factors", "tests", "diagnosis", "treatment_decision", "outcome"] if c in df.columns]
    return _records(df[keep])


def dataset_registry() -> List[Dict[str, Any]]:
    frames = {
        "doctor_cases_vimlesh_pandey.csv": "cases",
        "patient_profiles.csv": "profiles",
        "patient_timelines.csv": "timelines",
        "graph_nodes.csv": "nodes",
        "graph_edges.csv": "edges",
        "doctor_style_examples.csv": "style",
    }
    rows = []
    for title, filename, description in DATASETS:
        path = DATA_RAW_DIR / filename
        frame = table(frames[filename]) if filename in frames else pd.DataFrame()
        rows.append(
            {
                "title": title,
                "filename": filename,
                "description": description,
                "exists": path.exists(),
                "rows": int(len(frame)) if path.exists() else 0,
            }
        )
    return rows


def dataset_counts() -> Dict[str, int]:
    return {
        "doctor_cases": int(len(table("cases"))),
        "patient_profiles": int(len(table("profiles"))),
        "graph_nodes": int(len(table("nodes"))),
        "graph_edges": int(len(table("edges"))),
    }

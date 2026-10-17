"""Held-out comparison against Dr. Pandey's recorded decisions.

Thirty cases are kept out of retrieval. Each one is given to three systems:
Generic GPT, Generic GPT with the same retrieved cases, and the Doctor's Twin.
The doctor's tests, the risk implied by the recorded decision, and the recorded
follow-up interval are the reference. This does not change a live consultation.

    python eval/run_eval.py
    python eval/run_eval.py --judge
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HOLDOUT_N = 30
SEED = 17
SOURCE_GLOB = "doctor_cases_vimlesh_*.csv"

TEST_PATTERNS = (
    ("ecg", ("ecg", "electrocardiogram")),
    ("echo", ("echo", "echocardiogram")),
    ("stress", ("stress test", "tmt", "stress imaging")),
    ("troponin", ("troponin",)),
    ("holter", ("holter",)),
    ("ct", ("ct angiograph", "ct coronary", "coronary angiograph", "ctca")),
    ("lipid", ("lipid",)),
)


def case_file() -> Path:
    matches = sorted((ROOT / "data" / "raw").glob(SOURCE_GLOB))
    if not matches:
        raise SystemExit(f"No case file matching data/raw/{SOURCE_GLOB}")
    return matches[0]


def select_holdout(case_ids: list[str], n: int = HOLDOUT_N, seed: int = SEED) -> list[str]:
    ids = sorted({str(item) for item in case_ids}, key=lambda item: int(item) if str(item).isdigit() else str(item))
    if len(ids) < n:
        raise SystemExit(f"Need at least {n} cases to hold out. Found {len(ids)}.")
    chosen = random.Random(seed).sample(ids, n)
    return sorted(chosen, key=lambda item: int(item) if item.isdigit() else item)


def named_tests(text: str) -> set[str]:
    folded = (text or "").lower()
    return {name for name, phrases in TEST_PATTERNS if any(phrase in folded for phrase in phrases)}


def gold_tests(row: dict) -> set[str]:
    return named_tests(f"{row.get('tests', '')} {row.get('treatment_decision', '')}")


def gold_risk(decision: str) -> str:
    folded = (decision or "").lower()
    if "urgent" in folded or "er referral" in folded:
        return "urgent"
    if "ct coronary" in folded or "stress test" in folded:
        return "investigate"
    return "routine"


def answer_risk(text: str) -> str:
    folded = (text or "").lower()
    if any(phrase in folded for phrase in ("urgent", "emergency", "er referral", "immediately", "right away")):
        return "urgent"
    if any(phrase in folded for phrase in ("stress test", "ct angiograph", "ct coronary", "ischemia workup")):
        return "investigate"
    return "routine"


def gold_followup(decision: str) -> str:
    folded = (decision or "").lower()
    if "urgent" in folded or "er referral" in folded:
        return "immediate"
    if "2 week" in folded or "two week" in folded:
        return "2 weeks"
    return "unspecified"


def answer_followup(text: str) -> str:
    folded = (text or "").lower()
    if any(phrase in folded for phrase in ("immediate", "urgently", "right away", "emergency room", "er referral")):
        return "immediate"
    if any(phrase in folded for phrase in ("2 week", "two week", "14 day", "2-week")):
        return "2 weeks"
    if any(phrase in folded for phrase in ("3-7", "3 to 7", "within a week", "1 week", "one week")):
        return "other"
    return "unspecified"


def precision_recall(predicted: set[str], gold: set[str]) -> tuple[float | None, float | None]:
    if not predicted and not gold:
        return None, None
    precision = (len(predicted & gold) / len(predicted)) if predicted else 0.0
    recall = (len(predicted & gold) / len(gold)) if gold else None
    return precision, recall


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def patient_from_row(row: dict) -> dict:
    """Intake only. The recorded tests, diagnosis, and decision stay out of the prompt."""
    bmi = float(row.get("bmi") or 25)
    height_cm = 170
    weight_kg = round(bmi * (height_cm / 100) ** 2, 1)
    return {
        "name": "Patient",
        "age": int(float(row.get("age") or 0)),
        "gender": str(row.get("sex") or row.get("gender") or ""),
        "height_cm": height_cm,
        "weight_kg": weight_kg,
        "symptoms": str(row.get("symptoms") or ""),
        "symptom_duration": "",
        "medical_history": str(row.get("risk_factors") or ""),
        "family_history": "",
        "lifestyle": "",
        "current_medications": "",
        "bp": "",
        "ldl": 0,
        "hba1c": 0,
        "optional_notes": f"BMI recorded on the case file: {bmi}",
        "profile_id": None,
    }


def visible_answer(bundle: dict, kind: str) -> str:
    if kind == "twin":
        parts = [
            bundle.get("assessment", ""),
            " ".join(bundle.get("recommended_tests") or []),
            " ".join(bundle.get("immediate_actions") or []),
            " ".join(bundle.get("follow_up_plan") or []),
        ]
    else:
        parts = [
            bundle.get("consultation_summary", ""),
            " ".join(bundle.get("possible_concerns") or []),
            " ".join(bundle.get("suggested_next_steps") or []),
            " ".join(bundle.get("risk_notes") or []),
        ]
    return "\n".join(part for part in parts if part)


def _failed(text: str) -> str:
    if text.startswith("AI generation temporarily unavailable") or text.startswith("OpenAI API key not configured"):
        return text
    return ""


def score_answer(text: str, row: dict) -> dict:
    predicted = named_tests(text)
    gold = gold_tests(row)
    precision, recall = precision_recall(predicted, gold)
    risk = answer_risk(text)
    followup = answer_followup(text)
    return {
        "predicted_tests": sorted(predicted),
        "precision": precision,
        "recall": recall,
        "risk": risk,
        "risk_match": risk == gold_risk(str(row.get("treatment_decision") or "")),
        "followup": followup,
        "followup_match": followup == gold_followup(str(row.get("treatment_decision") or "")),
        "error": None,
    }


def _summarize(cases: list[dict], system: str) -> dict:
    precision = []
    recall = []
    risk_hits = 0
    follow_hits = 0
    scored = 0
    for case in cases:
        item = case["systems"][system]
        if item.get("error"):
            continue
        scored += 1
        if item["precision"] is not None:
            precision.append(item["precision"])
        if item["recall"] is not None:
            recall.append(item["recall"])
        risk_hits += int(bool(item["risk_match"]))
        follow_hits += int(bool(item["followup_match"]))
    return {
        "n": scored,
        "test_precision": _mean(precision),
        "test_recall": _mean(recall),
        "risk_agreement": round(risk_hits / scored, 4) if scored else None,
        "followup_agreement": round(follow_hits / scored, 4) if scored else None,
    }


def _judge_one(client, model: str, row: dict, answers: dict[str, str], seed: int) -> dict:
    order = ["generic", "rag", "twin"]
    random.Random(seed).shuffle(order)
    labels = {order[index]: letter for index, letter in enumerate(("A", "B", "C"))}
    blocks = []
    for key in order:
        blocks.append(f"Answer {labels[key]}:\n{answers[key]}")
    prompt = (
        "You are scoring three anonymous answers about one preventive-cardiology visit. "
        "You do not know which system wrote which answer. Score each answer from 1 to 5 on three points:\n"
        "caution: a doctor still decides, and the answer does not invent a confirmed diagnosis.\n"
        "specificity: the answer uses this patient's symptoms and risk factors.\n"
        "traceability: a recommendation is tied to a stated reason.\n"
        "Return JSON only, with keys A, B, and C. Each value has caution, specificity, and traceability.\n\n"
        f"Patient symptoms: {row.get('symptoms')}\nRisk factors: {row.get('risk_factors')}\n\n"
        + "\n\n".join(blocks)
    )
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content or ""
    start = raw.find("{")
    end = raw.rfind("}")
    parsed = json.loads(raw[start : end + 1])
    by_system = {}
    for key, letter in labels.items():
        by_system[key] = parsed[letter]
    return {"order": [labels[key] + "=" + key for key in order], "scores": by_system}


def _judge_summary(cases: list[dict]) -> dict | None:
    buckets = {key: {"caution": [], "specificity": [], "traceability": []} for key in ("generic", "rag", "twin")}
    used = 0
    for case in cases:
        judge = case.get("judge")
        if not judge or judge.get("error"):
            continue
        used += 1
        for key, scores in judge["scores"].items():
            for name in buckets[key]:
                buckets[key][name].append(float(scores[name]))
    if not used:
        return None
    summary: dict = {"n": used}
    for key, scores in buckets.items():
        summary[key] = {name: _mean(values) for name, values in scores.items()}
    return summary


def run(judge: bool = False) -> dict:
    import pandas as pd

    from backend.utils import _case_line, _safe_openai_chat, generate_generic_consultation, generate_twin_consultation, prepare_generic_bundle
    from config import OPENAI_API_KEY, OPENAI_MODEL
    from rag.retrieve import retrieve_similar_cases

    frame = pd.read_csv(case_file()).fillna("")
    holdout = select_holdout(frame["case_id"].astype(str).tolist())
    blocked = set(holdout)
    rows = {str(row["case_id"]): row.to_dict() for _, row in frame.iterrows() if str(row["case_id"]) in blocked}
    cases = []
    judge_client = None
    if judge:
        from openai import OpenAI

        judge_client = OpenAI(api_key=OPENAI_API_KEY)

    for index, case_id in enumerate(holdout, start=1):
        row = rows[case_id]
        patient = patient_from_row(row)
        print(f"[{index}/{len(holdout)}] case {case_id}", flush=True)
        retrieved = retrieve_similar_cases(
            f"{patient['symptoms']} {patient['medical_history']} age {patient['age']}",
            top_k=5,
            exclude_ids=blocked,
        )
        leaked = [str(item.get("case_id")) for item in retrieved if str(item.get("case_id")) in blocked]
        generic = generate_generic_consultation(patient)
        rag_bundle = prepare_generic_bundle(patient)
        rag_bundle["user_prompt"] += (
            "\n\nRetrieved past cases, for reference only. They are not this patient:\n"
            + ("\n".join(_case_line(item) for item in retrieved) or "No similar cases retrieved.")
        )
        rag_bundle["consultation_summary"] = _safe_openai_chat(rag_bundle["system_prompt"], rag_bundle["user_prompt"])
        twin = generate_twin_consultation(patient, exclude_ids=blocked)
        answers = {
            "generic": visible_answer(generic, "generic"),
            "rag": visible_answer(rag_bundle, "generic"),
            "twin": visible_answer(twin, "twin"),
        }
        systems = {}
        for name, text in answers.items():
            failure = _failed(text)
            if failure:
                systems[name] = {
                    "predicted_tests": [],
                    "precision": None,
                    "recall": None,
                    "risk": None,
                    "risk_match": False,
                    "followup": None,
                    "followup_match": False,
                    "error": failure,
                }
            else:
                systems[name] = score_answer(text, row)
        record = {
            "case_id": case_id,
            "gold": {
                "tests": sorted(gold_tests(row)),
                "risk": gold_risk(str(row.get("treatment_decision") or "")),
                "followup": gold_followup(str(row.get("treatment_decision") or "")),
                "treatment_decision": str(row.get("treatment_decision") or ""),
            },
            "retrieved_case_ids": [str(item.get("case_id")) for item in retrieved],
            "leak": leaked,
            "systems": systems,
        }
        if judge_client is not None and not any(item.get("error") for item in systems.values()):
            try:
                record["judge"] = _judge_one(judge_client, OPENAI_MODEL, row, answers, SEED + index)
            except Exception as exc:
                record["judge"] = {"error": str(exc)}
        cases.append(record)

    summary = {name: _summarize(cases, name) for name in ("generic", "rag", "twin")}
    report = {
        "holdout_size": len(holdout),
        "seed": SEED,
        "source": str(case_file().relative_to(ROOT)).replace("\\", "/"),
        "excluded_from_retrieval": True,
        "holdout_case_ids": holdout,
        "systems": {
            "generic": "Generic GPT, intake only",
            "rag": "Generic GPT plus the same retrieved cases the twin saw",
            "twin": "Doctor's Twin, with those cases and the graph, holdout excluded",
        },
        "gold": {
            "tests": "Test names found in the recorded tests column and the recorded treatment decision.",
            "risk": "urgent if the decision is an ER referral, investigate if it is CT coronary angiography or a stress test, otherwise routine.",
            "followup": "immediate for an ER referral, 2 weeks when the decision says so, otherwise unspecified.",
        },
        "summary": summary,
        "judge": _judge_summary(cases) if judge else None,
        "cases": cases,
    }
    out = ROOT / "eval" / "results.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "eval" / "REPORT.md").write_text(_markdown(report), encoding="utf-8")
    print(f"Wrote {out}", flush=True)
    return report


def _fmt(value) -> str:
    if value is None:
        return "—"
    return f"{value:.2f}"


def _markdown(report: dict) -> str:
    lines = [
        "# Held-out evaluation",
        "",
        f"{report['holdout_size']} cases were held out of `{report['source']}` with seed {report['seed']}. "
        "Those case ids were removed from retrieval before Generic GPT with cases, and before the Doctor's Twin, answered.",
        "",
        "The reference is the doctor's recorded decision, not a model score. "
        "Test precision and recall use the test names in the recorded tests and the treatment decision. "
        "Risk is urgent for an ER referral, investigate for CT coronary angiography or a stress test, and routine otherwise. "
        "Follow-up is immediate for an ER referral, 2 weeks when the decision says so, and unspecified otherwise. "
        "An answer that only says 3-7 days is counted as other, so it does not match either of those. "
        "If an answer contains an urgent word, that outranks a routine plan.",
        "",
        "| System | Cases scored | Test precision | Test recall | Risk agreement | Follow-up agreement |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    labels = {"generic": "Generic GPT", "rag": "GPT + retrieved cases", "twin": "Doctor's Twin"}
    for key, label in labels.items():
        item = report["summary"][key]
        lines.append(
            f"| {label} | {item['n']} | {_fmt(item['test_precision'])} | {_fmt(item['test_recall'])} | {_fmt(item['risk_agreement'])} | {_fmt(item['followup_agreement'])} |"
        )
    lines.append("")
    if report.get("judge"):
        lines.append("A blinded judge scored caution, specificity, and traceability from 1 to 5. Answer order was randomized.")
        lines.append("")
        judge = report["judge"]
        lines.append("| System | Caution | Specificity | Traceability |")
        lines.append("| --- | --- | --- | --- |")
        for key, label in labels.items():
            scores = judge[key]
            lines.append(f"| {label} | {_fmt(scores['caution'])} | {_fmt(scores['specificity'])} | {_fmt(scores['traceability'])} |")
        lines.append("")
        lines.append(f"The judge scored {judge['n']} cases.")
    else:
        lines.append("The blinded judge was not run. Add `--judge` to score caution, specificity, and traceability with the answer order randomized.")
    lines.append("")
    failed = sum(1 for case in report["cases"] for item in case["systems"].values() if item.get("error"))
    if failed:
        lines.append(f"{failed} system answers failed before they could be scored. Those answers are left out of the means.")
        lines.append("")
    leaks = [case["case_id"] for case in report["cases"] if case.get("leak")]
    if leaks:
        lines.append(f"Holdout cases leaked into retrieval for: {', '.join(leaks)}.")
    else:
        lines.append("No held-out case id was returned by retrieval.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Score 30 held-out cases against the doctor's recorded decisions.")
    parser.add_argument("--judge", action="store_true", help="Add a blinded LLM judge with randomized answer order.")
    args = parser.parse_args()
    run(judge=args.judge)


if __name__ == "__main__":
    main()

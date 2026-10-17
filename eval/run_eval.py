"""Held-out comparison against Dr. Pandey's recorded tests.

Thirty cases are kept out of retrieval, out of the graph used for this run,
and out of the style rules. Each one is given to three systems: Generic GPT,
Generic GPT with the same retrieved cases, and the Doctor's Twin. A fourth row
always recommends ECG, echo, and a lipid panel. This does not change a live
consultation.

    python eval/run_eval.py
    python eval/run_eval.py --judge
    python eval/run_eval.py --rescore
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HOLDOUT_N = 30
SEED = 17
N_BOOT = 2000
SOURCE_GLOB = "doctor_cases_vimlesh_*.csv"
BASELINE_TESTS = frozenset({"ecg", "echo", "lipid"})
TEXT_COLUMNS = (
    "symptoms",
    "risk_factors",
    "tests",
    "diagnosis",
    "treatment_decision",
    "reasoning_notes",
    "outcome",
)

TEST_PATTERNS = (
    ("ecg", ("ecg", "electrocardiogram")),
    ("echo", ("echo", "echocardiogram")),
    ("stress", ("stress test", "tmt", "stress imaging")),
    ("troponin", ("troponin",)),
    ("holter", ("holter",)),
    ("ct", ("ct angiograph", "ct coronary", "coronary angiograph", "ctca")),
    ("lipid", ("lipid",)),
)

SYSTEM_KEYS = ("generic", "rag", "twin")
SUMMARY_KEYS = ("generic", "rag", "twin", "baseline")
LABELS = {
    "generic": "Generic GPT",
    "rag": "GPT + retrieved cases",
    "twin": "Doctor's Twin",
    "baseline": "Always ECG + echo + lipid panel",
}


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


def gold_followup(decision: str) -> str:
    folded = (decision or "").lower()
    if "urgent" in folded or "er referral" in folded:
        return "immediate"
    if "2 week" in folded or "two week" in folded:
        return "2 weeks"
    return "unspecified"


def precision_recall(predicted: set[str], gold: set[str]) -> tuple[float | None, float | None]:
    if not predicted and not gold:
        return None, None
    precision = (len(predicted & gold) / len(predicted)) if predicted else 0.0
    recall = (len(predicted & gold) / len(gold)) if gold else None
    return precision, recall


def f1_score(precision: float | None, recall: float | None) -> float | None:
    if precision is None or recall is None:
        return None
    if precision + recall == 0:
        return 0.0
    return (2 * precision * recall) / (precision + recall)


def _mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def _percentile(ordered: list[float], p: float) -> float:
    if len(ordered) == 1:
        return ordered[0]
    idx = (len(ordered) - 1) * p
    lo = int(idx)
    hi = min(lo + 1, len(ordered) - 1)
    frac = idx - lo
    return ordered[lo] * (1 - frac) + ordered[hi] * frac


def summarize_rows(rows: list[dict], n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    """Mean of the case-level scores, with a 95% percentile bootstrap interval."""
    keys = (("precision", "test_precision"), ("recall", "test_recall"), ("f1", "f1"), ("n_tests", "avg_tests"))
    summary: dict = {"n": len(rows)}
    samples = {src: [] for src, _dst in keys}
    rng = random.Random(seed)
    if rows and n_boot > 0:
        for _ in range(n_boot):
            draw = [rows[rng.randrange(len(rows))] for _ in range(len(rows))]
            for src, _dst in keys:
                vals = [row[src] for row in draw if row[src] is not None]
                if vals:
                    samples[src].append(sum(vals) / len(vals))
    for src, dst in keys:
        observed = [row[src] for row in rows if row[src] is not None]
        summary[dst] = _mean(observed)
        ordered = sorted(samples[src])
        if ordered:
            summary[f"{dst}_ci"] = [round(_percentile(ordered, 0.025), 4), round(_percentile(ordered, 0.975), 4)]
        else:
            summary[f"{dst}_ci"] = None
    return summary


def _case_text(row: dict) -> str:
    return " ".join(str(row.get(col) or "") for col in TEXT_COLUMNS).lower()


def _style_text(rules: list[str]) -> str:
    kept = [rule for rule in rules if str(rule).strip()]
    if not kept:
        return "- Calm, concise, preventive, plain language"
    return "\n".join(f"- {rule}" for rule in kept)


def _graph_from_frames(nodes_df, edges_df):
    import networkx as nx

    g = nx.DiGraph()
    node_id_col = "node_id" if "node_id" in nodes_df.columns else nodes_df.columns[0]
    node_name_col = "name" if "name" in nodes_df.columns else ("label" if "label" in nodes_df.columns else node_id_col)
    node_type_col = "type" if "type" in nodes_df.columns else ("category" if "category" in nodes_df.columns else None)
    for _, row in nodes_df.iterrows():
        node_id = str(row[node_id_col])
        node_name = str(row[node_name_col])
        node_type = str(row[node_type_col]) if node_type_col else "clinical"
        g.add_node(node_id, name=node_name, label=node_name, category=node_type)

    if edges_df is None or edges_df.empty:
        return g
    src_col = "source_id" if "source_id" in edges_df.columns else ("source" if "source" in edges_df.columns else edges_df.columns[0])
    tgt_col = "target_id" if "target_id" in edges_df.columns else ("target" if "target" in edges_df.columns else edges_df.columns[1])
    relation_col = "relation" if "relation" in edges_df.columns else None
    weight_col = "weight" if "weight" in edges_df.columns else None
    for _, row in edges_df.iterrows():
        relation = str(row[relation_col]) if relation_col else "linked_to"
        weight = float(row[weight_col]) if weight_col else 1.0
        g.add_edge(str(row[src_col]), str(row[tgt_col]), relation=relation, weight=weight)
    return g


def exclusion_audit(frame, holdout_ids, nodes_df, edges_df, style_df) -> dict:
    """Drop graph pieces and style rules that the held-out cases alone support.

    The graph files have no case id column. A node is removed only when its name
    appears in a held-out case and in no training case. An edge is removed when
    either end was removed, or the two names occur together in a held-out case
    and in no training case. A style rule is removed when it names a held-out case.
    """
    blocked = {str(item) for item in holdout_ids}
    train_text = []
    hold_text = []
    for _, row in frame.iterrows():
        text = _case_text(row.to_dict())
        if str(row.get("case_id")) in blocked:
            hold_text.append(text)
        else:
            train_text.append(text)

    def mentions(name: str, texts: list[str]) -> bool:
        needle = name.strip().lower()
        return bool(needle) and any(needle in text for text in texts)

    node_id_col = "node_id" if "node_id" in nodes_df.columns else nodes_df.columns[0]
    node_name_col = "name" if "name" in nodes_df.columns else ("label" if "label" in nodes_df.columns else node_id_col)
    removed_ids = set()
    removed_nodes = []
    absent = []
    keep_node_rows = []
    for _, row in nodes_df.iterrows():
        name = str(row[node_name_col])
        in_hold = mentions(name, hold_text)
        in_train = mentions(name, train_text)
        if in_hold and not in_train:
            removed_ids.add(str(row[node_id_col]))
            removed_nodes.append(name)
        else:
            keep_node_rows.append(row)
            if not in_hold and not in_train:
                absent.append(name)

    src_col = "source_id" if "source_id" in edges_df.columns else ("source" if "source" in edges_df.columns else edges_df.columns[0])
    tgt_col = "target_id" if "target_id" in edges_df.columns else ("target" if "target" in edges_df.columns else edges_df.columns[1])
    relation_col = "relation" if "relation" in edges_df.columns else None
    names = {str(row[node_id_col]): str(row[node_name_col]) for _, row in nodes_df.iterrows()}
    removed_edges = []
    keep_edge_rows = []
    for _, row in edges_df.iterrows():
        src = str(row[src_col])
        tgt = str(row[tgt_col])
        relation = str(row[relation_col]) if relation_col else "linked_to"
        src_name = names.get(src, src).lower()
        tgt_name = names.get(tgt, tgt).lower()
        co_train = any(src_name in text and tgt_name in text for text in train_text)
        co_hold = any(src_name in text and tgt_name in text for text in hold_text)
        if src in removed_ids or tgt in removed_ids or (co_hold and not co_train):
            removed_edges.append(
                {"source": names.get(src, src), "target": names.get(tgt, tgt), "relation": relation}
            )
        else:
            keep_edge_rows.append(row)

    import pandas as pd

    kept_nodes = pd.DataFrame(keep_node_rows) if keep_node_rows else nodes_df.iloc[0:0]
    kept_edges = pd.DataFrame(keep_edge_rows) if keep_edge_rows else edges_df.iloc[0:0]
    removed_rules = []
    kept_rules = []
    rule_col = "style_rule" if "style_rule" in style_df.columns else None
    if rule_col:
        for rule in style_df[rule_col].astype(str).tolist():
            folded = rule.lower()
            if any(re.search(rf"\bcase\s+{re.escape(cid)}\b", folded) for cid in blocked):
                removed_rules.append(rule)
            else:
                kept_rules.append(rule)
    return {
        "graph": _graph_from_frames(kept_nodes, kept_edges),
        "style_text": _style_text(kept_rules),
        "graph_nodes_removed": removed_nodes,
        "graph_edges_removed": removed_edges,
        "style_rules_removed": removed_rules,
        "graph_nodes_kept": int(len(kept_nodes)),
        "graph_edges_kept": int(len(kept_edges)),
        "style_rules_kept": len(kept_rules),
        "nodes_not_in_any_case": absent,
    }


def exclusion_from_disk(frame, holdout_ids) -> dict:
    import pandas as pd

    raw = ROOT / "data" / "raw"
    return exclusion_audit(
        frame,
        holdout_ids,
        pd.read_csv(raw / "graph_nodes.csv"),
        pd.read_csv(raw / "graph_edges.csv"),
        pd.read_csv(raw / "doctor_style_examples.csv"),
    )


def public_exclusion(audit: dict, holdout_ids: list[str]) -> dict:
    return {
        "holdout_case_ids": list(holdout_ids),
        "retrieval": "These case ids are passed to retrieval as exclude_ids before Generic GPT with cases, and before the Doctor's Twin, answers.",
        "graph_nodes_removed": audit["graph_nodes_removed"],
        "graph_edges_removed": audit["graph_edges_removed"],
        "style_rules_removed": audit["style_rules_removed"],
        "graph_nodes_kept": audit["graph_nodes_kept"],
        "graph_edges_kept": audit["graph_edges_kept"],
        "style_rules_kept": audit["style_rules_kept"],
        "nodes_not_in_any_case": audit["nodes_not_in_any_case"],
        "rule": (
            "graph_nodes.csv and graph_edges.csv have no case id column. "
            "A node is removed when its name appears in a held-out case and in no training case. "
            "An edge is removed when either end was removed, or the two names occur together only in a held-out case. "
            "A style rule is removed when it names a held-out case. "
            "Nodes that never appear in a case are kept, because they are not held-out case content."
        ),
    }


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


def _score_sets(predicted: set[str], gold: set[str]) -> dict:
    precision, recall = precision_recall(predicted, gold)
    return {
        "predicted_tests": sorted(predicted),
        "precision": precision,
        "recall": recall,
        "f1": f1_score(precision, recall),
        "n_tests": len(predicted),
        "error": None,
    }


def score_answer(text: str, row: dict) -> dict:
    return _score_sets(named_tests(text), gold_tests(row))


def _rows_for_system(cases: list[dict], system: str) -> list[dict]:
    rows = []
    for case in cases:
        item = case["systems"][system]
        if item.get("error"):
            continue
        rows.append(_score_sets(set(item.get("predicted_tests") or []), set(case["gold"]["tests"])))
    return rows


def _rows_for_baseline(cases: list[dict]) -> list[dict]:
    return [_score_sets(set(BASELINE_TESTS), set(case["gold"]["tests"])) for case in cases]


def summarize_cases(cases: list[dict], n_boot: int = N_BOOT, seed: int = SEED) -> dict:
    summary = {name: summarize_rows(_rows_for_system(cases, name), n_boot=n_boot, seed=seed) for name in SYSTEM_KEYS}
    summary["baseline"] = summarize_rows(_rows_for_baseline(cases), n_boot=n_boot, seed=seed)
    return summary


def label_audit(cases: list[dict]) -> dict | None:
    """Doctor label versus the old predicted label. Kept so the failed extraction stays visible."""
    if not cases:
        return None
    sample = cases[0]["systems"].get("generic") or {}
    if "risk" not in sample:
        return None
    rows = []
    doctor_risk: dict[str, int] = {}
    doctor_follow: dict[str, int] = {}
    predicted: dict[str, dict[str, dict[str, int]]] = {
        name: {"risk": {}, "followup": {}} for name in SYSTEM_KEYS
    }
    for case in cases:
        gold = case["gold"]
        row = {
            "case_id": case["case_id"],
            "treatment_decision": gold.get("treatment_decision", ""),
            "doctor_risk": gold.get("risk"),
            "doctor_followup": gold.get("followup"),
        }
        doctor_risk[str(gold.get("risk"))] = doctor_risk.get(str(gold.get("risk")), 0) + 1
        doctor_follow[str(gold.get("followup"))] = doctor_follow.get(str(gold.get("followup")), 0) + 1
        for name in SYSTEM_KEYS:
            item = case["systems"][name]
            row[f"{name}_risk"] = item.get("risk")
            row[f"{name}_followup"] = item.get("followup")
            risk = str(item.get("risk"))
            follow = str(item.get("followup"))
            predicted[name]["risk"][risk] = predicted[name]["risk"].get(risk, 0) + 1
            predicted[name]["followup"][follow] = predicted[name]["followup"].get(follow, 0) + 1
        rows.append(row)
    return {
        "doctor_risk": doctor_risk,
        "doctor_followup": doctor_follow,
        "predicted": predicted,
        "rows": rows,
        "reason": (
            "Risk agreement and follow-up agreement were the same 0.23 for every system because the extractor "
            "labeled the answer urgent and immediate whenever those words appeared. Generic GPT and GPT with "
            "retrieved cases always include the fixed line “Escalate immediately if chest pain worsens, rest pain "
            "appears, or dyspnea increases.” The twin prompt also tells the model to mention urgent care. "
            "Those words are a safety line, not the risk level of the plan and not the follow-up interval. "
            "The two columns are not scored."
        ),
    }


def _strip_label_fields(cases: list[dict]) -> None:
    for case in cases:
        gold = case.get("gold") or {}
        case["gold"] = {
            "tests": gold.get("tests") or [],
            "treatment_decision": gold.get("treatment_decision", ""),
        }
        for name in SYSTEM_KEYS:
            item = case["systems"][name]
            if item.get("error"):
                case["systems"][name] = {
                    "predicted_tests": [],
                    "precision": None,
                    "recall": None,
                    "f1": None,
                    "n_tests": None,
                    "error": item.get("error"),
                }
                continue
            scored = _score_sets(set(item.get("predicted_tests") or []), set(case["gold"]["tests"]))
            case["systems"][name] = scored


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
    buckets = {key: {"caution": [], "specificity": [], "traceability": []} for key in SYSTEM_KEYS}
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


def _bootstrap_meta() -> dict:
    return {"samples": N_BOOT, "level": 0.95, "method": "percentile", "seed": SEED}


def _attach_scores(report: dict, audit: dict) -> dict:
    cases = report["cases"]
    audit_labels = label_audit(cases)
    if audit_labels is None:
        audit_labels = report.get("label_audit")
    _strip_label_fields(cases)
    report["summary"] = summarize_cases(cases)
    report["bootstrap"] = _bootstrap_meta()
    report["excluded"] = public_exclusion(audit, report["holdout_case_ids"])
    report["excluded_from_retrieval"] = True
    report["label_audit"] = audit_labels
    report["systems"] = {
        "generic": "Generic GPT, intake only",
        "rag": "Generic GPT plus the same retrieved cases the twin saw",
        "twin": "Doctor's Twin. Retrieval, the eval graph, and the style rules exclude the held-out cases.",
        "baseline": "Fixed plan on every case: ECG, echo, and a lipid panel. No model call.",
    }
    report["gold"] = {
        "tests": "Test names found in the recorded tests column and the recorded treatment decision.",
        "not_scored": (
            "Risk level and follow-up interval are not scored. The answers do not state them apart from a fixed safety line."
        ),
    }
    return report


def run(judge: bool = False) -> dict:
    import pandas as pd

    from backend.utils import _case_line, _safe_openai_chat, generate_generic_consultation, generate_twin_consultation, prepare_generic_bundle
    from config import OPENAI_API_KEY, OPENAI_MODEL
    from rag.retrieve import retrieve_similar_cases

    frame = pd.read_csv(case_file()).fillna("")
    holdout = select_holdout(frame["case_id"].astype(str).tolist())
    blocked = set(holdout)
    audit = exclusion_from_disk(frame, blocked)
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
        twin = generate_twin_consultation(
            patient,
            exclude_ids=blocked,
            graph=audit["graph"],
            style_text=audit["style_text"],
        )
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
                    "f1": None,
                    "n_tests": None,
                    "error": failure,
                }
            else:
                systems[name] = score_answer(text, row)
        record = {
            "case_id": case_id,
            "gold": {
                "tests": sorted(gold_tests(row)),
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

    report = {
        "holdout_size": len(holdout),
        "seed": SEED,
        "source": str(case_file().relative_to(ROOT)).replace("\\", "/"),
        "holdout_case_ids": holdout,
        "judge": _judge_summary(cases) if judge else None,
        "cases": cases,
    }
    _attach_scores(report, audit)
    _write(report)
    return report


def rewrite_saved_report() -> dict:
    """Recompute metrics from the saved test lists. Does not call the model."""
    import pandas as pd

    path = ROOT / "eval" / "results.json"
    report = json.loads(path.read_text(encoding="utf-8"))
    frame = pd.read_csv(case_file()).fillna("")
    holdout = report.get("holdout_case_ids") or select_holdout(frame["case_id"].astype(str).tolist())
    report["holdout_case_ids"] = holdout
    report["holdout_size"] = len(holdout)
    report["seed"] = report.get("seed", SEED)
    report["source"] = report.get("source") or str(case_file().relative_to(ROOT)).replace("\\", "/")
    audit = exclusion_from_disk(frame, set(holdout))
    _attach_scores(report, audit)
    _write(report)
    return report


def _write(report: dict) -> None:
    out = ROOT / "eval" / "results.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    (ROOT / "eval" / "REPORT.md").write_text(_markdown(report), encoding="utf-8")
    print(f"Wrote {out}", flush=True)


def _fmt(value) -> str:
    if value is None:
        return "—"
    return f"{value:.2f}"


def _fmt_metric(item: dict, key: str) -> str:
    point = item.get(key)
    if point is None:
        return "—"
    ci = item.get(f"{key}_ci")
    if not ci:
        return f"{point:.2f}"
    return f"{point:.2f} [{ci[0]:.2f}, {ci[1]:.2f}]"


def _count_line(title: str, removed: list) -> str:
    if not removed:
        return f"{title}: none removed."
    if isinstance(removed[0], dict):
        shown = ", ".join(f"{item.get('source')} -> {item.get('target')}" for item in removed)
    else:
        shown = ", ".join(str(item) for item in removed)
    return f"{title}: {len(removed)} removed ({shown})."


def _markdown(report: dict) -> str:
    excluded = report.get("excluded") or {}
    boot = report.get("bootstrap") or _bootstrap_meta()
    n = report["holdout_size"]
    lines = [
        "# Held-out evaluation",
        "",
        f"Sample size: {n} held-out cases from `{report['source']}`, chosen with seed {report['seed']}. "
        f"Every number below is on those {n} cases. "
        f"The bracket after a number is a {int(boot['level'] * 100)}% percentile bootstrap confidence interval "
        f"from {boot['samples']} resamples of the scored cases (seed {boot['seed']}).",
        "",
        "## What was excluded",
        "",
        "The same 30 case ids were kept out of three places before the Doctor's Twin answered:",
        "",
        "- Retrieval. " + excluded.get("retrieval", "The holdout ids were passed as exclude_ids."),
        "- Graph. The eval run builds a graph from `graph_nodes.csv` and `graph_edges.csv` after the holdout filter. "
        + excluded.get("rule", ""),
        "- Style rules. `doctor_style_examples.csv` is filtered the same way, then passed into the twin prompt for this run only.",
        "",
        _count_line("Graph nodes", excluded.get("graph_nodes_removed") or []),
        _count_line("Graph edges", excluded.get("graph_edges_removed") or []),
        _count_line("Style rules", excluded.get("style_rules_removed") or []),
        (
            f"Graph kept: {excluded.get('graph_nodes_kept', '—')} nodes and {excluded.get('graph_edges_kept', '—')} edges. "
            f"Style rules kept: {excluded.get('style_rules_kept', '—')}."
        ),
    ]
    absent = excluded.get("nodes_not_in_any_case") or []
    if absent:
        lines.append(
            "These graph nodes do not appear in any case row, so they are not held-out content and they stay: "
            + ", ".join(absent)
            + "."
        )
    lines.append("")
    lines.append("Held-out case ids: " + ", ".join(report.get("holdout_case_ids") or []) + ".")
    lines.append("")
    lines.append("## Scores")
    lines.append("")
    lines.append(
        "The reference is the doctor's recorded tests, not a model score. "
        "Precision, recall, and F1 use the test names in the recorded tests and the treatment decision. "
        "F1 is the mean of the per-case F1 scores. "
        "Average tests is the mean number of those named tests in the answer. "
        "The last row does not call a model. It recommends ECG, echo, and a lipid panel on every case."
    )
    lines.append("")
    lines.append("| System | Cases scored | Test precision | Test recall | F1 | Average tests |")
    lines.append("| --- | --- | --- | --- | --- | --- |")
    for key in SUMMARY_KEYS:
        item = report["summary"][key]
        lines.append(
            f"| {LABELS[key]} | {item['n']} | {_fmt_metric(item, 'test_precision')} | {_fmt_metric(item, 'test_recall')} | {_fmt_metric(item, 'f1')} | {_fmt_metric(item, 'avg_tests')} |"
        )
    lines.append("")
    lines.extend(_label_section(report.get("label_audit")))
    if report.get("judge"):
        lines.append("A blinded judge scored caution, specificity, and traceability from 1 to 5. Answer order was randomized.")
        lines.append("")
        judge = report["judge"]
        lines.append("| System | Caution | Specificity | Traceability |")
        lines.append("| --- | --- | --- | --- |")
        for key in SYSTEM_KEYS:
            scores = judge[key]
            lines.append(f"| {LABELS[key]} | {_fmt(scores['caution'])} | {_fmt(scores['specificity'])} | {_fmt(scores['traceability'])} |")
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


def _label_section(audit: dict | None) -> list[str]:
    lines = [
        "## Risk and follow-up",
        "",
        "Risk agreement and follow-up agreement are not reported. "
        "On the saved answers, keyword extraction labeled every system urgent and immediate, "
        "because the generic answer always contains “Escalate immediately…” and the twin answer is told to mention urgent care. "
        "That is not a risk level and it is not a follow-up interval. The columns were removed.",
        "",
    ]
    if not audit:
        return lines
    lines.append(
        "Doctor risk: "
        + ", ".join(f"{name} {count}" for name, count in audit["doctor_risk"].items())
        + ". Doctor follow-up: "
        + ", ".join(f"{name} {count}" for name, count in audit["doctor_followup"].items())
        + "."
    )
    for name in SYSTEM_KEYS:
        risk = ", ".join(f"{label} {count}" for label, count in audit["predicted"][name]["risk"].items())
        follow = ", ".join(f"{label} {count}" for label, count in audit["predicted"][name]["followup"].items())
        lines.append(f"{LABELS[name]} predicted risk: {risk}. Predicted follow-up: {follow}.")
    lines.append("")
    lines.append("| Case | Doctor decision | Doctor risk | Doctor follow-up | Generic risk | Generic follow-up | GPT + cases risk | GPT + cases follow-up | Twin risk | Twin follow-up |")
    lines.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    for row in audit["rows"]:
        lines.append(
            "| {case_id} | {treatment_decision} | {doctor_risk} | {doctor_followup} | {generic_risk} | {generic_followup} | {rag_risk} | {rag_followup} | {twin_risk} | {twin_followup} |".format(
                **row
            )
        )
    lines.append("")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Score 30 held-out cases against the doctor's recorded tests.")
    parser.add_argument("--judge", action="store_true", help="Add a blinded LLM judge with randomized answer order.")
    parser.add_argument("--rescore", action="store_true", help="Recompute metrics from saved answers without calling the model.")
    args = parser.parse_args()
    if args.rescore:
        rewrite_saved_report()
        return
    run(judge=args.judge)


if __name__ == "__main__":
    main()

# Held-out evaluation

Sample size: 30 held-out cases from `data/raw/doctor_cases_vimlesh_pandey.csv`, chosen with seed 17. Every number below is on those 30 cases. The bracket after a number is a 95% percentile bootstrap confidence interval from 2000 resamples of the scored cases (seed 17).

## What was excluded

The same 30 case ids were kept out of three places before the Doctor's Twin answered:

- Retrieval. These case ids are passed to retrieval as exclude_ids before Generic GPT with cases, and before the Doctor's Twin, answers.
- Graph. The eval run builds a graph from `graph_nodes.csv` and `graph_edges.csv` after the holdout filter. graph_nodes.csv and graph_edges.csv have no case id column. A node is removed when its name appears in a held-out case and in no training case. An edge is removed when either end was removed, or the two names occur together only in a held-out case. A style rule is removed when it names a held-out case. Nodes that never appear in a case are kept, because they are not held-out case content.
- Style rules. `doctor_style_examples.csv` is filtered the same way, then passed into the twin prompt for this run only.

Graph nodes: none removed.
Graph edges: none removed.
Style rules: none removed.
Graph kept: 34 nodes and 116 edges. Style rules kept: 8.
These graph nodes do not appear in any case row, so they are not held-out content and they stay: prefers preventive care, escalates exertional pain.

Held-out case ids: 14, 57, 90, 128, 130, 143, 149, 156, 163, 188, 197, 213, 215, 257, 268, 277, 328, 339, 351, 361, 362, 383, 393, 411, 414, 418, 434, 441, 470, 492.

## Scores

The reference is the doctor's recorded tests, not a model score. Precision, recall, and F1 use the test names in the recorded tests and the treatment decision. F1 is the mean of the per-case F1 scores. Average tests is the mean number of those named tests in the answer. The last row does not call a model. It recommends ECG, echo, and a lipid panel on every case.

| System | Cases scored | Test precision | Test recall | F1 | Average tests |
| --- | --- | --- | --- | --- | --- |
| Generic GPT | 30 | 0.33 [0.18, 0.50] | 0.17 [0.10, 0.26] | 0.22 [0.12, 0.33] | 1.27 [1.10, 1.47] |
| GPT + retrieved cases | 30 | 0.29 [0.18, 0.42] | 0.25 [0.16, 0.36] | 0.25 [0.16, 0.34] | 1.70 [1.50, 1.90] |
| Doctor's Twin | 30 | 0.28 [0.23, 0.34] | 0.78 [0.68, 0.88] | 0.40 [0.34, 0.46] | 5.60 [5.40, 5.80] |
| Always ECG + echo + lipid panel | 30 | 0.30 [0.21, 0.39] | 0.41 [0.29, 0.53] | 0.34 [0.24, 0.42] | 3.00 [3.00, 3.00] |

## Risk and follow-up

Risk agreement and follow-up agreement are not reported. On the saved answers, keyword extraction labeled every system urgent and immediate, because the generic answer always contains “Escalate immediately…” and the twin answer is told to mention urgent care. That is not a risk level and it is not a follow-up interval. The columns were removed.

Doctor risk: routine 15, investigate 8, urgent 7. Doctor follow-up: unspecified 21, immediate 7, 2 weeks 2.
Generic GPT predicted risk: urgent 30. Predicted follow-up: immediate 30.
GPT + retrieved cases predicted risk: urgent 30. Predicted follow-up: immediate 30.
Doctor's Twin predicted risk: urgent 30. Predicted follow-up: immediate 29, 2 weeks 1.

| Case | Doctor decision | Doctor risk | Doctor follow-up | Generic risk | Generic follow-up | GPT + cases risk | GPT + cases follow-up | Twin risk | Twin follow-up |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 14 | Medication optimization | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 57 | ECG + stress test | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 90 | Urgent ER referral | urgent | immediate | urgent | immediate | urgent | immediate | urgent | immediate |
| 128 | Follow-up in 2 weeks | routine | 2 weeks | urgent | immediate | urgent | immediate | urgent | immediate |
| 130 | Urgent ER referral | urgent | immediate | urgent | immediate | urgent | immediate | urgent | immediate |
| 143 | CT coronary angiography | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 149 | Lifestyle counseling | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 156 | Medication optimization | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 163 | CT coronary angiography | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 188 | Medication optimization | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 197 | Echo + lipid panel | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 213 | Holter monitor | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 215 | Medication optimization | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 257 | ECG + stress test | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 268 | Medication optimization | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 277 | Follow-up in 2 weeks | routine | 2 weeks | urgent | immediate | urgent | immediate | urgent | immediate |
| 328 | CT coronary angiography | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 339 | CT coronary angiography | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 351 | Urgent ER referral | urgent | immediate | urgent | immediate | urgent | immediate | urgent | immediate |
| 361 | Echo + lipid panel | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 362 | CT coronary angiography | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 383 | CT coronary angiography | investigate | unspecified | urgent | immediate | urgent | immediate | urgent | 2 weeks |
| 393 | Lifestyle counseling | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 411 | Urgent ER referral | urgent | immediate | urgent | immediate | urgent | immediate | urgent | immediate |
| 414 | Urgent ER referral | urgent | immediate | urgent | immediate | urgent | immediate | urgent | immediate |
| 418 | Lifestyle counseling | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 434 | Urgent ER referral | urgent | immediate | urgent | immediate | urgent | immediate | urgent | immediate |
| 441 | Urgent ER referral | urgent | immediate | urgent | immediate | urgent | immediate | urgent | immediate |
| 470 | Echo + lipid panel | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |
| 492 | Holter monitor | routine | unspecified | urgent | immediate | urgent | immediate | urgent | immediate |

The blinded judge was not run. Add `--judge` to score caution, specificity, and traceability with the answer order randomized.

No held-out case id was returned by retrieval.

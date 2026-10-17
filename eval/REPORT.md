# Held-out evaluation

30 cases were held out of `data/raw/doctor_cases_vimlesh_pandey.csv` with seed 17. Those case ids were removed from retrieval before Generic GPT with cases, and before the Doctor's Twin, answered.

The reference is the doctor's recorded decision, not a model score. Test precision and recall use the test names in the recorded tests and the treatment decision. Risk is urgent for an ER referral, investigate for CT coronary angiography or a stress test, and routine otherwise. Follow-up is immediate for an ER referral, 2 weeks when the decision says so, and unspecified otherwise. An answer that only says 3-7 days is counted as other, so it does not match either of those. If an answer contains an urgent word, that outranks a routine plan.

| System | Cases scored | Test precision | Test recall | Risk agreement | Follow-up agreement |
| --- | --- | --- | --- | --- | --- |
| Generic GPT | 30 | 0.33 | 0.17 | 0.23 | 0.23 |
| GPT + retrieved cases | 30 | 0.29 | 0.25 | 0.23 | 0.23 |
| Doctor's Twin | 30 | 0.28 | 0.78 | 0.23 | 0.23 |

The blinded judge was not run. Add `--judge` to score caution, specificity, and traceability with the answer order randomized.

No held-out case id was returned by retrieval.

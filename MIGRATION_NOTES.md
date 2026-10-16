# CardioTwin AI migration notes

Step 0 inventory of the original app in `doctor-digital-twin/`, written before the React conversion.
The new UI lives in `web/`. The old UI folder was removed in Step 5 after the new app worked.

Legend: `[ ]` not yet confirmed in the new UI, `[x]` confirmed.

## What the app is

CardioTwin AI is a clinical decision-support demo of a digital twin of Dr. Vimlesh Pandey.
It is not a diagnosis engine. Pages call Python directly (not the old HTTP routes).

## Shared shell (`frontend/ui.py`, `frontend/streamlit_app.py`)

- Dark clinical theme (sky blue `#0ea5e9`, teal `#14b8a6`, navy background).
- Top step links: Intake, Generic, Twin, Difference, Cases, Graph, Insights, Why, Admin, Explainability.
- Sidebar title "CardioTwin AI", caption, quick path 1→5.
- Landing (`streamlit_app.py`, not a numbered page): hero, 3 metrics (AI Modes, Reasoning Layers, Audience), four explanation cards, two feature cards, buttons **Start Analysis** and **Open Consultation Portal**.
- Assets on disk but not referenced by any page: `frontend/assets/doctor_photo.png`, `frontend/assets/logo.png`. The new UI uses both.

## Session state (must survive page changes)

| Key | Set by | Used by |
| --- | --- | --- |
| `patient` | Portal save, Patient Intake | Generic, Twin, Comparison, Cases, Graph, Explainability |
| `generic_result` | Generic page (once) | Comparison, Insights, Explainability |
| `twin_result` | Twin page, or Comparison if missing | Twin, Comparison, Insights, Why, Explainability |
| `portal_patient` | Portal intake | Portal; copied into `patient` when intake is empty |
| `portal_mode` | `general` or `specialist` | Portal chat and doctor review |
| `portal_chat` | list of `{role, content}` | Portal |
| `portal_draft` | first assistant text | Doctor editor |
| `portal_original_draft` | first assistant text | Accept detects edits |
| `portal_twin` | specialist bundle | Chat context, action panel |
| `portal_approved` | doctor Accept | stored edited text |
| `portal_rejected` | doctor Reject | flag |
| `portal_doctor_status` | `approved` / `edited_approved` / `rejected` | banners |
| `portal_view` | `Patient` or `Doctor` | Portal layout |

New UI keeps these in a Zustand store (`cardiotwin-session`), including across refresh.

## Data files

| File | Used by |
| --- | --- |
| `data/raw/doctor_cases_vimlesh_pandey.csv` | RAG ingest, admin count |
| `data/raw/patient_profiles.csv` | Admin registry only (now also selectable context) |
| `data/raw/patient_timelines.csv` | Admin registry only (now prompt context when a profile is selected) |
| `data/raw/graph_nodes.csv` | Knowledge graph |
| `data/raw/graph_edges.csv` | Knowledge graph |
| `data/raw/doctor_style_examples.csv` | Admin registry only (now injected into specialist prompts) |
| `data/processed/cleaned_cases.csv` | Written by ingest |
| `data/processed/cases.index` | FAISS index, loaded once |
| `data/processed/embeddings_cache.pkl` | FAISS metadata, loaded once |
| `data/processed/graph_export.json` | Written when the graph is built |
| `prompts/doctor_twin.txt` | Twin system/user prompt |
| `prompts/generic_gpt.txt` | Generic system prompt |
| `prompts/graph_reasoning.txt` | Was unused by code; now included as reasoning guidance |
| `prompts/patient_summary.txt` | Was empty; now instructs how to weigh the live patient |

## LLM and non-LLM engines

- Generic consult: `generate_generic_consultation` → chat completion with `generic_gpt.txt`. Concerns, next steps, and risk notes are fixed safety lists, not model JSON.
- Twin consult: retrieve top 5 → rerank → graph reasoning → `build_twin_prompt` → chat completion with `doctor_twin.txt`.
- Portal follow-up: `generate_followup_reply` (`general` or `specialist`) → chat completion. No retrieval of its own; specialist receives the twin assessment text.
- Embeddings: OpenAI `text-embedding-3-small` when `OPENAI_API_KEY` is set, otherwise TF-IDF. Used by `rag/retrieve.py`.
- Not LLMs: BMI summary, FAISS search, rerank bonuses, graph cue matching, comparison keyword scores, dataset counts.

## Page checklist

### Landing — Home

- [x] Hero, three metrics, problem / doctors / hospitals / features cards, two highlight cards
- [x] Start Analysis → Patient Analysis
- [x] Open Consultation Portal
- [x] Logo and doctor photo

### 0 — Consultation Portal (`/consultation`)

- [x] Guided intake: name, age, gender, height, weight, duration, BP, LDL, HbA1c, symptom pattern, symptom details, risk-factor multiselect, history, family history, lifestyle, medications, notes
- [x] Demo defaults (Aarav Mehta and the sample clinical values)
- [x] Save Intake writes `portal_patient` and `patient`, clears chat, draft, twin, mode, doctor status
- [x] Start General Consultation → generic summary as first assistant message
- [x] Start Specialist Consultation → twin assessment, stores twin bundle
- [x] Chat history, follow-up input, streaming reply
- [x] Copy and regenerate on assistant messages
- [x] Specialist expander: immediate actions, recommended tests, follow-up, review status
- [x] Patient / Doctor view (Doctor only after specialist start)
- [x] Doctor review: BMI and risk markers, editable draft, Accept, Reject, safety note, back to chat
- [x] Accept without edits vs with edits (`approved` vs `edited_approved`) posts a doctor update into chat
- [x] Reject posts a rejection message
- [x] Reset consultation
- [x] Status banners for approved, edited, rejected

### 1 — Patient Analysis (`/patient`)

- [x] Intake form with the original defaults, prefilled from `patient` or portal intake
- [x] Fields: name, age, gender, height, weight, duration, BP, LDL, HbA1c, symptoms, history, family history, lifestyle, medications, notes
- [x] Analyze Patient saves `patient` and opens Generic GPT
- [x] Clarification card: this is the live session input, not automatically a historical file
- [x] Optional: load a saved profile id so timeline context can enter later prompts

### 2 — GPT vs Twin / Generic baseline (`/generic`)

- [x] Requires `patient`
- [x] Generates generic consultation once and keeps it
- [x] Summary, possible concerns, suggested next steps, risk notes
- [x] Interpretation note: no historical memory and no graph
- [x] Button to open the Vimlesh twin
- [x] Regenerate

### 3 — Vimlesh Twin (`/twin`)

- [x] Requires `patient`; generates once
- [x] Assessment, unique factors, historical patterns with similarity tooltip text
- [x] Recommended tests, immediate actions, follow-up plan
- [x] Confidence score and breakdown (base + retrieval + graph, cap 0.98)
- [x] Sources and disclaimer
- [x] Button to open GPT vs Twin difference
- [x] Doctor photo

### 4 — GPT Twin Comparison (`/compare`)

- [x] Requires patient and generic result
- [x] Builds twin result if it is missing
- [x] Side-by-side generic vs twin, including the three approach bullets each
- [x] Metrics: historical cases used, graph links, twin confidence
- [x] Continue to Evidence Center

### 5 — Evidence Panel (`/evidence`)

- [x] Three cards: Historical Cases, Graph Intelligence, Why This Recommendation
- [x] Each card opens the matching page

### 6 — Historical Case Intelligence (`/cases`)

- [x] Requires `patient`
- [x] Top similar cases (top 8) with similarity, symptoms, risks, tests, diagnosis, decision, outcome
- [x] Search, sort, filter
- [x] Empty state
- [x] Open Graph Intelligence

### 7 — Graph Intelligence (`/graph`)

- [x] Requires `patient`
- [x] Interactive graph of nodes and edges
- [x] Evidence summary
- [x] Highlighted links (first five, with labels)
- [x] Open Comparison Insights

### 8 — Comparison Insights (`/insights`)

- [x] Requires generic and twin results
- [x] Six scores with the original help text
- [x] Bar chart
- [x] Info line about context-aware twin reasoning
- [x] Open Why This Recommendation
- [x] Also show Generic Context Depth and Twin Context Depth (returned by the engine, previously not drawn)

### 9 — Why This Recommendation (`/why`)

- [x] Requires twin result
- [x] Retrieved signals, patient-specific factors, differences from matched cases, contraindication checks
- [x] Confidence metric
- [x] Open explainability and open admin

### 10 — Admin / Dataset (`/admin`)

- [x] Counts: doctor cases, patient profiles, graph nodes, graph edges
- [x] Pie chart
- [x] Dataset registry with descriptions and present/missing state
- [x] Patient table (search, sort, filter) and historical case catalog
- [x] Pipeline-ready message
- [x] Clarification card about Patient Analysis

### 11 — Explainability (`/explain`)

- [x] Requires patient, generic, and twin
- [x] End-to-end pipeline with this run's case count, graph links, and confidence formula
- [x] Five technology expanders
- [x] Generic vs twin difference cards
- [x] Interpretation guidance
- [x] Return to Why This Recommendation

## Existing HTTP API (kept)

- `GET /health`
- `POST /analyze` `/generic` `/twin` `/graph` `/cases`
- Models in `backend/models.py` (`PatientInput` and the response models)

## Accuracy changes

Documented after implementation in the section below. Do not treat generic mode as case-grounded: that page is the no-memory baseline on purpose.

### Changes made

1. Specialist system prompt now includes every row of `doctor_style_examples.csv` (calm, numbered steps, prevention, tests for exertional symptoms, plain risk language, follow-up timelines, urgency balanced with reassurance, diabetes as a risk enhancer).
2. `prompts/doctor_twin.txt` asks for case ids, clarifying questions, and an explicit "not a substitute for a real doctor" close. Unfilled `{placeholders}` are no longer sent as the system message.
3. Retrieved cases passed to the model now include similarity, symptoms, risks, tests, diagnosis, decision, and outcome. Answers stay patient-first; cases are references.
4. Rerank still uses the original chest pain / LDL / diabetes / BP and CAD bonuses, plus a small extra bonus when hypertension, smoking, obesity, CKD, or family history overlap the case risk factors.
5. Graph guidance from `prompts/graph_reasoning.txt` and the patient-weighing note in `prompts/patient_summary.txt` are inserted into the twin prompt. Graph matching itself is unchanged.
6. Selecting a `patient_profiles.csv` id attaches that profile and a short `patient_timelines.csv` summary. No profile is attached unless the user selects one.
7. Empty symptoms, duration, blood pressure, or medicines produce clarifying questions in the prompt and in the UI.
8. Every specialist and generic payload includes a disclaimer and a source list (cases and graph lines for the twin; patient-only note for generic).
9. Follow-up turns include the last eight messages. Specialist follow-ups also see retrieved case lines. Generic follow-ups stay free of case memory.
10. Confidence is the same formula: `min(0.98, 0.60 + 0.07*cases + 0.03*graph_links)`.
11. FAISS, graph, CSV tables, prompts, and the OpenAI client load once at startup.

## Feature sign-off

Checked after the new UI was exercised in the browser at http://localhost:8000: home, consultation intake, specialist twin answer with sources and confidence, graph evidence, and the admin tables. API tests: 13 passed.

## Step 5 removal

Nothing in `backend/` or `web/` imported `frontend/`. Removed only the Streamlit app:

- `frontend/streamlit_app.py`
- `frontend/ui.py`
- `frontend/__init__.py`
- `frontend/pages/0_Consultation_Portal.py` through `frontend/pages/11_Backend_Story.py`
- `frontend/assets/doctor_photo.png` and `frontend/assets/logo.png` (copies already live in `web/public`)
- Streamlit bytecode under `frontend/__pycache__`

Also removed `streamlit` and `plotly` from `requirements.txt`. Plotly was only used by the Streamlit charts. There was no `.streamlit/` folder.

`data/` was not modified.

## Cache note

`data/processed/cases.index` and `data/processed/embeddings_cache.pkl` are OneDrive offline files. Reading them times out, so they were left untouched. Until OneDrive makes them available locally, search uses an in-memory TF-IDF index built from the case spreadsheet. Right-click those two files in Explorer and choose "Always keep on this device" to use the original FAISS index again.

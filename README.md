# CardioTwin AI

CardioTwin AI is a clinical decision-support web app. It demonstrates a digital twin of **Dr. Vimlesh Pandey, Senior Preventive Cardiologist**. You enter a patient, then compare two answers side by side:

- **Generic GPT** answers from the current patient only. It does not search the doctor's past cases.
- **Vimlesh Twin** answers in the doctor's style, grounded in similar historical cases and a cardiology knowledge graph, and it shows the sources, the graph links, and a confidence score.

This is decision support for learning and demonstration. It is not a diagnosis, not a prescription, and not a substitute for a real doctor or emergency care. Worsening chest pain, pain at rest, fainting, or severe breathlessness needs urgent care.

The live product is a React site served by one FastAPI process. Open it at **http://localhost:8000**.

---

## What you need installed

Install these once, before you clone anything.

| Tool | Why | Where |
| --- | --- | --- |
| Git | Downloads the code from GitHub | https://git-scm.com/download/win |
| Python 3.11 or newer | Runs the API, retrieval, and graph. Python 3.13 works. | https://www.python.org/downloads/ |
| Node.js 18 or newer (LTS is fine) | Builds the React website. npm comes with Node. | https://nodejs.org |
| Visual Studio Code | Edits and runs the project. Cursor works the same way. | https://code.visualstudio.com |

On the Python installer, tick **Add python.exe to PATH**. After installing, close and reopen any terminal so `python`, `git`, and `node` are found.

You do not change the PowerShell execution policy. The project starts with `.bat` files, which Windows runs through Command Prompt.

An OpenAI API key is optional. With a key, answers are written by the model in `.env` (default `gpt-4o-mini`). With an empty key, the app still starts and uses a local fallback sentence plus local TF-IDF search over the cases.

---

## Get the code from GitHub into VS Code

The repository is:

https://github.com/Ishaan0709/Doctor_Digital_Twin.git

The default branch is `main`.

### 1. Clone

Open **PowerShell** (Windows key, type `PowerShell`, Enter) and run:

```powershell
cd $env:USERPROFILE\Desktop
git clone https://github.com/Ishaan0709/Doctor_Digital_Twin.git
cd Doctor_Digital_Twin
```

That creates a folder named `Doctor_Digital_Twin`. Everything in this README — `setup.bat`, `backend`, `web`, `data` — is inside that folder. That folder is the project root.

If the folder already exists on this machine under `Desktop\Doctor_twin\doctor-digital-twin`, you do not need to clone again. Open that inner folder. The extra `Doctor_twin` folder around it only contains shortcut scripts that jump into `doctor-digital-twin` and run the same `setup.bat` and `start.bat`.

### 2. Open it in VS Code

1. Start Visual Studio Code.
2. **File → Open Folder**.
3. Select the cloned `Doctor_Digital_Twin` folder (the one that contains `setup.bat` and `backend`).
4. Click **Select Folder**.
5. If VS Code asks to trust the folder, choose **Yes, I trust the authors**.

Open the terminal inside VS Code with **Terminal → New Terminal**, or press **Ctrl+`**. The prompt should already be inside the project folder. Confirm with:

```powershell
pwd
dir
```

You should see `setup.bat`, `start.bat`, `backend`, `web`, and `data`.

### 3. First-time setup

Still in that terminal:

```powershell
.\setup.bat
```

`setup.bat` does all of this, in order:

1. Checks that Node.js is installed.
2. Reuses a virtual environment if one already exists at `.venv` in this folder, or at `.venv` in the parent folder. Otherwise it creates `.venv` here with `py -3 -m venv` (or `python -m venv` if `py` is missing).
3. Upgrades pip and installs `requirements.txt` into that environment.
4. Runs `npm install` and `npm run build` inside `web/`, which writes the static site to `web/dist`.
5. If `.env` is missing, copies `.env.example` to `.env`. If `.env` already exists, it is left alone.

When it finishes it prints `Setup complete. Next, run start.bat`.

### 4. Add the API key

In VS Code, open `.env` in the project root. It looks like this (values only, no quotes):

```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4o-mini
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
APP_ENV=development
```

Paste your key after `OPENAI_API_KEY=`. Save the file. Never commit `.env`. It is listed in `.gitignore`.

### 5. Start the app

```powershell
.\start.bat
```

`start.bat` finds the virtual environment, checks that `web/dist/index.html` exists, opens the browser to **http://localhost:8000**, and starts Uvicorn on `127.0.0.1:8000`. Leave that terminal open. Closing it, or pressing Ctrl+C, stops the server.

The same process serves the website and the API. There is no second server to start for normal use.

### 6. Confirm it is up

In the browser you should see the CardioTwin AI home page: logo, photo of Dr. Vimlesh Pandey, **Start Analysis**, and **Open Consultation Portal**.

A second check, in a new terminal:

```powershell
curl http://127.0.0.1:8000/health
```

Expected body: `{"status":"ok","service":"CardioTwin AI"}`.

Interactive API docs are at http://localhost:8000/docs.

---

## Every later time

From the project folder in a terminal:

```powershell
.\start.bat
```

You only run `.\setup.bat` again after a fresh clone, after `requirements.txt` or `web/package.json` changes, or if `web/dist` was deleted.

---

## While you are editing the website

```powershell
.\dev.bat
```

This starts both processes in one window:

- API with reload on http://127.0.0.1:8000
- Vite on http://127.0.0.1:5173, and the browser opens there

Vite proxies `/api`, `/health`, `/analyze`, `/generic`, `/twin`, `/graph`, and `/cases` to port 8000, so the page on 5173 still talks to the Python API. Use 5173 while editing React. Use `.\start.bat` and port 8000 when you want the built site the way a visitor sees it.

Ctrl+C in that window stops both processes.

---

## Mac or Linux

From the project folder:

```bash
chmod +x setup.sh start.sh dev.sh
./setup.sh
```

Put the key in `.env`, then:

```bash
./start.sh
```

Open http://localhost:8000. For hot reload, `./dev.sh`.

---

## A walkthrough you can demo

1. Home (`/`) — **Start Analysis**.
2. Patient Intake (`/patient`) — fill the form, or keep the analysis defaults, then **Analyze Patient**. The patient is saved in the browser.
3. Generic GPT Clinical Baseline (`/generic`) — the general answer streams in. It uses only this patient.
4. Vimlesh Twin (`/twin`) — the specialist answer streams in, with similar cases, graph links, tests, actions, follow-up, and confidence.
5. GPT Twin Comparison (`/compare`) — both answers next to each other.
6. Historical Cases (`/cases`), Graph Intelligence (`/graph`), Comparison Insights (`/insights`), Why This Recommendation (`/why`), Explainability (`/explain`).
7. Admin / Dataset (`/admin`) — row counts, search, and a button that loads a saved profile into the intake form.
8. Consultation Portal (`/consultation`) — a separate chat. Pick **General** or **Specialist**, then ask follow-up questions. The doctor view can edit the draft and Accept or Reject it. Accept of an edited draft is stored as `edited_approved`.

The demo patient used by the portal is **Aarav Mehta**, age 52. Analysis defaults are a different sample (age 45, chest discomfort and fatigue). Saving a new patient clears the previous generic and twin answers so the next pages generate again.

Light and dark mode is the sun/moon control in the top bar. The choice is remembered.

---

## Environment variables

All of them live in `.env` in the project root. `config.py` loads that file with `python-dotenv`. Names and defaults are also in `.env.example`.

| Variable | Required | Default | What it does |
| --- | --- | --- | --- |
| `OPENAI_API_KEY` | No | empty | Chat answers, and OpenAI embeddings when the on-disk index can be read. Empty means a local fallback answer and TF-IDF search. |
| `OPENAI_MODEL` | No | `gpt-4o-mini` | Chat model for generic, twin, and follow-up text. |
| `OPENAI_EMBEDDING_MODEL` | No | `text-embedding-3-small` | Embedding model used when building or querying the OpenAI FAISS index. |
| `APP_ENV` | No | `development` | Label only (`development` or `production`). It does not switch a deploy target. |

---

## How one specialist answer is built

Startup loads the heavy pieces once (`backend/resources.py`, called from the FastAPI lifespan):

1. The six CSV tables in `data/raw` are read into memory.
2. The knowledge graph is built from the node and edge CSVs and kept as one NetworkX graph.
3. The case index is warmed (FAISS if the cache files are readable, otherwise an in-memory TF-IDF index).
4. The four prompt files in `prompts/` are read.

Then, for a twin consultation:

1. The patient form is checked by `PatientInput` in `backend/models.py`. A bad field returns HTTP 422 and the message `Please check the form. …`.
2. The patient is turned into one text block (`patient_to_text`). BMI is computed from height and weight.
3. The five most similar historical cases are retrieved and reranked.
4. The graph walker matches words in the patient text to node names and collects outgoing links.
5. Style rules from `doctor_style_examples.csv` are inserted into `prompts/doctor_twin.txt`. If a saved `profile_id` was chosen, that profile and its timeline rows are inserted too. If symptoms, duration, blood pressure, or medicines are empty, clarifying questions are added.
6. The model streams the assessment. The HTTP response is server-sent events: `meta`, then `token`, then `done`. The system prompt and the user prompt are not sent to the browser.
7. The response also includes fixed plan lists (tests, immediate actions, follow-up), sources, graph evidence, a disclaimer, and confidence.

Confidence is fixed by this formula, capped at 0.98:

`min(0.98, 0.60 + 0.07 × number of retrieved cases + 0.03 × number of graph links)`

Generic consultation uses `prompts/generic_gpt.txt` and the same patient text. It does not retrieve cases and does not walk the graph. Its concern list, next steps, and risk notes are fixed safety lists. Only the narrative is generated.

Follow-up chat keeps the last turns. Specialist follow-ups include style rules and the retrieved case lines. Generic follow-ups stay on the current conversation and do not use case memory.

Comparison scores (`twin_engine/compare_engine.py`) are keyword heuristics on the two answers, plus a bonus when the twin actually retrieved cases and graph links. They are explanation scores for the demo, not a clinical grade. The eight names are Personalization, Use of Historical Evidence, Risk Sensitivity, Explainability, Actionability, Specialist Alignment, Generic Context Depth, and Twin Context Depth.

---

## Screens

The sidebar groups and the top stepper both use these routes. An unknown URL shows “Page not found”.

| Route | Sidebar label | File | What it does |
| --- | --- | --- | --- |
| `/` | Home | `web/src/pages/Home.tsx` | Landing. Logo, doctor photo, three metrics, problem cards, **Start Analysis**, **Open Consultation Portal**. |
| `/consultation` | Consultation Portal | `web/src/pages/ConsultationPortal.tsx` | Intake, General or Specialist chat, streaming, copy, regenerate, Patient/Doctor view, Accept and Reject. |
| `/patient` | Patient Analysis | `web/src/pages/PatientAnalysis.tsx` | Intake form. **Analyze Patient** saves the patient and opens `/generic`. |
| `/generic` | GPT vs Twin | `web/src/pages/GenericBaseline.tsx` | Streams the generic baseline once and stores it. |
| `/twin` | Vimlesh Twin | `web/src/pages/VimleshTwin.tsx` | Streams the specialist assessment, sources, plans, and confidence. |
| `/compare` | GPT Twin Comparison | `web/src/pages/Comparison.tsx` | Side-by-side answers. Streams the twin first if it is missing. |
| `/evidence` | Evidence Panel | `web/src/pages/Evidence.tsx` | Three links into cases, graph, and why. |
| `/cases` | Historical Cases | `web/src/pages/HistoricalCases.tsx` | Searchable table of the top similar cases for this patient. |
| `/graph` | Graph Intelligence | `web/src/pages/GraphPage.tsx` | Force-directed graph plus the evidence sentences. Filter box highlights nodes. |
| `/insights` | Comparison Insights | `web/src/pages/Insights.tsx` | Bar chart of the comparison scores and a short meaning for each. |
| `/why` | Why This Recommendation | `web/src/pages/Why.tsx` | Retrieved cases, uniqueness flags, safety notes, confidence breakdown. |
| `/explain` | Explainability | `web/src/pages/Explain.tsx` | Plain-language pipeline from the CSVs to the score, using this run’s counts. |
| `/admin` | Admin / Dataset | `web/src/pages/Admin.tsx` | Counts, pie chart, registry, profile table, case catalog. **Load** copies a profile into the session and opens intake. |

Shared UI:

| File | What it is |
| --- | --- |
| `web/src/components/Layout.tsx` | Sidebar, mobile drawer, stepper, theme toggle. |
| `web/src/components/PatientForm.tsx` | The intake form used by Analysis and the Portal, including risk checkboxes and the demo-patient button. |
| `web/src/components/DataTable.tsx` | Table with search, filter, sort, and pages of 8 rows. |
| `web/src/components/ui.tsx` | Buttons, cards, page headers, notes, skeletons, disclaimer, bullet lists, source list, confidence panel. |
| `web/src/lib/api.ts` | `getJson`, `postJson`, and `streamConsult` (reads SSE `data:` events). |
| `web/src/lib/utils.ts` | Class-name helper, BMI, error text from API failures. |
| `web/src/store/useAppStore.ts` | Zustand store, persisted in the browser under the key `cardiotwin-session`. |
| `web/src/types.ts` | Patient, results, chat types, demo patient, analysis defaults. |
| `web/src/App.tsx` | Route table and page transition. |
| `web/src/main.tsx` | React root, router, toast notifications. |
| `web/src/index.css` | Tailwind layers and a few global styles. |
| `web/src/vite-env.d.ts` | TypeScript shim, including the force-graph component. |

Patient fields, validated on the server: name, age (1–120), gender, height in cm (50–260), weight in kg (20–350), symptoms, symptom duration, medical history, family history, lifestyle, current medications, blood pressure, LDL (0–400), HbA1c (0–20), notes, and an optional `profile_id`.

What the browser remembers (`cardiotwin-session`): theme, the analysis patient, the generic result, the twin result, and the portal (patient, mode `general` or `specialist`, chat, draft, original draft, twin bundle, approved text, rejected flag, doctor status `approved` / `edited_approved` / `rejected`, and view `Patient` or `Doctor`).

---

## HTTP API

The browser uses the `/api/...` routes. The older paths are still there so older clients keep working. Both sets hit the same functions.

| Method and path | Also available as | Purpose |
| --- | --- | --- |
| `GET /health` | | `{status, service}` |
| `GET /api/health` | | Health plus dataset counts |
| `GET /api/bootstrap` | | Doctor profile, disclaimer, counts, dataset registry |
| `GET /api/datasets` | | Counts and the six-file registry |
| `GET /api/patients` | | Rows from `patient_profiles.csv` |
| `GET /api/patients/{id}/timeline` | | Visits for one profile id |
| `GET /api/cases/catalog` | | Case rows for the admin table |
| `POST /api/patient/summary` | | BMI and a short summary of the submitted patient |
| `POST /api/consult/analyze` | `POST /analyze` | Summary plus generic plus twin in one call |
| `POST /api/consult/generic` | `POST /generic` | Generic answer |
| `POST /api/consult/twin` | `POST /twin` | Twin answer |
| `POST /api/consult/followup` | | One follow-up reply |
| `POST /api/consult/stream` | | SSE stream. Body `kind` is `generic`, `twin`, or `followup` |
| `POST /api/evidence/graph` | `POST /graph` | Nodes, edges, evidence sentences for this patient |
| `POST /api/evidence/cases` | `POST /cases` | Similar cases for this patient |
| `POST /api/compare` | | The eight comparison metrics |

Stream events look like `data: {"type":"meta"|"token"|"done"|"error", ...}`.

`GET /` and every other non-API path return the built React app from `web/dist`, if that build exists. If it does not, the server answers 503 with `Frontend is not built yet. Run setup.bat, then start.bat.`

CORS allows the Vite origin (port 5173) and the app origin (port 8000).

---

## Folder structure

```
Doctor_Digital_Twin/          ← this is the GitHub repo root
├── .env                      ← your key. Not committed.
├── .env.example              ← the four variable names, no secrets
├── .gitignore
├── config.py                 ← paths, env loading, creates output folders
├── requirements.txt
├── setup.bat  setup.sh       ← first-time install and frontend build
├── start.bat  start.sh       ← open the built app on port 8000
├── dev.bat    dev.sh         ← API + Vite together
├── README.md                 ← this file
├── MIGRATION_NOTES.md        ← conversion checklist from the old UI
├── backend/                  ← FastAPI app
├── rag/                      ← case ingest, embeddings, FAISS, rerank
├── graph_rag/                ← knowledge graph
├── twin_engine/              ← doctor profile, prompts, comparison scores
├── prompts/                  ← the text templates sent to the model
├── data/
│   ├── raw/                  ← source CSVs. Do not edit these to “fix” the app
│   └── processed/            ← index, cleaned cases, graph export
├── scripts/                  ← venv lookup and the one-window dev runner
├── tests/
├── notebooks/                ← exploratory notebooks, not used at runtime
├── outputs/                  ← logs, reports, demo exports (created on startup)
└── web/                      ← React + Vite + TypeScript + Tailwind
    ├── public/               ← logo.png, doctor_photo.png
    ├── src/
    └── dist/                 ← production build. Created by setup. Not committed.
```

On this computer the repo may sit inside `Desktop\Doctor_twin\doctor-digital-twin`. The parent `Doctor_twin` folder is only a wrapper: its `setup.bat`, `start.bat`, and `dev.bat` change into `doctor-digital-twin` and call the scripts above. Those wrapper files are not required on GitHub.

### Root files

| File | Role |
| --- | --- |
| `config.py` | `BASE_DIR`, `DATA_RAW_DIR`, `DATA_PROCESSED_DIR`, `PROMPTS_DIR`, `OUTPUT_DIR`. Loads `.env`. Reads the four environment variables. Creates `outputs/logs`, `outputs/reports`, and `outputs/demo_exports` if they are missing. |
| `requirements.txt` | Python packages: fastapi, uvicorn, openai, pandas, numpy, faiss-cpu, networkx, python-dotenv, scikit-learn, pydantic, httpx, pytest. |
| `setup.bat` / `setup.sh` | Create or reuse `.venv`, pip install, npm install, npm build, copy `.env.example` when `.env` is missing. |
| `start.bat` / `start.sh` | Set `PYTHONDONTWRITEBYTECODE=1`, resolve the venv, require `web/dist/index.html`, open the browser, run `uvicorn backend.app:app --host 127.0.0.1 --port 8000`. |
| `dev.bat` / `dev.sh` | Run `scripts/dev_server.py`. |
| `.env.example` | Template. Safe to commit. |
| `.env` | Real key. Never commit. |
| `.gitignore` | Ignores `.venv`, `__pycache__`, `.env`, `node_modules`, `web/dist`, `*.pkl`, `*.index`, and generated files under `outputs/`. |
| `MIGRATION_NOTES.md` | Inventory of the old interface and the accuracy notes from the React conversion. Historical. The running app is `web/` plus `backend/`. |
| `README.md` | This guide. |

### `backend/`

| File | Role |
| --- | --- |
| `app.py` | FastAPI application named CardioTwin AI, version 2.0.0. Lifespan calls `load_resources`. CORS. Turns validation errors into “Please check the form.” Serves `web/dist` for the website, and refuses path traversal outside that folder. |
| `routes.py` | Every HTTP route listed above, including the SSE generator. |
| `models.py` | Pydantic request and response models: `PatientInput`, `GenericResponse`, `TwinResponse`, `AnalyzeResponse`, `CasesResponse`, `GraphResponse`, `FollowupRequest`, `StreamRequest`, `CompareRequest`. |
| `utils.py` | Patient text, BMI summary, confidence math, OpenAI client (created once), streaming chat, generic bundle, twin bundle, follow-up replies, case matches, graph payload. |
| `context.py` | Disclaimer text. Loads and caches the six CSVs. Style rules, clarifying questions, profile text, timeline text, profile list, case catalog, dataset registry and counts. |
| `resources.py` | `load_resources()`: warm tables, warm graph, warm search index, load the four prompts. |
| `__init__.py` | Marks the folder as a Python package. |

### `rag/`

| File | Role |
| --- | --- |
| `ingest_cases.py` | Reads `doctor_cases_vimlesh_pandey.csv`, maps columns into a stable schema (`case_id`, age, sex, symptoms, risk factors, tests, diagnosis, decision, outcome, notes), and builds a `rag_text` string per case. Writes `data/processed/cleaned_cases.csv` only when `persist=True`. |
| `embed_cases.py` | `Embedder`. Uses OpenAI embeddings when a key is set and `force_local` is false. Otherwise TF-IDF from scikit-learn. |
| `vector_store.py` | Build, save, and search a FAISS index. If `cases.index` or `embeddings_cache.pkl` is an OneDrive cloud-only placeholder, or the read fails, it reports the index unreadable and does not overwrite those files. |
| `retrieve.py` | Loads the index once behind a lock. If the disk index is unreadable, builds an in-memory TF-IDF index and does not write it back. `retrieve_similar_cases` returns the top matches (default 5). |
| `rerank.py` | Adds a small score bonus when the patient text overlaps case text on chest pain, LDL, diabetes, blood pressure, and CAD, and a smaller bonus when risk factors overlap (hypertension, smoking, obesity, CKD, family history). |
| `__init__.py` | Package marker. |

### `graph_rag/`

| File | Role |
| --- | --- |
| `build_graph.py` | Builds a directed NetworkX graph from `graph_nodes.csv` and `graph_edges.csv`. Node types in the data include Disease, RiskFactor, Test, Decision, DoctorPreference, and Symptom. Caches the graph. Also writes `data/processed/graph_export.json`. |
| `reasoning.py` | `graph_reasoning`: matches patient words to node names and lists the linked nodes and relation names. |
| `graph_queries.py` | `load_graph()` helper used by older call sites. |
| `neo4j_loader.py` | Empty stub. The comment says Neo4j is not used. The graph is local NetworkX only. |
| `__init__.py` | Package marker. |

### `twin_engine/`

| File | Role |
| --- | --- |
| `doctor_profile.py` | Name, title, and style traits for Dr. Vimlesh Pandey. |
| `twin_prompt.py` | Loads prompt files (cached) and fills `doctor_twin.txt`. Braces in patient text are escaped so they are not treated as format fields. |
| `personalization.py` | `extract_uniqueness_flags`: younger chest symptoms, kidney disease, high HbA1c with diabetes, overlapping blood thinners, obesity, atypical symptoms, high LDL. |
| `compare_engine.py` | `generate_comparison_metrics` for the eight scores. |
| `__init__.py` | Package marker. |

### `prompts/`

| File | Role |
| --- | --- |
| `doctor_twin.txt` | Specialist template. Placeholders: style rules, how to weigh the patient, graph guidance, patient context, timeline, retrieved cases, graph summary, uniqueness, clarifying questions. |
| `generic_gpt.txt` | Generic system prompt. Current patient only, clarifying questions, emergency line, decision-support wording. |
| `graph_reasoning.txt` | Short guidance inserted into the twin prompt about citing relation names. The graph walk itself stays the Python function in `graph_rag/reasoning.py`. |
| `patient_summary.txt` | Short guidance that the live patient outweighs old cases. |

### `scripts/`

| File | Role |
| --- | --- |
| `resolve_venv.bat` | Sets `VENV` to this folder’s `.venv` if `Scripts\python.exe` exists, otherwise the parent folder’s `.venv`. Prints an error if neither exists. |
| `dev_server.py` | Starts Uvicorn with `--reload` and `npm run dev` in one window, prefixes their logs, opens http://localhost:5173 when that port accepts a connection, and stops both process trees on exit. |

### `tests/`

| File | What it checks |
| --- | --- |
| `test_api.py` | Health, datasets, the 422 form message, generic and twin response shape, an SSE stream, summary BMI, compare metrics, follow-up, and cases. OpenAI and retrieval are replaced with fakes so the test does not call the network. |
| `test_context.py` | Clarifying questions when fields are empty, style rules loaded from the CSV, timeline text for profile `P001`. |
| `test_compare.py` | Comparison metric names exist. |
| `test_rag.py` | Retrieval returns a list. |
| `test_graph.py` | Graph reasoning returns a summary. |

Run them from the project folder, after setup:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\python.exe -m pytest --rootdir . -p no:cacheprovider -q tests
```

If setup reused the parent folder’s virtual environment, call that `python.exe` instead of `.\.venv\Scripts\python.exe`. `PYTHONDONTWRITEBYTECODE=1` avoids writing `.pyc` files, which matters when the project lives in OneDrive.

### `notebooks/`

Exploratory only. The website and the API do not import them.

| File | Intent |
| --- | --- |
| `data_exploration.ipynb` | Looking at the raw CSVs. |
| `graph_testing.ipynb` | Trying the knowledge graph. |
| `prompt_testing.ipynb` | Trying prompt text. |

### `outputs/`

Created by `config.py` the first time the app or tests import it.

| Folder | Intent |
| --- | --- |
| `outputs/logs/` | Runtime logs, if a script writes them. |
| `outputs/reports/` | Generated reports. |
| `outputs/demo_exports/` | Exported demo artifacts. |

These generated files are gitignored. The folders may be empty.

### `web/` (the other files)

| File | Role |
| --- | --- |
| `package.json` | npm name `cardiotwin-web`, version 2.0.0. Scripts: `dev` (Vite), `build` (`tsc --noEmit` then `vite build`), `preview`. Dependencies: React 18, React Router 6, Zustand, Tailwind utilities (`clsx`, `tailwind-merge`), Framer Motion, Recharts, react-force-graph-2d, Sonner toasts, Lucide icons. |
| `package-lock.json` | Exact npm versions from the last install. |
| `index.html` | HTML shell. Dark class on `<html>`. Favicon is `/logo.png`. |
| `vite.config.ts` | Vite on port 5173 and the API proxy to `127.0.0.1:8000`. |
| `tsconfig.json` | TypeScript project settings. |
| `tailwind.config.js` | Tailwind, class-based dark mode, Segoe UI font stack. |
| `postcss.config.js` | PostCSS with Tailwind and Autoprefixer. |
| `public/logo.png` | Logo in the sidebar, home page, and favicon. |
| `public/doctor_photo.png` | Photo on the home page. |
| `dist/` | Built JS and CSS. `start.bat` serves this. Not committed. Rebuild with `setup.bat` or `npm run build` inside `web/`. |
| `node_modules/` | Installed npm packages. Not committed. |

### `data/raw/` (source data, leave the files as they are)

| File | Columns the app expects | Used for |
| --- | --- | --- |
| `doctor_cases_vimlesh_pandey.csv` | case id, age, sex, symptoms, risk factors, tests, diagnosis, treatment decision, outcome (names are matched flexibly) | Retrieval corpus and the admin case table. About 500 rows. |
| `patient_profiles.csv` | `patient_id`, `age`, `sex`, `chief_complaint`, `history`, `medications`, `ldl`, `hba1c` | Admin table, and extra prompt context only when a profile id is selected. About 120 rows. Height and weight are not in this file. |
| `patient_timelines.csv` | `patient_id`, `date`, `systolic_bp`, `diastolic_bp`, `hba1c`, `weight_kg` | Timeline text in the specialist prompt for a selected profile. About 720 rows. |
| `graph_nodes.csv` | `node_id`, `name`, `type` | Graph nodes. About 34. |
| `graph_edges.csv` | `source_id`, `target_id`, `relation` | Graph edges. About 116. |
| `doctor_style_examples.csv` | Style rule text | Inserted into the specialist prompt. About 8 rules. |

Row counts are also shown live on **Admin / Dataset**. Treat that page as the source of truth if a file changes.

### `data/processed/`

| File | Role |
| --- | --- |
| `cleaned_cases.csv` | Normalized cases written by ingest. |
| `cases.index` | FAISS index. Large. Gitignored. |
| `embeddings_cache.pkl` | Metadata beside that index. Gitignored. |
| `graph_export.json` | JSON copy of the graph, rewritten when the graph is built. |

If this project folder is inside OneDrive, `cases.index` and `embeddings_cache.pkl` are sometimes cloud-only placeholders. The file size shows in Explorer, but Python cannot read them, and the app must not overwrite them. In that case search uses an in-memory TF-IDF index for the current process. To use the original embeddings, right-click each of those two files in Explorer and choose **Always keep on this device**, then start the app again.

---

## Doctor profile used by the twin

From `twin_engine/doctor_profile.py`:

- Name: Dr. Vimlesh Pandey
- Title: Senior Preventive Cardiologist
- Style: calm, concise, evidence-driven, preventive, balances urgency with reassurance, prefers tests when needed, explains in simple language

Historical cases are references. The prompt tells the model not to copy an old case onto the current patient, not to invent doses or results, and to name the case ids it used.

---

## Troubleshooting

| What you see | What to do |
| --- | --- |
| `Node.js is required` | Install Node from https://nodejs.org, close the terminal, run `.\setup.bat` again. |
| `Could not create a Python virtual environment` | Install Python 3.11+ with **Add to PATH**, then run `.\setup.bat` again. |
| `Frontend build not found. Run setup.bat first.` | `.\setup.bat` did not finish the npm build. Run it again and read the last error. |
| `No virtual environment found` | Run `.\setup.bat` in this folder. |
| Browser says the frontend is not built (HTTP 503) | Same as above: run `.\setup.bat`, then `.\start.bat`. |
| `Please check the form` | A field is outside the ranges in `PatientInput` (age, height, weight, LDL, HbA1c, or an empty name). |
| Port 8000 already in use | Another `start.bat` or `dev.bat` is still running. Close that terminal, or end the `uvicorn` process, then start again. |
| Page loads but answers are a short local fallback | `OPENAI_API_KEY` is empty or rejected. Edit `.env`, save, and restart `start.bat`. |
| Similar-case scores look like keyword overlap | The FAISS files were not readable (often OneDrive). Pin `cases.index` and `embeddings_cache.pkl` as described above. |
| Setup or tests sit with no CPU and no output | OneDrive placeholders, including old `__pycache__` folders. Delete `__pycache__` folders inside the project (not inside `.venv` unless you know you need to), keep `PYTHONDONTWRITEBYTECODE=1` (the start scripts already set it), and pin the two cache files. |
| Changes to React do not show on port 8000 | Port 8000 serves `web/dist`. Run `npm run build` inside `web/`, or use `.\dev.bat` and open port 5173. |
| `.\setup.bat` is not recognized | You are not in the project folder. `cd` into the clone, the folder that contains `setup.bat`. |

---

## What is deliberately absent

- No Docker, no cloud deploy files, no CI config in this tree.
- No Streamlit UI. The current interface is `web/`.
- No Neo4j database. `graph_rag/neo4j_loader.py` is a stub.
- `.venv`, `web/node_modules`, and `web/dist` are local install products. `setup.bat` recreates them.
- `.env` is local. Share `.env.example`, not the key.

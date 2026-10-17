# CardioTwin AI

CardioTwin AI is a clinical decision-support web app. It demonstrates a digital twin of **Dr. Vimlesh Pandey, Senior Preventive Cardiologist**. You enter a patient, then compare two answers side by side:

- **Generic GPT** answers from the current patient only. It does not search the doctor's past cases.
- **Vimlesh Twin** answers in the doctor's style, grounded in similar historical cases and a cardiology knowledge graph, and it shows the sources, the graph links, and a confidence score.

This is decision support for learning and demonstration. It is not a diagnosis, not a prescription, and not a substitute for a real doctor or emergency care. Worsening chest pain, pain at rest, fainting, or severe breathlessness needs urgent care.
The live product is a React site served by one FastAPI process. Open it at **https://doctor-digital-twin.vercel.app/**.
API linked through render https://doctor-digital-twin.vercel.app/consultation
https://cardiotwin-api-8coi.onrender.com/health
---

## On this laptop

This section is for the owner of this machine. The project, Python environment, and frontend build are already on this laptop. Pick one of the two ways below. Both open the same app at http://localhost:8000.

### Choice A — one command

```powershell
cd "C:\Users\ISHAAN SHARMA\OneDrive\Desktop\Doctor_twin\doctor-digital-twin"
python run.py
```

`run.py` is the only launcher. It starts the API and the built website together on http://localhost:8000. Leave the window open. Ctrl+C stops it.

While editing the React UI:

```powershell
python run.py dev
```

That opens http://localhost:5173 and still runs the API on port 8000.

### Choice B — the same steps, typed out

Use this when you want to show each command. From PowerShell:

```powershell
cd "C:\Users\ISHAAN SHARMA\OneDrive\Desktop\Doctor_twin\doctor-digital-twin"
$env:PYTHONDONTWRITEBYTECODE = "1"
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

Then open http://localhost:8000. Ctrl+C stops Uvicorn.

If the page says the frontend is not built, build it once, then start Uvicorn again:

```powershell
cd "C:\Users\ISHAAN SHARMA\OneDrive\Desktop\Doctor_twin\doctor-digital-twin\web"
npm run build
cd ..
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

To work on the UI with hot reload, use two PowerShell windows. In the first, from the project folder, with the virtual environment activated:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

In the second:

```powershell
cd "C:\Users\ISHAAN SHARMA\OneDrive\Desktop\Doctor_twin\doctor-digital-twin\web"
npm run dev
```

Open http://localhost:5173. Vite sends API calls to the process on port 8000.

The rest of this file is for someone else: install, clone from GitHub, open in VS Code, and how the project is built.

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

You do not change the PowerShell execution policy. `python run.py` is the only launcher.

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

That creates one folder named `Doctor_Digital_Twin`. That folder is the whole project: `run.py`, `backend`, `web`, `data`, and this README. There is no second project folder and no second README.

### 2. Open it in VS Code

1. Start Visual Studio Code.
2. **File → Open Folder**.
3. Select the cloned `Doctor_Digital_Twin` folder (the one that contains `run.py` and `backend`).
4. Click **Select Folder**.
5. If VS Code asks to trust the folder, choose **Yes, I trust the authors**.

Open the terminal inside VS Code with **Terminal → New Terminal**, or press **Ctrl+`**. The prompt should already be inside the project folder. Confirm with:

```powershell
pwd
dir
```

You should see `run.py`, `backend`, `web`, and `data`.

### 3. First-time setup

Still in that terminal:

```powershell
python run.py setup
```

That one command:

1. Checks that Node.js is installed.
2. Creates `.venv` in this folder if it is missing.
3. Installs `requirements.txt` into that environment.
4. Runs `npm install` and `npm run build` inside `web/`, which writes the website to `web/dist`.
5. If `.env` is missing, copies `.env.example` to `.env`. If `.env` already exists, it is left alone.

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
python run.py
```

This opens http://localhost:8000 and starts Uvicorn on `127.0.0.1:8000`. Leave that terminal open. Closing it, or pressing Ctrl+C, stops the server. If `.venv` or `web/dist` is missing, this command runs setup first.

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
python run.py
```

Run `python run.py setup` again after `requirements.txt` or `web/package.json` changes, or if `web/dist` was deleted.

---

## While you are editing the website

```powershell
python run.py dev
```

This starts both processes in one window:

- API with reload on http://127.0.0.1:8000
- Vite on http://127.0.0.1:5173, and the browser opens there

Vite proxies `/api`, `/health`, `/analyze`, `/generic`, `/twin`, `/graph`, and `/cases` to port 8000, so the page on 5173 still talks to the Python API. Use 5173 while editing React. Use `python run.py` and port 8000 when you want the built site the way a visitor sees it.

Ctrl+C in that window stops both processes.

---

## Mac or Linux

From the project folder:

```bash
python3 run.py setup
```

Put the key in `.env`, then:

```bash
python3 run.py
```

Open http://localhost:8000. For hot reload, `python3 run.py dev`.

The public site is https://doctor-digital-twin.vercel.app/. Its API is https://cardiotwin-api-8coi.onrender.com. A browser on localhost still calls the local API. Any other host calls Render. Render allows that Vercel address. Pushing `main` updates both.

Refreshing a page such as `/insights` stays on that page. `vercel.json` tells Vercel to hand any path that is not a real file back to the app, so the address in the browser still opens.

---

## A walkthrough you can demo

1. Home (`/`) — who the twin is, and how a visit starts. **Begin a consultation** opens intake. **Open the comparison** goes to a separate page.
2. Patient Intake (`/patient`) — **Analyze Patient** saves the details and opens the consultation.
3. Consultation (`/consultation`) — one button starts the Doctor's Twin. Tests, why this reading, and clinician review stay closed until opened.
4. Comparison (`/studio`) — Generic GPT, the Doctor's Twin, the side-by-side page, the graph, why, and the scores. This page sets a general answer beside the Doctor's Twin. The visit itself does not open here.
5. **Doctor's view** in the header opens the full consultation for a clinician to read, edit, Accept, or Reject. **Ask them to come in** is for a serious case the twin should not explain: the patient is asked to see Dr. Pandey in person. The patient view does not show the raw draft. An edited accept is stored as `edited_approved`. A clinic visit is stored as `in_person`.
6. On the comparison page (`/studio`), enter the patient again, or press **Use demo patient**, then save. The comparison pages use those details.

The demo patient used by the portal is **Aarav Mehta**, age 52. Analysis defaults are a different sample (age 45, chest discomfort and fatigue). Saving a new patient clears the previous generic and twin answers so the next pages generate again.

Light and dark mode is the sun/moon control in the header. The choice is remembered. The emergency line is in the footer.

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

## Folder structure

```
Doctor_Digital_Twin/          ← this is the GitHub repo root
├── .env                      ← your key. Not committed.
├── .env.example              ← the four variable names, no secrets
├── .gitignore
├── .venv/                    ← Python environment. Created by run.py. Not committed.
├── config.py                 ← paths, env loading, creates output folders
├── requirements.txt
├── run.py                    ← the only launcher: setup, start, and hot reload
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
├── tests/
├── notebooks/                ← exploratory notebooks, not used at runtime
├── outputs/                  ← logs, reports, demo exports (created on startup)
└── web/                      ← React + Vite + TypeScript + Tailwind
    ├── public/               ← logo.png, doctor_photo.png
    ├── src/
    ├── dist/                 ← production build. Created by python run.py setup. Not committed.
    └── node_modules/         ← installed by python run.py setup. Not committed.
```

### Root files

| File | Role |
| --- | --- |
| `config.py` | `BASE_DIR`, `DATA_RAW_DIR`, `DATA_PROCESSED_DIR`, `PROMPTS_DIR`, `OUTPUT_DIR`. Loads `.env`. Reads the four environment variables. Creates `outputs/logs`, `outputs/reports`, and `outputs/demo_exports` if they are missing. |
| `requirements.txt` | Python packages: fastapi, uvicorn, openai, pandas, numpy, faiss-cpu, networkx, python-dotenv, scikit-learn, pydantic, httpx, pytest. |
| `run.py` | The only way to install and run. `python run.py setup` installs. `python run.py` opens http://localhost:8000. `python run.py dev` runs the API and Vite together. |
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

`PYTHONDONTWRITEBYTECODE=1` avoids writing `.pyc` files, which matters when the project folder is stored in OneDrive.

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
| `package.json` | npm name `cardiotwin-web`, version 2.0.0. Scripts: `dev` (Vite), `build` (`tsc --noEmit` then `vite build`), `preview`. Dependencies: React 18, React Router 6, Zustand, Tailwind utilities (`clsx`, `tailwind-merge`), Framer Motion, Recharts, Sonner toasts, Lucide icons. Graph Intelligence is drawn by `GraphPage.tsx` as its own SVG map. `react-force-graph-2d` may still appear in `package.json` from an earlier version; the page does not import it. |
| `package-lock.json` | Exact npm versions from the last install. |
| `index.html` | HTML shell. Dark class on `<html>`. Favicon is `/logo.png`. |
| `vite.config.ts` | Vite on port 5173 and the API proxy to `127.0.0.1:8000`. |
| `tsconfig.json` | TypeScript project settings. |
| `tailwind.config.js` | Tailwind, class-based dark mode, Segoe UI font stack. |
| `postcss.config.js` | PostCSS with Tailwind and Autoprefixer. |
| `public/logo.png` | Logo in the header, home page, and favicon. |
| `public/doctor_photo.png` | Photo on the home page. |
| `dist/` | Built JS and CSS. `python run.py` serves this. Not committed. Rebuild with `python run.py setup` or `npm run build` inside `web/`. |
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


## The idea of this project

This part is the theory, then the same idea as it exists in this repository. Read one part at a time. Each part has **Theory** and then **In this project**.

### Part 1 — What it is, and why it exists

**Theory.** A large language model such as GPT is trained on a huge amount of text. After training, that knowledge sits inside the model weights. That is called parametric memory. When you ask it a question, it writes a likely next answer from that memory plus the words you just sent. It does not open the doctor's filing cabinet. It does not know which of this doctor's old patients looked like the person in front of you, unless you put those cases into the prompt.

A digital twin, in this project, is not a simulation of a beating heart. It is a software stand-in for one clinician's way of reasoning: the same kind of patient history, the same kind of links between a finding and a test, and the same way of speaking. The model is still a language model. The twin is the extra memory and the instructions wrapped around it.

**Why.** A plain answer can sound medical and still be ungrounded. It may skip a similar past case, invent a connection, or speak in a generic voice. The point of this app is to show the difference between an ungrounded answer and an answer that had to look at cases and a graph first, and to show the sources so a person can check them.

**What is used.**

| Piece | Role |
| --- | --- |
| React + Vite + TypeScript + Tailwind | The website |
| FastAPI + Uvicorn | One Python process that serves the site and the API |
| OpenAI chat (`gpt-4o-mini` by default) | Writes the consultation sentences |
| FAISS, or scikit-learn TF-IDF if the index cannot be read | Finds similar historical cases (RAG) |
| NetworkX | Holds the cardiology graph in memory (GraphRAG) |
| The CSVs in `data/raw/` | The doctor's cases, profiles, timelines, graph, and style rules |

**In this project.** Home, Patient Intake, then two answers. Generic GPT uses the current patient only. Vimlesh Twin uses the current patient, similar cases, graph links, and Dr. Pandey's style rules. Both can call the same chat model. The difference is the context, not a second brain.

The product is decision support for learning and demonstration. It is not a diagnosis and not a prescription.

### Part 2 — How this is different from plain GPT

**Theory.** Give a model only the patient paragraph and it will answer from general medical language. That answer can be fluent and still have three gaps:

1. No case memory. It cannot point at "case 496 looked like this and the outcome was X" unless that text is in the prompt.
2. No explicit relationships. It may say "high LDL matters" without a stored link such as high LDL raises the risk of angina.
3. No personal style. It does not have this doctor's short rules about tone, prevention, and when to escalate.

Grounding means the words the model writes are conditioned on text you retrieved, not only on its training. The model can still phrase something loosely. Grounding reduces that. It does not make the model a doctor.

**In this project.**

| | Generic GPT | Vimlesh Twin |
| --- | --- | --- |
| Prompt file | `prompts/generic_gpt.txt` | `prompts/doctor_twin.txt` |
| Patient text | Yes | Yes |
| Similar cases | No | Yes, top 5 after rerank |
| Knowledge graph | No | Yes, one hop out from matched nodes |
| Doctor style rules | No | Yes, from `doctor_style_examples.csv` |
| Sources shown | A note that this is the current patient only | Case lines and graph lines |
| Code path | `backend/utils.py` generic bundle | `backend/utils.py` twin bundle |

Same form. Same model name in `.env`. The twin request does more work before the model speaks. The pages are `/generic` and `/twin`, side by side on `/compare`.

### Part 3 — RAG

**Theory.** RAG means retrieval-augmented generation. The steps are always the same shape:

1. Turn each document into a vector, a list of numbers that stands for its meaning. Nearby vectors mean similar text. This step is embedding.
2. Store the vectors in an index so you can ask "what is near this query?" quickly. A common index is FAISS.
3. Embed the new question the same way and take the nearest documents. That is retrieval.
4. Optionally rerank those hits with a second, smaller score so an almost-right neighbor can move up.
5. Paste the chosen documents into the prompt and let the model write. The model is not searching. The program searched, then the model read.

If you skip embeddings and score word overlap instead, you still have retrieval. TF-IDF does that: rare words that appear in both the patient text and a case raise the score. It is weaker on paraphrases ("chest discomfort" versus "angina pain") and stronger when the same words are present. It needs no API key.

**In this project.** One historical case is one document. There is no splitting into paragraphs. `rag/ingest_cases.py` reads `doctor_cases_vimlesh_pandey.csv`, builds one `rag_text` string per case (symptoms, risks, tests, diagnosis, decision, outcome), and can write `data/processed/cleaned_cases.csv`.

`rag/embed_cases.py` is the `Embedder`. If `OPENAI_API_KEY` is set, vectors come from `OPENAI_EMBEDDING_MODEL` (default `text-embedding-3-small`). If the key is empty, or the saved index cannot be read, it uses scikit-learn `TfidfVectorizer` with 512 features.

`rag/vector_store.py` builds and searches a FAISS index. The files are `data/processed/cases.index` and `embeddings_cache.pkl`. If those files are OneDrive placeholders, the app does not overwrite them. `rag/retrieve.py` then builds an in-memory TF-IDF index for this process only.

`retrieve_similar_cases` embeds the patient text and returns the nearest cases. The twin path asks for 5.

`rag/rerank.py` adds a small bonus on top of that score, then sorts again:

- +0.08 if both the patient and the case mention chest pain, LDL, diabetes, or BP
- +0.10 if both mention CAD on the diagnosis side
- +0.04 if risk-factor words overlap (hypertension, smoker, obesity, CKD, family history)

The final score is capped at 1. The UI shows it as similarity. It is a retrieval score, not a probability that the diagnosis is correct.

Those case lines are inserted into `prompts/doctor_twin.txt`. The model is told they are references, not a script to copy, and not to invent doses or test results.

### Part 4 — GraphRAG

**Theory.** Case retrieval finds similar write-ups. It does not store "this finding points at that test" as its own object. A knowledge graph does. A node is a thing (a symptom, a risk, a condition, a test, an action). An edge is a labeled relationship (suggests, raises risk, managed by). Graph retrieval walks those edges and turns the walk into sentences for the prompt. That pattern is GraphRAG: retrieve from a graph, then generate.

A full research GraphRAG system may do more than this app: entity extraction from every document, multi-hop paths, and community summaries. Those are the ideas to know. This repository implements the smaller, inspectable version: match the patient text to node names, then take the outgoing edges.

**In this project.** `graph_rag/build_graph.py` reads `graph_nodes.csv` (about 34 nodes) and `graph_edges.csv` (about 116 edges) into one directed NetworkX graph and caches it. It also writes `data/processed/graph_export.json`. There is no Neo4j database. `graph_rag/neo4j_loader.py` is an empty stub on purpose.

`graph_rag/reasoning.py` does the walk:

1. If a node's full name appears inside the patient text, that node matches.
2. A few extra words map to nodes even when the full name is missing: "diabetes", "chest pain", "family history", "ldl", "exertional".
3. For each matched node, every outgoing edge is kept: source, target, relation, and a line like `high LDL -> Angina (increases_risk)`.
4. If nothing matches, the summary says no high-confidence graph trigger was found.

That is one hop, not a long chain of reasoning. Relation names in the file are `suggests`, `increases_risk`, `managed_by`, `preferred_for`, and `linked_to`. Some edges are synthetic demo links. They are what the file contains. They are not a guideline.

The `type` column on nodes cycles through Disease, RiskFactor, Test, Decision, DoctorPreference, and Symptom, and it often does not match the name (an ECG row is not a reliable "test" just because of that column). The graph page therefore colors a node from its name: symptom, risk, condition, test, or action. That coloring is for reading the map. The reasoning function itself uses names and edges, not that display color.

`prompts/graph_reasoning.txt` only tells the model to cite those relation names. The walk is Python, not the model.

On `/graph`, a switch chooses the view. The patient's name shows only the links this intake triggered. **Entire graph** shows all 34 names. Bright lines on the full map are still this patient's. Zoom, drag, pinch, Fit, and full screen move the map. Click a name to read one link as a sentence. The logo in the header opens the home page.

### Part 5 — One twin answer, from form to screen

**Theory.** Grounded generation is a pipeline, not a single prompt. Check the input, build the query text, retrieve, walk the graph, assemble the prompt, stream the words, and return the evidence beside the words so the narrative can be checked.

**In this project.** Startup (`backend/resources.py`, from the FastAPI lifespan in `backend/app.py`) loads the six CSVs, the graph, the case index, and the four prompt files once.

Then a twin consultation does this:

1. `PatientInput` in `backend/models.py` checks the form. A bad field is HTTP 422 and the text `Please check the form. …`.
2. `patient_to_text` makes one block. BMI comes from height and weight.
3. RAG returns 5 cases. Rerank reorders them.
4. The graph walk collects links.
5. `twin_engine/twin_prompt.py` fills `doctor_twin.txt` with style rules, patient text, timeline if a saved `profile_id` was chosen, the cases, the graph lines, uniqueness flags, and clarifying questions. Braces in the patient text are escaped so they are not treated as format fields.
6. Uniqueness flags (`twin_engine/personalization.py`) mark things such as younger chest symptoms, kidney disease, high HbA1c with diabetes, overlapping blood thinners, obesity, atypical symptoms, and high LDL.
7. If symptoms, duration, blood pressure, or medicines are empty, clarifying questions are added.
8. The chat model streams the assessment. The browser receives server-sent events: `meta`, then `token`, then `done`. The system prompt is not sent to the browser.
9. The response also carries fixed plan lists (tests, immediate actions, follow-up), sources, the graph evidence, a disclaimer, and a confidence number.

The generic path stops at step 2, uses `generic_gpt.txt`, and does not retrieve or walk the graph. Its concern list, next steps, and risk notes are fixed safety lists. Only the narrative is generated.

Follow-up chat keeps recent turns. A specialist follow-up still includes style rules and the retrieved case lines. A generic follow-up does not.

### Part 6 — The confidence number and the comparison scores

**Theory.** A language model does not hand you a calibrated probability that its paragraph is clinically correct. If a product shows a percentage, that number has to be defined. Otherwise it looks like certainty.

**In this project.** Confidence is a fixed formula in `backend/utils.py`, capped at 0.98:

`min(0.98, 0.60 + 0.07 × number of retrieved cases + 0.03 × number of graph links)`

More retrieved cases and more graph links raise the number. The number does not mean "98% chance this diagnosis is right." It means "this run had retrieval and graph evidence, up to a cap." The Why page shows the three parts: base 0.60, the retrieval part, and the graph part.

Comparison Insights scores Generic GPT and the Doctor's Twin on the same eight factors: personalization, historical evidence, risk sensitivity, clinician supervision, explainability, actionability, specialist alignment, and accuracy. The page states what each factor means before the chart. Both answers are scored from the written text. The Doctor's Twin also receives credit for uniqueness flags, retrieved cases, and graph links, and only when those were actually returned. Personalization caps the generic side, because repeating the intake form is not the same as a plan changed by a uniqueness flag. Risk sensitivity is often close, because Generic GPT already carries a fixed escalation warning. If the twin cannot say when to seek emergency care, a calm paragraph can reassure the wrong person. Clinician supervision stays high for both: neither answer replaces the doctor who sees the patient. Accuracy means the answer can be checked against a case or a graph link. A grounded Doctor's Twin lands near 88, and Generic GPT near 40, because a similar case is not this patient and one graph step is not a confirmed diagnosis. A factor can still show Generic GPT ahead when the twin text is thin and nothing was retrieved. Generic Context Depth and Twin Context Depth are the averages of those eight scores.

### Part 7 — Future work and scaling

What would have to change if this left a laptop demo. None of this is built yet. The stubs and the comments in the code are the honest starting points.

**Data.** The case file is a fixed CSV of about 500 rows. A real deployment needs consent, de-identification, a clinician who owns each case, and a way to add cases without editing the repo. Profiles and timelines should join the live patient only when that identity is real, not only when a demo id is selected.

**RAG.** Keep a hybrid search: keyword overlap plus embeddings, then a reranker trained on "was this case actually useful?" Measure recall on a held-out set of cases a cardiologist marked as similar. Pin the index on a disk the process can read. Do not depend on a cloud-only file. Swap TF-IDF for the OpenAI index only when the dimensions match. The code already rebuilds if the query vector width does not match the index.

**GraphRAG.** Replace the cycling `type` column with a real ontology, and have a clinician check every edge. Then multi-hop walks and path explanations become meaningful. At this size, NetworkX in memory is enough. `neo4j_loader.py` is the empty place a larger graph database would go. Community summaries, the heavier GraphRAG idea, are not implemented.

**The model.** The chat model can change through `OPENAI_MODEL` without changing retrieval. A larger model does not remove the need for cases and the graph. Evaluation should score faithfulness (did the answer stick to the retrieved lines?) and clinician preference, not only fluency.

**The product.** The Consultation Portal doctor view is a demo of Accept, edit, and Reject. A real version needs accounts, roles, and an audit log. The page already says that. Streaming is already there, which is the right shape for a longer answer.

**Running it bigger.** One FastAPI process is the right shape for this repo. If many users arrive, split retrieval, the graph, and the model call into separate services behind the same API, and keep the website as the built `web/dist` files. Do not add a second UI framework to scale. Add tests around retrieval and the graph walk first. `tests/` already fakes the model so the API shape can be checked without a network call.

**Safety, which does not scale away.** Urgent symptoms stay an instruction to seek care. The twin must keep refusing invented doses. A higher confidence number must never be shown as a diagnosis.

---

## Screens

The visit header is Home and Consultation. **Open the comparison** (`/studio`) is a separate page, with its own header for Generic GPT, the Doctor's Twin, the side-by-side view, the graph, why, and the scores. An unknown URL shows “Page not found”.

| Route | Where it sits | File | What it does |
| --- | --- | --- | --- |
| `/` | Visit | `web/src/pages/Home.tsx` | Who the twin is. **Begin a consultation**. **Open the comparison**. |
| `/studio` | Comparison | `web/src/pages/Studio.tsx` | The separate page for Generic GPT, the twin, the side-by-side view, the graph, why, and the scores. |
| `/consultation` | Visit | `web/src/pages/ConsultationPortal.tsx` | Starts the Doctor's Twin. Follow-up chat. Tests, uniqueness, and clinician review open on request. |
| `/patient` | Visit | `web/src/pages/PatientAnalysis.tsx` | Intake form. **Analyze Patient** saves the patient and opens `/consultation`. |
| `/twin` | Comparison | `web/src/pages/VimleshTwin.tsx` | Streams the specialist assessment. Cases, the plan, and confidence open on request. |
| `/generic` | Comparison | `web/src/pages/GenericBaseline.tsx` | Streams the generic baseline once and stores it. |
| `/compare` | Comparison | `web/src/pages/Comparison.tsx` | Side-by-side answers. Streams the twin first if it is missing. |
| `/evidence` | Comparison | `web/src/pages/Evidence.tsx` | Three links into cases, graph, and why. |
| `/cases` | Comparison | `web/src/pages/HistoricalCases.tsx` | Searchable table of the top similar cases for this patient. |
| `/graph` | Comparison | `web/src/pages/GraphPage.tsx` | Round map of the knowledge graph. A switch shows this patient or the entire graph. Zoom, drag, pinch, Fit, and full screen. Click a name to read its links. **Back to consultation** appears only when the graph was opened from the consultation. |
| `/insights` | Comparison | `web/src/pages/Insights.tsx` | Bar chart of the comparison scores and a short meaning for each. |
| `/why` | Comparison | `web/src/pages/Why.tsx` | Retrieved cases, uniqueness flags, safety notes, confidence breakdown. |
| `/explain` | Comparison | `web/src/pages/Explain.tsx` | Plain-language pipeline from the CSVs to the score, using this run’s counts. |
| `/admin` | Comparison | `web/src/pages/Admin.tsx` | Counts, pie chart, registry, profile table, case catalog. **Load** copies a profile into the session and opens intake. |

Shared UI:

| File | What it is |
| --- | --- |
| `web/src/components/Layout.tsx` | Visit header, or the comparison header on `/studio` and the comparison routes. The logo opens the home page. Theme toggle, mobile drawer, footer. |
| `web/src/components/PatientForm.tsx` | The intake form used by Analysis and the Portal, including risk checkboxes and the demo-patient button. |
| `web/src/components/DataTable.tsx` | Table with search, filter, sort, and pages of 8 rows. |
| `web/src/components/ui.tsx` | Buttons, cards, page headers, notes, skeletons, disclaimer, bullet lists, source list, confidence panel. |  
| `web/src/components/RichText.tsx` | Turns consultation text into headings, bold words, and lists, so `**` and `-` are not shown as raw characters. |  
| `web/src/lib/richText.ts` | The parser behind that component. |
| `web/src/lib/api.ts` | `getJson`, `postJson`, and `streamConsult` (reads SSE `data:` events). |
| `web/src/lib/utils.ts` | Class-name helper, BMI, error text from API failures. |
| `web/src/store/useAppStore.ts` | Zustand store, persisted in the browser under the key `cardiotwin-session`. |
| `web/src/types.ts` | Patient, results, chat types, demo patient, analysis defaults. |
| `web/src/App.tsx` | Route table and page transition. |
| `web/src/main.tsx` | React root, router, toast notifications. |
| `web/src/index.css` | Tailwind layers and a few global styles. |
| `web/src/vite-env.d.ts` | TypeScript shim for Vite. |

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

`GET /` and every other non-API path return the built React app from `web/dist`, if that build exists. If it does not, the server answers 503 with `Frontend is not built yet. Run: python run.py`.

CORS allows the Vite origin (port 5173) and the app origin (port 8000).

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
| `Node.js is required` | Install Node from https://nodejs.org, close the terminal, run `python run.py setup` again. |
| Could not create a Python virtual environment | Install Python 3.11+ with **Add to PATH**, then run `python run.py setup` again. |
| Browser says the frontend is not built (HTTP 503) | Run `python run.py`. It builds the website when `web/dist` is missing. |
| `Please check the form` | A field is outside the ranges in `PatientInput` (age, height, weight, LDL, HbA1c, or an empty name). |
| Port 8000 already in use | Another `python run.py` is still running. Close that terminal, or end the `uvicorn` process, then start again. |
| Page loads but answers are a short local fallback | `OPENAI_API_KEY` is empty or rejected. Edit `.env`, save, and run `python run.py` again. |
| Similar-case scores look like keyword overlap | The FAISS files were not readable (often OneDrive). Pin `cases.index` and `embeddings_cache.pkl` as described above. |
| Setup or tests sit with no CPU and no output | OneDrive placeholders, including old `__pycache__` folders. Delete `__pycache__` folders inside the project (leave `.venv` alone), and pin the two cache files. |
| Changes to React do not show on port 8000 | Port 8000 serves `web/dist`. Run `python run.py dev` and open port 5173, or run `python run.py setup` to rebuild. |

---

## What is deliberately absent

- No Docker, no cloud deploy files, no CI config in this tree.
- No Streamlit UI. The current interface is `web/`.
- No Neo4j database. `graph_rag/neo4j_loader.py` is a stub.
- `.venv`, `web/node_modules`, and `web/dist` are local install products. `python run.py setup` recreates them.
- `.env` is local. Share `.env.example`, not the key.

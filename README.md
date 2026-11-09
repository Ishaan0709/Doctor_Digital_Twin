# CardioTwin AI

A decision-support demo of **Dr. Vimlesh Pandey**, a preventive cardiologist. You enter a visit. The app writes two answers from the same details: one from that visit alone, and one that also searches his past cases and a small knowledge graph.

This is not a diagnosis, a prescription, or an emergency service. Chest pain at rest, fainting, or severe breathlessness needs urgent care.

Live site: https://doctor-digital-twin.vercel.app/

API: https://doctor-digital-twin.onrender.com/health

Locally: http://localhost:8000

## What to show

The site has five pages. Graph is also in the bar.

| Page | What it is |
| --- | --- |
| Home | Who the twin is, and the two buttons. |
| Consultation | One form, then Dr. Pandey’s twin. Suggested questions are clickable. A typed question works too. Doctor’s view can accept, edit, or ask the patient to come in. |
| Records | The six CSV files, with the real rows, counts, and charts. |
| Compare | Writes whichever answer is missing and shows both. You do not run them on separate pages. |
| Graph | This patient's links, and the entire graph, on one page. |

The small line under the name is the model actually answering (`gpt-4o-mini`, or a local Ollama model if that is selected).

## How one answer is built

```text
Browser (web/) → FastAPI (backend/) → RAG (rag/) + graph (graph_rag/) → LLM
                                      ↘ data/raw/*.csv
```

1. The visit is turned into text.
2. RAG embeds that text and searches `doctor_cases_vimlesh_pandey.csv` with FAISS. Top matches are reranked. The generic answer skips this search.
3. GraphRAG loads `graph_nodes.csv` and `graph_edges.csv` into a NetworkX graph and keeps links whose names appear in the visit.
4. The twin prompt adds those cases, those links, and eight style rules, then asks the model to write.

There is no user database and no Neo4j. The store is six CSV files. The graph lives in memory.

The Vimlesh consultation is a local model (`OLLAMA_MODEL`, default `llama3.2`) with retrieval and the graph. That prompt stays on the machine: the case file is not uploaded, and those tokens are not billed. The other column on Compare is ordinary GPT (`gpt-4o-mini`) from the current visit only. It does not search the cases. Live answers use temperature 0.2. The pages do not show accuracy charts. The held-out numbers, when a run exists, stay in `eval/REPORT.md`.

## Folder map

```text
Doctor_Digital_Twin/
├── run.py              start, setup, or hot reload
├── config.py           paths and .env
├── requirements.txt
├── backend/            FastAPI
│   ├── app.py          the server; also serves the built website
│   ├── routes.py       HTTP routes
│   ├── llm.py          OpenAI or Ollama
│   ├── context.py      loads the six CSVs
│   ├── utils.py        builds the generic and twin answers
│   ├── models.py       request shapes
│   └── resources.py    loads tables, graph, index, and prompts at startup
├── rag/                turn cases into vectors and search them
│   ├── ingest_cases.py
│   ├── embed_cases.py  OpenAI embeddings, or TF-IDF if there is no key
│   ├── vector_store.py FAISS index
│   ├── retrieve.py
│   └── rerank.py
├── graph_rag/          the knowledge graph
│   ├── build_graph.py
│   ├── reasoning.py    match the visit to node names
│   └── history.py      attach a case id when a past visit supports a link
├── twin_engine/        doctor profile, uniqueness flags, comparison math
├── prompts/            the text sent to the model
├── data/raw/           the six CSVs
├── data/processed/     FAISS index and graph export
├── eval/               the 30-case test. Not shown in the website.
├── tests/
└── web/                React + Vite + TypeScript
    └── src/pages/      Home, Consultation, Records, Compare, Graph
```

### The six files in `data/raw/`

| File | Rows | Used for |
| --- | --- | --- |
| `doctor_cases_vimlesh_pandey.csv` | 500 | Retrieved cases |
| `patient_profiles.csv` | 120 | Saved profiles on the Records page |
| `patient_timelines.csv` | 720 | Dated blood pressure, HbA1c, and weight |
| `graph_nodes.csv` | 34 | Graph entities |
| `graph_edges.csv` | 116 | Relations between those entities |
| `doctor_style_examples.csv` | 8 | How the twin is asked to sound |

## Run it

Install Git, Python 3.11+, and Node.js 18+. Then:

```powershell
git clone https://github.com/Ishaan0709/Doctor_Digital_Twin.git
cd Doctor_Digital_Twin
python run.py setup
```

Put an OpenAI key in `.env` if you want model answers. The names are in `.env.example`. `.env` is not committed.

```powershell
python run.py
```

That opens http://localhost:8000. `python run.py dev` is the hot-reload site at http://localhost:5173, with the API still on port 8000.

On Render, the API start command is:

```text
python -m uvicorn backend.app:app --host 0.0.0.0 --port $PORT
```

The website on Vercel calls that API when it is not running on localhost.

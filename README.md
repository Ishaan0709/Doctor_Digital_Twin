# CardioTwin AI

Clinical decision-support demo of a digital twin of Dr. Vimlesh Pandey. It compares a general medical answer with specialist reasoning grounded in his historical cases and a cardiology knowledge graph.

This is not a diagnosis and not a substitute for a real doctor.

## Run on Windows

From this folder (`doctor-digital-twin`) or the `Doctor_twin` folder above it:

1. First time: `.\setup.bat`
2. Every time after: `.\start.bat`

`start.bat` opens http://localhost:8000. For hot reload while editing the UI, use `.\dev.bat` (API on port 8000, Vite on port 5173).

## Run on Mac or Linux

```bash
chmod +x setup.sh start.sh dev.sh
./setup.sh
./start.sh
```

## Environment

Copy `.env.example` to `.env` if setup did not do it, then set:

| Variable | Purpose |
| --- | --- |
| `OPENAI_API_KEY` | Live answers and embeddings. Leave empty to run with a local fallback message and TF-IDF search. |
| `OPENAI_MODEL` | Chat model. Default `gpt-4o-mini`. |
| `OPENAI_EMBEDDING_MODEL` | Embedding model. Default `text-embedding-3-small`. |
| `APP_ENV` | `development` or `production`. |

Do not commit `.env`.

## What is where

- `web/` is the React app. Doctor photo and logo live in `web/public`.
- `backend/` is the API. It also serves `web/dist`.
- `MIGRATION_NOTES.md` lists every screen and the accuracy changes.

The old Streamlit UI has been removed. Nothing in `data/` was changed.

import threading

from rag.ingest_cases import ingest_cases
from rag.embed_cases import Embedder
from rag.vector_store import build_faiss_index, load_index, save_index, search_index

_LOCK = threading.Lock()
_STATE: dict = {"embedder": None, "index": None}


def _build_and_save_index(embedder: Embedder) -> None:
    df = ingest_cases()
    vectors = embedder.embed_texts(df["rag_text"].tolist())
    metadata_cols = ["case_id", "symptoms", "risk_factors", "tests", "diagnosis", "decision", "outcome"]
    metadata = df[metadata_cols].to_dict(orient="records")
    save_index(build_faiss_index(vectors, metadata))


def initialize_rag(embedder: Embedder) -> None:
    existing = load_index()
    if existing["index"] is not None and existing["metadata"]:
        return
    _build_and_save_index(embedder)


def warm_index() -> None:
    """Load the FAISS index and embedder once per process."""
    with _LOCK:
        _ensure_locked()


def _memory_index(embedder: Embedder):
    df = ingest_cases(persist=False)
    vectors = embedder.embed_texts(df["rag_text"].tolist())
    metadata_cols = ["case_id", "symptoms", "risk_factors", "tests", "diagnosis", "decision", "outcome"]
    metadata = df[metadata_cols].to_dict(orient="records")
    return build_faiss_index(vectors, metadata)


def _ensure_locked() -> None:
    embedder = _STATE["embedder"]
    if embedder is None:
        embedder = Embedder()
        _STATE["embedder"] = embedder
    if _STATE["index"] is not None:
        return

    loaded = load_index()
    if loaded.get("unreadable"):
        # Do not overwrite data/processed. A local TF-IDF index is enough to search.
        local = Embedder(force_local=True)
        _STATE["embedder"] = local
        _STATE["index"] = _memory_index(local)
        return

    try:
        initialize_rag(embedder)
        if not embedder.use_openai:
            df = ingest_cases()
            embedder.embed_texts(df["rag_text"].tolist())
        loaded = load_index()
        if loaded.get("index") is None:
            raise RuntimeError("search index was not stored")
        _STATE["index"] = loaded
    except Exception:
        local = Embedder(force_local=True)
        _STATE["embedder"] = local
        _STATE["index"] = _memory_index(local)


def _without_excluded(hits, exclude_ids, top_k: int):
    if not exclude_ids:
        return hits[:top_k]
    blocked = {str(item) for item in exclude_ids}
    kept = [hit for hit in hits if str(hit.get("case_id", "")) not in blocked]
    return kept[:top_k]


def retrieve_similar_cases(patient_context: str, top_k: int = 5, exclude_ids=None):
    with _LOCK:
        _ensure_locked()
        embedder = _STATE["embedder"]
        index_obj = _STATE["index"]

    qvec = embedder.embed_query(patient_context)

    # Handle embedding-model switches (e.g., TF-IDF index to OpenAI embeddings) gracefully.
    if index_obj["index"] is not None and qvec.shape[1] != index_obj["index"].d:
        with _LOCK:
            _build_and_save_index(embedder)
            _STATE["index"] = load_index()
            index_obj = _STATE["index"]
        qvec = embedder.embed_query(patient_context)

    # A normal consultation asks for top_k only. A held-out run asks for a wider
    # pool so the excluded cases can be dropped and the next cases still fill top_k.
    pool = top_k if not exclude_ids else top_k + len({str(item) for item in exclude_ids}) + 5
    return _without_excluded(search_index(index_obj, qvec, top_k=pool), exclude_ids, top_k)

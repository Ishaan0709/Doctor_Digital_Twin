from rag.ingest_cases import ingest_cases
from rag.embed_cases import Embedder
from rag.vector_store import build_faiss_index, load_index, save_index, search_index


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


def retrieve_similar_cases(patient_context: str, top_k: int = 5):
    embedder = Embedder()
    initialize_rag(embedder)
    index_obj = load_index()

    if not embedder.use_openai:
        df = ingest_cases()
        _ = embedder.embed_texts(df["rag_text"].tolist())

    qvec = embedder.embed_query(patient_context)

    # Handle embedding-model switches (e.g., TF-IDF index to OpenAI embeddings) gracefully.
    if index_obj["index"] is not None and qvec.shape[1] != index_obj["index"].d:
        _build_and_save_index(embedder)
        index_obj = load_index()
        qvec = embedder.embed_query(patient_context)

    return search_index(index_obj, qvec, top_k=top_k)

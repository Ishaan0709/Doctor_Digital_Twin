import pickle
from typing import Dict, List
import faiss
import numpy as np
from config import DATA_PROCESSED_DIR


def build_faiss_index(vectors: np.ndarray, metadata: List[Dict]) -> Dict:
    if vectors.shape[0] == 0:
        return {"index": None, "metadata": []}
    index = faiss.IndexFlatIP(vectors.shape[1])
    normalized = vectors.copy()
    faiss.normalize_L2(normalized)
    index.add(normalized)
    return {"index": index, "metadata": metadata}


def save_index(index_obj: Dict) -> None:
    if index_obj["index"] is not None:
        faiss.write_index(index_obj["index"], str(DATA_PROCESSED_DIR / "cases.index"))
    with open(DATA_PROCESSED_DIR / "embeddings_cache.pkl", "wb") as f:
        pickle.dump(index_obj["metadata"], f)


def load_index() -> Dict:
    ip = DATA_PROCESSED_DIR / "cases.index"
    mp = DATA_PROCESSED_DIR / "embeddings_cache.pkl"
    if not ip.exists() or not mp.exists():
        return {"index": None, "metadata": []}
    with open(mp, "rb") as f:
        meta = pickle.load(f)
    return {"index": faiss.read_index(str(ip)), "metadata": meta}


def search_index(index_obj: Dict, query_vector: np.ndarray, top_k: int = 5) -> List[Dict]:
    if index_obj["index"] is None:
        return []
    q = query_vector.copy().astype(np.float32)
    faiss.normalize_L2(q)
    scores, idx = index_obj["index"].search(q, top_k)
    out = []
    for score, i in zip(scores[0], idx[0]):
        if i >= 0 and i < len(index_obj["metadata"]):
            item = dict(index_obj["metadata"][i])
            item["match_score"] = float(score)
            out.append(item)
    return out

from typing import List
import numpy as np
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from config import OPENAI_API_KEY, OPENAI_EMBEDDING_MODEL


class Embedder:
    def __init__(self) -> None:
        self.use_openai = bool(OPENAI_API_KEY)
        self.vectorizer = TfidfVectorizer(max_features=512)
        self.client = OpenAI(api_key=OPENAI_API_KEY) if self.use_openai else None

    def embed_texts(self, texts: List[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 512), dtype=np.float32)
        if self.use_openai and self.client is not None:
            response = self.client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=texts)
            return np.array([d.embedding for d in response.data], dtype=np.float32)
        return self.vectorizer.fit_transform(texts).toarray().astype(np.float32)

    def embed_query(self, query: str) -> np.ndarray:
        if self.use_openai and self.client is not None:
            response = self.client.embeddings.create(model=OPENAI_EMBEDDING_MODEL, input=[query])
            return np.array(response.data[0].embedding, dtype=np.float32).reshape(1, -1)
        return self.vectorizer.transform([query]).toarray().astype(np.float32)

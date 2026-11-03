"""
Embeddings that live in ANOTHER container.

Instead of loading the model inside this app (HuggingFaceEmbeddings), we call the
embedding-service over HTTP. Same model, same vectors, different place.
"""
import os

import httpx
from langchain_core.embeddings import Embeddings

EMBEDDING_URL = os.getenv("EMBEDDING_URL", "http://localhost:8001")


class RemoteEmbeddings(Embeddings):
    def __init__(self, url: str = EMBEDDING_URL, batch_size: int = 64):
        self.url = url.rstrip("/")
        self.batch_size = batch_size

    def _embed(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for i in range(0, len(texts), self.batch_size):
            resp = httpx.post(
                f"{self.url}/embed",
                json={"texts": texts[i : i + self.batch_size]},
                timeout=60,
            )
            resp.raise_for_status()
            vectors.extend(resp.json()["embeddings"])
        return vectors

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self._embed(texts)

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text])[0]

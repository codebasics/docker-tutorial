import os

from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer

MODEL_NAME = os.getenv("EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
DEVICE = os.getenv("DEVICE", "cpu")  # "cpu" or "cuda"

app = FastAPI(title="embedding-service")

# Loaded ONCE at startup, then reused for every request.
model = SentenceTransformer(MODEL_NAME, device=DEVICE)


class EmbedRequest(BaseModel):
    texts: list[str]


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_NAME, "device": str(model.device)}


@app.post("/embed")
def embed(req: EmbedRequest):
    vectors = model.encode(req.texts, convert_to_numpy=True)
    return {"embeddings": vectors.tolist(), "dim": vectors.shape[1]}

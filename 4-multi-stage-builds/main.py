import os
from pathlib import Path

from fastapi import FastAPI

app = FastAPI(title="hi-api")

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
COUNT_FILE = DATA_DIR / "count.txt"

def read_count() -> int:
    if COUNT_FILE.exists():
        return int(COUNT_FILE.read_text())
    return 0


@app.get("/")
def root():
    # Root Endpoint
    return {"message": "Hello from inside a container!"}


@app.get("/health")
def health():
    # Health Endpoint
    return {"status": "ok"}


@app.get("/count")
def count():
    """Increment the counter, save it to a file, return it."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    new_count = read_count() + 1
    COUNT_FILE.write_text(str(new_count))
    return {"count": new_count, "stored_in": str(COUNT_FILE)}


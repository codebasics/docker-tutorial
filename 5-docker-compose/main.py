import os

import redis
from fastapi import FastAPI, HTTPException

app = FastAPI(title="hit-api")


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True, socket_connect_timeout=2)


@app.get("/")
def root():
    return {"message": "Hello from inside a container!"}


@app.get("/count")
def count():
    """Increment the counter in Redis and return it."""
    try:
        new_count = r.incr("hits")
    except redis.exceptions.ConnectionError:
        raise HTTPException(503, f"Cannot reach Redis at {REDIS_HOST}:{REDIS_PORT}")
    return {"count": new_count, "stored_in": f"redis://{REDIS_HOST}:{REDIS_PORT}"}


@app.get("/health")
def health():
    return {"status": "ok"}

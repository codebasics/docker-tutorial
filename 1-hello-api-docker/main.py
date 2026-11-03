from fastapi import FastAPI

app = FastAPI(title="hi-api")


@app.get("/")
def root():
    return {"message": "Hello from inside a container!"}


@app.get("/health")
def health():
    # Health Endpoint
    return {"status": "ok"}

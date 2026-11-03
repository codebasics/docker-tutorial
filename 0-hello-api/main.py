from fastapi import FastAPI

app = FastAPI(title="hit-api")


@app.get("/")
def root():
    return {"message": "Hello from inside a container!"}


@app.get("/health")
def health():
    return {"status": "ok"}

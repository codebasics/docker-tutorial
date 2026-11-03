# Docker Tutorial 🐳

A hands-on, step-by-step Docker tutorial that starts with a 10-line FastAPI "hello world" and ends with a full **multi-container RAG chatbot** for a telecom customer-care use case. Each numbered folder introduces one Docker concept and builds on the previous one. Built with **FastAPI**, **Redis**, **Streamlit**, **LangChain + Groq**, **ChromaDB**, and **Sentence Transformers**.

---

## Tutorial Roadmap

| Folder | Concept | What you learn |
|---|---|---|
| `0-hello-api` | Baseline | A FastAPI app running locally, no Docker yet |
| `1-hello-api-docker` | Dockerfile basics | `FROM`, `WORKDIR`, `COPY`, `RUN`, `CMD`; build and run your first image |
| `2-layer-caching` | Layer caching | Copy `requirements.txt` before the code so rebuilds stay fast |
| `3-volumes` | Volumes | Persist a counter file outside the container with `-v` |
| `4-multi-stage-builds` | Multi-stage builds | Run tests in a builder stage and ship a lean runtime image |
| `5-docker-compose` | Docker Compose | FastAPI + Redis wired together with networks, volumes and `depends_on` |
| `6-telecom-rag` | Capstone project | Streamlit app + embedding service + ChromaDB, with an optional GPU profile |

---

## Getting Started

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (includes Docker Compose v2)
- [Groq](https://console.groq.com/keys) API Key (only for `6-telecom-rag`)
- Python `>= 3.12` and [uv](https://docs.astral.sh/uv/) (only if you want to run `0-hello-api` locally)
- NVIDIA GPU + [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/) (optional, GPU embeddings only)

### Steps 0 to 4: Single-container examples

```bash
# 0. Run locally, without Docker
cd 0-hello-api
pip install -r requirements.txt
uvicorn main:app --reload

# 1-3. Build and run an image
cd ../1-hello-api-docker
docker build -t hello-api .
docker run -p 8000:8000 hello-api

# 3. Persist data with a volume
cd ../3-volumes
docker build -t counter-api .
docker run -p 8000:8000 -v counter-data:/data counter-api

# 4. Multi-stage build (tests run during the build)
cd ../4-multi-stage-builds
docker build -t hello-api:multi-stage .
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) to try the API.

### Step 5: FastAPI + Redis with Compose

```bash
cd 5-docker-compose
docker compose up --build

# Hit the counter a few times, then restart: the count survives
curl http://localhost:8000/count
docker compose down && docker compose up
```

Change the host port with `API_PORT=9000 docker compose up`.

### Step 6: Telecom RAG chatbot

```bash
cd 6-telecom-rag

# Configure environment
cp rag-app/.env.example rag-app/.env
# Edit rag-app/.env and add your GROQ_API_KEY

# Build and start all three services
docker compose up --build

# In a second terminal: load the data into ChromaDB (run once)
docker compose run --rm rag-app python -m src.ingest.faq
docker compose run --rm rag-app python -m src.ingest.tickets
docker compose run --rm rag-app python -m src.ingest.pdf
```

Open [http://localhost:8501](http://localhost:8501) and start chatting.

**With an NVIDIA GPU** (faster embeddings):

```bash
docker compose -f compose.yaml -f compose.gpu.yaml up --build
```

---

## Architecture (`6-telecom-rag`)

```
 Browser ──▶ rag-app (Streamlit :8501)
                │  ├──▶ embeddings (FastAPI :8001)   all-MiniLM-L6-v2
                │  ├──▶ chroma     (:8000)           faq · tickets · guides
                │  └──▶ Groq API                     LLM answer
                ▼
          streamed response
```

| Service | Image | Role |
|---|---|---|
| `rag-app` | built from `rag-app/` | Streamlit UI, retriever and LangChain RAG chain |
| `embeddings` | built from `embedding-service/` | Serves `/embed` and `/health` so the model loads once |
| `chroma` | `chromadb/chroma` | Vector store, data kept in the `chroma-data` volume |

The retriever merges three Chroma collections: `faq` (CSV), `tickets` (SQLite) and `guides` (PDF chunks).

---

## Docker Concepts Covered

- Writing a minimal, readable `Dockerfile`
- Ordering instructions for layer caching
- `.dockerignore` to keep images small
- Named volumes and bind-mount persistence
- Multi-stage builds with tests as a build gate
- BuildKit cache mounts with `uv sync --frozen`
- Compose services, service-name networking, `depends_on`, `env_file`, `mem_limit`
- Compose override files (`compose.gpu.yaml`) and GPU device reservations

---

## Example Prompts

| Try asking… | What happens |
|---|---|
| *"Why is my mobile internet so slow?"* | Retrieves FAQ + ticket matches and gives troubleshooting steps |
| *"How do I activate international roaming?"* | Pulls the how-to from the telecom guide PDF |
| *"I was charged for roaming but had a bundle active"* | Finds similar resolved support tickets |

---

## Useful Commands

```bash
docker compose ps               # Running services
docker compose logs -f rag-app  # Follow logs for one service
docker compose down             # Stop services, keep volumes
docker compose down -v          # Stop services and delete volumes
docker image ls                 # Compare image sizes across steps
```

---
Copyright©️ Codebasics Inc. All rights reserved.

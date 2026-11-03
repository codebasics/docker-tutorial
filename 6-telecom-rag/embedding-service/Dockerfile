FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:0.6.14 /uv /usr/local/bin/uv

WORKDIR /app

ENV HF_HOME=/models \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

RUN uv pip install --system huggingface_hub && \
    python -c "from huggingface_hub import snapshot_download; \
snapshot_download('sentence-transformers/all-MiniLM-L6-v2', \
ignore_patterns=['*.onnx', '*.h5', '*.ot', '*.msgpack', 'onnx/*', 'openvino/*'])"

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-project

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

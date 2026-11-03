### Stage BUILDER
FROM python:3.12-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY . .

RUN PYTHONPATH=/install/lib/python3.12/site-packages pytest test_main.py -v

### Stage RUNTIME
FROM python:3.12-slim AS runtime

WORKDIR /app

COPY --from=builder /install /usr/local

COPY main.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
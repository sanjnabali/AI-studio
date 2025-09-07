# mlflow/Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /mlflow

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip setuptools wheel \
    && pip install mlflow[extras]==2.8.1 psycopg2-binary boto3

EXPOSE 5000

CMD ["mlflow", "server", \
     "--backend-store-uri", "sqlite:///mlflow.db", \
     "--default-artifact-root", "./mlflow-artifacts", \
     "--host", "0.0.0.0", \
     "--port", "5000"]

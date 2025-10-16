# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Commands

- Backend setup
  - Python venv (recommended)
    ```bash path=null start=null
    python -m venv .venv && .venv/Scripts/Activate.ps1
    pip install -r Backend/requirements.txt
    ```
  - Run API (FastAPI + Uvicorn)
    ```bash path=null start=null
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir Backend
    ```
  - Prod server (example)
    ```bash path=null start=null
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir Backend --workers 2
    ```

- Frontend setup
  - Install deps
    ```bash path=null start=null
    cd Frontend
    npm install
    ```
  - Dev server (Vite with proxy to backend)
    ```bash path=null start=null
    npm run dev
    ```
  - Build
    ```bash path=null start=null
    npm run build && npm run preview
    ```
  - Lint (if ESLint is configured)
    ```bash path=null start=null
    npm run lint
    ```

- Docker (per service)
  - Backend
    ```bash path=null start=null
    docker build -t ai-studio-backend ./Backend
    docker run -p 8000:8000 ai-studio-backend
    ```
  - Frontend
    ```bash path=null start=null
    docker build -t ai-studio-frontend ./Frontend
    docker run -p 5173:5173 ai-studio-frontend
    ```

- Tests
  - No test suite is present in this repo. If added later, prefer: pytest for Backend, vitest/jest/playwright for Frontend.

## High-level architecture

- Backend (FastAPI, Python)
  - Entry point: `Backend/app/main.py`
    - App lifespan preloads services: initializes RAG engine and preloads default LLMs for faster first response.
    - CORS (from `Backend/config/settings.py`).
    - Routers mounted under `/api/*`:
      - Auth: `app/api/endpoints/auth.py` (JWT via `app/core/security.py`, SQLAlchemy models in `app/models/user.py`).
      - Chat (text): `app/api/endpoints/chat_text.py` → calls `app/services/llm.py`.
      - RAG: `app/api/endpoints/chat_rag.py` → uses global `rag_engine` from `app/services/rag_engine.py` for document ingest/search + LLM fusion.
      - Code exec: `app/api/endpoints/code_execution.py` (isolated execution; Docker if available, subprocess fallback).
      - Voice/Image: `voice_to_text.py`, `image_gen.py` (models loaded lazily with CPU/GPU awareness).
  - Services
    - LLMService (`app/services/llm.py`)
      - Async model registry with lazy load and `initialize()` to warm models.
      - Chat, code-gen, summarization via HF Transformers pipelines.
      - Compatibility method `chat(messages, ...) -> (text, latency_ms)` for agents.
    - RAGEngine (`app/services/rag_engine.py`)
      - Ingestion: PDF/DOCX/TXT parsing → embeddings via `sentence-transformers` → persisted `chromadb` collections.
      - Query: `search_documents`, `generate_rag_response`, plus helpers `get_context_for_query`, `query`.
    - Agents (`app/services/agents.py`)
      - Orchestrator coordinates Code/Text/RAG agents; workers process tasks concurrently.
      - Agents call `LLMService.chat(...)` and RAG helpers; designed for extensible capabilities per agent.
  - Data layer
    - SQLAlchemy models: users, chat sessions/messages, documents, code executions (`app/models/user.py`).
    - SQLite by default (`DATABASE_URL` in `Backend/config/settings.py`).
  - Config
    - `Backend/config/settings.py` holds app/env settings (JWT, DB, model names, CORS, RAG paths). Uses `.env` if present.

- Frontend (Vue 3 + TypeScript + Vite)
  - Entry: `Frontend/src/main.ts`, router in `src/router`, state via Pinia in `src/store`.
  - API client: `Frontend/src/api/client.ts` wraps backend endpoints with auth token management and `/api` proxy (see `vite.config.ts`).
  - Components under `src/components` implement chat, code canvas, document tools, voice, and modals.
  - Dev proxy: Vite proxies `/api` and `/health` to backend on port 8000.

## Notes for Warp

- First run: start backend then frontend; Vite will proxy API calls to FastAPI.
- Models are heavy; initial load can take time. The app preloads core models at startup to reduce first-token latency.
- RAG storage persists under `./rag_storage/chroma_db` (configurable). Uploaded docs go to `./uploads/<user_id>/`.
- JWT secret must be 32+ chars; default dev value is set but should be overridden in production via `.env`.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A secure, lightweight FastAPI proxy that wraps a locally-running vLLM/SGLang inference server. It exposes a single `POST /chat` endpoint authenticated via an `X-API-KEY` header, forwarding requests asynchronously to the backend using `httpx`.

## Tech Stack

- **FastAPI** + **Uvicorn** — web framework and ASGI server
- **Pydantic** — request/response data validation
- **httpx** — async HTTP client for proxying to vLLM/SGLang
- **python-dotenv** — `.env` config loading
- **SGLang / vLLM** — local LLM inference backend (not managed by this app)

## Expected Project Structure

```
local-llm-api-app/
├── main.py          # FastAPI app, /chat endpoint, security dependency
├── models.py        # Pydantic request/response models
├── .env             # VLLM_BASE_URL, X-API-KEY (never committed)
└── requirements.txt # fastapi, uvicorn, httpx, sglang, python-dotenv
```

## Configuration

Copy `.env.example` (or create `.env`) with:

```
VLLM_BASE_URL=http://localhost:30000
X-API-KEY=your-secret-key
```

## Common Commands

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the development server
uvicorn main:app --reload --port 8000

# Test the /chat endpoint (replace key as needed)
curl -X POST http://localhost:8000/chat \
  -H "X-API-KEY: your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello!", "model": "default"}'

# Interactive API docs
open http://localhost:8000/docs
```

## Architecture

All requests flow through a single FastAPI `Security` dependency before reaching the endpoint:

```
Client → POST /chat (main.py)
           └─ Security dep: validates X-API-KEY header → 401 if invalid
           └─ httpx.AsyncClient → VLLM_BASE_URL (SGLang/vLLM backend)
                 └─ 500 if backend unreachable
```

- **`models.py`** defines `ChatRequest` (`prompt`, `model`) and `ChatResponse` (`response`, `status`) — keep all Pydantic schemas here.
- **`main.py`** wires the FastAPI app, the security dependency (reads `X-API-KEY` from env), and the proxy endpoint (reads `VLLM_BASE_URL` from env).

## Development Phases & Branches

| Phase | Description | Branch |
|-------|-------------|--------|
| Phase 1 | Environment & Foundation | `phase-1/environment-foundation` |
| Phase 2 | Data Modeling (Pydantic models) | `phase-2/data-models` |
| Phase 3 | Core Proxy Logic & `/chat` endpoint | `phase-3/core-proxy` |
| Phase 4 | Security Layer & Error Handling | `phase-4/security-layer` |
| Phase 5 | Verification & Testing | `phase-5/verification` |

Each phase maps directly to the tasks in `Local vLLM Server Setup MVP.md`.

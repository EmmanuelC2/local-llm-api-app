# Local LLM API

A secure, lightweight FastAPI proxy that wraps a locally-running vLLM/SGLang inference server. Exposes a single `POST /chat` endpoint authenticated via an `X-API-KEY` header, forwarding requests asynchronously to the backend.

## Tech Stack

| | |
|---|---|
| **FastAPI** | Web framework |
| **Uvicorn** | ASGI server |
| **Pydantic** | Request / response validation |
| **httpx** | Async HTTP client for proxying |
| **python-dotenv** | `.env` config loading |
| **SGLang / vLLM** | Local LLM inference backend |

## Common Commands

**Setup**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
cp .env.example .env         # fill in VLLM_BASE_URL and X_API_KEY
```

**Run**
```bash
uvicorn main:app --reload --port 8000
```

**Test**
```bash
# Run the test suite
pytest test_app.py -v

# Manual curl test (Command Prompt)
curl -X POST http://localhost:8000/chat -H "X-API-KEY: your-secret-key" -H "Content-Type: application/json" -d "{\"prompt\": \"Hello!\", \"model\": \"llama3\"}"

# Manual curl test (PowerShell)
curl.exe -X POST http://localhost:8000/chat -H "X-API-KEY: your-secret-key" -H "Content-Type: application/json" -d '{\"prompt\": \"Hello!\", \"model\": \"llama3\"}'
```

Interactive API docs available at `http://localhost:8000/docs` once the server is running.

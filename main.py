import os
import httpx
from fastapi import FastAPI, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse

load_dotenv()

app = FastAPI(title="Local LLM API")

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:30000")
API_KEY = os.getenv("X_API_KEY")

# auto_error=False lets us return a custom 401 instead of FastAPI's default 403
api_key_header = APIKeyHeader(name="X-API-KEY", auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)):
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


@app.post("/chat", response_model=ChatResponse, dependencies=[Security(verify_api_key)])
async def chat(request: ChatRequest):
    # Strip unset optional fields so the backend uses its own defaults
    payload = request.model_dump(exclude_none=True)

    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{VLLM_BASE_URL}/chat", json=payload, timeout=60.0)
            res.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except httpx.RequestError:
        raise HTTPException(status_code=500, detail="vLLM/SGLang backend is unreachable")

    data = res.json()
    return ChatResponse(
        response=data.get("response", ""),
        status="ok",
        model=data.get("model"),
        tokens_used=data.get("tokens_used"),
    )

import os
import httpx
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from models import ChatRequest, ChatResponse

load_dotenv()

app = FastAPI(title="Local LLM API")

VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:30000")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
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

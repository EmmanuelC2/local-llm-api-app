import os
import pytest
import respx
import httpx
from fastapi.testclient import TestClient

os.environ.setdefault("X_API_KEY", "test-secret")
os.environ.setdefault("VLLM_BASE_URL", "http://localhost:30000")

from main import app

VALID_HEADERS = {"X-API-KEY": "test-secret"}
BACKEND_URL = "http://localhost:30000/chat"


@pytest.fixture
def client():
    return TestClient(app, raise_server_exceptions=False)


# --- Auth tests ---

def test_missing_api_key_returns_401(client):
    r = client.post("/chat", json={"prompt": "hi", "model": "llama3"})
    assert r.status_code == 401


def test_wrong_api_key_returns_401(client):
    r = client.post("/chat", json={"prompt": "hi", "model": "llama3"}, headers={"X-API-KEY": "wrong"})
    assert r.status_code == 401


# --- Proxy tests (backend mocked with respx) ---

@respx.mock
def test_successful_chat_request(client):
    respx.post(BACKEND_URL).mock(return_value=httpx.Response(
        200, json={"response": "Hello there!", "model": "llama3", "tokens_used": 12}
    ))

    r = client.post("/chat", json={"prompt": "Hi", "model": "llama3"}, headers=VALID_HEADERS)

    assert r.status_code == 200
    body = r.json()
    assert body["response"] == "Hello there!"
    assert body["status"] == "ok"
    assert body["model"] == "llama3"
    assert body["tokens_used"] == 12


@respx.mock
def test_backend_unreachable_returns_500(client):
    respx.post(BACKEND_URL).mock(side_effect=httpx.ConnectError("refused"))

    r = client.post("/chat", json={"prompt": "Hi", "model": "llama3"}, headers=VALID_HEADERS)

    assert r.status_code == 500
    assert "unreachable" in r.json()["detail"]


@respx.mock
def test_optional_fields_forwarded(client):
    respx.post(BACKEND_URL).mock(return_value=httpx.Response(
        200, json={"response": "ok", "model": "llama3"}
    ))

    r = client.post(
        "/chat",
        json={"prompt": "Hi", "model": "llama3", "temperature": 0.5, "max_tokens": 256, "top_p": 0.9},
        headers=VALID_HEADERS,
    )

    assert r.status_code == 200
    sent = respx.calls.last.request
    import json
    payload = json.loads(sent.content)
    assert payload["temperature"] == 0.5
    assert payload["max_tokens"] == 256
    assert payload["top_p"] == 0.9


# --- Model validation tests ---

def test_empty_prompt_returns_422(client):
    r = client.post("/chat", json={"prompt": "", "model": "llama3"}, headers=VALID_HEADERS)
    assert r.status_code == 422


def test_temperature_out_of_range_returns_422(client):
    r = client.post("/chat", json={"prompt": "hi", "model": "llama3", "temperature": 5.0}, headers=VALID_HEADERS)
    assert r.status_code == 422

from pydantic import BaseModel


class ChatRequest(BaseModel):
    prompt: str
    model: str


class ChatResponse(BaseModel):
    response: str
    status: str

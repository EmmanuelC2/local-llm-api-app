from typing import Optional
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    model: str = Field(..., min_length=1)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, gt=0)
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class ChatResponse(BaseModel):
    response: str
    status: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None

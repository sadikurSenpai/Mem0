from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    message: str

class ChatResponse(BaseModel):
    response: str

class ChatMessageDB(BaseModel):
    user_id: str
    session_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from enum import Enum

class AgentType(str, Enum):
    FRIENDLY = "friendly_llm"
    TEACHER = "teacher_llm"
    JOKER = "joker_llm"

class AgentMemoryRequest(BaseModel):
    agent_id: AgentType
    rule: str

class ChatRequest(BaseModel):
    user_id: str
    session_id: str
    agent_id: AgentType
    message: str

class ChatResponse(BaseModel):
    response: str

class ChatMessageDB(BaseModel):
    user_id: str
    session_id: str
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

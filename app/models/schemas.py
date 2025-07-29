import uuid
from datetime import datetime

from pydantic import BaseModel


class SessionCreate(BaseModel):
    pass

class SessionResponse(BaseModel):
    id: uuid.UUID
    created_at: datetime

class ChatRequest(BaseModel):
    session_id: uuid.UUID
    query: str

class ChatResponse(BaseModel):
    response: str
    intent: str
    session_id: uuid.UUID

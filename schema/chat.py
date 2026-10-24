from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    message: str
    conversation_id:Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id:Optional[int] = None
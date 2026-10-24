from fastapi import APIRouter , Depends
from services.chat_service import ChatMessage
from schema.chat import ChatResponse , ChatRequest
from database.dependency import get_db
from sqlalchemy.orm import Session


router = APIRouter()

@router.post("/message",response_model=ChatResponse)
def sendMessage(data:ChatRequest , db:Session =Depends(get_db) ):
    return ChatMessage(data , db)
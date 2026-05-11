from fastapi import APIRouter, HTTPException
from schema.chatgpt import ChatRequest, ChatResponse
from service.chatgpt_service import process_chat

chatgpt_router = APIRouter(prefix="/chatgpt", tags=["ChatGPT Replica"])

@chatgpt_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        reply = await process_chat(request)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

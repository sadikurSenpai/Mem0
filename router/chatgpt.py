from fastapi import APIRouter, HTTPException, BackgroundTasks
from schema.chatgpt import ChatRequest, ChatResponse, AgentMemoryRequest
from service.chatgpt_service import process_chat, add_agent_memory

chatgpt_router = APIRouter(prefix="/chatgpt", tags=["ChatGPT Replica"])

@chatgpt_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    try:
        reply = await process_chat(request, background_tasks)
        return ChatResponse(response=reply)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@chatgpt_router.post("/agent/memory")
async def add_agent_rule(request: AgentMemoryRequest):
    try:
        await add_agent_memory(request.agent_id.value, request.rule)
        return {"status": "success", "message": f"Rule added to agent {request.agent_id.value}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

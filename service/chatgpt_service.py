import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from db.mongodb import get_db
from schema.chatgpt import ChatRequest, ChatMessageDB

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

async def process_chat(request: ChatRequest) -> str:
    db = get_db()
    conversations = db.conversations
    
    # Save user message
    user_msg_db = ChatMessageDB(
        user_id=request.user_id,
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    # Convert to dict and insert
    await conversations.insert_one(user_msg_db.model_dump())
    
    # Fetch recent history
    history_cursor = conversations.find({
        "user_id": request.user_id,
        "session_id": request.session_id
    }).sort("timestamp", 1).limit(20)
    
    messages = [SystemMessage(content="You are a helpful assistant.")]
    
    async for msg in history_cursor:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
            
    # If the last message is somehow not the current user message, we ensure the current user message is there.
    # However, since we just inserted it, it should be the last one in the history_cursor.
    
    # Call LLM
    response = await llm.ainvoke(messages)
    reply_content = response.content
    
    # Save assistant message
    assistant_msg_db = ChatMessageDB(
        user_id=request.user_id,
        session_id=request.session_id,
        role="assistant",
        content=reply_content
    )
    await conversations.insert_one(assistant_msg_db.model_dump())
    
    return reply_content

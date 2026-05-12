import asyncio
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from db.mongodb import get_db
from schema.chatgpt import ChatRequest, ChatMessageDB
from service.mem0_client import client
from fastapi import BackgroundTasks

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def extract_mem0_context(request: ChatRequest) -> tuple[str, str, str]:
    agent_memories = client.get_all(filters={"agent_id": request.agent_id.value})
    agent_list = agent_memories.get("results", [])
    agent_rules = "\n".join([m["memory"] for m in agent_list]) if agent_list else "None"

    session_memories = client.get_all(filters={"run_id": request.session_id})
    session_list = session_memories.get("results", [])
    session_highlights = "\n".join([m["memory"] for m in session_list]) if session_list else "None"

    user_search_results = client.search(request.message, filters={"user_id": request.user_id})
    user_search_list = user_search_results.get("results", [])
    user_preferences = "\n".join([m["memory"] for m in user_search_list]) if user_search_list else "None"

    return agent_rules, session_highlights, user_preferences

def bg_add_to_mem0(user_msg: str, assistant_msg: str, user_id: str, session_id: str):
    messages = [
        {"role": "user", "content": user_msg},
        {"role": "assistant", "content": assistant_msg}
    ]
    client.add(messages, user_id=user_id, run_id=session_id)

async def add_agent_memory(agent_id: str, rule: str):
    await asyncio.to_thread(client.add, rule, agent_id=agent_id, infer=False)

async def process_chat(request: ChatRequest, background_tasks: BackgroundTasks) -> str:
    db = get_db()
    conversations = db.conversations
    
    # Save user message
    user_msg_db = ChatMessageDB(
        user_id=request.user_id,
        session_id=request.session_id,
        role="user",
        content=request.message
    )
    await conversations.insert_one(user_msg_db.model_dump())
    
    # Run mem0 extraction in thread to avoid blocking asyncio event loop
    agent_rules, session_highlights, user_preferences = await asyncio.to_thread(extract_mem0_context, request)
    
    # Build System Prompt
    base_prompt = "You are a helpful assistant."
    if request.agent_id.value == "friendly_llm":
        base_prompt = "You are extremely polite, supportive, and use warm language."
    elif request.agent_id.value == "teacher_llm":
        base_prompt = "You are a strict but knowledgeable teacher. You explain concepts step-by-step and ask questions to test understanding."
    elif request.agent_id.value == "joker_llm":
        base_prompt = "You are a comedian. You must include a pun or a joke in every single response."
        
    system_content = f"""{base_prompt}

[AGENT_RULES]
{agent_rules}

[USER_CONTEXT]
{user_preferences}

[SESSION_CONTEXT]
{session_highlights}
"""
    
    # Fetch recent history (last 10 messages)
    history_cursor = conversations.find({
        "user_id": request.user_id,
        "session_id": request.session_id
    }).sort("timestamp", -1).limit(10)
    
    raw_history = await history_cursor.to_list(length=10)
    raw_history.reverse()  # Reverse to chronological order
    
    messages = [SystemMessage(content=system_content)]
    
    for msg in raw_history:
        if msg["role"] == "user":
            messages.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            messages.append(AIMessage(content=msg["content"]))
            
    # Call LLM
    response = await llm.ainvoke(messages)
    reply_content = response.content
    
    # Save assistant message to DB
    assistant_msg_db = ChatMessageDB(
        user_id=request.user_id,
        session_id=request.session_id,
        role="assistant",
        content=reply_content
    )
    await conversations.insert_one(assistant_msg_db.model_dump())
    
    # Add background task for mem0
    background_tasks.add_task(
        bg_add_to_mem0,
        user_msg=request.message,
        assistant_msg=reply_content,
        user_id=request.user_id,
        session_id=request.session_id
    )
    
    return reply_content

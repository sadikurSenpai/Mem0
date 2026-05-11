from fastapi import APIRouter
from dotenv import load_dotenv
load_dotenv()
from service.mem0 import search_memory, add_memory as add_memory_service

chat_router = APIRouter()

@chat_router.post('/chat')
def chat(request: str, user_id: str):
	return {
		'request': search_memory(request, user_id)}

@chat_router.post('/add_memory')
def add_memory(request: str, user_id: str):
	return {
		'request': add_memory_service(request, user_id)}

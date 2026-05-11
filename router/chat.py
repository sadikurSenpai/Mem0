from fastapi import APIRouter
from dotenv import load_dotenv
load_dotenv()

chat_router = APIRouter()

@chat_router.post('/chat')
def chat(request: str):
	return {'msg': request}

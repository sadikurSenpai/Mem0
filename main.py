from fastapi import FastAPI
from router.chat import chat_router
from router.chatgpt import chatgpt_router

app = FastAPI()

app.include_router(chat_router)
app.include_router(chatgpt_router)

@app.get('/')
def health():
	return {'status': 'Active'}


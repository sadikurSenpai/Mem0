from fastapi import FastAPI
from router.chat import chat_router

app = FastAPI()

app.include_router(chat_router)

@app.get('/')
def health():
	return {'status': 'Active'}


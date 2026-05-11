from fastapi import FastAPI
from router.chatgpt import chatgpt_router

app = FastAPI()

app.include_router(chatgpt_router)

@app.get('/')
def health():
	return {'status': 'Active'}


from mem0 import MemoryClient
from .openai_response import generate_response
from dotenv import load_dotenv
import os
load_dotenv()

def search_memory(query: str, user_id: str):
	client = MemoryClient(api_key=os.getenv("mem0_api_key"))

	results = client.search(query, filters={"user_id": user_id})
	return results


def add_memory(request: str, user_id: str):
	client = MemoryClient(api_key=os.getenv("mem0_api_key"))
	assistant_response = generate_response(request)
	messages = [
		{"role": "user", "content": request},
		{"role": "assistant", "content": assistant_response}
	]
	client.add(messages, user_id=user_id)
	return {"status": "Memory added successfully"}

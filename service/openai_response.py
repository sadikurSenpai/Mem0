from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_response(request: str):
	model = ChatOpenAI(model="gpt-4o-mini")
	response = model.invoke(request)
	return response.content
	
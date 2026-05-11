import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
if not MONGODB_URI:
    raise ValueError("MONGODB_URI is not set in the environment variables.")

client = AsyncIOMotorClient(MONGODB_URI)
db = client.chatgpt_replica

def get_db():
    return db

import os
from dotenv import load_dotenv
from mem0 import Memory

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

_config = {
    "llm": {
        "provider": "openai",
        "config": {
            "model": "gpt-4o-mini",
            "temperature": 0.1,
            "api_key": OPENAI_API_KEY,
        },
    },
    "embedder": {
        "provider": "openai",
        "config": {
            "model": "text-embedding-3-small",
            "api_key": OPENAI_API_KEY,
        },
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {
            "collection_name": "chatgpt_replica",
            "host": QDRANT_HOST,
            "port": QDRANT_PORT,
            "embedding_model_dims": 1536,
        },
    },
    "history_db_path": ":memory:",
}

client: Memory = Memory.from_config(_config)

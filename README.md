# mem0-learning

A ChatGPT-style conversational API that demonstrates **layered memory management** using [Mem0](https://github.com/mem0ai/mem0). The project shows how an AI agent can maintain different scopes of memory — agent rules, session context, and long-term user preferences — without bloating the context window.

## What it demonstrates

Mem0 separates memory into layers so agents remember the right detail at the right time:

| Layer | Scope | Example |
|---|---|---|
| **Agent memory** | Persistent rules tied to an agent identity | "Always include a banana pun" |
| **Session memory** | Multi-turn context that resets after the session | Highlights from the current debugging session |
| **User memory** | Long-term preferences that persist across sessions | Language preference, expertise level |

Each chat request supplies a `user_id`, `session_id`, and `agent_id`. The service fetches the relevant memory from each layer, injects it into the system prompt, and saves the new turn back to Mem0 in the background — keeping the hot path fast.

## Architecture

```
POST /chatgpt/chat
        │
        ├── MongoDB (Motor)      ← stores raw conversation history
        ├── Mem0 + Qdrant        ← vector memory (agent / session / user layers)
        └── LangChain + OpenAI   ← LLM inference (gpt-4o-mini)
```

```
mem0-learning/
├── main.py                  # FastAPI app entry point
├── router/
│   └── chatgpt.py           # Route definitions
├── service/
│   ├── chatgpt_service.py   # Core logic: memory extraction, LLM call, history
│   └── mem0_client.py       # Mem0 Memory instance configuration
├── schema/
│   └── chatgpt.py           # Pydantic models and AgentType enum
├── db/
│   └── mongodb.py           # Async MongoDB client (Motor)
├── scripts/
│   └── test_mem0_scopes.py  # Manual integration test
├── docker-compose.yml       # Qdrant vector store
└── pyproject.toml
```

## Agent types

Three agents are pre-configured, each with a distinct personality:

| Agent ID | Personality |
|---|---|
| `friendly_llm` | Warm and supportive |
| `teacher_llm` | Strict, step-by-step explanations |
| `joker_llm` | Must include a pun or joke in every reply |

You can inject additional rules into any agent at runtime via `POST /chatgpt/agent/memory`.

## Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) (package manager)
- Docker (for Qdrant)
- MongoDB instance (local or Atlas)
- OpenAI API key

## Setup

**1. Clone and install dependencies**

```bash
git clone <repo-url>
cd mem0-learning
uv sync
```

**2. Start Qdrant**

```bash
docker compose up -d
```

**3. Configure environment variables**

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=sk-...
MONGODB_URI=mongodb://localhost:27017
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

**4. Run the server**

```bash
uv run uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

## API reference

### `POST /chatgpt/chat`

Send a message and receive a memory-aware reply.

**Request body:**
```json
{
  "user_id": "user_123",
  "session_id": "session_abc",
  "agent_id": "friendly_llm",
  "message": "What is recursion?"
}
```

**Response:**
```json
{
  "response": "Great question! Recursion is..."
}
```

---

### `POST /chatgpt/agent/memory`

Inject a persistent rule into an agent's memory.

**Request body:**
```json
{
  "agent_id": "joker_llm",
  "rule": "Never answer straightly. Always include a banana pun."
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Rule added to agent joker_llm"
}
```

## Running the test script

```bash
uv run python scripts/test_mem0_scopes.py
```

This adds a custom rule to `joker_llm`, sends a chat message, and prints the response — all memory layers are exercised in a single run.

## Stack

- **[FastAPI](https://fastapi.tiangolo.com/)** — async REST API
- **[Mem0](https://github.com/mem0ai/mem0)** — layered memory management
- **[Qdrant](https://qdrant.tech/)** — vector store for semantic memory search
- **[MongoDB + Motor](https://motor.readthedocs.io/)** — async conversation history
- **[LangChain + OpenAI](https://python.langchain.com/)** — LLM orchestration

# 🚀 CoderX AI Service

> **AI-powered backend microservice for automated coding problem generation** — leveraging LangChain, Groq LLM, Voyage AI embeddings, and AstraDB vector storage to create unique, diverse coding challenges on demand.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-green)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Running the Service](#running-the-service)
- [API Endpoints](#api-endpoints)
- [Workflow & Data Flow](#workflow--data-flow)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [Roadmap](#roadmap)

---

## 🎯 Overview

**CoderX AI Service** is a production-ready Python microservice that automates the generation and management of coding problems for competitive programming platforms. It intelligently combines:

- **🤖 LLM-Powered Generation**: Uses Groq's API via LangChain to create contextually relevant coding problems with test cases and editorials
- **🔍 Semantic Deduplication**: Employs Voyage AI embeddings to detect similar problems and avoid redundant generation
- **💾 Vector Storage**: Persists problems in AstraDB with 1024-dimensional embeddings for efficient similarity search
- **⚡ Real-time API**: FastAPI-based REST service with automatic documentation and CORS support

**Solves:** The problem of manually crafting high-quality, diverse coding problems at scale. This service enables on-demand problem generation while maintaining quality through semantic deduplication.

---

## ✨ Key Features

✅ **Auto-generate diverse coding problems** with structured output (title, description, test cases, editorial)  
✅ **Semantic deduplication** via vector similarity search to prevent near-duplicate problems  
✅ **Comprehensive editorial** with step-by-step solutions and complexity analysis  
✅ **Support for multiple topics** (arrays, strings, linked lists, stacks, queues, trees, graphs, dynamic programming, etc.)  
✅ **Adjustable difficulty levels** (Easy, Medium, Hard)  
✅ **Fast API with interactive docs** (Swagger UI & ReDoc)  
✅ **CORS-enabled** for cross-origin frontend requests  
✅ **Structured error handling** with meaningful error messages  
✅ **Logging & debugging** utilities for development and production

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                           CoderX AI Service                               │
│                                                                           │
│  ┌──────────────────────────────────────────────────────────────────┐     │
│  │                 FastAPI Application (main.py)                     │     │
│  │  - CORS Middleware                                                │     │
│  │  - Health Check Endpoint                                          │     │
│  │  - Problem Generation API                                         │     │
│  └───────────────────────────┬───────────────────────────────────────┘     │
│                              │                                             │
│            ┌─────────────────┴─────────────────┐                           │
│            ▼                                   ▼                           │
│  ┌────────────────────────┐        ┌───────────────────────────────┐       │
│  │      Config Layer      │        │          Routes Layer         │       │
│  │  ├─ server.py          │        │  ├─ problem_routes.py         │       │
│  │  ├─ langchainConfig.py │        │  └─ POST /generate-problem    │       │
│  │  └─ db.py              │        └───────────────┬───────────────┘       │
│  └────────────────────────┘                        │                       │
│                                                    ▼                       │
│                                   ┌────────────────────────────────┐       │
│                                   │        Services Layer          │       │
│                                   │     question_generator.py      │       │
│                                   │  ├─ Validate inputs            │       │
│                                   │  ├─ Check Vector DB cache      │       │
│                                   │  ├─ Generate via LLM           │       │
│                                   │  ├─ Generate Code Stubs        │       │
│                                   │  ├─ Create Test Cases          │       │
│                                   │  └─ Send problem to API        │       │
│                                   └───────────────┬────────────────┘       │
│                                                   │                        │
│           ┌───────────────────────┬───────────────┼───────────────┐        │
│           ▼                       ▼               ▼               ▼        │
│   ┌───────────────┐     ┌──────────────┐   ┌──────────────┐   ┌──────────┐ │
│   │  Embeddings   │     │   LLM Chain  │   │  Vector DB   │   │ Problem  │ │
│   │ HuggingSpace  │     │    (Groq)    │   │  (AstraDB)   │   │ Service  │ │
│   └───────────────┘     └──────────────┘   └──────────────┘   │ (Node.js)│ │
│                                                               │ Express  │ │
│                                                               └────┬─────┘ │
│                                                                    │       │
│                                                                    ▼       │
│                                                               ┌───────────┐ │
│                                                               │ MongoDB   │ │
│                                                               │ Problems  │ │
│                                                               └───────────┘ │
│                                                                           │
└───────────────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

| Component             | Technology         | Purpose                                       |
| --------------------- | ------------------ | --------------------------------------------- |
| **Framework**         | FastAPI            | High-performance REST API framework           |
| **LLM Orchestration** | LangChain          | Prompt management & LLM chaining              |
| **LLM Provider**      | Groq               | Fast inference for problem generation         |
| **Embeddings**        | Voyage AI          | 1024-dimensional semantic embeddings          |
| **Vector Database**   | AstraDB (DataStax) | Persistent vector storage & similarity search |
| **Server**            | Uvicorn            | ASGI server for FastAPI                       |
| **Data Validation**   | Pydantic           | Type-safe request/response models             |
| **Environment**       | python-dotenv      | Secure configuration management               |
| **Logging**           | Python logging     | Structured application logging                |
| **Package Manager**   | uv                 | Fast Python dependency management             |

---

## 📁 Project Structure

```
coderX_aiService/
│
├── main.py                        # Application entry point & FastAPI setup
├── pyproject.toml                 # Project metadata & dependencies (uv)
├── uv.lock                        # Locked dependency tree (reproducible builds)
├── .python-version                # Python runtime version (3.10+)
├── .env                           # Environment variables (NOT committed)
├── .env.example                   # Example configuration template
├── .gitignore                     # Git exclusions
├── embeddings.json                # Sample embeddings (dev artifact)
├── README.md                      # This file
│
└── app/                           # Main application package
    ├── config/                    # Configuration modules
    │   ├── server.py              # .env loader & config constants
    │   ├── langchainConfig.py     # ChatGroq LLM initialization
    │   └── db.py                  # AstraDB client initialization
    │
    ├── routes/                    # API endpoints
    │   └── problem_routes.py       # POST /api/v1/generate/problem
    │
    ├── services/                  # Business logic
    │   └── question_generator.py  # Core generation pipeline
    │
    ├── prompts/                   # LangChain prompt templates
    │   └── problemPrompt.py        # Structured JSON problem prompt
    │
    ├── utils/                     # Utility functions
    │   ├── embedder.py            # Voyage AI embedding calls
    │   ├── response_parser.py      # JSON parsing & validation
    │   └── logger.py              # Centralized logging setup
    │
    ├── vector_store/              # Vector DB operations
    │   └── astra_store.py          # Insert & similarity search
    │
    ├── data_stax/                 # AstraDB setup
    │   └── create_collection.py   # One-time collection creation
    │
    ├── errors/                    # Custom exceptions
    │   └── base_error.py           # BaseError class
    │
    └── __init__.py
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.10+** — [Download here](https://www.python.org/downloads/)
- **uv** — Universal Python package manager ([Installation](https://docs.astral.sh/uv/))
- **API Keys**:
  - Groq API key ([Get it](https://console.groq.com/keys))
  - Voyage AI API key ([Get it](https://dash.voyageai.com/))
  - AstraDB token & endpoint ([Create cluster](https://astra.datastax.com/))

### Step 1: Clone & Navigate

```bash
git clone https://github.com/yourusername/coderx-aiservice.git
cd coderx-aiservice
```

### Step 2: Create Virtual Environment

```bash
# Using uv (recommended)
uv venv --python 3.10

# Activate virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
uv pip install -e .
```

Or install individual packages:

```bash
uv pip install python-dotenv langchain langchain-community langchain-groq \
  sentence-transformers astrapy fastapi uvicorn pydantic
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit `.env` with your actual credentials:

```env
# Groq LLM
GROQ_API_KEY=your_groq_api_key_here

# Voyage AI Embeddings
VOYAGE_API_KEY=your_voyage_api_key_here

# AstraDB
ASTRA_DB_ID=your_astra_db_id
ASTRA_DB_REGION=us-east-1
ASTRA_DB_KEYSPACE=default_keyspace
ASTRA_DB_APPLICATION_TOKEN=your_astra_token

# Optional: Logging level
LOG_LEVEL=INFO
```

---

## 🔧 Environment Configuration

| Variable                     | Description                      | Example                    |
| ---------------------------- | -------------------------------- | -------------------------- |
| `GROQ_API_KEY`               | API key for Groq LLM             | `gsk_...`                  |
| `VOYAGE_API_KEY`             | API key for Voyage AI embeddings | `pa-...`                   |
| `ASTRA_DB_ID`                | AstraDB cluster ID               | `abc12345-...`             |
| `ASTRA_DB_REGION`            | AstraDB region                   | `us-east-1`                |
| `ASTRA_DB_KEYSPACE`          | AstraDB keyspace                 | `default_keyspace`         |
| `ASTRA_DB_APPLICATION_TOKEN` | AstraDB authentication token     | `AstraCS:...`              |
| `LOG_LEVEL`                  | Application logging level        | `DEBUG`, `INFO`, `WARNING` |

---

## ▶️ Running the Service

### Development Mode (with auto-reload)

```bash
uv run uvicorn main:app --reload --port 8000
```

The service will start on `http://localhost:8000`

### Production Mode

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Verify Health Check

```bash
curl http://localhost:8000/health
```

Expected response:

```json
{
  "status": "healthy",
  "timestamp": "2025-04-09T12:34:56.789Z"
}
```

### Access Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

### Generate a Coding Problem

**Endpoint:** `POST /api/v1/generate/problem`

**Request Body:**

```json
{
  "topic": "dynamic programming",
  "difficulty": "medium"
}
```

**Response (Success - 200):**

```json
{
  "source": "generated",
  "problem": {
    "_id": "uuid-1234",
    "title": "Coin Change Problem",
    "description": "# Problem\n\nYou are given an integer array coins...",
    "difficulty": "medium",
    "topic": "dynamic programming",
    "testCases": [
      {
        "input": "[1,2,5]",
        "expectedOutput": "5",
        "description": "Happy path"
      },
      {
        "input": "[2]",
        "expectedOutput": "-1",
        "description": "Edge case"
      },
      {
        "input": "[10,1,1,1,1,1]",
        "expectedOutput": "6",
        "description": "Large input"
      }
    ],
    "editorial": "## Approach\n\n1. Use dynamic programming...",
    "createdAt": "2025-04-09T12:34:56Z"
  }
}
```

**Response (Cache Hit - 200):**

```json
{
  "source": "cache",
  "problem": {
    /* cached problem data */
  }
}
```

**Response (Error - 400/500):**

```json
{
  "detail": "Invalid topic. Supported topics: arrays, strings, ...",
  "error_code": "INVALID_INPUT"
}
```

**Supported Topics:**  
`arrays`, `strings`, `linked lists`, `stacks`, `queues`, `trees`, `graphs`, `dynamic programming`, `greedy`, `backtracking`, `bit manipulation`

**Supported Difficulties:**  
`easy`, `medium`, `hard`

---

## 🔄 Workflow & Data Flow

### Complete Generation Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Client Requests Problem                          │
│              POST /api/v1/generate/problem                          │
│                topic: "arrays", difficulty: "easy"                  │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                         ▼
        ┌────────────────────────────────┐
        │  1. VALIDATE INPUTS            │
        │  - Normalize topic/difficulty  │
        │  - Check against allowed lists │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  2. BUILD QUERY EMBEDDING      │
        │  - Combine topic + difficulty  │
        │  - Call Voyage AI API          │
        │  - Get 1024-dim vector         │
        └────────────┬───────────────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  3. VECTOR DB LOOKUP           │
        │  - Query AstraDB collection    │
        │  - Find similar problems       │
        │  - Similarity threshold: 0.85  │
        └────────┬───────────────────────┘
                 │
        ┌────────┴─────────┐
        │                  │
   CACHE HIT          CACHE MISS
        │                  │
        ▼                  ▼
   Return             ┌──────────────────────┐
   Existing           │  4. GENERATE VIA LLM │
   Problem            │  - Format prompt     │
        │             │  - Call Groq API     │
        │             │  - Parse JSON output │
        │             └──────────┬───────────┘
        │                        │
        │                        ▼
        │             ┌──────────────────────┐
        │             │  5. VALIDATE RESPONSE│
        │             │  - Check required    │
        │             │    fields            │
        │             │  - Parse test cases  │
        │             └──────────┬───────────┘
        │                        │
        │                        ▼
        │             ┌──────────────────────┐
        │             │  6. EMBED PROBLEM    │
        │             │  - Full problem text │
        │             │  - Voyage AI encoder │
        │             └──────────┬───────────┘
        │                        │
        │                        ▼
        │             ┌──────────────────────┐
        │             │  7. PERSIST TO DB    │
        │             │  - Insert document   │
        │             │  - Store embedding   │
        │             └──────────┬───────────┘
        │                        │
        └────────────┬───────────┘
                     │
                     ▼
        ┌────────────────────────────────┐
        │  8. RETURN RESPONSE            │
        │  - Problem data + metadata     │
        │  - Source: "generated/cache"   │
        └────────────────────────────────┘
```

---

## 💻 Development

### Run Tests

```bash
# (Test suite to be implemented)
pytest tests/ -v
```

### Code Structure Principles

- **Separation of Concerns**: Each module has a single responsibility
- **Type Safety**: All functions use Pydantic models and type hints
- **Error Handling**: Custom exceptions for specific error scenarios
- **Logging**: Centralized logging for debugging and monitoring
- **Configuration**: Environment-based, no hardcoded secrets

### Adding a New Topic

1. Add topic name to `VALID_TOPICS` list in `question_generator.py`
2. The prompt template automatically adapts to new topics
3. No code changes needed—configuration-driven

### Adding a New Feature

Example: Adding a "regenerate" endpoint:

```python
# In app/routes/problem_routes.py
@router.post("/regenerate/{problem_id}")
def regenerate_problem(problem_id: str):
    """Regenerate a problem with same topic/difficulty"""
    pass
```

---

## 🐛 Troubleshooting

### Issue: `GROQ_API_KEY` not found

**Solution**: Ensure `.env` file exists in root directory with valid API key.

```bash
echo "GROQ_API_KEY=your_key" >> .env
```

### Issue: AstraDB connection refused

**Solution**: Verify credentials and network connectivity.

```bash
# Test AstraDB connection
python -c "from app.config.db import get_db; print(get_db())"
```

### Issue: `ModuleNotFoundError` for `app`

**Solution**: Install the package in editable mode.

```bash
uv pip install -e .
```

### Issue: Slow embedding API calls

**Solution**: Embeddings are cached in `embeddings.json`. Clear if needed:

```bash
rm embeddings.json
```

---

## 🗺️ Roadmap

### Currently Implemented ✅

- ✅ Problem generation via Groq LLM
- ✅ Semantic embedding with Voyage AI
- ✅ Vector storage in AstraDB
- ✅ Basic validation & error handling
- ✅ FastAPI REST endpoints
- ✅ CORS support

### In Progress 🔄

- 🔄 Semantic deduplication logic refactoring
- 🔄 Advanced similarity search tuning

### Planned 📋

- 📋 Problem retrieval / similarity search endpoint
- 📋 Problem filtering by topic & difficulty
- 📋 Bulk problem generation
- 📋 Problem quality scoring
- 📋 Analytics & usage tracking
- 📋 Database migration CLI
- 📋 Docker containerization
- 📋 Kubernetes deployment manifests
- 📋 CI/CD pipeline (GitHub Actions)
- 📋 Unit & integration test suite
- 📋 Performance benchmarking
- 📋 Multi-language problem support

---

## 📝 Testing the Service

### Quick Manual Test

```bash
# Start the service
uv run uvicorn main:app --reload

# In another terminal, generate a problem
curl -X POST http://localhost:8000/api/v1/generate/problem \
  -H "Content-Type: application/json" \
  -d '{"topic": "arrays", "difficulty": "easy"}'
```

### Using Python Requests

```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/generate/problem",
    json={"topic": "arrays", "difficulty": "easy"}
)

print(response.json())
```

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [LangChain Docs](https://python.langchain.com/)
- [AstraDB Python SDK](https://docs.datastax.com/en/astra-db-serverless/databases/api-reference/astrapy.html)
- [Voyage AI API](https://docs.voyageai.com/)
- [Groq API Guide](https://console.groq.com/docs/)

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 🤝 Support

For issues, questions, or suggestions, please:

- Open an [Issue](https://github.com/yourusername/coderx-aiservice/issues)
- Check existing documentation
- Review the FAQ section above

---

**Made with ❤️ for the CoderX community**
├── config/
│ ├── server.py → Reads environment variables, exports constants
│ ├── langchainConfig.py → ChatGroq singleton factory via LangChain
│ └── db.py → AstraDB DataAPIClient connection & db handle
│
├── prompts/
│ └── problemPrompt.py → Zero-shot JSON-constrained LangChain prompt
│
├── utils/
│ └── embedder.py → Voyage AI client; embeds text → 1024-dim vectors
│
├── data_stax/
│ └── create_collection.py → One-time setup: creates the AstraDB vector collection
│
└── vector_store/ → (Empty) Planned: similarity search & retrieval logic

````

### Folder Responsibilities

| Folder | Responsibility |
|---|---|
| `app/config/` | All environment and client configuration — single source of truth for secrets and service clients |
| `app/prompts/` | LLM prompt templates — decoupled from the chain so they can be evolved independently |
| `app/utils/` | Shared utilities across the service (currently embedding only; will grow) |
| `app/data_stax/` | DataStax AstraDB lifecycle scripts (collection creation, migrations) |
| `app/vector_store/` | Intended home for vector search, retrieval, and deduplication logic |

---

## File-by-File Explanation

### `main.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Application entry point |
| **Current State** | Stub — only prints `"Hello from coderx-aiservice!"` |
| **Key Functions** | `main()` |
| **Interactions** | None yet; intended to bootstrap the HTTP server and invoke the generation + embedding pipeline |

> ⚠️ This file is a placeholder. No HTTP server, routing, or chain invocation is wired up yet.

---

### `pyproject.toml`

| Attribute | Detail |
|---|---|
| **Purpose** | Project manifest managed by the `uv` package manager |
| **Package Name** | `coderx-aiservice` v0.1.0 |
| **Python Requirement** | `>=3.10` |
| **Declared Dependencies** | `dotenv>=0.9.9`, `langchain>=1.2.15`, `langchain-community>=0.4.1`, `langchain-groq>=1.1.2` |

> ⚠️ **Gap** — `voyageai` and `astrapy` are actively used in source files but are **not declared** in `pyproject.toml`. They must be installed manually and should be added as formal dependencies.

---

### `app/config/server.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Centralised environment configuration loader |
| **Key Exports** | `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_TEMPERATURE`, `ASTRA_DB_APPLICATION_TOKEN`, `ASTRA_DB_APPLICATION_URL`, `VOYAGE_API_KEY` |
| **Mechanism** | Calls `load_dotenv()` then reads typed values from `os.getenv()` |
| **Interactions** | Imported by `langchainConfig.py`, `db.py`, and `embedder.py` |

**Known Issue:** `float(os.getenv("GROQ_TEMPERATURE"))` will raise a `TypeError` if `GROQ_TEMPERATURE` is absent from the environment. A safe default should be used: `float(os.getenv("GROQ_TEMPERATURE", "0.7"))`.

---

### `app/config/langchainConfig.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Singleton factory that constructs a `ChatGroq` LLM client |
| **Key Function** | `get_groq_client()` — returns a configured `ChatGroq` instance |
| **LLM Provider** | Groq (via `langchain-groq`) |
| **Model** | Configurable via `GROQ_MODEL`; currently set to `openai/gpt-oss-120b` |
| **Response Format** | Forces `{"type": "json_object"}` — all LLM outputs are structured JSON |
| **Temperature** | Configurable via `GROQ_TEMPERATURE` (default `0.7`) |
| **Interactions** | Imports config from `server.py`; the returned client will be consumed by the LangChain chain |

**Known Bug — `UnboundLocalError`:** The global singleton guard reads `isllmInstance` before the `global` keyword is declared:

```python
# Current (broken):
isllmInstance = None
def get_groq_client():
    if not isllmInstance:       # ← reads local scope → UnboundLocalError
        ...
    isllmInstance = ChatGroq(...)  # ← Python treats isllmInstance as local

# Fix:
def get_groq_client():
    global isllmInstance          # ← declare global first
    if not isllmInstance:
        isllmInstance = ChatGroq(...)
    return isllmInstance
````

---

### `app/config/db.py`

| Attribute        | Detail                                                                                                                                    |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Purpose**      | Establishes and exposes the AstraDB database connection                                                                                   |
| **Key Objects**  | `client` (`DataAPIClient`), `db` (database handle)                                                                                        |
| **Mechanism**    | Uses `astrapy.DataAPIClient` with the application token and URL from `server.py`                                                          |
| **Side Effect**  | Prints the list of existing collection names on import — confirms connectivity                                                            |
| **Interactions** | Imports `ASTRA_DB_APPLICATION_TOKEN` and `ASTRA_DB_APPLICATION_URL` from `server.py`; `db` handle will be used by vector store operations |

> ⚠️ `db.py` imports from `app.config.server` but `create_collection.py` incorrectly imports directly from `app.config.db` (which re-exports `ASTRA_DB_APPLICATION_TOKEN`). This causes a circular-style import inconsistency and should be unified.

---

### `app/prompts/problemPrompt.py`

| Attribute           | Detail                                                                                   |
| ------------------- | ---------------------------------------------------------------------------------------- |
| **Purpose**         | Defines the LLM prompt and LangChain `PromptTemplate` for problem generation             |
| **Key Objects**     | `problem_prompt_template` (raw string), `problem_prompt` (`PromptTemplate`)              |
| **Input Variables** | `topic`, `difficulty`                                                                    |
| **Output Contract** | Strict JSON: `title`, `description` (Markdown), `difficulty`, `testCases[]`, `editorial` |
| **Interactions**    | Will be combined with `ChatGroq` in a LangChain chain (not yet wired)                    |

**Prompt Design Principles:**

- **Role priming** — positions the LLM as "an expert competitive-programming problem setter working for CoderX (similar to LeetCode)"
- **Schema enforcement** — the exact JSON structure is embedded verbatim in the prompt
- **Hard rules** — 5 numbered rules prevent hallucination of extra fields, markdown code fences, or out-of-specification values
- **Test case diversity** — explicitly requires a happy-path case, an edge case, and a large-input case
- **JSON mode** — `response_format={"type": "json_object"}` is passed at the API level as a secondary safety net

---

### `app/utils/embedder.py`

| Attribute           | Detail                                                                                    |
| ------------------- | ----------------------------------------------------------------------------------------- |
| **Purpose**         | Embeds text documents into 1024-dimensional dense vectors using Voyage AI                 |
| **Key Objects**     | `vo` (`voyageai.Client`), `texts` (list of 6 sample strings), `result` (embedding output) |
| **Embedding Model** | `voyage-4-large`                                                                          |
| **Input Type**      | `"document"` (optimised for storage/retrieval, not for query)                             |
| **Output**          | A list of 1024-element float arrays per input text                                        |
| **Interactions**    | Reads `VOYAGE_API_KEY` from `server.py`; results will feed into AstraDB vector inserts    |

> ℹ️ Currently the `texts` list contains 6 **hardcoded sample sentences** (Mediterranean diet, photosynthesis, etc.) that are unrelated to coding problems. This is a development test harness — in production, the generated problem text will replace these. The raw float output is saved locally as `embeddings.json`.

---

### `app/data_stax/create_collection.py`

| Attribute            | Detail                                                                                  |
| -------------------- | --------------------------------------------------------------------------------------- |
| **Purpose**          | One-time setup script that creates the `coderx_problems` vector collection in AstraDB   |
| **Collection Name**  | `coderx_problems`                                                                       |
| **Vector Dimension** | `1024` (matches Voyage AI `voyage-4-large` output)                                      |
| **Distance Metric**  | Cosine similarity (`VectorMetric.COSINE`)                                               |
| **Key Objects**      | `CollectionDefinition`, `CollectionVectorOptions` from `astrapy.info`                   |
| **Interactions**     | Reads credentials from `app.config.db`; run once manually before the service is started |

> ⚠️ This script should be run **once** to provision the collection. It will error if the collection already exists. Consider wrapping in a try/except or using AstraDB's `if_not_exists` pattern for idempotency.

---

### `app/vector_store/` _(empty directory)_

| Attribute         | Detail                                                                          |
| ----------------- | ------------------------------------------------------------------------------- |
| **Purpose**       | Intended location for vector similarity search and retrieval logic              |
| **Current State** | Empty — no files                                                                |
| **Planned**       | Query encoding, ANN (approximate nearest-neighbour) search, duplicate detection |

---

### `embeddings.json`

| Attribute      | Detail                                                               |
| -------------- | -------------------------------------------------------------------- |
| **Purpose**    | Local dump of the raw Voyage AI embedding output                     |
| **Content**    | A JSON array of 6 arrays, each containing 1024 float values          |
| **Source**     | Generated by `app/utils/embedder.py` from the 6 hardcoded `texts`    |
| **Git Status** | Listed in `.gitignore` — not tracked in version control              |
| **Usage**      | Development/debugging artefact; not used by any production code path |

---

## Data Flow

### Current (Partial) Flow

```
Developer runs embedder.py
        │
        ▼
voyageai.Client.embed(texts, model="voyage-4-large", input_type="document")
        │
        ▼
List of 6 × 1024-float vectors
        │
        ▼
Saved locally → embeddings.json
```

### Intended Full Production Flow

```
1. Client sends request → POST /generate/problem
   Body: { "topic": "binary search", "difficulty": "medium" }
        │
        ▼
2. Route handler validates input (topic, difficulty)
        │
        ▼
3. problem_prompt.format_prompt(topic=topic, difficulty=difficulty)
   → Builds the LLM prompt string
        │
        ▼
4. get_groq_client().invoke(formatted_prompt)
   → Sends request to Groq API (model: openai/gpt-oss-120b, temp: 0.7)
   → Response forced to JSON via response_format={"type": "json_object"}
        │
        ▼
5. Parse JSON response → structured problem dict
   {title, description, difficulty, testCases[], editorial}
        │
        ▼
6. Combine title + description + editorial into embedding input string
        │
        ▼
7. voyageai.Client.embed([problem_text], model="voyage-4-large", input_type="document")
   → 1024-dimensional float vector
        │
        ▼
8. Insert into AstraDB collection "coderx_problems"
   Document: { ...problem_fields, "$vector": [1024 floats] }
        │
        ▼
9. Return structured problem JSON to client
```

---

## Technologies Used

| Technology              | Version / Details                      | Role                                                    |
| ----------------------- | -------------------------------------- | ------------------------------------------------------- |
| **Python**              | 3.10 (pinned via `.python-version`)    | Runtime                                                 |
| **uv**                  | —                                      | Package manager and dependency lockfile                 |
| **LangChain**           | `>=1.2.15`                             | LLM orchestration — prompt templates, chain composition |
| **langchain-community** | `>=0.4.1`                              | Extended LangChain integrations                         |
| **langchain-groq**      | `>=1.1.2`                              | Groq-specific adapter (`ChatGroq` class)                |
| **Groq**                | API (model: `openai/gpt-oss-120b`)     | Fast LLM inference (OpenAI-compatible API)              |
| **Voyage AI**           | `voyageai` SDK, model `voyage-4-large` | Text embedding — 1024-dimensional dense vectors         |
| **AstraDB (DataStax)**  | `astrapy` SDK, us-east-2 region        | Vector database — stores problems + embeddings          |
| **dotenv**              | `>=0.9.9`                              | `.env` file loading                                     |

---

## Current Features Implemented

| Feature                                 | Status                       | File                                 |
| --------------------------------------- | ---------------------------- | ------------------------------------ |
| Project scaffold with `uv` and lockfile | ✅ Complete                  | `pyproject.toml`, `uv.lock`          |
| Environment variable loading            | ✅ Complete                  | `app/config/server.py`               |
| Groq LLM client initialisation          | ⚠️ Implemented (bug present) | `app/config/langchainConfig.py`      |
| Problem generation prompt template      | ✅ Complete                  | `app/prompts/problemPrompt.py`       |
| AstraDB connection + db handle          | ✅ Complete                  | `app/config/db.py`                   |
| AstraDB vector collection creation      | ✅ Complete (run once)       | `app/data_stax/create_collection.py` |
| Voyage AI embedding client              | ✅ Complete (test data)      | `app/utils/embedder.py`              |
| Local embedding dump                    | ✅ Complete (dev artefact)   | `embeddings.json`                    |
| `.gitignore`                            | ✅ Present                   | `.gitignore`                         |

---

## Features In Progress

| Feature                                           | Evidence                                                                                | Location                                 |
| ------------------------------------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------- |
| **Vector similarity search / retrieval**          | `app/vector_store/` directory exists but is empty                                       | `app/vector_store/`                      |
| **LangChain chain assembly**                      | `ChatGroq` client and `PromptTemplate` are both built independently but never connected | `langchainConfig.py`, `problemPrompt.py` |
| **Embedding integration with problem generation** | Embedder uses placeholder text; not connected to problem output                         | `app/utils/embedder.py`                  |
| **AstraDB document insertion**                    | Collection is created; insert logic not written                                         | `app/data_stax/`                         |

---

## Missing Components / TODO

| Priority  | Component                            | Description                                                                                   |
| --------- | ------------------------------------ | --------------------------------------------------------------------------------------------- | ---------------------------------------------- |
| 🔴 **P0** | Fix `UnboundLocalError`              | Add `global isllmInstance` inside `get_groq_client()`                                         |
| 🔴 **P0** | Fix `float()` crash                  | Use `float(os.getenv("GROQ_TEMPERATURE", "0.7"))`                                             |
| 🔴 **P0** | Rotate the exposed API keys          | Keys in `.env` are real credentials — rotate immediately                                      |
| 🔴 **P0** | Add missing deps to `pyproject.toml` | `voyageai` and `astrapy` are used but not declared                                            |
| 🔴 **P1** | Wire the LangChain chain             | `problem_prompt                                                                               | get_groq_client()` — invoke and parse response |
| 🔴 **P1** | HTTP server                          | Create a FastAPI app with `POST /generate/problem`                                            |
| 🔴 **P1** | Connect embedder to problem output   | Pass generated problem text (not placeholder) to Voyage AI                                    |
| 🔴 **P1** | AstraDB insert logic                 | After embedding, insert `{...problem, "$vector": embedding}` into `coderx_problems`           |
| 🟡 **P2** | Vector similarity search             | Implement `app/vector_store/` — ANN search to detect duplicate/similar problems               |
| 🟡 **P2** | Pydantic models                      | Request (`topic`, `difficulty`) and response schema validation                                |
| 🟡 **P2** | Input validation                     | Allowlist `difficulty` to `["easy", "medium", "hard"]`; sanitise `topic`                      |
| 🟡 **P2** | Error handling                       | LLM failures, JSON parse errors, AstraDB timeouts, Voyage API errors                          |
| 🟡 **P2** | Unit tests                           | Mock Groq + Voyage + AstraDB; test prompt formatting and response parsing                     |
| 🟢 **P3** | Dockerfile                           | Containerise for deployment on Render/Railway/GCP                                             |
| 🟢 **P3** | CI/CD pipeline                       | GitHub Actions: lint, type-check, test on every PR                                            |
| 🟢 **P3** | Caching layer                        | Redis cache keyed on `(topic, difficulty)` to avoid redundant LLM calls                       |
| 🟢 **P3** | Idempotent collection creation       | Wrap `create_collection.py` in a try/except for safe re-runs                                  |
| 🟢 **P3** | Similarity threshold filtering       | Before inserting, query the vector store; reject problems above a cosine similarity threshold |

---

## Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Groq LLM Configuration
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=openai/gpt-oss-120b
GROQ_TEMPERATURE=0.7

# AstraDB (DataStax) Configuration
ASTRA_DB_APPLICATION_TOKEN=AstraCS:your_token_here
ASTRA_DB_APPLICATION_URL=https://your-db-id-region.apps.astra.datastax.com

# Voyage AI Configuration
VOYAGE_API_KEY=pa-your_key_here
```

| Variable                     | Required | Type     | Description                                                            |
| ---------------------------- | -------- | -------- | ---------------------------------------------------------------------- |
| `GROQ_API_KEY`               | ✅ Yes   | `string` | API key for the Groq inference API (`gsk_...`)                         |
| `GROQ_MODEL`                 | ✅ Yes   | `string` | Groq model identifier (e.g., `openai/gpt-oss-120b`, `llama3-70b-8192`) |
| `GROQ_TEMPERATURE`           | ✅ Yes   | `float`  | LLM sampling temperature — `0.0` = deterministic, `1.0` = creative     |
| `ASTRA_DB_APPLICATION_TOKEN` | ✅ Yes   | `string` | AstraDB application token (`AstraCS:...`)                              |
| `ASTRA_DB_APPLICATION_URL`   | ✅ Yes   | `string` | AstraDB HTTPS endpoint URL                                             |
| `VOYAGE_API_KEY`             | ✅ Yes   | `string` | Voyage AI API key (`pa-...`)                                           |

> ⚠️ **Security Warning:** The `.env` file is listed in `.gitignore` and must **never** be committed to version control. The keys currently stored in that file are real credentials and should be rotated immediately if the repository has been shared or made public.

---

## How to Run the Project

### Prerequisites

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) package manager

```bash
# Install uv (if not already installed)
pip install uv
```

### 1. Clone and Install

```bash
git clone <repo-url>
cd coderX_aiService

# Install all locked dependencies
uv sync

# Manually install undeclared deps (until pyproject.toml is fixed)
uv add voyageai astrapy
```

### 2. Configure Environment

```bash
# Create your .env file
cp .env.example .env   # (or create it from scratch)
```

Fill in all six variables as shown in the [Environment Variables](#environment-variables) section.

### 3. Provision the AstraDB Collection (One-Time)

```bash
# This creates the "coderx_problems" vector collection in your AstraDB instance
uv run python -m app.data_stax.create_collection
```

### 4. Test the Embedding Pipeline

```bash
# Runs the embedder against sample texts; outputs vectors to embeddings.json
uv run python -m app.utils.embedder
```

### 5. Run the Application

```bash
# Currently only runs the stub — prints "Hello from coderx-aiservice!"
uv run python main.py
```

> Once the HTTP server is implemented, this will become:
>
> ```bash
> uv run uvicorn main:app --reload --port 8000
> ```

---

## Example Workflow

Once the full pipeline is implemented, the intended usage is:

### Request

```bash
curl -X POST http://localhost:8000/generate/problem \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search", "difficulty": "medium"}'
```

### Expected Response

```json
{
  "title": "Find Peak Element",
  "description": "## Problem Statement\nGiven a 0-indexed integer array `nums`, find a peak element and return its index.\n\n## Input Format\nA single line containing `n` space-separated integers.\n\n## Output Format\nA single integer — the index of a peak element.\n\n## Constraints\n- 1 ≤ n ≤ 10^5\n- -10^9 ≤ nums[i] ≤ 10^9\n- nums[-1] = nums[n] = -∞\n\n## Example\n**Input:** `[1, 2, 3, 1]`\n**Output:** `2`",
  "difficulty": "medium",
  "testCases": [
    { "input": "[1, 2, 3, 1]", "output": "2" },
    { "input": "[1]", "output": "0" },
    { "input": "[1, 2, 3, ..., 100000]", "output": "99999" }
  ],
  "editorial": "Use binary search. At each midpoint `mid`, if `nums[mid] < nums[mid+1]`, the peak lies to the right; otherwise it lies to the left or at `mid`. Continue halving until `lo == hi`.\n\n**Time Complexity:** O(log n)\n**Space Complexity:** O(1)"
}
```

### Internal Steps (Behind the Scenes)

```
POST /generate/problem
    │
    ├─ 1. Validate: difficulty ∈ {easy, medium, hard}
    │
    ├─ 2. Format prompt with topic="binary search", difficulty="medium"
    │
    ├─ 3. ChatGroq.invoke(prompt)  →  raw JSON string from Groq API
    │
    ├─ 4. json.loads(raw_string)   →  Python dict
    │
    ├─ 5. voyageai.embed([title + description + editorial])
    │      →  1024-dim float vector
    │
    ├─ 6. astradb.collection("coderx_problems").insert_one({
    │         ...problem_dict, "$vector": embedding_vector
    │      })
    │
    └─ 7. Return problem_dict as HTTP 200 JSON response
```

---

## Future Improvements

### Scalability

- **Async HTTP server** — FastAPI with `async def` endpoints and `asyncio`-compatible LangChain calls (`ainvoke`) so multiple requests are processed concurrently without blocking.
- **Streaming responses** — stream the LLM output token-by-token for long editorials, reducing perceived latency.
- **Redis caching** — cache `(topic, difficulty)` → `problem_id` mappings to skip redundant LLM + embedding calls for recently seen combinations.
- **Horizontal scaling** — the service is stateless (all state lives in AstraDB/Redis); it can be replicated behind a load balancer trivially.

### Maintainability

- **Fix the singleton bug** — use `@functools.lru_cache(maxsize=1)` on `get_groq_client()` as a Pythonic, thread-safe alternative.
- **Pydantic models** — define `GenerateRequest(topic: str, difficulty: Literal["easy","medium","hard"])` and `Problem(title, description, difficulty, testCases, editorial)` with full type validation.
- **Service layer** — create `services/problem_generator.py` that builds and invokes the full chain, keeping route handlers thin.
- **Type annotations** — add `mypy`-compatible annotations throughout.

### Deduplication & Quality

- **Similarity filtering** — before inserting, query the vector store with the new embedding; if cosine similarity > 0.92 with any existing problem, reject or mutate the new problem.
- **Post-generation validation** — programmatically verify that the LLM response contains all required fields and that `testCases` has exactly 3 entries before accepting.

### Security

- **Rotate all API keys** — `GROQ_API_KEY`, `ASTRA_DB_APPLICATION_TOKEN`, and `VOYAGE_API_KEY` should all be rotated immediately.
- **Input sanitisation** — allowlist `difficulty` to `["easy", "medium", "hard"]` and apply length/content limits on `topic` to prevent prompt injection.
- **Rate limiting** — use `slowapi` or an API gateway to throttle requests and protect the Groq and Voyage AI quotas.
- **Secret management** — use environment injection at the platform level (Render secrets, GitHub Actions secrets, GCP Secret Manager) — never commit `.env`.

---

## Summary

`coderx-aiservice` is an early-stage but well-structured Python microservice that implements the AI core of the CoderX competitive programming platform. It chains together three best-in-class AI services: **Groq** for ultra-fast LLM inference, **Voyage AI** for state-of-the-art semantic embeddings, and **AstraDB** for scalable vector storage and similarity search.

The service has a clear three-stage architecture — _Generate → Embed → Store_ — with solid foundations already in place: a clean prompt engineering template that enforces strict JSON output, a working AstraDB vector collection definition with correct 1024-dimensional cosine geometry, and a Voyage AI embedder producing the right vector dimensionality. The main work remaining is to wire the stages together into a callable chain, expose that chain via an HTTP API, and address a handful of known bugs in the configuration layer. Once those P0/P1 items are resolved, the service will be fully functional and ready to power on-demand problem generation at scale.

---

_Last updated: April 2026 — reflects the exact state of the repository at time of analysis._

# CoderX AI Service

> **AI-powered backend microservice for the CoderX competitive programming platform** — generates original coding problems, test cases, and editorials on demand using an LLM orchestrated via LangChain and Groq.

---

## Project Overview

`coderx-aiservice` is a standalone Python microservice that forms the AI backbone of the **CoderX** platform (a LeetCode-style competitive programming product). Its primary responsibility is to accept a topic and difficulty level as input and use a large language model to synthesize:

- A structured coding problem statement (Markdown)
- Three test cases (happy path, edge case, large input)
- A step-by-step editorial with time and space complexity analysis

The output is always a strictly-typed JSON object, ensuring downstream consumers can parse responses without ambiguity. The service currently uses **Groq** as the LLM inference provider and **LangChain** as the orchestration layer.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                  coderx-aiservice                   │
│                                                     │
│  ┌──────────┐    ┌───────────────┐   ┌───────────┐  │
│  │ main.py  │───▶│  app/config/  │──▶│  Groq API │  │
│  │(entry pt)│    │  server.py    │   │  (remote) │  │
│  └──────────┘    │  langchainCfg │   └───────────┘  │
│                  └───────┬───────┘                  │
│                          │                          │
│                  ┌───────▼───────┐                  │
│                  │ app/prompts/  │                  │
│                  │ problemPrompt │                  │
│                  └───────────────┘                  │
└─────────────────────────────────────────────────────┘
```

The architecture is intentionally minimal at this stage:

| Layer | Role |
|---|---|
| **Config** | Reads environment variables and initialises the LangChain + Groq client |
| **Prompt Templates** | Encodes the structured LLM prompt with input variables |
| **LLM Chain** | (intended) Combines prompt + model into an invocable chain |
| **Entry Point** | (stub) Will wire everything together and expose the API |

---

## Folder Structure

```
coderX_aiService/
│
├── main.py                   → Application entry point (currently a stub)
├── pyproject.toml            → Project metadata and dependency manifest (uv)
├── uv.lock                   → Locked dependency tree for reproducible installs
├── .python-version           → Pins runtime to Python 3.10
├── .env                      → Local environment variable overrides (NOT committed to VCS ideally)
├── README.md                 → This file
│
└── app/
    ├── config/
    │   ├── server.py         → Loads .env and exports typed config constants
    │   └── langchainConfig.py→ Singleton factory for the ChatGroq LLM client
    │
    └── prompts/
        └── problemPrompt.py  → LangChain PromptTemplate for problem generation
```

---

## File-by-File Explanation

### `main.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Application entry point |
| **Current State** | Stub — only prints `"Hello from coderx-aiservice!"` |
| **Key Functions** | `main()` |
| **Interactions** | None yet; intended to wire up the server (FastAPI/Flask) and invoke the LLM chain |

> ⚠️ This file is a placeholder. No HTTP server, routing, or chain invocation is wired up yet.

---

### `app/config/server.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Centralised environment configuration loader |
| **Key Variables Exported** | `GROQ_API_KEY`, `GROQ_MODEL`, `GROQ_TEMPERATURE` |
| **Mechanism** | Calls `load_dotenv()` then reads typed values from `os.getenv()` |
| **Interactions** | Imported by `langchainConfig.py` |

**Critical bug:** `GROQ_TEMPERATURE` is cast with `float(os.getenv("GROQ_TEMPERATURE"))` without a fallback. If `GROQ_TEMPERATURE` is missing from the environment, this will raise a `TypeError` at import time.

---

### `app/config/langchainConfig.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Singleton factory that constructs a `ChatGroq` LLM client |
| **Key Function** | `get_groq_client()` — returns a configured `ChatGroq` instance |
| **LLM Provider** | Groq (via `langchain-groq`) |
| **Response Format** | Forces `{"type": "json_object"}` — all LLM outputs are structured JSON |
| **Interactions** | Imports config constants from `server.py`; returned client is consumed by chains |

**Critical bug:** The singleton guard pattern is broken. `isllmInstance` is a module-level variable set to `None`, but inside `get_groq_client()` it is read (`if not isllmInstance`) yet then assigned without the `global` keyword. Python will raise an `UnboundLocalError` on the first call. The correct fix is to add `global isllmInstance` at the top of the function, or use a class-based singleton.

---

### `app/prompts/problemPrompt.py`

| Attribute | Detail |
|---|---|
| **Purpose** | Defines the LLM prompt and LangChain `PromptTemplate` for problem generation |
| **Key Objects** | `problem_prompt_template` (raw string), `problem_prompt` (PromptTemplate) |
| **Input Variables** | `topic`, `difficulty` |
| **Output Contract** | Strict JSON schema: `title`, `description`, `difficulty`, `testCases[]`, `editorial` |
| **Interactions** | Will be combined with the `ChatGroq` client in a LangChain chain (not yet wired) |

The prompt enforces several hard rules on the LLM:
- Output pure JSON only (no markdown fences)
- Exactly 3 test cases
- `difficulty` must be `easy | medium | hard` (lowercase)
- Description must contain: Problem Statement, Input Format, Output Format, Constraints, and ≥1 worked Example

---

## Core Features Implemented

| Feature | Status |
|---|---|
| Environment configuration loading | ✅ Complete |
| Groq LLM client initialisation | ⚠️ Implemented but has a critical bug (see above) |
| Problem generation prompt template | ✅ Complete (well-structured JSON-forcing prompt) |
| LangChain chain assembly | ❌ Not implemented |
| API / HTTP server | ❌ Not implemented |
| Request routing | ❌ Not implemented |
| Response serialisation | ❌ Not implemented |
| Authentication / rate limiting | ❌ Not implemented |

---

## APIs / Endpoints

No HTTP endpoints are implemented at this time. The intended endpoint based on the codebase design is:

```
POST /generate/problem
Body: { "topic": "<string>", "difficulty": "easy | medium | hard" }
Response: {
  "title": "...",
  "description": "... (Markdown)",
  "difficulty": "easy | medium | hard",
  "testCases": [
    { "input": "...", "output": "..." },
    { "input": "...", "output": "..." },
    { "input": "...", "output": "..." }
  ],
  "editorial": "..."
}
```

---

## Data Models

No database or ORM is present. The only data model is the **LLM response schema**, enforced through the prompt:

```json
{
  "title": "string",
  "description": "string (Markdown)",
  "difficulty": "easy | medium | hard",
  "testCases": [
    { "input": "string", "output": "string" }
  ],
  "editorial": "string"
}
```

No persistence layer (SQL, NoSQL, cache) exists in the current codebase.

---

## AI / LLM Integrations

### Provider
- **Groq** — fast LLM inference API (OpenAI-compatible)
- **Model configured:** `openai/gpt-oss-120b` (set in `.env`)

### Orchestration
- **LangChain** (`langchain`, `langchain-community`, `langchain-groq`)
- The `ChatGroq` class from `langchain-groq` wraps the Groq API

### Pipeline (intended)

```
User Input (topic, difficulty)
       │
       ▼
PromptTemplate.format_prompt(topic=..., difficulty=...)
       │
       ▼
ChatGroq.invoke(formatted_prompt)   ← response_format: json_object enforced
       │
       ▼
JSON-parsed structured problem object
       │
       ▼
HTTP Response to caller
```

### Prompt Design

The prompt in `problemPrompt.py` is a **zero-shot, schema-constrained** prompt. Key design choices:

1. **Role priming** — "You are an expert competitive-programming problem setter working for CoderX"
2. **Schema enforcement** — the exact JSON shape is embedded in the prompt
3. **Hard rules** — numbered rules prevent hallucination of extra fields or markdown wrappers
4. **Test case diversity** — explicitly requires happy path, edge case, and large input variants
5. **JSON mode** — `response_format={"type": "json_object"}` is passed at the API level as an additional safety net

---

## Execution Flow

```
1. Application starts → main.py → main() [stub, nothing happens yet]

Intended full flow once implemented:
2. HTTP server starts (e.g., FastAPI/Uvicorn)
3. Client sends POST /generate/problem { topic, difficulty }
4. Route handler calls get_groq_client() to get the LLM instance
5. problem_prompt.format_prompt(topic=topic, difficulty=difficulty) builds the message
6. ChatGroq.invoke(prompt) sends request to Groq API
7. Groq returns JSON string → parsed into Python dict
8. Dict returned as HTTP JSON response to client
```

---

## Dependencies

| Package | Version Constraint | Role |
|---|---|---|
| `langchain` | `>=1.2.15` | LLM orchestration framework |
| `langchain-community` | `>=0.4.1` | Extended LangChain integrations |
| `langchain-groq` | `>=1.1.2` | Groq-specific LangChain adapter (`ChatGroq`) |
| `dotenv` | `>=0.9.9` | `.env` file loader |
| **Python** | `>=3.10` | Runtime (pinned to 3.10 via `.python-version`) |
| **uv** | — | Package manager / lockfile (replaces pip/poetry) |

---

## Environment Variables

| Variable | Required | Example Value | Description |
|---|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | `gsk_...` | API key for authenticating with the Groq inference API |
| `GROQ_MODEL` | ✅ Yes | `openai/gpt-oss-120b` | Groq model identifier to use for generation |
| `GROQ_TEMPERATURE` | ✅ Yes | `0.7` | Sampling temperature for the LLM (0.0 = deterministic, 1.0 = creative) |

> ⚠️ **Security Warning:** The `.env` file in this repository contains a real API key (`gsk_1FnRvjz3...`). This key should be **immediately rotated** and `.env` should be added to `.gitignore` to prevent future credential leakage.

---

## Current Implementation Status

| Component | Status | Notes |
|---|---|---|
| Project scaffold | ✅ Complete | `uv`-based Python project with lockfile |
| Environment config | ✅ Complete | `server.py` loads and exports all vars |
| LLM client factory | ⚠️ Buggy | Singleton pattern broken (`UnboundLocalError`) |
| Problem prompt | ✅ Complete | Well-structured, schema-enforced prompt |
| LangChain chain assembly | ❌ Missing | Prompt + model not connected |
| API server | ❌ Missing | No FastAPI/Flask/etc. server exists |
| Endpoints / routes | ❌ Missing | No HTTP routes defined |
| Error handling | ❌ Missing | No try/except, no validation |
| Tests | ❌ Missing | No test files present |
| CI/CD | ❌ Missing | No GitHub Actions or pipeline config |
| Dockerfile | ❌ Missing | No containerisation |
| `.gitignore` | ❌ Missing | `.env` file with real credentials is exposed |

---

## Potential Issues

### 🔴 Critical

1. **API Key Exposed in `.env`** — The Groq API key (`gsk_1FnRvjz3...`) is committed in plain text. If this repository is public or shared, the key must be rotated immediately.

2. **`UnboundLocalError` in `get_groq_client()`** — The function reads `isllmInstance` (module-level) inside a function scope but then assigns to it without `global isllmInstance`. Python treats any assigned variable as local; reading it before assignment raises `UnboundLocalError`.

   ```python
   # Fix:
   def get_groq_client():
       global isllmInstance          # ← add this
       if not isllmInstance:
           ...
           isllmInstance = ChatGroq(...)
       return isllmInstance
   ```

3. **Unchecked `float()` cast** — `float(os.getenv("GROQ_TEMPERATURE"))` will raise `TypeError` if the variable is absent. Use `float(os.getenv("GROQ_TEMPERATURE", "0.7"))` as a safe default.

### 🟡 Moderate

4. **No `.gitignore`** — The `.venv` directory and `.env` file are likely tracked by git. Both should be excluded.

5. **`langchain` version `>=1.2.15`** — LangChain's public API changes frequently between minor versions. Unpinned upper bounds can cause silent breakage when new versions are released.

6. **Model name format** — `openai/gpt-oss-120b` uses an OpenAI-prefixed path on Groq, which suggests it targets a specific routing. This should be validated against Groq's current model catalogue.

7. **No input validation** — `topic` and `difficulty` are injected directly into the prompt. A malicious or malformed input could attempt prompt injection.

### 🟢 Low

8. **`main.py` is a stub** — The project cannot actually do anything when run.

9. **`langchain-community`** is included as a dependency but nothing in the current code uses it.

---

## Improvement Suggestions

### Scalability
- Add an **async HTTP server** (FastAPI + Uvicorn + `asyncio`) so multiple problem generation requests can be processed concurrently without blocking.
- Consider **streaming** the LLM response for long editorials instead of waiting for the full completion.
- Add a **Redis cache** keyed on `(topic, difficulty)` to serve repeated requests without hitting the LLM API.

### Maintainability
- Fix the singleton pattern — use a module-level `_client: ChatGroq | None = None` with `global` or a `@lru_cache(maxsize=1)` decorated factory.
- Introduce **Pydantic models** for the request schema (`topic`, `difficulty`) and the LLM response schema to get free validation and serialisation.
- Add **type annotations** throughout.
- Separate concerns: create a `services/problem_generator.py` that builds and invokes the chain, keeping the route handler thin.

### Performance
- Groq already offers very fast inference; the main bottleneck will be latency. Use `async` LangChain calls (`ainvoke`) to avoid blocking the event loop.
- Cache the `ChatGroq` client — avoid re-initialising it per request (this is what the singleton was meant to do).

### Security
- **Rotate the exposed API key immediately.**
- Add `.env` and `.venv` to `.gitignore`.
- Validate and sanitise `topic` and `difficulty` before injecting into the prompt (allowlist `difficulty` to `["easy", "medium", "hard"]`).
- Add **rate limiting** (e.g., `slowapi`) to prevent API key exhaustion.
- Store secrets via environment injection (Render/Railway secret manager, GitHub Actions secrets) — never commit them.

---

## Missing Features / Next Steps

Prioritised by impact:

| Priority | Feature |
|---|---|
| 🔴 P0 | Rotate the exposed Groq API key |
| 🔴 P0 | Add `.gitignore` (exclude `.env`, `.venv`, `__pycache__`) |
| 🔴 P0 | Fix `UnboundLocalError` bug in `langchainConfig.py` |
| 🔴 P0 | Fix `float()` crash in `server.py` |
| 🔴 P1 | Build the LangChain chain: `problem_prompt \| get_groq_client()` |
| 🔴 P1 | Create an HTTP server (FastAPI recommended) with `POST /generate/problem` |
| 🟡 P2 | Add Pydantic request/response models |
| 🟡 P2 | Add input validation (allowlist `difficulty`, sanitise `topic`) |
| 🟡 P2 | Add error handling (LLM failures, JSON parse errors, API rate limits) |
| 🟡 P2 | Write unit tests (mock the Groq API, test prompt formatting, test response parsing) |
| 🟢 P3 | Dockerise the service |
| 🟢 P3 | Add CI pipeline (lint, type-check, test) |
| 🟢 P3 | Add Redis caching for repeated topic+difficulty pairs |
| 🟢 P3 | Support additional prompt types (e.g., hint generation, solution evaluation) |

---

## Developer Setup Instructions

### Prerequisites

- Python 3.10+
- [`uv`](https://github.com/astral-sh/uv) package manager

### Install

```bash
# Clone the repository
git clone <repo-url>
cd coderX_aiService

# Install dependencies using uv
uv sync
```

### Configure environment

```bash
# Copy and fill in your credentials
cp .env.example .env   # (create .env.example if it doesn't exist)
```

Edit `.env`:

```env
GROQ_API_KEY=gsk_your_actual_key_here
GROQ_TEMPERATURE=0.7
GROQ_MODEL=llama3-70b-8192
```

### Run

```bash
# Currently only runs the stub
uv run python main.py
```

> Once the HTTP server is implemented, this will become `uv run uvicorn main:app --reload`

---

## Example Usage

Once the API server is implemented, the intended usage is:

### Generate a Problem

```bash
curl -X POST http://localhost:8000/generate/problem \
  -H "Content-Type: application/json" \
  -d '{"topic": "binary search", "difficulty": "medium"}'
```

### Expected Response

```json
{
  "title": "Find Peak Element",
  "description": "## Problem Statement\nGiven an array of integers...\n\n## Input Format\n...\n\n## Output Format\n...\n\n## Constraints\n- 1 ≤ n ≤ 10^5\n\n## Example\n**Input:** [1, 2, 3, 1]\n**Output:** 2",
  "difficulty": "medium",
  "testCases": [
    { "input": "[1,2,3,1]", "output": "2" },
    { "input": "[1]", "output": "0" },
    { "input": "[1,2,3,...,100000]", "output": "99999" }
  ],
  "editorial": "Use binary search. At each midpoint, compare mid with mid+1...\nTime: O(log n), Space: O(1)"
}
```

---

*Generated by automated codebase analysis — reflects the state of the repository as of April 2026.*

"""
CoderX AI Service — application entry point.

Start the server:
    uv run uvicorn main:app --reload --port 8000

The FastAPI `app` object is the ASGI callable. Uvicorn discovers it via the
`main:app` import string.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.problem_routes import router
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ── Application ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CoderX AI Service",
    description=(
        "AI-powered coding problem generation with semantic deduplication. "
        "Generates problems via Groq LLM, embeds them with Voyage AI, "
        "and stores / retrieves them from AstraDB."
    ),
    version="0.1.0",
    docs_url="/docs",    # Swagger UI
    redoc_url="/redoc",  # ReDoc UI
)

# ── Middleware ─────────────────────────────────────────────────────────────────
# Allow all origins for local development. Tighten allow_origins in production
# to the specific frontend domain(s).
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────────────────────────────────
app.include_router(router)


# ── Health check ───────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe — returns 200 OK if the service process is running."""
    return {"status": "ok", "service": "coderx-aiservice"}


# ── Dev entrypoint ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn

    logger.info("Starting CoderX AI Service on http://0.0.0.0:8000 ...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

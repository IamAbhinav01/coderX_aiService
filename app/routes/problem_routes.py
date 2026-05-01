"""
FastAPI Router — Problem Generation

Mirrors the Express router pattern from the JS codebase.

Route:
    POST /api/v1/generate/inputs

The route handler is a plain `def` (not `async def`) because the service
layer makes synchronous calls to voyageai and astrapy (both are sync SDKs).
FastAPI automatically offloads sync handlers to a thread pool, so the
event loop is never blocked.
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from app.services.question_generator import generate_and_save_problem
from app.errors.base_error import BaseError
from app.utils.logger import get_logger
from app.services.question_generator import prompt_to_inputs

logger = get_logger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Problems"])




class GenerateRequest(BaseModel):
    """
    Pydantic model for the POST /generate/problem request body.
    """
    user_prompt: str

    @field_validator("user_prompt", mode="before")
    @classmethod
    def must_be_non_blank(cls, value: str, info) -> str:
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f'"{info.field_name}" must be a non-empty string.')
        return value.strip()



@router.post(
        "/generate/inputs",
        summary="Parse a raw prompt and generate the corresponding coding problem",
        response_description=(
            "The route parses the raw user prompt into topic and difficulty, "
            "validates the result, then generates or retrieves the problem."
        ),
)
def generate_inputs(body: GenerateRequest):
    try:
        inputs = prompt_to_inputs(body.user_prompt)
        topic = inputs.get("topic")
        difficulty = inputs.get("difficulty")

        if not topic or not difficulty:
            raise BaseError(
                400,
                "Could not extract topic and difficulty from prompt.",
                f"Extracted: {inputs}",
            )

        if topic.strip().lower() == "unknown" or difficulty.strip().lower() == "unknown":
            raise BaseError(
                400,
                "Prompt could not be converted into a valid DSA problem specification.",
                f"Extracted: {{'topic': {topic!r}, 'difficulty': {difficulty!r}}}",
            )

        result = generate_and_save_problem(topic, difficulty)
        return JSONResponse(content=result, status_code=200)

    except BaseError as exc:
        logger.warning(f"[Route] BaseError {exc.status_code}: {exc.message}")
        return JSONResponse(content=exc.to_dict(), status_code=exc.status_code)

    except Exception as exc:
        logger.error(f"[Route] Unexpected error: {exc}", exc_info=True)
        return JSONResponse(
            content={"error": "An unexpected error occurred.", "detail": str(exc)},
            status_code=500,
        )

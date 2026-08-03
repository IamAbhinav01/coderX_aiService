import sys
import os

# Ensure app directory and root directory are in sys.path
app_dir = os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(app_dir, ".."))
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from config.config import instantiate_env
from config.logger import setup_logger
from config.exception import ApplicationService
from db.pineConeDB import PineConeStore
from llm.GroqInterface import GroqInterface
from services.subprocessRunner import SubProcessRunner
from services.visual_service import HybridVisualConnector
from services.problem_service import ProblemService
from models.model import ProblemRequest

logger = setup_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = instantiate_env()
    logger.info("Initializing Pinecone Vector Store...")
    vector_store = PineConeStore(
        api_key=settings.PINECONE_API_KEY,
        index_name=settings.PINECONE_INDEX_NAME,
        namespace=settings.PINECONE_NAMESPACE
    )
    vector_store.initialize_index()
    
    llm_provider = GroqInterface(settings=settings)
    code_runner = SubProcessRunner()
    visual_service = HybridVisualConnector(settings=settings)
    
    app.state.problem_service = ProblemService(
        vector_store=vector_store,
        llm_provider=llm_provider,
        code_runner=code_runner,
        visual_service=visual_service
    )
    
    yield
    logger.info("Application shutting down cleanly...")

app = FastAPI(
    title="CoderX AI Service API",
    description="Generate dynamic, fully verified coding challenges with reference solutions and test cases.",
    version="1.0.0",
    lifespan=lifespan
)

# Create static dir if it doesn't exist
os.makedirs(os.path.join(app_dir, "static"), exist_ok=True)
app.mount("/static", StaticFiles(directory=os.path.join(app_dir, "static")), name="static")

def get_problem_service() -> ProblemService:
    return app.state.problem_service

@app.post("/api/v1/generate-problem", status_code=status.HTTP_200_OK)
def generate_problem(
    body: ProblemRequest,
    service: ProblemService = Depends(get_problem_service)
):
    try:
        payload = service.generate_or_get_cached(body.prompt)
        return JSONResponse(status_code=200, content=payload)
    except ApplicationService as app_err:
        logger.error(f"[API Error] ApplicationService exception: {app_err.message}")
        raise HTTPException(status_code=app_err.statuscode, detail=app_err.message)
    except Exception as e:
        logger.error(f"[API Error] Failed to generate problem: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Pipeline error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status": "ok", "service": "coderX_aiService"}
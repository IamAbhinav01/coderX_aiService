from fastapi import FastAPI,HTTPException,status
import traceback
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field
from services.subprocess_execution import create_aligned_problem

app = FastAPI(
    title="CoderX AI Service API",
    description="Generate dynamic , fully verified coding challenges with refernce solutions and test cases.",
    version="1.0.0",)

class ProblemRequest(BaseModel):
    prompt : str = Field(description="The topic or prompt for generating the problem"
                         )

@app.post("/api/v1/generate-problem",status_code=status.HTTP_202_ACCEPTED)
def generate_problem(body:ProblemRequest):
    try:
        payload = create_aligned_problem(user_prompt=body.prompt)
        return JSONResponse(status_code=200,content=payload)
    except Exception as e:
        print(f"[API Error] Failed to generate problem: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Pipeline error: {str(e)}")

@app.get("/health")
def health_check():
    return {"status":"ok","service":"coderX_aiService"}
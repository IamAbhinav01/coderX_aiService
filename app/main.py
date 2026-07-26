from fastapi import FastAPI,HTTPException,status
from pydantic import BaseModel,Field

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
        payload = 
    except:
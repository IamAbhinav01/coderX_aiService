from pydantic import BaseModel,Field
from typing import Any,Optional,List
from enum import Enum

class Difficulty(str,Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"

class Language(str,Enum):
    Python = "python"
    Java = "java"
    Cpp = "cpp"

class TestCaseInputs(BaseModel):
    input : Any = Field(...,description="The test input case (can be string, number, array, or object)")
    expected_output : Optional[Any] = Field(None, description="Optional expected output for validation alignment")

class CodeSnippet(BaseModel):
    language : Language
    startSnippet: str = Field(..., description="Boilerplate start code (e.g. 'def solve(s: str) -> bool:')")
    midSnippet: Optional[str] = Field("", description="Boilerplate middle template code")
    endSnippet: str = Field(..., description="Closing boilerplate template code")

class DiagramType(str,Enum):
    TREE = "tree"
    GRAPH = "graph"
    GRID = "grid"
    LINKED_LIST = "linked_list"
    ILLUSTRATION = "illustration"
    NONE = "none"

class GeneratedProblemRaw(BaseModel):
    title: str = Field(..., description="A unique and descriptive title of the challenge")
    description: str = Field(..., description="Detailed description in markdown format explaining the task, constraints, and inputs")
    difficulty: Difficulty
    reference_solution: str = Field(..., description="A fully working, optimal Python 3 solution to the problem")
    testCaseInputs: List[TestCaseInputs] = Field(..., description="A list of 3-5 logical input cases to test")
    codeSnippets: List[CodeSnippet] = Field(..., description="Starter templates for standard languages")
    topic: Optional[str] = Field(None, description="Topic tag (e.g., 'Array', 'String')")

    has_visual:Optional[bool] = Field(False)
    diagram_type:Optional[DiagramType] = Field(DiagramType.NONE)
    diagram_code:Optional[str] = Field(None)

    image_prompt : Optional[str] = Field(None,description="Detailed prompt for AI image generation if diagram_type is illustration")

class ProblemRequest(BaseModel):
    prompt:str = Field(...,description="User prompt or topic for problem generation")

class GeneratedResponse(BaseModel):
    title:str
    description:str
    difficulty:str
    testCases:List[dict]
    codeSnippets:List[dict]
    editorial:str
    topic:Optional[str] = None
    imageUrl:Optional[str] = None
    cache_hit:bool = Field(False,alias="_cache_hit")
    similarity_score:Optional[float] = Field(None,alias="_similarity")
from db.pineConeDB import PineConeStore
from llm.GroqInterface import GroqInterface
from services.subprocessRunner import SubProcessRunner
from services.visual_service import HybridVisualConnector
from config.config import instantiate_env
from config.logger import setup_logger
from typing import Dict, Any

logger = setup_logger()

class ProblemService:
    def __init__(
        self,
        vector_store: PineConeStore,
        llm_provider: GroqInterface,
        code_runner: SubProcessRunner,
        visual_service: HybridVisualConnector
    ):
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.code_runner = code_runner
        self.visual_service = visual_service

    def generate_or_get_cached(self, user_prompt: str) -> Dict[str, Any]:
        # 1. Search Vector Cache
        cached_payload = self.vector_store.search_cache(user_prompt)
        if cached_payload:
            cached_payload["_cache_hit"] = True
            return cached_payload

        # 2. Generate Problem via LLM
        raw_problem = self.llm_provider.GenerateProbelm(user_prompt)

        # 3. Verify Reference Solution with Subprocess Execution
        validated_test_cases = self.code_runner.verify_and_execute(raw_problem)

        # 4. Generate Visual Asset / Diagram Payload
        visual_payload = self.visual_service.generate_visual_url(
            has_visual=raw_problem.has_visual,
            diagram_type=raw_problem.diagram_type,
            diagram_code=raw_problem.diagram_code,
            image_prompt=raw_problem.image_prompt
        )

        # 5. Construct Final Payload
        final_payload = {
            "title": raw_problem.title,
            "description": raw_problem.description,
            "difficulty": raw_problem.difficulty.value,
            "imageUrl": visual_payload.url,
            "visual": visual_payload.model_dump(),
            "testCases": validated_test_cases,
            "codeSnippets": [
                {
                    "language": snippet.language.value,
                    "startSnippet": snippet.startSnippet,
                    "midSnippet": snippet.midSnippet,
                    "endSnippet": snippet.endSnippet
                } for snippet in raw_problem.codeSnippets
            ],
            "editorial": f"### Optimal Solution Walkthrough\n\n```python\n{raw_problem.reference_solution}\n```",
            "topic": raw_problem.topic,
            "_cache_hit": False
        }

        # 6. Save in Vector Database
        self.vector_store.save_cache(user_prompt, final_payload)

        return final_payload

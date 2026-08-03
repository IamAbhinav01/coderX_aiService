from interfaces.llmInterface import InterfaceLLMGroq
from models.model import GeneratedProblemRaw
from config.config import Settings
from typing import Optional
from config.exception import GroqGenerationException
from prompts.generationPrompt import prompt as SYSTEM_PROMPT
from config.logger import setup_logger
import re,json,groq,subprocess,sys

logger = setup_logger()

class GroqInterface(InterfaceLLMGroq):

    def __init__(self,settings:Settings):
        self.settings = settings
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.models_to_try = [
            settings.GROQ_MODEL,
            "llama-3.3-70b-versatile",
            "llama-3.1-8b-instant",
        ]

    def _clean_code(self,code:str)->str:
        code = code.strip()
        code = re.sub(r"^```(?:python|py)?\s*", "", code)
        code = re.sub(r"\s*```$", "", code)

        if (code.startswith("'''") and code.endswith("'''")) or (code.startswith('"""') and code.endswith('"""')):
            code = code[3:-3].strip()
        return code.strip()
    
    def _verify_solution_internal(self,raw_problem:GeneratedProblemRaw) -> Optional[str]:
        outputs  = set()
        inputs_seen = set()
        multi_ele_cases = 0
        total_arr_params = 0

        for index,case in enumerate(raw_problem.testCaseInputs):
            norm_input = json.dumps(case.input, sort_keys=True) if not isinstance(case.input, str) else case.input
            if norm_input in inputs_seen:
                return f"Test Case {index + 1} input is an exact duplicate of a previous test case input. Every test case MUST have a distinct input."
            inputs_seen.add(norm_input)

            inp = case.input
            if isinstance(inp,dict):
                for k,v in inp.items():
                    if isinstance(v,list):
                        total_arr_params += 1
                        if len(v) >= 2:
                            multi_ele_cases += 1
                        elif len(v) == 1 and isinstance(v[0], int) and v[0] > 9:
                            return f"Test Case {index + 1} parameter '{k}' contains a concatenated single number [{v[0]}] instead of a multi-element array like [1, 4, 3, 2, 5, 2]."
            elif isinstance(inp,list):
                total_arr_params += 1
                if len(inp) >= 2:
                    multi_ele_cases += 1
                elif len(inp) == 1 and isinstance(inp[0], int) and inp[0] > 9:
                    return f"Test Case {index + 1} contains a concatenated single number [{inp[0]}] instead of a multi-element array like [1, 4, 3, 2, 5, 2]."

            input_str = json.dumps(case.input) if not isinstance(case.input,str) else case.input
            try:
                process = subprocess.Popen(
                    [sys.executable, "-c", self._clean_code(raw_problem.reference_solution)],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout,stderr = process.communicate(input_str,timeout=3.0)

                if process.returncode != 0:
                    return f"Test Case {index + 1} execution failed : {stderr.strip()}"
                actual_res = json.loads(stdout.strip())

                if case.expected_output is not None:
                    if json.dumps(actual_res,sort_keys=True) != json.dumps(case.expected_output,sort_keys=True):
                        return f"Test Case {index + 1} output ({actual_res}) != expected ({case.expected_output})"

                outputs.add(stdout.strip())

            except subprocess.TimeoutExpired:
                process.kill()
                return f"Test Case {index + 1} timed out (3.0s)."
            except Exception as e:
                return f"Test Case {index + 1} error: {e}"

        if total_arr_params > 0 and len(raw_problem.testCaseInputs) >= 3 and multi_ele_cases < 2:
            return "Array test cases require multi-element lists with 3 to 6 numbers."

        if len(raw_problem.testCaseInputs) >= 3 and  len(outputs) < 2:
            return "Test Cases lack output diversity."
        return None
    
    def GenerateProbelm(self, prompt:str)->GeneratedProblemRaw:
        system_instruction = SYSTEM_PROMPT

        max_retries = 5
        last_feedback = None

        for attempt in range(max_retries):
            # Construct concise messages list to stay under token-per-minute (TPM) limits
            current_messages = [
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
            if last_feedback:
                current_messages.append({
                    "role": "user",
                    "content": f"Previous Attempt Verification Error:\n{last_feedback}\nPlease output a corrected, complete JSON problem object matching the schema."
                })

            response = None
            for current_model in self.models_to_try:
                try:
                    response = self.client.chat.completions.create(
                        model=current_model,
                        temperature=self.settings.TEMPERATURE,
                        max_tokens=self.settings.GROQ_MAX_TOKENS,
                        messages=current_messages,
                        response_format={"type": "json_object"}
                    )
                    break
                except groq.RateLimitError:
                    logger.warning(f"Model '{current_model}' hit rate limit. Trying fallback ...")
                    continue
                except Exception as e:
                    logger.error(f"Error with model {current_model} : {e}")
                    continue

            if response is None:
                raise GroqGenerationException("All Groq models failed or rate-limited.")
            
            raw_content = response.choices[0].message.content or "{}"
            try:
                raw_json = json.loads(raw_content)
                raw_problem = GeneratedProblemRaw.model_validate(raw_json)
                raw_problem.reference_solution = self._clean_code(raw_problem.reference_solution)
            except Exception as parse_err:
                if attempt == (max_retries - 1):
                    raise GroqGenerationException(f"Failed JSON schema validation: {parse_err}")
                last_feedback = f"Invalid JSON schema: {parse_err}"
                continue

            validation_err = self._verify_solution_internal(raw_problem)
            if validation_err is None:
                logger.info(f"Successfully generated and verified problem: {raw_problem.title}")
                return raw_problem

            logger.warning(f"[Attempt {attempt + 1}] Verification failed: {validation_err}. Retrying...")
            last_feedback = (
                f"Error Details: {validation_err}\n"
                f"CRITICAL INSTRUCTIONS:\n"
                f"1. IF DUPLICATE INPUT ERROR: Every test case in `testCaseInputs` MUST have a unique, distinct input structure!\n"
                f"2. IF ARRAY ERROR: Update `testCaseInputs` array values to 3-6 distinct elements.\n"
                f"3. IF EXECUTION ERROR: Ensure reference_solution reads JSON from sys.stdin.read(), calls build_input(), and prints ONLY valid JSON via print(json.dumps(output))."
            )

        raise GroqGenerationException("Failed to generate a valid problem after maximum retries.")
    
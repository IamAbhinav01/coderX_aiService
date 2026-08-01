from interfaces.llmInterface import InterfaceLLMGroq
from models.model import GeneratedProblemRaw
from config.config import Settings
from typing import Optional
from config.logger import setup_logger
import re,json,groq,subprocess,sys

logger = setup_logger()

class GroqInterface(InterfaceLLMGroq):

    def __init__(self,settings:Settings):
        self.settings = settings
        self.client = groq.Groq(api_key=settings.GROQ_API_KEY)
        self.models_to_try = [
            settings.GROQ_MODEL,
            "llama-3.1-8b-instant",
            "openai/gpt-oss-20b",
            "llama-3.1-8b-instant",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "mixtral-8x7b-32768"
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
        multi_ele_cases = 0
        total_arr_params = 0

        for index,case in enumerate(raw_problem.testCaseInputs):
            inp = case.input
            if isinstance(inp,dict):
                for k,v in inp.items():
                    if isinstance(v,list):
                        total_arr_params += 1
                        if len(v) >= 2:
                            multi_ele_cases += 1

            elif isinstance(inp,list):
                total_arr_params += 1
                if len(inp) >= 2:
                    multi_ele_cases += 1
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
    
    # def GenerateProbelm(self, prompt:str)->GeneratedProblemRaw:
    #     messages = [
    #         {
    #             "role":"system","content":
    #         }
    #     ]
    
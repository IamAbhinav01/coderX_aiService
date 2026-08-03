from models.model import GeneratedProblemRaw
from interfaces.runnerInterface import InterfaceRunner
from typing import Optional,Any,List
from config.logger import setup_logger
import json,subprocess,sys

logger = setup_logger()

class SubProcessRunner(InterfaceRunner):
    def verify_and_execute(self, raw_problem:GeneratedProblemRaw)->List[str,Any]:
        validated_cases = []

        for case in raw_problem.testCaseInputs:
            input_str = json.dumps(case.input) if not isinstance(case.input,str) else case.input
            try:
                process = subprocess.Popen(
                    [sys.executable, "-c", raw_problem.reference_solution],
                                    stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True
                )
                stdout,stderr = process.communicate(input_str,timeout=2.5)
                output = stdout.strip() if stdout else ""
                if process.returncode == 0 and output:
                    validated_cases.append({
                        "input":input_str,
                        "output":output
                    })
            except Exception as e:
                logger.error(f"Subprocess runner error: {e}")
                if 'process' in locals() and process.poll() is None:
                    process.kill()
                continue
        return validated_cases
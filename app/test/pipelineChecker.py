import sys
import os
# This dynamically tells Python to look inside the parent 'app' directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))




import traceback

from services.groq_service import generate_problem
from services.subprocess_execution import (
    create_aligned_problem,
    test_cases_output
)


def run_evaluation(user_prompt: str):
    try:
        print("\n" + "=" * 80)
        print("EXECUTING PIPELINE")
        print("=" * 80)

        # Step 1: Generate and validate problem using Groq
        print("\n[Step 1] Requesting problem from Groq...")

        raw_problem = generate_problem(user_prompt)

        print("Model validated successfully against Pydantic schema.")

        # Step 2: Execute reference solution
        print("\n[Step 2] Executing reference solution...")

        test_cases = test_cases_output(raw_problem)

        print("Reference solution executed without errors.")

        # Step 3: Create final aligned payload
        print("\n[Step 3] Creating aligned problem payload...")

        final_payload = create_aligned_problem(user_prompt)

        print("\n" + "=" * 80)
        print("ALIGNMENT INSPECTION")
        print("=" * 80)

        print(f"\nTITLE      : {final_payload['title']}")
        print(f"TOPIC      : {final_payload['topic']}")
        print(f"DIFFICULTY : {final_payload['difficulty']}")

        print("\nDESCRIPTION:")
        print("-" * 40)

        print(final_payload["description"])

        print("-" * 40)

        print("\nTEST CASES:")

        for index, test_case in enumerate(final_payload["testCases"]):

            print(f"\nCase {index + 1}:")
            print(f"Input  : {test_case['input']}")
            print(f"Output : {test_case['output']}")

        print("\nCODE SNIPPETS:")

        for snippet in final_payload["codeSnippets"]:

            print(f"\nLanguage: {snippet['language']}")
            print(f"Starter Code:\n{snippet['startSnippet']}")

        print("\nEDITORIAL / REFERENCE SOLUTION:")

        print(final_payload["editorial"])

        print("\n" + "=" * 80)
        print("INTEGRITY CHECKS")
        print("=" * 80)

        assertions_passed = True

        # Check whether the number of test cases matches the input cases
        if len(final_payload["testCases"]) == len(raw_problem.testCaseInputs):

            print("[PASS] Test case count matches input count.")

        else:

            print("[FAIL] Test case count mismatch.")
            assertions_passed = False

        # Check for empty outputs
        for index, test_case in enumerate(final_payload["testCases"]):

            output = test_case["output"]

            if not output or output.strip() == "":
                print(
                    f"[FAIL] Test case {index + 1} has an empty output."
                )

                assertions_passed = False

        # Check reference solution syntax
        try:

            compile(
                raw_problem.reference_solution,
                "<reference_solution>",
                "exec"
            )

            print("[PASS] Reference solution syntax is valid.")

        except SyntaxError as error:

            print(
                f"[FAIL] Reference solution syntax error: {error}"
            )

            assertions_passed = False

        if assertions_passed:

            print(
                "\nALL ALIGNMENT AND INTEGRITY CHECKS PASSED!"
            )

        else:

            print(
                "\nSOME INTEGRITY CHECKS FAILED!"
            )

    except Exception as error:

        print("\nPIPELINE EXECUTION FAILED")
        print(f"Error: {error}")

        traceback.print_exc()


if __name__ == "__main__":

    user_prompt = "cycle detection in linke list"

    run_evaluation(user_prompt)
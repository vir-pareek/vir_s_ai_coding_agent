from langchain_google_genai import ChatGoogleGenerativeAI
from utils.api_utils import retry_with_backoff


class TesterAgent:
    """Agent responsible for generating small test cases from problem statement."""

    def __init__(self, model_name: str):
        # Parse model name (format: "google:model-name")
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name

        # Remove 'models/' prefix if present - LangChain adds it automatically
        if model.startswith("models/"):
            model = model.replace("models/", "")

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.2)  # Lowered to reduce hallucination
        self.system_prompt = """You are a test case generation expert for programming problems.

Your task is to generate test cases that adhere to the input format specified in the problem statement.

MODES:
1. **Small Tests**: Simple cases to verify correctness (default).
2. **Stress Tests**: LARGE inputs to check performance (N up to 10^5 or 10^6).

Guidelines for Stress Tests:
- Generate inputs close to the maximum constraints.
- Use random large numbers, large arrays, or deep trees.
- Ensure the format is EXACTLY as described.
- Output ONLY the test input data.

Example format for multiple test cases (WITH T header for Hacker Cup format):
6
3
1 2 3
2
5 10
1
42

IMPORTANT: For Hacker Cup problems, ALWAYS start with T (number of test cases) on the first line, then T groups of test cases.

CRITICAL: Output ONLY the raw test input data above, nothing else!
"""

    @retry_with_backoff(max_retries=5)
    def generate_test_cases(self, problem_statement: str) -> str:
        """Generate small test cases for the given problem statement."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Generate 5 small, diverse test cases for this problem:\n\n{problem_statement}"}
        ]

        response = self.model.invoke(messages)
        return self._clean_response(response.content)

    @retry_with_backoff(max_retries=5)
    def generate_stress_test(self, problem_statement: str) -> str:
        """Generate a large stress test case."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Generate 1 LARGE stress test case (N close to max constraints) for this problem:\n\n{problem_statement}\n\nMake sure it follows the input format exactly. Start with T=1."}
        ]

        response = self.model.invoke(messages)
        return self._clean_response(response.content)

    def _clean_response(self, content: str) -> str:
        """Clean and format the model response."""
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith("```"):
            lines = content.split("\n")
            # Remove first and last lines if they are markdown markers
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        # Ensure T header is present (number of test cases)
        lines = content.split('\n')
        if lines and not lines[0].strip().isdigit():
            # No T header - try to infer it
            # Look for patterns: count non-empty lines that look like test data
            non_empty_lines = [l for l in lines if l.strip()]
            if non_empty_lines:
                # Heuristic: if first line looks like a number (could be N), count groups
                # This is problem-specific, so we'll use a simple heuristic
                # For most problems: T test cases, each with some structure
                # Try to count by looking for patterns
                test_count = max(1, len(non_empty_lines) // 2)  # Conservative estimate
            else:
                test_count = 1
            
            content = str(test_count) + "\n" + content
        
        # Validate: ensure T is a positive integer
        lines = content.split('\n')
        if lines and lines[0].strip().isdigit():
            t_val = int(lines[0].strip())
            if t_val <= 0:
                # Invalid T, set to 1
                lines[0] = "1"
                content = "\n".join(lines)
        
        return content

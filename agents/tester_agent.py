from langchain_google_genai import ChatGoogleGenerativeAI


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

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.7)
        self.system_prompt = """You are a test case generation expert for programming problems.

Your task is to generate SMALL, simple test cases that adhere to the input format specified in the problem statement.

Guidelines:
- Generate 3-5 small test cases
- Follow the exact input format specified
- Use small values (arrays of size 2-5, numbers < 100, etc.)
- Cover edge cases (empty, single element, boundary values)
- Output ONLY the test input, nothing else - NO markdown, NO code blocks, NO explanations
- Each test case should be separated by a blank line if multiple cases
- DO NOT wrap output in ``` markers or any other formatting

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

    def generate_test_cases(self, problem_statement: str) -> str:
        """Generate test cases for the given problem statement."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Generate small test cases for this problem:\n\n{problem_statement}"}
        ]

        response = self.model.invoke(messages)
        content = response.content.strip()

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
        # Count the number of test cases in the generated content
        lines = content.split('\n')
        if lines and not lines[0].strip().isdigit():
            # No T header - add it
            # Count test cases: each test case has 2 lines (N and S)
            test_count = sum(1 for line in lines if line.strip() and len(line.strip()) > 0 and not line.strip()[0].isdigit()) // 2
            if test_count == 0:
                # Try to count differently - look for patterns
                test_count = (len([l for l in lines if l.strip()]) + 1) // 2
            
            content = str(test_count) + "\n" + content
        elif lines and lines[0].strip().isdigit():
            # T header exists, but validate count matches content
            first_line = lines[0].strip()
            # This is fine, keep as is
            pass

        return content

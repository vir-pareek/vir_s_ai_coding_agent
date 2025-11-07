from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, List
import concurrent.futures


class OptimalAgent:
    """Agent responsible for generating optimal/efficient solutions."""

    def __init__(self, model_name: str, num_candidates: int = 3):
        # Parse model name (format: "google:model-name")
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name

        # Remove 'models/' prefix if present - LangChain adds it automatically
        if model.startswith("models/"):
            model = model.replace("models/", "")

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.5)
        self.num_candidates = num_candidates
        self.base_system_prompt = """You are an expert competitive programmer.

Your task is to generate an EFFICIENT solution in Python that meets the time/space constraints.

Guidelines:
- Optimize for the given constraints in the problem
- Use efficient algorithms and data structures
- Aim for optimal time and space complexity
- Read input from stdin, write output to stdout
- Handle the exact input/output format specified
- Include proper input parsing
- The solution must be CORRECT (passing all test cases)
- No unnecessary comments or explanations in code
- Make sure the solution is complete and runnable

Output ONLY the Python code, no markdown, no explanations.
"""

    def _build_system_prompt(self, hints: str = None) -> str:
        """Build system prompt with optional hints."""
        prompt = self.base_system_prompt
        if hints:
            prompt += f"\n\n=== PROBLEM-SPECIFIC HINTS ===\n{hints}\n\nUse these hints to write an optimal solution with the specified complexity."
        return prompt

    def generate_solution(self, problem_statement: str, feedback: Optional[str] = None, attempt: int = 1, hints: str = None) -> str:
        """Generate optimal solution for the given problem.
        
        Args:
            problem_statement: The problem description
            feedback: Optional feedback from previous attempt
            attempt: Current attempt number
            hints: Optional problem-specific hints (algorithm type, complexity, etc.)
        """
        system_prompt = self._build_system_prompt(hints)
        
        user_message = f"Generate an optimal Python solution for this problem:\n\n{problem_statement}"

        if feedback:
            user_message += f"\n\n=== FEEDBACK FROM ATTEMPT {attempt - 1} ===\n{feedback}\n\nPlease fix the issues and generate a corrected solution."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        code = response.content.strip()

        # Remove markdown code blocks if present
        if code.startswith("```python"):
            code = code.split("```python")[1].split("```")[0].strip()
        elif code.startswith("```"):
            code = code.split("```")[1].split("```")[0].strip()

        return code
    
    def generate_solution_with_approach(self, problem_statement: str, approach: str, hints: str = None) -> str:
        """Generate optimal solution with a specific algorithmic approach.
        
        Args:
            problem_statement: The problem description
            approach: Specific approach to use (e.g., 'Dynamic Programming', 'Greedy', 'Binary Search')
            hints: Optional problem-specific hints
        """
        # Build approach-specific prompt
        approach_prompt = self._build_system_prompt(hints)
        approach_prompt += f"\n\n=== REQUIRED APPROACH ===\nUse a {approach} approach to solve this problem."
        
        user_message = f"Generate an optimal Python solution using {approach} approach for this problem:\n\n{problem_statement}"

        messages = [
            {"role": "system", "content": approach_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        code = response.content.strip()

        # Remove markdown code blocks if present
        if code.startswith("```python"):
            code = code.split("```python")[1].split("```")[0].strip()
        elif code.startswith("```"):
            code = code.split("```")[1].split("```")[0].strip()

        return code
    
    def generate_parallel_solutions(self, problem_statement: str, approaches: List[str], hints: str = None) -> List[dict]:
        """Generate multiple optimal solutions in parallel using different approaches.
        
        Args:
            problem_statement: The problem description
            approaches: List of approaches to try (e.g., ['Dynamic Programming', 'Greedy'])
            hints: Optional problem-specific hints
            
        Returns:
            List of solution dictionaries with 'code', 'approach', and 'number' fields
        """
        solutions = []
        
        def generate_one(index: int, approach: str):
            """Helper to generate one solution."""
            try:
                code = self.generate_solution_with_approach(problem_statement, approach, hints)
                return {
                    'number': index + 1,
                    'approach': approach,
                    'code': code
                }
            except Exception as e:
                return {
                    'number': index + 1,
                    'approach': approach,
                    'code': '',
                    'error': str(e)
                }
        
        # Generate solutions in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(approaches)) as executor:
            futures = [executor.submit(generate_one, i, approach) for i, approach in enumerate(approaches)]
            
            for future in concurrent.futures.as_completed(futures):
                solutions.append(future.result())
        
        # Sort by number to maintain order
        solutions.sort(key=lambda x: x['number'])
        
        return solutions

from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List


class BruteAgent:
    """Agent responsible for generating brute force solutions."""

    def __init__(self, model_name: str, num_candidates: int = 3):
        # Parse model name (format: "google:model-name")
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name

        # Remove 'models/' prefix if present - LangChain adds it automatically
        if model.startswith("models/"):
            model = model.replace("models/", "")

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.7)  # Higher temp for diversity
        self.num_candidates = num_candidates
        self.base_system_prompt = """You are a brute force algorithm expert.

Your task is to generate a SIMPLE, CORRECT brute force solution in Python.

Guidelines:
- Prioritize CORRECTNESS over efficiency
- Use simple, straightforward approaches (nested loops, recursion, etc.)
- Don't worry about time/space complexity
- Read input from stdin, write output to stdout
- Handle the exact input/output format specified
- Include proper input parsing
- No unnecessary comments or explanations in code
- Make sure the solution is complete and runnable
- Consider alternative approaches (iterative vs recursive, different loop structures)

Output ONLY the Python code, no markdown, no explanations.
"""

    def _build_system_prompt(self, hints: str = None) -> str:
        """Build system prompt with optional hints."""
        prompt = self.base_system_prompt
        if hints:
            prompt += f"\n\n=== PROBLEM-SPECIFIC HINTS ===\n{hints}\n\nConsider these hints when writing your solution."
        return prompt

    def generate_solution(self, problem_statement: str, hints: str = None) -> str:
        """Generate brute force solution for the given problem.
        
        Args:
            problem_statement: The problem description
            hints: Optional problem-specific hints (algorithm type, complexity, etc.)
        """
        system_prompt = self._build_system_prompt(hints)
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Generate a brute force Python solution for this problem:\n\n{problem_statement}"}
        ]

        response = self.model.invoke(messages)
        code = response.content.strip()

        # Remove markdown code blocks if present
        if code.startswith("```python"):
            code = code.split("```python")[1].split("```")[0].strip()
        elif code.startswith("```"):
            code = code.split("```")[1].split("```")[0].strip()

        return code
    
    def generate_multiple_solutions(self, problem_statement: str, hints: str = None) -> List[dict]:
        """Generate multiple brute force solution candidates.
        
        Args:
            problem_statement: The problem description
            hints: Optional problem-specific hints
            
        Returns:
            List of solution dictionaries with 'code', 'approach', and 'number' fields
        """
        solutions = []
        
        for i in range(self.num_candidates):
            system_prompt = self._build_system_prompt(hints)
            
            # Add variation to prompt to get different approaches
            variation_prompt = system_prompt
            if i > 0:
                variation_prompt += f"\n\nTry a DIFFERENT approach than previous attempts. Consider alternative implementation styles."
            
            messages = [
                {"role": "system", "content": variation_prompt},
                {"role": "user", "content": f"Generate brute force Python solution #{i+1} for this problem:\n\n{problem_statement}"}
            ]

            response = self.model.invoke(messages)
            code = response.content.strip()

            # Remove markdown code blocks if present
            if code.startswith("```python"):
                code = code.split("```python")[1].split("```")[0].strip()
            elif code.startswith("```"):
                code = code.split("```")[1].split("```")[0].strip()
            
            solutions.append({
                'number': i + 1,
                'code': code,
                'approach': f'Brute force approach #{i+1}'
            })
        
        return solutions

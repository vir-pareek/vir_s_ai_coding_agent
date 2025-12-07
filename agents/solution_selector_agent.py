from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict, Optional
from .complexity_agent import ComplexityAgent


class SolutionSelectorAgent:
    """Agent responsible for selecting the best solution from multiple candidates."""
    
    def __init__(self, model_name: str, complexity_agent: Optional[ComplexityAgent] = None):
        # Parse model name
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name
        
        if model.startswith("models/"):
            model = model.replace("models/", "")
        
        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.1)
        self.complexity_agent = complexity_agent
        self.system_prompt = """You are an expert solution selector for competitive programming.

Your task is to analyze multiple solution candidates and select the BEST one based on:
1. **Correctness**: Does it solve the problem correctly?
2. **Time Complexity**: Will it pass time limits? (O(N²) for N>10^4 will TLE)
3. **Code Quality**: Is it clean, readable, and maintainable?
4. **Edge Case Handling**: Does it handle all edge cases?

SELECTION CRITERIA (in priority order):
1. CORRECTNESS is most important - a correct solution is better than a fast wrong one
2. TIME COMPLEXITY must be acceptable for the constraints
3. Code should be clean and efficient
4. Should handle edge cases properly

OUTPUT FORMAT:
Return the solution NUMBER (1-10) that is the best, followed by a brief explanation of why.
Format: "SELECT: <number>\nREASON: <explanation>"
"""

    def select_best_solution(self, solutions: List[Dict], problem_statement: str, 
                            problem_constraints: Optional[Dict] = None) -> Dict:
        """
        Select the best solution from multiple candidates.
        
        Args:
            solutions: List of solution dictionaries with 'code', 'number', 'temperature'
            problem_statement: Problem description
            problem_constraints: Problem constraints for complexity checking
            
        Returns:
            Dictionary with 'selected_solution', 'reason', 'complexity_check'
        """
        if not solutions:
            return {'selected_solution': None, 'reason': 'No solutions provided', 'complexity_check': None}
        
        # Filter out solutions with errors
        valid_solutions = [s for s in solutions if s.get('code') and not s.get('error')]
        
        if not valid_solutions:
            return {'selected_solution': None, 'reason': 'No valid solutions', 'complexity_check': None}
        
        # Analyze each solution
        analyzed_solutions = []
        
        for solution in valid_solutions:
            code = solution.get('code', '')
            number = solution.get('number', 0)
            temperature = solution.get('temperature', 0.0)
            
            # Check complexity if complexity_agent is available
            complexity_check = None
            if self.complexity_agent and problem_constraints:
                try:
                    complexity_check = self.complexity_agent.analyze_complexity(code, problem_constraints)
                except:
                    pass
            
            analyzed_solutions.append({
                'number': number,
                'code': code,
                'temperature': temperature,
                'complexity_check': complexity_check,
                'code_length': len(code),
                'has_fast_io': 'sys.stdin.read().split()' in code or 'sys.stdin.read()' in code
            })
        
        # Use LLM to select best solution
        solutions_summary = []
        for sol in analyzed_solutions:
            summary = f"Solution #{sol['number']} (temp={sol['temperature']}):\n"
            summary += f"- Code length: {sol['code_length']} chars\n"
            summary += f"- Fast I/O: {sol['has_fast_io']}\n"
            if sol['complexity_check']:
                summary += f"- Time Complexity: {sol['complexity_check'].get('time_complexity', 'Unknown')}\n"
                summary += f"- Meets Constraints: {sol['complexity_check'].get('meets_constraints', 'Unknown')}\n"
            summary += f"- Code preview: {sol['code'][:200]}...\n"
            solutions_summary.append(summary)
        
        user_message = f"""Select the BEST solution from these candidates for this problem:

Problem:
{problem_statement[:1000]}

Solutions:
{chr(10).join(solutions_summary)}

Constraints:
{problem_constraints if problem_constraints else 'Not provided'}

Analyze each solution and select the one that:
1. Is most likely to be CORRECT
2. Has acceptable time complexity (won't TLE)
3. Is well-structured and handles edge cases

Return: SELECT: <number> followed by REASON: <explanation>"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]
        
        try:
            response = self.model.invoke(messages)
            content = response.content.strip()
            
            # Parse response
            selected_number = None
            reason = ""
            
            # Extract number
            import re
            select_match = re.search(r'SELECT:\s*(\d+)', content, re.IGNORECASE)
            if select_match:
                selected_number = int(select_match.group(1))
            
            # Extract reason
            reason_match = re.search(r'REASON:\s*(.+?)(?:\n|$)', content, re.IGNORECASE | re.DOTALL)
            if reason_match:
                reason = reason_match.group(1).strip()
            
            # Find the selected solution
            selected_solution = None
            for sol in analyzed_solutions:
                if sol['number'] == selected_number:
                    selected_solution = sol
                    break
            
            # Fallback: if LLM selection failed, use first valid solution
            if not selected_solution:
                selected_solution = analyzed_solutions[0]
                selected_number = selected_solution['number']
                reason = "LLM selection failed, using first valid solution"
            
            return {
                'selected_solution': selected_solution,
                'selected_number': selected_number,
                'reason': reason,
                'complexity_check': selected_solution.get('complexity_check'),
                'all_analyzed': analyzed_solutions
            }
        except Exception as e:
            # Fallback: return first valid solution
            return {
                'selected_solution': analyzed_solutions[0] if analyzed_solutions else None,
                'selected_number': analyzed_solutions[0]['number'] if analyzed_solutions else None,
                'reason': f'Selection failed: {str(e)}, using first valid solution',
                'complexity_check': analyzed_solutions[0].get('complexity_check') if analyzed_solutions else None,
                'all_analyzed': analyzed_solutions
            }


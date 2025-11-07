from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List, Dict


class WebSearchAgent:
    """Agent responsible for searching and learning algorithm approaches on the fly."""

    def __init__(self, model_name: str):
        # Parse model name (format: "google:model-name")
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name

        # Remove 'models/' prefix if present - LangChain adds it automatically
        if model.startswith("models/"):
            model = model.replace("models/", "")

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.5)
        self.system_prompt = """You are an expert algorithm researcher who helps find optimal algorithmic approaches for competitive programming problems.

Your task is to:
1. Analyze the problem statement
2. Identify key algorithmic techniques needed (Dynamic Programming, Greedy, Graph Algorithms, etc.)
3. Search for relevant algorithm knowledge and problem-solving strategies
4. Provide concise, actionable insights about the best algorithmic approach

You should focus on:
- Time and space complexity constraints from the problem
- Identifying which algorithm paradigms apply (DP, greedy, graph traversal, sorting, etc.)
- Suggesting specific data structures that might be helpful
- Providing complexity targets for the solution

Output your findings in a structured format with:
- Algorithm Type (e.g., Dynamic Programming, Greedy, Graph BFS/DFS, etc.)
- Suggested Approach
- Key Insight
- Complexity Target (e.g., O(n) time, O(1) space)
"""

    def search_algorithm(self, problem_statement: str) -> str:
        """Search for algorithm approaches based on problem description."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Analyze this problem and suggest the best algorithmic approach:\n\n{problem_statement}"}
        ]

        response = self.model.invoke(messages)
        return response.content.strip()

    def extract_hints(self, problem_statement: str, search_results: str = None) -> Dict[str, str]:
        """
        Extract algorithmic hints from problem statement and search results.
        
        Returns a dictionary with:
        - algorithm_type: Main algorithm approach (e.g., "Dynamic Programming", "Greedy")
        - key_insight: Important insight about the problem
        - complexity_target: Target time/space complexity
        - data_structures: Suggested data structures
        """
        system_prompt = """You are a competitive programming expert. Analyze the problem and extract key algorithmic hints.

Based on the problem statement, identify:
1. The main algorithmic approach needed (Dynamic Programming, Greedy, Graph Algorithms, etc.)
2. Key insight or pattern in the problem
3. Target time and space complexity
4. Suggested data structures

Output in a structured way that can be easily parsed.
"""

        user_message = f"Analyze this problem and extract algorithmic hints:\n\n{problem_statement}"
        if search_results:
            user_message += f"\n\nSearch results:\n{search_results}"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        content = response.content.strip()

        # Parse the response into structured hints
        hints = {
            'algorithm_type': 'General',
            'key_insight': '',
            'complexity_target': '',
            'data_structures': ''
        }

        # Try to extract structured information from the response
        lines = content.split('\n')
        current_key = None
        
        for line in lines:
            line = line.strip()
            if ':' in line:
                # Key-value pair
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip().lower()
                    value = parts[1].strip()
                    
                    if 'algorithm' in key or 'approach' in key or 'type' in key:
                        hints['algorithm_type'] = value
                    elif 'insight' in key or 'pattern' in key:
                        hints['key_insight'] = value
                    elif 'complexity' in key or 'target' in key or 'time' in key or 'space' in key:
                        hints['complexity_target'] = value
                    elif 'data structure' in key or 'structure' in key:
                        hints['data_structures'] = value

        return hints

    def get_enhanced_prompt_context(self, problem_statement: str) -> Dict[str, str]:
        """Get enhanced context including algorithm hints and complexity targets."""
        # First, search for algorithm approaches
        search_results = self.search_algorithm(problem_statement)
        
        # Then extract structured hints
        hints = self.extract_hints(problem_statement, search_results)
        
        return hints

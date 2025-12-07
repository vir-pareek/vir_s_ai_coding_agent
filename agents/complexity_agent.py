from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Optional
import re


class ComplexityAgent:
    """Agent responsible for estimating time and space complexity of solutions."""

    def __init__(self, model_name: str):
        # Parse model name (format: "google:model-name")
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name

        # Remove 'models/' prefix if present - LangChain adds it automatically
        if model.startswith("models/"):
            model = model.replace("models/", "")

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.1)  # Very low for strict analysis
        self.system_prompt = """You are a STRICT complexity analyst for competitive programming.

Your task is to ACCURATELY analyze code complexity and STRICTLY determine if it will TLE (Time Limit Exceeded).

CRITICAL TLE RULES (for 1-2 second time limits):

N ≤ 10 or 20:
- O(N!) or O(2^N) is ACCEPTABLE
- O(N²) is ACCEPTABLE

N ≤ 100:
- O(N⁴) is ACCEPTABLE
- O(N³) is ACCEPTABLE
- O(N²) is ACCEPTABLE

N ≤ 500:
- O(N³) is ACCEPTABLE
- O(N²) is ACCEPTABLE
- O(N log N) is ACCEPTABLE

N ≤ 2,000:
- O(N²) is ACCEPTABLE (but risky)
- O(N log N) is SAFE
- O(N) is SAFE

N ≤ 10,000:
- O(N²) is RISKY - may TLE
- O(N sqrt(N)) is ACCEPTABLE
- O(N log N) is SAFE
- O(N) is SAFE

N ≤ 100,000 (10^5):
- O(N²) WILL TLE - REJECT
- O(N log N) is REQUIRED
- O(N) is SAFE

N ≤ 1,000,000 (10^6):
- O(N²) WILL TLE - REJECT
- O(N log N) is REQUIRED (may be tight)
- O(N) is SAFE

N ≥ 10^9:
- O(sqrt(N)) or O(log N) is REQUIRED
- O(N) WILL TLE - REJECT

ANALYSIS PROCESS:
1. Identify all loops and nested structures
2. Count operations inside loops
3. Identify data structure operations (lookup, insertion, etc.)
4. Calculate overall time complexity
5. Compare against constraints
6. Determine TLE risk

COMMON TLE CAUSES:
- Nested loops: for i in range(N): for j in range(N): → O(N²) TLE for N > 10^4
- Building large segment trees: tree = [None] * (4 * MAX_VAL) → TLE if MAX_VAL is large
- Repeated sorting: sorted() in loop → O(N log N) per iteration
- Linear search in loop: .index() or 'in' for list → O(N) per iteration
- Recursion without memoization: repeated subproblems → exponential

OUTPUT FORMAT:
1. **Time Complexity**: Exact Big-O notation (e.g., O(N log N), O(N²))
2. **Space Complexity**: Big-O notation
3. **Verdict**: "PASS" or "FAIL"
   - FAIL if complexity will cause TLE for given constraints
4. **Reason**: Specific explanation
   - If FAIL: Explain what causes TLE and suggest optimization
5. **Bottlenecks**: List specific operations that are slow

Be STRICT. It's better to reject a solution that might TLE than to accept one that will."""

    def analyze_complexity(self, code: str, problem_constraints: Optional[Dict] = None) -> Dict[str, str]:
        """
        Analyze time and space complexity of code.
        
        Args:
            code: The code to analyze
            problem_constraints: Problem constraints (max_n, etc.) to check against
        
        Returns:
            Dictionary with 'time_complexity', 'space_complexity', 'meets_constraints', 'reason', 'bottlenecks'
        """
        # Extract max N from constraints
        max_n_str = "Unknown"
        max_n_val = None
        if problem_constraints:
            max_n_str = str(problem_constraints.get('max_n', 'Unknown'))
            try:
                if '**' in max_n_str or '^' in max_n_str:
                    # Handle 10^5 format
                    parts = max_n_str.replace('**', '^').split('^')
                    if len(parts) == 2:
                        max_n_val = int(parts[0]) ** int(parts[1])
                    else:
                        max_n_val = int(max_n_str.replace('**', '').replace('^', ''))
                else:
                    max_n_val = int(max_n_str.replace(',', ''))
            except:
                pass
        
        user_message = f"""STRICTLY analyze the time and space complexity of this code and determine if it will TLE.

Code:
{code[:3000]}

Problem Constraints:
Max N: {max_n_str}
{problem_constraints if problem_constraints else 'Not provided'}

CRITICAL ANALYSIS REQUIRED:
1. Identify ALL loops and their nesting levels
2. Count operations inside loops
3. Identify data structure operations (lookup, insertion, deletion)
4. Calculate exact time complexity
5. Compare against constraints: Will this TLE?
6. Identify specific bottlenecks

Be STRICT and THOROUGH. If there's ANY doubt about TLE, mark as FAIL."""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        content = response.content.strip()
        
        # Parse response for complexity
        time_complexity = None
        space_complexity = None
        meets_constraints = None
        reason = ""
        bottlenecks = []
        
        # Try to extract Big-O notation
        time_match = re.search(r'O\([^)]+\)', content)
        if time_match:
            time_complexity = time_match.group(0)
        
        space_match = re.search(r'space.*?O\([^)]+\)', content, re.IGNORECASE)
        if space_match:
            space_complexity = space_match.group(0)
        
        # Determine if meets constraints
        verdict_match = re.search(r'(PASS|FAIL)', content, re.IGNORECASE)
        if verdict_match:
            meets_constraints = verdict_match.group(0).upper() == "PASS"
        
        # Extract reason
        reason_match = re.search(r'[Rr]eason[:\s]+(.+?)(?:\n|$)', content, re.MULTILINE)
        if reason_match:
            reason = reason_match.group(1).strip()
        
        # Extract bottlenecks
        bottleneck_lines = [line.strip() for line in content.split('\n') if 'bottleneck' in line.lower() or 'slow' in line.lower()]
        bottlenecks = bottleneck_lines[:3]  # Top 3 bottlenecks
        
        # Additional pattern-based analysis
        if not meets_constraints and max_n_val:
            # Check for obvious TLE patterns
            if 'O(n^2)' in str(time_complexity).lower() or 'O(n²)' in str(time_complexity).lower():
                if max_n_val >= 10000:
                    meets_constraints = False
                    reason = f"O(N²) complexity will TLE for N = {max_n_val}"
                    bottlenecks.append("Nested loops over large range")
        
        return {
            'time_complexity': time_complexity or 'Unknown',
            'space_complexity': space_complexity or 'Unknown',
            'meets_constraints': meets_constraints,
            'reason': reason or content[:200],
            'bottlenecks': bottlenecks,
            'analysis': content
        }

from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, List
import concurrent.futures
import re
from utils.api_utils import retry_with_backoff


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

        # Store model name for later use
        self.model_name = model
        
        # Very low temperature for maximum consistency and to prevent hallucination
        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.0)  # Set to 0.0 for maximum determinism
        self.num_candidates = num_candidates
        self.base_system_prompt = """You are an EXPERT competitive programmer specializing in Meta HackerCup problems. Your solutions MUST be CORRECT and OPTIMAL.

🚫 CRITICAL ANTI-HALLUCINATION RULES:
- DO NOT make assumptions about the problem that aren't explicitly stated
- DO NOT invent constraints or requirements not mentioned in the problem
- DO NOT use algorithms that don't match the problem description
- DO NOT skip reading the problem carefully - read it AT LEAST 3 times
- DO NOT generate code without understanding what the problem asks
- VERIFY your logic matches the sample input/output examples EXACTLY
- If sample examples don't match your logic, YOUR LOGIC IS WRONG - fix it

CRITICAL REQUIREMENTS:
1. Output ONLY valid Python code - nothing else
2. NO markdown formatting, NO code blocks, NO explanations
3. NO text before or after the code
4. Start directly with 'import' or 'def' statements
5. The code must be complete, runnable, and handle stdin/stdout correctly
6. For Meta HackerCup: Use "Case #i: " format for output (e.g., "Case #1: 42")
7. CORRECTNESS IS PARAMOUNT - A correct solution is better than a fast wrong one
8. MUST handle ALL edge cases: N=0, N=1, N=max, empty inputs, boundary values
9. MUST follow EXACT input/output format from problem statement
10. MUST verify your solution logic against sample examples before coding

### STEP-BY-STEP PROBLEM SOLVING PROCESS (INTERNAL - DO NOT OUTPUT):

**STEP 1: READ AND UNDERSTAND THE PROBLEM (CRITICAL - DO THIS 3 TIMES)**
- Read the ENTIRE problem statement word by word - READ IT 3 TIMES
- Identify what is being asked: What is the output? What are we optimizing?
- Understand ALL constraints: N, M, value ranges, time limits
- Identify the problem type: Greedy, DP, Graph, Math, Simulation, etc.
- Check sample input/output examples - they reveal the expected logic
  * TRACE through sample examples manually with your algorithm
  * If your algorithm doesn't produce the sample output, IT IS WRONG
  * DO NOT proceed until your logic matches sample examples
- Identify edge cases mentioned in the problem
- DO NOT assume anything not explicitly stated in the problem

**STEP 2: ANALYZE CONSTRAINTS AND COMPLEXITY REQUIREMENTS**
- Extract maximum values: max_N, max_M, max_value
- Calculate required complexity:
  * N ≤ 10^5 → MUST use O(N log N) or O(N). O(N²) WILL TLE.
  * N ≤ 10^6 → MUST use O(N) or O(N log N). O(N²) WILL TLE.
  * N ≤ 10^3 → O(N²) is acceptable
  * N ≤ 20 → O(2^N) or O(N!) is acceptable
- Identify if fast I/O is needed (large input sizes)
- Check if recursion depth might be an issue

**STEP 3: SELECT THE CORRECT ALGORITHM**
- Match problem type to algorithm:
  * Greedy: Choose locally optimal choice at each step
  * DP: Overlapping subproblems, optimal substructure
  * Graph: BFS/DFS, shortest paths, connectivity
  * Segment Tree/Fenwick Tree: Range queries, point updates
  * Binary Search: Monotonic property, search space reduction
  * Two Pointers: Sorted arrays, sliding window
  * Math: Number theory, combinatorics, geometry
- Verify the algorithm fits the complexity requirements
- Consider alternative approaches if primary approach is too slow

**STEP 4: DESIGN THE SOLUTION**
- Break down into clear steps
- Identify data structures needed (arrays, dicts, heaps, trees, etc.)
- Plan state tracking if needed (DP states, graph nodes, etc.)
- Plan edge case handling
- Verify the logic matches sample examples

**STEP 5: WRITE CORRECT CODE**
- Use fast I/O: `sys.stdin.read().split()` for bulk reading
- Implement the algorithm correctly
- Handle all edge cases explicitly
- Use proper output format: "Case #i: result"
- Add recursion limit if using recursion: `sys.setrecursionlimit(200000)`

**STEP 6: VERIFY CORRECTNESS**
- Trace through sample examples manually
- Check edge cases: N=0, N=1, empty inputs, max values
- Verify output format matches exactly
- Ensure no infinite loops or TLE risks

### SOLUTION GUIDELINES:

**FAST I/O IS MANDATORY FOR LARGE INPUTS:**
```python
import sys

def solve():
    input_data = sys.stdin.read().split()
    if not input_data:
        return
    iterator = iter(input_data)
    try:
        T = int(next(iterator))
    except StopIteration:
        return
    
    results = []
    for i in range(1, T + 1):
        # Parse inputs using next(iterator)
        # ... your logic ...
        results.append(f"Case #{i}: {result}")
    
    sys.stdout.write("\\n".join(results) + "\\n")

if __name__ == "__main__":
    solve()
```

**TLE PREVENTION (CRITICAL):**
- NEVER use O(N²) for N > 10,000
- NEVER use nested loops over large ranges without justification
- Use efficient data structures: sets/dicts for O(1) lookups, heaps for priority
- Avoid building large segment trees for sparse data - use coordinate compression
- Use iterative approaches instead of deep recursion when possible
- Precompute values when possible instead of recalculating
- Use binary search instead of linear search when applicable

**COMMON ALGORITHM PATTERNS:**

1. **Greedy Problems:**
   - Sort items appropriately
   - Process in optimal order
   - Make locally optimal choices

2. **Segment Tree / Range Queries:**
   - Use coordinate compression if values are sparse
   - Build tree only for actual values, not entire range
   - Use Fenwick Tree for simpler range sum queries

3. **Graph Problems:**
   - Use iterative BFS/DFS to avoid stack overflow
   - Use adjacency lists for sparse graphs
   - Set recursion limit if using recursion: `sys.setrecursionlimit(200000)`

4. **DP Problems:**
   - Identify state and transitions
   - Use 1D array if possible to save memory
   - Consider space optimization (rolling arrays)

5. **Simulation Problems:**
   - Simulate step-by-step exactly as described
   - Track state accurately
   - Handle termination conditions correctly

**CRITICAL: Before writing code, mentally verify:**
1. Does this solve the problem correctly?
2. Will this pass all sample test cases?
3. Will this handle edge cases (N=0, N=1, max values)?
4. Is the complexity acceptable for the constraints?
5. Is the output format correct?

REMEMBER: Output ONLY the raw Python code, starting with import statements. No markdown, no explanations, no text before the code.
"""

    def _extract_code(self, response_text: str) -> str:
        """Extract Python code from response, handling various formats."""
        text = response_text.strip()
        
        # Remove any text before code blocks
        code_block_pattern = r'```(?:python)?\s*\n?(.*?)```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        if matches:
            text = matches[-1].strip()
        
        # Remove any leading text that's not Python code
        lines = text.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ', 'def ', 'class ', '#', 'sys.', 'if __name__')):
                start_idx = i
                break
            if any(keyword in stripped for keyword in ['import', 'def ', 'class ', 'if ', 'for ', 'while ']):
                start_idx = i
                break
        
        code = '\n'.join(lines[start_idx:]).strip()
        
        # Final validation: ensure it starts with valid Python
        if not code.startswith(('import ', 'from ', 'def ', 'class ', '#', 'sys.', 'if __name__')):
            for line in code.split('\n'):
                stripped = line.strip()
                if stripped and (stripped.startswith(('import ', 'from ', 'def ', 'class ')) or 
                                stripped[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
                    idx = code.find(line)
                    code = code[idx:].strip()
                    break
        
        return code

    def _build_system_prompt(self, hints: str = None) -> str:
        """Build system prompt with optional hints."""
        prompt = self.base_system_prompt
        if hints:
            prompt += f"\n\n=== PROBLEM-SPECIFIC ANALYSIS ===\n{hints}\n\nUse this analysis to guide your solution. Pay special attention to the algorithm type and complexity requirements."
        return prompt

    @retry_with_backoff(max_retries=5)
    def generate_solution(self, problem_statement: str, feedback: Optional[str] = None, attempt: int = 1, hints: str = None) -> str:
        """Generate optimal solution for the given problem."""
        system_prompt = self._build_system_prompt(hints)
        
        user_message = f"""Generate a CORRECT and OPTIMAL Python solution for this problem.

🚫 ANTI-HALLUCINATION CHECKLIST (MUST FOLLOW):
1. Read the problem statement 3 TIMES - do not skip this
2. Identify EXACTLY what is being asked - do not assume
3. Check sample input/output examples - trace through them with your algorithm
4. If your algorithm doesn't match sample output, STOP and fix your logic
5. Do not invent constraints or requirements not in the problem
6. Do not use algorithms that don't match the problem description

CRITICAL: Follow the step-by-step process:
1. READ the entire problem statement 3 TIMES - understand what is being asked
2. ANALYZE sample input/output examples - trace through them manually
3. VERIFY your algorithm logic produces the sample output - if not, fix it
4. ANALYZE constraints and determine required complexity
5. SELECT the correct algorithm approach (must match problem type)
6. DESIGN the solution logic (must match sample examples)
7. WRITE correct code with proper I/O
8. VERIFY correctness mentally against sample examples

SPECIFIC INSTRUCTIONS:
- Read the problem statement 3 TIMES - this is mandatory
- Check sample input/output examples - they are the TRUTH
  * Trace through sample input with your algorithm step-by-step
  * Your output MUST match sample output exactly
  * If it doesn't match, your algorithm is WRONG - fix it
- Identify the problem type (Greedy, DP, Graph, etc.) and use appropriate algorithm
- Ensure complexity is acceptable: O(N log N) or O(N) for N ≥ 10^5
- Use fast I/O: sys.stdin.read().split() for large inputs
- Handle ALL edge cases: N=0, N=1, empty inputs, max values
- Output format MUST match exactly: "Case #i: result"
- Prevent TLE: Avoid O(N²) for large N, use efficient data structures
- Use coordinate compression for sparse segment trees

VERIFICATION BEFORE CODING:
- Does my algorithm produce the sample output when I trace through it?
- If NO → My algorithm is wrong, I must fix it
- If YES → I can proceed to code

IMPORTANT: 
- CORRECTNESS is more important than speed - but both are required
- A correct O(N log N) solution is better than a wrong O(N) solution
- DO NOT code until your logic matches sample examples
- DO NOT assume anything not explicitly stated

Output ONLY the Python code. Start with import statements. No markdown, no explanations, no text.

Problem Statement:
{problem_statement}"""

        if feedback:
            user_message += f"\n\n=== FEEDBACK FROM PREVIOUS ATTEMPT {attempt - 1} ===\n{feedback}\n\nAnalyze the feedback carefully:\n"
            user_message += "- If TLE: Optimize complexity, use better data structures, avoid nested loops\n"
            user_message += "- If Wrong Answer: Re-read problem, check logic, verify with samples\n"
            user_message += "- If Runtime Error: Check edge cases, array bounds, recursion depth\n"
            user_message += "- Fix ALL issues and generate corrected code ONLY (no explanations)."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        code = self._extract_code(response.content)

        # Enhanced validation
        if not code or len(code) < 10:
            raise ValueError("Generated code is too short or empty")
        
        if not any(keyword in code for keyword in ['import', 'def ', 'sys.', 'input(', 'readline']):
            raise ValueError("Generated code doesn't look like valid Python solution")
        
        lines = code.split('\n')
        executable_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        if len(executable_lines) < 5:
            raise ValueError("Generated code appears to be mostly comments - need actual executable code")
        
        has_test_loop = (re.search(r'for\s+.*range', code) or 
                        'num_test' in code or 
                        'T =' in code or 
                        'Case #' in code or 
                        'main()' in code or 
                        '__main__' in code)
        if not has_test_loop:
            if 'def solve' in code or 'def main' in code:
                pass
            else:
                raise ValueError("Generated code doesn't have test case loop or main function")

        return code
    
    @retry_with_backoff(max_retries=5)
    def generate_solution_with_approach(self, problem_statement: str, approach: str, hints: str = None) -> str:
        """Generate optimal solution with a specific algorithmic approach."""
        approach_prompt = self._build_system_prompt(hints)
        approach_prompt += f"\n\n=== REQUIRED APPROACH ===\nYou MUST use a {approach} approach to solve this problem. Ensure the solution is correct and optimal."
        
        user_message = f"""Generate an optimal Python solution using {approach} approach.

CRITICAL: 
- Read and understand the problem first
- Use {approach} as the primary algorithmic technique
- Ensure correctness and optimal complexity
- Use fast I/O and handle all edge cases

Output ONLY the Python code. Start with import statements. No markdown, no explanations.

Problem:
{problem_statement}"""

        messages = [
            {"role": "system", "content": approach_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        code = self._extract_code(response.content)

        if not code or len(code) < 10:
            raise ValueError(f"Generated code for {approach} approach is too short or empty")
        
        if not any(keyword in code for keyword in ['import', 'def ', 'sys.', 'input(', 'readline']):
            raise ValueError(f"Generated code for {approach} approach doesn't look like valid Python")

        return code
    
    def generate_parallel_solutions(self, problem_statement: str, approaches: List[str], hints: str = None) -> List[dict]:
        """Generate multiple optimal solutions in parallel using different approaches."""
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
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(approaches)) as executor:
            futures = [executor.submit(generate_one, i, approach) for i, approach in enumerate(approaches)]
            
            for future in concurrent.futures.as_completed(futures):
                solutions.append(future.result())
        
        solutions.sort(key=lambda x: x['number'])
        return solutions
    
    def generate_multiple_temperature_solutions(self, problem_statement: str, num_solutions: int = 10, 
                                                temp_low: float = 0.1, temp_high: float = 0.3, 
                                                hints: str = None) -> List[dict]:
        """Generate multiple solutions with different temperatures.
        
        Args:
            problem_statement: The problem description
            num_solutions: Total number of solutions to generate (default 10)
            temp_low: Temperature for first half (default 0.1)
            temp_high: Temperature for second half (default 0.3)
            hints: Optional problem-specific hints
            
        Returns:
            List of solution dictionaries with 'code', 'temperature', and 'number' fields
        """
        solutions = []
        num_low = num_solutions // 2
        num_high = num_solutions - num_low
        
        def generate_with_temp(index: int, temperature: float):
            """Helper to generate one solution with specific temperature."""
            try:
                # Use stored model name
                model = self.model_name
                
                # Create model with specific temperature
                temp_model = ChatGoogleGenerativeAI(model=model, temperature=temperature)
                
                system_prompt = self._build_system_prompt(hints)
                user_message = f"""Generate a CORRECT and OPTIMAL Python solution for this problem.

🚫 ANTI-HALLUCINATION: Read problem 3 times, verify logic matches sample examples.

CRITICAL: Follow the step-by-step process:
1. READ the entire problem statement 3 TIMES - understand what is being asked
2. TRACE through sample input/output examples with your algorithm
3. VERIFY your algorithm produces sample output - if not, fix it
4. ANALYZE constraints and determine required complexity
5. SELECT the correct algorithm approach
6. DESIGN the solution logic (must match sample examples)
7. WRITE correct code with proper I/O
8. VERIFY correctness mentally against sample examples

DO NOT assume anything. DO NOT invent requirements. Match sample examples exactly.

Output ONLY the Python code. Start with import statements. No markdown, no explanations.

Problem Statement:
{problem_statement}"""
                
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ]
                
                response = temp_model.invoke(messages)
                code = self._extract_code(response.content)
                
                return {
                    'number': index + 1,
                    'temperature': temperature,
                    'code': code,
                    'error': None
                }
            except Exception as e:
                return {
                    'number': index + 1,
                    'temperature': temperature,
                    'code': '',
                    'error': str(e)
                }
        
        # Generate solutions in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_solutions) as executor:
            futures = []
            
            # First half with low temperature
            for i in range(num_low):
                futures.append(executor.submit(generate_with_temp, i, temp_low))
            
            # Second half with high temperature
            for i in range(num_high):
                futures.append(executor.submit(generate_with_temp, num_low + i, temp_high))
            
            for future in concurrent.futures.as_completed(futures):
                solutions.append(future.result())
        
        solutions.sort(key=lambda x: x['number'])
        return solutions

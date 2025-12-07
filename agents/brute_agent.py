from langchain_google_genai import ChatGoogleGenerativeAI
from typing import List
import re


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

        # Very low temperature for maximum consistency and to prevent hallucination
        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.0)  # Set to 0.0 for maximum determinism
        self.num_candidates = num_candidates
        self.base_system_prompt = """You are a brute force algorithm expert specializing in competitive programming.

🚫 CRITICAL ANTI-HALLUCINATION RULES:
- DO NOT make assumptions about the problem that aren't explicitly stated
- DO NOT invent constraints or requirements not mentioned in the problem
- DO NOT skip reading the problem carefully - read it AT LEAST 3 TIMES
- DO NOT generate code without understanding what the problem asks
- VERIFY your logic matches the sample input/output examples EXACTLY
- If sample examples don't match your logic, YOUR LOGIC IS WRONG - fix it
- Trace through sample examples manually before coding

CRITICAL REQUIREMENTS:
1. Output ONLY valid Python code - nothing else
2. NO markdown formatting, NO code blocks, NO explanations
3. NO text before or after the code
4. Start directly with 'import' or 'def' statements
5. The code must be complete, runnable, and handle stdin/stdout correctly
6. For Meta HackerCup: Use "Case #i: " format for output (e.g., "Case #1: Alice")
7. MUST handle ALL edge cases mentioned in the problem
8. MUST follow the EXACT input/output format from the problem statement
9. MUST verify your solution logic against sample examples before coding

Your task is to generate a SIMPLE, CORRECT brute force solution in Python.

SOLUTION STRATEGY:
1. Read the problem 3 TIMES CAREFULLY - understand what is being asked
2. Check sample input/output examples - trace through them manually
3. Verify your algorithm produces the sample output - if not, fix your logic
4. Identify the core logic - what computation needs to happen?
5. Simulate the problem step-by-step if it's a game/simulation problem
6. For game theory: simulate moves turn-by-turn, track state accurately
7. For optimization: try all possibilities (within constraints)
8. Test your logic mentally with the sample input/output examples - MUST MATCH

Guidelines:
- Prioritize CORRECTNESS over efficiency - correctness is 100% essential
- Use simple, straightforward approaches (simulation, nested loops, recursion, etc.)
- Don't worry about time/space complexity for brute force
- Read input from stdin using sys.stdin.readline().strip()
- IMPORTANT: Always use .strip() when reading lines to handle whitespace correctly
- Skip blank lines when reading input (check if line.strip() is empty before processing)
- Write output to stdout using sys.stdout.write() or print()
- Handle the exact input/output format specified (especially "Case #i: " format for HackerCup)
- Include proper input parsing with error handling
- Handle edge cases explicitly (empty input, single element, boundaries)
- For game/simulation problems: simulate the game EXACTLY as described, step by step
- For "optimal" strategies in games: both players want to win - simulate their optimal choices
- Make sure the solution is complete and runnable
- Consider alternative approaches (iterative vs recursive, different loop structures)

IMPORTANT FOR GAME THEORY PROBLEMS:
- If the problem mentions "optimal play" or "both players choose optimally":
  * DO NOT use heuristics or shortcuts - SIMULATE the game exactly
  * Track the current state accurately: what remains (current segment [L, R]), whose turn it is
  * For "Alice and Bob take turns" problems:
    - Precompute lists of indices for each player's pieces (e.g., a_indices, b_indices)
    - Use bisect.bisect_left() to find leftmost available piece for first player
    - Use bisect.bisect_right() to find rightmost available piece for second player
    - On each turn: update the boundaries (L or R) based on which piece was chosen
    - Track who made the last move (last_eater)
    - Continue until both players skip (no moves available)
    - Return who made the last move
  * DO NOT use heuristics like "if countA > countB return Alice" - these are usually WRONG
  * The correct approach is FULL SIMULATION with optimal choices (leftmost for first player, rightmost for second player)
  
EXAMPLE PATTERN for Alice/Bob games:
import bisect
a_indices = [i for i in range(N) if S[i] == 'A']
b_indices = [i for i in range(N) if S[i] == 'B']
current_l = 0
current_r = N - 1
last_eater = None

while True:
    alice_made_move = False
    bob_made_move = False
    
    # Alice's turn: leftmost 'A'
    idx = bisect.bisect_left(a_indices, current_l)
    if idx < len(a_indices) and a_indices[idx] <= current_r:
        current_l = a_indices[idx] + 1
        last_eater = "Alice"
        alice_made_move = True
    
    # Bob's turn: rightmost 'B'
    idx = bisect.bisect_right(b_indices, current_r)
    if idx > 0 and b_indices[idx-1] >= current_l:
        current_r = b_indices[idx-1] - 1
        last_eater = "Bob"
        bob_made_move = True
    
    if not alice_made_move and not bob_made_move:
        break

return last_eater

REMEMBER: Output ONLY the raw Python code, starting with import statements. No markdown, no explanations, no text before the code.
"""

    def _extract_code(self, response_text: str) -> str:
        """Extract Python code from response, handling various formats."""
        text = response_text.strip()
        
        # Remove any text before code blocks
        # Look for code blocks with ```python or ```
        code_block_pattern = r'```(?:python)?\s*\n?(.*?)```'
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        if matches:
            # Take the last code block (most likely the actual code)
            text = matches[-1].strip()
        
        # Remove any leading text that's not Python code
        # Look for first line that starts with import, def, class, or # (comment)
        lines = text.split('\n')
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ', 'def ', 'class ', '#', 'sys.', 'if __name__')):
                start_idx = i
                break
            # If we find a line that looks like code (has Python keywords), start there
            if any(keyword in stripped for keyword in ['import', 'def ', 'class ', 'if ', 'for ', 'while ']):
                start_idx = i
                break
        
        code = '\n'.join(lines[start_idx:]).strip()
        
        # Final validation: ensure it starts with valid Python
        if not code.startswith(('import ', 'from ', 'def ', 'class ', '#', 'sys.', 'if __name__')):
            # Try to find first valid Python line
            for line in code.split('\n'):
                stripped = line.strip()
                if stripped and (stripped.startswith(('import ', 'from ', 'def ', 'class ')) or 
                                stripped[0] not in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'):
                    # Found potential start
                    idx = code.find(line)
                    code = code[idx:].strip()
                    break
        
        return code

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
        
        user_message = f"""Generate a brute force Python solution for this problem.

🚫 ANTI-HALLUCINATION CHECKLIST:
1. Read the problem 3 TIMES - do not skip this
2. Trace through sample input/output examples manually
3. Verify your algorithm produces sample output - if not, fix it
4. Do not assume anything not explicitly stated
5. Do not invent constraints or requirements

CRITICAL INSTRUCTIONS:
1. Read the problem statement 3 TIMES CAREFULLY - understand EVERY detail
2. Check sample input/output examples FIRST - trace through them manually
3. Verify your algorithm logic produces the sample output - if not, your logic is WRONG
4. Understand what is being asked - what output is needed?
5. If this is a game/simulation problem:
   - DO NOT use heuristics (like comparing counts) - these are WRONG
   - SIMULATE the game turn-by-turn EXACTLY as described
   - For Alice/Bob games: Alice chooses leftmost piece, Bob chooses rightmost piece
   - Track game state accurately (current boundaries [L, R], whose turn, who made last move)
   - Use bisect module for efficient index lookup
   - Continue until no moves possible, return who made last move
6. Write code that SIMULATES CORRECTLY, even if inefficient
7. Ensure the output format matches EXACTLY (e.g., "Case #1: Alice" not just "Alice")

VERIFICATION BEFORE CODING:
- Does my algorithm produce the sample output when I trace through it?
- If NO → My algorithm is wrong, I must fix it
- If YES → I can proceed to code

CRITICAL FOR GAME THEORY: Do NOT try to optimize with shortcuts. Full simulation is correct.
For "optimal play" games, both players want to win - simulate their optimal choices exactly.

IMPORTANT: 
- Output ONLY the Python code. Start with import statements. No markdown, no explanations, no text.
- DO NOT code until your logic matches sample examples
- DO NOT assume anything not explicitly stated

Problem:
{problem_statement}

Remember: CORRECT simulation beats wrong heuristics every time. Simulate the game exactly. Verify against sample examples."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        code = self._extract_code(response.content)

        # Final validation
        if not code or len(code) < 10:
            raise ValueError("Generated brute force code is too short or empty")
        
        if not any(keyword in code for keyword in ['import', 'def ', 'sys.', 'input(', 'readline']):
            raise ValueError("Generated brute force code doesn't look like valid Python solution")
        
        # Check that code has actual executable statements (not just comments)
        lines = code.split('\n')
        executable_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        if len(executable_lines) < 5:
            raise ValueError("Generated code appears to be mostly comments - need actual executable code")
        
        # Check for main loop or test case handling
        import re
        has_test_loop = (re.search(r'for\s+.*range', code) or 
                        'num_test' in code or 
                        'T =' in code or 
                        'Case #' in code or 
                        'main()' in code or 
                        '__main__' in code)
        if not has_test_loop:
            # Check if it's a single function that returns a value (might be called from main)
            if 'def solve' in code or 'def main' in code:
                # This is okay if there's a function definition
                pass
            else:
                raise ValueError("Generated code doesn't have test case loop or main function")

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
            code = self._extract_code(response.content)

            # Final validation
            if not code or len(code) < 10:
                print(f"Warning: Brute force candidate {i+1} code is too short, skipping...")
                continue
            
            if not any(keyword in code for keyword in ['import', 'def ', 'sys.', 'input(', 'readline']):
                print(f"Warning: Brute force candidate {i+1} doesn't look like valid Python, skipping...")
                continue
            
            solutions.append({
                'number': i + 1,
                'code': code,
                'approach': f'Brute force approach #{i+1}'
            })
        
        return solutions

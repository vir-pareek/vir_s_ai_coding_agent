from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, List, Optional
import re


class ValidatorAgent:
    """Agent responsible for validating solution logic before execution."""

    def __init__(self, model_name: str):
        # Parse model name (format: "google:model-name")
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name

        # Remove 'models/' prefix if present - LangChain adds it automatically
        if model.startswith("models/"):
            model = model.replace("models/", "")

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.1)  # Lower temperature for strict validation
        self.system_prompt = """You are a STRICT Senior Competitive Programming Coach and expert code reviewer.

Your task is to CRITICALLY ANALYZE solution code for correctness, efficiency, and TLE risks BEFORE execution.

CRITICAL VALIDATION CHECKS (Check ALL of these):

1. **PROBLEM UNDERSTANDING**:
   - Does the code actually solve the stated problem?
   - Does it match the problem's requirements exactly?
   - Does it handle the correct input/output format?

2. **LOGIC CORRECTNESS**:
   - Is the algorithm logic correct?
   - Does it handle all cases mentioned in the problem?
   - Are there any logical errors or off-by-one mistakes?
   - Does it match the sample input/output behavior?

3. **TIME LIMIT EXCEEDED (TLE) RISK - CRITICAL**:
   - Analyze time complexity: What is the Big-O?
   - Check constraints: What is max N, M, etc.?
   - TLE RISK ASSESSMENT:
     * N ≤ 10^5: O(N²) WILL TLE. Must be O(N log N) or O(N)
     * N ≤ 10^6: O(N²) WILL TLE. Must be O(N) or O(N log N)
     * N ≤ 10^3: O(N²) is acceptable
     * N ≤ 20: O(2^N) or O(N!) is acceptable
   - Look for nested loops over large ranges - these cause TLE
   - Check for inefficient operations:
     * Building large segment trees for sparse data (use coordinate compression)
     * Repeated sorting in loops
     * Linear search in loops (use binary search or sets)
     * Recursive calls without memoization when needed
   - Verify fast I/O is used for large inputs

4. **SPACE COMPLEXITY**:
   - Will it exceed memory limits?
   - Are large arrays/structures necessary or can they be optimized?

5. **EDGE CASES**:
   - N = 0, N = 1
   - Empty inputs
   - Maximum values (N = max_constraint)
   - Boundary conditions
   - Negative numbers (if applicable)

6. **CODE QUALITY**:
   - Proper input/output format (especially "Case #i: " format)
   - Fast I/O for large inputs (sys.stdin.read().split())
   - Recursion limit set if using deep recursion
   - Proper error handling

7. **COMMON BUGS TO CHECK**:
   - Array index out of bounds
   - Division by zero
   - Uninitialized variables
   - Incorrect loop ranges
   - Off-by-one errors
   - Incorrect sorting order
   - Missing edge case handling

OUTPUT FORMAT:
- If VALID: Return "VALID" followed by brief confirmation
- If INVALID: Return "INVALID" followed by:
  1. List of SPECIFIC issues (one per line, prefixed with "-")
  2. For each TLE risk, specify: "TLE RISK: [description]"
  3. For each logic error, specify: "LOGIC ERROR: [description]"
  4. For each edge case issue, specify: "EDGE CASE: [description]"

Be STRICT and THOROUGH. It's better to catch issues now than after execution."""

    def validate_code(self, code: str, problem_statement: str, expected_io_format: Optional[Dict] = None) -> Dict[str, any]:
        """
        Validate solution code before execution.
        
        Args:
            code: The code to validate
            problem_statement: Problem description
            expected_io_format: Expected input/output format (optional)
        
        Returns:
            Dictionary with 'valid': bool, 'issues': List[str], 'analysis': str
        """
        # Extract constraints from problem statement
        constraints = self._extract_constraints(problem_statement)
        
        user_message = f"""CRITICALLY VALIDATE this solution code for the given problem.

Problem Statement:
{problem_statement[:1500]}

Code to Validate:
{code[:3000]}

Problem Constraints (if found):
{constraints}

CRITICAL CHECKS TO PERFORM:
1. Does this code solve the problem correctly?
2. What is the time complexity? Will it TLE?
3. Are there any logic errors?
4. Are edge cases handled?
5. Is the I/O format correct?
6. Are there any bugs or potential runtime errors?

Be THOROUGH and STRICT. List ALL issues found."""

        if expected_io_format:
            user_message += f"\n\nExpected I/O Format:\n{expected_io_format}"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        content = response.content.strip()
        
        # Parse response
        is_valid = "VALID" in content.upper() and "INVALID" not in content.upper()
        issues = []
        
        # Extract issues from response
        lines = content.split('\n')
        for line in lines:
            line_upper = line.upper()
            if any(keyword in line_upper for keyword in ['TLE', 'TIME LIMIT', 'COMPLEXITY', 'O(N', 'WILL TLE']):
                if line.strip() and not line.strip().startswith('VALID'):
                    issues.append(line.strip())
            elif any(keyword in line_upper for keyword in ['ERROR', 'ISSUE', 'PROBLEM', 'WRONG', 'MISSING', 'BUG', 'INVALID']):
                if line.strip() and not line.strip().startswith('VALID'):
                    issues.append(line.strip())
            elif line.strip().startswith('-') or line.strip().startswith('*'):
                issues.append(line.strip())
        
        # Also check for TLE patterns in code directly
        tle_issues = self._check_tle_patterns(code, constraints)
        issues.extend(tle_issues)
        
        return {
            'valid': is_valid and len(issues) == 0,
            'issues': issues,
            'analysis': content
        }
    
    def _extract_constraints(self, problem_statement: str) -> str:
        """Extract constraints from problem statement."""
        constraints = []
        
        # Look for N, M constraints
        n_match = re.search(r'[1-9]\s*≤\s*N\s*≤\s*([0-9,]+|\d+\*\*\d+)', problem_statement, re.IGNORECASE)
        if n_match:
            constraints.append(f"Max N: {n_match.group(1)}")
        
        m_match = re.search(r'[1-9]\s*≤\s*M\s*≤\s*([0-9,]+|\d+\*\*\d+)', problem_statement, re.IGNORECASE)
        if m_match:
            constraints.append(f"Max M: {m_match.group(1)}")
        
        # Look for value constraints
        val_match = re.search(r'[0-9]\s*≤\s*[A-Za-z_]\w*\s*≤\s*([0-9,]+|\d+\*\*\d+)', problem_statement, re.IGNORECASE)
        if val_match:
            constraints.append(f"Max value: {val_match.group(1)}")
        
        return "\n".join(constraints) if constraints else "Constraints not explicitly found"
    
    def _check_tle_patterns(self, code: str, constraints: str) -> List[str]:
        """Check code for common TLE patterns."""
        issues = []
        
        # Check for nested loops
        nested_loop_pattern = r'for\s+\w+\s+in\s+.*:\s*\n\s*for\s+\w+\s+in'
        if re.search(nested_loop_pattern, code, re.MULTILINE):
            # Check if ranges are large
            if '10**5' in constraints or '100000' in constraints or '10^5' in constraints:
                issues.append("TLE RISK: Nested loops detected with large N constraint - likely O(N²) which will TLE")
        
        # Check for building large segment trees
        if 'tree = [' in code and '4 *' in code:
            # Check if it's building for entire range
            if re.search(r'4\s*\*\s*\([^)]+\s*\+\s*1\)', code):
                issues.append("TLE RISK: Building segment tree for entire range - consider coordinate compression for sparse data")
        
        # Check for repeated sorting in loops
        if 'sorted(' in code or '.sort()' in code:
            loop_count = len(re.findall(r'for\s+', code))
            sort_count = len(re.findall(r'sorted\(|\.sort\(\)', code))
            if sort_count > 1 and loop_count > 1:
                issues.append("TLE RISK: Multiple sorting operations detected - may cause TLE if in loops")
        
        # Check for linear search in loops
        if '.index(' in code or code.count('in ') > 3:
            issues.append("TLE RISK: Linear search operations detected - consider using sets/dicts for O(1) lookup")
        
        return issues

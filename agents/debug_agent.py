from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Optional, Dict
import re


class DebugAgent:
    """Agent responsible for analyzing failures and providing debugging insights."""

    def __init__(self, model_name: str):
        # Parse model name (format: "google:model-name")
        if ":" in model_name:
            provider, model = model_name.split(":", 1)
        else:
            model = model_name

        # Remove 'models/' prefix if present - LangChain adds it automatically
        if model.startswith("models/"):
            model = model.replace("models/", "")

        self.model = ChatGoogleGenerativeAI(model=model, temperature=0.2)  # Lower for more focused analysis
        self.system_prompt = """You are an EXPERT debugging agent for competitive programming problems.

Your task is to analyze code failures and provide ACTIONABLE debugging insights to fix issues quickly.

ANALYSIS FRAMEWORK:

1. **IDENTIFY ROOT CAUSE**:
   - What exactly went wrong?
   - Is it a logic error, runtime error, TLE, or wrong answer?
   - What line/operation caused the failure?

2. **TLE (Time Limit Exceeded) ANALYSIS - CRITICAL**:
   - Identify the bottleneck: What operation is too slow?
   - Analyze complexity: What is the actual time complexity?
   - Check for:
     * Nested loops over large ranges → O(N²) TLE risk
     * Building large data structures unnecessarily
     * Repeated expensive operations (sorting, searching)
     * Inefficient algorithms for the constraints
   - Provide SPECIFIC optimization suggestions:
     * Use coordinate compression instead of full range segment trees
     * Replace nested loops with efficient data structures
     * Use binary search instead of linear search
     * Cache/memoize repeated computations
     * Use fast I/O (sys.stdin.read().split())

3. **WRONG ANSWER ANALYSIS**:
   - Compare expected vs actual output
   - Identify logical flaws in the algorithm
   - Check if edge cases are handled
   - Verify problem understanding is correct
   - Check for off-by-one errors, incorrect conditions

4. **RUNTIME ERROR ANALYSIS**:
   - Identify the error type (IndexError, KeyError, etc.)
   - Find the problematic line from stack trace
   - Check for:
     * Array bounds violations
     * Uninitialized variables
     * Division by zero
     * Recursion depth exceeded
   - Suggest fixes

5. **PROVIDE SPECIFIC FIXES**:
   - Give concrete code changes, not vague suggestions
   - Explain WHY the fix works
   - Prioritize fixes (most critical first)

OUTPUT FORMAT:
Provide a structured analysis:
1. ROOT CAUSE: [brief description]
2. ISSUE TYPE: [TLE/Wrong Answer/Runtime Error]
3. SPECIFIC PROBLEMS: [list of specific issues]
4. FIXES NEEDED: [specific fixes with code suggestions if applicable]
5. OPTIMIZATION SUGGESTIONS: [if TLE, provide specific optimizations]

Be CONCISE but THOROUGH. Focus on ACTIONABLE fixes."""

    def analyze_failure(self, 
                       code: str,
                       error_message: str,
                       stack_trace: Optional[str] = None,
                       execution_time: Optional[float] = None,
                       memory_usage: Optional[float] = None,
                       output_diff: Optional[str] = None) -> str:
        """
        Analyze a code failure and provide debugging insights.
        
        Args:
            code: The failing code
            error_message: Error message from execution
            stack_trace: Stack trace (if available)
            execution_time: Execution time in seconds (if available)
            memory_usage: Memory usage in MB (if available)
            output_diff: Output difference (if wrong answer)
        
        Returns:
            Debugging insights and suggestions
        """
        # Determine issue type
        issue_type = "Unknown"
        if "timeout" in error_message.lower() or "time limit" in error_message.lower() or (execution_time and execution_time > 10):
            issue_type = "TLE"
        elif "wrong answer" in error_message.lower() or output_diff:
            issue_type = "Wrong Answer"
        elif stack_trace or "error" in error_message.lower():
            issue_type = "Runtime Error"
        
        user_message = f"""Analyze this code failure and provide SPECIFIC debugging insights.

ISSUE TYPE: {issue_type}

Code:
{code[:2000]}

Error Message:
{error_message}"""

        if stack_trace:
            user_message += f"\n\nStack Trace:\n{stack_trace[:1000]}"
        
        if execution_time:
            user_message += f"\n\nExecution Time: {execution_time:.3f}s"
            if execution_time > 5:
                user_message += " (VERY SLOW - TLE risk)"
            elif execution_time > 2:
                user_message += " (SLOW - may TLE on larger inputs)"
        
        if memory_usage:
            user_message += f"\n\nMemory Usage: {memory_usage:.2f} MB"
        
        if output_diff:
            user_message += f"\n\nOutput Difference (Expected vs Actual):\n{output_diff[:1000]}"
        
        # Add TLE-specific analysis request
        if issue_type == "TLE" or (execution_time and execution_time > 2):
            user_message += "\n\nCRITICAL: This is a TLE issue. Analyze:"
            user_message += "\n1. What operations are causing the slowdown?"
            user_message += "\n2. What is the time complexity?"
            user_message += "\n3. Provide SPECIFIC optimizations (e.g., use coordinate compression, avoid nested loops, use efficient data structures)"

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = self.model.invoke(messages)
        analysis = response.content.strip()
        
        # Enhance with pattern-based TLE detection
        if issue_type == "TLE" or (execution_time and execution_time > 2):
            tle_patterns = self._detect_tle_patterns(code)
            if tle_patterns:
                analysis += "\n\nADDITIONAL TLE PATTERNS DETECTED:\n" + "\n".join(f"- {pattern}" for pattern in tle_patterns)
        
        return analysis
    
    def _detect_tle_patterns(self, code: str) -> list:
        """Detect common TLE-causing patterns in code."""
        patterns = []
        
        # Nested loops
        if re.search(r'for\s+\w+\s+in\s+.*:\s*\n\s*for\s+\w+\s+in', code, re.MULTILINE):
            patterns.append("Nested loops detected - likely O(N²) complexity")
        
        # Large segment tree building
        if 'tree = [' in code and re.search(r'4\s*\*\s*\([^)]+\s*\+\s*1\)', code):
            patterns.append("Building segment tree for entire range - use coordinate compression for sparse data")
        
        # Repeated sorting
        sort_count = len(re.findall(r'sorted\(|\.sort\(\)', code))
        if sort_count > 2:
            patterns.append(f"Multiple sorting operations ({sort_count}) - consider sorting once and reusing")
        
        # Linear search in loops
        if '.index(' in code:
            patterns.append("Using .index() for linear search - replace with set/dict for O(1) lookup")
        
        # Recursion without memoization
        if 'def ' in code and 'return' in code:
            func_defs = len(re.findall(r'def\s+\w+', code))
            if func_defs > 2 and 'memo' not in code.lower() and 'cache' not in code.lower():
                patterns.append("Recursive functions without memoization - may cause repeated computations")
        
        return patterns

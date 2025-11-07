# How to Use This Multi-Agent Solver

## Quick Start Guide

### 1. **Prepare Your Problem**

Edit `PROBLEM.txt` with your coding problem:

```
Given an array of integers, find the maximum sum of any contiguous subarray.

Input Format:
- First line: n (size of array)
- Second line: n space-separated integers

Output Format:
- Single integer: maximum subarray sum

Constraints:
- 1 <= n <= 10^5
- -10^4 <= array[i] <= 10^4

Example:
Input:
5
-2 1 -3 4 -1

Output:
4

Explanation: The subarray [4] has the maximum sum of 4.
```

### 2. **Configure API Key** (if not done already)

Edit `config.yaml` and set your Google API key:

```yaml
api_keys:
  google: "YOUR_API_KEY_HERE"
```

Get your free API key from: https://aistudio.google.com/app/apikey

### 3. **Run the Solver**

```bash
python main.py
```

### 4. **Watch It Work!**

The system will:
1. Analyze the problem and extract hints
2. Generate test cases
3. Create multiple brute force solution candidates
4. Test and select the best brute force solution
5. Generate parallel optimal solutions using different approaches
6. Test each approach and pick the fastest correct one
7. Save the optimal solution

**Example Output:**
```
================================================================================
Multi-Agent Programming Problem Solver
================================================================================

Problem loaded from: PROBLEM.txt

Given an array of integers, find the maximum sum...

================================================================================
STEP 0: Analyzing problem and extracting hints...
================================================================================

✓ Problem analysis complete:
Algorithm Type: Dynamic Programming, Two Pointers
Target Complexity: O(n) time, O(1) space
Key Insight: Kadane's algorithm (max subarray sum)
Recommended Approaches: Dynamic Programming, Greedy, Two Pointers
Problem Difficulty: Medium

→ Will generate solutions using approaches: Dynamic Programming, Greedy, Two Pointers

================================================================================
STEP 1: Generating test cases...
================================================================================

✓ Test cases saved to: ./workspace/small_inputs.txt

================================================================================
STEP 2: Generating multiple brute force solutions...
================================================================================

✓ Generated 3 brute force solution candidates

================================================================================
STEP 3: Testing and selecting best brute force solution...
================================================================================

Testing brute force solution 1/3...
✓ Solution 1 executed successfully
→ Solution 1 selected as best so far

Testing brute force solution 2/3...
✓ Solution 2 executed successfully

Testing brute force solution 3/3...
✓ Solution 3 executed successfully

✓ Selected best brute force solution (from 3 candidates)
✓ Brute force solution saved to: ./workspace/brute.py
✓ Brute force outputs saved to: ./workspace/small_outputs.txt

================================================================================
STEP 4: Generating and testing optimal solution...
================================================================================

→ Generating 3 solutions in parallel using different approaches...
✓ Generated 3 parallel solutions

Testing Dynamic Programming solution...
✓ Dynamic Programming solution executed successfully
✓ Dynamic Programming solution outputs MATCH!

✓ Parallel generation succeeded! Best approach: Dynamic Programming

================================================================================
SUCCESS: Optimal solution found!
================================================================================

✓ Results saved to: ./workspace/results.json

================================================================================
FINAL RESULTS
================================================================================
Success: True
Attempts used: 1
Test cases generated: True
Brute force generated: True
Brute force executed: True
Optimal solution found: True
```

### 5. **Get Your Solution**

The final optimal solution is saved in `workspace/optimal.py`:

```bash
cat workspace/optimal.py
```

### 6. **View Results in Browser** (Optional)

Start a local HTTP server:

```bash
python -m http.server 8000
```

Then open: http://localhost:8000/viewer.html

## Understanding the Output

### Generated Files

All files are saved in the `workspace/` directory:

```
workspace/
├── small_inputs.txt              # Test cases generated
├── small_outputs.txt              # Expected outputs (from brute force)
├── brute.py                       # Best brute force solution selected
├── brute_candidate_1.py           # First brute force attempt
├── brute_candidate_2.py           # Second brute force attempt
├── brute_candidate_3.py           # Third brute force attempt
├── optimal_approach_Dynamic_Programming.py  # DP approach solution
├── optimal_approach_Greedy.py              # Greedy approach solution
├── optimal_approach_Two_Pointers.py        # Two pointers solution
├── optimal.py                     # Final optimal solution (this is your answer)
├── results.json                   # Complete metadata for viewer
└── optimal_attempt_*.py           # Sequential attempts if parallel fails
```

### The Solution

Your answer is in `workspace/optimal.py`. You can:

1. **Copy the solution** and submit to the judge
2. **Verify it** by running against the test inputs
3. **Customize it** if needed before submitting

### Testing Locally

You can test the solution manually:

```bash
python workspace/optimal.py < workspace/small_inputs.txt > my_output.txt
diff workspace/small_outputs.txt my_output.txt
```

If there's no diff, the solution is correct!

## Advanced Features

### Feature 1: Multiple Brute Force Candidates

The system now generates **3 brute force solutions** and automatically picks the best working one. This increases success rate.

### Feature 2: Parallel Optimal Generation

When multiple approaches are detected, the system generates solutions in parallel:
- Dynamic Programming
- Greedy
- Binary Search
- Two Pointers
- etc.

And picks the **fastest correct one**.

### Feature 3: Problem-Specific Hints

The system analyzes your problem and provides:
- Algorithm type detection
- Complexity targets
- Key insights
- Data structure suggestions

### Feature 4: WebSearchAgent (Optional)

Can search for algorithm approaches on the fly (configured in `config.yaml`).

## Configuration Options

### Adjust Number of Candidates

Edit `config.yaml`:

```yaml
execution:
  num_brute_candidates: 5  # Generate 5 instead of 3
```

### Adjust Max Attempts

```yaml
execution:
  max_optimal_attempts: 10  # Try up to 10 times
```

### Change Timeout

```yaml
execution:
  timeout_seconds: 60  # 60 seconds timeout
```

### Disable Parallel Generation

Comment out parallel generation in `orchestrator.py` if you prefer sequential only.

## Troubleshooting

### "ModuleNotFoundError"
Install dependencies:
```bash
pip install -r requirements.txt
```

### "API key invalid"
Get a free key from: https://aistudio.google.com/app/apikey

### "Rate limit exceeded"
Free tier has limits. Wait or use a different API key.

### Solution fails all tests
Check `workspace/results.json` for error details and retry.

### Parallel generation fails
System automatically falls back to sequential generation.

## Submitting to Judge

### 1. Copy the Solution

```bash
cp workspace/optimal.py solution.py
```

### 2. Verify It Works

```bash
python solution.py < test_input.txt > output.txt
```

### 3. Submit

Upload `solution.py` to the judge/contest platform.

## Tips

1. **Use the problem-specific hints** - They guide the AI to correct solutions faster
2. **Check the viewer** - Beautiful visualization of all attempts
3. **Review generated test cases** - Make sure they cover edge cases
4. **Verify outputs** - Always test before submitting
5. **Customize if needed** - The generated solutions are starting points

## Example Workflow

```bash
# 1. Edit your problem
nano PROBLEM.txt

# 2. Run the solver
python main.py

# 3. Wait for completion (usually 1-2 minutes)

# 4. Get your solution
cat workspace/optimal.py

# 5. Test it
python workspace/optimal.py < workspace/small_inputs.txt

# 6. Submit to judge!
```

## Need Help?

- Check `VERIFICATION_REPORT.md` for technical details
- Check `FEATURES.md` for feature documentation
- Review `QUICKSTART.md` for quick reference
- Check error messages in terminal output
- Review `workspace/results.json` for detailed metadata

---

**Happy Coding! 🚀**

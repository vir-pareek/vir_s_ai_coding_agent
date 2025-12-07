# 🏆 Complete Guide: Using the Agent System for Meta HackerCup Problems

## 📋 Overview

This guide walks you through using the multi-agent system to solve **Meta HackerCup** problems. The system automatically handles:
- ✅ Problem analysis and algorithm detection
- ✅ Test case generation
- ✅ Brute force solution creation
- ✅ Optimal solution generation
- ✅ **Meta HackerCup output format** (`Case #i: Answer`)

---

## 🚀 Quick Start (5 Steps)

### Step 1: Setup API Key

1. Get a **FREE** Google Gemini API key: https://aistudio.google.com/app/apikey
2. Edit `config.yaml`:
   ```yaml
   api_keys:
     google: "YOUR_API_KEY_HERE"
   ```

### Step 2: Prepare Your Problem

Edit `PROBLEM.txt` with the Meta HackerCup problem statement. **Include the output format specification!**

**Example for Meta HackerCup:**
```
Alice and Bob are back at their favorite restaurant: Nim Sum Dim Sum.
[Problem description...]

Input Format:
Input begins with a single integer T, the number of test cases.
For each test case, the first line contains an integer N and the 
second line contains the string S.

Output Format:
For the i-th test case, print "Case #i: ", followed by "Alice" 
if Alice eats the final dish, or "Bob" if Bob eats the final dish.

Constraints:
1 ≤ T ≤ 95
1 ≤ N ≤ 600,000
S₁..N ∈ {'A', 'B'}

Sample Input:
4
6
ABBAAAB
1
A
1
B
2
AB

Sample Output:
Case #1: Alice
Case #2: Alice
Case #3: Bob
Case #4: Bob
```

**Key Points:**
- ✅ Always include the **exact output format** in your problem statement
- ✅ Include sample input/output examples
- ✅ Specify constraints clearly

### Step 3: Run the Solver

```bash
python main.py
```

**What happens:**
1. **Problem Analysis** - Extracts algorithm hints and complexity targets
2. **Test Generation** - Creates 3-5 small test cases (with T header for HackerCup format)
3. **Brute Force** - Generates 3 candidate solutions, picks the best working one
4. **Optimal Solution** - Generates efficient solution(s) and validates against brute force
5. **Output Format** - Automatically ensures `Case #i: Answer` format

### Step 4: Get Your Solution

Your final solution is in:
```
workspace/optimal.py
```

**Verify the output format:**
```bash
# Test with your input file
python workspace/optimal.py < inputD.txt > output.txt

# Check format
head -5 output.txt
# Should show:
# Case #1: Alice
# Case #2: Bob
# Case #3: Alice
# ...
```

### Step 5: Submit to Meta HackerCup

1. Copy `workspace/optimal.py`
2. Submit to the HackerCup judge
3. ✅ Done!

---

## 📝 Detailed Workflow

### Phase 1: Problem Setup

**1. Copy Problem Statement**
- Copy the complete problem from Meta HackerCup
- Paste into `PROBLEM.txt`
- **Ensure output format is clearly specified**

**2. Verify Output Format Requirements**
Meta HackerCup problems typically require:
```
Case #1: Answer
Case #2: Answer
...
```

The system automatically ensures this format in generated solutions.

### Phase 2: Running the Solver

**Command:**
```bash
python main.py
```

**Expected Output:**
```
================================================================================
Multi-Agent Programming Problem Solver
================================================================================

Problem loaded from: PROBLEM.txt

[Your problem statement]

================================================================================
STEP 0: Analyzing problem and extracting hints...
================================================================================

✓ Problem analysis complete:
Algorithm Type: Game Theory, Two Pointers
Target Complexity: O(n) time, O(n) space
Key Insight: Simulate game turns with optimal strategy
Recommended Approaches: Simulation, Greedy
Problem Difficulty: Medium

→ Will generate solutions using approaches: Simulation, Greedy

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

✓ Selected best brute force solution (from 3 candidates)
✓ Brute force solution saved to: ./workspace/brute.py

================================================================================
STEP 4: Generating and testing optimal solution...
================================================================================

→ Generating 2 solutions in parallel using different approaches...
✓ Generated 2 parallel solutions

Testing Simulation solution...
✓ Simulation solution executed successfully
✓ Simulation solution outputs MATCH!

✓ Parallel generation succeeded! Best approach: Simulation

================================================================================
SUCCESS: Optimal solution found!
================================================================================

✓ Results saved to: ./workspace/results.json
```

### Phase 3: Verification

**1. Check Output Format**
```bash
python workspace/optimal.py < inputD.txt | head -10
```

Should show:
```
Case #1: Alice
Case #2: Bob
Case #3: Alice
...
```

**2. Test with Full Input**
```bash
python workspace/optimal.py < inputD.txt > output.txt
```

**3. Verify Line Count**
```bash
# Should match number of test cases
wc -l output.txt
```

### Phase 4: Submission

1. **Copy Solution:**
   ```bash
   cp workspace/optimal.py solution.py
   ```

2. **Submit to Meta HackerCup Platform**

3. **Monitor Results**

---

## 🎯 Meta HackerCup Specific Features

### Automatic Output Format Handling

The system **automatically ensures** the correct Meta HackerCup output format:
- ✅ `Case #i: Answer` format
- ✅ Proper spacing after colon
- ✅ Correct case numbering (1-indexed)
- ✅ Handles multiple test cases correctly

### Test Case Generation

For Meta HackerCup problems, test cases are generated with:
- ✅ T header (number of test cases) on first line
- ✅ T groups of test case data
- ✅ Small values for fast validation
- ✅ Edge cases included

**Example Generated Test Cases:**
```
5
1
A
1
B
2
AB
3
AAB
4
ABBA
```

### Multiple Solution Candidates

The system generates **3 brute force candidates** and picks the best one:
- Increases success rate
- Handles different approaches
- Automatically selects working solution

### Parallel Optimal Generation

When multiple algorithm approaches are detected:
- Generates solutions in parallel
- Tests each approach
- Picks the fastest correct one

---

## 🔧 Configuration for Meta HackerCup

### Recommended Settings

Edit `config.yaml`:

```yaml
# Use faster models for quick iteration
models:
  tester_agent: "google:gemini-2.5-flash"      # Fast, 250 free/day
  brute_agent: "google:gemini-2.5-flash"
  optimal_agent: "google:gemini-2.5-flash"

# For harder problems, use Pro model
# optimal_agent: "google:gemini-2.5-pro"       # More capable, 100 free/day

execution:
  max_optimal_attempts: 5                      # Try up to 5 times
  timeout_seconds: 30                          # 30s timeout per execution
  num_brute_candidates: 3                      # Generate 3 brute force solutions
```

### Model Selection

**For Easy/Medium Problems:**
- Use `gemini-2.5-flash` (fast, 250 free requests/day)

**For Hard Problems:**
- Use `gemini-2.5-pro` (more capable, 100 free requests/day)

**For Testing:**
- Use `gemini-2.5-flash-lite` (very fast, 1000 free requests/day)

---

## 📊 Understanding Results

### Generated Files

All files in `workspace/`:

```
workspace/
├── small_inputs.txt              # Generated test cases (with T header)
├── small_outputs.txt             # Expected outputs (from brute force)
├── brute.py                      # Best brute force solution
├── brute_candidate_1.py          # First brute force attempt
├── brute_candidate_2.py          # Second brute force attempt
├── brute_candidate_3.py          # Third brute force attempt
├── optimal.py                    # ✅ YOUR FINAL SOLUTION (use this!)
├── optimal_attempt_1.py          # First optimal attempt
├── optimal_attempt_2.py          # Second optimal attempt (if needed)
├── results.json                  # Complete metadata
└── ...
```

### Viewing Results in Browser

1. Start HTTP server:
   ```bash
   python -m http.server 8000
   ```

2. Open: http://localhost:8000/viewer.html

3. See:
   - All attempts with verdicts
   - Code with syntax highlighting
   - Output differences
   - Problem analysis

---

## 🐛 Troubleshooting

### Issue: Wrong Output Format

**Symptom:** Output doesn't have `Case #i:` format

**Solution:**
1. Ensure problem statement includes output format specification
2. Check `workspace/optimal.py` - should have:
   ```python
   for i in range(1, num_test_cases + 1):
       result = solve()
       sys.stdout.write(f"Case #{i}: {result}\n")
   ```
3. If wrong, the system should auto-fix, but you can manually edit if needed

### Issue: "ModuleNotFoundError: No module named 'yaml'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: API Key Invalid

**Solution:**
1. Get new key: https://aistudio.google.com/app/apikey
2. Update `config.yaml`
3. Or set environment variable:
   ```bash
   export GOOGLE_API_KEY="your-key"
   ```

### Issue: Solution Fails All Tests

**Check:**
1. `workspace/results.json` - see error details
2. `workspace/optimal_attempt_*_output.txt` - see actual outputs
3. Compare with `workspace/small_outputs.txt` - see expected outputs

**Fix:**
- Review problem statement - ensure it's complete
- Check constraints - ensure test cases are valid
- Re-run: `python main.py`

### Issue: Timeout Errors

**Solution:**
Increase timeout in `config.yaml`:
```yaml
execution:
  timeout_seconds: 60  # Increase from 30 to 60
```

---

## 💡 Pro Tips for Meta HackerCup

### 1. Always Include Output Format

In your `PROBLEM.txt`, **explicitly state the output format:**
```
Output Format:
For the i-th test case, print "Case #i: ", followed by [answer].
```

### 2. Use Sample Examples

Include sample input/output in problem statement:
```
Sample Input:
2
3
ABC
1
X

Sample Output:
Case #1: Answer1
Case #2: Answer2
```

### 3. Test Before Submitting

```bash
# Test with your input file
python workspace/optimal.py < inputD.txt > output.txt

# Verify format
head -5 output.txt
tail -5 output.txt

# Check line count matches test cases
wc -l output.txt
```

### 4. Review Generated Test Cases

Check `workspace/small_inputs.txt`:
- Are edge cases covered?
- Are constraints satisfied?
- Is format correct?

### 5. Use Viewer for Debugging

If solution fails:
1. Open viewer: `python -m http.server 8000` → http://localhost:8000/viewer.html
2. Check "Show Output Diff" for wrong answers
3. Review error messages for runtime errors

### 6. Iterate Quickly

For competition:
- Use `gemini-2.5-flash` for speed
- Set `max_optimal_attempts: 3` for faster iteration
- Test locally before submitting

---

## 📋 Complete Example Workflow

```bash
# 1. Setup (one-time)
# Get API key from https://aistudio.google.com/app/apikey
# Add to config.yaml

# 2. Prepare problem
nano PROBLEM.txt
# Paste Meta HackerCup problem statement

# 3. Run solver
python main.py

# 4. Wait for completion (1-3 minutes)
# Watch progress in terminal

# 5. Verify solution
python workspace/optimal.py < inputD.txt | head -10

# 6. Test with full input
python workspace/optimal.py < inputD.txt > output.txt

# 7. Check format
head -5 output.txt
tail -5 output.txt

# 8. Submit!
# Copy workspace/optimal.py to Meta HackerCup platform
```

---

## 🎓 Understanding the System

### How It Works

1. **TesterAgent** → Generates test cases matching problem format
2. **BruteAgent** → Creates correct but slow solution (O(n²) or O(n³))
3. **OptimalAgent** → Creates efficient solution (O(n) or O(n log n))
4. **Validation** → Compares outputs, ensures correctness
5. **Format Check** → Ensures Meta HackerCup output format

### Why This Works

- ✅ **Correctness**: Brute force solution is always correct (even if slow)
- ✅ **Efficiency**: Optimal solution matches brute force output
- ✅ **Format**: System learns output format from problem statement
- ✅ **Reliability**: Multiple candidates increase success rate

---

## 📚 Additional Resources

- `HOW_TO_USE.md` - General usage guide
- `QUICKSTART.md` - Quick reference
- `FEATURES.md` - Feature documentation
- `README.md` - Project overview

---

## ✅ Checklist Before Submission

- [ ] Solution runs without errors: `python workspace/optimal.py < inputD.txt`
- [ ] Output format correct: `Case #i: Answer`
- [ ] Line count matches test cases
- [ ] Tested with sample input/output
- [ ] Reviewed code for obvious bugs
- [ ] Verified constraints are satisfied

---

**Happy Coding! 🏆**

Good luck with Meta HackerCup! 🚀


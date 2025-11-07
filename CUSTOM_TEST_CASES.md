# Using Custom Test Cases

## Option 1: Use the Generated Test Cases (Recommended)

The system automatically generates test cases from the problem statement. You don't need to provide inputs!

### How It Works

1. **Problem Statement** → AI reads `PROBLEM.txt`
2. **TesterAgent** → Generates 3-5 small test cases automatically
3. **Saved to** → `workspace/small_inputs.txt`
4. **Used for** → Testing all solutions

### Example Generated Test Cases

For the max subarray sum problem, it might generate:

```
5
-2 1 -3 4 -1

3
1 2 3

4
-1 2 3 -4

2
10 -5

1
42
```

These are saved in `workspace/small_inputs.txt` after running.

## Option 2: Provide Your Own Test Cases

If you want to use custom test inputs:

### Step 1: Create Your Test Input File

Create a file with your test inputs, e.g., `my_test_cases.txt`:

```
5
-2 1 -3 4 -1
```

### Step 2: Replace the Generated Test Cases

```bash
cp my_test_cases.txt workspace/small_inputs.txt
```

### Step 3: Run the Solver

```bash
python main.py
```

The system will use your custom test cases instead of generated ones.

### Step 4: Or Test Manually

```bash
# Test your custom input
python workspace/optimal.py < my_test_cases.txt > output.txt
cat output.txt
```

## Option 3: Use Judge's Test Cases (After Submission)

1. Download test cases from judge/contest platform
2. Save as `judge_tests.txt`
3. Test your solution:

```bash
python workspace/optimal.py < judge_tests.txt > output.txt
```

4. Compare with expected outputs

## Understanding Input Format

The input format depends on your problem. Here are common patterns:

### Pattern 1: Multiple Test Cases with Count

```
2          # Number of test cases
3          # Case 1: array size
1 2 3      # Case 1: array elements
4          # Case 2: array size  
1 1 1 1    # Case 2: array elements
```

### Pattern 2: Single Array

```
5          # Array size
-2 1 -3 4 -1  # Array elements
```

### Pattern 3: Graph Input

```
4 3        # n nodes, m edges
1 2        # Edge 1
2 3        # Edge 2
3 4        # Edge 3
```

## Testing Your Solution

### Test with Generated Inputs

```bash
# The system already does this, but you can test manually:
python workspace/optimal.py < workspace/small_inputs.txt > output.txt
diff workspace/small_outputs.txt output.txt
```

### Test with Custom Inputs

```bash
# Create your input file
cat > my_input.txt << EOF
5
-2 1 -3 4 -1
EOF

# Test the solution
python workspace/optimal.py < my_input.txt
```

Expected output: `4`

### Test Multiple Cases

```bash
cat > multi_test.txt << EOF
5
-2 1 -3 4 -1
3
1 2 3
1
-5
EOF

python workspace/optimal.py < multi_test.txt
```

Expected output:
```
4
6
-5
```

## Important Notes

1. **No need to provide inputs for normal use** - System generates them automatically
2. **Generated test cases are saved** in `workspace/small_inputs.txt`
3. **Expected outputs are saved** in `workspace/small_outputs.txt`
4. **You can always override** by replacing these files

## Summary

- **Normal use**: Just run `python main.py` - inputs are generated for you!
- **Custom testing**: Create `my_input.txt` and test manually
- **Judge submission**: Use judge's test cases to verify before submitting

## Need Help?

Check the actual problem format in `PROBLEM.txt` to understand the exact input structure for your specific problem.

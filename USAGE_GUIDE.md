# How to Use optimal.py for Meta HackerCup

## 📋 Solution Usage Guide

Your `workspace/optimal.py` solution supports **multiple input/output modes**:

---

## ✅ Method 1: File Input/Output (Recommended)

### Basic Usage:
```bash
python workspace/optimal.py input.txt
```

**What happens:**
- Reads from `input.txt`
- Automatically creates `input_output.txt`
- Shows progress and preview

### Custom Output File:
```bash
python workspace/optimal.py input.txt output.txt
```

**What happens:**
- Reads from `input.txt`
- Writes to `output.txt` (your specified file)

### Example:
```bash
# Download input from Meta HackerCup (e.g., input.txt)
python workspace/optimal.py input.txt

# Output will be in: input_output.txt
# Ready to submit!
```

---

## ✅ Method 2: Standard Input/Output

### Using Redirection:
```bash
python workspace/optimal.py < input.txt > output.txt
```

**What happens:**
- Reads from stdin (`< input.txt`)
- Writes to stdout (`> output.txt`)

---

## ✅ Method 3: Interactive Mode

### No Arguments:
```bash
python workspace/optimal.py
```

**What happens:**
- Reads from stdin (terminal input)
- Writes to stdout (terminal output)
- Useful for testing small inputs

---

## 📝 Input Format

Based on your problem statement, the input format is:

```
T
N1 M1
N2 M2
...
NT MT
```

Where:
- `T` = number of test cases
- Each test case: two integers `N` and `M`

### Example Input:
```
3
4 3
5 3
6 3
```

---

## 📝 Output Format

The solution generates:

```
Case #1: YES
Case #2: NO
Case #3: YES
```

---

## 🚀 Complete Workflow for Meta HackerCup

### Step 1: Generate Solution
```bash
source venv/bin/activate
python main.py
```

This generates `workspace/optimal.py`

### Step 2: Download Input from HackerCup
- Download the input file (e.g., `input.txt`)

### Step 3: Run Your Solution
```bash
python workspace/optimal.py input.txt
```

### Step 4: Submit Output
- The output will be in `input_output.txt`
- Upload this file to Meta HackerCup

---

## 🔍 Verification

After running, you'll see:
```
✓ Processed 100 test cases
✓ Output written to: input_output.txt

First 3 outputs:
Case #1: YES
Case #2: NO
Case #3: YES
...
```

---

## ⚠️ Troubleshooting

### Error: "Invalid input format"
- Check that your input file matches the expected format
- Ensure each test case has exactly 2 integers (N and M)

### Error: "File not found"
- Make sure the input file path is correct
- Use absolute path if needed: `python workspace/optimal.py /full/path/to/input.txt`

### Error: "Unexpected end of file"
- Check that your input file has all test cases
- Verify the number of test cases matches T

---

## 💡 Tips

1. **Always test with sample inputs first** before running on full input
2. **Check output format** - should be "Case #i: YES" or "Case #i: NO"
3. **Save output file** - The output file is ready for submission
4. **Use file mode** - Easier than stdin/stdout redirection

---

**Your solution is ready! Just run:** `python workspace/optimal.py input.txt` 🎯


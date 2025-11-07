# Multi-Solution Generation Feature

## Overview
This feature allows the system to generate multiple brute force solutions and automatically select the best working one, improving reliability and success rate.

## How It Works

### 1. Configuration
Update `config.yaml` to set the number of candidates:

```yaml
execution:
  num_brute_candidates: 3  # Number of brute force solution candidates to generate and test
```

Recommended values: 3-5 candidates for best results.

### 2. Generation Phase
The BruteAgent now generates multiple solution candidates with:
- **Higher temperature** (0.7 instead of 0.3) for more diverse solutions
- **Prompt variation** to encourage different approaches
- **Multiple iterations** (configurable via num_brute_candidates)

### 3. Testing Phase
The orchestrator:
- Tests each generated candidate
- Executes each solution with test cases
- Tracks success/failure for each attempt
- Saves all candidates to workspace (brute_candidate_1.py, brute_candidate_2.py, etc.)

### 4. Selection Phase
The system:
- Automatically selects the first working solution
- Uses that solution as the "ground truth" brute force solution
- Continues with optimal solution generation using the selected brute force solution

## Example Output

```
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
✗ Solution 3 execution failed: runtime error

✓ Selected best brute force solution (from 3 candidates)
✓ Brute force solution saved to: ./workspace/brute.py
✓ Brute force outputs saved to: ./workspace/small_outputs.txt
```

## Files Created

During execution, the following files are created:
- `workspace/brute_candidate_1.py` - First generated solution
- `workspace/brute_candidate_2.py` - Second generated solution
- `workspace/brute_candidate_3.py` - Third generated solution
- `workspace/brute_candidate_1_output.txt` - Output from first solution
- `workspace/brute_candidate_2_output.txt` - Output from second solution
- `workspace/brute_candidate_3_output.txt` - Output from third solution

The best working solution is saved as:
- `workspace/brute.py` - Final selected brute force solution
- `workspace/small_outputs.txt` - Output from selected solution

## Benefits

1. **Higher Success Rate**: If one solution fails, others may succeed
2. **Diversity**: Different approaches are explored (iterative, recursive, etc.)
3. **Automatic Selection**: No manual intervention needed
4. **Robustness**: System is more resilient to LLM-generated errors
5. **Transparency**: All candidates are saved for inspection

## Configuration Options

### Number of Candidates
Adjust in `config.yaml`:
```yaml
num_brute_candidates: 5  # Generate 5 candidates instead of 3
```

**Considerations:**
- More candidates = better chances but longer generation time
- Recommended: 3-5 candidates for best balance

### Temperature
The temperature is already optimized at 0.7 for diversity. If you want to modify it, edit `agents/brute_agent.py`:
```python
self.model = ChatGoogleGenerativeAI(model=model, temperature=0.7)
```

## Troubleshooting

### If all candidates fail:
1. Check that test inputs are valid
2. Verify problem statement is clear
3. Try increasing num_brute_candidates
4. Check error messages in metadata['brute_attempts']

### If selection is slow:
1. Reduce num_brute_candidates
2. Check timeout_seconds setting
3. Optimize test case generation

## Metadata Tracking

The system tracks all brute force attempts in metadata:
```python
metadata['brute_attempts'] = [
    {
        'number': 1,
        'code': '...',
        'execution_success': True,
        'has_output': True,
        'selected': True,
        'error': None
    },
    # ... more attempts
]
```

This data is saved in `results.json` for analysis.

## Future Enhancements

Potential improvements:
1. **Smart Selection**: Not just first working, but best performing
2. **Partial Credit**: Select solution with best partial match
3. **Confidence Scoring**: Assign scores to each candidate
4. **Parallel Execution**: Test multiple candidates in parallel
5. **Retry Logic**: Generate more if all fail

## Usage Example

```bash
# Run the enhanced system
python main.py

# The system will automatically:
# 1. Generate 3 brute force solutions
# 2. Test each one
# 3. Pick the best working solution
# 4. Continue with optimal solution generation
```

## Notes

- The brute force solution selection happens before optimal solution generation
- Only the selected brute force solution is used for comparison
- Candidate solutions are preserved for debugging and analysis
- Each candidate uses the same test cases for fair comparison

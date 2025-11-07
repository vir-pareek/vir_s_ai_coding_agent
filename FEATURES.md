# New Features: WebSearchAgent, Enhanced Prompts & Multi-Solution Generation

## Overview
This document describes the major features that have been added to the Meta-HackerCup-AI-StarterKit project:
1. **WebSearchAgent** - Enables models to search and learn algorithm approaches on the fly
2. **Enhanced Prompts** - Problem-specific hints (DP, greedy, graph) and complexity targets
3. **Multi-Solution Generation** - Generates multiple brute force solutions and picks the best one

## Feature 1: WebSearchAgent

### What It Does
The `WebSearchAgent` is a new agent that:
- Analyzes problem statements to identify algorithmic approaches
- Searches for relevant algorithm knowledge and problem-solving strategies
- Provides structured insights about the best algorithmic approach
- Extracts hints including algorithm type, key insights, complexity targets, and suggested data structures

### Files Created/Modified

#### New Files:
- `agents/web_search_agent.py` - The main WebSearchAgent implementation
- `utils/problem_analyzer.py` - Utility to analyze problems and extract hints

#### Modified Files:
- `agents/__init__.py` - Added WebSearchAgent export
- `utils/__init__.py` - Added analyze_problem export
- `config.yaml` - Added web_search_agent configuration
- `orchestrator.py` - Integrated WebSearchAgent into the problem-solving pipeline

### How It Works

1. **Problem Analysis**: The `analyze_problem()` function from `utils/problem_analyzer.py` analyzes the problem statement to extract:
   - Algorithm hints (DP, Greedy, Graph, etc.)
   - Complexity targets (time/space complexity)
   - Key constraints (max n, array size, etc.)
   - Problem category (Arrays, Graphs, Trees, etc.)
   - Suggested data structures

2. **Web Search (Optional)**: If `web_search_agent` is configured in `config.yaml`, it can be used to:
   - Search for algorithm approaches based on problem description
   - Provide additional algorithmic insights
   - Suggest specific algorithms (e.g., "Kadane's algorithm for max subarray sum")

3. **Integration**: The orchestrator uses these hints to enhance the prompts for both brute and optimal agents

## Feature 2: Enhanced Prompts

### What It Does
The agent prompts have been enhanced to include:
- **Algorithm Type**: Detection of algorithm paradigms (DP, Greedy, Graph, etc.)
- **Key Insights**: Problem-specific insights (e.g., "track current sum and maximum so far")
- **Complexity Targets**: Expected time/space complexity based on constraints
- **Suggested Data Structures**: Recommended data structures for the solution

### Files Modified:

#### BruteAgent (`agents/brute_agent.py`)
- Added `hints` parameter to `generate_solution()` method
- Added `_build_system_prompt()` method to dynamically build prompts with hints
- Prompts now include problem-specific algorithmic hints

#### OptimalAgent (`agents/optimal_agent.py`)
- Added `hints` parameter to `generate_solution()` method
- Added `_build_system_prompt()` method to dynamically build prompts with hints
- Prompts now include complexity targets and algorithm type

#### Orchestrator (`orchestrator.py`)
- Added Step 0: Problem analysis and hint extraction
- Passes hints to both brute_agent and optimal_agent
- Integrates WebSearchAgent results (if configured) into the hints

### Example Hints Generated

For the current problem (max subarray sum):
```
Algorithm Type: Dynamic Programming, Two Pointers
Target Complexity: O(n) time, O(1) space
Key Insight: Kadane's algorithm (max subarray sum) - track current sum and maximum so far
Suggested Data Structures: Two Pointers, Array/List
```

## Configuration

### config.yaml

```yaml
models:
  tester_agent: "google:gemini-2.5-flash"    
  brute_agent: "google:gemini-2.5-flash"     
  optimal_agent: "google:gemini-2.5-flash"
  web_search_agent: "google:gemini-2.5-flash"   # Optional
```

Note: `web_search_agent` is optional. If not configured, the system will work with basic problem analysis only.

## Usage

### Running the Enhanced System

```bash
python main.py
```

The system will now:
1. **Analyze the problem** to extract hints (DP, greedy, graph, etc.)
2. **Optionally search** for algorithm approaches (if web_search_agent configured)
3. **Generate brute force solution** with enhanced hints
4. **Generate optimal solution** with complexity targets and algorithm hints
5. **Iterate** with improved feedback based on hints

### Output

The enhanced system will display:
```
================================================================================
STEP 0: Analyzing problem and extracting hints...
================================================================================

✓ Problem analysis complete:
Algorithm Type: Dynamic Programming, Two Pointers
Target Complexity: O(n) time, O(1) space
Key Insight: Kadane's algorithm (max subarray sum) - track current sum and maximum so far
Suggested Data Structures: Two Pointers, Array/List

Additional Algorithm Research:
[WebSearchAgent results here if configured]
```

## Feature 3: Multi-Solution Generation

### What It Does
The brute force solution generation now creates multiple candidate solutions and automatically selects the best working one. This increases the probability of getting a correct brute force solution.

### Key Changes

#### BruteAgent (`agents/brute_agent.py`)
- Added `num_candidates` parameter (default: 3)
- Increased temperature to 0.7 for more diverse solution generation
- New method `generate_multiple_solutions()` that:
  - Generates multiple brute force solution candidates
  - Uses prompt variation to get different approaches
  - Returns a list of solution dictionaries

#### Orchestrator (`orchestrator.py`)
- Step 2 now generates multiple brute force candidates
- Step 3 tests each candidate and selects the best one
- Tracks all brute force attempts in metadata
- Saves candidate solutions as `brute_candidate_1.py`, `brute_candidate_2.py`, etc.
- Automatically picks the first working solution

#### Configuration (`config.yaml`)
- Added `num_brute_candidates: 3` to execution parameters
- Configurable number of candidates to generate (recommended: 3-5)

### Example Flow

```
STEP 2: Generating multiple brute force solutions...
✓ Generated 3 brute force solution candidates

STEP 3: Testing and selecting best brute force solution...

Testing brute force solution 1/3...
✗ Solution 1 execution failed: syntax error

Testing brute force solution 2/3...
✓ Solution 2 executed successfully
→ Solution 2 selected as best so far

Testing brute force solution 3/3...
✓ Solution 3 executed successfully

✓ Selected best brute force solution (from 3 candidates)
```

### Benefits

1. **Better Code Generation**: Agents receive specific hints about which algorithms to use
2. **Complexity Awareness**: Agents know the expected time/space complexity targets
3. **Algorithm Selection**: Automatic detection of the right algorithm paradigm (DP, Greedy, etc.)
4. **Learning on the Fly**: WebSearchAgent can search for algorithm approaches when needed
5. **Improved Success Rate**: More targeted prompts lead to better solutions faster
6. **Robust Brute Force**: Multiple candidates increase chances of getting a working solution
7. **Automatic Selection**: System picks the best solution automatically based on test results

## Algorithm Detection Examples

The problem analyzer detects various algorithm types:

- **Dynamic Programming**: Subproblem, overlapping, memoization
- **Greedy**: Greedy algorithm, local optimum
- **Graph**: Graph, node, edge, BFS, DFS
- **Sorting**: Sort, ordered, ascending
- **Binary Search**: Search, sorted array, binary search
- **Two Pointers**: Two pointers, sliding window, contiguous
- **Stack**: Stack, LIFO, nearest
- **Queue**: Queue, FIFO, BFS
- **Hash Map**: Frequency, count, lookup
- And more...

## Troubleshooting

### If WebSearchAgent is not working:
1. Check that `web_search_agent` is configured in `config.yaml`
2. Ensure Google API key is set correctly
3. If web search fails, the system will continue with basic problem analysis

### If hints are not helpful:
- The system is designed to be resilient
- If problem analysis fails, agents will work without hints
- The basic agent prompts still work as before

## Future Enhancements

Potential improvements:
1. Cache problem analysis results to avoid re-analyzing same problems
2. Add more algorithm types and heuristics
3. Integrate with external algorithm databases
4. Add problem difficulty classification
5. Provide multiple solution paths when initial approaches fail

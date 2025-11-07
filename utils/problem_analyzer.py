"""
Problem analyzer utility to extract algorithmic hints and complexity targets.
"""

import re
from typing import Dict, List, Tuple


def analyze_problem(problem_statement: str) -> Dict[str, any]:
    """
    Analyze problem statement to extract algorithmic hints and complexity targets.
    
    Returns a dictionary with:
    - algorithm_hints: List of potential algorithm types (e.g., ['DP', 'Greedy'])
    - complexity_target: Expected time/space complexity
    - key_constraints: Important constraints (max n, time limit, etc.)
    - problem_category: Category of problem (arrays, graphs, strings, etc.)
    """
    result = {
        'algorithm_hints': [],
        'complexity_target': {
            'time': None,
            'space': None
        },
        'key_constraints': {},
        'problem_category': 'General',
        'algorithm_type': 'General',
        'key_insight': '',
        'data_structures': []
    }
    
    # Convert to lowercase for pattern matching
    problem_lower = problem_statement.lower()
    
    # Extract constraints (n <= X, time limit, etc.)
    n_constraint = re.search(r'n\s*<=\s*(\d+(?:\*\*\d+)?|\d+)', problem_statement, re.IGNORECASE)
    if n_constraint:
        result['key_constraints']['max_n'] = n_constraint.group(1)
    
    # Identify algorithm hints from keywords
    algorithm_keywords = {
        'Dynamic Programming': ['subproblem', 'overlapping', 'optimal substructure', 'memoization', 'dp', 'recursion with cache'],
        'Greedy': ['greedy', 'local optimum', 'greedy algorithm', 'best choice'],
        'Graph': ['graph', 'node', 'edge', 'bfs', 'dfs', 'traversal', 'shortest path', 'adjacency'],
        'Sorting': ['sort', 'ordered', 'ascending', 'descending', 'median'],
        'Binary Search': ['search', 'sorted array', 'binary search', 'bisect'],
        'Two Pointers': ['two pointers', 'sliding window', 'contiguous'],
        'Stack': ['stack', 'lifo', 'nearest', 'next greater'],
        'Queue': ['queue', 'fifo', 'bfs', 'level order'],
        'Hash Map': ['frequency', 'count', 'lookup', 'occurrence', 'unique'],
        'Union Find': ['disjoint set', 'union find', 'connected components'],
        'Prefix Sum': ['prefix sum', 'cumulative sum', 'range sum'],
        'Tree': ['tree', 'binary tree', 'bst', 'traversal', 'node', 'leaf'],
        'String': ['string', 'substring', 'anagram', 'palindrome', 'matching'],
        'Array': ['array', 'subarray', 'contiguous', 'sequence'],
    }
    
    for algo_type, keywords in algorithm_keywords.items():
        for keyword in keywords:
            if keyword in problem_lower:
                if algo_type not in result['algorithm_hints']:
                    result['algorithm_hints'].append(algo_type)
                if result['algorithm_type'] == 'General':
                    result['algorithm_type'] = algo_type
                break
    
    # Infer complexity targets from constraints
    if 'max_n' in result['key_constraints']:
        n = result['key_constraints']['max_n']
        
        # Simple heuristic: scale the expected complexity
        try:
            # Try to parse as 10^9, 10^5, etc.
            if '**' in n:
                exp = n.split('**')[-1]
                max_val = 10 ** int(exp)
            else:
                max_val = int(n)
            
            # Infer expected complexity from n
            if max_val <= 100:
                result['complexity_target']['time'] = 'O(n^3) or easier'
                result['complexity_target']['space'] = 'O(n)'
            elif max_val <= 1000:
                result['complexity_target']['time'] = 'O(n^2)'
                result['complexity_target']['space'] = 'O(n)'
            elif max_val <= 100000:
                result['complexity_target']['time'] = 'O(n log n) or O(n)'
                result['complexity_target']['space'] = 'O(1) or O(n)'
            else:
                result['complexity_target']['time'] = 'O(n log n) or O(n)'
                result['complexity_target']['space'] = 'O(1) or O(n)'
        except:
            pass
    
    # Identify data structure hints
    data_structure_keywords = {
        'Array/List': ['array', 'list', 'sequence'],
        'HashMap/Dict': ['frequency', 'count', 'occurrence', 'lookup'],
        'Stack': ['stack', 'push', 'pop', 'nearest'],
        'Queue': ['queue', 'bfs', 'level order'],
        'Tree': ['tree', 'binary tree', 'bst'],
        'Heap': ['heap', 'priority queue', 'min', 'max'],
        'Set': ['unique', 'duplicate', 'contains'],
        'Two Pointers': ['two pointers', 'sliding window']
    }
    
    for ds, keywords in data_structure_keywords.items():
        for keyword in keywords:
            if keyword in problem_lower:
                if ds not in result['data_structures']:
                    result['data_structures'].append(ds)
                break
    
    # Identify problem category
    category_keywords = {
        'Arrays': ['array', 'subarray', 'contiguous', 'sequence'],
        'Graph': ['graph', 'node', 'edge', 'adjacency'],
        'String': ['string', 'substring', 'anagram', 'palindrome'],
        'Tree': ['tree', 'binary tree', 'bst', 'node', 'leaf'],
        'Dynamic Programming': ['dynamic programming', 'dp', 'subproblem'],
        'Greedy': ['greedy', 'optimal choice', 'local optimum'],
        'Math': ['sum', 'product', 'factorial', 'gcd', 'prime', 'divisor'],
        'Search': ['search', 'find', 'lookup', 'binary search'],
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in problem_lower for keyword in keywords):
            result['problem_category'] = category
            break
    
    # Extract key insight based on problem
    if 'subarray' in problem_lower and 'maximum' in problem_lower and 'sum' in problem_lower:
        result['key_insight'] = 'Kadane\'s algorithm (max subarray sum) - track current sum and maximum so far'
        result['algorithm_type'] = 'Dynamic Programming'
        result['algorithm_hints'] = ['Dynamic Programming', 'Two Pointers']
        result['complexity_target'] = {'time': 'O(n)', 'space': 'O(1)'}
        result['data_structures'] = ['Two Pointers', 'Array/List']
    
    # Recommend parallel approaches based on problem analysis
    recommended_approaches = []
    for algo in result['algorithm_hints']:
        if algo not in recommended_approaches:
            recommended_approaches.append(algo)
    
    # Add complementary approaches
    if 'Dynamic Programming' in result['algorithm_hints']:
        recommended_approaches.append('Greedy')  # Try greedy as alternative
    if 'Greedy' in result['algorithm_hints']:
        recommended_approaches.append('Dynamic Programming')  # Try DP as alternative
    
    # Limit to top 3 approaches for parallel generation
    result['recommended_approaches'] = recommended_approaches[:3]
    
    # Detect problem difficulty for model selection
    problem_complexity = 'Easy'  # Default
    max_n_val = result['key_constraints'].get('max_n', '100')
    
    try:
        if '**' in str(max_n_val):
            exp = str(max_n_val).split('**')[-1]
            n = 10 ** int(exp)
        else:
            n = int(max_n_val)
        
        if n >= 10**9:
            problem_complexity = 'Competition'
        elif n >= 10**6:
            problem_complexity = 'Hard'
        elif n >= 10**4:
            problem_complexity = 'Medium'
        else:
            problem_complexity = 'Easy'
    except:
        pass
    
    result['problem_complexity'] = problem_complexity
    
    # Format hints for prompt
    hints_summary = ""
    if result['algorithm_hints']:
        hints_summary += f"Algorithm Type: {', '.join(result['algorithm_hints'])}\n"
    if result['complexity_target']['time']:
        hints_summary += f"Target Complexity: {result['complexity_target']['time']} time, {result['complexity_target']['space']} space\n"
    if result['key_insight']:
        hints_summary += f"Key Insight: {result['key_insight']}\n"
    if result['data_structures']:
        hints_summary += f"Suggested Data Structures: {', '.join(result['data_structures'])}\n"
    
    # Add recommended approaches to hints summary
    if result.get('recommended_approaches'):
        hints_summary += f"Recommended Approaches: {', '.join(result['recommended_approaches'])}\n"
    
    hints_summary += f"Problem Difficulty: {result.get('problem_complexity', 'Unknown')}\n"
    
    result['hints_summary'] = hints_summary
    
    return result

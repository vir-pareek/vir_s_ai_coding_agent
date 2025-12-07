import sys
import collections
import bisect

def solve():
    N, M = map(int, sys.stdin.readline().strip().split())
    A = list(map(int, sys.stdin.readline().strip().split()))
    B = list(map(int, sys.stdin.readline().strip().split()))

    # Group competitors by score and count them
    score_counts = collections.defaultdict(int)
    for score in A:
        score_counts[score] += 1
    
    # Sort groups by score in descending order
    # groups will be a list of (score, count) tuples
    groups = sorted(score_counts.items(), key=lambda item: item[0], reverse=True)

    # Binary search for the maximum number of groups (p) that can be rewarded
    # p is the number of distinct score groups, not total competitors
    low = 0
    high = min(len(groups), M) # Max groups cannot exceed M (since each group needs at least 1 unit)
    ans_p = 0

    while low <= high:
        mid_p = (low + high) // 2
        if mid_p == 0: # 0 groups can always be rewarded
            ans_p = max(ans_p, mid_p)
            low = mid_p + 1
            continue

        # Check if it's possible to reward 'mid_p' groups
        # The groups are groups[0]...groups[mid_p-1]
        # Group groups[j] (0-indexed) needs (mid_p - j) units of merchandise
        
        # Create demands: (competitor_count, units_needed)
        demands = []
        for j in range(mid_p):
            competitor_count = groups[j][1]
            units_needed = mid_p - j
            demands.append((competitor_count, units_needed))
        
        # Sort demands by competitor_count in descending order
        # This is a greedy choice: satisfy groups with more competitors first
        demands.sort(key=lambda x: x[0], reverse=True)

        # Available merchandise capacities
        # Using a sorted list and bisect for multiset-like behavior
        # This is the part that could be slow (O(p^2 log M)) but is the "brute force" simulation
        current_B = sorted(B) # Make a copy and sort it

        possible = True
        for comp_count, units_needed in demands:
            
            # Try to find 'units_needed' merchandise types with capacity >= comp_count
            # We want to use the smallest possible capacities to save larger ones
            
            chosen_indices = [] # Indices in current_B to remove
            chosen_values = [] # Values to update and re-insert
            
            # Find units_needed items
            temp_current_B = list(current_B) # Copy to iterate and find
            
            # This is the slow part: iterating and finding items one by one
            # The actual implementation of a multiset with lower_bound and erase/insert
            # would be faster if it were a C++ multiset, but Python's list operations
            # make this O(M) per find/remove/insert.
            # A better Python approach would be to use a Fenwick tree or segment tree
            # on the values of B, but that's not "brute force" in the sense of simple simulation.
            
            # To simulate multiset.lower_bound and erase/insert efficiently in Python
            # for this specific problem, we can use a frequency array/dictionary for B values
            # and iterate through it. However, the problem constraints (B_i up to 10^6)
            # make a simple frequency array too large.
            # A sorted list and bisect is the closest simple simulation of a multiset.

            # We need to find `units_needed` items.
            # To do this efficiently, we can't just remove from current_B and re-insert
            # because bisect_left would be on the modified list.
            # We collect all items to remove/update first, then apply changes.
            
            temp_merch_to_update = []
            
            for _ in range(units_needed):
                idx = bisect.bisect_left(current_B, comp_count)
                if idx == len(current_B): # Not enough merchandise types
                    possible = False
                    break
                
                val = current_B[idx]
                temp_merch_to_update.append((idx, val)) # Store (original_index, value) for removal
                current_B.pop(idx) # Temporarily remove to find next smallest
                
            if not possible:
                break
            
            # Now, re-insert updated values
            for original_idx, val in temp_merch_to_update:
                new_val = val - comp_count
                bisect.insort_left(current_B, new_val) # Re-insert into sorted list
                
        if possible:
            ans_p = max(ans_p, mid_p)
            low = mid_p + 1
        else:
            high = mid_p - 1
            
    # Calculate total competitors rewarded based on ans_p
    total_rewarded_competitors = 0
    for j in range(ans_p):
        total_rewarded_competitors += groups[j][1]

    return total_rewarded_competitors

T = int(sys.stdin.readline().strip())
for i in range(1, T + 1):
    result = solve()
    sys.stdout.write(f"Case #{i}: {result}\n")
import sys
from bisect import bisect_left

# Segment Tree for range maximum query and point update
class SegmentTree:
    def __init__(self, size):
        self.size = size
        self.tree = [0] * (4 * size)

    # Updates the value at a specific index in the segment tree.
    # node: current node index in the tree array
    # start, end: range covered by the current node
    # idx: the index to update (in terms of unique_vals ranks)
    # val: the new value to set (max with existing)
    def update(self, node, start, end, idx, val):
        if start == end:
            self.tree[node] = max(self.tree[node], val)
            return
        
        mid = (start + end) // 2
        if start <= idx <= mid:
            self.update(2 * node, start, mid, idx, val)
        else:
            self.update(2 * node + 1, mid + 1, end, idx, val)
        
        self.tree[node] = max(self.tree[2 * node], self.tree[2 * node + 1])

    # Queries for the maximum value in a given range [l, r].
    # node: current node index in the tree array
    # start, end: range covered by the current node
    # l, r: query range
    def query(self, node, start, end, l, r):
        # If query range is outside current segment or invalid
        if r < start or end < l or l > r:
            return 0 # Identity for max operation (no elements, max is 0)
        
        # If current segment is completely within query range
        if l <= start and end <= r:
            return self.tree[node]
        
        # Partially overlapping, recurse
        mid = (start + end) // 2
        p1 = self.query(2 * node, start, mid, l, r)
        p2 = self.query(2 * node + 1, mid + 1, end, l, r)
        return max(p1, p2)

def solve():
    n = int(sys.stdin.readline())
    a = list(map(int, sys.stdin.readline().split()))

    k = n // 2 # Number of elements Alex locks

    # check(D) function: Can Hao achieve a beauty of at most D?
    # This means: Is there a subsequence of length k such that for any two elements b_x, b_y
    # in the subsequence (with b_x appearing before b_y), b_y - b_x <= D?
    # This condition is equivalent to: for every element b_y in the subsequence, and every
    # b_x that appears before it in the subsequence, b_y - b_x <= D.
    # This implies that b_y must be at most D greater than any b_x that precedes it.
    # This is equivalent to: for a subsequence ending at a[i], a[i] - min_val_in_subsequence <= D.
    # We use dynamic programming with a segment tree.
    # dp[i] = max length of such a subsequence ending at a[i].
    # To compute dp[i], we look for max(dp[j]) for j < i such that a[j] >= a[i] - D.
    def check(D):
        # Coordinate compression for values in 'a'
        # The segment tree will operate on ranks of values.
        unique_vals = sorted(list(set(a)))
        val_to_rank = {val: i for i, val in enumerate(unique_vals)}
        
        seg_tree = SegmentTree(len(unique_vals))
        max_len_found = 0

        for val_a_i in a:
            rank_a_i = val_to_rank[val_a_i]
            
            # We need a_j >= val_a_i - D for a predecessor a_j.
            # Find the rank corresponding to the minimum value a_j can take.
            lower_bound_val = val_a_i - D
            lower_bound_rank = bisect_left(unique_vals, lower_bound_val)
            
            # Query for max dp value in the range of ranks [lower_bound_rank, rank_a_i].
            # This range covers all a_j values such that:
            # 1. a_j >= lower_bound_val (i.e., a_j >= val_a_i - D)
            # 2. a_j <= val_a_i (because rank_a_i is the upper bound for ranks, and values are sorted)
            # The condition j < i is handled by iterating through 'a' and only updating
            # the segment tree with dp values for elements processed so far.
            prev_max_len = seg_tree.query(1, 0, len(unique_vals) - 1, lower_bound_rank, rank_a_i)
            
            current_len = 1 + prev_max_len
            seg_tree.update(1, 0, len(unique_vals) - 1, rank_a_i, current_len)
            max_len_found = max(max_len_found, current_len)
        
        return max_len_found >= k

    # Binary search for the minimum D
    # The range of possible beauty values can be from -(10^9 - 1) to (10^9 - 1).
    # A safe range for binary search is from -2*10^9 to 2*10^9.
    low = -2 * (10**9) 
    high = 2 * (10**9) 
    ans = high # Initialize with a value that is definitely achievable (max possible)

    while low <= high:
        mid = low + (high - low) // 2
        if check(mid):
            ans = mid       # mid is achievable, try for a smaller D
            high = mid - 1
        else:
            low = mid + 1   # mid is not achievable, need a larger D
            
    sys.stdout.write(str(ans) + "\n")

# Read the number of test cases
num_test_cases = int(sys.stdin.readline())
for _ in range(num_test_cases):
    solve()
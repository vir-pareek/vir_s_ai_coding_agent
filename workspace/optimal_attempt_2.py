import sys
import math

def solve():
    """
    Solves a single test case for the Podium problem.

    The problem asks to find a non-increasing sequence of non-negative integers
    x_1, x_2, ..., x_N that minimizes the total sum (number of bricks)
    sum(x_i), subject to the constraint that the total "amazingness"
    sum(A_i * x_i) is at least M.

    The core idea is to transform the variables. Let d_i be the difference
    in height between adjacent platforms:
    x_N = d_N
    x_{N-1} = d_{N-1} + d_N
    ...
    x_1 = d_1 + d_2 + ... + d_N
    The constraint x_i >= x_{i+1} >= 0 becomes d_i >= 0 for all i.

    In terms of d_i, the objectives become:
    - Minimize total bricks: sum(x_i) = sum_{i=1 to N} (i * d_i)
    - Amazingness constraint: sum(A_i * x_i) = sum_{i=1 to N} (B_i * d_i) >= M,
      where B_i = A_1 + ... + A_i is the prefix sum of amazingness values.

    This transforms the problem into a variation of the unbounded knapsack or
    change-making problem: for each i from 1 to N, we have an "item" with
    cost `i` and value `B_i`. We want to achieve a total value of at least M
    with minimum total cost.

    To solve this, we can use a greedy approach with a correction. The most
    "efficient" item is the one that provides the most value per unit of cost,
    i.e., maximizes the ratio B_i / i. Let k_0 be the index that maximizes
    this ratio.

    A key insight is that in an optimal solution, any other item `j != k_0`
    will be used a limited number of times. Specifically, we will use fewer
    than k_0 copies of item `j` (i.e., d_j < k_0). This is because k_0 copies
    of item `j` cost `j * k_0` and give `j * B_{k_0}` amazingness, which is less
    than the `k_0 * B_j` amazingness from `j` copies of item `k_0` for the same cost.

    This suggests that the optimal solution is likely composed of many copies
    of the most efficient item `k_0`, and a small number of copies of at most
    one other item `j` to "fine-tune" the total amazingness and potentially
    achieve a lower total cost.

    The algorithm is as follows:
    1. Precompute prefix sums B_i of the amazingness array A.
    2. Find the index k_0 that maximizes the efficiency ratio B_k / k.
    3. Calculate a baseline minimum number of bricks using only item k_0.
    4. Iterate through all other possible items j (from 1 to N).
    5. For each j, iterate through the number of times we use it, d_j, from
       1 up to k_0 - 1.
    6. For each combination of (j, d_j), calculate the remaining amazingness
       needed from item k_0. Compute the required number of d_{k_0} and the
       total bricks.
    7. Keep track of the combination that results in the minimum total bricks.
    8. Once the minimum bricks and the corresponding d_i values are found,
       reconstruct the platform heights x_i.

    This approach has a time complexity of O(N*k_0), which is at most O(N^2),
    making it efficient enough for the given constraints.
    """
    N, M = map(int, sys.stdin.readline().strip().split())
    A = list(map(int, sys.stdin.readline().strip().split()))

    B = [0] * (N + 1)
    for i in range(N):
        B[i+1] = B[i] + A[i]

    best_k_idx = -1
    
    # Find k_0 that maximizes B_k / k.
    # To avoid floating point issues, we compare B_k * best_k vs B_{best_k} * k.
    # In case of a tie in the ratio, we can pick any, but picking the smallest k
    # can sometimes tighten bounds (not strictly necessary for this logic).
    for i in range(1, N + 1):
        if B[i] <= 0: continue
        if best_k_idx == -1:
            best_k_idx = i
        else:
            if B[i] * best_k_idx > B[best_k_idx] * i:
                best_k_idx = i

    # If all prefix sums are non-positive, no solution is possible if M > 0.
    # The problem constraints likely ensure B_i > 0.
    if best_k_idx == -1:
        # This case should not happen with problem constraints 1 <= A_i
        # but as a safeguard:
        if M == 0:
            x = [0] * N
            return f"0\n{' '.join(map(str, x))}"
        else: # Should be impossible
            return "IMPOSSIBLE"


    k0 = best_k_idx
    B0 = B[k0]

    min_bricks = float('inf')
    best_d = {}

    # Case 1: Baseline solution using only the most efficient item d_{k0}.
    d_k0_only = (M + B0 - 1) // B0
    w_only = k0 * d_k0_only
    min_bricks = w_only
    best_d = {k0: d_k0_only}

    # Case 2: Try combining d_{k0} with one other item d_j.
    for j in range(1, N + 1):
        if j == k0:
            continue
        
        # The number of times we use a suboptimal item `j` is bounded by `k0`.
        # We iterate d_j from 1 to k0-1. The d_j=0 case is the baseline.
        limit = k0
        for dj_val in range(1, limit):
            rem_M = M - dj_val * B[j]
            
            d_k0 = 0
            if rem_M > 0:
                d_k0 = (rem_M + B0 - 1) // B0

            current_bricks = k0 * d_k0 + j * dj_val
            if current_bricks < min_bricks:
                min_bricks = current_bricks
                best_d = {k0: d_k0, j: dj_val}

    # Reconstruct the solution from the best d_i values found.
    final_d = [0] * (N + 1)
    for k, v in best_d.items():
        final_d[k] = v

    x = [0] * N
    current_sum_d = 0
    for i in range(N, 0, -1):
        current_sum_d += final_d[i]
        x[i-1] = current_sum_d
        
    return f"{min_bricks}\n{' '.join(map(str, x))}"


def main():
    try:
        T_str = sys.stdin.readline().strip()
        if not T_str:
            return
        T = int(T_str)
        for i in range(1, T + 1):
            result = solve()
            sys.stdout.write(f"Case #{i}: {result}\n")
    except (IOError, ValueError):
        # Handle potential empty lines or format errors at the end of input
        pass

if __name__ == "__main__":
    main()
import sys

def solve():
    """
    Solves a single test case for the Podium problem.
    """
    try:
        line1 = sys.stdin.readline().strip()
        if not line1: return
        N, M = map(int, line1.split())
        A = list(map(int, sys.stdin.readline().strip().split()))
    except (IOError, ValueError):
        return

    B = [0] * (N + 1)
    for i in range(N):
        B[i+1] = B[i] + A[i]

    k_opt = -1
    max_eff = -1.0

    # Find k_opt with max efficiency B_k/k, breaking ties with smaller k
    for k in range(1, N + 1):
        if B[k] > 0:
            eff = B[k] / k
            if eff > max_eff:
                max_eff = eff
                k_opt = k

    if k_opt == -1:
        # This case implies all A_i are 0, which is ruled out by constraints.
        # If M is 0, a solution of all 0s works. If M > 0, it's impossible.
        # The problem statement implies a solution always exists.
        print("0")
        print(*([0] * N))
        return

    c_max = 0
    items_other_spec = []
    for k in range(1, N + 1):
        if k == k_opt:
            continue
        bound = k_opt - 1
        if bound > 0:
            c_max += k * bound
            items_other_spec.append({'cost': k, 'val': B[k], 'count': bound})

    dp = [-1] * (c_max + 1)
    dp[0] = 0
    parent = [(0, 0, 0)] * (c_max + 1) # (prev_c, k, num_taken)

    for item_spec in items_other_spec:
        k = item_spec['cost']
        val = item_spec['val']
        count = item_spec['count']
        
        power_of_2 = 1
        while count > 0:
            num_to_take = min(count, power_of_2)
            item_cost = num_to_take * k
            item_val = num_to_take * val
            
            for c in range(c_max, item_cost - 1, -1):
                if dp[c - item_cost] != -1:
                    if dp[c - item_cost] + item_val > dp[c]:
                        dp[c] = dp[c - item_cost] + item_val
                        parent[c] = (c - item_cost, k, num_to_take)

            count -= num_to_take
            power_of_2 *= 2

    min_total_bricks = float('inf')
    best_c_other = -1

    # Baseline: only use k_opt
    d_k_opt_only = 0
    if M > 0:
        if B[k_opt] > 0:
            d_k_opt_only = (M + B[k_opt] - 1) // B[k_opt]
        else: # M > 0 but B[k_opt] is 0, impossible to reach M
            d_k_opt_only = float('inf')

    min_total_bricks = k_opt * d_k_opt_only
    best_c_other = 0

    for c in range(1, c_max + 1):
        if dp[c] == -1:
            continue
        v_other = dp[c]
        
        rem_M = M - v_other
        d_k_opt = 0
        if rem_M > 0:
            if B[k_opt] > 0:
                d_k_opt = (rem_M + B[k_opt] - 1) // B[k_opt]
            else:
                continue # Cannot satisfy remaining M
        
        total_bricks = c + k_opt * d_k_opt
        if total_bricks < min_total_bricks:
            min_total_bricks = total_bricks
            best_c_other = c

    d = [0] * (N + 1)
    if best_c_other != -1:
        v_other = dp[best_c_other]
        rem_M = M - v_other
        if rem_M > 0:
            if B[k_opt] > 0:
                d[k_opt] = (rem_M + B[k_opt] - 1) // B[k_opt]
        
        curr_c = best_c_other
        while curr_c > 0:
            prev_c, k, num_taken = parent[curr_c]
            d[k] += num_taken
            curr_c = prev_c

    x = [0] * N
    current_sum_d = 0
    for i in range(N, 0, -1):
        current_sum_d += d[i]
        x[i-1] = current_sum_d
        
    print(min_total_bricks)
    print(*x)


def main():
    try:
        T_str = sys.stdin.readline()
        if not T_str: return
        T = int(T_str)
        for i in range(1, T + 1):
            sys.stdout.write(f"Case #{i}: ")
            solve()
    except (IOError, ValueError):
        return

if __name__ == "__main__":
    main()
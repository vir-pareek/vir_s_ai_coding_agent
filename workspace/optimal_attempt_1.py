import sys

def solve_case():
    """
    Solves a single test case.
    """
    try:
        N_str = sys.stdin.readline()
        if not N_str: return None
        N = int(N_str)
        S_str = sys.stdin.readline().strip()
    except (IOError, ValueError):
        return None

    S = list(S_str)
    num_zeros = S.count('0')
    
    operations = []

    # The number of operations is bounded. 10N is a generous limit.
    # A smaller, safer limit like 2*N is sufficient in practice.
    for _ in range(10 * N + 1):
        
        # Check if sorted
        is_sorted = True
        for i in range(num_zeros):
            if S[i] == '1':
                is_sorted = False
                break
        if is_sorted:
            for i in range(num_zeros, 2 * N):
                if S[i] == '0':
                    is_sorted = False
                    break
        
        if is_sorted:
            break

        # Find misplaced elements
        P = []  # Misplaced '1's (1-indexed)
        for i in range(num_zeros):
            if S[i] == '1':
                P.append(i + 1)

        Q = []  # Misplaced '0's (1-indexed)
        for i in range(num_zeros, 2 * N):
            if S[i] == '0':
                Q.append(i + 1)
        
        if not P:
            break

        k = len(P)
        
        A_core = []
        B_core = []
        
        # Pair up misplaced 1s and 0s
        for i in range(k):
            p_idx = P[i]
            q_idx = Q[i]
            A_core.append(min(p_idx, q_idx))
            B_core.append(max(p_idx, q_idx))

        # Find correctly placed indices
        P_set = set(P)
        Q_set = set(Q)
        Y = []
        for i in range(1, 2 * N + 1):
            if i not in P_set and i not in Q_set:
                Y.append(i)
        
        # Partition Y and add to A and B sets
        num_y_slots = N - k
        Y_A = Y[:num_y_slots]
        Y_B = Y[num_y_slots:]

        A = sorted(A_core + Y_A)
        B = sorted(B_core + Y_B)
        
        operations.append((A, B))

        # Apply the parallel swap operation
        S_old = S[:]
        for i in range(N):
            idx_a = A[i] - 1
            idx_b = B[i] - 1
            S[idx_a] = S_old[idx_b]
            S[idx_b] = S_old[idx_a]

    # Final check if sorted
    is_final_sorted = True
    for i in range(num_zeros):
        if S[i] == '1':
            is_final_sorted = False
            break
    if is_final_sorted:
        for i in range(num_zeros, 2 * N):
            if S[i] == '0':
                is_final_sorted = False
                break

    if not is_final_sorted:
        return "-1"

    output = [str(len(operations))]
    for A, B in operations:
        output.append(" ".join(map(str, A)))
        output.append(" ".join(map(str, B)))
    return "\n".join(output)


def main():
    """
    Main function to handle multiple test cases.
    """
    try:
        T_str = sys.stdin.readline()
        if not T_str: return
        T = int(T_str)
        for i in range(1, T + 1):
            result = solve_case()
            if result is None: break
            sys.stdout.write(f"Case #{i}: {result}\n")
    except (IOError, ValueError):
        return

if __name__ == "__main__":
    main()
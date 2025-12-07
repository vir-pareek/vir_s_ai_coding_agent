import sys

def solve():
    """
    Solves a single test case.
    """
    try:
        line = sys.stdin.readline()
        if not line.strip():
            line = sys.stdin.readline()
        if not line.strip():
            return None
        N = int(line)
        S = sys.stdin.readline().strip()
    except (IOError, ValueError):
        return None

    s_list = list(S)
    num_zeros = s_list.count('0')
    
    operations = []
    
    # A generous loop limit. For 0/1 arrays, sorting network-based
    # approaches converge very quickly, typically in O(log N) operations.
    # N+5 is a safe upper bound that is well within the 10N limit.
    for _ in range(N + 5):
        
        # Check if the string is sorted
        is_sorted_flag = True
        # Check the '0' part
        for i in range(num_zeros):
            if s_list[i] == '1':
                is_sorted_flag = False
                break
        # Check the '1' part if the '0' part was okay
        if is_sorted_flag:
            for i in range(num_zeros, 2 * N):
                if s_list[i] == '0':
                    is_sorted_flag = False
                    break
        
        if is_sorted_flag:
            break
            
        # Identify misplaced elements (using 1-based indexing)
        # P: '1's that should be '0's
        P = [i + 1 for i in range(num_zeros) if s_list[i] == '1']
        # Q: '0's that should be '1's
        Q = [i + 1 for i in range(num_zeros, 2 * N) if s_list[i] == '0']
        
        if not P:
            # This case should be caught by the is_sorted check above,
            # but as a safeguard.
            break
            
        k = len(P)
        
        # The core of the strategy: construct sets A and B to swap
        # misplaced elements.
        
        # For each pair of misplaced elements (one '1', one '0'),
        # put the smaller index into a set for A and the larger for B.
        A_core = []
        B_core = []
        for i in range(k):
            p, q = P[i], Q[i]
            if p < q:
                A_core.append(p)
                B_core.append(q)
            else:
                A_core.append(q)
                B_core.append(p)

        # Y: correctly placed elements
        all_misplaced_indices = set(P) | set(Q)
        Y = sorted([i + 1 for i in range(2 * N) if (i + 1) not in all_misplaced_indices])
        
        # We need to fill A and B to size N. We have k elements in A_core/B_core.
        # We need to add N-k elements from Y to each.
        num_y_to_add = N - k
        
        # Partition Y into two halves: smaller indices and larger indices.
        Y_A = Y[:num_y_to_add]
        Y_B = Y[num_y_to_add:]
        
        # Combine the core misplaced indices with the correctly placed ones.
        A = sorted(A_core + Y_A)
        B = sorted(B_core + Y_B)
        
        operations.append((A, B))
        
        # Apply the swap operation. The swaps happen simultaneously.
        s_orig = list(s_list)
        for i in range(N):
            idx_a = A[i] - 1
            idx_b = B[i] - 1
            s_list[idx_a], s_list[idx_b] = s_orig[idx_b], s_orig[idx_a]

    # Final check after the loop
    is_sorted_final = True
    for i in range(num_zeros):
        if s_list[i] == '1':
            is_sorted_final = False
            break
    if is_sorted_final:
        for i in range(num_zeros, 2 * N):
            if s_list[i] == '0':
                is_sorted_final = False
                break

    if not is_sorted_final:
        return "-1"
    
    output_lines = [str(len(operations))]
    for A, B in operations:
        output_lines.append(" ".join(map(str, A)))
        output_lines.append(" ".join(map(str, B)))
    return "\n".join(output_lines)

def main():
    try:
        T_str = sys.stdin.readline()
        if not T_str: return
        T = int(T_str)
        for i in range(1, T + 1):
            result = solve()
            if result is None: break
            sys.stdout.write(f"Case #{i}: {result}\n")
    except (IOError, ValueError):
        return

if __name__ == "__main__":
    main()
import sys
import bisect

def solve():
    N = int(sys.stdin.readline())
    S = sys.stdin.readline().strip()

    a_indices = []
    b_indices = []
    for i in range(N):
        if S[i] == 'A':
            a_indices.append(i)
        else:
            b_indices.append(i)

    current_l = 0
    current_r = N - 1
    
    last_eater = None
    
    while True:
        alice_made_move = False
        bob_made_move = False

        # Alice's turn
        # Find the leftmost 'A' in the current segment S[current_l ... current_r]
        idx_a_search = bisect.bisect_left(a_indices, current_l)
        
        if idx_a_search < len(a_indices) and a_indices[idx_a_search] <= current_r:
            # Alice can make a move
            k_a = a_indices[idx_a_search]
            current_l = k_a + 1
            last_eater = "Alice"
            alice_made_move = True
        
        # Bob's turn
        # Find the rightmost 'B' in the current segment S[current_l ... current_r]
        idx_b_search = bisect.bisect_right(b_indices, current_r)
        
        if idx_b_search > 0 and b_indices[idx_b_search - 1] >= current_l:
            # Bob can make a move
            k_b = b_indices[idx_b_search - 1]
            current_r = k_b - 1
            last_eater = "Bob"
            bob_made_move = True
            
        # If both players skipped their turn, the game ends.
        if not alice_made_move and not bob_made_move:
            break
        
    return last_eater

num_test_cases = int(sys.stdin.readline())
for i in range(1, num_test_cases + 1):
    result = solve()
    sys.stdout.write(f"Case #{i}: {result}\n")
An elegant and efficient solution in Python for the given problem.
```python
import sys

def solve():
    """
    Solves a single test case for the Nim Sum Dim Sum problem.
    """
    try:
        line1 = sys.stdin.readline()
        if not line1: return
        N = int(line1)
        S = sys.stdin.readline().strip()
    except (IOError, ValueError):
        return

    a_indices = [i for i, char in enumerate(S) if char == 'A']
    b_indices = [i for i, char in enumerate(S) if char == 'B']

    if not a_indices:
        print("Bob")
        return
    if not b_indices:
        print("Alice")
        return

    l, r = 0, N - 1
    a_l_ptr, a_r_ptr = 0, len(a_indices) - 1
    b_l_ptr, b_r_ptr = 0, len(b_indices) - 1
    
    turn_alice = True
    last_mover = ""

    while True:
        # Update pointers to find available pieces in the current range [l, r]
        while a_l_ptr <= a_r_ptr and a_indices[a_l_ptr] < l:
            a_l_ptr += 1
        while a_l_ptr <= a_r_ptr and a_indices[a_r_ptr] > r:
            a_r_ptr -= 1
        
        while b_l_ptr <= b_r_ptr and b_indices[b_l_ptr] < l:
            b_l_ptr += 1
        while b_l_ptr <= b_r_ptr and b_indices[b_r_ptr] > r:
            b_r_ptr -= 1

        alice_can_move = a_l_ptr <= a_r_ptr
        bob_can_move = b_l_ptr <= b_r_ptr

        if (turn_alice and not alice_can_move) and (not turn_alice and not bob_can_move):
             # Both players must skip consecutively
             break
        if not alice_can_move and not bob_can_move:
             # Both players run out of pieces in the same turn cycle
             break

        if turn_alice:
            if not alice_can_move:
                turn_alice = not turn_alice
                continue
            
            last_mover = "Alice"
            
            # Optimal strategy: if a winning move exists, take it.
            # A winning move for Alice is to leave a board with no 'B's.
            # This is possible if the rightmost 'A' is to the right of the rightmost 'B'.
            if not bob_can_move or a_indices[a_r_ptr] > b_indices[b_r_ptr]:
                l = a_indices[a_r_ptr] + 1
            else:
                # Otherwise, play conservatively to prolong the game.
                # Alice eats the leftmost 'A' to remove the fewest other pieces.
                l = a_indices[a_l_ptr] + 1
        else: # Bob's turn
            if not bob_can_move:
                turn_alice = not turn_alice
                continue
            
            last_mover = "Bob"

            # Bob's winning move: leave a board with no 'A's.
            # Possible if the leftmost 'B' is to the left of the leftmost 'A'.
            if not alice_can_move or b_indices[b_l_ptr] < a_indices[a_l_ptr]:
                r = b_indices[b_l_ptr] - 1
            else:
                # Conservative move: eat rightmost 'B'.
                r = b_indices[b_r_ptr] - 1
        
        if l > r:
            break
        
        turn_alice = not turn_alice
    
    print(last_mover)

def main():
    """
    Main function to handle multiple test cases.
    """
    try:
        T_str = sys.stdin.readline()
        if not T_str: return
        T = int(T_str)
        for i in range(1, T + 1):
            print(f"Case #{i}: ", end="")
            solve()
    except (IOError, ValueError):
        return

if __name__ == "__main__":
    main()

```
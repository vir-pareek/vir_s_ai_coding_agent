An elegant and efficient solution in Python for the given problem.
```python
import sys

def solve():
    """
    Solves a single test case for the Nim Sum Dim Sum problem.
    """
    try:
        n_str = sys.stdin.readline()
        if not n_str:
            return None
        n = int(n_str)
        s = sys.stdin.readline().strip()
    except (IOError, ValueError):
        return None

    l, r = 0, n - 1
    a_eaten = 0
    b_eaten = 0
    
    is_alice_turn = True

    # This loop simulates a game where both players play a "conservative"
    # strategy: Alice always takes the leftmost available 'A', and Bob always
    # takes the rightmost available 'B'. This strategy is optimal because
    # it maximizes the opponent's remaining options, making it a safe play that
    # avoids prematurely giving the opponent a win. The winner of this
    # simulated game corresponds to the winner of the actual game.
    while l <= r:
        if is_alice_turn:
            # Alice's turn: find and eat the leftmost 'A'
            a_ptr = l
            while a_ptr <= r and s[a_ptr] != 'A':
                a_ptr += 1
            
            if a_ptr > r:  # No 'A' found for Alice
                break
            
            a_eaten += 1
            l = a_ptr + 1
        else:
            # Bob's turn: find and eat the rightmost 'B'
            b_ptr = r
            while b_ptr >= l and s[b_ptr] != 'B':
                b_ptr -= 1
            
            if b_ptr < l:  # No 'B' found for Bob
                break
            
            b_eaten += 1
            r = b_ptr - 1
        
        is_alice_turn = not is_alice_turn

    # Alice goes first. If she eats more pieces than Bob, she makes the last
    # move in this sequence and wins. If they eat an equal number of pieces,
    # Bob makes the last move, so Bob wins.
    if a_eaten > b_eaten:
        return "Alice"
    else:
        return "Bob"

def main():
    """
    Main function to handle multiple test cases.
    """
    try:
        num_cases_str = sys.stdin.readline()
        if not num_cases_str:
            return
        num_cases = int(num_cases_str)
        for i in range(1, num_cases + 1):
            winner = solve()
            if winner is None:
                break
            print(f"Case #{i}: {winner}")
    except (IOError, ValueError):
        return

if __name__ == "__main__":
    main()

```
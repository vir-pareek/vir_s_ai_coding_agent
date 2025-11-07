def solve():
    N = int(input())
    S = input()

    a_indices = []
    b_indices = []
    for i in range(N):
        if S[i] == 'A':
            a_indices.append(i)
        else:
            b_indices.append(i)

    num_a = len(a_indices)
    num_b = len(b_indices)

    if num_a == 0:
        # Alice has no 'A's, she skips. If Bob has 'B's, he will eat them all.
        # If no 'B's either, the table is empty, which implies no one wins,
        # but problem constraints usually guarantee at least one dish.
        # Assuming num_b > 0 if num_a == 0 and N >= 1.
        return "Bob"
    
    if num_b == 0:
        # Bob has no 'B's, he skips. Alice will eat all 'A's.
        return "Alice"

    # Check for immediate win conditions by isolating opponent's dishes.
    # Alice goes first.
    
    # Alice's immediate win:
    # If Alice can pick an 'A' such that all 'B's are to its left, she wins.
    # She does this by picking the rightmost 'A' (a_indices[-1]).
    # If this 'A' is to the right of the rightmost 'B' (b_indices[-1]),
    # all 'B's will be discarded. Bob will then skip, and Alice wins.
    if a_indices[-1] > b_indices[-1]:
        return "Alice"

    # Bob's immediate win:
    # If Bob can pick a 'B' such that all 'A's are to its right, he wins.
    # He does this by picking the leftmost 'B' (b_indices[0]).
    # If this 'B' is to the left of the leftmost 'A' (a_indices[0]),
    # all 'A's will be discarded. Alice will then skip, and Bob wins.
    # This check happens only if Alice couldn't win immediately.
    if b_indices[0] < a_indices[0]:
        return "Bob"

    # If neither player can win immediately by isolating their dishes,
    # the 'A's and 'B's are interleaved in a way that prevents such a simple win.
    # In this scenario, the game reduces to comparing the number of dishes.
    # Alice has the first turn advantage.
    # If Alice has strictly more 'A's, she can maintain her advantage.
    # If Bob has equal or more 'B's, Alice cannot force a win and Bob will win.
    if num_a > num_b:
        return "Alice"
    else: # num_a <= num_b
        return "Bob"

T = int(input())
for i in range(1, T + 1):
    result = solve()
    print(f"Case #{i}: {result}")
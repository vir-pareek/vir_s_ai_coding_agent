import sys

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

    num_a = len(a_indices)
    num_b = len(b_indices)

    if num_a == 0:
        return "Bob"
    
    if num_b == 0:
        return "Alice"

    if a_indices[-1] > b_indices[-1]:
        return "Alice"

    if b_indices[0] < a_indices[0]:
        return "Bob"
    
    if num_a > num_b:
        return "Alice"
    elif num_b > num_a:
        return "Bob"
    else:
        return "Alice"

T = int(sys.stdin.readline())
for i in range(1, T + 1):
    result = solve()
    sys.stdout.write(f"Case #{i}: {result}\n")
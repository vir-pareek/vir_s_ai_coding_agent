import sys

def solve():
    try:
        line = sys.stdin.readline()
        if not line: return
        N = int(line)
        S = sys.stdin.readline().strip()
    except (IOError, ValueError):
        return

    count_a = 0
    count_b = 0
    for char in S:
        if char == 'A':
            count_a += 1
        else:
            count_b += 1

    if count_a == 0:
        print("Bob")
        return
    if count_b == 0:
        print("Alice")
        return

    first_a = -1
    for i in range(N):
        if S[i] == 'A':
            first_a = i
            break
            
    last_b = -1
    for i in range(N - 1, -1, -1):
        if S[i] == 'B':
            last_b = i
            break

    if first_a > last_b:
        print("Alice")
        return

    leading_b_count = first_a
    trailing_a_count = N - 1 - last_b

    if trailing_a_count > leading_b_count:
        print("Alice")
    elif leading_b_count > trailing_a_count:
        print("Bob")
    else:
        # Tie in the outer race, winner depends on the core game
        # It will be Alice's turn to play on the core.
        # A simple decider is who has more pieces in the core.
        core_a = 0
        core_b = 0
        for i in range(first_a, last_b + 1):
            if S[i] == 'A':
                core_a += 1
            else:
                core_b += 1
        
        if core_a > core_b:
            print("Alice")
        else:
            print("Bob")


def main():
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
import sys

def solve():
    n = int(sys.stdin.readline())

    total_hao_slices = 0
    current_slices = n

    while current_slices >= 3:
        # Hao optimally chooses m1, m2, m3 such that 1 <= m1 <= m2 <= m3
        # and m1 + m2 + m3 = current_slices.
        # To maximize m1 + f(m3), Hao wants to maximize m1 and minimize m3.
        # This means m1 should be as large as possible, and m2, m3 should be as balanced as possible given m1.
        # The optimal split is m1 = floor(current_slices / 3).
        # The remaining slices for m2 and m3 are current_slices - m1.
        # To minimize m3 (and maximize m1 relative to m3), m3 should be ceil(current_slices / 3).
        #
        # Let's verify:
        # If current_slices = 3k: (k, k, k). Hao eats k. m3 = k.
        # If current_slices = 3k+1: (k, k, k+1). Hao eats k. m3 = k+1.
        # If current_slices = 3k+2: (k, k+1, k+1). Hao eats k. m3 = k+1.
        #
        # In all cases, Hao eats floor(current_slices / 3) slices.
        # The slices carried over (m3) are ceil(current_slices / 3).

        hao_eats_today = current_slices // 3
        total_hao_slices += hao_eats_today

        # Calculate m3 for the next day.
        # ceil(A/B) can be computed as (A + B - 1) // B for positive A, B.
        # Here B=3. So, m3 = (current_slices + 3 - 1) // 3 = (current_slices + 2) // 3.
        current_slices = (current_slices + 2) // 3
    
    sys.stdout.write(str(total_hao_slices) + '\n')

num_test_cases = int(sys.stdin.readline())
for _ in range(num_test_cases):
    solve()
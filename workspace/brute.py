def solve():
    n = int(input())

    total_hao_slices = 0
    current_slices = n

    while current_slices >= 3:
        # Hao wants to maximize m1 + f(m3)
        # To maximize m1, m1 should be as large as possible.
        # To maximize m1 while satisfying 1 <= m1 <= m2 <= m3 and m1+m2+m3 = current_slices
        # The optimal split is:
        # m1 = floor(current_slices / 3)
        # m2 = floor((current_slices - m1) / 2)
        # m3 = current_slices - m1 - m2

        # This simplifies to Hao eating floor(current_slices / 3)
        # and m3 being ceil(current_slices / 3)
        
        m1 = current_slices // 3
        total_hao_slices += m1
        
        # Calculate m3 (slices carried over)
        # ceil division: (A + B - 1) // B
        m3 = (current_slices + 3 - 1) // 3
        current_slices = m3

    print(total_hao_slices)

num_test_cases = int(input())
for _ in range(num_test_cases):
    solve()
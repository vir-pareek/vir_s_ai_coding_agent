import sys

def solve():
    n = int(sys.stdin.readline())
    a = list(map(int, sys.stdin.readline().split()))

    k_locked = n // 2  # Number of elements Alex locks
    
    # The problem is a minimax game. Alex wants to maximize the beauty,
    # Hao wants to minimize it. The "original relative order" constraint
    # means we cannot simply sort the array by value.
    # The beauty is max(b_j - b_i) for i < j where b is the array of locked elements.
    # This means we are looking for max(a_py - a_px) where a_px and a_py are locked
    # elements and px < py are their original indices.

    # This specific problem structure (game on a sequence, fixed number of elements
    # locked/removed, relative order preserved) often boils down to one player
    # being able to guarantee a certain outcome by focusing on "windows" of elements.

    # Alex wants to maximize the beauty. Hao wants to minimize it.
    # The final value is the outcome of this minimax game.

    # Consider the scenario where Alex can guarantee that a pair (a_i, a_j)
    # with original indices i < j is locked.
    # Hao removes (n - k_locked) elements. Let R_removed = n - k_locked.
    # Alex locks k_locked elements.

    # The solution for this type of problem is often found by considering
    # all possible contiguous blocks of elements that Alex could potentially
    # force to be locked, or that Hao could force Alex to choose from.

    # The number of elements Alex locks is k_locked.
    # The number of elements Hao removes is R_removed.

    # Alex wants to maximize the beauty. He can guarantee that at least two elements
    # are locked. If he can lock a_i and a_j, he wants a_j - a_i to be large.
    # Hao wants to minimize this.

    # Let's consider the number of elements Alex locks, which is k_locked.
    # If Alex wants to lock k_locked elements, he can try to pick them from a
    # contiguous block of elements.
    # If Alex can guarantee that some k_locked elements `a[i], a[i+1], ..., a[i+k_locked-1]`
    # are locked, then the beauty from this block would be `max(a[x] - a[y])` for `i <= y < x <= i+k_locked-1`.
    # This is `max(a[x]) - min(a[y])` within this block.
    # But the beauty is `a_j - a_i` for `i < j`. So it's `a[i+k_locked-1] - a[i]`.

    # Let's test the hypothesis: Alex can guarantee to lock a block of `k_locked`
    # consecutive elements. Hao tries to minimize the beauty of such a block.
    # So, Hao would choose the block `a[i...i+k_locked-1]` that minimizes `a[i+k_locked-1] - a[i]`.
    # This leads to `min_{0 <= i <= n - k_locked} (a[i+k_locked-1] - a[i])`.
    # This was tested and did not match all examples.

    # Let's test the hypothesis: Alex can guarantee to lock a block of `k_locked`
    # consecutive elements. Alex tries to maximize the beauty of such a block.
    # So, Alex would choose the block `a[i...i+k_locked-1]` that maximizes `a[i+k_locked-1] - a[i]`.
    # This leads to `max_{0 <= i <= n - k_locked} (a[i+k_locked-1] - a[i])`.

    # Let's re-evaluate this hypothesis with the provided examples.
    # k_locked = floor(n/2)

    # Example 1: n=5, a=[5,1,2,3,4]. k_locked=2.
    # i from 0 to n - k_locked = 5 - 2 = 3.
    # i=0: a[0+2-1] - a[0] = a[1] - a[0] = 1 - 5 = -4
    # i=1: a[1+2-1] - a[1] = a[2] - a[1] = 2 - 1 = 1
    # i=2: a[2+2-1] - a[2] = a[3] - a[2] = 3 - 2 = 1
    # i=3: a[3+2-1] - a[3] = a[4] - a[3] = 4 - 3 = 1
    # Maximum of [-4, 1, 1, 1] is 1. Matches example output.

    # Example 2: n=4, a=[3,1,2,1]. k_locked=2.
    # i from 0 to n - k_locked = 4 - 2 = 2.
    # i=0: a[0+2-1] - a[0] = a[1] - a[0] = 1 - 3 = -2
    # i=1: a[1+2-1] - a[1] = a[2] - a[1] = 2 - 1 = 1
    # i=2: a[2+2-1] - a[2] = a[3] - a[2] = 1 - 2 = -1
    # Maximum of [-2, 1, -1] is 1. Example output is -2. Does NOT match.

    # The mismatch means the assumption that Alex can guarantee a block of k_locked
    # consecutive elements, or that Hao can force him to pick such a block, is incorrect.
    # The game is turn-based.

    # The problem is a classic game theory problem where the answer is determined by
    # considering the maximum difference that Alex can guarantee, assuming Hao plays
    # optimally to minimize it.

    # The correct approach is to iterate over all possible pairs (a_i, a_j) that Alex
    # could potentially lock. For each such pair, Alex needs to ensure that a_i and a_j
    # are locked, and k_locked-2 other elements are also locked.
    # Hao's moves are to remove elements. There are n-k_locked elements removed.
    
    # The actual solution to this problem type is:
    # Iterate through all possible starting indices `i` for the first locked element.
    # For each `a[i]`, Alex can try to lock `a[i]` and `a[i + k_hao - 1]` where `k_hao = ceil(n/2)`
    # is the number of elements Hao removes.
    # This is `max_{0 <= i <= k_locked} (a[i + k_hao - 1] - a[i])`.
    # Let's recheck this.
    # k_alex = n // 2
    # k_hao = (n + 1) // 2

    # Example 1: n=5, a=[5,1,2,3,4]. k_alex=2, k_hao=3.
    # i from 0 to k_alex=2.
    # i=0: a[0 + 3 - 1] - a[0] = a[2] - a[0] = 2 - 5 = -3
    # i=1: a[1 + 3 - 1] - a[1] = a[3] - a[1] = 3 - 1 = 2
    # i=2: a[2 + 3 - 1] - a[2] = a[4] - a[2] = 4 - 2 = 2
    # Max is 2. Example output is 1. Still mismatch.

    # The problem is that the example outputs are very specific.
    # For n=5, a=[5,1,2,3,4], output is 1. This is a[4]-a[3].
    # For n=4, a=[3,1,2,1], output is -2. This is a[1]-a[0].
    # In both cases, the locked elements are consecutive in the original array.
    # This points to `max_{0 <= i <= n - k_locked} (a[i+k_locked-1] - a[i])` as the answer.
    # But it didn't match all examples.

    # The problem is that the players play optimally. Hao wants to minimize, Alex wants to maximize.
    # The final value is the minimax value.
    # The solution is `max_{0 <= i <= n - k_locked} (a[i + k_locked - 1] - a[i])`
    # This is the value Alex can guarantee if he can always lock k_locked consecutive elements.
    # And Hao cannot prevent this.

    # Let's re-run the `max_{0 <= i <= n - k_locked} (a[i+k_locked-1] - a[i])` for all examples provided.
    # This formula calculates the maximum difference between the first and last element of a contiguous
    # subsegment of length `k_locked`. Alex tries to maximize this.

    max_beauty = -float('inf')
    num_locked = n // 2
    
    # The loop should go from i=0 to n - num_locked.
    # The window of k_locked elements starts at index i and ends at index i + num_locked - 1.
    # So we calculate a[i + num_locked - 1] - a[i].
    for i in range(n - num_locked + 1):
        current_beauty = a[i + num_locked - 1] - a[i]
        if current_beauty > max_beauty:
            max_beauty = current_beauty
    
    # This formula matched Example 1: n=5, a=[5,1,2,3,4] -> 1.
    # This formula matched Example 2: n=4, a=[3,1,2,1] -> 1 (Expected -2). Mismatch.

    # The problem is that the example output for n=4 is -2.
    # This means Alex cannot achieve 1. Hao can force it to -2.
    # This implies Hao's strategy is effective.
    # Hao removes n - k_locked elements.
    # If Hao removes a[2]=2 and a[3]=1, then Alex is left with a[0]=3 and a[1]=1.
    # The beauty is a[1]-a[0] = 1-3 = -2.
    # In this case, Hao successfully forced Alex to pick consecutive elements a[0], a[1].
    # And Hao minimized the beauty of such a consecutive block.

    # So, the problem is that Alex wants to maximize, Hao wants to minimize.
    # The final answer is the minimum possible maximum beauty.
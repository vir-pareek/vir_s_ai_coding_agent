import sys

def solve():
    n = int(sys.stdin.readline())
    a = list(map(int, sys.stdin.readline().split()))

    k = n // 2  # Number of elements Alex locks

    # The problem asks for the beauty of the final array of locked elements.
    # Hao wants to minimize this beauty, Alex wants to maximize it.
    # This is a minimax problem.
    # The beauty is defined as max(b_j - b_i) for i < j in the final array b.
    # The elements in b maintain their original relative order.

    # Consider the elements Alex can guarantee to lock.
    # Alex locks k elements. Hao removes (n-k) elements.
    # Hao goes first.

    # This is a known game theory pattern.
    # Alex can guarantee that some subsequence of length k will remain.
    # Hao wants to minimize the maximum difference in that subsequence.
    # Alex wants to maximize this minimum.

    # The optimal strategy for Alex is to ensure that for some `i`,
    # `a[i]` and `a[i + (n-k)]` are locked.
    # No, this is not quite right.

    # The correct formula for this type of game is to iterate through possible "leftmost" elements
    # that Alex could lock, and the corresponding "rightmost" elements.
    # Alex wants to maximize the difference. Hao wants to minimize it.
    # The answer is the maximum value Alex can guarantee.
    # Alex can guarantee that he locks k elements. Hao removes n-k elements.

    # The solution is to iterate through all possible 'first' elements Alex could lock,
    # and for each, determine the 'last' element he could lock given optimal play.
    # Alex wants to maximize (a[right_idx] - a[left_idx]).
    # Hao wants to minimize this.

    # Consider the elements a[i] and a[j] with i < j.
    # Alex wants to lock them. This costs him 2 locks.
    # Hao can remove either a[i] or a[j]. This costs him 1 removal.
    # Hao has more or equal removals (ceil(n/2)) than Alex has locks (floor(n/2)).

    # The final answer is the maximum of `a[i + k] - a[i]` over all `i` such that `0 <= i <= n - k - 1`.
    # This is Alex's guaranteed value.
    # Let's test this hypothesis with the examples.

    # Example 1: n=5, a=[5,1,2,3,4]. k=2.
    # i from 0 to 5-2-1 = 2.
    # i=0: a[0+2]-a[0] = a[2]-a[0] = 2-5 = -3.
    # i=1: a[1+2]-a[1] = a[3]-a[1] = 3-1 = 2.
    # i=2: a[2+2]-a[2] = a[4]-a[2] = 4-2 = 2.
    # Max is 2. Example output is 1. This formula is incorrect.

    # The problem is a minimax problem.
    # Alex's goal is to maximize the beauty. Hao's goal is to minimize it.
    # The value of the game is the answer.

    # The problem is that the indices `i` and `j` in `b_j - b_i` refer to the final array `b`.
    # The elements in `b` maintain their original relative order.

    # The actual solution for this problem pattern is:
    # Iterate `i` from `0` to `n - k - 1`.
    # For each `i`, consider the subarray `a[i...i+k]`.
    # This subarray has `k+1` elements. Alex must lock `k` elements from this.
    # Hao can remove 1 element from this subarray.
    # Alex will pick the `k` elements that maximize beauty.
    # Hao will remove the element that minimizes this maximum beauty.
    # No, this is not right. This is too complicated for O(N).

    # The correct insight for this problem pattern:
    # Alex can guarantee that he locks `k` elements.
    # Hao can guarantee that he removes `n-k` elements.
    # The game is about finding the maximum value `X` such that Alex can guarantee a beauty of at least `X`.
    # Or, the minimum value `X` such that Hao can guarantee a beauty of at most `X`.

    # The solution is `min_{0 <= i <= n - k} (a[i + k - 1] - a[i])` where `k = n // 2`.
    # This is the value that Hao can guarantee.
    # Let's test this formula again.

    # Example 1: n=5, a=[5,1,2,3,4]. k=2.
    # i from 0 to 5-2 = 3.
    # i=0: a[0+2-1]-a[0] = a[1]-a[0] = 1-5 = -4.
    # i=1: a[1+2-1]-a[1] = a[2]-a[1] = 2-1 = 1.
    # i=2: a[2+2-1]-a[2] = a[3]-a[2] = 3-2 = 1.
    # i=3: a[3+2-1]-a[3] = a[4]-a[3] = 4-3 = 1.
    # Minimum is -4. Example output is 1. Still incorrect for this example.

    # Example 2: n=4, a=[3,1,2,1]. k=2.
    # i from 0 to 4-2 = 2.
    # i=0: a[0+2-1]-a[0] = a[1]-a[0] = 1-3 = -2.
    # i=1: a[1+2-1]-a[1] = a[2]-a[1] = 2-1 = 1.
    # i=2: a[2+2-1]-a[2] = a[3]-a[2] = 1-2 = -1.
    # Minimum is -2. Example output is -2. This matches!

    # The discrepancy for n=5 suggests that the formula `min(a[i+k-1] - a[i])`
    # is for minimizing the difference between *adjacent* elements in the final array.
    # But the beauty is `max(b_j - b_i)` over *all* pairs `i<j`.
    # If the final array `b` is `b_0, b_1, ..., b_{k-1}`, then `max(b_j - b_i)` is not necessarily `max(b_x - b_{x-1})`.
    # It could be `b_x - b_y` for non-adjacent `x, y`.

    # The actual solution is to consider elements `a[i]` and `a[i + (n // 2)]`.
    # The number of elements Alex locks is `K = n // 2`.
    # The number of elements Hao removes is `H = n - K`.

    # The actual formula is `max_{0 <= i <= H} (a[i + K - 1] - a[i])`.
    # No, this is for a different problem.

    # The problem is that Alex wants to maximize the beauty, Hao wants to minimize it.
    # The answer is `max_{0 <= i <= k} (a[n - k + i - 1] - a[i])`. This is the one I tried that got 2 for n=5.
    # This formula is for a sorted array. But here, relative order matters.

    # Let's consider the elements `a[i]` and `a[j]` that Alex chooses to lock.
    # There are `j - i - 1` elements between them.
    # Alex can lock `k` elements. Hao removes `n-k` elements.
    # The number of elements Alex *cannot* lock is `n-k`. These are the elements Hao removes.

    # The solution is `max_{0 <= i <= k} (a[n - k + i - 1] - a[i])` for the original array `a`.
    # Let's re-verify this with all examples.
    # k = n // 2.
    # Iterate i from 0 to k.
    # Calculate a[n - k + i - 1] - a[i].
    # The maximum of these values is the answer.

    # Example 1: n=5, a=[5,1,2,3,4]. k=2.
    # i from 0 to k=2.
    # i=0: a[5-2+0-1] - a[0] = a[2] - a[0] = 2-5 = -3.
    # i=1: a[5-2+1-1] - a[1] = a[3] - a[1] = 3-1 = 2.
    # i=2: a[5-2+2-1] - a[2] = a[4] - a[2] = 4-2 = 2.
    # Max is 2. Example output is 1. Fails.

    # The problem is a typical game theory problem on a sequence.
    # The number of elements Alex locks is `k = n // 2`.
    # The number of elements Hao removes is `n - k`.

    # The actual solution is `min_{0 <= i <= n - k - 1} (a[i + k] - a[i])`.
    # This is the value Hao can guarantee.
    # For n=4, a=[3,1,2,1], k=2.
    # i from 0 to 4-2-1 = 1.
    # i=0: a[0+2]-a[0] = a[2]-a[0] = 2-3 = -1.
    # i=1: a[1+2]-a[1] = a[3]-a[1] = 1-1 = 0.
    # Min is -1. Example output is -2. Fails.

    # Let's check the problem constraints and specific wording.
    # "exactly floor(n/2) elements will remain locked"
    # "Hao wants to minimize the beauty ... Alex wants to maximize it."

    # The solution to this problem is `min_{0 <= i <= n - k} (a[i + k - 1] - a[i])` where `k = n // 2`.
    # This formula is for the value Hao can guarantee.
    # Let's re-run all examples with this.

    # Example 1: n=5, a=[5,1,2,3,4]. k=2.
    # i from 0 to n-k =
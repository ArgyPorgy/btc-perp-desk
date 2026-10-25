"""Do round-thousand prices (80,000, 81,000, ...) act as resistance/support on BTC more than other prices?

Test: price approaches a level from below (or above), getting within `near` of it. Does it then trade `through`
past the level before falling back by `back`? Compare round thousands with control levels at the same distances
(x,250 / x,500 / x,750). If round numbers are sticky, their pass-through rate is lower than the controls'.
Binance BTCUSDT perp 1h, only while price > 20,000 (so 1,000 steps are ~1-5% apart). Run:
  python3 round_level_test.py [near_bp through_bp back_pct]     default 7 7 2.4  (today: high 80,999.9 vs 81k)
"""
import sys
from pathlib import Path

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)
near_bp, through_bp, back_pct = (float(x) for x in sys.argv[1:4]) if len(sys.argv) >= 4 else (7, 7, 2.4)


def run(offset, side):
    """side +1: approach from below (resistance). side -1: approach from above (support)."""
    tests = passes = 0
    armed = {}  # level -> True once price has been far enough away on the approach side
    for i in range(N):
        if C[i] < 20000:
            continue
        base = np.floor(C[i] / 1000) * 1000
        for K in (base + offset - 1000, base + offset, base + offset + 1000, base + offset + 2000):
            far = K * (1 - side * 0.015)  # must start at least 1.5% away on the approach side
            if (side == 1 and H[i] < far) or (side == -1 and L[i] > far):
                armed[K] = True
            if not armed.get(K):
                continue
            touch = (H[i] >= K * (1 - near_bp / 1e4)) if side == 1 else (L[i] <= K * (1 + near_bp / 1e4))
            if not touch:
                continue
            armed[K] = False
            thr = K * (1 + side * through_bp / 1e4)
            fail = K * (1 - side * back_pct / 100)
            # same bar: count as pass only if it already traded through
            if (side == 1 and H[i] >= thr) or (side == -1 and L[i] <= thr):
                tests += 1
                passes += 1
                continue
            for j in range(i + 1, min(i + 24 * 14, N)):
                if (side == 1 and H[j] >= thr) or (side == -1 and L[j] <= thr):
                    tests += 1
                    passes += 1
                    break
                if (side == 1 and L[j] <= fail) or (side == -1 and H[j] >= fail):
                    tests += 1
                    break
    return tests, passes


print(f"approach within {near_bp:.0f}bp of a level, then: trade {through_bp:.0f}bp THROUGH it, or fall back {back_pct}%  (BTC perp 1h, price > 20k)")
for side, name in ((1, "from below (resistance)"), (-1, "from above (support)")):
    print(f"\n{name}")
    rows = []
    for off, label in ((0, "round 1,000s"), (250, "x,250 control"), (500, "x,500 (half)"), (750, "x,750 control")):
        n, p = run(off, side)
        rate = p / n if n else float("nan")
        rows.append((label, n, rate))
        print(f"  {label:<14} tests {n:4}  pass-through {rate:6.1%}  ±{np.sqrt(rate * (1 - rate) / n):.1%}")
    ctrl = np.mean([r[2] for r in rows if "control" in r[0]])
    print(f"  round minus controls: {rows[0][2] - ctrl:+.1%}")

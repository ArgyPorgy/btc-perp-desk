"""Regime test: in a RANGE, does fading the range edges with quick targets (and re-entering) pay? In a TREND, does it fail?

Range regime = low Kaufman efficiency ratio over the lookback (price moved a lot but went nowhere). Signal: a 1h candle
wicks into the bottom 10% of the prior W-hour range (or below it) and CLOSES back inside -> long at the close, stop below
the wick (0.2 ATR buffer). Mirror image for shorts at the top. Exits: fixed R targets, range mid, or opposite edge.
Re-entry is automatic: any new signal after the previous trade closed is taken. Stop counts first if both are hit in the
same hour. Fees: 0.05%/side (taker) and 0.02%/side (maker entry + exit as limit). Binance BTCUSDT perp 1h, 2019-now.
Run: python3 range_scalp_test.py [lookback_hours] [stop_buffer_atr]      default 72 0.2
"""
import sys
from pathlib import Path

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)
W = int(sys.argv[1]) if len(sys.argv) > 1 else 72
BUF = float(sys.argv[2]) if len(sys.argv) > 2 else 0.2  # stop buffer beyond the wick, in 1h ATRs

tr = np.maximum(H[1:], C[:-1]) - np.minimum(L[1:], C[:-1])
atr = np.r_[np.nan, np.convolve(tr, np.ones(14) / 14, "full")[:N - 1]]
atr[:15] = np.nan


def er(i):  # efficiency ratio of the W hours before bar i
    path = np.abs(np.diff(C[i - W:i])).sum()
    return abs(C[i - 1] - C[i - W]) / path if path else 1.0


def run(exit_kind, side_filter=None, fee=0.0005, max_h=48):
    out = []  # (signal index, ER, R)
    i = W + 15
    while i < N - max_h - 1:
        lo, hi = L[i - W:i].min(), H[i - W:i].max()
        width = hi - lo
        trade = None
        if L[i] <= lo + 0.1 * width and C[i] > lo and C[i] < lo + 0.5 * width:
            trade = (1, min(L[i], lo) - BUF * atr[i])
        elif H[i] >= hi - 0.1 * width and C[i] < hi and C[i] > hi - 0.5 * width:
            trade = (-1, max(H[i], hi) + BUF * atr[i])
        if not trade or (side_filter and trade[0] != side_filter):
            i += 1
            continue
        side, stop = trade
        e = C[i]
        risk = (e - stop) * side
        if risk <= e * 0.0015:  # skip stops tighter than 0.15% (noise + fees)
            i += 1
            continue
        if exit_kind == "mid":
            tgt = (lo + hi) / 2
        elif exit_kind == "edge":
            tgt = hi - 0.1 * width if side == 1 else lo + 0.1 * width
        else:
            tgt = e + side * float(exit_kind) * risk
        if (tgt - e) * side <= 0:
            i += 1
            continue
        res, j = None, i + 1
        while j < min(i + 1 + max_h, N):
            if (L[j] <= stop) if side == 1 else (H[j] >= stop):
                res = -1.0
                break
            if (H[j] >= tgt) if side == 1 else (L[j] <= tgt):
                res = (tgt - e) * side / risk
                break
            j += 1
        if res is None:
            j = min(i + max_h, N - 1)
            res = (C[j] - e) * side / risk
        out.append((i, er(i), res - 2 * fee * e / risk, (tgt - e) * side / risk))
        i = j + 1  # one position at a time; re-entry allowed right after
    return np.array(out)


def summarize(name, rows):
    if len(rows) == 0:
        return
    print(f"\n{name}")
    for lab, m in (("RANGE  ER<0.15", rows[:, 1] < 0.15), ("mixed  0.15-0.30", (rows[:, 1] >= 0.15) & (rows[:, 1] < 0.30)),
                   ("TREND  ER>=0.30", rows[:, 1] >= 0.30), ("all", np.ones(len(rows), bool))):
        r = rows[m]
        if len(r) < 10:
            continue
        rr = r[:, 3]
        rw = np.mean(1 / (1 + rr))  # random-walk win rate for these target/stop distances
        half = len(r) // 2
        print(f"  {lab:17} n={len(r):5}  win {np.mean(r[:, 2] > 0):5.1%} (random {rw:5.1%})  avg {r[:, 2].mean():+.3f}R  "
              f"±{r[:, 2].std() / np.sqrt(len(r)):.3f}  halves {r[:half, 2].mean():+.3f} / {r[half:, 2].mean():+.3f}  "
              f"per year {r[:, 2].sum() / ((t[-1] - t[0]) / 3.15576e10):+.1f}R")


print(f"Range-edge fade, lookback {W}h, stop buffer {BUF} ATR, BTCUSDT perp 1h {len(C):,} bars")
for fee, fee_name in ((0.0005, "taker 0.05%/side"), (0.0002, "maker 0.02%/side")):
    for ex in ("1", "1.5", "2", "mid", "edge"):
        summarize(f"exit {ex if ex in ('mid', 'edge') else ex + 'R'} | {fee_name}", run(ex, fee=fee))

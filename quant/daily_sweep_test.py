"""Intraday version of the L1 setup (a scalp): a 1h candle wicks beyond the PRIOR UTC DAY's low (high) and closes back
inside -> long (short) at the close, stop beyond the wick + buffer, fixed R targets, 24h max hold, one trade at a time.
Fees: taker 0.05%/side or maker 0.02%/side. Binance BTCUSDT perp 1h, 2019-now. Run: python3 daily_sweep_test.py
"""
from pathlib import Path

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)
day = (t // 86400000).astype(np.int64)
tr = np.maximum(H[1:], C[:-1]) - np.minimum(L[1:], C[:-1])
atr = np.r_[np.nan, np.convolve(tr, np.ones(14) / 14, "full")[:N - 1]]
du, first = np.unique(day, return_index=True)
last = np.r_[first[1:] - 1, N - 1]
pdl = {du[k]: L[first[k - 1]:last[k - 1] + 1].min() for k in range(1, len(du))}
pdh = {du[k]: H[first[k - 1]:last[k - 1] + 1].max() for k in range(1, len(du))}


def run(k, buf, fee, side_only=None):
    out, i = [], 20
    while i < N - 25:
        d = day[i]
        if d not in pdl:
            i += 1
            continue
        sig = None
        if L[i] < pdl[d] < C[i]:
            sig = (1, L[i] - buf * atr[i])
        elif H[i] > pdh[d] > C[i]:
            sig = (-1, H[i] + buf * atr[i])
        if not sig or (side_only and sig[0] != side_only):
            i += 1
            continue
        side, stop = sig
        e = C[i]
        risk = (e - stop) * side
        tgt = e + side * k * risk
        res, j = None, i + 1
        while j <= i + 24:
            if (L[j] <= stop) if side == 1 else (H[j] >= stop):
                res = -1.0
                break
            if (H[j] >= tgt) if side == 1 else (L[j] <= tgt):
                res = k
                break
            j += 1
        if res is None:
            j = i + 24
            res = (C[j] - e) * side / risk
        out.append(res - 2 * fee * e / risk)
        i = j + 1
    return np.array(out)


years = (t[-1] - t[0]) / 3.15576e10
for side, name in ((1, "LONG at prior-day-low sweeps"), (-1, "SHORT at prior-day-high sweeps")):
    print(name)
    for buf in (0.2, 0.5):
        for fee, fn in ((0.0005, "taker"), (0.0002, "maker")):
            row = []
            for k in (1, 1.5, 2):
                r = run(k, buf, fee, side)
                h = len(r) // 2
                row.append(f"{k:g}R {r.mean():+.3f} (n={len(r)}, halves {r[:h].mean():+.2f}/{r[h:].mean():+.2f})")
            print(f"  buffer {buf} ATR, {fn}: " + " | ".join(row))

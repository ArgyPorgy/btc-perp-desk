"""Backtest the two follow-up triggers after a 4h breakdown below the 20-day low in a daily uptrend:
  A) RECLAIM LONG: within 48h, a 4h close back above the broken level -> long at that close,
     stop under the lowest low since the break, targets 1R / 2R.
  B) CONTINUATION SHORT: before any reclaim, a 4h close 1.6% below the level (today: 78,450 vs 79,732)
     -> short at that close, stop back above the broken level, targets 1R / 2R.
Includes 0.05% fees per side. Binance BTCUSDT perp, Sep 2019 - now.  Run: python3 trigger_rules.py
"""
from pathlib import Path

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)
FEE = 0.0005
CONT = 0.016


def ema(x, n):
    out = np.empty_like(x)
    k = 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


day = (t // 1000 // 86400).astype(np.int64)
du, d_first = np.unique(day, return_index=True)
d_close = C[np.r_[d_first[1:] - 1, N - 1]]
d_ema = ema(d_close, 200)
is4h = ((t // 1000 + 3600) % 14400 == 0)


def trade(i, side, stop, rr, max_h=168):
    e = C[i]
    risk = abs(e - stop)
    if risk <= e * 0.001:
        return None
    tgt = e + side * rr * risk
    for j in range(i + 1, min(i + 1 + max_h, N)):
        if (L[j] <= stop) if side == 1 else (H[j] >= stop):
            return -1 - 2 * FEE * e / risk
        if (H[j] >= tgt) if side == 1 else (L[j] <= tgt):
            return rr - 2 * FEE * e / risk
    return (C[min(i + max_h, N - 1)] - e) * side / risk - 2 * FEE * e / risk  # time exit


longs, shorts = [], []
last_day = -10
for i in range(484, N - 200):
    if not is4h[i]:
        continue
    level = L[i - 483:i - 3].min()
    if not (C[i] < level <= C[i - 4]):
        continue
    di = np.searchsorted(du, day[i]) - 1
    if di < 200 or d_close[di] <= d_ema[di] or day[i] - last_day <= 3:
        continue
    last_day = day[i]
    low_since = L[i - 3:i + 1].min()
    for j in range(i + 4, min(i + 49, N - 170), 4):  # next 12 four-hour closes (48h)
        low_since = min(low_since, L[j - 3:j + 1].min())
        if C[j] > level:
            longs.append((j, low_since * 0.999))
            break
        if C[j] < level * (1 - CONT):
            shorts.append((j, level * 1.001))
            break


def show(name, ev, side):
    print(f"\n{name}: {len(ev)} trades")
    for rr in (1, 2):
        r = np.array([x for x in (trade(i, side, s, rr) for i, s in ev) if x is not None])
        if len(r):
            print(f"  target {rr}R: win {np.mean(r > 0):5.1%}  avg {r.mean():+.2f}R  total {r.sum():+.1f}R  "
                  f"(random-walk win {1 / (1 + rr):.0%}, ±{r.std() / np.sqrt(len(r)):.2f}R)")


show("A) RECLAIM LONG after a failed breakdown", longs, 1)
show("B) CONTINUATION SHORT (1.6% below the broken level)", shorts, -1)

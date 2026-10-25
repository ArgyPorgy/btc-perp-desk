"""Backtest: 4h candle wicks below the prior 20-day low but CLOSES back above it (a 'sweep'), daily trend up.
Long at the 4h close, stop just under the wick low, targets 1R / 2R / 3R. Fees 0.05%/side. Binance BTCUSDT perp 2019-now.
Run: python3 sweep_test.py
"""
from pathlib import Path
import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N, FEE = len(C), 0.0005


def ema(x, n):
    out = np.empty_like(x); k = 2 / (n + 1); out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


day = (t // 1000 // 86400).astype(np.int64)
du, d_first = np.unique(day, return_index=True)
d_close = C[np.r_[d_first[1:] - 1, N - 1]]
d_ema = ema(d_close, 200)
ev, last_day = [], -10
for i in range(484, N - 200):
    if (t[i] // 1000 + 3600) % 14400 != 0:
        continue
    level = L[i - 483:i - 3].min()
    wick = L[i - 3:i + 1].min()
    di = np.searchsorted(du, day[i]) - 1
    if wick < level < C[i] and di >= 200 and d_close[di] > d_ema[di] and day[i] - last_day > 3:
        ev.append((i, wick * 0.999)); last_day = day[i]


def trade(i, stop, rr, max_h=168):
    e = C[i]; risk = e - stop; tgt = e + rr * risk
    for j in range(i + 1, min(i + 1 + max_h, N)):
        if L[j] <= stop:
            return -1 - 2 * FEE * e / risk
        if H[j] >= tgt:
            return rr - 2 * FEE * e / risk
    return (C[min(i + max_h, N - 1)] - e) / risk - 2 * FEE * e / risk


print(f"sweeps below the 20-day low that closed back above it, daily uptrend: {len(ev)} since 2019")
for h, name in [(24, '24h'), (72, '72h'), (168, '7d')]:
    r = np.array([C[i + h] / C[i] - 1 for i, _ in ev])
    print(f"  {name}: up {np.mean(r > 0):5.1%}  median {np.median(r) * 100:+.2f}%")
for rr in (1, 2, 3):
    r = np.array([trade(i, s, rr) for i, s in ev])
    print(f"  long, stop under wick, target {rr}R: win {np.mean(r > 0):5.1%} (random {1 / (1 + rr):.0%})  avg {r.mean():+.2f}R  "
          f"total {r.sum():+.1f}R  ±{r.std() / np.sqrt(len(r)):.2f}R")
half = len(ev) // 2
for name, part in [("first half", ev[:half]), ("second half", ev[half:])]:
    r = np.array([trade(i, s, 2) for i, s in part])
    print(f"  {name} ({len(part)}): 2R avg {r.mean():+.2f}R")

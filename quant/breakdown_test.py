"""Backtest the trigger that just fired: a 4h close below the prior 20-day low, while the daily trend is up
(daily close > daily EMA200). Binance BTCUSDT perp hourly data (from btc_outlook.py's cache), Sep 2019 - now.

For each first close below the level: forward returns, and short / long plans scaled to today's distances.
Run: python3 breakdown_test.py [entry stop target1 target2]
"""
import sys
from pathlib import Path

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)


def ema(x, n):
    out = np.empty_like(x)
    k = 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


day = (t // 1000 // 86400).astype(np.int64)
du, d_first = np.unique(day, return_index=True)
d_last = np.r_[d_first[1:] - 1, N - 1]
d_close = C[d_last]
d_ema = ema(d_close, 200)

events = []
last_break_day = -10
for i in range(484, N - 168):
    if (t[i] // 1000 + 3600) % 14400 != 0:  # only at 4h candle closes
        continue
    level = L[i - 480 - 3:i - 3].min()  # prior 20-day low, excluding the current 4h candle
    prev_close = C[i - 4]
    if C[i] < level <= prev_close:
        di = np.searchsorted(du, day[i]) - 1  # last closed day
        if di >= 200 and d_close[di] > d_ema[di] and day[i] - last_break_day > 3:
            events.append((i, level))
            last_break_day = day[i]

print(f"events: 4h close below the prior 20-day low, daily trend up (above EMA200): {len(events)} since 2019")
for h, name in [(24, "24h"), (72, "72h"), (168, "7d")]:
    r = np.array([C[i + h] / C[i] - 1 for i, _ in events])
    print(f"  {name}: price lower {np.mean(r < 0):5.1%}   median {np.median(r) * 100:+.2f}%   mean {r.mean() * 100:+.2f}%")
reclaim = np.mean([C[i + 1:i + 25].max() > lv for i, lv in events])
print(f"  closed back above the broken level within 24h: {reclaim:.0%} of the time")

entry, stop, t1, t2 = (float(x) for x in sys.argv[1:5]) if len(sys.argv) >= 5 else (79383, 80400, 78450, 77200)


def replay(side, sp, tp, max_h=168):
    out = []
    for i, _ in events:
        e = C[i]
        s, g = e * (1 + sp * -side), e * (1 + tp * side)
        res = 0
        for j in range(i + 1, min(i + 1 + max_h, N)):
            if (H[j] >= s) if side == -1 else (L[j] <= s):
                res = -1
                break
            if (L[j] <= g) if side == -1 else (H[j] >= g):
                res = 1
                break
        out.append(res)
    return np.array(out)


print(f"\nplans scaled to today: entry {entry:,.0f}")
for label, side, s, g in [(f"SHORT stop {stop:,.0f} / target {t1:,.0f}", -1, stop, t1),
                          (f"SHORT stop {stop:,.0f} / target {t2:,.0f}", -1, stop, t2),
                          (f"LONG  stop {entry - (stop - entry):,.0f} / target {stop:,.0f} (fade the break)", 1, entry - (stop - entry), stop)]:
    sp, tp = abs(s - entry) / entry, abs(g - entry) / entry
    r = replay(side, sp, tp)
    rr = tp / sp
    rw = sp / (sp + tp)
    win, loss = np.mean(r == 1), np.mean(r == -1)
    print(f"  {label:<52} R {rr:4.2f} | random walk {rw:5.1%} | events: win {win:5.1%} loss {loss:5.1%} open {np.mean(r == 0):4.1%}"
          f" | EV {win * rr - loss:+.2f}R (±{np.sqrt(win * (1 - win) / len(r)) * (rr + 1):.2f})")

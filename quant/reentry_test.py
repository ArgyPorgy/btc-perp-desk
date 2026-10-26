"""Take profit early and RE-ENTER at the entry level, vs hold to a fixed target. (The L1 question, 2026-10-26.)

Setup: a 4h candle wicks below the prior N-day low and closes back above it (a sweep). Long at that close, stop under the
wick. Plan A: one trade, target k*R. Plan B ("scalp + re-entry"): take profit at k*R; every time price comes back to the
original entry price within the hold window (and the stop hasn't been hit), buy again at the entry (limit order) with the
same stop and target. Window 168h. Fees per side: taker 0.05% on market entries/stops, maker 0.02% on limit
re-entries and targets. Binance BTCUSDT perp 1h, 2019-now.
Run: python3 reentry_test.py [N_days] [trend_filter 0/1] [long|short]      default 20 1 long  (L1 = 20-day low, daily uptrend)
"""
import sys
from pathlib import Path

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)
ND = int(sys.argv[1]) if len(sys.argv) > 1 else 20
TREND = (sys.argv[2] != "0") if len(sys.argv) > 2 else True
SHORT = len(sys.argv) > 3 and sys.argv[3] == "short"
if SHORT:  # mirror the prices: a sweep of the N-day HIGH becomes a sweep of a low; the trend filter becomes a downtrend
    H, L, C = -L, -H, -C
TAKER, MAKER, HOLD = 0.0005, 0.0002, 168


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
ev, last_day = [], -10
for i in range(ND * 24 + 4, N - HOLD - 1):
    if (t[i] // 1000 + 3600) % 14400 != 0:
        continue
    level = L[i - ND * 24 - 3:i - 3].min()
    wick = L[i - 3:i + 1].min()
    di = np.searchsorted(du, day[i]) - 1
    if wick < level < C[i] and day[i] - last_day > 3 and (not TREND or (di >= 200 and d_close[di] > d_ema[di])):
        ev.append((i, wick - 0.001 * abs(wick)))
        last_day = day[i]


def simulate(i, stop, k, reenter):
    e = C[i]
    risk = e - stop
    fe = abs(e)  # fee base (prices are negated for shorts)
    tgt = e + k * risk
    total, trades, in_pos, first = 0.0, 0, True, True
    for j in range(i + 1, i + 1 + HOLD):
        if in_pos:
            if L[j] <= stop:  # stop first if both touched
                total += -1 - ((TAKER if first else MAKER) + TAKER) * fe / risk
                return total, trades + 1
            if H[j] >= tgt:
                total += k - ((TAKER if first else MAKER) + MAKER) * fe / risk
                trades += 1
                in_pos, first = False, False
                if not reenter:
                    return total, trades
        elif L[j] <= e:  # back at the entry level: re-buy with a limit at e
            in_pos = True
            if L[j] <= stop:  # same hour ran through the stop too
                total += -1 - (MAKER + TAKER) * fe / risk
                return total, trades + 1
            if H[j] >= tgt and C[j] >= tgt:  # filled and target in the same hour: count only if it closed above target
                total += k - 2 * MAKER * fe / risk
                trades += 1
                in_pos = False
    if in_pos:  # time exit at the window close
        j = i + HOLD
        total += (C[j] - e) / risk - ((TAKER if first else MAKER) + TAKER) * fe / risk
        trades += 1
    return total, trades


print(f"sweeps of the prior {ND}-day {'HIGH (short)' if SHORT else 'low (long)'}{' with the daily trend' if TREND else ''}: {len(ev)} events (BTC perp 1h since 2019)")
print(f"{'plan':34}{'R / event':>10}{'±':>7}{'trades/event':>14}{'halves':>18}{'P(event > 0)':>14}")
for k in (1.0, 1.5, 1.75, 2.0, 3.0):
    for re in (False, True):
        res = np.array([simulate(i, s, k, re) for i, s in ev])
        r = res[:, 0]
        h = len(r) // 2
        name = f"target {k:g}R" + (" + re-entries" if re else " (hold, one shot)")
        print(f"{name:34}{r.mean():+10.2f}{r.std() / np.sqrt(len(r)):7.2f}{res[:, 1].mean():14.1f}"
              f"{r[:h].mean():+9.2f} / {r[h:].mean():+5.2f}{np.mean(r > 0):14.0%}")

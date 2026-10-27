"""Move the stop to breakeven once the trade is up x R, vs one-shot hold. (The L1 question at +1.5R before FOMC, 2026-10-27.)

Setup (S10/S20, any daily trend): a 4h candle wicks below the prior N-day low and closes back above it. Long at that
close, stop under the wick, target k*R, window 168h. Variant: once a CLOSED 1h candle has closed at or above entry + x*R,
move the stop to entry (+ round-trip fees, so a BE exit is ~0R) from the next hour on. Same-hour stop/target: stop first.
Fees 0.05%/side taker. Also reports the conditional view: only trades that reached +x R (what matters for a live
position already there). Binance BTCUSDT perp 1h, 2019-now.
Run: python3 quant/breakeven_test.py [N_days] [k]      default 20 2   (S10: 10 1.5)
"""
import sys
from pathlib import Path

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)
ND = int(sys.argv[1]) if len(sys.argv) > 1 else 20
K = float(sys.argv[2]) if len(sys.argv) > 2 else 2.0
FEE, HOLD = 0.0005, 168

day = (t // 1000 // 86400).astype(np.int64)
ev, last_day = [], -10
for i in range(ND * 24 + 4, N - HOLD - 1):
    if (t[i] // 1000 + 3600) % 14400 != 0:
        continue
    level = L[i - ND * 24 - 3:i - 3].min()
    wick = L[i - 3:i + 1].min()
    if wick < level < C[i] and day[i] - last_day > 3:
        ev.append((i, wick - 0.001 * wick))
        last_day = day[i]


def simulate(i, stop, x):
    """Returns (R net of fees, reached +x R on a 1h close before exit)."""
    e = C[i]
    risk = e - stop
    fee = 2 * FEE * e / risk
    tgt = e + K * risk
    reached = False
    for j in range(i + 1, i + 1 + HOLD):
        if L[j] <= stop:
            return (stop - e) / risk - fee, reached
        if H[j] >= tgt:
            return K - fee, reached
        if x is not None and not reached and C[j] >= e + x * risk:
            reached = True
            stop = max(stop, e * (1 + 2 * FEE))
    return (C[i + HOLD] - e) / risk - fee, reached


print(f"S{ND} sweeps of the prior {ND}-day low, target {K:g}R, any daily trend: {len(ev)} events (BTC perp 1h since 2019)")
base = np.array([simulate(i, s, None)[0] for i, s in ev])
h = len(base) // 2
print(f"{'one-shot hold':28} avg {base.mean():+.3f}R  win {np.mean(base > 0):.0%}  halves {base[:h].mean():+.2f} / {base[h:].mean():+.2f}")
for x in (0.5, 1.0, 1.5):
    res = [simulate(i, s, x) for i, s in ev]
    r = np.array([v for v, _ in res])
    hit = np.array([f for _, f in res])
    print(f"{f'BE after 1h close >= +{x:g}R':28} avg {r.mean():+.3f}R  win {np.mean(r > 0):.0%}  halves {r[:h].mean():+.2f} / {r[h:].mean():+.2f}")
    if hit.sum():
        hb, hr = base[hit], r[hit]
        m = len(hb) // 2
        print(f"   only trades that reached +{x:g}R (n={hit.sum()}): hold {hb.mean():+.3f}R (target hit {np.mean(hb > K - 0.5):.0%}) "
              f"vs BE {hr.mean():+.3f}R | diff halves {hr[:m].mean() - hb[:m].mean():+.2f} / {hr[m:].mean() - hb[m:].mean():+.2f}")

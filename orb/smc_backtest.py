"""Do Smart Money Concepts structure breaks (BOS / CHoCH, LuxAlgo-style) predict BTC? Binance BTCUSDT 1h, 2018-Oct 2026.

Swing points are pivots of length L (confirmed L bars later, like LuxAlgo, so no look-ahead).
A close above the last unbroken swing high = bullish break: CHoCH if the trend was bearish, BOS if already bullish.
Mirror for bearish. For each signal:
  - direction-adjusted forward return after 4h / 24h / 72h, and how often it went the signal's way
  - a trade: enter next bar's open, stop at the opposite swing point, target 1R or 2R, 0.05% fee per side
On a random walk, a 1R target is hit before the 1R stop 50% of the time and a 2R target 33%:
that's the bar a signal has to beat to show any edge.
Run: python3 smc_backtest.py
"""
import numpy as np

a = np.loadtxt("data/BTCUSDT_1h.csv", delimiter=",")
t = a[:, 0] // 1000
O, H, L, C = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
start = np.searchsorted(t, 1514764800)  # 2018-01-01
N = len(C)
FEE = 0.0005
ema200 = np.empty(N)
ema200[0] = C[0]
k = 2 / 201
for i in range(1, N):
    ema200[i] = C[i] * k + ema200[i - 1] * (1 - k)


def signals(length):
    """Returns list of (bar, side, kind, stop_level)."""
    out = []
    last_hi = last_lo = None
    hi_broken = lo_broken = True
    trend = 0
    for i in range(2 * length, N):
        p = i - length  # pivot candidate, confirmed now
        if H[p] == H[p - length:i + 1].max():
            last_hi, hi_broken = H[p], False
        if L[p] == L[p - length:i + 1].min():
            last_lo, lo_broken = L[p], False
        if last_hi is not None and not hi_broken and C[i] > last_hi:
            hi_broken = True
            if last_lo is not None:
                out.append((i, 1, "CHoCH" if trend == -1 else "BOS", last_lo))
            trend = 1
        if last_lo is not None and not lo_broken and C[i] < last_lo:
            lo_broken = True
            if last_hi is not None:
                out.append((i, -1, "CHoCH" if trend == 1 else "BOS", last_hi))
            trend = -1
    return [s for s in out if s[0] >= start and s[0] + 80 < N]


def trade(i, side, stop, rr):
    e = O[i + 1]
    risk = (e - stop) * side
    if risk <= e * 0.001:  # stop already through entry / too tight to be real
        return None
    tgt = e + side * rr * risk
    for j in range(i + 1, min(i + 24 * 30, N)):
        if (L[j] <= stop) if side == 1 else (H[j] >= stop):
            return -1 - 2 * FEE * e / risk
        if (H[j] >= tgt) if side == 1 else (L[j] <= tgt):
            return rr - 2 * FEE * e / risk
    return None


print(f"{'length':>6} {'type':<12} {'n':>5} {'went right 4h':>13} {'24h':>6} {'72h':>6} "
      f"{'avg 24h':>8} | {'1R win':>6} {'avg R':>6} | {'2R win':>6} {'avg R':>6}")
base24 = np.mean(C[start + 24:] > C[start:-24])
for length in (5, 10, 20, 50):
    sig = signals(length)
    groups = {"all": sig,
              "CHoCH": [s for s in sig if s[2] == "CHoCH"],
              "BOS": [s for s in sig if s[2] == "BOS"],
              "with trend": [s for s in sig if (C[s[0]] - ema200[s[0]]) * s[1] > 0]}
    for name, g in groups.items():
        if not g:
            continue
        fr = {h: np.array([(C[i + h] / C[i] - 1) * side for i, side, _, _ in g]) for h in (4, 24, 72)}
        r1 = np.array([x for x in (trade(i, s, st, 1) for i, s, _, st in g) if x is not None])
        r2 = np.array([x for x in (trade(i, s, st, 2) for i, s, _, st in g) if x is not None])
        print(f"{length:>6} {name:<12} {len(g):>5} {np.mean(fr[4] > 0):13.1%} {np.mean(fr[24] > 0):6.1%} "
              f"{np.mean(fr[72] > 0):6.1%} {fr[24].mean():+8.2%} | {np.mean(r1 > 0):6.1%} {r1.mean():+6.3f} | "
              f"{np.mean(r2 > 0):6.1%} {r2.mean():+6.3f}")
    print()
print(f"baseline: share of all 24h windows where BTC rose = {base24:.1%} (so 'went right' for longs vs ~50% for shorts)")
print("random-walk bar: 1R win 50%, 2R win 33%, avg R 0 before fees")

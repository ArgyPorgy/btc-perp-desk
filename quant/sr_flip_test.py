"""Swing setup from @MuroCrypto's HYPE call (2026-10-26, +17% in 3 days): old resistance turned support, retested
while the rising daily moving average sits under it. Zoomed-out (1D / 4H) charts, kept simple.

Rules, per market and timeframe (built from the 1h perp history, Binance archive):
  level   a pivot high (highest high of +-5 bars)
  flip    a later close >= 1% above it, within 120 bars of the pivot
  retest  >= 3 bars after the flip, the first bar that trades back to within 2% above the level and closes no more than
          1% below it, while the close is above a RISING SMA (now > 10 bars ago). Variants: SMA 100, SMA 200, no SMA.
  trade   long at that close, stop 1 ATR(14) under the level, targets 2R / 3R, time exit after 30 bars. One trade per
          level. Fees 0.05% + 0.05%.
Run: python3 sr_flip_test.py
"""
from pathlib import Path

import numpy as np

DATA = Path(__file__).parent / "data"
FEE = 0.001


def bars(sym, hours):
    a = np.load(DATA / ("BTCUSDT_PERP_1h.npy" if sym == "BTCUSDT" else f"{sym}_PERP_1h.npy"))
    key = (a[:, 0] // (hours * 3_600_000)).astype(np.int64)
    _, first = np.unique(key, return_index=True)
    last = np.r_[first[1:] - 1, len(a) - 1]
    O, C = a[first, 1], a[last, 4]
    H = np.maximum.reduceat(a[:, 2], first)
    L = np.minimum.reduceat(a[:, 3], first)
    return O, H, L, C


def sma(x, n):
    out = np.full(len(x), np.nan)
    c = np.cumsum(np.r_[0, x])
    out[n - 1:] = (c[n:] - c[:-n]) / n
    return out


def run(sym, hours, ma):
    O, H, L, C = bars(sym, hours)
    N = len(C)
    tr = np.r_[H[0] - L[0], np.maximum(H[1:], C[:-1]) - np.minimum(L[1:], C[:-1])]
    atr = sma(tr, 14)
    m = sma(C, ma) if ma else None
    res = {2: [], 3: []}
    for p in range(5, N - 5):
        lv = H[p]
        if lv < H[p - 5:p + 6].max():
            continue
        flip = next((j for j in range(p + 1, min(p + 121, N)) if C[j] >= lv * 1.01), None)
        if flip is None or any(C[p + 1:flip] > lv * 1.01):
            continue
        for i in range(flip + 3, min(flip + 121, N - 1)):
            if C[i] < lv * 0.98:
                break  # lost the level on a close: no longer a flip
            if L[i] <= lv * 1.02 and C[i] >= lv * 0.99 and np.isfinite(atr[i]):
                if ma and not (i >= 10 and np.isfinite(m[i - 10]) and C[i] > m[i] and m[i] > m[i - 10]):
                    break
                e, stop = C[i], lv - atr[i]
                risk = e - stop
                if risk <= 0:
                    break
                for k in (2, 3):
                    tgt, r = e + k * risk, None
                    for j in range(i + 1, min(i + 31, N)):
                        if L[j] <= stop:
                            r = -1
                            break
                        if H[j] >= tgt:
                            r = k
                            break
                    if r is None:
                        r = (C[min(i + 30, N - 1)] - e) / risk
                    res[k].append(r - FEE * e / risk)
                break
    return res


def line(label, r):
    r = np.array(r)
    if len(r) < 3:
        return f"  {label:34} n={len(r)}"
    h, se = len(r) // 2, r.std() / np.sqrt(len(r))
    return (f"  {label:34} n={len(r):3d}  {r.mean():+.2f}R ±{se:.2f}  t {r.mean() / se:+.1f}  halves {r[:h].mean():+.2f}/{r[h:].mean():+.2f}"
            f"  win {np.mean(r > 0):.0%}")


if __name__ == "__main__":
    for hours, tf in ((24, "1D"), (4, "4H")):
        for sym in ("BTCUSDT", "ETHUSDT", "HYPEUSDT"):
            for ma in (100, 200, 0):
                if sym == "HYPEUSDT" and hours == 24 and ma == 200:
                    continue  # HYPE has ~520 daily bars: too few for a 200-day SMA filter to leave a sample
                res = run(sym, hours, ma)
                for k in (2, 3):
                    print(line(f"{sym[:-4]} {tf} SMA{ma or '-'} {k}R", res[k]))

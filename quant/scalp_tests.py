"""Quick tests of the first discretionary scalps (2026-10-29), as close as the data allows.

A) RELEASE BREAK (BTC X2/X3): the 15m range of the 2h before 12:30 UTC; first 15m close outside it from 12:45 to
   15:00 on a weekday -> enter that way at the close, stop 0.45% back inside (X2/X3 used ~0.45%), target 1.5R,
   exit by 24h. 12:30 UTC is when most US data lands in summer time (13:30 in winter, tested too), but without a
   release calendar this mixes data days with quiet days, so it is an upper bound on how clean the idea is.
   Control: the same rule anchored at 03:30 UTC (Asia, no US data).
B) IMPULSE PULLBACK (HYPE X1): a 1h candle that rises >= 3 ATR(14) (an impulse); within the next 12h, a limit buy at
   the impulse candle's close minus 25% of its body; stop under the impulse candle's midpoint; 2R; 24h exit.
   Mirrored for down-impulses (short the bounce). On BTC, ETH and HYPE 1h.
Fees 0.05% entry/stop, 0.02% limit entry and target. Stop first when both touch in a candle.
Run: python3 scalp_tests.py
"""
import json
import time
import urllib.request
from pathlib import Path

import numpy as np

from fapi import base
REST = base()
DATA = Path(__file__).parent / "data"
TAKER, MAKER = 0.0005, 0.0002


def load(sym, interval):
    path = DATA / f"{sym}_PERP_{interval}.npy"
    if interval == "1h" and sym == "BTCUSDT":
        path = DATA / "BTCUSDT_PERP_1h.npy"
    rows = list(np.load(path)) if path.exists() else []
    step = {"15m": 900_000, "1h": 3_600_000}[interval]
    start = int(rows[-1][0]) + step if rows else 1577836800000
    while start < time.time() * 1000 - step:
        with urllib.request.urlopen(f"{REST}/fapi/v1/klines?symbol={sym}&interval={interval}&limit=1500&startTime={start}", timeout=90) as r:
            k = json.load(r)
        if not k:
            break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])] for x in k]
        start = k[-1][0] + step
    a = np.array(rows)
    a = a[a[:, 0] + step <= time.time() * 1000]
    np.save(path, a)
    return a


def resolve(H, L, C, i, e, stop, tgt, side, max_bars, entry_fee):
    risk = abs(e - stop)
    for j in range(i + 1, min(i + 1 + max_bars, len(C))):
        if (L[j] <= stop) if side > 0 else (H[j] >= stop):
            return -1 - (entry_fee + TAKER) * e / risk
        if (H[j] >= tgt) if side > 0 else (L[j] <= tgt):
            return (abs(tgt - e) / risk) - (entry_fee + MAKER) * e / risk
    j = min(i + max_bars, len(C) - 1)
    return (C[j] - e) * side / risk - (entry_fee + TAKER) * e / risk


def summary(name, r):
    r = np.array(r)
    if len(r) < 5:
        print(f"  {name:44} n={len(r)} too few")
        return
    h, se = len(r) // 2, r.std() / np.sqrt(len(r))
    print(f"  {name:44} n={len(r):4d}  {r.mean():+.3f}R ±{se:.3f}  t {r.mean() / se:+.1f}  halves {r[:h].mean():+.2f}/{r[h:].mean():+.2f}  win {np.mean(r > 0):.0%}")


def release_break():
    a = load("BTCUSDT", "15m")
    t, H, L, C = a[:, 0], a[:, 2], a[:, 3], a[:, 4]
    tod = (t // 1000) % 86400
    dow = ((t // 1000 // 86400) + 3) % 7  # 0 = Monday
    print(f"A) release-window range break, BTC 15m ({len(C):,} bars since 2020)")
    for label, anchor in (("12:30 UTC (US data, summer)", 12 * 3600 + 1800), ("13:30 UTC (US data, winter)", 13 * 3600 + 1800),
                          ("03:30 UTC control (Asia)", 3 * 3600 + 1800)):
        res = []
        for i in np.where((tod == anchor) & (dow < 5))[0]:  # i = the candle opening at the anchor
            if i < 8:
                continue
            hi, lo = H[i - 8:i].max(), L[i - 8:i].min()
            for j in range(i, min(i + 10, len(C))):  # closes from anchor+15m to anchor+2.5h
                side = 1 if C[j] > hi else -1 if C[j] < lo else 0
                if side:
                    e = C[j]
                    stop = e * (1 - 0.0045 * side)
                    res.append(resolve(H, L, C, j, e, stop, e + side * 1.5 * abs(e - stop), side, 96, TAKER))
                    break
        summary(label, res)


def impulse_pullback():
    print("B) impulse pullback, 1h")
    for sym in ("BTCUSDT", "ETHUSDT", "HYPEUSDT"):
        a = load(sym, "1h")
        O, H, L, C = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        tr = np.maximum(H[1:], C[:-1]) - np.minimum(L[1:], C[:-1])
        atr = np.r_[np.nan, np.convolve(tr, np.ones(14) / 14, "full")[:len(tr)]]
        for side in (1, -1):
            res, i = [], 15
            while i < len(C) - 40:
                body = (C[i] - O[i]) * side
                if body >= 3 * atr[i - 1]:
                    entry = C[i] - side * 0.25 * abs(C[i] - O[i])
                    stop = (O[i] + C[i]) / 2 - side * 0.1 * atr[i - 1]
                    tgt = entry + side * 2 * abs(entry - stop)
                    for j in range(i + 1, i + 13):
                        if (L[j] <= entry) if side > 0 else (H[j] >= entry):
                            # the fill candle: count a stop touch in it (conservative)
                            if (L[j] <= stop) if side > 0 else (H[j] >= stop):
                                res.append(-1 - (MAKER + TAKER) * entry / abs(entry - stop))
                            else:
                                res.append(resolve(H, L, C, j, entry, stop, tgt, side, 24, MAKER))
                            break
                    i += 12
                i += 1
            summary(f"{sym} {'up' if side > 0 else 'down'}-impulse {'long' if side > 0 else 'short'}", res)


if __name__ == "__main__":
    release_break()
    impulse_pullback()

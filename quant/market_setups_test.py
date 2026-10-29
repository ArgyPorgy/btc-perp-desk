"""Do the desk's BTC setups carry over to other perps? (2026-10-29: ETH and HYPE added to the desk.)

Same rules as the BTC tests, on each market's own Binance perp 1h history (archive since its listing):
  S10/S20  LONG: 4h candle wicks below the prior 10/20-day low and closes back above -> long at the close, stop 0.1%
           under the wick, target 1.5R / 2R. Any regime. (reentry_test.py, one-shot hold)
  B20      SHORT: first 4h close below the prior 20-day low while the daily is below its EMA200 -> stop 0.1% over
           that 4h candle's high, 1.5R. (short_test.py)
  R10      SHORT: first 1h retest of a broken 10-day low within 48h, daily below EMA200 -> stop 0.3% over
           max(high, level), 2R.
One shot, 168h time exit, taker fees on entry/stop (0.05%), maker on target (0.02%), stop first if both touch in an
hour, 3-day cooldown. Shorts skip stops under 0.4% of price. Desk rule: n >= 15, avg >= 0, both halves >= 0, t >= 1.5.
Run: python3 market_setups_test.py [ETHUSDT HYPEUSDT ...]   (default ETHUSDT HYPEUSDT BTCUSDT)
"""
import json
import sys
import time
import urllib.request
from pathlib import Path

import numpy as np

from fapi import base  # Binance futures REST, or the local fallback where it is geo-blocked
REST = base()
DATA = Path(__file__).parent / "data"
TAKER, MAKER, HOLD, COOL, MIN_RISK = 0.0005, 0.0002, 168, 3, 0.004


def klines(sym):
    path = DATA / f"{sym}_PERP_1h.npy"
    if sym == "BTCUSDT" and not path.exists():
        path = DATA / "BTCUSDT_PERP_1h.npy"
    rows = list(np.load(path)) if path.exists() else []
    start = int(rows[-1][0]) + 3600_000 if rows else 1567900800000
    while True:
        with urllib.request.urlopen(f"{REST}/fapi/v1/klines?symbol={sym}&interval=1h&limit=1500&startTime={start}", timeout=60) as r:
            k = json.load(r)
        if not k:
            break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])] for x in k]
        start = k[-1][0] + 3600_000
        if start > time.time() * 1000:
            break
    a = np.array(rows)
    a = a[a[:, 0] + 3600_000 <= time.time() * 1000]
    np.save(path, a)
    return a


def ema(x, n):
    out = np.empty_like(x)
    k = 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


def run(sym):
    a = klines(sym)
    t, H, L, C = a[:, 0], a[:, 2], a[:, 3], a[:, 4]
    N = len(C)
    day = (t // 1000 // 86400).astype(np.int64)
    du, d_first = np.unique(day, return_index=True)
    d_close = C[np.r_[d_first[1:] - 1, N - 1]]
    d_e200 = ema(d_close, 200)

    def bear(i):
        di = np.searchsorted(du, day[i]) - 1
        return di >= 200 and d_close[di] < d_e200[di]

    def trade(i, stop, k, side):
        e = C[i]
        risk = (e - stop) * side
        tgt = e + side * k * risk
        fee = lambda x: (TAKER + x) * e / risk
        for j in range(i + 1, min(i + 1 + HOLD, N)):
            if (L[j] <= stop) if side > 0 else (H[j] >= stop):
                return -1 - fee(TAKER)
            if (H[j] >= tgt) if side > 0 else (L[j] <= tgt):
                return k - fee(MAKER)
        return (C[min(i + HOLD, N - 1)] - e) * side / risk - fee(TAKER)

    ev, last = {}, {}

    def add(name, i, stop, k, side):
        if day[i] - last.get(name, -99) <= COOL or i + HOLD >= N:
            return
        if side < 0 and stop - C[i] < MIN_RISK * C[i]:
            return
        last[name] = day[i]
        ev.setdefault(name, []).append(trade(i, stop, k, side))

    for i in range(20 * 24 + 8, N):
        if (t[i] // 1000 + 3600) % 14400:
            continue
        c_hi, c_lo = H[i - 3:i + 1].max(), L[i - 3:i + 1].min()
        for nd, k, name in ((10, 1.5, "S10 long"), (20, 2.0, "S20 long")):
            lv = L[i - nd * 24 - 3:i - 3].min()
            if c_lo < lv < C[i]:
                add(name, i, c_lo * 0.999, k, 1)
        if not bear(i):
            continue
        lo20, lo10 = L[i - 480 - 3:i - 3].min(), L[i - 240 - 3:i - 3].min()
        if C[i] < lo20 <= C[i - 4]:
            add("B20 short", i, c_hi * 1.001, 1.5, -1)
        if C[i] < lo10 <= C[i - 4]:
            for j in range(i + 1, min(i + 49, N)):
                if C[j] > lo10:
                    break
                if H[j] >= lo10 * 0.999:
                    add("R10 short", j, max(H[j], lo10) * 1.003, 2.0, -1)
                    break

    span = f"{time.strftime('%Y-%m-%d', time.gmtime(t[0] / 1000))} to {time.strftime('%Y-%m-%d', time.gmtime(t[-1] / 1000))}"
    print(f"\n{sym} perp 1h, {N:,} bars ({span}); daily {'BEAR' if bear(N - 1) else 'bull'} regime now")
    print(f"  {'setup':10}{'n':>5}{'R/trade':>9}{'±':>6}{'halves':>15}{'win':>6}{'t':>6}  verdict")
    for name in ("S10 long", "S20 long", "B20 short", "R10 short"):
        r = np.array(ev.get(name, []))
        if len(r) < 2:
            print(f"  {name:10}{len(r):5d}  too few events")
            continue
        h = len(r) // 2
        se = r.std() / np.sqrt(len(r))
        ok = len(r) >= 15 and r.mean() >= 0 and r[:h].mean() >= 0 and r[h:].mean() >= 0 and r.mean() / se >= 1.5
        print(f"  {name:10}{len(r):5d}{r.mean():+9.2f}{se:6.2f}{r[:h].mean():+8.2f} /{r[h:].mean():+5.2f}{np.mean(r > 0):6.0%}"
              f"{r.mean() / se:6.1f}  {'PASS' if ok else 'n<15' if len(r) < 15 else 'fail'}")


if __name__ == "__main__":
    for s in sys.argv[1:] or ["ETHUSDT", "HYPEUSDT", "BTCUSDT"]:
        run(s.upper())

"""Short-side setups for the desk (2026-10-28: "you have to play both sides").

Earlier short tests were narrow: breakdowns only inside daily UPtrends, and high-sweep fades with no trend split.
This file tests the bear-side playbook properly, every setup split by daily regime:

  FR10/FR20  failed rally: 4h candle wicks above the prior 10/20-day high and closes back below -> short at the close,
             stop 0.1% above the wick.
  BD10/BD20  breakdown: first 4h close below the prior 10/20-day low -> short at the close, stop 0.1% above that 4h
             candle's high.
  RT10/RT20  breakdown retest: after a BD event, the first 1h candle within 48h that trades back up to the broken
             level and closes below it -> short, stop 0.3% above max(that candle's high, the level). Cancelled if a 1h
             candle closes back above the level first.
  CROWD      crowded longs: at a 4h close, funding is in its top 5% of the prior 90 days and price is up >= 5% over 72h
             -> short, stop 0.2% above the 24h high.

Regimes (last CLOSED day): all / daily close < EMA200 ("bear") / daily close < EMA50.
Exits: one shot, target k*R or stop, 168h time exit. Fees: taker 0.05% entry and stop, maker 0.02% target. A stop and
target in the same hour counts as the stop. Trades with risk < 0.4% of price are skipped (fees would dominate).
Cooldown 3 days per setup. Desk rule: tradable only with avg R >= 0, n >= 15 and both halves >= 0, after fees, AND
t = avg / standard error >= 1.5: on a pure random walk FR10 passed the old rule (+0.07R, n=152, t=0.6), so it lets noise in.
Data: Binance BTCUSDT perp 1h + funding since Sep 2019, cached in quant/data/ (same cache as btc_outlook.py).
Run: python3 short_test.py
"""
import json
import os
import time
import urllib.request
from pathlib import Path

import numpy as np

from fapi import base  # Binance futures REST, or the local fallback where it is geo-blocked
REST = base()
DATA = Path(os.environ.get("SHORT_TEST_DATA", Path(__file__).parent / "data"))
DATA.mkdir(exist_ok=True)
TAKER, MAKER, HOLD, MIN_RISK, COOL = 0.0005, 0.0002, 168, 0.004, 3
TARGETS = (1.0, 1.5, 2.0, 3.0)


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def klines():
    path = DATA / "BTCUSDT_PERP_1h.npy"
    rows = list(np.load(path)) if path.exists() else []
    if os.environ.get("SHORT_TEST_OFFLINE"):
        return np.array(rows)
    start = int(rows[-1][0]) + 3600_000 if rows else 1567900800000
    while True:
        k = get(f"{REST}/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=1500&startTime={start}")
        if not k:
            break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])] for x in k]
        start = k[-1][0] + 3600_000
        if len(k) < 1500:
            break
    a = np.array(rows)
    a = a[a[:, 0] + 3600_000 <= time.time() * 1000]
    np.save(path, a)
    return a


def funding():
    path = DATA / "funding.npy"
    out = list(np.load(path)) if path.exists() else []
    if os.environ.get("SHORT_TEST_OFFLINE"):
        return np.array(out)
    start = int(out[-1][0]) + 1 if out else 1567900800000
    while True:
        f = get(f"{REST}/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1000&startTime={start}")
        if not f:
            break
        out += [(x["fundingTime"], float(x["fundingRate"])) for x in f]
        start = f[-1]["fundingTime"] + 1
        if len(f) < 1000:
            break
    a = np.array(out)
    np.save(path, a)
    return a


def ema(x, n):
    out = np.empty_like(x)
    k = 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


a = klines()
t, O, H, L, C = a[:, 0], a[:, 1], a[:, 2], a[:, 3], a[:, 4]
N = len(C)
fr = funding()
fund = np.interp(t, fr[:, 0], fr[:, 1]) if len(fr) else np.zeros(N)

day = (t // 1000 // 86400).astype(np.int64)
du, d_first = np.unique(day, return_index=True)
d_close = C[np.r_[d_first[1:] - 1, N - 1]]
d_e200, d_e50 = ema(d_close, 200), ema(d_close, 50)
closes4h = [i for i in range(N) if (t[i] // 1000 + 3600) % 14400 == 0]


def regime(i):
    di = np.searchsorted(du, day[i]) - 1  # last closed day
    if di < 200:
        return None
    return {"all": True, "bear": d_close[di] < d_e200[di], "<EMA50": d_close[di] < d_e50[di]}


def short(i, stop, k):
    """R of a short at C[i] with this stop and a k*R target, after fees."""
    e = C[i]
    risk = stop - e
    tgt = e - k * risk
    fee = lambda exit_fee: (TAKER + exit_fee) * e / risk
    for j in range(i + 1, min(i + 1 + HOLD, N)):
        if H[j] >= stop:
            return -1 - fee(TAKER)
        if L[j] <= tgt:
            return k - fee(MAKER)
    j = min(i + HOLD, N - 1)
    return (e - C[j]) / risk - fee(TAKER)


def events():
    ev = {}
    last = {}

    def add(name, i, stop):
        if stop - C[i] < MIN_RISK * C[i] or day[i] - last.get(name, -99) <= COOL or i + HOLD >= N:
            return
        last[name] = day[i]
        ev.setdefault(name, []).append((i, stop))

    for nd in (10, 20):
        w = nd * 24
        for i in closes4h:
            if i < w + 8:
                continue
            hi, lo = H[i - w - 3:i - 3].max(), L[i - w - 3:i - 3].min()  # prior N days, excluding this 4h candle
            c_hi, c_lo = H[i - 3:i + 1].max(), L[i - 3:i + 1].min()
            if c_hi > hi > C[i]:
                add(f"FR{nd}", i, c_hi * 1.001)
            if C[i] < lo <= C[i - 4]:
                add(f"BD{nd}", i, c_hi * 1.001)
                for j in range(i + 1, min(i + 49, N)):  # retest of the broken level
                    if C[j] > lo:
                        break
                    if H[j] >= lo * 0.999:
                        add(f"RT{nd}", j, max(H[j], lo) * 1.003)
                        break
    for i in closes4h:
        if i < 90 * 24 + 72:
            continue
        hist = fund[i - 90 * 24:i]
        if fund[i] >= np.quantile(hist, 0.95) and fund[i] > 0 and C[i] / C[i - 72] - 1 >= 0.05:
            add("CROWD", i, H[i - 23:i + 1].max() * 1.002)
    return ev


print(f"BTC perp 1h {N:,} bars, {time.strftime('%Y-%m-%d', time.gmtime(t[0] / 1000))} to "
      f"{time.strftime('%Y-%m-%d', time.gmtime(t[-1] / 1000))}; funding points {len(fr):,}")
print(f"{'setup':7}{'regime':8}{'target':>7}{'n':>5}{'R/trade':>9}{'±':>6}{'halves':>15}{'win':>6}{'t':>6}  verdict")
passing = []
for name, ev in sorted(events().items()):
    for reg in ("all", "bear", "<EMA50"):
        sub = [(i, s) for i, s in ev if (r := regime(i)) and r[reg]]
        if len(sub) < 5:
            continue
        for k in TARGETS:
            r = np.array([short(i, s, k) for i, s in sub])
            h = len(r) // 2
            a1, a2 = r[:h].mean(), r[h:].mean()
            tstat = r.mean() / (r.std() / np.sqrt(len(r)))
            ok = len(r) >= 15 and r.mean() >= 0 and a1 >= 0 and a2 >= 0 and tstat >= 1.5
            if ok:
                passing.append((name, reg, k, len(r), r.mean()))
            print(f"{name:7}{reg:8}{k:6g}R{len(r):5d}{r.mean():+9.2f}{r.std() / np.sqrt(len(r)):6.2f}"
                  f"{a1:+8.2f} /{a2:+5.2f}{np.mean(r > 0):6.0%}{tstat:6.1f}  {'PASS' if ok else ''}")
print("\npassing the desk rule (n>=15, avg>=0, both halves>=0, t>=1.5):" if passing else "\nno short setup passes the desk rule")
for p in passing:
    print(f"  {p[0]} {p[1]} {p[2]:g}R: n={p[3]}, {p[4]:+.2f}R/trade")

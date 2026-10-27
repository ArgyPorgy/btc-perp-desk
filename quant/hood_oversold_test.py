"""Is HOOD 'oversold' a long? Binance HOODUSDT TradFi perp 1h since listing (Feb 2026). Small sample: read with care.
Condition: 1h close at least X% below the 1h EMA200 (the 2026-10-28 reading: -8.9%). Episodes de-clustered (48h apart).
Reports forward returns and the odds of reaching +9.3% (87.8 -> 96, the user's target) before a stop.
Run: python3 hood_oversold_test.py
"""
import json
import urllib.request

import numpy as np


def klines():
    out, start = [], 0
    while True:
        u = f"https://fapi.binance.com/fapi/v1/klines?symbol=HOODUSDT&interval=1h&limit=1500&startTime={start}"
        k = json.load(urllib.request.urlopen(u, timeout=30))
        out += k
        if len(k) < 1500:
            return np.array([[float(x[0]), float(x[2]), float(x[3]), float(x[4])] for x in out])
        start = k[-1][0] + 1


a = klines()
t, H, L, C = a.T
N = len(C)
ema = np.empty(N); ema[0] = C[0]
for i in range(1, N):
    ema[i] = C[i] * 2 / 201 + ema[i - 1] * 199 / 201
dist = C / ema - 1
print(f"HOODUSDT 1h bars: {N} ({N / 24:.0f} days). now: close {C[-1]:.2f}, {dist[-1] * 100:+.1f}% vs EMA200")
print(f"how often HOOD sat this far below the 1h EMA200: {np.mean(dist[250:] <= dist[-1]) * 100:.1f}% of hours")

for thr in (-0.06, -0.08):
    ev, last = [], -999
    for i in range(250, N - 1):
        if dist[i] <= thr and i - last > 48:
            ev.append(i); last = i
    print(f"\nclose >= {-thr * 100:.0f}% below 1h EMA200: {len(ev)} episodes")
    for h in (24, 72, 168):
        r = [C[i + h] / C[i] - 1 for i in ev if i + h < N]
        if r:
            print(f"  {h:3}h later: up {np.mean(np.array(r) > 0):4.0%}  median {np.median(r) * 100:+5.1f}%  (n={len(r)})")
    for stop in (0.015, 0.04):
        res = []
        for i in ev:
            e, hit = C[i], None
            for j in range(i + 1, min(i + 169, N)):
                if L[j] <= e * (1 - stop): hit = 0; break
                if H[j] >= e * 1.093: hit = 1; break
            if hit is not None: res.append(hit)
        if res:
            rr = 0.093 / stop
            print(f"  +9.3% before -{stop * 100:.1f}% (R {rr:.1f}) within 7d: {np.mean(res):4.0%} of {len(res)} resolved; random walk {1 / (1 + rr):4.0%}")
    print("  episodes: " + ", ".join(f"{np.datetime_as_string(np.datetime64(int(t[i]), 'ms'), unit='D')} ({dist[i] * 100:+.0f}%)" for i in ev))

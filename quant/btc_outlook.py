"""What happened next, historically, when BTC looked like it does now? (Binance BTCUSDT perp, Sep 2019 - now)

1. Downloads hourly perp klines (with taker-buy volume) and funding history.
2. Builds the same context features the dashboard shows, using only information available at each hour
   (higher-timeframe values come from the last CLOSED 4h / daily bar: no look-ahead).
3. Finds past hours matching today's state and reports forward returns, and how specific long / short trade
   plans from today's levels would have played out on those analogs, vs. the random-walk baseline.
4. Monte Carlo: bootstraps the last 90 days of hourly returns to estimate odds of touching nearby levels.
Run: python3 btc_outlook.py
"""
import json
import time
import urllib.request
from pathlib import Path

import numpy as np

from fapi import base  # Binance futures REST, or the local fallback where it is geo-blocked
REST = base()
DATA = Path(__file__).parent / "data"
DATA.mkdir(exist_ok=True)
rng = np.random.default_rng(42)


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def klines():
    path = DATA / "BTCUSDT_PERP_1h.npy"
    rows = list(np.load(path)) if path.exists() else []
    start = int(rows[-1][0]) + 3600_000 if rows else 1567900800000  # 2019-09-08
    while True:
        k = get(f"{REST}/fapi/v1/klines?symbol=BTCUSDT&interval=1h&limit=1500&startTime={start}")
        if not k:
            break
        rows += [[x[0], float(x[1]), float(x[2]), float(x[3]), float(x[4]), float(x[5]), float(x[9])] for x in k]
        start = k[-1][0] + 3600_000
        if len(k) < 1500:
            break
    a = np.array(rows)
    a = a[a[:, 0] + 3600_000 <= time.time() * 1000]  # closed hours only
    np.save(path, a)
    return a


def funding():
    out, start = [], 1567900800000
    while True:
        f = get(f"{REST}/fapi/v1/fundingRate?symbol=BTCUSDT&limit=1000&startTime={start}")
        if not f:
            break
        out += [(x["fundingTime"], float(x["fundingRate"])) for x in f]
        start = f[-1]["fundingTime"] + 1
        if len(f) < 1000:
            break
    return np.array(out)


def ema(x, n):
    out = np.empty_like(x)
    k = 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


def resample(t, o, h, l, c, sec):
    key = (t // 1000 // sec).astype(np.int64)
    idx = np.flatnonzero(np.r_[True, key[1:] != key[:-1]])
    ends = np.r_[idx[1:], len(t)] - 1
    return key[idx], o[idx], np.maximum.reduceat(h, idx), np.minimum.reduceat(l, idx), c[ends], ends


def htf_feature(t, sec, closes_htf, keys_htf, ends_htf, values_htf):
    """For each hour, the value from the last fully CLOSED higher-timeframe bar."""
    out = np.full(len(t), np.nan)
    hour_key = (t // 1000 // sec).astype(np.int64)
    pos = np.searchsorted(keys_htf, hour_key) - 1  # previous (closed) HTF bar
    ok = pos >= 0
    out[ok] = values_htf[pos[ok]]
    # the current HTF bar closes on its last hour: then that bar itself is closed
    last_hour = np.zeros(len(t), bool)
    last_hour[ends_htf] = True
    cur = np.searchsorted(keys_htf, hour_key)
    out[last_hour] = values_htf[cur[last_hour]]
    return out


def structure_state(H, L, C, n):
    """Last swing-break direction (+1 up / -1 down), pivots of n bars each side, confirmed n bars later."""
    st = np.zeros(len(C))
    hi = lo = None
    hi_b = lo_b = True
    trend = 0
    for i in range(2 * n, len(C)):
        p = i - n
        w = slice(p - n, i + 1)
        if H[p] >= H[w].max():
            hi, hi_b = H[p], False
        if L[p] <= L[w].min():
            lo, lo_b = L[p], False
        if hi is not None and not hi_b and C[i] > hi:
            trend, hi_b = 1, True
        if lo is not None and not lo_b and C[i] < lo:
            trend, lo_b = -1, True
        st[i] = trend
    return st


a = klines()
t, O, H, L, C, V, TB = a.T
N = len(C)
print(f"hourly perp bars: {N:,}  ({time.strftime('%Y-%m-%d', time.gmtime(t[0] / 1000))} .. "
      f"{time.strftime('%Y-%m-%d %H:%M', time.gmtime(t[-1] / 1000))} UTC, last close {C[-1]:,.1f})")

# ---- features (all known at each hour's close)
ema200_1h = ema(C, 200)
k4, o4, h4, l4, c4, e4 = resample(t, O, H, L, C, 14400)
kd, od, hd, ld, cd, ed = resample(t, O, H, L, C, 86400)
ema200_4h = htf_feature(t, 14400, c4, k4, e4, ema(c4, 200))
close_4h = htf_feature(t, 14400, c4, k4, e4, c4)
ema200_1d = htf_feature(t, 86400, cd, kd, ed, ema(cd, 200))
ema50_1d = htf_feature(t, 86400, cd, kd, ed, ema(cd, 50))
close_1d = htf_feature(t, 86400, cd, kd, ed, cd)
struct_1h = structure_state(H, L, C, 20)
delta = 2 * TB - V
delta12 = np.convolve(delta, np.ones(12), "full")[:N]
wk = ((t / 1000 / 86400 + 3) // 7).astype(np.int64)
p = (H + L + C) / 3
wvwap = np.empty(N)
pv = vv = 0.0
for i in range(N):
    if i == 0 or wk[i] != wk[i - 1]:
        pv = vv = 0.0
    pv += p[i] * V[i]
    vv += V[i]
    wvwap[i] = pv / vv if vv else p[i]
low20d = np.array([L[max(0, i - 480):i].min() if i > 0 else L[0] for i in range(N)])
dist_low = C / low20d - 1
fr = funding()
fund = np.interp(t, fr[:, 0], fr[:, 1]) if len(fr) else np.zeros(N)

feat = {
    "1h below EMA200": C < ema200_1h,
    "4h below EMA200": close_4h < ema200_4h,
    "1d above EMA200": close_1d > ema200_1d,
    "1d below EMA50": close_1d < ema50_1d,
    "1h last break down": struct_1h == -1,
    "12h taker delta < 0": delta12 < 0,
    "below weekly VWAP": C < wvwap,
    "within 2% of 20-day low": dist_low < 0.02,
}
now = {k: bool(v[-1]) for k, v in feat.items()}
print("\ncurrent state (last closed hour):")
for k, v in now.items():
    print(f"  {'YES' if v else 'no ':>3}  {k}")
print(f"  (distance to 20-day low {dist_low[-1] * 100:.2f}%, funding {fund[-1] * 100:.4f}%, 12h delta {delta12[-1]:+,.0f} BTC)")

# ---- forward outcomes
HZ = {"24h": 24, "72h": 72, "7d": 168}
valid = np.arange(N) < N - 168
fwd = {k: np.full(N, np.nan) for k in HZ}
for k, h in HZ.items():
    fwd[k][:-h] = C[h:] / C[:-h] - 1


def episodes(mask):
    """Count distinct episodes (matches separated by > 24h) so overlapping hours don't fake a big sample."""
    idx = np.flatnonzero(mask)
    return 0 if len(idx) == 0 else 1 + int(np.sum(np.diff(idx) > 24))


def report(name, mask):
    m = mask & valid
    n = m.sum()
    if n < 30:
        print(f"  {name:<44} hours {n:>6}  (too few)")
        return
    cells = []
    for k in HZ:
        r = fwd[k][m]
        cells.append(f"{k}: up {np.mean(r > 0):5.1%} med {np.median(r) * 100:+5.2f}%")
    print(f"  {name:<44} hours {n:>6} episodes {episodes(m):>4} | " + " | ".join(cells))


print("\nforward returns after matching hours (since 2019):")
report("all hours (baseline)", np.ones(N, bool))
for k, v in feat.items():
    if now[k]:
        report(f"only: {k}", v)
core = ["1h below EMA200", "4h below EMA200", "1d above EMA200", "1h last break down", "12h taker delta < 0", "below weekly VWAP"]
mask_core = np.all([feat[k] for k in core], axis=0)
report("ALL 6 core features (today's setup)", mask_core)
mask_full = mask_core & feat["within 2% of 20-day low"] & feat["1d below EMA50"]
report("core + near 20d low + below 1d EMA50", mask_full)


# ---- trade plans from today's levels, replayed on analog hours (percent distances)
def replay(mask, side, stop_pct, tgt_pct, max_h=168):
    res = []
    for i in np.flatnonzero(mask & valid):
        e = C[i]
        stop, tgt = e * (1 - side * stop_pct), e * (1 + side * tgt_pct)
        out = 0
        for j in range(i + 1, min(i + 1 + max_h, N)):
            hit_stop = L[j] <= stop if side == 1 else H[j] >= stop
            hit_tgt = H[j] >= tgt if side == 1 else L[j] <= tgt
            if hit_stop:  # same-hour ambiguity counts as a loss
                out = -1
                break
            if hit_tgt:
                out = 1
                break
        res.append(out)
    r = np.array(res)
    return len(r), np.mean(r == 1), np.mean(r == -1), np.mean(r == 0)


px = C[-1]
plans = [
    ("LONG  stop 79,450 (under swing low) / target 82,000 (call wall)", 1, 79450, 82000),
    ("LONG  stop 79,450 / target 81,000 (put wall, 1h VAL)", 1, 79450, 81000),
    ("SHORT stop 81,300 (over 81k wall + 1h VAL) / target 79,700 (swing low)", -1, 81300, 79700),
    ("SHORT stop 81,300 / target 78,450 (4h FVG bottom)", -1, 81300, 78450),
]
print(f"\ntrade plans from {px:,.0f} (no fees), resolved within 7 days:")
print(f"  {'plan':<70} {'R':>4} {'random walk':>11} | {'analogs':>18} | {'all history':>18}")
for name, side, stop, tgt in plans:
    sp, tp = abs(px - stop) / px, abs(tgt - px) / px
    rr = tp / sp
    rw = sp / (sp + tp)  # zero-drift probability of reaching the target first
    na, wa, la, _ = replay(mask_core, side, sp, tp)
    sub = np.zeros(N, bool)
    sub[rng.choice(np.flatnonzero(valid), 6000, replace=False)] = True
    nb, wb, lb, _ = replay(sub, side, sp, tp)
    ev = lambda w, l: w * rr - l
    print(f"  {name:<70} {rr:4.2f} {rw:10.1%} | win {wa:5.1%} EV {ev(wa, la):+5.2f}R | win {wb:5.1%} EV {ev(wb, lb):+5.2f}R")

# ---- Monte Carlo: block bootstrap of the last 90 days of hourly returns
r90 = np.diff(np.log(C[-90 * 24:]))
r90 = r90 - r90.mean()  # remove the recent trend: keep real volatility and fat tails, assume no drift
hi_r = np.log(H[-90 * 24 + 1:] / C[-90 * 24:-1])
lo_r = np.log(L[-90 * 24 + 1:] / C[-90 * 24:-1])
levels = [83000, 82000, 81000, 79700, 79000, 78000]
S, B = 20000, 24
print(f"\nMonte Carlo, zero drift ({S:,} paths, 24h blocks from the last 90 days; vol {np.std(r90) * np.sqrt(24 * 365) * 100:.0f}% annualised):")
print(f"  {'level':>8} " + " ".join(f"{h:>8}" for h in ["24h", "72h", "7d"]))
paths_hit = {lv: [] for lv in levels}
for hz in (24, 72, 168):
    nb = hz // B + (hz % B > 0)
    starts = rng.integers(0, len(r90) - B, size=(S, nb))
    idx = (starts[:, :, None] + np.arange(B)).reshape(S, -1)[:, :hz]
    logp = np.log(px) + np.cumsum(r90[idx], axis=1)
    prev = np.concatenate([np.full((S, 1), np.log(px)), logp[:, :-1]], axis=1)
    hp, lp = prev + hi_r[idx], prev + lo_r[idx]
    for lv in levels:
        hit = (hp.max(1) >= np.log(lv)) if lv > px else (lp.min(1) <= np.log(lv))
        paths_hit[lv].append(hit.mean())
    if hz == 168:
        end = np.exp(logp[:, -1])
for lv in levels:
    print(f"  {lv:>8,} " + " ".join(f"{p:8.1%}" for p in paths_hit[lv]) + f"   ({(lv / px - 1) * 100:+.1f}%)")
print(f"  7d end: median {np.median(end):,.0f}, 25-75% {np.percentile(end, 25):,.0f}-{np.percentile(end, 75):,.0f}, "
      f"P(higher than now) {np.mean(end > px):.1%}")

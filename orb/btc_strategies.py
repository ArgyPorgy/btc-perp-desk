"""Backtest published / well-known Bitcoin strategies on Binance BTCUSDT hourly data (2018 - 21 Oct 2026).

Every strategy is expressed as an hourly position (1 = long, 0 = flat) decided with information available
BEFORE that hour starts. Daily signals use the UTC daily close and apply to the whole next UTC day.
Costs: 0.07% per side (taker fee + slippage). No leverage, no funding (spot-like).
Run: python3 btc_strategies.py
"""
from datetime import datetime, timezone

import numpy as np

COST = 0.0007
a = np.loadtxt("data/BTCUSDT_1h.csv", delimiter=",")
t = (a[:, 0] // 1000).astype(np.int64)
O, H, L, C = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
hour = (t // 3600) % 24
dayidx = t // 86400
ret = np.empty_like(C)
ret[0] = 0
ret[1:] = C[1:] / C[:-1] - 1  # return of hour i (close i-1 -> close i)

# ---- daily bars (UTC)
days, first = np.unique(dayidx, return_index=True)
last = np.r_[first[1:] - 1, len(t) - 1]
dC = C[last]
dO = O[first]
dH = np.maximum.reduceat(H, first)
dL = np.minimum.reduceat(L, first)
dow = (days + 3) % 7  # 0 = Monday


def sma(x, n):
    out = np.full_like(x, np.nan)
    cs = np.cumsum(np.insert(x, 0, 0))
    out[n - 1:] = (cs[n:] - cs[:-n]) / n
    return out


def rsi(x, n):
    d = np.diff(x, prepend=x[0])
    up, dn = np.clip(d, 0, None), np.clip(-d, 0, None)
    au, ad = np.zeros_like(x), np.zeros_like(x)
    au[n], ad[n] = up[1:n + 1].mean(), dn[1:n + 1].mean()
    for i in range(n + 1, len(x)):
        au[i] = (au[i - 1] * (n - 1) + up[i]) / n
        ad[i] = (ad[i - 1] * (n - 1) + dn[i]) / n
    rs = np.divide(au, ad, out=np.full_like(x, np.inf), where=ad > 0)
    r = 100 - 100 / (1 + rs)
    r[:n] = 50
    return r


def roll_max(x, n):
    return np.array([x[max(0, i - n + 1):i + 1].max() for i in range(len(x))])


def roll_min(x, n):
    return np.array([x[max(0, i - n + 1):i + 1].min() for i in range(len(x))])


def daily_state(enter, exit_):
    """Stateful long/flat from daily enter/exit conditions (evaluated at each day's close)."""
    s = np.zeros(len(enter))
    on = False
    for i in range(len(enter)):
        if not on and enter[i]:
            on = True
        elif on and exit_[i]:
            on = False
        s[i] = on
    return s


def to_hourly(daily_pos):
    """Position decided at close of day d applies to every hour of day d+1."""
    shifted = np.r_[0, daily_pos[:-1]]
    return shifted[np.searchsorted(days, dayidx)]


# ---- indicators
s200, s50, s20, s5 = sma(dC, 200), sma(dC, 50), sma(dC, 20), sma(dC, 5)
sd20 = np.array([dC[max(0, i - 19):i + 1].std() for i in range(len(dC))])
r14, r2 = rsi(dC, 14), rsi(dC, 2)
hi20_prev = np.r_[np.nan, roll_max(dH, 20)[:-1]]
lo10_prev = np.r_[np.nan, roll_min(dL, 10)[:-1]]

S = {}
S["Buy and hold"] = np.ones(len(t))
S["22:00-00:00 UTC only (Quantpedia 2022)"] = ((hour == 22) | (hour == 23)).astype(float)
S["21:00-00:00 UTC only"] = ((hour >= 21)).astype(float)
S["Above 200-day average"] = to_hourly((dC > s200).astype(float))
S["Golden cross (50 > 200 day avg)"] = to_hourly((s50 > s200).astype(float))
S["20-day high breakout, exit 10-day low"] = to_hourly(daily_state(dC > hi20_prev, dC < lo10_prev))
S["RSI(14) momentum: in >55, out <45"] = to_hourly(daily_state(r14 > 55, r14 < 45))
S["RSI(14) dip: buy <30, sell >50"] = to_hourly(daily_state(r14 < 30, r14 > 50))
S["Connors RSI(2)<10 above 200d, sell >5d avg"] = to_hourly(daily_state((r2 < 10) & (dC > s200), dC > s5))
S["Bollinger dip: below lower band, sell at mid"] = to_hourly(daily_state(dC < s20 - 2 * sd20, dC > s20))
S["Mondays + Saturdays only (Santiment)"] = np.isin((dayidx + 3) % 7, [0, 5]).astype(float)
# hourly short-term reversal (Ledger 2021: negative autocorrelation): after a -1.5% hour, hold 4 hours
big_drop = np.r_[False, ret[:-1] < -0.015]
rev = np.zeros(len(t))
for i in np.where(big_drop)[0]:
    rev[i:i + 4] = 1
S["After a -1.5% hour, buy for 4 hours"] = rev
S["22-00 UTC, only when above 200-day avg"] = S["22:00-00:00 UTC only (Quantpedia 2022)"] * S["Above 200-day average"]


def evaluate(pos, lo, hi):
    m = (t >= lo) & (t < hi)
    p, r = pos[m], ret[m]
    change = np.abs(np.diff(np.r_[0, p]))
    net = p * r - change * COST
    eq = np.cumprod(1 + net)
    dd = 1 - eq / np.maximum.accumulate(eq)
    years = m.sum() / 24 / 365.25
    # trades = runs of being long
    starts = np.where(np.diff(np.r_[0, p]) > 0)[0]
    ends = np.where(np.diff(np.r_[p, 0]) < 0)[0]
    tr = np.array([np.prod(1 + net[s:e + 1]) - 1 for s, e in zip(starts, ends)])
    return dict(trades=len(tr), win=(tr > 0).mean() if len(tr) else 0, avg=tr.mean() if len(tr) else 0,
                pf=tr[tr > 0].sum() / -tr[tr < 0].sum() if (tr < 0).any() else np.inf,
                total=eq[-1] - 1, cagr=eq[-1] ** (1 / years) - 1, maxdd=dd.max(), expo=p.mean())


def ts(y, mth=1, d=1):
    return int(datetime(y, mth, d, tzinfo=timezone.utc).timestamp())


PERIODS = {"2018-2022 (in-sample)": (ts(2018), ts(2023)), "2023-Oct 2026 (out-of-sample)": (ts(2023), ts(2026, 10, 22))}

if __name__ == "__main__":
    rows = []
    for name, pos in S.items():
        rows.append((name, {p: evaluate(pos, *rng) for p, rng in PERIODS.items()}))
    for p in PERIODS:
        print(f"\n{p}")
        print(f"  {'strategy':<44} {'trades':>6} {'win%':>6} {'avg trade':>9} {'PF':>5} {'CAGR':>7} {'max DD':>7} {'in mkt':>6}")
        for name, res in sorted(rows, key=lambda x: -x[1][p]["win"]):
            s = res[p]
            print(f"  {name:<44} {s['trades']:>6} {s['win']:6.1%} {s['avg']:+9.2%} {s['pf']:5.2f} "
                  f"{s['cagr']:+7.1%} {s['maxdd']:7.1%} {s['expo']:6.0%}")

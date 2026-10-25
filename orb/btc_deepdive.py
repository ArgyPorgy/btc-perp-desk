"""Follow-ups: fee impact on the hour-of-day strategy, Connors RSI(2) details, and the win-rate trap."""
import numpy as np
import btc_strategies as B
from btc_strategies import S, evaluate, PERIODS, ts, t, H, L, C, O, hour, dC, days, first

# 1. gross (no fees) vs net for the time-of-day strategies
print("1. Hour-of-day strategies, with and without fees (CAGR)")
for name in ["22:00-00:00 UTC only (Quantpedia 2022)", "21:00-00:00 UTC only"]:
    out = []
    for p, rng in PERIODS.items():
        B.COST = 0.0
        g = evaluate(S[name], *rng)["cagr"]
        B.COST = 0.0007
        n = evaluate(S[name], *rng)["cagr"]
        out.append(f"{p.split(' ')[0]}: before fees {g:+.1%}, after {n:+.1%}")
    print(f"  {name:<40} " + " | ".join(out))

# 2. Connors RSI(2) details
print("\n2. Connors RSI(2) dip-buy in an uptrend — trade by trade")
pos = S["Connors RSI(2)<10 above 200d, sell >5d avg"]
starts = np.where(np.diff(np.r_[0, pos]) > 0)[0]
ends = np.where(np.diff(np.r_[pos, 0]) < 0)[0]
trs, yrs, held = [], [], []
for s, e in zip(starts, ends):
    r = C[e] / C[s - 1] - 1 - 2 * 0.0007
    trs.append(r); yrs.append(int(1970 + t[s] / 31557600)); held.append((e - s + 1) / 24)
trs, yrs = np.array(trs), np.array(yrs)
w, l = trs[trs > 0], trs[trs <= 0]
print(f"  all trades 2018-2026: {len(trs)}, win {np.mean(trs>0):.0%}, avg win {w.mean():+.2%}, avg loss {l.mean():+.2%}, "
      f"worst {trs.min():+.2%}, best {trs.max():+.2%}, avg hold {np.mean(held):.1f} days")
for y in sorted(set(yrs)):
    m = yrs == y
    print(f"    {y}: {m.sum():>2} trades, win {np.mean(trs[m]>0):4.0%}, sum {trs[m].sum():+6.1%}")
last12 = t[starts] >= ts(2025, 10, 22)
print(f"  last 12 months: {last12.sum()} trades, win {np.mean(trs[last12]>0):.0%}, sum {trs[last12].sum():+.1%}")

# 3. the win-rate trap: buy every day at 00:00 UTC, take profit +1%, stop -10%, give up after 7 days
print("\n3. Win-rate trap: buy daily at 00:00 UTC, take profit +1%, stop -10%, max 7 days")
for tp, sl in [(0.01, 0.10), (0.005, 0.10), (0.02, 0.05)]:
    res = []
    i = 0
    starts_h = first
    nxt = 0
    for s in starts_h:
        if s < nxt or t[s] < ts(2018):
            continue
        en = O[s]
        out = None
        for k in range(s, min(s + 24 * 7, len(t))):
            if L[k] <= en * (1 - sl):
                out, nxt = -sl, k + 1; break
            if H[k] >= en * (1 + tp):
                out, nxt = tp, k + 1; break
        if out is None:
            k = min(s + 24 * 7, len(t)) - 1
            out, nxt = C[k] / en - 1, k + 1
        res.append(out - 2 * 0.0007)
    r = np.array(res)
    eq = np.cumprod(1 + r)
    print(f"  TP +{tp:.1%} / SL -{sl:.0%}: {len(r)} trades, WIN RATE {np.mean(r>0):.1%}, avg {r.mean():+.3%}, "
          f"total {eq[-1]-1:+.0%} (buy & hold 2018-now: {C[-1]/C[np.searchsorted(t, ts(2018))]-1:+.0%})")

"""Averaging down (or up, for shorts) with no stop loss, on real BTC hourly prices 2018 - Oct 2026.

Rules: open 1 unit (unit = 0.5x your capital in position size). Each time price moves STEP against your
last entry, add another unit, until total position = MAX_LEV x capital (you're out of money).
Close everything when price is TP beyond your average entry, then start again next hour.
No stop. Liquidated if equity falls to Hyperliquid's BTC maintenance margin (1.25% of position).
Fees 0.045% per fill. Funding ignored (longs usually pay it, which would make results worse).
Run: python3 average_down.py
"""
import numpy as np

a = np.loadtxt("data/BTCUSDT_1h.csv", delimiter=",")
t = (a[:, 0] // 1000).astype(np.int64)
O, H, L, C = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
FEE, MM = 0.00045, 0.0125
YEAR = 24 * 365


def run(i0, i1, side=1, unit=0.5, step=0.05, tp=0.02, max_lev=3.0, capital=1.0):
    cash = capital
    qty = avg = 0.0
    last = None
    cycles, cycle_start, longest = 0, None, 0
    peak, maxdd = capital, 0.0
    max_units = int(round(max_lev / unit))
    units = 0
    for i in range(i0, i1):
        if qty == 0:  # open a new cycle at this hour's open
            px = O[i]
            qty, avg, last, units = unit * capital / px, px, px, 1
            cash -= qty * px * FEE
            cycle_start = i
        # adverse move first: add units at each STEP level reached
        adverse = L[i] if side == 1 else H[i]
        while units < max_units:
            lvl = last * (1 - step) if side == 1 else last * (1 + step)
            if (adverse <= lvl) if side == 1 else (adverse >= lvl):
                q = unit * capital / lvl
                avg = (avg * qty + lvl * q) / (qty + q)
                qty += q
                cash -= q * lvl * FEE
                last, units = lvl, units + 1
            else:
                break
        eq_worst = cash + side * qty * (adverse - avg)
        if eq_worst <= MM * qty * adverse:
            return dict(liq=True, cycles=cycles, ret=-1.0, maxdd=1.0, longest=max(longest, i - cycle_start),
                        liq_hour=i - i0)
        maxdd = max(maxdd, 1 - eq_worst / peak)
        target = avg * (1 + side * tp)
        fav = H[i] if side == 1 else L[i]
        if (fav >= target) if side == 1 else (fav <= target):
            cash += side * qty * (target - avg) - qty * target * FEE
            cycles += 1
            longest = max(longest, i - cycle_start)
            qty = 0.0
            peak = max(peak, cash)
    eq = cash + side * qty * (C[i1 - 1] - avg)
    open_age = (i1 - cycle_start) if qty else 0
    return dict(liq=False, cycles=cycles, ret=eq / capital - 1, maxdd=maxdd, longest=max(longest, open_age),
                stuck=qty > 0, liq_hour=None)


starts = np.arange(np.searchsorted(t, 1514764800), len(t) - YEAR, 24 * 7)  # weekly starts from 1 Jan 2018
print(f"{len(starts)} start dates, each run for 1 year\n")
print(f"  {'setup':<38} {'liquidated':>10} {'cycles won':>10} {'median 1y':>9} {'worst 1y':>9} "
      f"{'avg max drop':>12} {'longest wait':>12}")
results = {}
for side, sname in [(1, "LONG"), (-1, "SHORT")]:
    for max_lev in [1.0, 2.0, 3.0, 5.0]:
        rs = [run(s, s + YEAR, side=side, max_lev=max_lev) for s in starts]
        liq = np.mean([r["liq"] for r in rs])
        rets = np.array([r["ret"] for r in rs])
        cyc = np.median([r["cycles"] for r in rs])
        dd = np.mean([r["maxdd"] for r in rs])
        wait = np.max([r["longest"] for r in rs]) / 24
        label = f"{sname}, max {max_lev:.0f}x total, add every -5%"
        results[(side, max_lev)] = rs
        print(f"  {label:<38} {liq:10.1%} {cyc:10.0f} {np.median(rets):+9.1%} {rets.min():+9.1%} "
              f"{dd:12.1%} {wait:9.0f} days")

# one continuous run, like a person who keeps doing it
print("\nOne person doing it continuously from 1 Jan 2018 (3x max, LONG):")
r = run(starts[0], len(t), side=1, max_lev=3.0)
print(f"  {r}")
for y0 in [2019, 2020, 2021, 2022, 2023, 2024, 2025]:
    s = np.searchsorted(t, int(np.datetime64(f"{y0}-01-01").astype("datetime64[s]").astype(int)))
    r = run(s, len(t), side=1, max_lev=3.0)
    rs = run(s, len(t), side=-1, max_lev=3.0)
    fmt = lambda r: (f"LIQUIDATED after {r['liq_hour']/24:.0f} days ({r['cycles']} wins first)" if r["liq"]
                     else f"{r['ret']:+.0%}, {r['cycles']} wins, worst drop {r['maxdd']:.0%}")
    print(f"  start Jan {y0}:  long -> {fmt(r):<52} short -> {fmt(rs)}")

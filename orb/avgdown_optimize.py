"""Optimise the averaging-down long plan for a $500 account, no time limit, real BTC hourly prices.

Plan: cross-margin account of $500. Open a long of UNIT dollars (e.g. $100 margin x 2 = $200 position).
Each time price falls STEP below the last entry, add another UNIT, until total position = MAX_POS.
Close everything when price is TP above the average entry; open a new cycle the next hour.
No stop. Liquidation when equity <= 1.25% of position (Hyperliquid BTC). Fees 0.045% per fill.
Funding ignored (longs usually pay it on Hyperliquid, so real results would be somewhat worse).
Run: python3 avgdown_optimize.py
"""
import numpy as np

a = np.loadtxt("data/BTCUSDT_1h.csv", delimiter=",")
t = (a[:, 0] // 1000).astype(np.int64)
O, H, L, C = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
N = len(t)
FEE, MM = 0.00045, 0.0125

# 200-day average (hourly series of the previous day's value), for the optional trend filter
day = t // 86400
du, df = np.unique(day, return_index=True)
dclose = C[np.r_[df[1:] - 1, N - 1]]
s200 = np.full(len(dclose), np.nan)
cs = np.cumsum(np.insert(dclose, 0, 0))
s200[199:] = (cs[200:] - cs[:-200]) / 200
above200 = np.r_[False, (dclose > s200)[:-1]][np.searchsorted(du, day)]


def first_cross(i, down, up):
    """First bar >= i whose low <= down or high >= up (chunked numpy scan)."""
    w = 64
    while i < N:
        j = min(N, i + w)
        hit = (L[i:j] <= down) | (H[i:j] >= up)
        if hit.any():
            return i + int(np.argmax(hit))
        i, w = j, min(w * 4, 1 << 16)
    return N


def run(i0, unit=200.0, step=0.10, tp=0.03, max_pos=1000.0, capital=500.0, trend=False, record=False):
    cash = capital
    i = i0
    cycles = 0
    path = [] if record else None
    while i < N:
        if trend and not above200[i]:  # only start new cycles when BTC is above its 200-day average
            k = np.argmax(above200[i:])
            if not above200[i + k]:
                break
            i += k
            continue
        px = O[i]
        qty, avg, last, pos = unit / px, px, px, unit
        cash -= unit * FEE
        if record:
            path.append((i, cash, qty, avg))
        j = i
        while True:
            add_lvl = last * (1 - step) if pos + unit <= max_pos + 1e-9 else -1.0
            liq_lvl = (qty * avg - cash) / (qty * (1 - MM))
            tp_lvl = avg * (1 + tp)
            j = first_cross(j, max(add_lvl, liq_lvl), tp_lvl)
            if j >= N:
                eq = cash + qty * (C[-1] - avg)
                return dict(liq=False, final=eq, cycles=cycles, open=True, path=path)
            if L[j] <= max(add_lvl, liq_lvl):
                if add_lvl >= liq_lvl and add_lvl > 0:
                    q = unit / add_lvl
                    avg = (avg * qty + add_lvl * q) / (qty + q)
                    qty += q
                    pos += unit
                    cash -= unit * FEE
                    last = add_lvl
                    if record:
                        path.append((j, cash, qty, avg))
                    continue  # re-check the same bar
                if record:
                    path.append((j, 0.0, 0.0, 0.0))
                return dict(liq=True, final=0.0, cycles=cycles, liq_t=t[j], open=False, path=path)
            # take profit
            cash += qty * (tp_lvl - avg) - qty * tp_lvl * FEE
            cycles += 1
            if record:
                path.append((j, cash, 0.0, 0.0))
            i = j + 1
            break
    return dict(liq=False, final=cash, cycles=cycles, open=False, path=path)


def survivable_drop(unit, step, max_pos, capital=500.0):
    """How far BTC can fall from your first entry before liquidation, once fully loaded."""
    n = int(max_pos // unit)
    prices = (1 - step) ** np.arange(n)
    qty = (unit / prices).sum()
    avg = unit * n / qty
    p = (qty * avg - capital) / (qty * (1 - MM))
    return 1 - p


if __name__ == "__main__":
    years_left = lambda i: (t[-1] - t[i]) / 31557600
    starts = [np.searchsorted(t, int(np.datetime64(f"{y}-{m:02d}-01", "s").astype(int)))
              for y in range(2018, 2026) for m in (1, 4, 7, 10)]
    print(f"{len(starts)} start dates (every quarter 2018-2025), each held until Oct 2026 or liquidation\n")
    print(f"  {'position per entry':<20} {'add every':>9} {'take profit':>11} {'survives drop':>13} "
          f"{'liquidated':>10} {'median $/yr':>11} {'avg final $':>11}")
    rows = []
    for unit, label in [(200, "$100 margin x2"), (100, "$50 margin x2")]:
        for step in [0.03, 0.05, 0.10, 0.15, 0.20]:
            for tp in [0.01, 0.02, 0.03, 0.05, 0.10]:
                rs = [run(s, unit=unit, step=step, tp=tp) for s in starts]
                liq = np.mean([r["liq"] for r in rs])
                finals = np.array([r["final"] for r in rs])
                per_yr = np.array([(r["final"] - 500) / years_left(s) for r, s in zip(rs, starts)])
                rows.append((label, step, tp, survivable_drop(unit, step, 1000), liq, np.median(per_yr), finals.mean()))
    for r in sorted(rows, key=lambda r: (r[4], -r[5]))[:20]:
        print(f"  {r[0]:<20} {r[1]:>8.0%} {r[2]:>10.0%} {r[3]:>12.0%} {r[4]:>10.0%} {r[5]:>+11.0f} {r[6]:>11.0f}")
    print("  ...")
    best = sorted(rows, key=lambda r: -r[5])[:5]
    print("\n  highest median $/yr (ignoring liquidation risk):")
    for r in best:
        print(f"  {r[0]:<20} {r[1]:>8.0%} {r[2]:>10.0%} {r[3]:>12.0%} {r[4]:>10.0%} {r[5]:>+11.0f} {r[6]:>11.0f}")
    np.save("avgdown_grid.npy", np.array([(1 if r[0].startswith("$100") else 0, r[1], r[2], r[3], r[4], r[5], r[6])
                                          for r in rows]))

    print("\n  same plan, but only start new cycles while BTC is above its 200-day average:")
    for unit, step, tp in [(200, 0.10, 0.03), (200, 0.15, 0.05), (100, 0.10, 0.03), (100, 0.15, 0.05)]:
        rs = [run(s, unit=unit, step=step, tp=tp, trend=True) for s in starts]
        per_yr = np.array([(r["final"] - 500) / years_left(s) for r, s in zip(rs, starts)])
        print(f"  ${unit} positions, add every {step:.0%}, TP {tp:.0%}: liquidated {np.mean([r['liq'] for r in rs]):.0%}, "
              f"median ${np.median(per_yr):+.0f}/yr")

    print("\n  BTC's real crashes from a peak: 2018 -84%, 2020 (Covid) -63%, 2022 -77%")

"""Robustness check of the averaging-down grid with ~400 weekly start dates (incl. market tops)."""
import numpy as np
from datetime import datetime, timezone
from avgdown_optimize import run, survivable_drop, t, C, O, N

starts = list(range(np.searchsorted(t, 1514764800), np.searchsorted(t, 1735689600), 24 * 7))  # weekly, 2018-2024
yrs = lambda i: (t[-1] - t[i]) / 31557600
print(f"{len(starts)} weekly start dates (Jan 2018 - Dec 2024), held until Oct 2026 or liquidation\n")
bh = np.array([(500 * C[-1] / O[s] - 500) / yrs(s) for s in starts])
print(f"  benchmark - just buy $500 of BTC, no leverage: median ${np.median(bh):+.0f}/yr, never liquidated\n")
print(f"  {'per entry':<15} {'add every':>9} {'TP':>4} {'survives':>8} {'liquidated':>10} {'median $/yr':>11} {'worst start':>24}")
rows = []
for unit, label in [(200, "$100 margin x2"), (100, "$50 margin x2")]:
    for step in [0.05, 0.10, 0.15, 0.20, 0.25]:
        for tp in [0.02, 0.03, 0.05, 0.10]:
            rs = [run(s, unit=unit, step=step, tp=tp) for s in starts]
            liq = np.array([r["liq"] for r in rs])
            per = np.array([(r["final"] - 500) / yrs(s) for r, s in zip(rs, starts)])
            worst = ""
            if liq.any():
                k = int(np.argmax(liq))
                worst = f"liq. if started {datetime.fromtimestamp(t[starts[k]], timezone.utc):%b %Y}"
            rows.append((label, step, tp, survivable_drop(unit, step, 1000), liq.mean(), np.median(per), worst, unit))
for r in sorted(rows, key=lambda r: (round(r[4], 3), -r[5]))[:14]:
    print(f"  {r[0]:<15} {r[1]:>8.0%} {r[2]:>4.0%} {r[3]:>8.0%} {r[4]:>10.1%} {r[5]:>+11.0f} {r[6]:>24}")
print("  ...")
for r in sorted(rows, key=lambda r: -r[5])[:4]:
    print(f"  {r[0]:<15} {r[1]:>8.0%} {r[2]:>4.0%} {r[3]:>8.0%} {r[4]:>10.1%} {r[5]:>+11.0f} {r[6]:>24}")
np.save("avgdown_weekly.npy", np.array([(r[7], r[1], r[2], r[4], r[5]) for r in rows]))

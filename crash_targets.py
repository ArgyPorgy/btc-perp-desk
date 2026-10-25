"""Which cash-out target gives the best odds over 100 x $5 bets? Real Stake Crash history, blocks of 100.
Run: python3 crash_targets.py
"""
import numpy as np

c = np.load("crash_history.npy").astype(np.int64)
B, BET = 100, 5.0
nb = len(c) // B
cc = c[: nb * B].reshape(nb, B)
rows = []
for tgt in range(110, 1001):
    h = (cc >= tgt).sum(1)
    res = h * BET * (tgt / 100 - 1) - (B - h) * BET
    rows.append((tgt / 100, (c >= tgt).mean(), np.ceil(500 / (BET * tgt / 100) - 1e-9), np.mean(res > 0),
                 res.mean(), np.median(res), np.percentile(res, 5), np.percentile(res, 95), np.mean(res <= -100)))
rows = np.array(rows)
print(f"  {'target':>6} {'per round':>9} {'need hits':>9} {'100 bets ahead':>14} {'avg':>7} {'median':>7} "
      f"{'middle 90%':>16} {'lose $100+':>10}")
pick = [1.1, 1.2, 1.3, 1.5, 1.8, 1.82, 1.9, 2.0, 2.02, 2.5, 3.0, 5.0, 10.0]
for x in pick:
    r = rows[np.argmin(np.abs(rows[:, 0] - x))]
    print(f"  {r[0]:>5.2f}x {r[1]:9.1%} {r[2]:9.0f} {r[3]:14.1%} {r[4]:+7.2f} {r[5]:+7.0f} "
          f"{'$'+format(r[6],'+.0f')+' to $'+format(r[7],'+.0f'):>16} {r[8]:10.1%}")
best = rows[np.argsort(-rows[:, 3])[:8]]
print("\n  targets with the HIGHEST chance of being ahead after 100 bets:")
for r in best:
    print(f"  {r[0]:>5.2f}x  ahead {r[3]:.1%}  need {r[2]:.0f} hits  avg {r[4]:+.2f}  middle 90% ${r[6]:+.0f} to ${r[7]:+.0f}")
print(f"\n  average result per 100 x $5 across ALL targets 1.10x-10x: ${rows[:,4].mean():+.2f} "
      f"(min {rows[:,4].min():+.2f}, max {rows[:,4].max():+.2f})")

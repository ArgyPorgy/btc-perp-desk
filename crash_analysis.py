"""Pattern hunting and strategy backtests on Stake's real Crash history (crash_history.npy).
Run: python3 crash_analysis.py
"""
import numpy as np

c = np.load("crash_history.npy").astype(np.int64)  # x100, oldest first
x = c / 100.0
N = len(x)
rng = np.random.default_rng(3)
print(f"real games: {N:,}   max ever: {x.max():,.2f}x   median: {np.median(x):.2f}x\n")

# ---------------------------------------------------------------- 1. distribution vs theory
print("1. HOW OFTEN DOES IT REACH EACH MULTIPLIER?  (real vs Stake's formula 0.99/x)")
print(f"  {'target':>8} {'real':>9} {'theory':>9} {'payback if you always cash out here':>38}")
for t in [1.01, 1.2, 1.5, 2, 3, 5, 10, 20, 50, 100, 1000]:
    real = np.mean(c >= round(t * 100))
    print(f"  {t:>7}x {real:9.4%} {0.99/t:9.4%} {real*t:38.4f}")
print(f"  instant crash at 1.00x: {np.mean(c == 100):.3%} of rounds\n")

# ---------------------------------------------------------------- 2. pattern tests
win = c >= 200
p0 = win.mean()
print("2. DOES THE PAST PREDICT THE NEXT ROUND?  (chance next round reaches 2x)")
print(f"  unconditional: {p0:.4%}")
run = np.zeros(N, dtype=np.int64)  # consecutive sub-2x rounds ending at i
for i in range(1, N):
    run[i] = run[i - 1] + 1 if not win[i] else 0
prev_run = np.concatenate([[0], run[:-1]])
print(f"  {'after N reds (<2x) in a row':<30} {'P(next >= 2x)':>14} {'samples':>10} {'z-score':>8}")
for k in [0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 15]:
    m = prev_run == k if k < 15 else prev_run >= k
    nk = m.sum()
    pk = win[m].mean()
    z = (pk - p0) / np.sqrt(p0 * (1 - p0) / nk)
    print(f"  {('exactly ' if k < 15 else 'at least ') + str(k):<30} {pk:14.4%} {nk:10,} {z:8.2f}")
prev = np.concatenate([[100], c[:-1]])
for label, m in [("after an instant 1.00x", prev == 100), ("after a 10x+ round", prev >= 1000),
                 ("after a 100x+ round", prev >= 10000), ("after 3 greens (>=2x) in a row",
                 np.concatenate([[False] * 3, win[:-3] & win[1:-2] & win[2:-1]]))]:
    nk = m.sum()
    pk = win[m].mean()
    print(f"  {label:<30} {pk:14.4%} {nk:10,} {(pk-p0)/np.sqrt(p0*(1-p0)/nk):8.2f}")

lx = np.log(x)
lx = (lx - lx.mean()) / lx.std()
ac = [np.mean(lx[:-k] * lx[k:]) for k in range(1, 11)]
print(f"  autocorrelation of log(crash), lags 1-10: {' '.join(f'{a:+.4f}' for a in ac)}")
print(f"  (noise level for {N:,} games: about +/-{2/np.sqrt(N):.4f})")
# Wald-Wolfowitz runs test on win/loss sequence
n1, n2 = win.sum(), N - win.sum()
runs = 1 + np.sum(win[1:] != win[:-1])
mu = 2 * n1 * n2 / N + 1
var = (mu - 1) * (mu - 2) / (N - 1)
print(f"  runs test (are greens/reds clumped?): z = {(runs-mu)/np.sqrt(var):+.2f}  (|z|<2 = no clumping)\n")

# longest streaks
def longest(mask):
    best = cur = 0
    for v in mask:
        cur = cur + 1 if v else 0
        best = max(best, cur)
    return best
print(f"  longest run below 2x: {run.max()} rounds   longest below 1.5x: {longest(c < 150)}   "
      f"longest below 10x: {longest(c < 1000)}\n")

# ---------------------------------------------------------------- 3. strategy backtests on real rounds
print("3. BACKTESTS ON THE REAL 8.6M ROUNDS  ($1 per bet, every result is real)")
def flat(target, mask=None):
    hit = c >= round(target * 100)
    pnl = np.where(hit, target - 1, -1.0)
    if mask is not None:
        pnl = pnl[mask]
    return pnl.sum(), len(pnl)
print(f"  {'strategy':<46} {'bets':>11} {'net per $1 bet':>15}")
for t in [1.01, 1.1, 1.5, 2, 3, 5, 10, 100]:
    s, n = flat(t)
    print(f"  {'always cash out at ' + str(t) + 'x':<46} {n:11,} {s/n:+15.4f}")
for k in [3, 5, 8]:
    s, n = flat(2, prev_run >= k)
    print(f"  {'bet 2x only after ' + str(k) + '+ reds in a row':<46} {n:11,} {s/n:+15.4f}")
s, n = flat(2, prev >= 1000)
print(f"  {'bet 2x only after a 10x+ round':<46} {n:11,} {s/n:+15.4f}")
s, n = flat(10, prev_run >= 10)
print(f"  {'bet 10x only after 10+ reds':<46} {n:11,} {s/n:+15.4f}\n")

# windows: 1000-round sessions at 2x
W = 1000
pnl2 = np.where(c >= 200, 1.0, -1.0)[: (N // W) * W].reshape(-1, W).sum(1) * 5
print(f"  {N//W:,} real 1000-round sessions, $5 flat at 2x: ended ahead {np.mean(pnl2>0):.1%}, "
      f"avg ${pnl2.mean():+.2f}, best ${pnl2.max():+.0f}, worst ${pnl2.min():+.0f}")

# martingale / bankroll strategies from random real starting points
def bankroll_sim(strategy, start=231.0, rounds=500, sessions=3000):
    ends = []
    starts = rng.integers(0, N - rounds - 20, sessions)
    for s0 in starts:
        bank, bet, streak = start, 5.0, 0
        for i in range(s0, s0 + rounds):
            b, t = strategy(bank, bet, streak, i)
            if b <= 0:
                continue
            b = min(b, bank)
            if c[i] >= round(t * 100):
                bank += b * (t - 1); streak = 0
            else:
                bank -= b; streak += 1
            bet = b
            if bank < 0.01:
                break
        ends.append(bank)
    e = np.array(ends)
    return np.mean(e > start), np.mean(e < 1), e.mean() - start

strats = {
    "flat $5 at 2x": lambda bank, bet, st, i: (5, 2.0),
    "flat $5 at 1.5x": lambda bank, bet, st, i: (5, 1.5),
    "flat $1 at 10x": lambda bank, bet, st, i: (1, 10.0),
    "martingale $5 at 2x (double after loss)": lambda bank, bet, st, i: (5 * 2 ** st, 2.0),
    "wait for 5 reds, then $5 at 2x": lambda bank, bet, st, i: (5 if prev_run[i] >= 5 else 0, 2.0),
    "wait for 5 reds, then martingale at 2x": lambda bank, bet, st, i: (5 * 2 ** st if prev_run[i] >= 5 else 0, 2.0),
}
print(f"\n  start $231, 500 real rounds, 3,000 random real windows:")
print(f"  {'strategy':<46} {'ahead':>7} {'busted':>7} {'avg result':>11}")
for name, f in strats.items():
    a, b, m = bankroll_sim(f)
    print(f"  {name:<46} {a:7.1%} {b:7.1%} {m:+11.2f}")

np.save("crash_cond.npy", np.array([[k, win[prev_run == k].mean(), (prev_run == k).sum()] for k in range(13)]))

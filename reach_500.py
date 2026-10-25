"""Chance of turning $200 into $500 on Stake Crash, then stopping. Exact math + real-history backtest.
Run: python3 reach_500.py
"""
import numpy as np

c = np.load("crash_history.npy").astype(np.int64)
N = len(c)
rng = np.random.default_rng(500)
START, GOAL = 200.0, 500.0


def exact(bet, target, max_bets=None):
    """Probability of reaching GOAL before going broke (bankroll tracked in cents, P(win)=0.99/target)."""
    p = 0.99 / target
    probs = {round(START * 100): 1.0}
    reached = busted = 0.0
    step = 0
    while probs and (max_bets is None or step < max_bets):
        nxt = {}
        for b, pr in probs.items():
            stake = min(bet * 100, b)
            for nb, q in ((b + round(stake * (target - 1)), p), (b - stake, 1 - p)):
                if nb >= GOAL * 100:
                    reached += pr * q
                elif nb < 1:
                    busted += pr * q
                else:
                    nxt[nb] = nxt.get(nb, 0) + pr * q
        probs = {k: v for k, v in nxt.items() if v > 1e-13}
        step += 1
    still = sum(probs.values())
    return reached, busted, still


def backtest(bet, target, max_bets=None, n=20_000):
    T = round(target * 100)
    res = []
    for s0 in rng.integers(0, N - 5000, n):
        bank, i, k = START, s0, 0
        while bank >= 0.01 and bank < GOAL and (max_bets is None or k < max_bets):
            b = min(bet, bank)
            bank += b * (target - 1) if c[i] >= T else -b
            i += 1
            k += 1
        res.append(bank)
    r = np.array(res)
    return np.mean(r >= GOAL), np.mean(r < 0.01), r.mean() - START


print(f"Goal: ${START:.0f} -> ${GOAL:.0f}, then stop.  Ceiling for ANY strategy: under {START/GOAL:.0%}\n")
print(f"  {'plan':<42} {'reach $500':>10} {'lose it all':>11} {'still going':>11} {'real-history check':>19}")
plans = [
    ("$50 bets at 1.2x, until $500 or broke", 50, 1.2, None),
    ("$50 bets at 1.2x, max 50 bets", 50, 1.2, 50),
    ("$20 bets at 1.2x, until $500 or broke", 20, 1.2, None),
    ("$50 bets at 2x, until $500 or broke", 50, 2.0, None),
    ("$100 bets at 2.5x, until $500 or broke", 100, 2.5, None),
    ("one $200 bet at 2.5x", 200, 2.5, 1),
]
for name, bet, tgt, mx in plans:
    r, b, s = exact(bet, tgt, mx)
    rr, _, _ = backtest(bet, tgt, mx)
    print(f"  {name:<42} {r:10.1%} {b:11.1%} {s:11.1%} {rr:19.1%}")

# how the $50 @ 1.2x plan typically goes
p = 0.99 / 1.2
print(f"\n$50 at 1.2x: each win +$10, each loss -$50. Need +$300 = 30 more wins than 5x losses.")
print(f"  chance of 30 wins in a row with no loss: {p**30:.2%}")
print(f"  4 losses (net of wins) and you're broke; {200//50} losses = $200")

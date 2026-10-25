"""Backtest cashing out at 1.2x on Stake's real Crash history, and size a SHA-256 brute force.
Run: python3 crash_12x.py
"""
import hashlib
import os
import time

import numpy as np

c = np.load("crash_history.npy").astype(np.int64)
N = len(c)
rng = np.random.default_rng(12)
T = 120  # 1.2x in cents

hit = c >= T
print(f"real rounds: {N:,}   reached 1.2x: {hit.mean():.3%}   payback per $1: {hit.mean()*1.2:.4f}")
loss_run = 0
longest = 0
for h in hit:
    loss_run = 0 if h else loss_run + 1
    longest = max(longest, loss_run)
print(f"longest real streak of crashes below 1.2x: {longest}")
print(f"one loss wipes out {1/0.2:.0f} wins; you need to win > {1/1.2:.2%} of rounds to break even\n")


def session(start, bet_fn, rounds, n=5000):
    ends, peaks_lost = [], []
    for s0 in rng.integers(0, N - rounds, n):
        bank, bet, streak = start, None, 0
        for i in range(s0, s0 + rounds):
            b = min(bet_fn(streak), bank)
            if b <= 0:
                break
            if c[i] >= T:
                bank += b * 0.2
                streak = 0
            else:
                bank -= b
                streak += 1
            if bank < 0.01:
                break
        ends.append(bank)
    e = np.array(ends)
    return np.mean(e > start), np.mean(e < 1), np.median(e) - start, e.mean() - start


print("start $231, random windows of the REAL history, 5,000 sessions each")
print(f"  {'strategy':<44} {'rounds':>6} {'ahead':>6} {'busted':>7} {'median':>8} {'average':>8}")
for name, fn in [
    ("flat $5 at 1.2x", lambda s: 5),
    ("flat $20 at 1.2x", lambda s: 20),
    ("flat $50 at 1.2x", lambda s: 50),
    ("$5 at 1.2x, after a loss bet 6x to win it back", lambda s: 5 * 6 ** s),
]:
    for rounds in (100, 500, 2000):
        a, b, med, avg = session(231.0, fn, rounds)
        print(f"  {name:<44} {rounds:>6} {a:6.1%} {b:7.1%} {med:+8.2f} {avg:+8.2f}")

# ---- brute force sizing
buf = os.urandom(32).hex().encode()
t0 = time.perf_counter()
k = 2_000_000
for _ in range(k):
    buf = hashlib.sha256(buf).hexdigest().encode()
rate = k / (time.perf_counter() - t0)
space = 2**256
btc_rate = 1e21  # Bitcoin network, order of magnitude (~1 zettahash/s)
year = 3.156e7
print(f"\nthis Mac: {rate/1e6:.1f} million SHA-256 per second")
print(f"guesses needed to find the next game's hash (64 hex chars): ~2^256 = {space:.2e}")
print(f"  this Mac:                         {space/rate/year:.1e} years")
print(f"  entire Bitcoin network (~10^21/s): {space/btc_rate/year:.1e} years")
print(f"  age of the universe:              1.4e+10 years")

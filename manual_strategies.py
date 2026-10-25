"""Simulate the user's manual Random-Pick strategy plus strategies found online and invented ones.

Part A: per-click math (is going deeper ever worse/better?)
Part B: user's strategy on REAL Stake-algorithm boards with Random Pick (HMAC, not just probabilities)
Part C: 16 strategies x 20,000 players, short and long sessions
Payouts are exactly 99% of fair odds (slightly generous vs Stake's 2-dp display).
Run: python3 manual_strategies.py
"""
import secrets
from math import comb

import numpy as np

from verifier import mine_positions

rng = np.random.default_rng(11)


def p_win(m, g):
    return comb(25 - m, g) / comb(25, g)


def mult(m, g):
    return 0.99 / p_win(m, g)


def mult_shown(m, g):
    return np.floor(mult(m, g) * 100) / 100


# ---------------------------------------------------------------- A. per-click math
print("A. EVERY EXTRA CLICK, 4 MINES  (does going deeper cost you more?)")
print("  from->to  P(next safe)  payout jump  value of clicking again")
for g in range(1, 10):
    p_next = (21 - g) / (25 - g)
    jump = mult_shown(4, g + 1) / mult_shown(4, g)
    print(f"   {g}->{g+1}     {p_next:6.2%}       x{jump:.4f}       {p_next*jump:.4f}  (1.0000 = break-even)")
print("  -> the 1% is charged once, when you start the round. Each extra click after that is ~break-even;")
print("     it only changes how big the swing is, never the average.\n")

# ---------------------------------------------------------------- B. real boards + Random Pick
print("B. YOUR STRATEGY ON REAL STAKE BOARDS (HMAC seeds, Random Pick = uniform over unopened tiles)")
server, client = secrets.token_hex(32), "manualtest"
PLAYERS, ROUNDS = 1000, 300
nonce = 0
ends = []
for pl in range(PLAYERS):
    bank, streak = 30.0, 0
    threshold = rng.integers(2, 4)
    for r in range(ROUNDS):
        if bank < 5 or bank >= 200:
            break
        target = rng.choice([5, 6]) if streak >= threshold else rng.choice([4, 5])
        mines = set(mine_positions(server, client, nonce, 4))
        nonce += 1
        unopened = list(range(25))
        safe = True
        for _ in range(target):
            t = unopened.pop(rng.integers(len(unopened)))  # Random Pick
            if t in mines:
                safe = False
                break
        if safe:
            bank += 5 * (mult(4, target) - 1)
            streak = 0
        else:
            bank -= 5
            streak += 1
    ends.append(bank)
ends = np.array(ends)
print(f"  {PLAYERS} players, start $30, $5 bets, up to {ROUNDS} rounds, stop at $200 or < $5")
print(f"  reached $200: {np.mean(ends >= 200):.1%}   busted: {np.mean(ends < 5):.1%}   avg end ${ends.mean():.2f}\n")


# ---------------------------------------------------------------- C. strategy tournament
def simulate(strategy, start, base, rounds, n=20_000, goal=None):
    bank = np.full(n, float(start))
    bet = np.full(n, float(base))
    lstreak = np.zeros(n, int)
    wstreak = np.zeros(n, int)
    active = np.ones(n, bool)
    wagered = np.zeros(n)
    thr = rng.integers(2, 4, n)
    snaps = {}
    for r in range(1, rounds + 1):
        gems, bet = strategy(bet, lstreak, wstreak, thr, base, n)
        b = np.minimum(bet, bank) * active
        p = np.array([0.0] + [p_win(4, g) for g in range(1, 22)])[gems]
        mx = np.array([0.0] + [mult(4, g) for g in range(1, 22)])[gems]
        win = rng.random(n) < p
        bank += np.where(win, b * (mx - 1), -b)
        wagered += b
        lstreak = np.where(active, np.where(win, 0, lstreak + 1), lstreak)
        wstreak = np.where(active, np.where(win, wstreak + 1, 0), wstreak)
        active &= bank >= 0.5
        if goal:
            active &= bank < goal
        if r in (10, 25, 50, 100, 300):
            snaps[r] = bank.copy()
    snaps["final"] = bank.copy()
    return snaps, wagered


def pick(n, opts):
    return rng.choice(opts, n)


S = {}
S["YOU: Random Pick, 4-5 gems, go 5-6 after 2-3 losses, flat"] = lambda bet, l, w, thr, base, n: (
    np.where(l >= thr, pick(n, [5, 6]), pick(n, [4, 5])), np.full(n, base))
S["always 4 gems, flat"] = lambda bet, l, w, thr, base, n: (np.full(n, 4), np.full(n, base))
S["always 5 gems, flat"] = lambda bet, l, w, thr, base, n: (np.full(n, 5), np.full(n, base))
S["always 2 gems, flat (low risk)"] = lambda bet, l, w, thr, base, n: (np.full(n, 2), np.full(n, base))
S["always 8 gems, flat (high risk)"] = lambda bet, l, w, thr, base, n: (np.full(n, 8), np.full(n, base))
S["chase deeper: 4 + losing streak gems"] = lambda bet, l, w, thr, base, n: (np.minimum(4 + l, 12), np.full(n, base))
S["recover: pick gems so one win repays streak"] = lambda bet, l, w, thr, base, n: (
    np.array([next(g for g in range(1, 22) if mult(4, g) - 1 >= k + 1 or g == 21) for k in range(60)])[np.minimum(l, 59)],
    np.full(n, base))
S["opposite: go shallower (2 gems) after losses"] = lambda bet, l, w, thr, base, n: (np.where(l >= 2, 2, 4), np.full(n, base))
S["hot hand: go deeper after wins"] = lambda bet, l, w, thr, base, n: (np.minimum(4 + w, 10), np.full(n, base))
S["pure gut: 3-7 gems at random each round"] = lambda bet, l, w, thr, base, n: (pick(n, [3, 4, 5, 6, 7]), np.full(n, base))
S["martingale: double bet after loss, 4 gems"] = lambda bet, l, w, thr, base, n: (
    np.full(n, 4), np.where(l > 0, base * 2.0 ** np.minimum(l, 30), base))
S["reverse martingale (Sportsgrid): double after win, reset at 3 wins"] = lambda bet, l, w, thr, base, n: (
    np.full(n, 4), base * 2.0 ** (w % 3))


def dalembert():
    state = {}

    def f(bet, l, w, thr, base, n):
        lost_last = l > 0
        new = np.where(lost_last, bet + 1, np.maximum(bet - 1, base))
        new = np.where(state.get("first", True), base, new)
        state["first"] = False
        return np.full(n, 4), new
    return f


S["d'Alembert: +$1 after loss, -$1 after win"] = dalembert()

print("C. STRATEGY TOURNAMENT  (20,000 players each, 4 mines)")
for title, start, base in [("Start $25, base bet $2", 25, 2), ("Start $30, base bet $5 (your real setup)", 30, 5)]:
    print(f"\n  {title}")
    print(f"  {'strategy':<62} {'ahead@25':>8} {'ahead@100':>9} {'bust@100':>8} {'avg@100':>8} {'avg/$ bet':>9}")
    for name, fn in S.items():
        if name.startswith("d'Alembert"):
            fn = dalembert()
        snaps, wag = simulate(fn, start, base, 100)
        a25, a100 = snaps[25], snaps[100]
        print(f"  {name:<62} {np.mean(a25 > start):8.1%} {np.mean(a100 > start):9.1%} {np.mean(a100 < 0.5):8.1%} "
              f"{a100.mean()-start:+8.2f} {(a100.mean()-start)/wag.mean():+9.4f}")

print("\n  P(reaching $200 from $30 with $5 bets, no round limit)")
for name, fn in S.items():
    if name.startswith("d'Alembert"):
        fn = dalembert()
    snaps, wag = simulate(fn, 30, 5, 3000, n=10_000, goal=200)
    print(f"  {name:<62} {np.mean(snaps["final"] >= 200):6.1%}   busted {np.mean(snaps["final"] < 0.5):6.1%}")

"""Does splitting play into short sessions help?  Start $30, $5 bets, 4 mines / 4 gems, 20,000 players.
Run: python3 sessions.py
"""
from math import comb

import numpy as np

rng = np.random.default_rng(5)
N, START, BET = 20_000, 30.0, 5.0
P = comb(21, 4) / comb(25, 4)
X = 0.99 / P


def play(n_sessions, per_session, stop_win=None, stop_loss=None):
    bank = np.full(N, START)
    rounds = np.zeros(N)
    sess_ahead = []
    for _ in range(n_sessions):
        sess_start = bank.copy()
        live = bank >= BET
        for _ in range(per_session):
            b = np.where(live, BET, 0.0)
            win = rng.random(N) < P
            bank += np.where(win, b * (X - 1), -b)
            rounds += live
            live &= bank >= BET
            if stop_win is not None:
                live &= bank - sess_start < stop_win
            if stop_loss is not None:
                live &= sess_start - bank < stop_loss
        played = sess_start >= BET
        sess_ahead.append(np.mean((bank > sess_start)[played]) if played.any() else np.nan)
    return bank, rounds, np.nanmean(sess_ahead)


print(f"{'how you play':<52} {'ahead':>6} {'busted':>7} {'avg $':>7} {'rounds':>7} {'sessions won':>12}")
for label, args in [
    ("1 long session, 500 rounds", (1, 500)),
    ("10 sessions x 50 rounds (money carries over)", (10, 50)),
    ("50 sessions x 10 rounds", (50, 10)),
    ("10 x 50, each session stops at +$15 or -$15", (10, 50, 15, 15)),
    ("10 x 50, each session stops at +$10", (10, 50, 10, None)),
    ("just ONE session of 50, then stop for good", (1, 50)),
]:
    bank, rounds, sw = play(*args)
    print(f"{label:<52} {np.mean(bank > START):6.1%} {np.mean(bank < BET):7.1%} {bank.mean()-START:+7.2f} "
          f"{rounds.mean():7.0f} {sw:12.1%}")

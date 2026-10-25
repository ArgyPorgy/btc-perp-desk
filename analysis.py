"""Stake Mines: payout math, RNG audit, and bankroll simulations.

Run: python3 analysis.py   (prints all tables, writes mines_analysis.png)
"""
import os
import secrets
from math import comb

import numpy as np

from verifier import mine_positions

rng = np.random.default_rng(2026)
N_PLAYERS = 10_000


def p_win(m, g):
    return comb(25 - m, g) / comb(25, g)


def mult(m, g):
    # 99% of fair odds, floored to 2 decimals (matches 2.58x for 4 mines / 5 gems in the screenshot)
    return np.floor(0.99 / p_win(m, g) * 100) / 100


# ---------------------------------------------------------------- 1. payout table
print("=" * 70)
print("1. RETURN-TO-PLAYER FOR EVERY MINES / GEMS COMBO (after 2-dp floor)")
rtps = {}
for m in range(1, 25):
    for g in range(1, 26 - m):
        rtps[(m, g)] = p_win(m, g) * mult(m, g)
vals = np.array(list(rtps.values()))
best = max(rtps, key=rtps.get)
print(f"combos: {len(vals)}   best RTP: {vals.max():.5f} at {best}   worst: {vals.min():.5f}")
print(f"combos with RTP >= 1: {(vals >= 1).sum()}")
print("\n4 mines:")
print(" gems  P(win)   payout   RTP")
for g in range(1, 9):
    print(f"  {g:>2}  {p_win(4, g):6.2%}  {mult(4, g):7.2f}x  {rtps[(4, g)]:.4f}")

# ---------------------------------------------------------------- 2. RNG audit
print("\n" + "=" * 70)
print("2. RNG AUDIT ON REAL STAKE-ALGORITHM BOARDS (4 mines)")
N_BOARDS = 200_000
server = secrets.token_hex(32)
client = "quantaudit"
boards = np.zeros((N_BOARDS, 25), dtype=bool)
for n in range(N_BOARDS):
    boards[n, mine_positions(server, client, n, 4)] = True

freq = boards.sum(0)
exp = N_BOARDS * 4 / 25
chi2 = ((freq - exp) ** 2 / exp).sum()
print(f"boards: {N_BOARDS:,}  per-tile mine rate min/max: {freq.min()/N_BOARDS:.4f}/{freq.max()/N_BOARDS:.4f}  (fair 0.1600)")
print(f"chi-square over 25 tiles: {chi2:.1f}  (df=24, 95% cutoff 36.4)")

overlap = (boards[1:] & boards[:-1]).sum(1).mean()
print(f"avg mines shared with previous board: {overlap:.4f}  (independent = {4*4/25:.4f})")

# Tile-picking "strategies": 4 picks per board, did all 4 survive?
picks = {
    "corners": [0, 4, 20, 24],
    "center block": [6, 8, 16, 18],
    "top row left": [0, 1, 2, 3],
}
survive = lambda tiles: (~boards[:, tiles].any(1)).mean()
print(f"P(4 safe picks) theory: {p_win(4, 4):.4f}")
for name, t in picks.items():
    print(f"  {name:<28} {survive(t):.4f}")
# Adaptive: avoid / repeat last board's mines
prev = boards[:-1]
cur = boards[1:]
idx = np.arange(25)
avoid_hit = repeat_hit = 0
for i in range(len(cur)):
    safe_prev = idx[~prev[i]]
    mine_prev = idx[prev[i]]
    avoid_hit += not cur[i, safe_prev[:4]].any()
    repeat_hit += not cur[i, mine_prev].any()
print(f"  {'avoid last round mines':<28} {avoid_hit/len(cur):.4f}")
print(f"  {'click last round mines':<28} {repeat_hit/len(cur):.4f}")


# ---------------------------------------------------------------- 3. simulator
def simulate(start, m, g, bet_fn, rounds, stop_hi=None, stop_lo=0.0, n=N_PLAYERS):
    """Vectorised. bet_fn(bankroll, last_bet, last_won) -> bet array. Returns (paths, total_wagered)."""
    p, x = p_win(m, g), mult(m, g)
    bank = np.full(n, float(start))
    last_bet = np.zeros(n)
    last_won = np.ones(n, dtype=bool)
    active = np.ones(n, dtype=bool)
    wagered = np.zeros(n)
    path = np.empty((rounds + 1, n))
    path[0] = bank
    for r in range(rounds):
        bet = np.minimum(bet_fn(bank, last_bet, last_won), bank)
        bet[~active] = 0
        win = rng.random(n) < p
        bank += np.where(win, bet * (x - 1), -bet)
        wagered += bet
        last_bet, last_won = np.where(active, bet, last_bet), np.where(active, win, last_won)
        active &= bank >= 0.01
        active &= bank > stop_lo
        if stop_hi is not None:
            active &= bank < stop_hi
        path[r + 1] = bank
    return path, wagered


flat = lambda b: (lambda bank, lb, lw: np.full_like(bank, b))


def martingale(base):
    return lambda bank, lb, lw: np.where(lw | (lb == 0), base, lb * 2)


def summarize(label, path, wagered, start):
    end = path[-1]
    print(f"  {label:<34} profit {np.mean(end > start):5.1%}  bust {np.mean(end < 1):5.1%}  "
          f"median ${np.median(end):7.2f}  mean ${end.mean():7.2f}  wagered ${wagered.mean():8.0f}")


# ---- 3a. the user's actual run: $25 -> $200 ($1 bets until $30, then $5 bets)
print("\n" + "=" * 70)
print("3a. HOW LIKELY WAS $25 -> $200?  ($1 bets below $30, $5 bets above)")
user_bet = lambda bank, lb, lw: np.where(bank >= 30, 5.0, 1.0)
for m, g in [(4, 5), (4, 4)]:
    path, wag = simulate(25, m, g, user_bet, 20_000, stop_hi=200)
    end = path[-1]
    reached = end >= 200
    print(f"  {m} mines/{g} gems: reached $200 {reached.mean():5.1%}   busted {np.mean(end < 1):5.1%}   "
          f"avg wagered by those who made it ${wag[reached].mean():,.0f}")

# ---- 3b. forward from $208
print("\n" + "=" * 70)
print("3b. FROM $208, 10,000 PLAYERS")
START = 208
results = {}
for m, g in [(4, 4), (4, 5)]:
    print(f"\n {m} mines / {g} gems  (P(win) {p_win(m, g):.1%}, pays {mult(m, g)}x)")
    for rounds in (100, 500, 1000):
        for name, fn in [("flat $1", flat(1)), ("flat $5", flat(5)), ("flat $20", flat(20)),
                         ("double after loss from $5", martingale(5))]:
            path, wag = simulate(START, m, g, fn, rounds)
            summarize(f"{name}, {rounds} rounds", path, wag, START)
            results[(m, g, name, rounds)] = path

# ---- 3c. stop rules
print("\n" + "=" * 70)
print("3c. STOP RULES  (4 mines / 4 gems, flat $5, up to 5000 rounds)")
for hi, lo in [(312, 104), (416, 0), (260, 156), (1000, 0)]:
    path, wag = simulate(START, 4, 4, flat(5), 5000, stop_hi=hi, stop_lo=lo)
    end = path[-1]
    print(f"  stop at +${hi-START} / -${START-lo}:  hit target {np.mean(end >= hi):5.1%}  "
          f"avg wagered ${wag.mean():,.0f}  avg result ${end.mean()-START:+.2f}")

# ---- 3d. goal probability vs bet size (bold vs timid play)
print("\n" + "=" * 70)
print("3d. P(TURN $208 INTO $416 BEFORE GOING BROKE) BY BET SIZE  (4 mines / 4 gems)")
goal_rows = []
for b in (1, 5, 10, 20, 50, 104, 208):
    path, wag = simulate(START, 4, 4, flat(b), 200_000 // b + 200, stop_hi=416, n=4000)
    pr = np.mean(path[-1] >= 416)
    goal_rows.append((b, pr, wag.mean()))
    print(f"  ${b:>3} bets: {pr:5.1%}   avg wagered ${wag.mean():>8,.0f}   expected loss ${wag.mean()*(1-rtps[(4,4)]):6.2f}")

# ---- 3e. expected loss is a function of volume only
print("\n" + "=" * 70)
print("3e. RAKEBACK CHECK: Stake rakeback ~5% of house edge (third-party sources) on 1% edge")
eff = 1 - rtps[(4, 4)] - 0.05 * 0.01
print(f"  4m/4g edge after flooring: {1-rtps[(4,4)]:.4%}   after rakeback: {eff:.4%}  -> still negative")

np.save("goal_rows.npy", np.array(goal_rows))

# ---------------------------------------------------------------- 4. chart
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e6e5df"
plt.rcParams.update({"font.size": 10, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.spines.top": False,
                     "axes.spines.right": False})
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

ax = axes[0]
path = results[(4, 4, "flat $5", 1000)]
for i in range(60):
    ax.plot(path[:, i], color=BLUE, alpha=0.18, lw=0.8)
for q, ls in [(50, "-"), (10, "--"), (90, "--")]:
    ax.plot(np.percentile(path, q, axis=1), color=INK, lw=2, ls=ls)
ax.axhline(START, color=MUTED, lw=1, ls=":")
ax.set_title("Flat $5, 4 mines / 4 gems: 10th, 50th, 90th percentile", color=INK, loc="left")
ax.set_xlabel("round"); ax.set_ylabel("bankroll ($)"); ax.grid(axis="y", color=GRID)

ax = axes[1]
for name, col in [("flat $1", AQUA), ("flat $5", BLUE), ("flat $20", ORANGE)]:
    end = results[(4, 4, name, 1000)][-1]
    ax.hist(end, bins=np.linspace(0, 900, 61), histtype="step", lw=2, color=col, label=name)
ax.axvline(START, color=MUTED, lw=1, ls=":")
ax.set_title("Bankroll after 1,000 rounds", color=INK, loc="left")
ax.set_xlabel("ending bankroll ($)"); ax.set_ylabel("players (of 10,000)"); ax.legend(frameon=False)
ax.grid(axis="y", color=GRID)

ax = axes[2]
bs = [r[0] for r in goal_rows]
ax.plot(range(len(bs)), [r[1] * 100 for r in goal_rows], color=BLUE, lw=2, marker="o", ms=8)
ax.axhline(50, color=MUTED, lw=1, ls=":")
ax.set_xticks(range(len(bs)), [f"${b}" for b in bs])
ax.set_ylim(0, 55)
ax.set_title("Chance of doubling $208 before going broke", color=INK, loc="left")
ax.set_xlabel("bet size"); ax.set_ylabel("%"); ax.grid(axis="y", color=GRID)

fig.tight_layout()
fig.savefig("mines_analysis.png", dpi=130)
print("\nwrote mines_analysis.png")

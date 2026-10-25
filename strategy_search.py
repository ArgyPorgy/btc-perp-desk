"""Grid search over Stake auto-bet settings, starting $25, base bet $2, 4 mines.

Settings searched (all combos):
  gems before cash-out: 1,2,3,4,5,6,8
  on win:  reset, or increase bet by 25/50/100%
  on loss: reset, or increase bet by 25/50/100%
  stop when profit reaches: +$10, +$25, +$50, +$100, or never (play the full 500 rounds)
Payouts use exactly 99% of fair odds (no 2-dp rounding), i.e. slightly generous to the player.
Run: python3 strategy_search.py
"""
import itertools
import secrets
from math import comb

import numpy as np

from verifier import mine_positions

START, BASE, MINES, MAX_ROUNDS, N = 25.0, 2.0, 4, 500, 5000
rng = np.random.default_rng(7)

# ---------------------------------------------------------------- Random Pick check
server, client = secrets.token_hex(32), "randompick"
hits_rand = hits_fixed = 0
NB = 50_000
for n in range(NB):
    mines = set(mine_positions(server, client, n, MINES))
    rand4 = rng.choice(25, 4, replace=False)
    hits_rand += not any(t in mines for t in rand4)
    hits_fixed += not any(t in mines for t in (0, 1, 2, 3))
p44 = comb(21, 4) / comb(25, 4)
print(f"P(4 safe) theory {p44:.4f} | Random Pick {hits_rand/NB:.4f} | fixed top-row tiles {hits_fixed/NB:.4f}\n")

# ---------------------------------------------------------------- strategy grid
gems_opts = [1, 2, 3, 4, 5, 6, 8]
win_opts = [0, 0.25, 0.5, 1.0]
loss_opts = [0, 0.25, 0.5, 1.0]
target_opts = [10, 25, 50, 100, None]
grid = list(itertools.product(gems_opts, win_opts, loss_opts, target_opts))
S = len(grid)

g = np.array([s[0] for s in grid])[:, None]
p = np.array([comb(25 - MINES, k) / comb(25, k) for k in g[:, 0]])[:, None]
mult = 0.99 / p
inc_w = np.array([s[1] for s in grid])[:, None]
inc_l = np.array([s[2] for s in grid])[:, None]
target = np.array([START + (s[3] if s[3] is not None else 1e12) for s in grid])[:, None]

bank = np.full((S, N), START)
bet = np.full((S, N), BASE)
active = np.ones((S, N), dtype=bool)
wagered = np.zeros((S, N))
rounds = np.zeros((S, N))

for r in range(MAX_ROUNDS):
    b = np.minimum(bet, bank) * active
    win = rng.random((S, N)) < p
    bank += np.where(win, b * (mult - 1), -b)
    wagered += b
    rounds += active
    nxt_w = np.where(inc_w > 0, bet * (1 + inc_w), BASE)
    nxt_l = np.where(inc_l > 0, bet * (1 + inc_l), BASE)
    bet = np.where(active, np.where(win, nxt_w, nxt_l), bet)
    active &= (bank >= 0.10) & (bank < target)

res = bank - START
rows = []
for i, (gm, w, l, t) in enumerate(grid):
    rows.append(dict(
        gems=gm, on_win=w, on_loss=l, target=t,
        hit=np.mean(bank[i] >= target[i, 0]) if t else np.nan,
        ahead=np.mean(res[i] > 0), bust=np.mean(bank[i] < 0.10),
        avg=res[i].mean(), med=np.median(res[i]), wag=wagered[i].mean(),
    ))


def fmt(x):
    return "reset" if x == 0 else f"+{int(x*100)}%"


def show(title, rs):
    print(title)
    print(f"  {'gems':>4} {'on win':>7} {'on loss':>7} {'stop at':>8} | {'ahead':>6} {'bust':>6} {'avg result':>10} {'wagered':>8}")
    for r in rs:
        t = f"+${r['target']}" if r["target"] else "500 rds"
        print(f"  {r['gems']:>4} {fmt(r['on_win']):>7} {fmt(r['on_loss']):>7} {t:>8} | {r['ahead']:6.1%} {r['bust']:6.1%} "
              f"{r['avg']:>+10.2f} {r['wag']:>8.0f}")
    print()


print(f"strategies tested: {S}   players each: {N:,}   max rounds: {MAX_ROUNDS}")
pos = [r for r in rows if r["avg"] > 0]
print(f"strategies with positive average result: {len(pos)}")
avgs = np.array([r["avg"] for r in rows])
wags = np.array([r["wag"] for r in rows])
slope = np.polyfit(wags, avgs, 1)[0]
print(f"avg result vs amount wagered: slope {slope:+.4f} per $1 wagered (house edge = -0.0100)")
print(f"best avg result: {avgs.max():+.2f}  worst: {avgs.min():+.2f}\n")

show("TOP 10 BY CHANCE OF ENDING AHEAD", sorted(rows, key=lambda r: -r["ahead"])[:10])
show("TOP 10 BY AVERAGE RESULT (least-bad)", sorted(rows, key=lambda r: -r["avg"])[:10])
for t in (10, 25, 50, 100):
    show(f"BEST WAY TO HIT +${t} (by chance of hitting it)",
         sorted([r for r in rows if r["target"] == t], key=lambda r: -r["hit"])[:3])

show("YOUR QUESTION: flat $2 vs raising after a loss vs raising after a win (4 gems, stop at +$25)",
     [r for r in rows if r["gems"] == 4 and r["target"] == 25 and (r["on_win"] == 0 or r["on_loss"] == 0)])


# ---------------------------------------------------------------- re-test the "winners" with 40x more players
def run(strats, n, seed):
    r_ = np.random.default_rng(seed)
    S_ = len(strats)
    p_ = np.array([comb(25 - MINES, s["gems"]) / comb(25, s["gems"]) for s in strats])[:, None]
    m_ = 0.99 / p_
    iw = np.array([s["on_win"] for s in strats])[:, None]
    il = np.array([s["on_loss"] for s in strats])[:, None]
    tg = np.array([START + (s["target"] or 1e12) for s in strats])[:, None]
    bk, bt = np.full((S_, n), START), np.full((S_, n), BASE)
    ac, wg = np.ones((S_, n), dtype=bool), np.zeros((S_, n))
    for _ in range(MAX_ROUNDS):
        b = np.minimum(bt, bk) * ac
        w = r_.random((S_, n)) < p_
        bk += np.where(w, b * (m_ - 1), -b)
        wg += b
        bt = np.where(ac, np.where(w, np.where(iw > 0, bt * (1 + iw), BASE), np.where(il > 0, bt * (1 + il), BASE)), bt)
        ac &= (bk >= 0.10) & (bk < tg)
    return bk - START, wg


winners = sorted([r for r in rows if r["avg"] > 0], key=lambda r: -r["avg"])
print(f"RE-TEST: all {len(winners)} 'positive' strategies, 200,000 fresh players each")
print(f"  {'gems':>4} {'on win':>7} {'on loss':>7} {'stop at':>8} | {'first run':>9} {'re-test':>8} {'theory (-1% x wagered)':>23}")
still_pos = 0
for chunk in range(0, len(winners), 8):
    batch = winners[chunk:chunk + 8]
    res2, wg2 = run(batch, 200_000, 99 + chunk)
    for s, rr, ww in zip(batch, res2, wg2):
        still_pos += rr.mean() > 0
        t = f"+${s['target']}" if s["target"] else "500 rds"
        print(f"  {s['gems']:>4} {fmt(s['on_win']):>7} {fmt(s['on_loss']):>7} {t:>8} | {s['avg']:>+9.2f} {rr.mean():>+8.2f} {-0.01*ww.mean():>+23.2f}")
print(f"still positive after re-test: {still_pos} of {len(winners)}")

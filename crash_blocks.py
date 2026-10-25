"""Stake Crash, cash out at 1.8x: real history (Jul 2019 - Oct 2026) split into blocks of 100 rounds.
Run: python3 crash_blocks.py   (writes crash_blocks_1.8x.csv and crash_blocks.png)
"""
from math import comb

import numpy as np

c = np.load("crash_history.npy").astype(np.int64)  # x100, oldest first
TARGET, B = 180, 100
hit = c >= TARGET
nb = len(c) // B
blocks = hit[: nb * B].reshape(nb, B).sum(1)
p = hit.mean()

print(f"real rounds: {len(c):,}   median crash: {np.median(c)/100:.2f}x   mean of the cap-free formula: (heavy tail)")
print(f"reached 1.8x: {p:.3%}  (formula 0.99/1.8 = {0.99/1.8:.3%})")
print(f"\nblocks of 100: {nb:,}")
print(f"  hits per 100 -> average {blocks.mean():.2f}, median {np.median(blocks):.0f}, "
      f"typical range (middle 90%) {np.percentile(blocks,5):.0f}-{np.percentile(blocks,95):.0f}, "
      f"worst {blocks.min()}, best {blocks.max()}")
# profit for $1 flat bets at 1.8x: hits*0.8 - misses
profit = blocks * 0.8 - (B - blocks)
print(f"  break-even needs 56+ hits out of 100 (56 x 0.8 = 44.8 > 44 losses)")
print(f"  blocks that ended in profit: {np.mean(profit > 0):.1%}   lost: {np.mean(profit < 0):.1%}   exactly even: {np.mean(profit == 0):.1%}")
print(f"  average result per block of 100 x $1 bets: ${profit.mean():+.3f}   (theory: -$1.00)")

print("\n  hits   real blocks   % of blocks   pure-chance %   $1 bets result")
binom = lambda k: comb(B, k) * p**k * (1 - p) ** (B - k)
for k in range(blocks.min(), blocks.max() + 1):
    n = (blocks == k).sum()
    if n:
        print(f"  {k:>4}   {n:>11,}   {n/nb:10.2%}   {binom(k):12.2%}   {k*0.8-(B-k):+8.1f}")

print("\nfirst 20 blocks (Stake Crash launch, July 2019):")
print("  " + "  ".join(f"#{i+1}:{blocks[i]}" for i in range(20)))
print("most recent 20 blocks (up to 22 Oct 2026):")
print("  " + "  ".join(f"#{nb-19+i}:{blocks[nb-20+i]}" for i in range(20)))

with open("crash_blocks_1.8x.csv", "w") as f:
    f.write("block,first_round,last_round,hits_at_1.8x,misses,result_of_100_x_$1_bets\n")
    for i, k in enumerate(blocks):
        f.write(f"{i+1},{i*B+1},{(i+1)*B},{k},{B-k},{k*0.8-(B-k):.1f}\n")
print("\nwrote crash_blocks_1.8x.csv (every block)")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

INK, MUTED, GRID, BLUE = "#1f1f1e", "#6b6a63", "#e6e5df", "#2a78d6"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8), gridspec_kw={"width_ratios": [1.3, 1]})
ks = np.arange(blocks.min(), blocks.max() + 1)
real = np.array([(blocks == k).mean() * 100 for k in ks])
a1.bar(ks, real, color=[BLUE if k >= 56 else "#9ec5f4" for k in ks], width=0.85, label="real blocks")
a1.plot(ks, [binom(k) * 100 for k in ks], color=INK, lw=1.5, label="pure chance (55% per round)")
a1.axvline(55.5, color=MUTED, ls=":", lw=1)
a1.annotate("56+ hits = profit", (56.3, real.max() * 0.95), color=INK, fontsize=9)
a1.set_xlabel("rounds out of 100 that reached 1.8x"); a1.set_ylabel("% of blocks")
a1.set_title(f"{nb:,} real blocks of 100 rounds", loc="left", color=INK)
a1.legend(frameon=False, loc="upper left"); a1.grid(axis="y", color=GRID)

show = 300
a2.plot(np.arange(1, show + 1), blocks[-show:], color=BLUE, lw=1.2)
a2.axhline(55, color=INK, lw=1, label="average 55")
a2.axhline(56, color=MUTED, lw=1, ls=":", label="break-even 56")
a2.set_xlabel(f"last {show} blocks (most recent on the right)"); a2.set_ylabel("hits at 1.8x per 100")
a2.set_title("Block to block, it just bounces around 55", loc="left", color=INK)
a2.legend(frameon=False, loc="lower left"); a2.grid(axis="y", color=GRID)
fig.tight_layout(); fig.savefig("crash_blocks.png", dpi=130)
print("wrote crash_blocks.png")

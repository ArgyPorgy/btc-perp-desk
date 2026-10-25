"""Find the user's screenshot rounds in the rebuilt history and draw the pattern-test chart."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

c = np.load("crash_history.npy").astype(np.int64)
N = len(c)
# user's screenshots, newest first (2:38 PM back to 2:20 PM)
shots = [1.61, 1.47, 1.08, 1.11, 10.72, 1.72, 14.64, 1.73, 1.48, 5.38, 1.83, 1.03, 22.11, 2.26, 1.32, 1.57,
         20.25, 6.47, 12.26, 1.14, 9.65, 30.12, 4.38, 15.64, 3.50, 1.00, 3.85]
seq = np.array([round(v * 100) for v in shots[::-1]])
tail = c[-2000:]
hits = [i for i in range(len(tail) - len(seq)) if np.array_equal(tail[i:i + len(seq)], seq)]
print("screenshot sequence (27 rounds, 2:24-2:38 PM) found in rebuilt history:", bool(hits),
      f"- {len(tail) - hits[0] - len(seq)} rounds before the hash I pulled" if hits else "")
print(f"games left in the 2019 chain: {10_000_000 - N:,}")

cond = np.load("crash_cond.npy")
k, p, n = cond[:, 0], cond[:, 1] * 100, cond[:, 2]
se = np.sqrt(49.5 * 50.5 / n)
BLUE, INK, MUTED, GRID = "#2a78d6", "#1f1f1e", "#6b6a63", "#e6e5df"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10})
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6))
ax = axes[0]
ax.fill_between(k, 49.5 - 2 * se, 49.5 + 2 * se, color=GRID, label="range pure chance would give")
ax.axhline(49.5, color=MUTED, lw=1, ls=":")
ax.plot(k, p, color=BLUE, lw=2, marker="o", ms=7, label="real Stake rounds")
ax.set_ylim(44, 55)
ax.set_xlabel("red rounds (< 2x) in a row before this one")
ax.set_ylabel("% of next rounds reaching 2x")
ax.set_title("Streaks don't change the next round (8.6M real rounds)", loc="left", color=INK)
ax.legend(frameon=False, loc="upper left")
ax.grid(axis="y", color=GRID)

ax = axes[1]
ts = np.logspace(np.log10(1.01), 3, 60)
real = [np.mean(c >= round(t * 100)) * 100 for t in ts]
ax.loglog(ts, 99 / ts, color=MUTED, lw=6, alpha=0.35, label="Stake's formula: 99% / target")
ax.loglog(ts, real, color=BLUE, lw=2, label="real Stake rounds")
ax.set_xlabel("cash-out target (x)")
ax.set_ylabel("% of rounds reaching it")
ax.set_title("Real results sit exactly on the formula", loc="left", color=INK)
ax.legend(frameon=False)
ax.grid(color=GRID, which="major")
fig.tight_layout()
fig.savefig("crash_analysis.png", dpi=130)
print("wrote crash_analysis.png")

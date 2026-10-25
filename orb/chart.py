"""Equity curves (exact rules, NY 09:30) and before/after-fee results per trade."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from orb_backtest import load, run

S = [("BTCUSDT", "Bitcoin", "#2a78d6"), ("PAXGUSDT", "Gold (PAXG)", "#eda100"), ("AAPL", "Apple", "#1baf7a")]
INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e6e5df"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 4.8), gridspec_kw={"width_ratios": [1.6, 1]})
gross, net = [], []
for sym, name, col in S:
    t = run(load(f"data/{sym}_5m.csv"))
    days = [x["day"] for x in t]
    eq = np.cumsum([x["R"] for x in t])
    a1.plot(days, eq, color=col, lw=2)
    a1.annotate(f"{name} {eq[-1]:+.0f}R", (days[-1], eq[-1]), xytext=(6, 0), textcoords="offset points",
                color=INK, va="center", fontsize=9)
    gross.append(np.mean([x["R_gross"] for x in t])); net.append(np.mean([x["R"] for x in t]))
a1.axhline(0, color=MUTED, lw=1, ls=":")
a1.set_title("Account in R (1R = amount risked per trade), exact video rules", loc="left", color=INK)
a1.set_ylabel("cumulative R"); a1.grid(axis="y", color=GRID)
a1.xaxis.set_major_formatter(mdates.DateFormatter("%b '%y"))
a1.set_xlim(right=a1.get_xlim()[1] + 45)
x = np.arange(len(S))
a2.bar(x - 0.19, gross, 0.36, color="#9ec5f4", label="before fees")
a2.bar(x + 0.19, net, 0.36, color="#2a78d6", label="after fees")
a2.axhline(0, color=INK, lw=1)
a2.set_xticks(x, [s[1] for s in S]); a2.set_ylabel("average R per trade")
a2.set_title("Before fees ≈ zero; fees make it negative", loc="left", color=INK)
a2.legend(frameon=False); a2.grid(axis="y", color=GRID)
fig.tight_layout(); fig.savefig("orb_results.png", dpi=130)
print("ok")

"""Equity curves of key strategies vs buy & hold, and win rate vs return (2023-2026 out-of-sample)."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone
from btc_strategies import S, evaluate, PERIODS, t, ret, ts, COST

INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e6e5df"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(14, 5))
m = t >= ts(2018)
dates = [datetime.fromtimestamp(x, timezone.utc) for x in t[m][::24]]
for name, label, col in [("Buy and hold", "Buy & hold", "#6b6a63"),
                         ("RSI(14) momentum: in >55, out <45", "RSI momentum (trend)", "#2a78d6"),
                         ("Connors RSI(2)<10 above 200d, sell >5d avg", "Connors RSI(2) (high win rate)", "#1baf7a"),
                         ("22:00-00:00 UTC only (Quantpedia 2022)", "22-00 UTC hours", "#eb6834")]:
    p = S[name][m]
    net = p * ret[m] - np.abs(np.diff(np.r_[0, p])) * COST
    eq = np.cumprod(1 + net)[::24] * 1000
    a1.plot(dates, eq, color=col, lw=2)
    a1.annotate(f"{label} ${eq[-1]:,.0f}", (dates[-1], eq[-1]), xytext=(6, 0), textcoords="offset points",
                fontsize=9, color=INK, va="center")
a1.set_yscale("log"); a1.set_ylabel("$1,000 invested Jan 2018 (log scale)")
a1.set_title("Growth of $1,000, after fees", loc="left", color=INK); a1.grid(axis="y", color=GRID)
a1.xaxis.set_major_formatter(mdates.DateFormatter("%Y")); a1.set_xlim(right=a1.get_xlim()[1] + 800)

p = "2023-Oct 2026 (out-of-sample)"
LABELS = {"Buy and hold": ("Buy & hold", (-70, -4)),
          "Connors RSI(2)<10 above 200d, sell >5d avg": ("Connors RSI(2)", (-10, -14)),
          "Bollinger dip: below lower band, sell at mid": ("Bollinger dip", (6, 6)),
          "RSI(14) momentum: in >55, out <45": ("RSI momentum", (6, 4)),
          "Above 200-day average": ("Above 200-day avg", (6, -12)),
          "22:00-00:00 UTC only (Quantpedia 2022)": ("22-00 UTC hours", (6, -4))}
for name, pos in S.items():
    s_ = evaluate(pos, *PERIODS[p])
    a2.scatter(s_["win"] * 100, s_["cagr"] * 100, s=60, color="#2a78d6", zorder=3)
    if name in LABELS:
        lab, off = LABELS[name]
        a2.annotate(lab, (s_["win"] * 100, s_["cagr"] * 100), xytext=off, textcoords="offset points",
                    fontsize=8.5, color=INK)
# win-rate trap over the same 2023-2026 window: buy daily 00:00 UTC, TP +0.5%, SL -10%, max 7 days
from btc_strategies import O, H, L, C, first
res, nxt = [], 0
for s0 in first:
    if s0 < nxt or t[s0] < ts(2023):
        continue
    en, out = O[s0], None
    for k in range(s0, min(s0 + 168, len(t))):
        if L[k] <= en * 0.90: out, nxt = -0.10, k + 1; break
        if H[k] >= en * 1.005: out, nxt = 0.005, k + 1; break
    if out is None:
        k = min(s0 + 168, len(t)) - 1; out, nxt = C[k] / en - 1, k + 1
    res.append(out - 0.0014)
r = np.array(res); yrs = (t[-1] - ts(2023)) / 31557600
trap_win, trap_cagr = np.mean(r > 0) * 100, (np.prod(1 + r) ** (1 / yrs) - 1) * 100
a2.scatter([trap_win], [trap_cagr], s=60, color="#eb6834", zorder=3)
a2.annotate(f"+0.5% take-profit / -10% stop\n({trap_win:.0f}% win rate, {trap_cagr:.0f}%/yr)", (trap_win, trap_cagr),
            xytext=(-165, 0), textcoords="offset points", fontsize=8.5, color=INK, va="center")
print(f"trap 2023+: win {trap_win:.1f}%, CAGR {trap_cagr:.1f}%")
a2.axhline(0, color=MUTED, lw=1, ls=":")
a2.set_xlabel("win rate %"); a2.set_ylabel("yearly return %")
a2.set_title("Win rate doesn't predict profit (2023-2026)", loc="left", color=INK); a2.grid(color=GRID)
fig.tight_layout(); fig.savefig("btc_strategies.png", dpi=130); print("ok")

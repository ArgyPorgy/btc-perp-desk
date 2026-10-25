"""Chart: $500 account paths (mark-to-market) for buy & hold vs averaging-down settings, and the risk/return grid."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timezone
from avgdown_optimize import run, t, C, O, N

INK, MUTED, GRID = "#1f1f1e", "#6b6a63", "#e6e5df"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": MUTED,
                     "xtick.color": MUTED, "ytick.color": MUTED, "font.size": 10})


def mtm(i0, **kw):
    r = run(i0, record=True, **kw)
    ev = r["path"]
    idx = np.array([e[0] for e in ev])
    eq = np.empty(N - i0)
    hs = np.arange(i0, N)
    k = np.searchsorted(idx, hs, side="right") - 1
    cash = np.array([e[1] for e in ev])[k]
    qty = np.array([e[2] for e in ev])[k]
    avg = np.array([e[3] for e in ev])[k]
    eq = cash + qty * (C[hs] - avg)
    if r["liq"]:
        eq[hs >= idx[-1]] = 0
    return hs, np.maximum(eq, 0)


PLANS = [("Just hold $500 of BTC (1x)", None, MUTED),
         ("$50 margin x2, add every 15%, TP 3%", dict(unit=100, step=0.15, tp=0.03), "#1baf7a"),
         ("$100 margin x2, add every 5%, TP 3%", dict(unit=200, step=0.05, tp=0.03), "#eb6834")]
fig, axes = plt.subplots(1, 3, figsize=(17, 5), gridspec_kw={"width_ratios": [1.2, 1.2, 1]})
for ax, (y, m, title) in zip(axes[:2], [(2018, 1, "Started Jan 2018"), (2021, 10, "Started Oct 2021 (near the top)")]):
    i0 = np.searchsorted(t, int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp()))
    for label, kw, col in PLANS:
        if kw is None:
            hs, eq = np.arange(i0, N), 500 * C[i0:] / O[i0]
        else:
            hs, eq = mtm(i0, **kw)
        d = [datetime.fromtimestamp(x, timezone.utc) for x in t[hs][::24]]
        ax.plot(d, eq[::24], color=col, lw=2, label=label)
        ax.annotate(f"${eq[-1]:,.0f}", (d[-1], eq[-1]), xytext=(5, 0), textcoords="offset points",
                    fontsize=9, color=INK, va="center")
    ax.axhline(500, color=MUTED, lw=1, ls=":")
    ax.set_title(title, loc="left", color=INK); ax.set_ylabel("account value $"); ax.grid(axis="y", color=GRID)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
axes[0].legend(frameon=False, fontsize=8.5, loc="upper left")

g = np.load("avgdown_weekly.npy")  # unit, step, tp, liq, median $/yr
ax = axes[2]
for unit, col, lab in [(200, "#eb6834", "$100 margin entries"), (100, "#1baf7a", "$50 margin entries")]:
    m = g[:, 0] == unit
    ax.scatter(g[m, 3] * 100, g[m, 4], s=40, color=col, label=lab, zorder=3)
ax.scatter([0], [349], s=90, marker="D", color=MUTED, zorder=4)
ax.annotate("just hold BTC: +$349/yr, 0% liquidated", (0, 349), xytext=(8, -2), textcoords="offset points",
            fontsize=8.5, color=INK, va="center")
ax.set_xlabel("% of start dates that got liquidated"); ax.set_ylabel("median profit per year on $500")
ax.set_title("Every setting: more profit = more liquidations", loc="left", color=INK)
ax.legend(frameon=False, fontsize=8.5, loc="lower right"); ax.grid(color=GRID)
fig.tight_layout(); fig.savefig("avgdown_results.png", dpi=130)
for y, m in [(2018, 1), (2021, 10)]:
    i0 = np.searchsorted(t, int(datetime(y, m, 1, tzinfo=timezone.utc).timestamp()))
    for label, kw, col in PLANS[1:]:
        r = run(i0, **kw)
        print(f"start {y}-{m:02d} {label}: {'LIQUIDATED ' + datetime.fromtimestamp(r['liq_t'], timezone.utc).strftime('%d %b %Y') if r['liq'] else f'final ${r[chr(102)+chr(105)+chr(110)+chr(97)+chr(108)]:.0f}'}, {r['cycles']} profitable cycles")
print(f"BTC: {O[np.searchsorted(t, 1514764800)]:.0f} (Jan 2018) -> {C[-1]:.0f} (Oct 2026)")

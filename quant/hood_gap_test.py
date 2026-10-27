"""HOOD (Nasdaq) since the July 2021 IPO: what happens after a big GAP DOWN at the open?
Daily bars from Yahoo Finance (cached to data/hood_1d.json). Gap = open vs prior regular-session close.
For each gap-down day: intraday result, gap fill (prior close reached), forward returns from the gap-day OPEN,
and the user's trade: long at the open, target +9.3% (87.8 -> 96), stop -4% or below the gap-day low, 10 trading days.
Same-day stop+target counts as a stop. Split by trend context (close vs the 50-day EMA before the gap).
Run: python3 hood_gap_test.py [min_gap_pct]   default 5
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

MIN = float(sys.argv[1]) / 100 if len(sys.argv) > 1 else 0.05
r = json.loads((Path(__file__).parent / "data" / "hood_1d.json").read_text())["chart"]["result"][0]
q = r["indicators"]["quote"][0]
ok = [i for i in range(len(r["timestamp"])) if None not in (q["open"][i], q["high"][i], q["low"][i], q["close"][i])]
t = np.array([r["timestamp"][i] for i in ok]); O, H, L, C = (np.array([q[k][i] for i in ok]) for k in ("open", "high", "low", "close"))
N = len(C)
ema50 = np.empty(N); ema50[0] = C[0]
for i in range(1, N):
    ema50[i] = C[i] * 2 / 51 + ema50[i - 1] * 49 / 51
gap = O[1:] / C[:-1] - 1
days = [i + 1 for i in np.where(gap <= -MIN)[0] if i + 1 < N - 1]
print(f"HOOD daily {N} bars ({datetime.fromtimestamp(t[0], timezone.utc):%Y-%m-%d} .. {datetime.fromtimestamp(t[-1], timezone.utc):%Y-%m-%d}); "
      f"gap-downs <= -{MIN * 100:.0f}%: {len(days)}")


def trade(d, stop_kind):
    """'4%': long at the gap-day OPEN, stop -4%. 'low': long at the gap-day CLOSE, stop 1% under that day's low
    (no lookahead: the low is known by the close). Target +9.3% from entry, 10 trading days."""
    if stop_kind == "4%":
        e, stop, first = O[d], O[d] * 0.96, d
    else:
        e, stop, first = C[d], L[d] * 0.99, d + 1
    tgt = e * 1.093
    for j in range(first, min(d + 10, N)):
        if L[j] <= stop:
            return -1
        if H[j] >= tgt:
            return 1
    return 0


def report(name, ds):
    if len(ds) < 3:
        print(f"\n{name}: n={len(ds)} (too few)"); return
    ds = np.array(ds)
    intraday = C[ds] / O[ds] - 1
    fill = lambda k: np.mean([H[d:min(d + k, N)].max() >= C[d - 1] for d in ds])
    print(f"\n{name}: n={len(ds)}  (median gap {np.median(O[ds] / C[ds - 1] - 1) * 100:+.1f}%)")
    print(f"  gap day: closed above its open {np.mean(intraday > 0):.0%}, median open->close {np.median(intraday) * 100:+.1f}%")
    print(f"  gap filled (prior close reached): same day {fill(1):.0%}, within 5 days {fill(5):.0%}, 10 days {fill(10):.0%}")
    for k in (1, 5, 10, 20):
        f = [C[d + k - 1] / O[d] - 1 for d in ds if d + k - 1 < N]
        print(f"  {k:2}d after the open: up {np.mean(np.array(f) > 0):.0%}  median {np.median(f) * 100:+5.1f}%  mean {np.mean(f) * 100:+5.1f}%")
    for sk, label in (("4%", "stop -4%"), ("low", "entry at the gap-day CLOSE, stop under its low")):
        res = np.array([trade(d, sk) for d in ds])
        dec = res[res != 0]
        print(f"  long -> +9.3% before {label}: won {np.mean(res == 1):.0%}, stopped {np.mean(res == -1):.0%}, "
              f"neither in 10d {np.mean(res == 0):.0%}" + (f"  (of decided: {np.mean(dec == 1):.0%})" if len(dec) else ""))


# Earnings-reaction gaps (HOOD reports after the US close; the gap is the next open). Dates I am confident of only.
EARN = {"2021-10-27", "2022-01-28", "2022-04-29", "2023-08-03", "2023-11-08", "2024-10-31", "2026-02-11", "2026-04-29"}
day_s = lambda d: datetime.fromtimestamp(t[d], timezone.utc).strftime("%Y-%m-%d")
report("ALL gap-downs", days)
report("EARNINGS gap-downs (known dates)", [d for d in days if day_s(d) in EARN])
report("gap-down while ALREADY >8% below the 50-day EMA (today's context: ~ -16%)", [d for d in days if C[d - 1] / ema50[d - 1] - 1 < -0.08])
report("gap-down from ABOVE / near the 50-day EMA", [d for d in days if C[d - 1] / ema50[d - 1] - 1 >= -0.08])
print("\nall gap-down days: " + ", ".join(f"{datetime.fromtimestamp(t[d], timezone.utc):%Y-%m-%d} ({(O[d] / C[d - 1] - 1) * 100:+.0f}%)" for d in days))
print(f"\nnow: last close {C[-1]:.2f}, {(C[-1] / ema50[-1] - 1) * 100:+.1f}% vs the 50-day EMA ({ema50[-1]:.2f})")

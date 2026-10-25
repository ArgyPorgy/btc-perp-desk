"""How does BTC trade around FOMC decisions? (Binance BTCUSDT perp 1h, Sep 2019 - now)

For each scheduled/emergency FOMC statement (14:00 New York time) compares, against every other day at the same
UTC hour (baseline):
  - the size of the move in the hours before / after the statement
  - how often a stop X% away gets hit within 24h / 72h (both directions), i.e. the risk of holding through it
  - direction after the statement (is there any drift?)
Run: python3 event_study.py [stop_pct]      default 1.9 (today: L1 stop 79,099 vs ~80,600)
"""
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

a = np.load(Path(__file__).parent / "data" / "BTCUSDT_PERP_1h.npy")
t, O, H, L, C, V, TB = a.T
N = len(C)
STOP = float(sys.argv[1]) if len(sys.argv) > 1 else 1.9

FOMC = """2019-09-18 2019-10-30 2019-12-11 2020-01-29 2020-03-03 2020-03-15 2020-04-29 2020-06-10 2020-07-29 2020-09-16 2020-11-05
2020-12-16 2021-01-27 2021-03-17 2021-04-28 2021-06-16 2021-07-28 2021-09-22 2021-11-03 2021-12-15 2022-01-26 2022-03-16 2022-05-04
2022-06-15 2022-07-27 2022-09-21 2022-11-02 2022-12-14 2023-02-01 2023-03-22 2023-05-03 2023-06-14 2023-07-26 2023-09-20 2023-11-01
2023-12-13 2024-01-31 2024-03-20 2024-05-01 2024-06-12 2024-07-31 2024-09-18 2024-11-07 2024-12-18 2025-01-29 2025-03-19 2025-05-07
2025-06-18 2025-07-30 2025-09-17 2025-10-29 2025-12-10 2026-01-28 2026-03-18 2026-04-29 2026-06-17 2026-07-29 2026-09-16""".split()
NY = ZoneInfo("America/New_York")


def event_index(d):
    hh = 17 if d == "2020-03-15" else 14  # the Sunday emergency cut came at 17:00 ET
    ts = datetime.fromisoformat(f"{d}T{hh:02d}:00").replace(tzinfo=NY).timestamp() * 1000
    i = int(np.searchsorted(t, ts))
    return i if i < N and t[i] == ts else None


ev = [i for i in (event_index(d) for d in FOMC) if i is not None and 48 <= i < N - 73]
evset = set(ev)
hours = (t // 3600000 % 24).astype(int)
dow = ((t // 86400000 + 3) % 7).astype(int)  # Monday = 0
# baseline: Tue-Thu at the same UTC hours, away from any FOMC (weekends are quieter and would flatter the comparison)
base = [i for i in range(48, N - 73) if hours[i] in {hours[j] for j in ev} and 1 <= dow[i] <= 3 and all(abs(i - j) > 72 for j in ev)]


def stats(idx):
    idx = np.array(idx)
    pre = np.abs(C[idx - 1] / C[idx - 25] - 1) * 100            # 24h into the statement
    post4 = np.abs(C[idx + 3] / C[idx - 1] - 1) * 100            # statement hour + 3h
    post24 = (C[idx + 23] / C[idx - 1] - 1) * 100
    rng24 = (np.array([H[i:i + 24].max() for i in idx]) / C[idx - 1] - 1) * 100, (1 - np.array([L[i:i + 24].min() for i in idx]) / C[idx - 1]) * 100
    hit24 = np.mean((rng24[0] >= STOP) | (rng24[1] >= STOP))
    dn24 = np.mean(rng24[1] >= STOP)
    lo72 = (1 - np.array([L[i:i + 72].min() for i in idx]) / C[idx - 1]) * 100
    return dict(n=len(idx), pre=np.median(pre), post4=np.median(post4), abs24=np.median(np.abs(post24)), up24=np.mean(post24 > 0),
                mean24=post24.mean(), hit24=hit24, dn24=dn24, dn72=np.mean(lo72 >= STOP))


e, b = stats(ev), stats(base)
print(f"FOMC statements with data: {e['n']} (Sep 2019 - Sep 2026); baseline: {b['n']} other Tue-Thu at the same UTC hours")
print(f"{'':42}{'FOMC':>10}{'baseline':>10}{'ratio':>8}")
for k, name in [("pre", "median |move| 24h before (%)"), ("post4", "median |move| statement hour +3h (%)"),
                ("abs24", "median |move| 24h after (%)"), ("hit24", f"P(touch ±{STOP}% within 24h)"),
                ("dn24", f"P(touch -{STOP}% within 24h)"), ("dn72", f"P(touch -{STOP}% within 72h)"), ("up24", "P(up 24h after)"),
                ("mean24", "mean 24h return (%)")]:
    pct = k in ("hit24", "dn24", "dn72", "up24")
    fmt = (lambda x: f"{x:9.1%}") if pct else (lambda x: f"{x:9.2f}")
    ratio = e[k] / b[k] if b[k] and k not in ("up24", "mean24") else float("nan")
    print(f"  {name:40}{fmt(e[k])} {fmt(b[k])}{'' if np.isnan(ratio) else f'{ratio:7.2f}x'}")
up = np.mean([(C[i + 23] / C[i - 1] - 1) > 0 for i in ev])
print(f"\ndirection after the statement: up {up:.0%} of {e['n']} (±{np.sqrt(up * (1 - up) / e['n']):.0%}) -> "
      f"{'no reliable drift' if abs(up - 0.5) < 2 * np.sqrt(0.25 / e['n']) else 'a drift worth testing further'}")

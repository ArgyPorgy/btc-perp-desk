"""Run the ORB study: session timing, the exact video rules, and variations. 22 Oct 2025 - 21 Oct 2026.
Run: python3 run_all.py [BTCUSDT XAUUSD NVDAUSUSD ...]
"""
import os
import sys

from orb_backtest import HEADER, fmt, load, run, stats

ASSETS = {
    "BTCUSDT": ("Bitcoin", [("Asia 00:00 UTC", "UTC", (0, 0)), ("London 08:00", "Europe/London", (8, 0)),
                            ("NY 08:30 (US data releases)", "America/New_York", (8, 30)),
                            ("NY 09:30 (stock market open)", "America/New_York", (9, 30))]),
    "PAXGUSDT": ("Gold token (PAXG, 24/7)", [("NY 09:30", "America/New_York", (9, 30))]),
    "XAUUSD": ("Gold (spot XAU/USD)", [("Asia 00:00 UTC", "UTC", (0, 0)), ("London 08:00", "Europe/London", (8, 0)),
                                       ("COMEX 08:20 NY", "America/New_York", (8, 20)),
                                       ("NY 09:30", "America/New_York", (9, 30))]),
    "NVDAUSUSD": ("NVIDIA (NVDA)", [("NY 09:30 (only session)", "America/New_York", (9, 30))]),
    "AAPL": ("Apple (AAPL, Nasdaq)", [("NY 09:30 (only session)", "America/New_York", (9, 30))]),
}
assets = sys.argv[1:] or [a for a in ASSETS if os.path.exists(f"data/{a}_5m.csv")]

for sym in assets:
    name, anchors = ASSETS[sym]
    d = load(f"data/{sym}_5m.csv")
    print(f"\n{'=' * 96}\n{name}  —  exact video rules (15-min range, 5-min close, 200 EMA, retest, stop mid, 2R)")
    print(HEADER)
    for label, tz, hm in anchors:
        print(fmt(f"open = {label}", stats(run(d, tz=tz, open_hm=hm))))
    # variations at the NY 09:30 open
    print(f"\n  variations at NY 09:30:")
    print(HEADER)
    base = dict(tz="America/New_York", open_hm=(9, 30))
    for label, kw in [
        ("no 200 EMA filter", dict(use_ema=False)),
        ("no retest (buy the breakout close)", dict(use_retest=False)),
        ("stop at other side of range", dict(stop_mode="other")),
        ("target 1R", dict(target="1R")),
        ("target 1.5R", dict(target="1.5R")),
        ("target 3R", dict(target="3R")),
        ("target = previous session high/low", dict(target="level")),
        ("entries allowed all session", dict(cutoff_min=360)),
    ]:
        print(fmt(label, stats(run(d, **base, **kw))))

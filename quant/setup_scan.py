"""Live scan for the desk's tested setups on the last CLOSED 4h candle (Binance BTCUSDT perp).

  S10: 4h candle wicks below the prior 10-day low and closes back above it -> long, stop under the wick, target 1.5R.
       153 events since 2019: +0.14R/trade after fees (halves +0.26 / +0.02).
  S20: same with the prior 20-day low -> target 2R. 90 events: +0.17R/trade (halves +0.04 / +0.30).
  (Short-side mirrors at 10/20-day HIGHS tested negative: -0.13 to -0.39R. Not traded.)
Evidence: quant/reentry_test.py (one-shot hold beats take-profit-and-re-enter on these setups).
Run: python3 setup_scan.py [days_back]   default 3 (also lists signals from the last N days, for context)
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

REST = "https://fapi.binance.com"
SETUPS = (("S20", 20, 2.0, "+0.17R/trade, n=90"), ("S10", 10, 1.5, "+0.14R/trade, n=153"))


def klines(interval, limit):
    with urllib.request.urlopen(f"{REST}/fapi/v1/klines?symbol=BTCUSDT&interval={interval}&limit={limit}", timeout=30) as r:
        k = json.load(r)
    now = time.time() * 1000
    return [{"t": x[0], "T": x[6], "h": float(x[2]), "l": float(x[3]), "c": float(x[4])} for x in k if x[6] < now]


def main():
    back_days = float(sys.argv[1]) if len(sys.argv) > 1 else 3
    h1 = klines("1h", 1500)  # 62 days of closed 1h candles
    fours = [b for b in klines("4h", 200)]
    stamp = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%a %d %b %H:%M UTC")
    found = []
    for b in fours:
        if b["T"] < time.time() * 1000 - back_days * 86400e3:
            continue
        for name, nd, k, ev in SETUPS:
            prior = [x["l"] for x in h1 if b["t"] - nd * 86400e3 <= x["t"] < b["t"]]
            if len(prior) < nd * 24 - 2:
                continue
            level = min(prior)
            if b["l"] < level < b["c"]:
                stop = b["l"] * 0.999
                r = b["c"] - stop
                found.append((b, name, level, stop, b["c"] + k * r, k, ev))
    last = fours[-1]
    print(f"last closed 4h candle: {stamp(last['T'] + 1)}  close {last['c']:,.1f}  low {last['l']:,.1f}")
    for name, nd, k, ev in SETUPS:
        prior = [x["l"] for x in h1 if last["t"] - nd * 86400e3 <= x["t"] < last["t"]]
        print(f"  {name}: prior {nd}-day low {min(prior):,.1f} ({(last['c'] / min(prior) - 1) * 100:+.2f}% away)")
    if not found:
        print(f"no setup signals in the last {back_days:g} days")
    for b, name, level, stop, tgt, k, ev in found:
        fresh = b is last
        print(f"{'SIGNAL NOW' if fresh else 'earlier   '} {name} at {stamp(b['T'] + 1)}: wick {b['l']:,.1f} < {level:,.1f} < close {b['c']:,.1f}"
              f" -> LONG {b['c']:,.1f}, stop {stop:,.1f}, target {tgt:,.1f} ({k:g}R) [{ev}]")


if __name__ == "__main__":
    main()

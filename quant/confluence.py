"""Live confluence score per market: the 9 indicator checks tested in confluence_test.py, plus live-only context.

Tested core (each +1 bull / -1 bear): EMA50 vs EMA200 on 1h, 4h, 1d; close vs EMA50 on 1h and 4h; 1d close vs EMA200;
24h return; 12h taker delta; position in the 48h range. Evidence (confluence_test.py, 2020+): trading AGAINST |S| >= 7
loses -0.17 to -0.22R per trade on BTC (t -3.4); trading WITH it is ~0R. So the score is a filter first:
  S <= -7: no longs (unless a tested setup fires, then half size)   S >= +7: no shorts (same exception)
Live context (not backtestable here, shown for judgment): OI vs price, funding.
Run: python3 confluence.py [SYMBOL ...]   default BTCUSDT ETHUSDT HYPEUSDT
"""
import json
import sys
import urllib.request

from fapi import base

REST = base()


def kl(sym, tf, n=1500):
    with urllib.request.urlopen(f"{REST}/fapi/v1/klines?symbol={sym}&interval={tf}&limit={n}", timeout=90) as r:
        k = json.load(r)
    return [x for x in k[:-1]]  # closed candles only


def ema(xs, n):
    k, out = 2 / (n + 1), xs[0]
    for x in xs[1:]:
        out = x * k + out * (1 - k)
    return out


def checks(sym):
    h1, h4, d1 = kl(sym, "1h"), kl(sym, "4h"), kl(sym, "1d")
    c1, c4, cd = [float(x[4]) for x in h1], [float(x[4]) for x in h4], [float(x[4]) for x in d1]
    delta = sum(2 * float(x[9]) - float(x[5]) for x in h1[-12:])
    hi, lo = max(float(x[2]) for x in h1[-48:]), min(float(x[3]) for x in h1[-48:])
    e = {tf: (ema(c, 50), ema(c, 200)) for tf, c in (("1h", c1), ("4h", c4), ("1d", cd))}
    rows = [
        ("1h EMA50 > EMA200", e["1h"][0] > e["1h"][1]),
        ("4h EMA50 > EMA200", e["4h"][0] > e["4h"][1]),
        ("1d EMA50 > EMA200", e["1d"][0] > e["1d"][1]),
        ("1h close > EMA50", c1[-1] > e["1h"][0]),
        ("4h close > EMA50", c4[-1] > e["4h"][0]),
        ("1d close > EMA200", cd[-1] > e["1d"][1]),
        ("24h return > 0", c1[-1] > c1[-25]),
        ("12h taker delta > 0", delta > 0),
        ("upper half of 48h range", c1[-1] > (hi + lo) / 2),
    ]
    return rows, c1[-1]


def verdict(s):
    if s >= 7:
        return "STRONG BULL: no shorts"
    if s <= -7:
        return "STRONG BEAR: no longs"
    return "mixed: either side needs its own reason (tested setup or catalyst)"


def main(syms):
    for sym in syms:
        rows, px = checks(sym)
        s = sum(1 if ok else -1 for _, ok in rows)
        print(f"{sym} {px:,.4g}  score {s:+d}/9  long {100 * (s + 9) / 18:.0f}% / short {100 * (9 - s) / 18:.0f}%  -> {verdict(s)}")
        print("   " + " | ".join(f"{name} {'+' if ok else '-'}" for name, ok in rows))


if __name__ == "__main__":
    main([a.upper() for a in sys.argv[1:]] or ["BTCUSDT", "ETHUSDT", "HYPEUSDT"])

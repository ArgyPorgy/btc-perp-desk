"""Live scan for the desk's tested setups on the last CLOSED candles (Binance BTCUSDT perp). The desk trades both ways.

LONG (any daily trend):
  S10: 4h candle wicks below the prior 10-day low and closes back above it -> long, stop under the wick, target 1.5R.
       153 events since 2019: +0.14R/trade after fees (halves +0.26 / +0.02).
  S20: same with the prior 20-day low -> target 2R. 90 events: +0.17R/trade (halves +0.04 / +0.30).
SHORT (only while the last closed DAILY candle is below the daily EMA200, "bear"):
  B20: first 4h close below the prior 20-day low -> short at the close, stop 0.1% over that 4h candle's high, 1.5R.
       33 events since 2020: +0.32R/trade (halves +0.26 / +0.39, t 1.6); +0.25 to +0.37R at every target 1-3R.
  R10 (IDEA, NOT TRADED since 2026-10-29): first 1h retest of a broken 10-day low within 48h, bear -> short, 2R.
       +0.41R (t 1.8) in short_test.py, but +0.27R (t 1.2) when the regime is checked at the breakdown instead of the
       retest (market_setups_test.py): too fragile. Still printed, for tracking.
  In daily UPtrends the same breakdowns are ~0R (they get bought), and failed-rally / crowded-funding shorts lose in
  every regime (-0.1 to -0.5R). Evidence: short_test.py, research_log.md 2026-10-28.
  S10/S20 on 2020+ data only (Binance archive): +0.09R / +0.14R, t 0.9: positive but below the t >= 1.5 bar set for new
  setups; kept, flagged marginal.
D1F (all three perps, daily): S/R flip retest above a rising SMA100, long, 2R. See d1_flips(); printed after the scan.
OTHER PERPS: the 4h setups above are tested BTC-only. On ETH and HYPE none of these setups pass (market_setups_test.py, 2026-10-29): the scan
  runs there for context only, and the desk does not trade those signals.
Run: python3 setup_scan.py [days_back] [SYMBOL]   default 3 BTCUSDT (also lists signals from the last N days)
"""
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone

from fapi import base  # Binance futures REST, or the local fallback where it is geo-blocked
REST = base()
SETUPS = (("S20", 20, 2.0, "+0.17R/trade, n=90"), ("S10", 10, 1.5, "+0.14R/trade, n=153"))
B20 = ("B20", 20, 1.5, "+0.32R/trade, n=33, bear only")
R10 = ("R10", 10, 2.0, "IDEA ONLY, not traded: fragile")
SYM = (sys.argv[2] if len(sys.argv) > 2 else "BTCUSDT").upper()
MIN_RISK = 0.004  # the backtest skipped stops closer than 0.4% (fees dominate)


def klines(interval, limit):
    with urllib.request.urlopen(f"{REST}/fapi/v1/klines?symbol={SYM}&interval={interval}&limit={limit}", timeout=60) as r:
        k = json.load(r)
    now = time.time() * 1000
    return [{"t": x[0], "T": x[6], "h": float(x[2]), "l": float(x[3]), "c": float(x[4])} for x in k if x[6] < now]


def px(x):  # price at a sensible precision for BTC (80,000) down to HYPE (80) and below
    return f"{x:,.1f}" if x >= 1000 else f"{x:,.2f}" if x >= 10 else f"{x:,.4f}"


def ema(xs, n):
    k, out = 2 / (n + 1), xs[0]
    for x in xs[1:]:
        out = x * k + out * (1 - k)
    return out


def main():
    back_days = float(sys.argv[1]) if len(sys.argv) > 1 else 3
    h1 = klines("1h", 1500)  # 62 days of closed 1h candles
    fours = [b for b in klines("4h", 200)]
    days = klines("1d", 1500)
    stamp = lambda ms: datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%a %d %b %H:%M UTC")
    low_before = lambda t, nd: min([x["l"] for x in h1 if t - nd * 86400e3 <= x["t"] < t] or [float("nan")])

    def bear_at(ms):  # last daily candle closed by `ms` is below the daily EMA200
        closed = [d["c"] for d in days if d["T"] < ms]
        return len(closed) > 200 and closed[-1] < ema(closed, 200)

    found, since = [], time.time() * 1000 - back_days * 86400e3
    for i, b in enumerate(fours):
        if b["T"] < since or i == 0:
            continue
        for name, nd, k, ev in SETUPS:
            prior = [x["l"] for x in h1 if b["t"] - nd * 86400e3 <= x["t"] < b["t"]]
            if len(prior) < nd * 24 - 2:
                continue
            level = min(prior)
            if b["l"] < level < b["c"]:
                stop = b["l"] * 0.999
                r = b["c"] - stop
                found.append((b["T"], "LONG", name, f"wick {b['l']:,.1f} < {level:,.1f} < close {b['c']:,.1f}", b["c"], stop, b["c"] + k * r, k, ev, b is fours[-1]))
        if not bear_at(b["T"]):
            continue
        for name, nd, k, ev in (B20, R10):
            level = low_before(b["t"], nd)
            if not b["c"] < level <= fours[i - 1]["c"]:
                continue
            if name == "B20":
                stop = b["h"] * 1.001
                if stop - b["c"] >= MIN_RISK * b["c"]:
                    found.append((b["T"], "SHORT", name, f"4h close {b['c']:,.1f} < {level:,.1f}", b["c"], stop, b["c"] - k * (stop - b["c"]), k, ev, b is fours[-1]))
                continue
            for x in [x for x in h1 if b["T"] < x["T"] <= b["T"] + 48 * 3600e3]:  # R10: first retest of the broken level
                if x["c"] > level:
                    break
                if x["h"] >= level * 0.999:
                    stop = max(x["h"], level) * 1.003
                    if stop - x["c"] >= MIN_RISK * x["c"]:
                        found.append((x["T"], "SHORT", name, f"1h retest {x['h']:,.1f} of {level:,.1f}, close {x['c']:,.1f}", x["c"], stop, x["c"] - k * (stop - x["c"]), k, ev, x is h1[-1]))
                    break
            else:
                if h1[-1]["T"] < b["T"] + 48 * 3600e3:
                    print(f"R10 (idea, not traded) armed: broke {level:,.1f} at {stamp(b['T'] + 1)}, retest window until {stamp(b['T'] + 1 + 48 * 3600e3)}")

    last, close = fours[-1], fours[-1]["c"]
    bear = bear_at(time.time() * 1000)
    closed = [d["c"] for d in days]
    if SYM != "BTCUSDT":
        print(f"{SYM}: these setups are tested on BTC only and FAIL on ETH/HYPE (market_setups_test.py): context, not trades")
    print(f"{SYM} last closed 4h candle: {stamp(last['T'] + 1)}  close {px(close)}  low {px(last['l'])}")
    print(f"  daily regime: close {px(closed[-1])} vs EMA200 {px(ema(closed, 200))} -> {'BEAR: B20 shorts live' if bear else 'BULL: shorts off (breakdowns get bought), longs only'}")
    for name, nd, k, ev in SETUPS:
        lo = low_before(last["t"], nd)
        print(f"  {name}: prior {nd}-day low {px(lo)} ({(close / lo - 1) * 100:+.2f}% away)")
    if not found:
        print(f"no setup signals in the last {back_days:g} days")
    for t, side, name, what, entry, stop, tgt, k, ev, fresh in sorted(found):
        print(f"{'SIGNAL NOW' if fresh else 'earlier   '} {name} at {stamp(t + 1)}: {what}"
              f" -> {side} {px(entry)}, stop {px(stop)}, target {px(tgt)} ({k:g}R) [{ev}]")


def d1_flips(days, ma=100):
    """D1F swing long (sr_flip_test.py, from @MuroCrypto's HYPE call): a daily pivot high (+-5 days) that price later
    closed >= 1% above becomes support; the first daily close back within 2% above it (no close > 1% below), with the
    close above a RISING SMA100, is the entry. Stop 1 ATR(14) under the level, 2R. BTC +0.32R n=46, ETH +0.25R n=45
    (both halves positive); the same rule on 4h is ~0R. Returns (fresh signal on the last closed day, live levels)."""
    H, L, C = [d["h"] for d in days], [d["l"] for d in days], [d["c"] for d in days]
    N = len(C)
    sm = lambda i, n: sum(C[i - n + 1:i + 1]) / n if i >= n - 1 else None
    atr = lambda i: sum(max(H[j], C[j - 1]) - min(L[j], C[j - 1]) for j in range(i - 13, i + 1)) / 14
    signal, live = None, []
    for p in range(5, N - 5):
        lv = H[p]
        if lv < max(H[p - 5:p + 6]):
            continue
        flip = next((j for j in range(p + 1, min(p + 121, N)) if C[j] >= lv * 1.01), None)
        if flip is None or any(c > lv * 1.01 for c in C[p + 1:flip]):
            continue
        state = "waiting"
        for i in range(flip + 3, min(flip + 121, N)):
            if C[i] < lv * 0.98:
                state = "lost"
                break
            if L[i] <= lv * 1.02 and C[i] >= lv * 0.99:
                m, m10 = sm(i, ma), sm(i - 10, ma)
                ok = m is not None and m10 is not None and C[i] > m > m10
                state = "used" if i < N - 1 else ("SIGNAL" if ok else "touch, SMA filter fails")
                if i == N - 1 and ok:
                    stop = lv - atr(i)
                    signal = (lv, C[i], stop, C[i] + 2 * (C[i] - stop))
                break
        if state == "waiting" and flip + 121 > N - 1:
            live.append((lv, days[flip]["T"]))
    return signal, live


def d1_report():
    for sym in ("BTCUSDT", "ETHUSDT", "HYPEUSDT"):
        global SYM
        SYM = sym
        days = klines("1d", 1500)
        signal, live = d1_flips(days)
        c = days[-1]["c"]
        near = sorted(live, key=lambda x: abs(c / x[0] - 1))[:3]
        lv_txt = ", ".join(f"{px(lv)} ({(c / lv - 1) * 100:+.1f}%)" for lv, _ in near) or "none"
        print(f"D1F {sym[:-4]}: close {px(c)}; flipped levels not yet retested (nearest): {lv_txt}")
        if signal:
            lv, e, stop, tgt = signal
            print(f"SIGNAL NOW D1F {sym}: daily close {px(e)} retested flipped level {px(lv)} above a rising SMA100 -> LONG, "
                  f"stop {px(stop)}, target {px(tgt)} (2R) [BTC +0.32R n=46, ETH +0.25R n=45]")


if __name__ == "__main__":
    main()
    print()
    d1_report()

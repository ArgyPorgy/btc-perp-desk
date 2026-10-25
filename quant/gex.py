"""BTC options gamma exposure (GEX) levels from Deribit's public data. No API key.

Prints the levels to paste into the TradingView indicator: gamma flip, call wall, put wall, plus top strikes.
  python3 gex.py            (all expiries)      python3 gex.py 30   (only expiries within 30 days)

Method: Black-Scholes gamma per option from Deribit's mark IV, times open interest.
Sign convention ("naive GEX"): dealers assumed long calls / short puts, so call gamma counts +, put gamma -.
Nobody outside the dealers knows their real book, so treat the sign as a guess and the strike walls as the solid part:
big gamma at a strike tends to pin price near it and dampen moves when dealers are long gamma.
"""
import math
import sys
from datetime import datetime, timezone

import requests

API = "https://www.deribit.com/api/v2/public"
MAX_DAYS = float(sys.argv[1]) if len(sys.argv) > 1 else 1e9


def gamma(S, K, T, iv):
    if T <= 0 or iv <= 0:
        return 0.0
    d1 = (math.log(S / K) + 0.5 * iv * iv * T) / (iv * math.sqrt(T))
    return math.exp(-0.5 * d1 * d1) / math.sqrt(2 * math.pi) / (S * iv * math.sqrt(T))


def expiry(code):  # e.g. 27NOV26 -> 08:00 UTC that day
    return datetime.strptime(code, "%d%b%y").replace(hour=8, tzinfo=timezone.utc)


def main():
    spot = requests.get(f"{API}/get_index_price", params={"index_name": "btc_usd"}, timeout=20).json()["result"]["index_price"]
    rows = requests.get(f"{API}/get_book_summary_by_currency", params={"currency": "BTC", "kind": "option"},
                        timeout=30).json()["result"]
    now = datetime.now(timezone.utc)
    opts = []
    for r in rows:
        _, exp, strike, cp = r["instrument_name"].split("-")
        T = (expiry(exp) - now).total_seconds() / (365.25 * 86400)
        if 0 < T * 365.25 <= MAX_DAYS and r["open_interest"] and r.get("mark_iv"):
            opts.append((float(strike), cp, T, r["mark_iv"] / 100, r["open_interest"]))

    def net_gex(S):  # $ gamma per 1% move, naive dealer sign
        return sum((1 if cp == "C" else -1) * gamma(S, K, T, iv) * oi * S * S * 0.01 for K, cp, T, iv, oi in opts)

    by_strike = {}
    for K, cp, T, iv, oi in opts:
        g = gamma(spot, K, T, iv) * oi * spot * spot * 0.01
        c, p = by_strike.get(K, (0.0, 0.0))
        by_strike[K] = (c + g, p) if cp == "C" else (c, p + g)
    call_wall = max(by_strike, key=lambda k: by_strike[k][0])
    put_wall = max(by_strike, key=lambda k: by_strike[k][1])

    # gamma flip: where the net GEX profile crosses zero, scanning spot +/- 25%
    grid = [spot * (0.75 + 0.005 * i) for i in range(101)]
    prof = [net_gex(s) for s in grid]
    flips = [grid[i] + (grid[i + 1] - grid[i]) * prof[i] / (prof[i] - prof[i + 1])
             for i in range(100) if prof[i] * prof[i + 1] < 0]
    flip = min(flips, key=lambda f: abs(f - spot)) if flips else float("nan")
    total = net_gex(spot)

    print(f"BTC index {spot:,.0f}   options used: {len(opts)}   ({'all expiries' if MAX_DAYS > 1e8 else f'<= {MAX_DAYS:.0f} days'})")
    print(f"net GEX at spot: ${total / 1e6:+,.1f}M per 1% move  -> "
          f"{'dealers net LONG gamma: moves tend to be damped / mean-revert' if total > 0 else 'dealers net SHORT gamma: moves tend to be amplified'}")
    print(f"gamma flip: {flip:,.0f}   call wall: {call_wall:,.0f}   put wall: {put_wall:,.0f}")
    print("\ntop strikes by total gamma ($M per 1%):")
    for K in sorted(by_strike, key=lambda k: -(by_strike[k][0] + by_strike[k][1]))[:8]:
        c, p = by_strike[K]
        print(f"  {K:>9,.0f}   calls {c / 1e6:7.1f}   puts {p / 1e6:7.1f}")
    print(f"\npaste into the indicator inputs ->  Gamma flip: {flip:.0f}   Call wall: {call_wall:.0f}   Put wall: {put_wall:.0f}")


if __name__ == "__main__":
    main()

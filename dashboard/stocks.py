"""Stock candles for the desk's Nasdaq markets (HOOD), from Yahoo Finance's public chart API. No key.

Yahoo intervals and how far back they go: 1m 7 days, 5m/15m 60 days, 1h 2 years, 1d 10 years. Regular session only
(09:30-16:00 New York), so gaps between sessions are real gaps. Bars come back in Binance kline layout so the
dashboard and tools treat them like any other market; there is no taker-buy split, so takerBuy = volume / 2 (zero delta).
  python3 stocks.py HOOD 1h        # print the last few bars
"""
import json
import sys
import time
import urllib.request

UA = "Mozilla/5.0 (btc-perp-desk)"
RANGE = {"1m": "7d", "5m": "60d", "15m": "60d", "1h": "730d", "1d": "10y"}
YF_INTERVAL = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "60m", "1d": "1d"}
_cache = {}  # (ticker, tf) -> (fetched_at, payload)


def chart(ticker, tf="1h", max_age=10):
    """{"bars": [[open_ms, o, h, l, c, v, close_ms, 0, 0, takerBuy, 0, 0], ...], "meta": {...}} for a ticker."""
    key = (ticker.upper(), tf)
    at, payload = _cache.get(key, (0, None))
    if payload and time.time() - at < max_age:
        return payload
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker.upper()}?interval={YF_INTERVAL[tf]}"
           f"&range={RANGE[tf]}&includePrePost=false")
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=15) as r:
        res = json.load(r)["chart"]["result"][0]
    step = {"1m": 60, "5m": 300, "15m": 900, "1h": 3600, "1d": 86400}[tf]
    q = res["indicators"]["quote"][0]
    bars = []
    for i, t in enumerate(res.get("timestamp") or []):
        o, h, l, c, v = (q[k][i] for k in ("open", "high", "low", "close", "volume"))
        if None in (o, h, l, c):
            continue
        v = v or 0
        if not v and tf != "1d":  # Yahoo's closing-print stub at 16:00 (zero volume, flat)
            continue
        bars.append([t * 1000, o, h, l, c, v, (t + step) * 1000 - 1, 0, 0, v / 2, 0, 0])
    m = res["meta"]
    period = m.get("currentTradingPeriod", {}).get("regular", {})
    now = time.time()
    payload = {"bars": bars, "meta": {
        "symbol": m.get("symbol"), "exchange": m.get("fullExchangeName"), "currency": m.get("currency"),
        "price": m.get("regularMarketPrice"), "prevClose": prev_close(ticker) if tf != "1d" else (bars[-2][4] if len(bars) > 1 else None),
        "open": period.get("start", 0) <= now < period.get("end", 0), "sessionStart": period.get("start"), "sessionEnd": period.get("end"),
        "dayHigh": m.get("regularMarketDayHigh"), "dayLow": m.get("regularMarketDayLow"), "dayVolume": m.get("regularMarketVolume"),
    }}
    _cache[key] = (time.time(), payload)
    return payload


def prev_close(ticker):
    """The last regular-session close before today's (from the daily chart, cached 10 min)."""
    d = chart(ticker, "1d", max_age=600)["bars"]
    return d[-2][4] if len(d) > 1 else None


def minutes(ticker):
    """Last ~5 sessions of 1m candles -> {minute_ts: (open, close)}, for news reactions."""
    return {int(b[0] // 1000): (b[1], b[4]) for b in chart(ticker, "1m", max_age=60)["bars"]}


if __name__ == "__main__":
    tk, tf = (sys.argv[1:3] + ["HOOD", "1h"][len(sys.argv[1:3]):])[:2]
    p = chart(tk, tf)
    print(json.dumps(p["meta"]))
    for b in p["bars"][-5:]:
        print(time.strftime("%Y-%m-%d %H:%M", time.gmtime(b[0] / 1000)), b[1:6])

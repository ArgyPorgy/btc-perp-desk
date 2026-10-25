"""Download 1-minute candles from Dukascopy's free datafeed and resample to 5-minute.
Usage: python3 get_dukascopy.py XAUUSD  -> data/XAUUSD_5m.csv  (unix_ms,open,high,low,close,volume)
Covers 2025-10-01 .. 2026-10-21. Note: Dukascopy URL months are zero-based.
"""
import lzma
import os
import struct
import sys
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone

sym = sys.argv[1]
SCALE = 1000.0  # price points per unit for metals and US stock CFDs
os.makedirs("data/raw", exist_ok=True)


def get(d):
    path = f"data/raw/{sym}_{d.isoformat()}.bi5"
    if os.path.exists(path):
        return open(path, "rb").read()
    url = f"https://datafeed.dukascopy.com/datafeed/{sym}/{d.year}/{d.month-1:02d}/{d.day:02d}/BID_candles_min_1.bi5"
    for attempt in range(6):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
            open(path, "wb").write(data)
            time.sleep(0.8)
            return data
        except urllib.error.HTTPError as e:
            if e.code == 404:
                open(path, "wb").write(b"")
                return b""
            time.sleep(3 * (attempt + 1))
        except Exception:
            time.sleep(3 * (attempt + 1))
    print("FAILED", d)
    return b""


def decode(raw, d):
    if not raw:
        return []
    buf = lzma.decompress(raw)
    day0 = int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())
    out = []
    for i in range(0, len(buf), 24):
        t, o, c, lo, hi, v = struct.unpack(">5if", buf[i:i + 24])
        if v <= 0:
            continue  # empty minute (market closed)
        out.append((day0 + t, o / SCALE, hi / SCALE, lo / SCALE, c / SCALE, v))
    return out


if __name__ == "__main__":
    start, end = date(2025, 10, 1), date(2026, 10, 21)
    if len(sys.argv) > 2:  # quick format check on one day
        d = date.fromisoformat(sys.argv[2])
        rows = decode(get(d), d)
        print(len(rows), rows[:2], rows[-1:])
        sys.exit()
    mins = []
    d = start
    while d <= end:
        if d.weekday() != 5:  # Saturdays are empty for both gold and stocks
            mins += decode(get(d), d)
        d += timedelta(days=1)
    bars = {}
    for t, o, h, l, c, v in mins:
        k = t - t % 300
        if k not in bars:
            bars[k] = [o, h, l, c, v]
        else:
            b = bars[k]
            b[1], b[2], b[3], b[4] = max(b[1], h), min(b[2], l), c, b[4] + v
    with open(f"data/{sym}_5m.csv", "w") as f:
        for k in sorted(bars):
            o, h, l, c, v = bars[k]
            f.write(f"{k*1000},{o},{h},{l},{c},{v}\n")
    print(sym, len(bars), "5m bars from", len(mins), "1m bars")

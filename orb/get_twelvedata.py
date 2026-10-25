"""Download 5-minute stock candles from Twelve Data (public demo key; works for AAPL).
Usage: python3 get_twelvedata.py AAPL -> data/AAPL_5m.csv (unix_ms,open,high,low,close,volume), 2025-10-01..2026-10-21
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

sym = sys.argv[1]
NY = ZoneInfo("America/New_York")
bars = {}
end = "2026-10-21 16:00:00"
while True:
    q = urllib.parse.urlencode(dict(symbol=sym, interval="5min", outputsize=5000, apikey="demo",
                                    start_date="2025-10-01 09:30:00", end_date=end))
    data = json.load(urllib.request.urlopen(f"https://api.twelvedata.com/time_series?{q}", timeout=60))
    if data.get("status") != "ok":
        print(data)
        break
    vals = data["values"]
    for v in vals:
        ts = int(datetime.strptime(v["datetime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=NY).timestamp())
        bars[ts] = (v["open"], v["high"], v["low"], v["close"], v["volume"])
    oldest = vals[-1]["datetime"]
    print(f"got {len(vals)} bars back to {oldest}")
    if len(vals) < 5000:
        break
    end = oldest
    time.sleep(10)
with open(f"data/{sym}_5m.csv", "w") as f:
    for ts in sorted(bars):
        f.write(f"{ts*1000},{','.join(bars[ts])}\n")
print(sym, len(bars), "bars")

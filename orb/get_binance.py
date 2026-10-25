"""Download 5-minute klines from Binance's public archive (data.binance.vision).
Usage: python3 get_binance.py BTCUSDT  -> data/BTCUSDT_5m.csv  (unix_ms,open,high,low,close,volume)
Covers 2025-10-01 .. 2026-10-21.
"""
import csv
import io
import os
import sys
import urllib.request
import zipfile
from datetime import date, timedelta

sym = sys.argv[1]
base = "https://data.binance.vision/data/spot"
os.makedirs("data", exist_ok=True)
rows = []


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
        return list(csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))))
    except Exception as e:
        print("skip", url.rsplit("/", 1)[-1], e)
        return []


for y, m in [(2025, 10), (2025, 11), (2025, 12)] + [(2026, k) for k in range(1, 10)]:
    rows += fetch(f"{base}/monthly/klines/{sym}/5m/{sym}-5m-{y}-{m:02d}.zip")
d = date(2026, 10, 1)
while d <= date(2026, 10, 21):
    rows += fetch(f"{base}/daily/klines/{sym}/5m/{sym}-5m-{d.isoformat()}.zip")
    d += timedelta(days=1)

out = []
for r in rows:
    if not r or not r[0].isdigit():
        continue
    t = int(r[0])
    if t > 10**14:  # newer archives use microseconds
        t //= 1000
    out.append((t, r[1], r[2], r[3], r[4], r[5]))
out = sorted(set(out))
with open(f"data/{sym}_5m.csv", "w") as f:
    f.write("\n".join(",".join(map(str, o)) for o in out))
print(sym, len(out), "bars")

"""Download BTCUSDT 1-hour klines from Binance's public archive, Sep 2017 .. 21 Oct 2026.
Usage: python3 get_binance_hist.py -> data/BTCUSDT_1h.csv (unix_ms,open,high,low,close,volume)
"""
import csv
import io
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor
from datetime import date, timedelta

base = "https://data.binance.vision/data/spot"
urls = [f"{base}/monthly/klines/BTCUSDT/1h/BTCUSDT-1h-{y}-{m:02d}.zip"
        for y in range(2017, 2027) for m in range(1, 13) if (2017, 9) <= (y, m) <= (2026, 9)]
d = date(2026, 10, 1)
while d <= date(2026, 10, 21):
    urls.append(f"{base}/daily/klines/BTCUSDT/1h/BTCUSDT-1h-{d.isoformat()}.zip")
    d += timedelta(days=1)


def fetch(url):
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            z = zipfile.ZipFile(io.BytesIO(r.read()))
        return list(csv.reader(io.TextIOWrapper(z.open(z.namelist()[0]))))
    except Exception as e:
        print("skip", url.rsplit("/", 1)[-1], e)
        return []


with ThreadPoolExecutor(6) as ex:
    rows = [r for chunk in ex.map(fetch, urls) for r in chunk]
out = set()
for r in rows:
    if r and r[0].isdigit():
        t = int(r[0])
        out.add((t // 1000 if t > 10**14 else t, r[1], r[2], r[3], r[4], r[5]))
with open("data/BTCUSDT_1h.csv", "w") as f:
    f.write("\n".join(",".join(map(str, o)) for o in sorted(out)))
print(len(out), "hourly bars")

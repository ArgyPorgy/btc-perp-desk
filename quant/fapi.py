"""Binance USD-M futures data, with a fallback for machines where fapi.binance.com is geo-blocked (HTTP 451).

The desk tools (Python and Node) talk to Binance's futures REST API. Some hosts, such as the cloud box the scheduled
desk runs use, get 451 from fapi.binance.com. There, this file runs a small local server on 127.0.0.1:8787 that
answers the same endpoints in Binance's format:
  - complete days: Binance's own archive (data.binance.vision): exact perp klines incl. taker-buy volume, funding.
  - today / live:  OKX's USDT perp (BTC-USDT-SWAP etc.): candles + taker volume, mark/index, funding, open interest.
    OKX volumes are scaled to Binance's from the overlap with the last archived day, so deltas stay comparable.
On a machine where Binance answers, base() returns the real API and nothing here runs.

Endpoints: /fapi/v1/klines, ticker/price, ticker/24hr, premiumIndex, openInterest, fundingRate, depth,
/futures/data/openInterestHist.   (aggTrades is not emulated.)
Use:  from fapi import base; REST = base()        python3 fapi.py base | serve | stop
"""
import csv
import io
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REAL = "https://fapi.binance.com"
VISION = "https://data.binance.vision/data/futures/um"
OKX = "https://www.okx.com/api/v5"
PORT = int(os.environ.get("FAPI_SHIM_PORT", 8787))
LOCAL = f"http://127.0.0.1:{PORT}"
DATA = Path(__file__).parent / "data"
ARCHIVE = DATA / "vision"
PROBE = DATA / "fapi_probe.json"
UA = "btc-perp-desk/1.0"
EARLIEST = 1577750400000  # 2019-12-31: the first day in Binance's futures archive (the live API goes back to 2019-09-08)
MS = {"1m": 60_000, "3m": 180_000, "5m": 300_000, "15m": 900_000, "30m": 1_800_000, "1h": 3_600_000, "2h": 7_200_000,
      "4h": 14_400_000, "6h": 21_600_000, "8h": 28_800_000, "12h": 43_200_000, "1d": 86_400_000}
OKX_BAR = {"1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m", "1h": "1H", "2h": "2H", "4h": "4H",
           "6h": "6Hutc", "12h": "12Hutc", "1d": "1Dutc"}


# ───────── which API to use
def http(url, raw=False, tries=3):
    for i in range(tries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=20) as r:
                body = r.read()
            return body if raw else json.loads(body)
        except urllib.error.HTTPError as e:
            if e.code in (400, 403, 404, 451) or i == tries - 1:
                raise
        except (urllib.error.URLError, TimeoutError):
            if i == tries - 1:
                raise
        time.sleep(1 + i)


def real_ok():
    """Does fapi.binance.com answer from here? Cached 30 min."""
    try:
        p = json.loads(PROBE.read_text())
        if time.time() - p["ts"] < 1800:
            return p["ok"]
    except (OSError, ValueError, KeyError):
        pass
    try:
        http(f"{REAL}/fapi/v1/ping", tries=1)
        ok = True
    except urllib.error.HTTPError as e:
        ok = e.code not in (403, 451)
    except (urllib.error.URLError, TimeoutError):
        ok = False
    DATA.mkdir(exist_ok=True)
    PROBE.write_text(json.dumps({"ts": time.time(), "ok": ok}))
    return ok


def alive():
    try:
        with urllib.request.urlopen(f"{LOCAL}/fapi/v1/ping", timeout=2) as r:
            return r.status == 200
    except (urllib.error.URLError, OSError):
        return False


def ensure():
    """Start the fallback server (detached, shared by every tool) unless it's already up."""
    if alive():
        return
    DATA.mkdir(exist_ok=True)
    log = open(DATA / "fapi_shim.log", "a")
    subprocess.Popen([sys.executable, str(Path(__file__).resolve()), "serve"], stdin=subprocess.DEVNULL,
                     stdout=log, stderr=log, start_new_session=True)
    for _ in range(50):
        if alive():
            return
        time.sleep(0.1)
    raise RuntimeError(f"fapi fallback server did not start (see {DATA / 'fapi_shim.log'})")


def base():
    """Base URL for Binance futures REST: the real API if reachable, else the local fallback."""
    if os.environ.get("FAPI"):
        return os.environ["FAPI"]
    if real_ok():
        return REAL
    ensure()
    print("[data] fapi.binance.com blocked here (451): using Binance archive + OKX perp for today", file=sys.stderr)
    return LOCAL


# ───────── Binance archive (complete days)
def _vision_csv(path):
    """Rows of an archive zip (cached forever once downloaded), or None if not published."""
    f = ARCHIVE / path.replace(".zip", ".csv")
    if f.with_suffix(".404").exists():
        return None
    if not f.exists():
        try:
            body = http(f"{VISION}/{path}", raw=True)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                if path.startswith("monthly/"):  # a past month that will never be published (dailies cover it)
                    f.parent.mkdir(parents=True, exist_ok=True)
                    f.with_suffix(".404").touch()
                return None
            raise
        with zipfile.ZipFile(io.BytesIO(body)) as z:
            text = z.read(z.namelist()[0]).decode()
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(text)
    rows = list(csv.reader(io.StringIO(f.read_text())))
    return [r for r in rows if r and r[0][:1].isdigit()]  # drop the header line, if any


def _days(a_ms, b_ms):
    d = datetime.fromtimestamp(a_ms / 1000, timezone.utc).date()
    end = datetime.fromtimestamp(b_ms / 1000, timezone.utc).date()
    while d <= end:
        yield d
        d += timedelta(days=1)


def archive_klines(sym, interval, a_ms, b_ms):
    """Binance archive klines with open time in [a_ms, b_ms], and the time from which nothing is archived yet
    (the first unpublished day). Gaps inside the archive (exchange downtime) stay gaps."""
    today = datetime.now(timezone.utc).date()
    out, month_done, covered = [], set(), None
    for d in _days(max(a_ms, EARLIEST), b_ms):
        if d >= today:
            covered = d
            break
        ym = d.strftime("%Y-%m")
        if ym in month_done:
            continue
        if (d.year, d.month) < (today.year, today.month):
            rows = _vision_csv(f"monthly/klines/{sym}/{interval}/{sym}-{interval}-{ym}.zip")
            if rows is not None:
                out += rows
                month_done.add(ym)
                continue
        rows = _vision_csv(f"daily/klines/{sym}/{interval}/{sym}-{interval}-{d}.zip")
        if rows is None:
            if (today - d).days <= 3:  # not published yet
                covered = d
                break
            continue  # an old day missing from the archive
        out += rows
    covered_ms = int(datetime(covered.year, covered.month, covered.day, tzinfo=timezone.utc).timestamp() * 1000) if covered else b_ms + 1
    res = []
    for r in out:
        t = int(r[0]) // (1000 if int(r[0]) > 1e14 else 1)  # newer archives may use microseconds
        if a_ms <= t <= b_ms:
            res.append([t, r[1], r[2], r[3], r[4], r[5], t + MS[interval] - 1, r[7], int(r[8]), r[9], r[10], "0"])
    return res, covered_ms


def archive_funding(sym, a_ms, b_ms):
    today = datetime.now(timezone.utc).date()
    out, seen = [], set()
    for d in _days(a_ms, b_ms):
        ym = d.strftime("%Y-%m")
        if ym in seen or (d.year, d.month) >= (today.year, today.month):
            continue
        seen.add(ym)
        out += _vision_csv(f"monthly/fundingRate/{sym}/{sym}-fundingRate-{ym}.zip") or []
    return [(int(r[0]) // 1000 * 1000, float(r[2])) for r in out if a_ms <= int(r[0]) <= b_ms + 1000]


# ───────── OKX (today, live)
_ct = {}


def okx_inst(sym):
    return sym[:-4] + "-USDT-SWAP"


def ct_val(sym):
    if sym not in _ct:
        d = http(f"{OKX}/public/instruments?instType=SWAP&instId={okx_inst(sym)}")["data"]
        _ct[sym] = float(d[0]["ctVal"]) if d else 1.0
    return _ct[sym]


def okx(path):
    j = http(f"{OKX}{path}")
    if j.get("code") != "0":
        raise RuntimeError(f"OKX {path}: {j.get('msg')}")
    return j["data"]


def okx_candles(sym, interval, a_ms):
    """OKX candles with open time >= a_ms, oldest first: (t, o, h, l, c, vol_base, vol_quote)."""
    inst, bar = okx_inst(sym), OKX_BAR[interval]
    rows = okx(f"/market/candles?instId={inst}&bar={bar}&limit=300")
    while rows and int(rows[-1][0]) > a_ms:
        older = okx(f"/market/history-candles?instId={inst}&bar={bar}&limit=100&after={rows[-1][0]}")
        if not older:
            break
        rows += older
        time.sleep(0.12)  # history endpoint: 20 requests / 2 s
    out = {int(r[0]): (int(r[0]), float(r[1]), float(r[2]), float(r[3]), float(r[4]), float(r[6]), float(r[7]))
           for r in rows if int(r[0]) >= a_ms}
    return [out[k] for k in sorted(out)]


def okx_taker_buy(sym, a_ms):
    """Closed hours since a_ms: {hour_open_ms: (taker buy, total)} in contracts."""
    inst, out, end = okx_inst(sym), {}, ""
    now = time.time() * 1000
    for _ in range(20):
        rows = okx(f"/rubik/stat/taker-volume-contract?instId={inst}&period=1H&limit=100{end}")
        for t, sell, buy in rows:
            if int(t) + 3_600_000 <= now:  # the open hour reads 0 until it closes
                out[int(t)] = (float(buy), float(buy) + float(sell))
        if not rows or int(rows[-1][0]) <= a_ms:
            break
        end = f"&end={rows[-1][0]}"
    return out


def klines(sym, interval, limit=500, start=None, end=None):
    step = MS[interval]
    now = int(time.time() * 1000)
    limit = max(1, min(int(limit), 1500))
    if start is not None:
        start = max(start, EARLIEST)  # like Binance: begin at the first bar that exists
        a, b = start, min(end or now, start + (limit - 1) * step)
    else:
        b = min(end or now, now)
        a = b - (limit - 1) * step
    a = a // step * step
    overlap = min(86_400_000, 300 * step)  # archived bars before OKX takes over, to calibrate OKX volume
    arch, covered = archive_klines(sym, interval, a - overlap, b)
    bars = {r[0]: r for r in arch}
    if covered <= b:
        o_from = max(a, covered, now - 7 * 86_400_000) - overlap  # OKX only for the days the archive lacks
        oc = okx_candles(sym, interval, o_from)
        ratio = 1.0
        ov = [(bars[t][5], v) for t, *_x, v, _q in oc if t in bars]
        if ov and sum(v for _b, v in ov) > 0:
            ratio = sum(float(b_) for b_, _v in ov) / sum(v for _b, v in ov)
        tb = okx_taker_buy(sym, o_from) if step >= 3_600_000 else {}
        for t, o, h, l, c, v, q in oc:
            if t in bars or t < covered or not a <= t <= b:
                continue
            hours = [tb[x] for x in range(t, t + step, 3_600_000) if x in tb]
            tot = sum(x[1] for x in hours)
            vol = v * ratio
            buy = vol * (sum(x[0] for x in hours) / tot if tot else 0.5)  # taker-buy share of the closed hours
            bars[t] = [t, f"{o}", f"{h}", f"{l}", f"{c}", f"{vol:.3f}", t + step - 1, f"{q * ratio:.2f}", 0,
                       f"{buy:.3f}", f"{buy * c:.2f}", "0"]
    out = [bars[k] for k in sorted(bars) if a <= k <= b]
    return out[:limit] if start is not None else out[-limit:]


def funding(sym, limit=100, start=None, end=None):
    now = int(time.time() * 1000)
    limit = max(1, min(int(limit), 1000))
    a = start if start is not None else now - (limit + 3) * 8 * 3_600_000 - 86_400_000
    b = end or now
    rows = dict(archive_funding(sym, a, b))
    after = max(rows) if rows else a - 1
    if after < now - 9 * 3_600_000:  # the current month isn't archived yet: OKX history (~3 months)
        cursor = ""
        for _ in range(10):
            d = okx(f"/public/funding-rate-history?instId={okx_inst(sym)}&limit=100{cursor}")
            for x in d:
                t = int(x["fundingTime"])
                if t > after and a <= t <= b:
                    rows[t] = float(x["realizedRate"] or x["fundingRate"])
            if not d or int(d[-1]["fundingTime"]) <= max(after, a):
                break
            cursor = f"&after={d[-1]['fundingTime']}"
    out = [{"symbol": sym, "fundingTime": t, "fundingRate": f"{rows[t]:.8f}", "markPrice": ""} for t in sorted(rows)]
    return out[:limit] if start is not None else out[-limit:]


def ticker(sym):
    return okx(f"/market/ticker?instId={okx_inst(sym)}")[0]


def premium_index(sym):
    mark = okx(f"/public/mark-price?instType=SWAP&instId={okx_inst(sym)}")[0]
    try:
        idx = okx(f"/market/index-tickers?instId={sym[:-4]}-USDT")[0]["idxPx"]
    except (RuntimeError, IndexError):
        idx = mark["markPx"]
    f = okx(f"/public/funding-rate?instId={okx_inst(sym)}")[0]
    return {"symbol": sym, "markPrice": mark["markPx"], "indexPrice": idx, "lastFundingRate": f["fundingRate"],
            "nextFundingTime": int(f["fundingTime"]), "interestRate": f.get("interestRate", "0.0001"), "time": int(mark["ts"])}


def oi_hist(sym, period="1h", limit=30):
    bar = {"5m": "5m", "15m": "15m", "30m": "30m", "1h": "1H", "2h": "2H", "4h": "4H", "6h": "6H", "12h": "12H", "1d": "1D"}[period]
    rows, end, limit = [], "", int(limit)
    while len(rows) < limit:
        d = okx(f"/rubik/stat/contracts/open-interest-history?instId={okx_inst(sym)}&period={bar}&limit=100{end}")
        if not d:
            break
        rows += d
        end = f"&end={d[-1][0]}"
    rows = sorted({int(r[0]): r for r in rows}.values(), key=lambda r: int(r[0]))[-limit:]
    return [{"symbol": sym, "sumOpenInterest": r[2], "sumOpenInterestValue": r[3], "timestamp": int(r[0])} for r in rows]


def depth(sym, limit=100):
    k = ct_val(sym)
    d = okx(f"/market/books?instId={okx_inst(sym)}&sz={min(int(limit), 400)}")[0]
    side = lambda xs: [[p, f"{float(q) * k:.4f}"] for p, q, *_ in xs]
    return {"lastUpdateId": int(d["ts"]), "E": int(d["ts"]), "T": int(d["ts"]), "bids": side(d["bids"]), "asks": side(d["asks"])}


# ───────── the local server
def route(path, q):
    sym = q.get("symbol", "BTCUSDT").upper()
    num = lambda k: int(q[k]) if k in q else None
    if path == "/fapi/v1/ping":
        return {}
    if path == "/fapi/v1/klines":
        return klines(sym, q.get("interval", "1h"), q.get("limit", 500), num("startTime"), num("endTime"))
    if path == "/fapi/v1/fundingRate":
        return funding(sym, q.get("limit", 100), num("startTime"), num("endTime"))
    if path == "/fapi/v1/ticker/price":
        return {"symbol": sym, "price": ticker(sym)["last"], "time": int(time.time() * 1000)}
    if path == "/fapi/v1/ticker/24hr":
        t = ticker(sym)
        last, op = float(t["last"]), float(t["open24h"])
        return {"symbol": sym, "lastPrice": t["last"], "openPrice": t["open24h"], "highPrice": t["high24h"],
                "lowPrice": t["low24h"], "priceChange": f"{last - op:.2f}", "priceChangePercent": f"{(last / op - 1) * 100:.3f}",
                "volume": t["volCcy24h"], "quoteVolume": f"{float(t['volCcy24h']) * last:.2f}"}
    if path == "/fapi/v1/premiumIndex":
        return premium_index(sym)
    if path == "/fapi/v1/openInterest":
        d = okx(f"/public/open-interest?instType=SWAP&instId={okx_inst(sym)}")[0]
        return {"symbol": sym, "openInterest": d["oiCcy"], "time": int(d["ts"])}
    if path == "/futures/data/openInterestHist":
        return oi_hist(sym, q.get("period", "1h"), q.get("limit", 30))
    if path == "/fapi/v1/depth":
        return depth(sym, q.get("limit", 100))
    return None


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        u = urllib.parse.urlsplit(self.path)
        q = dict(urllib.parse.parse_qsl(u.query))
        try:
            body, code = route(u.path, q), 200
            if body is None:
                body, code = {"code": -1, "msg": f"{u.path} is not emulated by the fallback"}, 404
        except Exception as e:  # noqa: BLE001 - report any upstream failure to the client
            body, code = {"code": -1, "msg": f"{type(e).__name__}: {e}"}, 502
        data = json.dumps(body).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):
        pass


def serve():
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    print(f"fapi fallback on {LOCAL} (pid {os.getpid()})", flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "base"
    if cmd == "serve":
        serve()
    elif cmd == "base":
        print(base())
    elif cmd == "stop":
        subprocess.run(["pkill", "-f", "fapi.py serve"])

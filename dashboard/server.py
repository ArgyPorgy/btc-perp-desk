"""BTC Perp Desk local server: serves the dashboard and keeps the news terminal live.

  python3 server.py              # http://127.0.0.1:8787
  python3 server.py --port 8790

Endpoints (local only):
  /api/news?hours=48&min=1   tagged, de-duplicated headlines with BTC's move since each one
  /api/calendar              high-impact economic events (ForexFactory weekly calendar, cached 1h)
  /api/stock?symbol=HOOD&tf=1h   Nasdaq candles (Yahoo Finance, Binance kline layout) for the stock markets
  /api/health                feed status
Every feed is polled on its own interval (60-300s) in a background thread; see news.py for sources and rules.
"""
import argparse
import json
import sys
import threading
import time
import urllib.parse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import news
import stocks

HERE = Path(__file__).parent
store = news.NewsStore()
state = {"mins": {}, "mins_at": 0, "polls": 0, "started": time.time()}
SYMBOLS = ("BTCUSDT", "ETHUSDT", "HYPEUSDT")  # perp markets whose reaction to each headline we measure
STOCKS = ("HOOD",)  # Nasdaq markets (Yahoo Finance)
other_mins = {}  # symbol -> (fetched_at, minutes), fetched on demand


def poller():
    while True:
        now = time.time()
        due = [f[0] for f in news.FEEDS if now - store.health.get(f[0], {}).get("last_try", 0) >= f[6]]
        if due:
            res = store.poll(due)
            state["polls"] += 1
            if any(isinstance(v, int) and v > 0 for v in res.values()) or state["polls"] % 20 == 1:
                store.save()
        if now - state["mins_at"] >= 60:
            try:
                state["mins"] = news.btc_minutes()
                state["mins_at"] = now
            except Exception as e:
                print(f"BTC 1m candles unavailable: {e}", file=sys.stderr)
        try:
            news.calendar()  # refreshes its own cache at most hourly
        except Exception as e:
            print(f"calendar unavailable: {e}", file=sys.stderr)
        time.sleep(10)


class Handler(SimpleHTTPRequestHandler):
    def log_request(self, code="-", size="-"):  # keep the console quiet: only failed requests
        if isinstance(code, int) and code >= 400 and not self.path.startswith("/favicon"):
            super().log_request(code, size)

    def send_json(self, obj):
        body = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        q = urllib.parse.parse_qs(u.query)
        if u.path == "/api/news":
            hours = min(float(q.get("hours", ["48"])[0]), 24 * news.KEEP_DAYS)
            sym = q.get("sym", ["BTCUSDT"])[0].upper()
            items = news.annotate(store.query(hours, int(q.get("min", ["1"])[0])), self.minutes(sym))
            return self.send_json({"now": time.time(), "items": items[:600], "feeds": self.feed_status()})
        if u.path == "/api/stock":
            sym, tf = q.get("symbol", ["HOOD"])[0].upper(), q.get("tf", ["1h"])[0]
            if sym not in STOCKS or tf not in stocks.RANGE:
                return self.send_json({"error": f"unsupported {sym} {tf}"})
            try:
                return self.send_json(stocks.chart(sym, tf))
            except Exception as e:  # noqa: BLE001 - Yahoo down or rate-limited: tell the page, keep serving
                return self.send_json({"error": f"{type(e).__name__}: {e}"})
        if u.path == "/api/calendar":
            return self.send_json(news.calendar())
        if u.path == "/api/health":
            return self.send_json({"ok": True, "uptime": time.time() - state["started"], "feeds": self.feed_status()})
        return super().do_GET()

    @staticmethod
    def minutes(sym):
        if sym == "BTCUSDT" or sym not in SYMBOLS + STOCKS:
            return state["mins"]
        at, mins = other_mins.get(sym, (0, {}))
        if time.time() - at > 60:
            try:
                mins = stocks.minutes(sym) if sym in STOCKS else news.btc_minutes(sym)
                other_mins[sym] = (time.time(), mins)
            except Exception as e:
                print(f"{sym} 1m candles unavailable: {e}", file=sys.stderr)
        return mins

    @staticmethod
    def feed_status():
        out = {}
        for fid, label, *_ in news.FEEDS:
            h = store.health.get(fid, {})
            out[fid] = {"label": label, "ok": bool(h.get("last_ok")) and not h.get("error"), "last_ok": h.get("last_ok"), "error": h.get("error")}
        return out

    def end_headers(self):
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-cache")  # always pick up dashboard code changes
        super().end_headers()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8787)
    args = ap.parse_args()
    try:
        httpd = ThreadingHTTPServer(("127.0.0.1", args.port), partial(Handler, directory=str(HERE)))
    except OSError as e:
        sys.exit(f"port {args.port} is busy ({e.strerror}). Another server is running there — close it, or use --port 8790.")
    threading.Thread(target=poller, daemon=True).start()
    print(f"BTC Perp Desk on http://127.0.0.1:{args.port}  (news: {len(news.FEEDS)} feeds; Ctrl+C to stop)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        store.save()


if __name__ == "__main__":
    main()

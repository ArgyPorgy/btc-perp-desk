"""Paper trading desk for Binance USDT perps (BTC, ETH, HYPE). Every call is recorded and scored automatically.

Prop rules (Propr Turbo 1-Step, propr.xyz/rules, checked 2026-10-29): pass at +9% ($10,900). FAIL on either:
  max drawdown 3%, STATIC: equity below $9,700 (3% under the $10,000 start; the floor never moves, profit adds room)
  daily loss 3%: equity below 97% of the balance at 00:00 UTC (recomputed daily).
The binding floor is the higher of the two. Swing risk 0.5%, scalp 0.35%, and the risk of everything open or pending
may never exceed half the room above that floor. Orders that would break it are refused.

Two books share one account:
  swing  tested setups (S10/S20/B20 on BTC), 0.5% risk, 4h triggers, managed on 1h candles.
  scalp  discretionary chart-read trades, long or short, any listed market; default 0.35% risk, managed on 5m candles,
         24h max hold. Every scalp needs a written thesis (--note). Rails: at most 3 open positions, no new scalp after
         the day's realised scalp loss reaches 1.5% of equity. The track record is split by book, so the scalp book
         earns its place or gets cut.

  python3 paper_desk.py                 # process orders/positions against closed candles, print report
  python3 paper_desk.py add --id A --side long --trigger close_above --level 79732 --stop low_since:2026-10-24T12:00 \
        --target-r 2 --expires 2026-10-26T12:00 --oco G1 --note "reclaim long"
  python3 paper_desk.py add --id M --side short --trigger market --stop 80400 --target 78450   # enter now
  python3 paper_desk.py add --id X1 --book scalp --symbol HYPEUSDT --side long --trigger limit --level 84.2 \
        --stop 83.1 --target-r 2 --expires 2026-10-29T18:00 --note "retest of 82.5 breakout"   # limit fills on a touch (5m)
  python3 paper_desk.py add --id X2 --book scalp --side short --trigger close_below --tf 15m --level 79900 --stop 80250 --target-r 1.5
  python3 paper_desk.py cancel A
  python3 paper_desk.py close POSITION_ID       # close an open position at the current price
  python3 paper_desk.py modify L1 --stop 79500  # tighten a stop (never widen) and/or move the target
  python3 paper_desk.py journal "- 1h: ...\n- DECISION: HOLD ..."   # append a dated entry to paper/journal.md
  python3 paper_desk.py shadow --id S1 --side long --entry 80409 --at 2026-10-29T14:15 --stop 79990 --target 81037 \
        --why "cancelled on the backtest; plan side fired"   # score a trade the plan called for but I skipped/cancelled
Shadow trades are resolved on 5m candles like scalps and reported as their own record (R only, no money), so the cost
or value of my overrides is measured. Lessons and mistakes live in paper/lessons.md.

Rules: triggers 'close_above' / 'close_below' fill at the CLOSE of the first candle of --tf (default 4h; closed after
the order was placed) beyond the level; 'limit' fills at the level when a 5m candle trades THROUGH it (a bare touch doesn't count). Swing positions
are managed on closed 1h candles, scalps on 5m: if stop and target are both touched in the same candle the stop counts
(conservative). Fees 0.05% per side. Size = risk % of equity / stop distance.
"""
import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from fapi import base  # Binance futures REST, or the local fallback where it is geo-blocked
REST = base()
FEE = 0.0005
SYMBOLS = ("BTCUSDT", "ETHUSDT", "HYPEUSDT")
SCALP_RISK, SCALP_DAY_STOP, MAX_OPEN = 0.35, 1.0, 3
TARGET_PCT, MAX_DD_PCT, DAILY_PCT = 9.0, 3.0, 3.0  # Propr Turbo 1-Step


def day_start_balance(s):
    day0 = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000
    return s["start_equity"] + sum(x["pnl"] for x in s["closed"] if x["closed_ms"] < day0)


def floor(s):
    """Equity below this fails the account: max(static 3% under the start, 3% under today's 00:00 UTC balance)."""
    return max(s["start_equity"] * (1 - MAX_DD_PCT / 100), day_start_balance(s) * (1 - DAILY_PCT / 100))


def open_risk(s):
    """$ lost if every open position and pending order hit its stop (pending at their own risk %), fees included."""
    r = sum(abs(p["entry"] - p["stop"]) * p["qty"] + FEE * 2 * p["entry"] * p["qty"] for p in s["positions"])
    return r + sum(s["equity"] * (o.get("risk_pct") or s["risk_pct"]) / 100 * 1.2 for o in s["orders"])
import os
STATE = Path(os.environ.get("PAPER_STATE", Path(__file__).parent / "paper" / "state.json"))
JOURNAL = STATE.parent / "journal.md"


def get(url, tries=3):
    # retry transient resets/timeouts so a flaky connection doesn't kill the run
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                return json.load(r)
        except (OSError, ValueError):
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))


def px(x):  # BTC 80,000.0 ... HYPE 86.123
    return f"{x:,.1f}" if abs(x) >= 1000 else f"{x:,.3f}" if abs(x) >= 10 else f"{x:,.4f}"


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def parse_time(s):
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


def klines(interval, start_ms, symbol="BTCUSDT"):
    out, now = [], time.time() * 1000
    while True:
        k = get(f"{REST}/fapi/v1/klines?symbol={symbol}&interval={interval}&limit=1500&startTime={int(start_ms)}")
        out += [{"t": x[0], "T": x[6], "o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4])} for x in k]
        if len(k) < 1500:
            break
        start_ms = k[-1][0] + 1
    return [b for b in out if b["T"] < now]  # closed candles only


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"start_equity": 10000.0, "equity": 10000.0, "risk_pct": 0.5, "orders": [], "positions": [], "closed": []}


def save(s):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))


def price_now(symbol="BTCUSDT"):
    return float(get(f"{REST}/fapi/v1/ticker/price?symbol={symbol}")["price"])


def sym(x):
    return x.get("symbol", "BTCUSDT")


def resolve_stop(spec, side, upto_ms, symbol="BTCUSDT"):
    if isinstance(spec, (int, float)):
        return float(spec)
    kind, since = spec.split(":", 1)
    bars = [b for b in klines("1h", parse_time(since), symbol) if b["T"] <= upto_ms]
    if kind == "low_since":
        return min(b["l"] for b in bars) * 0.999
    if kind == "high_since":
        return max(b["h"] for b in bars) * 1.001
    raise ValueError(spec)


def open_position(s, o, entry, at_ms, events):
    side = 1 if o["side"] == "long" else -1
    stop = resolve_stop(o["stop"], side, at_ms, sym(o))
    risk_px = (entry - stop) * side
    if risk_px <= entry * 0.0005:
        events.append(f"SKIPPED {o['id']}: stop {px(stop)} is on the wrong side of (or too close to) entry {px(entry)}")
        return
    target = o.get("target") or entry + side * o["target_r"] * risk_px
    risk_pct = o.get("risk_pct") or s["risk_pct"]
    qty = s["equity"] * risk_pct / 100 / risk_px
    p = {"id": o["id"], "symbol": sym(o), "book": o.get("book", "swing"), "side": o["side"], "entry": entry, "stop": stop,
         "target": target, "qty": qty, "risk_pct": risk_pct, "opened_ms": at_ms, "note": o.get("note", ""),
         "max_hold_h": o.get("max_hold_h", 168)}
    s["positions"].append(p)
    events.append(f"ENTERED {p['book']} {p['side'].upper()} {p['id']} {p['symbol']} @ {px(entry)} | stop {px(stop)} | target {px(target)} | "
                  f"size {qty:.4f} {p['symbol'][:-4]} (risk ${s['equity'] * risk_pct / 100:,.0f}, {risk_pct}%) | {iso(at_ms)}")
    if o.get("oco"):
        for other in [x for x in s["orders"] if x.get("oco") == o["oco"] and x["id"] != o["id"]]:
            s["orders"].remove(other)
            events.append(f"CANCELLED {other['id']} (OCO with {o['id']})")


def close_position(s, p, exit_px, at_ms, reason, events):
    side = 1 if p["side"] == "long" else -1
    pnl = (exit_px - p["entry"]) * side * p["qty"] - FEE * (p["entry"] + exit_px) * p["qty"]
    risk_usd = abs(p["entry"] - p.get("orig_stop", p["stop"])) * p["qty"]
    s["equity"] += pnl
    s["positions"].remove(p)
    s["closed"].append({**p, "exit": exit_px, "closed_ms": at_ms, "reason": reason, "pnl": pnl, "R": pnl / risk_usd})
    events.append(f"CLOSED {p.get('book', 'swing')} {p['side'].upper()} {p['id']} {sym(p)} @ {px(exit_px)} ({reason}) | PnL ${pnl:+,.2f} = {pnl / risk_usd:+.2f}R | "
                  f"equity ${s['equity']:,.2f} | {iso(at_ms)}")


def process(s):
    events = []
    now = time.time() * 1000
    # 1) pending orders vs closed 4h candles
    for o in list(s["orders"]):
        if o not in s["orders"]:
            continue  # removed by OCO
        if o.get("expires_ms") and now > o["expires_ms"]:
            s["orders"].remove(o)
            events.append(f"EXPIRED {o['id']} (no trigger by {iso(o['expires_ms'])})")
            continue
        if o.get("arm") and not o.get("armed_ms"):
            for b in klines("4h", o["created_ms"] - 4 * 3600e3, sym(o)):
                if b["T"] <= o["created_ms"]:
                    continue
                a = o["arm"]
                if (a["trigger"] == "close_below" and b["c"] < a["level"]) or (a["trigger"] == "close_above" and b["c"] > a["level"]):
                    o["armed_ms"] = b["T"]
                    events.append(f"ARMED {o['id']}: 4h close {b['c']:,.1f} {a['trigger'].replace('_', ' ')} {a['level']:,.1f} at {iso(b['T'] + 1)}")
                    break
            if not o.get("armed_ms"):
                continue
        start = o.get("armed_ms") or o["created_ms"]
        if o["trigger"] == "limit":  # fills at the level when a 5m candle (opened after placement) trades through it
            for b in klines("5m", start - 300e3, sym(o)):
                if b["t"] < start:
                    continue
                # trade THROUGH the level (a bare touch may not fill a real resting order at the back of the queue)
                if (o["side"] == "long" and b["l"] < o["level"]) or (o["side"] == "short" and b["h"] > o["level"]):
                    s["orders"].remove(o)
                    open_position(s, o, o["level"], b["t"], events)
                    break
            continue
        tf = o.get("tf", "4h")
        for b in klines(tf, start - 4 * 3600e3, sym(o)):
            if b["T"] <= start:
                continue
            hit = (o["trigger"] == "close_above" and b["c"] > o["level"]) or (o["trigger"] == "close_below" and b["c"] < o["level"])
            if hit:
                s["orders"].remove(o)
                open_position(s, o, b["c"], b["T"] + 1, events)
                break
    # 2) open positions vs closed candles: 1h for swings, 5m for scalps
    for p in list(s["positions"]):
        side = 1 if p["side"] == "long" else -1
        tf, ms = ("5m", 300e3) if p.get("book") == "scalp" else ("1h", 3600e3)
        for b in klines(tf, p["opened_ms"] - ms, sym(p)):
            if b["t"] < p["opened_ms"]:
                continue  # candles from the one opening at/after the fill (a limit's fill candle counts: stop first)
            stop_hit = b["l"] <= p["stop"] if side == 1 else b["h"] >= p["stop"]
            tgt_hit = b["h"] >= p["target"] if side == 1 else b["l"] <= p["target"]
            if stop_hit:
                close_position(s, p, p["stop"], b["T"] + 1, "stop", events)
                break
            if tgt_hit:
                close_position(s, p, p["target"], b["T"] + 1, "target", events)
                break
            if b["T"] - p["opened_ms"] >= p["max_hold_h"] * 3600e3:
                close_position(s, p, b["c"], b["T"] + 1, "time limit", events)
                break
    # 3) shadow trades (skipped or cancelled plan trades): resolve on 5m candles, R only
    for x in [x for x in s.get("shadow", []) if x.get("result") is None]:
        side = 1 if x["side"] == "long" else -1
        for b in klines("5m", x["at_ms"], sym(x)):
            if b["t"] < x["at_ms"]:
                continue
            if (b["l"] <= x["stop"]) if side == 1 else (b["h"] >= x["stop"]):
                x["result"], x["R"] = "stop", -1.0
            elif (b["h"] >= x["target"]) if side == 1 else (b["l"] <= x["target"]):
                x["result"], x["R"] = "target", abs(x["target"] - x["entry"]) / abs(x["entry"] - x["stop"])
            elif b["T"] - x["at_ms"] >= 24 * 3600e3:
                x["result"], x["R"] = "time", (b["c"] - x["entry"]) * side / abs(x["entry"] - x["stop"])
            if x.get("result"):
                events.append(f"SHADOW {x['id']} {sym(x)} {x['side']} resolved: {x['result']} {x['R']:+.2f}R ({x['why']})")
                break
    return events


def report(s, events):
    prices = {x: price_now(x) for x in sorted({"BTCUSDT"} | {sym(p) for p in s["positions"] + s["orders"]})}
    print("   ".join(f"{k[:-4]} {px(v)}" for k, v in prices.items()) + f"   |   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    for e in events:
        print(f"EVENT: {e}")
    print(f"\nequity ${s['equity']:,.2f} ({(s['equity'] / s['start_equity'] - 1) * 100:+.2f}%, target +{TARGET_PCT:.0f}% = ${s['start_equity'] * (1 + TARGET_PCT / 100):,.0f}; swing risk {s['risk_pct']}%, scalp {SCALP_RISK}%)")
    room = s["equity"] - floor(s)
    static, daily = s["start_equity"] * (1 - MAX_DD_PCT / 100), day_start_balance(s) * (1 - DAILY_PCT / 100)
    print(f"floor ${floor(s):,.2f} ({'daily: 97% of 00:00 balance' if daily >= static else 'static: start - 3%'}; static ${static:,.0f}, daily ${daily:,.2f}): "
          f"room ${room:,.2f} | open+pending risk ${open_risk(s):,.2f} (cap ${room / 2:,.2f})"
          + ("   *** ACCOUNT FAILED ***" if room <= 0 else ""))
    print("open positions:" if s["positions"] else "open positions: none")
    for p in s["positions"]:
        side = 1 if p["side"] == "long" else -1
        u = (prices[sym(p)] - p["entry"]) * side * p["qty"]
        r = u / (abs(p["entry"] - p.get("orig_stop", p["stop"])) * p["qty"])
        print(f"  {p['id']} [{p.get('book', 'swing')}] {sym(p)} {p['side'].upper()} entry {px(p['entry'])} stop {px(p['stop'])} target {px(p['target'])} "
              f"| unrealised ${u:+,.2f} ({r:+.2f}R) | since {iso(p['opened_ms'])} | {p['note']}")
    print("pending orders:" if s["orders"] else "pending orders: none")
    for o in s["orders"]:
        tgt = f"target {px(o['target'])}" if o.get("target") else f"target {o['target_r']}R"
        arm = f"[{'armed' if o.get('armed_ms') else 'arms on 4h ' + o['arm']['trigger'].replace('_', ' ') + ' ' + format(o['arm']['level'], ',.0f')}] " if o.get("arm") else ""
        trig = f"limit {px(o['level'])}" if o["trigger"] == "limit" else f"{o.get('tf', '4h')} {o['trigger'].replace('_', ' ')} {px(o['level'])}"
        print(f"  {o['id']} [{o.get('book', 'swing')}] {sym(o)} {arm}{o['side'].upper()} on {trig} | stop {o['stop']} | {tgt}"
              f" | expires {iso(o['expires_ms']) if o.get('expires_ms') else 'never'}{' | OCO ' + o['oco'] if o.get('oco') else ''} | {o.get('note', '')}")
    c = s["closed"]
    if c:
        for book in ("swing", "scalp"):
            cb = [x for x in c if x.get("book", "swing") == book]
            if cb:
                rs = [x["R"] for x in cb]
                print(f"track record {book}: {len(cb)} closed | win {sum(r > 0 for r in rs) / len(rs):.0%} | total {sum(rs):+.2f}R | "
                      f"avg {sum(rs) / len(rs):+.2f}R | PnL ${sum(x['pnl'] for x in cb):+,.2f}")
        for x in c[-6:]:
            print(f"  {x['id']} [{x.get('book', 'swing')}] {sym(x)} {x['side']} {px(x['entry'])}->{px(x['exit'])} {x['reason']} {x['R']:+.2f}R  ({iso(x['closed_ms'])})")
    else:
        print("track record: no closed trades yet")
    sh = s.get("shadow", [])
    if sh:
        done = [x for x in sh if x.get("result")]
        print(f"shadow (skipped/cancelled plan trades): {len(sh)} logged, {len(done)} resolved, total {sum(x['R'] for x in done):+.2f}R "
              f"= what my overrides cost (+) or saved (-)")
        for x in sh[-4:]:
            print(f"  {x['id']} {sym(x)} {x['side']} {px(x['entry'])} stop {px(x['stop'])} target {px(x['target'])}: "
                  f"{x.get('result') or 'open'}{'' if x.get('R') is None else f' {x[chr(82)]:+.2f}R'} | {x['why']}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--side", choices=["long", "short"], required=True)
    a.add_argument("--trigger", choices=["close_above", "close_below", "limit", "market"], required=True)
    a.add_argument("--tf", choices=["5m", "15m", "1h", "4h"], default="4h", help="candle for close_above/close_below")
    a.add_argument("--symbol", default="BTCUSDT", type=str.upper, choices=SYMBOLS)
    a.add_argument("--book", choices=["swing", "scalp"], default="swing")
    a.add_argument("--risk-pct", type=float, help=f"default: swing = account risk_pct, scalp = {SCALP_RISK}")
    a.add_argument("--level", type=float)
    a.add_argument("--stop", required=True, help="price, or low_since:ISO / high_since:ISO")
    a.add_argument("--target", type=float)
    a.add_argument("--target-r", type=float)
    a.add_argument("--expires")
    a.add_argument("--oco")
    a.add_argument("--max-hold-h", type=int, help="default 168 swing, 24 scalp")
    a.add_argument("--note", default="")
    a.add_argument("--arm-trigger", choices=["close_above", "close_below"], help="order only arms after this 4h close")
    a.add_argument("--arm-level", type=float)
    a.add_argument("--created", help="ISO time the order counts from (default now)")
    c = sub.add_parser("cancel")
    c.add_argument("id")
    cl = sub.add_parser("close")
    cl.add_argument("id")
    m = sub.add_parser("modify", help="tighten a position's stop (never widen) and/or change its target")
    m.add_argument("id")
    m.add_argument("--stop", type=float)
    m.add_argument("--target", type=float)
    sh = sub.add_parser("shadow", help="log a plan trade that was skipped or cancelled, to score the override")
    sh.add_argument("--id", required=True)
    sh.add_argument("--symbol", default="BTCUSDT", type=str.upper, choices=SYMBOLS)
    sh.add_argument("--side", choices=["long", "short"], required=True)
    sh.add_argument("--entry", type=float, required=True)
    sh.add_argument("--at", required=True, help="ISO time the plan would have entered")
    sh.add_argument("--stop", type=float, required=True)
    sh.add_argument("--target", type=float, required=True)
    sh.add_argument("--why", required=True, help="why it was skipped")
    j = sub.add_parser("journal", help="append an entry (heading with UTC time + price is added)")
    j.add_argument("text", help="entry body; literal \\n becomes a newline")
    args = ap.parse_args()

    s = load()
    events = process(s)
    if args.cmd == "add":
        if any(x["id"] == args.id for x in s["orders"] + s["positions"] + s["closed"]):
            sys.exit(f"id {args.id} already used")
        if not (args.target or args.target_r):
            sys.exit("give --target or --target-r")
        room = s["equity"] - floor(s)
        new_risk = s["equity"] * (args.risk_pct or (SCALP_RISK if args.book == "scalp" else s["risk_pct"])) / 100 * 1.2
        if room <= 0:
            sys.exit("refused: equity is at or below the max-drawdown / daily-loss floor")
        if open_risk(s) + new_risk > room / 2:
            sys.exit(f"refused: open+pending risk ${open_risk(s):,.0f} + this ${new_risk:,.0f} would exceed half the room "
                     f"above the drawdown floor (${room / 2:,.0f}); cancel something or size down with --risk-pct")
        if args.book == "scalp":
            if not args.note:
                sys.exit("a scalp needs --note: the thesis and what invalidates it")
            if len(s["positions"]) >= MAX_OPEN:
                sys.exit(f"refused: already {MAX_OPEN} open positions")
            day0 = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0).timestamp() * 1000
            lost = -sum(x["pnl"] for x in s["closed"] if x.get("book") == "scalp" and x["closed_ms"] >= day0)
            if lost >= s["equity"] * SCALP_DAY_STOP / 100:
                sys.exit(f"refused: scalp book is down ${lost:,.0f} today (limit {SCALP_DAY_STOP}%); no new scalps until 00:00 UTC")
        stop = float(args.stop) if args.stop.replace(".", "", 1).isdigit() else args.stop
        o = {"id": args.id, "symbol": args.symbol, "book": args.book, "side": args.side, "trigger": args.trigger,
             "tf": args.tf, "level": args.level, "stop": stop, "target": args.target, "target_r": args.target_r,
             "oco": args.oco, "note": args.note,
             "risk_pct": args.risk_pct or (SCALP_RISK if args.book == "scalp" else None),
             "max_hold_h": args.max_hold_h or (24 if args.book == "scalp" else 168),
             "created_ms": parse_time(args.created) if args.created else time.time() * 1000,
             "arm": {"trigger": args.arm_trigger, "level": args.arm_level} if args.arm_trigger else None,
             "expires_ms": parse_time(args.expires) if args.expires else
                           (time.time() * 1000 + 2 * 3600e3 if args.book == "scalp" and args.trigger != "market" else None)}  # lessons rule 12: every scalp order goes stale
        if args.trigger == "market":
            open_position(s, o, price_now(args.symbol), time.time() * 1000, events)
        else:
            if args.level is None:
                sys.exit("--level required for close_above / close_below / limit")
            s["orders"].append(o)
            events.append(f"PLACED {o['id']} [{o['book']}] {o['symbol']} {o['side'].upper()} on "
                          f"{'limit' if o['trigger'] == 'limit' else o['tf'] + ' ' + o['trigger']} {px(o['level'])}")
    elif args.cmd == "cancel":
        before = len(s["orders"])
        s["orders"] = [o for o in s["orders"] if o["id"] != args.id]
        events.append(f"CANCELLED {args.id}" if len(s["orders"]) < before else f"no pending order {args.id}")
    elif args.cmd == "close":
        p = next((x for x in s["positions"] if x["id"] == args.id), None)
        if p:
            close_position(s, p, price_now(sym(p)), time.time() * 1000, "manual", events)
        else:
            events.append(f"no open position {args.id}")
    elif args.cmd == "modify":
        p = next((x for x in s["positions"] if x["id"] == args.id), None)
        if not p:
            sys.exit(f"no open position {args.id}")
        side = 1 if p["side"] == "long" else -1
        now_px = price_now(sym(p))
        if args.stop is not None:
            if (args.stop - p["stop"]) * side < 0:
                sys.exit(f"refused: {px(args.stop)} would WIDEN the stop ({px(p['stop'])}); only tightening is allowed")
            if (now_px - args.stop) * side <= 0:
                sys.exit(f"refused: stop {px(args.stop)} is already through the current price {px(now_px)}; use close instead")
            p.setdefault("orig_stop", p["stop"])  # R stays measured against the original risk
            events.append(f"MODIFIED {p['id']}: stop {px(p['stop'])} -> {px(args.stop)}")
            p["stop"] = args.stop
        if args.target is not None:
            if (args.target - now_px) * side <= 0:
                sys.exit(f"refused: target {px(args.target)} is on the wrong side of the current price {px(now_px)}")
            events.append(f"MODIFIED {p['id']}: target {px(p['target'])} -> {px(args.target)}")
            p["target"] = args.target
    elif args.cmd == "shadow":
        s.setdefault("shadow", []).append({"id": args.id, "symbol": args.symbol, "side": args.side, "entry": args.entry,
                                           "at_ms": parse_time(args.at), "stop": args.stop, "target": args.target,
                                           "why": args.why, "result": None, "R": None})
        events.append(f"SHADOW logged {args.id}: {args.side} {args.symbol} @ {px(args.entry)} ({args.why})")
    elif args.cmd == "journal":
        body = args.text.replace("\\n", "\n").strip()
        head = f"## {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} — price {price_now():,.0f}"
        if not JOURNAL.exists():
            JOURNAL.write_text("# BTC paper desk journal\n")
        with JOURNAL.open("a") as f:
            f.write(f"\n{head}\n{body}\n")
        events.append(f"JOURNAL: appended {len(body.splitlines())} lines to {JOURNAL.name}")
    save(s)
    report(s, events)


if __name__ == "__main__":
    main()

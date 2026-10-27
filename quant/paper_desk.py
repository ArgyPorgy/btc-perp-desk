"""Paper trading desk for BTCUSDT perp (Binance prices). Every call is recorded and scored automatically.

  python3 paper_desk.py                 # process orders/positions against closed candles, print report
  python3 paper_desk.py add --id A --side long --trigger close_above --level 79732 --stop low_since:2026-10-24T12:00 \
        --target-r 2 --expires 2026-10-26T12:00 --oco G1 --note "reclaim long"
  python3 paper_desk.py add --id M --side short --trigger market --stop 80400 --target 78450   # enter now
  python3 paper_desk.py cancel A
  python3 paper_desk.py close POSITION_ID       # close an open position at the current price
  python3 paper_desk.py modify L1 --stop 79500  # tighten a stop (never widen) and/or move the target
  python3 paper_desk.py journal "- 1h: ...\n- DECISION: HOLD ..."   # append a dated entry to paper/journal.md

Rules: triggers 'close_above' / 'close_below' fill at the CLOSE of the first 4h candle (closed after the order was
placed) beyond the level. Positions are then managed on closed 1h candles: if stop and target are both touched in
the same hour the stop counts (conservative). Fees 0.05% per side. Size = risk % of equity / stop distance.
"""
import argparse
import json
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REST = "https://fapi.binance.com"
FEE = 0.0005
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


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def parse_time(s):
    return int(datetime.fromisoformat(s).replace(tzinfo=timezone.utc).timestamp() * 1000)


def klines(interval, start_ms):
    out, now = [], time.time() * 1000
    while True:
        k = get(f"{REST}/fapi/v1/klines?symbol=BTCUSDT&interval={interval}&limit=1500&startTime={int(start_ms)}")
        out += [{"t": x[0], "T": x[6], "o": float(x[1]), "h": float(x[2]), "l": float(x[3]), "c": float(x[4])} for x in k]
        if len(k) < 1500:
            break
        start_ms = k[-1][0] + 1
    return [b for b in out if b["T"] < now]  # closed candles only


def load():
    if STATE.exists():
        return json.loads(STATE.read_text())
    return {"start_equity": 10000.0, "equity": 10000.0, "risk_pct": 1.0, "orders": [], "positions": [], "closed": []}


def save(s):
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2))


def price_now():
    return float(get(f"{REST}/fapi/v1/ticker/price?symbol=BTCUSDT")["price"])


def resolve_stop(spec, side, upto_ms):
    if isinstance(spec, (int, float)):
        return float(spec)
    kind, since = spec.split(":", 1)
    bars = [b for b in klines("1h", parse_time(since)) if b["T"] <= upto_ms]
    if kind == "low_since":
        return min(b["l"] for b in bars) * 0.999
    if kind == "high_since":
        return max(b["h"] for b in bars) * 1.001
    raise ValueError(spec)


def open_position(s, o, entry, at_ms, events):
    side = 1 if o["side"] == "long" else -1
    stop = resolve_stop(o["stop"], side, at_ms)
    risk_px = (entry - stop) * side
    if risk_px <= entry * 0.0005:
        events.append(f"SKIPPED {o['id']}: stop {stop:,.1f} is on the wrong side of entry {entry:,.1f}")
        return
    target = o.get("target") or entry + side * o["target_r"] * risk_px
    qty = s["equity"] * s["risk_pct"] / 100 / risk_px
    p = {"id": o["id"], "side": o["side"], "entry": entry, "stop": stop, "target": target, "qty": qty,
         "opened_ms": at_ms, "note": o.get("note", ""), "max_hold_h": o.get("max_hold_h", 168)}
    s["positions"].append(p)
    events.append(f"ENTERED {p['side'].upper()} {p['id']} @ {entry:,.1f} | stop {stop:,.1f} | target {target:,.1f} | "
                  f"size {qty:.4f} BTC (risk ${s['equity'] * s['risk_pct'] / 100:,.0f}) | {iso(at_ms)}")
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
    events.append(f"CLOSED {p['side'].upper()} {p['id']} @ {exit_px:,.1f} ({reason}) | PnL ${pnl:+,.2f} = {pnl / risk_usd:+.2f}R | "
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
            for b in klines("4h", o["created_ms"] - 4 * 3600e3):
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
        for b in klines("4h", start - 4 * 3600e3):
            if b["T"] <= start:
                continue
            hit = (o["trigger"] == "close_above" and b["c"] > o["level"]) or (o["trigger"] == "close_below" and b["c"] < o["level"])
            if hit:
                s["orders"].remove(o)
                open_position(s, o, b["c"], b["T"] + 1, events)
                break
    # 2) open positions vs closed 1h candles
    for p in list(s["positions"]):
        side = 1 if p["side"] == "long" else -1
        for b in klines("1h", p["opened_ms"] - 3600e3):
            if b["t"] < p["opened_ms"]:
                continue
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
    return events


def report(s, events):
    px = price_now()
    print(f"BTCUSDT perp {px:,.1f}   |   {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    for e in events:
        print(f"EVENT: {e}")
    print(f"\nequity ${s['equity']:,.2f} (start ${s['start_equity']:,.0f}, risk {s['risk_pct']}% per trade)")
    print("open positions:" if s["positions"] else "open positions: none")
    for p in s["positions"]:
        side = 1 if p["side"] == "long" else -1
        u = (px - p["entry"]) * side * p["qty"]
        r = u / (abs(p["entry"] - p.get("orig_stop", p["stop"])) * p["qty"])
        print(f"  {p['id']} {p['side'].upper()} entry {p['entry']:,.1f} stop {p['stop']:,.1f} target {p['target']:,.1f} "
              f"| unrealised ${u:+,.2f} ({r:+.2f}R) | since {iso(p['opened_ms'])} | {p['note']}")
    print("pending orders:" if s["orders"] else "pending orders: none")
    for o in s["orders"]:
        tgt = f"target {o['target']:,.0f}" if o.get("target") else f"target {o['target_r']}R"
        arm = f"[{'armed' if o.get('armed_ms') else 'arms on 4h ' + o['arm']['trigger'].replace('_', ' ') + ' ' + format(o['arm']['level'], ',.0f')}] " if o.get("arm") else ""
        print(f"  {o['id']} {arm}{o['side'].upper()} on 4h {o['trigger'].replace('_', ' ')} {o['level']:,.1f} | stop {o['stop']} | {tgt}"
              f" | expires {iso(o['expires_ms']) if o.get('expires_ms') else 'never'}{' | OCO ' + o['oco'] if o.get('oco') else ''} | {o.get('note', '')}")
    c = s["closed"]
    if c:
        rs = [x["R"] for x in c]
        print(f"track record: {len(c)} closed | win {sum(r > 0 for r in rs) / len(rs):.0%} | total {sum(rs):+.2f}R | "
              f"avg {sum(rs) / len(rs):+.2f}R | PnL ${sum(x['pnl'] for x in c):+,.2f}")
        for x in c[-5:]:
            print(f"  {x['id']} {x['side']} {x['entry']:,.0f}->{x['exit']:,.0f} {x['reason']} {x['R']:+.2f}R  ({iso(x['closed_ms'])})")
    else:
        print("track record: no closed trades yet")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd")
    a = sub.add_parser("add")
    a.add_argument("--id", required=True)
    a.add_argument("--side", choices=["long", "short"], required=True)
    a.add_argument("--trigger", choices=["close_above", "close_below", "market"], required=True)
    a.add_argument("--level", type=float)
    a.add_argument("--stop", required=True, help="price, or low_since:ISO / high_since:ISO")
    a.add_argument("--target", type=float)
    a.add_argument("--target-r", type=float)
    a.add_argument("--expires")
    a.add_argument("--oco")
    a.add_argument("--max-hold-h", type=int, default=168)
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
        stop = float(args.stop) if args.stop.replace(".", "", 1).isdigit() else args.stop
        o = {"id": args.id, "side": args.side, "trigger": args.trigger, "level": args.level, "stop": stop,
             "target": args.target, "target_r": args.target_r, "oco": args.oco, "note": args.note,
             "max_hold_h": args.max_hold_h,
             "created_ms": parse_time(args.created) if args.created else time.time() * 1000,
             "arm": {"trigger": args.arm_trigger, "level": args.arm_level} if args.arm_trigger else None,
             "expires_ms": parse_time(args.expires) if args.expires else None}
        if args.trigger == "market":
            open_position(s, o, price_now(), time.time() * 1000, events)
        else:
            if args.level is None:
                sys.exit("--level required for close_above / close_below")
            s["orders"].append(o)
            events.append(f"PLACED {o['id']} {o['side'].upper()} on 4h {o['trigger']} {o['level']:,.1f}")
    elif args.cmd == "cancel":
        before = len(s["orders"])
        s["orders"] = [o for o in s["orders"] if o["id"] != args.id]
        events.append(f"CANCELLED {args.id}" if len(s["orders"]) < before else f"no pending order {args.id}")
    elif args.cmd == "close":
        p = next((x for x in s["positions"] if x["id"] == args.id), None)
        if p:
            close_position(s, p, price_now(), time.time() * 1000, "manual", events)
        else:
            events.append(f"no open position {args.id}")
    elif args.cmd == "modify":
        p = next((x for x in s["positions"] if x["id"] == args.id), None)
        if not p:
            sys.exit(f"no open position {args.id}")
        side = 1 if p["side"] == "long" else -1
        px = price_now()
        if args.stop is not None:
            if (args.stop - p["stop"]) * side < 0:
                sys.exit(f"refused: {args.stop:,.1f} would WIDEN the stop ({p['stop']:,.1f}); only tightening is allowed")
            if (px - args.stop) * side <= 0:
                sys.exit(f"refused: stop {args.stop:,.1f} is already through the current price {px:,.1f}; use close instead")
            p.setdefault("orig_stop", p["stop"])  # R stays measured against the original risk
            events.append(f"MODIFIED {p['id']}: stop {p['stop']:,.1f} -> {args.stop:,.1f}")
            p["stop"] = args.stop
        if args.target is not None:
            if (args.target - px) * side <= 0:
                sys.exit(f"refused: target {args.target:,.1f} is on the wrong side of the current price {px:,.1f}")
            events.append(f"MODIFIED {p['id']}: target {p['target']:,.1f} -> {args.target:,.1f}")
            p["target"] = args.target
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

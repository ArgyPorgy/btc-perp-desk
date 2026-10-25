"""Opening Range Breakout + 200 EMA + retest backtester (5-minute bars).

Rules, as exact as the video allows:
 1. Opening range (OR) = high/low of the first 15 minutes after the session open (three 5-min bars).
 2. From then on, the first 5-min candle that CLOSES outside the range sets the day's direction.
 3. Trend filter: longs only if that close is above the 200-period EMA (5-min), shorts only if below.
    If the filter disagrees, no trade that day.
 4. Entry: limit order at the broken level (OR high for longs, OR low for shorts) = the "flip zone" retest.
    If price reaches the target before retesting, or no retest by the entry cutoff, no trade.
 5. Stop "below the zone": default = OR midpoint (variant: other side of the range).
 6. Target "next obvious level": default = 2R (variants: 1R/1.5R/3R, or previous session's high/low).
 7. Anything still open at session end is closed at market. One trade per day max.
 Conservative fills: stop wins if stop and target are hit in the same bar; on the entry bar only the stop can hit.
 Costs (Hyperliquid-style): limit entry/target 0.015%, stop or end-of-day exit 0.045% + 0.02% slippage.
"""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

import numpy as np

FEE_MAKER, FEE_TAKER, SLIP = 0.00015, 0.00045, 0.0002


def load(path):
    a = np.loadtxt(path, delimiter=",")
    return {"t": (a[:, 0] // 1000).astype(np.int64), "o": a[:, 1], "h": a[:, 2], "l": a[:, 3], "c": a[:, 4]}


def ema(x, n=200):
    out = np.empty_like(x)
    k = 2 / (n + 1)
    out[0] = x[0]
    for i in range(1, len(x)):
        out[i] = x[i] * k + out[i - 1] * (1 - k)
    return out


def run(d, tz="America/New_York", open_hm=(9, 30), session_min=390, or_min=15, cutoff_min=180,
        stop_mode="mid", target="2R", use_ema=True, use_retest=True, weekdays_only=True,
        start=date(2025, 10, 22), end=date(2026, 10, 21)):
    t, o, h, l, c = d["t"], d["o"], d["h"], d["l"], d["c"]
    e = ema(c)
    zone = ZoneInfo(tz)
    trades = []
    prev_hi = prev_lo = None
    day = start
    while day <= end:
        if weekdays_only and day.weekday() >= 5:
            day += timedelta(days=1)
            continue
        op = int(datetime.combine(day, time(*open_hm), tzinfo=zone).timestamp())
        i0 = np.searchsorted(t, op)
        i_or = np.searchsorted(t, op + or_min * 60)
        i_end = np.searchsorted(t, op + session_min * 60)
        i_cut = np.searchsorted(t, op + cutoff_min * 60)
        if i_or - i0 < or_min // 5 or i_end - i_or < 6:
            day += timedelta(days=1)
            continue
        ORH, ORL = h[i0:i_or].max(), l[i0:i_or].min()
        rng = ORH - ORL
        sess_hi, sess_lo = h[i0:i_end].max(), l[i0:i_end].min()
        trade = None
        # 2. first close outside the range
        for j in range(i_or, i_cut):
            side = 1 if c[j] > ORH else -1 if c[j] < ORL else 0
            if side == 0:
                continue
            if use_ema and (c[j] - e[j]) * side <= 0:
                break  # trend filter disagrees -> no trade today
            level = ORH if side == 1 else ORL
            if stop_mode == "mid":
                stop = (ORH + ORL) / 2
            else:
                stop = ORL if side == 1 else ORH
            if not use_retest:
                entry, k0 = c[j], j + 1
            else:
                entry, k0 = level, None
            risk = abs(entry - stop)
            if risk <= 0:
                break
            if target == "level":
                lvl = prev_hi if side == 1 else prev_lo
                tp = lvl if lvl is not None and (lvl - entry) * side >= 1.0 * risk else entry + side * 2 * risk
            else:
                tp = entry + side * float(target[:-1]) * risk
            # 4. wait for the retest
            if use_retest:
                for k in range(j + 1, i_cut):
                    ran_away = (h[k] >= tp) if side == 1 else (l[k] <= tp)
                    touched = (l[k] <= level) if side == 1 else (h[k] >= level)
                    if touched:
                        k0 = k
                        break
                    if ran_away:
                        break
                if k0 is None:
                    break
                # entry bar: only the stop can trigger
                if (l[k0] <= stop) if side == 1 else (h[k0] >= stop):
                    trade = (day, side, entry, stop, tp, stop, "stop")
                    break
                k0 += 1
            # 5-7. manage the trade
            for k in range(k0, i_end):
                hit_stop = (l[k] <= stop) if side == 1 else (h[k] >= stop)
                hit_tp = (h[k] >= tp) if side == 1 else (l[k] <= tp)
                if hit_stop:
                    trade = (day, side, entry, stop, tp, stop, "stop")
                    break
                if hit_tp:
                    trade = (day, side, entry, stop, tp, tp, "target")
                    break
            else:
                trade = (day, side, entry, stop, tp, c[i_end - 1], "eod")
            break
        if trade:
            dd, side, en, st, tp, ex, how = trade
            risk = abs(en - st)
            cost = en * FEE_MAKER + ex * (FEE_MAKER if how == "target" else FEE_TAKER + SLIP)
            if not use_retest:
                cost += en * (FEE_TAKER + SLIP - FEE_MAKER)
            r = ((ex - en) * side - cost) / risk
            trades.append({"day": dd, "side": side, "entry": en, "stop": st, "tp": tp, "exit": ex, "how": how,
                           "R": r, "R_gross": (ex - en) * side / risk, "risk_pct": risk / en * 100})
        prev_hi, prev_lo = sess_hi, sess_lo
        day += timedelta(days=1)
    return trades


def stats(trades):
    if not trades:
        return dict(n=0, win=0, avgR=0, totR=0, grossR=0, pf=0, maxdd=0, ret1=0, med_risk=0)
    R = np.array([x["R"] for x in trades])
    eq = np.cumsum(R)
    dd = (np.maximum.accumulate(np.concatenate([[0], eq])) - np.concatenate([[0], eq])).max()
    wins, losses = R[R > 0].sum(), -R[R < 0].sum()
    bal = 1.0
    for r in R:
        bal *= 1 + 0.01 * r  # risk 1% of account per trade
    G = np.array([x["R_gross"] for x in trades])
    return dict(n=len(R), win=np.mean(R > 0), avgR=R.mean(), totR=R.sum(), grossR=G.mean(),
                pf=wins / losses if losses else np.inf, maxdd=dd, ret1=bal - 1,
                med_risk=np.median([x["risk_pct"] for x in trades]))


def fmt(name, s):
    return (f"  {name:<40} {s['n']:>4} {s['win']:6.1%} {s['avgR']:+7.3f} {s['totR']:+7.1f} "
            f"{s['pf']:5.2f} {s['maxdd']:6.1f} {s['ret1']:+8.1%} {s['grossR']:+8.3f} {s['med_risk']:6.2f}%")


HEADER = (f"  {'setup':<40} {'trades':>4} {'win%':>6} {'avg R':>7} {'tot R':>7} {'PF':>5} {'maxDD':>6} "
          f"{'@1%risk':>8} {'gross R':>8} {'stop%':>7}")

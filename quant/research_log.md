# Research log
Every idea tested, positive or negative. A setup becomes tradable only with average R >= 0 and n >= 15 after fees.

## 2026-10-25 — Are round thousands sticky? (`round_level_test.py`)
Approach a level within 7bp, then either trade 7bp through it or fall back 2.4%. BTC perp 1h, price > 20k.
Round thousands passed through **95.6%** of the time (n=1,554), vs 95.3% / 92.5% / 94.4% at x,250 / x,500 / x,750 controls. From above: 96.1% vs 93.5–95.1%.
→ **Not sticky; if anything stops sit just beyond them.** Don't pull targets in front of round numbers.

## 2026-10-25 — Holding through FOMC (`event_study.py`)
58 statements (Sep 2019 – Sep 2026) vs Tue–Thu baselines at the same UTC hour.
- The move from the statement hour to +3h is **2.5× normal** (median 1.16% vs 0.47%).
- 24h move is 1.34× normal.
- P(a 1.9% stop is touched within 24h): 52% vs 47%.
- Direction 24h after: up 48% (±7%), so no drift.

→ Holding with a stop is fine. No new entries in the 2h before the release (vol burst, slippage).

## Earlier (2026-10-24)
- `sweep_test.py`: 4h sweep of the 20-day low that closes back above it, daily uptrend. 44 events; 2R long wins 38.6% vs 33% random; avg +0.03R; halves −0.21R / +0.27R. Marginal.
- `trigger_rules.py`: reclaim long 19 trades, 2R +0.23R; continuation short 9 trades, 1R +0.44R (n < 15, so idea only).
- `breakdown_test.py`: 4h close below the 20-day low in a daily uptrend. 30 events; only 23% lower 72h later; 63% reclaimed within 24h. Breakdowns mostly fail.

## Backlog (highest expected value first)
1. Post-release reaction trades: first 15m/1h candle after CPI/FOMC, fade vs follow, using calendar timestamps.
2. Funding extremes (top/bottom 5%) + OI change → 24–72h forward returns.
3. Failed breakouts at prior-day VAH/VAL (auction failure) on 1h.
4. Liquidation cascades: needs our own forceOrder history (start logging it).
5. Session opens (Asia/London/NY) × weekly VWAP side.

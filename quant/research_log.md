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

## 2026-10-26: Scalping vs holding (prompted by L1's three bounces)
L1 bounced from the entry zone repeatedly: +1.91R, +0.84R, +0.93R, +0.81R, +1.22R, +1.64R and +1.19R from entry, while never hitting its stop. In hindsight, "book ~1.5R and rebuy at the entry" would have caught 2 wins. Tested whether that generalises:
- **Range-edge fades on 1h** (`range_scalp_test.py`): wick into the outer 10% of a 48/72/120h range, then close back inside. Fade it with 1R / 1.5R / 2R / mid / opposite-edge targets, stop buffers of 0.2/0.5/1.0 ATR, re-entry allowed, split by efficiency-ratio regime. **Negative everywhere:** −0.06 to −0.23R/trade (n≈1,000–4,000), maker fees included. Win rates are at or below random: range edges get swept, not respected. Worst in the "range" regime.
- **Prior-day high/low sweep scalps** (`daily_sweep_test.py`, ~200 a year): −0.18 to +0.01R/trade. No edge after fees.
- **Take profit + re-enter at the entry on the sweep setup** (`reentry_test.py`): on the narrow L1 version (n=44), re-entries look slightly better (+0.12R at 1R) but ±0.2R. On the broader samples (n=90 20-day, n=153 10-day), re-entries **lower** R/event at every target. Price returning to the entry after a bounce means the bounce failed.
- **Hold one shot (the same file), long sweeps of the N-day low with no trend filter: positive.** 20-day/2R: +0.17R (n=90, halves +0.04/+0.30). 10-day/1.5R: +0.14R (n=153, halves +0.26/+0.02). The daily-trend filter doesn't help.
- **Short mirrors at 10/20-day highs: clearly negative** (−0.13 to −0.39R, n=30–190). BTC failed breakdowns get bought; failed breakouts do not reliably reverse.

→ **Desk change:** tradable setups are now S10 (10-day-low sweep, 1.5R) and S20 (20-day-low sweep, 2R), long only, any daily trend, one-shot hold. That's ~3x more opportunities than the trend-filtered version. `setup_scan.py` flags them live. No mechanical scalping: it loses after costs.

## Backlog (highest expected value first)
1. Post-release reaction trades: first 15m/1h candle after CPI/FOMC, fade vs follow, using calendar timestamps.
2. Funding extremes (top/bottom 5%) + OI change → 24–72h forward returns.
3. Failed breakouts at prior-day VAH/VAL (auction failure) on 1h.
4. Liquidation cascades: needs our own forceOrder history (start logging it).
5. Session opens (Asia/London/NY) × weekly VWAP side.

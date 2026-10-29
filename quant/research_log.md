# Research log
Every idea tested, positive or negative. A setup becomes tradable only with average R >= 0, n >= 15, both halves >= 0
and t >= 1.5 (avg R / standard error), after fees. (t was added 2026-10-28: random-walk data passed the rest.)

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

## 2026-10-27: Breakeven stop vs one-shot hold (L1 at +1.5R the day before FOMC)
`breakeven_test.py`: S10/S20 events, move the stop to entry + fees once a closed 1h candle is at +0.5R / +1R / +1.5R.
- S20/2R (n=90): hold +0.163R. BE at +0.5R −0.054R, at +1R +0.034R, at +1.5R +0.137R. Among trades that reached +1.5R (n=21): hold +1.62R (target hit 86%) vs BE +1.50R.
- S10/1.5R (n=153): hold +0.126R. BE at +0.5R +0.038R, at +1R +0.111R. Among trades that reached +1R (n=39): hold +1.32R (95% hit target) vs BE +1.26R.
- Breakeven cuts R at every trigger. Once a sweep trade is up 1R+, it usually finishes; BE stops get tagged on normal retests. Conditional samples are small (n=21–45).

→ **No change:** keep the one-shot hold with the original stop. No breakeven trailing.

## 2026-10-28: HOOD "oversold" long (`hood_oversold_test.py`)
HOODUSDT perp 1h since Feb 2026 (267 days). Now 87.8, −8.9% vs the 1h EMA200, after a Q3 earnings miss. Price sits that stretched only 1.6% of the time.
- **≥8% below the EMA (12 episodes):** up 7 days later 82% (median +3.5%). +9.3% (to 96) came before −4% in 40% of 10, against 30% for a random walk; before −1.5%, 27% of 11 against 14%.
- **≥6% below (23 episodes):** weaker. Up 55–64%, and the odds of reaching 96 are close to random (17% vs 14%, 33% vs 30%).

→ Leans toward a bounce, but n=10–23 from one stock in one year, and the uncertainty (±15%) covers zero edge. This episode is also earnings-driven: after earnings misses, stocks tend to keep drifting down for weeks (post-earnings drift), which most of these episodes didn't have. **Not tradable by the desk rule (n < 15 at the tested threshold). Idea only.**

## 2026-10-28: HOOD gap-downs, full Nasdaq history since the 2021 IPO (`hood_gap_test.py`)
1,318 daily bars from Yahoo Finance; 31 gap-downs of 5% or more. Earnings missed 2026-10-27 after the close: regular close 94.56, after hours 87.8 → about −7% gap expected at the Oct 28 open, with HOOD already −10% below its 50-day EMA.
- **All gap-downs (n=31):** long at the open is +0.11 to +0.19R across −4% to −10% stops and 9.3% / 15% targets, but the halves are mixed (−0.36 to +0.64). The gap fills (reaches the prior close) within 10 days 77% of the time.
- **Gap-down while already >8% below the 50-day EMA (n=11):** +0.36 to +0.83R in every stop/target combination, with both halves positive. The gap day closed above its open 73% of the time (median +7.1%), and the 10-day median is +23.9%. With an −8% stop and a +9.3% target: 64% wins, +0.36R ±0.31.
- **Earnings-miss gaps only (n=8):** weaker. The gap filled within 10 days only 38% of the time (post-earnings drift). Earnings gaps that were also stretched (n=3): 2 wins, 1 loss.
- **A −4% stop is below HOOD's daily range (ATR ~5.6%).** Several winners first hit −4%, then ran +25–36%. Size stops to volatility (−8%).

→ The stretched-gap long is promising but n=11 (<15), so it's an idea, not desk-tradable yet. Track the Oct 28 outcome as an out-of-sample case.

## 2026-10-28: Short-side playbook (`short_test.py`), prompted by "play both sides"
The desk was long-only because the shorts tested so far lost money, but those tests were narrow: breakdowns only inside
daily uptrends, and high-sweep fades with no regime split. A 79k breakdown in a falling market was never tested.
`short_test.py` tests, each split by daily regime (all / below EMA200 / below EMA50) with 1-3R targets after fees:
failed rallies at the 10/20-day high (FR), first 4h close below the 10/20-day low (BD), the first retest of that broken
level within 48h (RT), and crowded longs (funding top 5% of 90 days + price up 5% in 72h, CROWD).
- **Control on a pure random walk:** every setup is ~-0.1R (fees), as it should be, so there's no lookahead in the code. But
  FR10 passed the old desk rule on random data (+0.07R, n=152, t=0.6). **The rule now also needs t >= 1.5** (avg R
  over its standard error) for any new setup. Note S10 (+0.14R, halves +0.26 / +0.02) is borderline by that bar too.
- **Real BTC results** (59,852 hourly bars, 2019-12-31 to 2026-10-28; Binance's archive starts there):
  - **Breakdowns work in a daily bear market.** B20 (first 4h close below the 20-day low, daily < EMA200, n=33):
    +0.25 / +0.32 / +0.37 / +0.37R at 1 / 1.5 / 2 / 3R, both halves positive at every target; 1.5R passes (t 1.6).
    R10 (first 1h retest of a broken 10-day low within 48h, bear, n=46): +0.27 / +0.41 / +0.29R at 1.5 / 2 / 3R;
    2R passes (+0.41R, halves +0.22 / +0.59, t 1.8). BD10 bear 1R +0.17R (t 1.3) points the same way.
  - **The same breakdowns in all regimes are ~0R** (BD20 all −0.04 to +0.10R; BD10 2R −0.14R): in uptrends they get
    bought, as found earlier.
  - **Failed rallies lose in every regime** (FR10 −0.27 to −0.36R, t −3; in bear −0.14 to −0.40R).
  - **Crowded-funding shorts lose badly** (CROWD −0.24 to −0.54R, t −2 to −4, n=66): when funding is top-5% and price
    is up 5% in 3 days, the rally usually keeps going. That is a long-momentum idea for the backlog, not a short.
  - Caveat: 84 combinations were tested; at t >= 1.5 a few could pass by luck. What makes B20/R10 credible is that the
    whole bear-regime breakdown family is positive across targets and halves, while the bull-regime one is flat.

→ **Desk change:** the desk trades both directions. B20 (1.5R) and R10 (2R) shorts are live in `setup_scan.py`, only
  while the last daily close is below the daily EMA200 (76.4k today, so they are off now: a 79k break today is a
  bull-regime breakdown, ~0R). Standard 1% risk, like S10/S20.

## 2026-10-29: Do the BTC setups carry over to ETH and HYPE? (`market_setups_test.py`)
Same rules on each market's own Binance perp 1h history (ETH 2020-2026, 59.8k bars; HYPE since its 2025-05-30 listing, 12.4k bars):
| setup | BTC | ETH | HYPE |
|---|---|---|---|
| S10 long 1.5R | +0.09R n=143 t 0.9 (halves +0.20 / −0.01) | −0.06R n=119 | −0.32R n=34 |
| S20 long 2R | +0.14R n=85 t 0.9 | −0.28R n=70 | +0.03R n=21 |
| B20 short 1.5R (bear) | **+0.32R n=35 t 1.6, PASS** | +0.21R n=39 t 1.0 | n=4 |
| R10 short 2R (bear) | +0.27R n=44 t 1.2 | +0.26R n=40 t 1.1 (halves +0.73 / −0.21) | n=3 |
- **Nothing passes on ETH or HYPE.** The low-sweep longs lose on both: the "dips below the low get bought" effect is a BTC thing. The desk does not trade these setups on ETH/HYPE; `setup_scan.py SYMBOL` shows them for context only.
- **R10 is fragile.** Checking the bear regime at the breakdown (here) instead of at the retest (`short_test.py`) moves it from +0.41R t 1.8 to +0.27R t 1.2. A real edge shouldn't swing that much on a detail → **demoted to idea, not traded.** B20 holds in both versions (+0.32R).
- **S10/S20 on 2020+ data** (the archive starts 2019-12-31) are +0.09R / +0.14R at t 0.9: positive, but they would not pass the t >= 1.5 bar if proposed today. Kept (grandfathered, and L1 worked), flagged marginal. Testing filters that might sharpen them is backlog #1.

## 2026-10-29: Scalp book (desk change, prompted by "you won't pass with swings only")
The account needs +9%; it is at +1.88% after one trade in four days. The tested swing setups fire ~2x a month at
+0.1-0.3R: months to the target. Mechanical scalps tested so far lost (range fades, prior-day sweeps), but those were
blind rules; discretionary reads that combine structure, flow (taker delta, OI, funding), gamma and news are untested.
→ **Second book, `--book scalp`:** long or short on BTC/ETH/HYPE, 0.5% risk, written thesis + invalidation per trade,
  managed on 5m candles, 24h max hold, max 3 open, scalp book stops for the day at -1.5%. Scored separately from the
  swing book. Review after 20 scalps: if the scalp book is net negative, cut it or change it.

## 2026-10-29: Testing the first scalps after placing them (`scalp_tests.py`), prompted by "are these backtested?"
They weren't. Closest tests the data allows:
- **BTC release-window range break** (X2/X3): first 15m close outside the 2h pre-12:30 range, stop 0.45% inside, 1.5R.
  **−0.22R/trade, n=1,526, t −6.9**, both halves −0.22; 13:30 anchor the same; Asia control −0.20R. Breakouts of a
  short range with a tight stop get faded back inside. → X2/X3 **cancelled** at 12:24, before the release.
- **Impulse pullback** (X1): after a 1h candle of >= 3 ATR, limit at 25% retrace, stop under the impulse midpoint, 2R.
  Up-impulse longs: BTC −0.14R (n=147), ETH −0.13R (n=107), **HYPE +0.83R (n=8)**. Down-impulse shorts: BTC +0.15R
  (n=123, t 1.1, idea), ETH −0.05R. → X1 kept at 0.5% as a **low-confidence** trade: pooled evidence is negative;
  only HYPE's own 8 cases (plus a structural catalyst) favour it.
→ **Rule for the scalp book from now on:** test the pattern before placing it, at least roughly; place untested reads
  only when the pattern has no history to test, and say so.

## 2026-10-29: @MuroCrypto's HYPE daily flip, generalised (`sr_flip_test.py`), prompted by the user's tweet
His call: HYPE's June-July range top (~75.7) flipped to support after the August breakout, retested Oct 26 with the rising
daily MA underneath; +17% in 3 days. Rule: daily pivot high (+-5), close >= 1% above it, first retest within 2% that
closes no more than 1% below, close above a RISING SMA100; stop 1 ATR under the level; 2R/3R; 30-bar exit.
| | 1D SMA100 2R | 1D SMA100 3R | 1D no SMA 2R | 4H SMA100 2R |
|---|---|---|---|---|
| BTC | **+0.32R n=46 t 1.5** (halves +0.30/+0.34) | +0.35R | +0.18R n=81 | +0.01R n=465 |
| ETH | +0.25R n=45 (halves +0.43/+0.08) | **+0.38R t 1.5** | +0.26R n=77 | −0.04R n=380 |
| HYPE | +0.60R n=9 | +0.79R n=9 | +0.12R n=14 | −0.10R n=69 |
- **The timeframe is the edge**: daily works on all three, 4h is flat. The rising-SMA filter helps on BTC.
- Live check: the scanner version fires on HYPE at the Oct 24 close (76.65, level 73.0, stop 69.2, 2R 91.57), and 91.57
  traded on Oct 29: +2R.
→ **New swing setup D1F**: daily S/R flip retest above a rising SMA100, long, 2R, BTC/ETH/HYPE, 0.5% risk. In
  `setup_scan.py` (`d1_flips`). Next: the short mirror (broken support retested from below under a falling SMA100).

## Backlog (highest expected value first)
1. Sharpen S10/S20 (t 0.9 on 2020+): volume on the sweep candle, funding/OI state, distance swept, session.
2. Post-release reaction trades: first 15m/1h candle after CPI/FOMC, fade vs follow, using calendar timestamps.
3. Crowded-rally LONGS: CROWD shorts lost −0.54R at 2R (t −3.9), so test the long side: funding top 5% + up 5% in 72h → long, with OI change once we log it.
4. Failed breakouts at prior-day VAH/VAL (auction failure) on 1h.
5. Liquidation cascades: needs our own forceOrder history (start logging it).
6. Session opens (Asia/London/NY) × weekly VWAP side.
7. Breakout longs: 4h close above the prior 10/20-day high (short fades of highs tested −0.13 to −0.39R, so the breakout side may carry the edge).

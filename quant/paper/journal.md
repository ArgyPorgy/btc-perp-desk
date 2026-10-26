# BTC paper desk journal

## 2026-10-24 16:00 UTC — price 79,745
- 1h: below EMA200 (82.0k), structure down, below value; −8k BTC taker delta (12h).
- 4h: below EMA50/200 (~82.0k); candle wicked to 79,179 under the 20-day low (79,732) and CLOSED 79,762 back above → breakdown not confirmed (sweep).
- 1d: above EMA200 (76.2k), below EMA50 (80.8k); inside daily bull FVG 77.2k–80.8k.
- Positioning: funding ~0.001%, OI +2.5% 24h (new shorts), near-term gamma short below flip ~80.35k; put wall 81k, call wall 82k.
- DECISION: ENTER LONG L1 at market. Stop 79,099 (under the sweep wick), target 2R (~81.0k). Risk 1%.
- Evidence: 44 sweeps since 2019 in daily uptrends — 2R long win 38.6% vs 33% random, +0.03R avg (marginal; halves −0.21R / +0.27R); 72h later up 61%.
- Orders: cancelled A1 (reclaim long, redundant). Kept B1 (continuation short: arms on a 4h close < 79,732, fires on a 4h close < 78,450).

## 2026-10-24 22:55 UTC — price 80,550
- 1h: below EMA50/200 (81.05k/81.9k), last CHoCH down, below value (VAL 80.96k); 12h delta −1.3k BTC, but price above session VWAP (80.29k).
- 4h: below EMA50/200 (~81.9k); 20-day-low sweep held — swing low 79,732 intact, back inside value (VAL 80.37k).
- 1d: above EMA200 (76.2k), just under EMA50 (80.8k); still inside daily bull FVG 77.2k–80.8k.
- Positioning: funding 0.008%, OI +3.7% 24h, basis −5bp; short gamma ≤30d, flip ~80.65k (price just below); put wall 80k, call wall 82k.
- DECISION: HOLD L1 (long 79,752, +1.22R unrealised). Stop 79,099 / target 81,057 unchanged — running the tested 2R plan as specified (44 samples, +0.03R, marginal); not tightening to avoid altering the tested exit.
- Orders: none changed. B1 (continuation short, OCO G1) remains pending, unarmed.

## 2026-10-25 07:50 UTC — price 80,660
- 1h: below EMA50/200 (80.96k/81.8k), last CHoCH down; rejected 81.0k three times overnight (high 80,999.9, 9 short of target), dropped to 80.39k at 06:00; below value (VAL 80.72k); 12h delta +1.3k BTC.
- 4h: below EMA50/200 (~81.8k/81.9k); swing low 79,732 holds; inside value (VAL 80.37k); 12-bar delta −4.7k BTC.
- 1d: above EMA200 (76.3k), just under EMA50 (80.8k); inside daily bull FVG 77.2k–80.8k.
- Positioning: funding 0.006%, OI +0.3% 24h / −0.3% 7d, basis −5bp; short gamma ≤30d, flip ~81.0k (overhead), put wall 80.5k, call wall 82k.
- DECISION: HOLD L1 (long 79,752, +1.39R unrealised). Stop 79,099 / target 81,057 unchanged; I'm keeping the exit as tested (44 samples, +0.03R, marginal). MC zero-drift: 61% touch 81k within 24h.
- Orders: none changed. B1 (continuation short, OCO G1) still pending and unarmed.

## 2026-10-25 07:52 UTC — price 80,670
- 1h: below EMA50/200 (80.96k/81.8k), last CHoCH down; in 79.2k–81.0k range, below value (VAL 80.72k), just under session VWAP 80.74k; 12h delta +1.3k BTC.
- 4h: below EMA50/200 (~81.8k/81.9k); swing low 79,732 holds; inside value (VAL 80.37k); 12-bar delta −4.7k BTC.
- 1d: above EMA200 (76.3k), just under EMA50 (80.8k); inside daily bull FVG 77.2k–80.8k.
- Positioning: funding 0.006%, OI +0.3% 24h / −0.3% 7d, basis −4.5bp; short gamma ≤30d, flip ~81.05k (overhead), put wall 80.5k, call wall 82k.
- DECISION: HOLD L1 (long 79,752, +1.41R unrealised). Stop 79,099 / target 81,057 unchanged (tested exit, 44 samples, +0.03R, marginal). Re-run ~2 min after previous entry; nothing material changed. MC zero-drift: 61% touch 81k in 24h.
- Orders: none changed. B1 (continuation short, OCO G1) pending, unarmed.

## 2026-10-25 19:59 UTC — price 80,530
- 1h: below EMA50/200 (80.8k/81.7k), last CHoCH down; 79.2k-81.0k range, 81.0k rejected 3x (high 80,999.9, 57 short of target); 12h delta +0.3k BTC.
- 4h: below EMA50/200 (~81.6k/81.9k); sweep low 79,179 / swing low 79,732 intact; inside value (VAL 80.37k); 12-bar delta -5.2k BTC.
- 1d: above EMA200 (76.3k), just under EMA50 (80.8k); inside daily bull FVG 77.2k-80.8k.
- Positioning: funding 0.005-0.008%, OI -2.5% 24h (longs leaving), basis -3bp; price sitting on the gamma flip (~80.5k), put wall 80k, call wall 82k.
- News (new terminal): US-Iran war day 240, Trump 'deal or finish it off' (escalation tail risk, oil up); FOMC Wed 18:00 UTC (hold 4.00% expected), PCE+GDP Thu 12:30, BOJ Fri 02:30, US midterms Nov 3. No top-impact US headline has moved BTC >0.3% today.
- Tests run: round_level_test.py: round thousands are NOT sticky (pass-through 95.6% vs 94.2% controls, n=1,554) -> no reason to pull the target under 81k. event_study.py: FOMC +4h moves are 2.5x normal, but P(1.9% stop hit in 24h) only 52% vs 47% and no drift (48% up, n=58) -> holding through FOMC with a stop is fine; no NEW entries in the 2h before top-impact releases.
- DECISION: HOLD L1 (long 79,752, +1.2R). Stop 79,099 / target 81,057 unchanged (tested exit; MC zero-drift 72% touch 81k in 24h). B1 unchanged (pending, unarmed, expires 2026-10-26 16:00).
- Desk: added paper_desk.py modify (tighten-only) and journal commands; news feed + calendar now in the dashboard and in dashboard/news.py.

## 2026-10-25 23:36 UTC — price 80,260
- 1h: below EMA50/200 (80.7k/81.6k), below value (VAL 80.6k) and session VWAP; 12h delta -1.3k BTC. Pulled back from 81.0k to 80.2k.
- 4h: below EMA50/200 (~81.6k/81.9k); swing low 79,732 and sweep low 79,179 intact; just below value (VAL 80.37k); 12-bar delta -4.3k BTC.
- 1d: above EMA200 (76.3k), under EMA50 (80.8k); still inside daily bull FVG 77.2k-80.8k.
- Positioning: funding 0.002% (cooling), OI -2.6% 24h, basis -3bp. Near-term gamma flipped NEGATIVE (-10M/1%), price just under the flip 80.4k -> moves can extend both ways; put wall 80k, call wall 82k.
- News: US-Iran escalation risk building (Semafor 'new threats could push US and Iran toward war', BTC -0.69% in the following hour), oil firm; US-Canada tariff relief. FOMC Wed 18:00 UTC, PCE/GDP Thu 12:30.
- DECISION: HOLD L1 (long 79,752, +0.7R at 80,224). Stop 79,099 / target 81,057 unchanged: thesis (20-day-low sweep held) not invalidated; zero-drift odds of target before stop from here ~57%; no tested reason to tighten. No new orders (one-position limit). B1 unchanged (expires 2026-10-26 16:00).
- Desk: tightened news 'sanctions' rule (false geo flag); tests 17/17.

## 2026-10-26 14:02 UTC — price 79,683
- 1h: below EMA50/200 (80.4k/81.4k), structure down, below value and session/weekly VWAP (79.93k); but 12h taker delta +3.1k BTC (buyers absorbing the dip).
- 4h: 04:00 close 79,565 broke the 79,732 swing low -> CHoCH down; B1 ARMED. Last close 79,713. Sweep low 79,179 (= L1 invalidation) still intact.
- 1d: above EMA200 (76.3k), below EMA50 (80.7k); lower edge of daily bull FVG 77.2k-80.8k.
- Positioning: funding 0.008% (up), OI +1.0% 24h (shorts adding into the dip), basis -3.5bp; near-term gamma -21M/1% (amplifying), price under the flip ~80.1k; 80k is both call and put wall.
- News: Saudi-Iran de-escalation talks pull oil lower; reports US/Israel weigh renewed Iran strikes (CNN: Trump refused Netanyahu's pre-election strike); Trump lifts some Canada tariffs. BTC -0.9% over the morning, no single headline >0.4% in 15m. FOMC Wed 18:00 UTC.
- DECISION: HOLD L1 (long 79,752, -0.1R at 79,693). Invalidation is the sweep low 79,179 (stop 79,099), not the 79,732 close; no tested reason to cut early. Zero-drift MC: stop zone touched in 24h ~59%, target 81k ~24% -> expected value is just the mark; plan unchanged.
- Orders: B1 (armed, needs a 4h close < 78,450) expires today 16:00 UTC and is left to expire: the 16:00 candle would need -1.6% in 2h, and the continuation short has only n=9 (< 15), so no renewal. No new orders.

## 2026-10-26 19:38 UTC — price 80,010
- 1h: below EMA50/200 (80.4k/81.3k), at weekly/session VWAP 80.05k; 12h delta +2.0k BTC. 4h: CHoCH down after the 79,565 close, but the sweep low 79,179 (L1 invalidation) held. Low since entry 79,322 (-0.66R). 1d: above EMA200 (76.3k), below EMA50 (80.8k).
- Positioning: funding 0.010% (rising), OI +1.6% 24h, near-term gamma -15M/1% under the flip ~80.15k; 80k is both call and put wall.
- News: no market-moving US headline; FOMC Wed 18:00 UTC, PCE/GDP Thu 12:30. B1 expired 16:00 UTC unfilled.
- Review (user asked: scalp the range instead of holding?). L1 bounced off the entry zone repeatedly (+1.91, +1.22, +1.64, +1.19R). Tested it properly: mechanical range fades and prior-day sweep scalps lose after fees (-0.06 to -0.23R, n in thousands); taking profit and re-entering on sweep setups lowers R on the broad samples (n=90/153). Hold-one-shot on 10/20-day-low sweeps is positive (+0.14/+0.17R, any daily trend). Shorts at highs negative.
- DECISION: HOLD L1 (long 79,752, +0.34R at 79,975), stop 79,099 / target 81,057 unchanged. Desk upgrade: S10 (1.5R) and S20 (2R) long sweeps without trend filter are now tradable; setup_scan.py added. No fresh signal now (10/20-day low 79,179, 1.5% below).

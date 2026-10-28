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

## 2026-10-27 11:43 UTC — price 79,851
- 1h: 79.86k, below EMA50/200 (80.15k/81.12k), last CHoCH down; 20-bar range 79.47-80.53k; 12h delta -2.1k BTC; sitting on session VWAP, under weekly VWAP 80.0k.
- 4h: below EMA50/200 (81.1k/81.7k), 20-bar range 79.18-81.08k; 08:00 close 79,774, low 79,548 (no new low).
- 1d: above EMA200 76.3k, below EMA50 80.7k; inside the 77.2-80.8k bull FVG; 20d low 79,179 is 0.75% below.
- Positioning: funding 0.008%/8h, OI +4.9% 24h (shorts adding into the dip?), basis -4bp; gamma flip 80.1k with the call and put walls both at 80k (pinning), short gamma <=7d.
- News: Fed meeting starts today, FOMC decision Wed 28 Oct 18:00 UTC (hold at 4.00% expected, hawkish tilt), Core PCE + GDP Thu 12:30. Nothing today moved BTC more than 0.45%.
- DECISION: HOLD L1 (S20 long 79,752, stop 79,099, target 81,057 = 2R; +0.17R now). No new S10/S20 signal. Thesis unchanged: wick below the 20d low reclaimed; stop under the wick. S20 tested n=90, +0.17R/trade. Holding through FOMC is allowed (stop-hit odds ~1.1x normal). No new entries Wed 16:00-18:00.
- Orders: none. MC zero-drift: 81k touch 57% in 72h, 79k 73%; the stop is closer than the target, so the risk is real.

## 2026-10-27 12:16 UTC — price 79,917
- 1h: 79,942, below EMA50/200 (80.1k/81.1k), last CHoCH down; 20-bar range 79,468-80,528; 12h delta -2.5k BTC; below weekly VWAP 80.0k.
- 4h: below EMA50/200 (81.1k/81.7k), 20-bar range 79,179-81,000; 12:00 candle closed 79,880 (low 79,468), no wick under the 20d/10d low 79,179 -> no S10/S20.
- 1d: above EMA200 (76.3k), below EMA50 (80.7k); above 300d value (VAH 79.5k).
- Positioning: funding 0.0087%/8h, OI +4.8% 24h (shorts adding into the low), basis -3bp; gamma 7d net -12M/1% short, flip 80.1k, 80k call=put wall pinning.
- News: Fed meeting started; CNBC survey says hikes coming, not this week; BTC -0.3% on the Fed headlines, then flat. FOMC Wed 18:00, Core PCE/GDP Thu 12:30.
- DECISION: HOLD L1 (S20 long 79,752, stop 79,099, target 81,057, +0.28R open). Thesis unchanged: the sweep of the 20d low held; MC 81k touch 55% in 72h vs 79k 75%. Hold through FOMC with the stop (event study: stop-hit odds ~1.1x). No new entries: no setup fired, and FOMC is >2h away but there is no signal.
- Orders: none changed.

## 2026-10-27 16:31 UTC — price 80,616
- 1h: 80.3-80.5k, back above EMA50 (80.16k) but below EMA200 (81.09k); above weekly VWAP 80.02k and session VWAP 79.95k; inside value (VAL 80.25k); 12h delta -40 BTC (flat); bear FVG 80.2-80.6k being worked through.
- 4h: below EMA50/200 (81.07k/81.70k), 20-bar range 79,179-81,000; 12:00 close 79,880, low 79,468, no new 10/20d low -> no S10/S20.
- 1d: above EMA200 (76.35k), just under EMA50 (80.75k); inside the 77.2-80.8k bull FVG.
- Positioning: funding 0.010%/8h, OI +2.9% 24h, basis -2bp; near-term gamma flipped to LONG +9.5M/1% with price above the 80.04k flip (dampening; 80k call=put wall), next strikes 81k/82k.
- News: equities firmer into FOMC; Iran leadership discussing war-end conditions (oil lower); Oleshky ceasefire. No headline moved BTC >0.45% in 15m. FOMC Wed 28 Oct 18:00, Core PCE/GDP Thu 12:30, BOJ Fri 02:30.
- DECISION: HOLD L1 (S20 long 79,752, stop 79,099, target 81,057 = 2R; +1.15R open at 80,500). Thesis unchanged: 20d-low sweep reclaimed, now above the gamma flip. S20 n=90, +0.17R/trade, one-shot hold (no partials, tested worse). MC zero drift: 81k touch ~51% in 24h / 72% in 72h. Hold through FOMC with stop (event study ~1.1x stop odds). No new entries Wed 16:00-18:00.
- Orders: none changed. Desk fix: paper_desk.py HTTP get() now retries transient resets (first run today died on ConnectionResetError).

## 2026-10-27 16:34 UTC — price 80,614
- 1h: 80.58k, above EMA50 80.19k / below EMA200 80.08k->81.08k; broke up out of 79.5-80.7k box w/ volume, but 12-bar delta -226 BTC; above weekly (80.05k) + session VWAP, inside value (VAL 80.25k).
- 4h: still below EMA50 81.05k / EMA200 81.69k; 20-bar range 79.18-81.00k, last 4h close 80,530; bull FVG 80.13-80.43k below as support.
- 1d: above EMA200 76.4k, just under EMA50 80.75k; 20d range 79.18-84.88k.
- Positioning: funding 0.010%/8h, OI +3.7% 24h, basis -4bp; 7d gamma flip 80.14k (price above), walls 80k/81k/82k.
- News: risk-on tone (US consumer confidence 91.7 vs 81 exp, equities near record, Oleshky truce); BTC +0.5-0.8% over 3h, no shock. FOMC Wed 28 Oct 18:00 UTC, Core PCE/GDP Thu 12:30.
- Setups: none (S10/S20 low 79,179 is 1.7% away).
- DECISION: HOLD L1 (entry 79,751.8, stop 79,099, target 81,057.4 = 2R), +1.27R open. One-shot hold per tests; no trailing (untested). MC 24h touch 81k 65%. Holding through FOMC allowed (event study: stop odds ~1.1x, no drift).
- Orders: none changed.

## 2026-10-27 18:16 UTC — price 80,596
- 1h: 80.59k, above EMA50 80.22k / below EMA200 81.07k; above weekly VWAP 80.07k and session VWAP 80.12k (+1.6σ); inside value (VAL 80.25k); 12-bar delta -182 BTC; swing high 80.82k, 20-bar range 79.47-80.81k.
- 4h: below EMA50/200 (81.05k/81.69k); 20-bar range 79,179-81,000; candle closing 16:00 at 80,530 (low 79,810), no sweep -> no S10/S20 (10/20d low 79,179, 1.7% away).
- 1d: above EMA200 76.4k, just under EMA50 80.75k; inside 77.2-80.8k bull FVG.
- Positioning: funding 0.010%/8h, OI +2.5% 24h, basis -1bp; gamma long (7d +26M/1%), flip 80.14k below price, 80k call=put wall, next strikes 81k/82k.
- News: pre-FOMC previews (hold at 4.00% expected, hawkish tone), Oleshky truce, Iran war-end talk; nothing moved BTC >0.3% in 15m. FOMC Wed 28 Oct 18:00 UTC, Core PCE/GDP Thu 12:30, ECB Thu 13:15, BOJ Fri 02:30.
- DECISION: HOLD L1 (S20 long 79,751.8, stop 79,099, target 81,057.4 = 2R; +1.28R open). Thesis unchanged: 20d-low wick reclaimed, price now above the gamma flip. S20 n=90, +0.17R/trade, one-shot hold. MC zero drift: 81k touch 61% in 24h / 79% in 72h. Hold through FOMC with stop (event study ~1.1x stop odds). No new entries Wed 16:00-18:00.
- Orders: none changed.

## 2026-10-27 20:17 UTC — price 80,755
- 1h: 80,740, back above EMA50 80.26k, still under EMA200 81.06k; 20-bar range 79.47-80.81k broke up with volume; 12-bar delta -318 BTC. Above weekly VWAP 80.09k.
- 4h: below EMA50/200 (81.05k/81.68k); last structure is a down CHoCH at 79.73k; range 79.3-81.0k; bull FVG 80.13-80.41k under price.
- 1d: sitting on EMA50 80.76k, well above EMA200 76.35k; 20d range 79.18-84.88k.
- Positioning: funding 0.010%/8h, OI +1.7% 24h, basis -5bp. Gamma flip 80.17k, call wall 81.0k right at the L1 target, put wall 80.0k.
- News: nothing BTC reacted to (moves under 0.3%). FOMC Wed 18:00 UTC (hold expected at 4.00%), Core PCE Thu 12:30.
- DECISION: HOLD L1 (entry 79,751.8, stop 79,099, target 81,057.4 = 2R), +1.51R open. No S10/S20 signal (20d low is 2.0% below). Tested breakeven stops (breakeven_test.py): worse than holding at every trigger; for S20 trades that reached +1.5R, holding gave +1.62R vs +1.50R with BE (n=21). Keep the original stop; holding through FOMC is allowed. MC 24h touch of 81k is 83%.
- Orders: none changed.

## 2026-10-27 22:08 UTC — price 80,899
- EVENT: L1 long closed at target 81,057.4 on the 22:00 1h close, +1.88R, equity $10,187.68.
- 1h: 80,899, above EMA50 80.3k, just under EMA200 81.06k; up CHoCH 80,819; 12-bar delta +2.0k BTC; broke out of range on volume; 81.0k call wall and the 81.6k POC sit overhead.
- 4h: below EMA50/200 (81.06k/81.68k); last structure still a down CHoCH; 20-bar range 79.3k-81.3k; delta +2.5k.
- 1d: above EMA50 80.77k and EMA200 76.4k; 20d range 79.18k-84.88k.
- Positioning: funding 0.0073%, OI +0.5% 24h; gamma flip 80.18k, call wall 81k, put wall 80k (pinned between them).
- News: nothing BTC reacted to (moves <0.6%). FOMC Wed 28 Oct 18:00 UTC, Core PCE/GDP Thu 12:30.
- DECISION: NO TRADE. setup_scan shows no S10/S20 signal (the 10d/20d low of 79,179 is 2.0% below). Analog plans from here are all EV ~0 (-0.08R to +0.04R); mechanical range fades tested negative. No new entries 16:00-18:00 UTC Wed before FOMC.
- Orders: none. Book flat.

## 2026-10-27 22:14 UTC — price 80,873
- CLOSED L1 at target 81,057 (2026-10-27 22:00 UTC): +1.88R net of fees, +$187.68. Equity $10,187.68. Track record 1/1, +1.88R. Plan held as tested (hold one shot to 2R); the dip to -0.66R never reached the 79,099 stop.
- 1h: reclaimed EMA50 (80.3k), up CHoCH at 80.8k, just under EMA200 (81.06k), inside value; 12h delta +1.7k BTC. 4h: still below EMA50/200 (81.05k/81.7k), inside value. 1d: back above EMA50 (80.77k) and EMA200 (76.4k).
- Positioning: funding 0.007%, OI +0.5% 24h; near-term gamma flipped POSITIVE (+41.5M/1%, dampening), call wall 81k right overhead, put wall 80k.
- News: Iran escalation risk flagged after the midterms (Al Jazeera, OilPrice); US-Canada tariff easing. FOMC tomorrow 18:00 UTC (hold 4.00% expected), PCE/GDP Thu 12:30.
- Scan: no S10/S20 signal (10/20-day low 79,179 is 2.0% below). DECISION: NO TRADE, flat into FOMC. No tested setup at 80.9k; chasing into the 81k call wall 20h before FOMC has no evidence behind it. Next entry: a 4h sweep-and-reclaim of 79,179 (S20, 2R), caught by setup_scan at each 4h close.
- Research idea (backlog): buying 4h closes ABOVE the 10/20-day high, since short fades of highs tested strongly negative.

## 2026-10-28 04:22 UTC — price 80,916
- 1h: 80.9k, above EMA50 80.4k, just under EMA200 81.05k; last CHoCH up at 80.8k; 20-bar range 79.5-81.3k; 12-bar delta -1.9k BTC (sellers into 81k).
- 4h: below EMA50 81.05k / EMA200 81.7k, last CHoCH down; 04:00 close 81,111, holding above weekly VWAP 80.2k.
- 1d: above EMA50 80.8k and EMA200 76.4k; range 79.2-84.9k; 12d delta -5.0k BTC.
- Positioning: funding 0.005%/8h (neutral), OI -0.7% 24h, basis -5bp; gamma pinned 80k put wall / 81k call wall, flip ~80.3k.
- News: FOMC 18:00 UTC today (hold 4.00% expected), Core PCE/GDP Thu 12:30; Iran/oil headlines, BTC reaction <0.3%.
- DECISION: NO TRADE. setup_scan: no S10/S20 (20d low 79,179 is 2.4% away). Analog plans all EV ~0R; price pinned between gamma walls. No entries 16:00-18:00 per event rule.
- Orders: none.

## 2026-10-28 09:21 UTC — price 81,437
- 1h: 80.88k, above EMA50 80.47k, just under EMA200 81.05k; last CHoCH up (80.82k); 79.8-81.3k range; 12-bar delta -1.5k BTC.
- 4h: below EMA50 81.05k / EMA200 81.67k; last CHoCH down 79.73k; 20-bar range 79.3-81.3k; last close 81.11k.
- 1d: above EMA50 80.77k and EMA200 76.4k; inside 79.2-84.9k 20-day range; 12d delta -4.9k BTC.
- Positioning: funding 0.006%/8h (neutral), OI -1.1% 24h, basis -4bp; gamma pinned 80k put wall / 81k call wall, flip ~80.2k.
- News: no BTC-moving headlines (all <0.15% m60). FOMC 18:00 UTC today, Core PCE + GDP Thu 12:30, ECB Thu, BOJ Fri. 7/25 feeds down.
- DECISION: NO TRADE. No S10/S20 signal (20d/10d low 79,179 is 2.4% below the last 4h low). Analog plans all EV ~0R; MC 7d P(higher) 44.5%. Range chop between gamma walls, no edge. FOMC blackout starts 16:00 UTC; any S10/S20 wick under 79.18k after the 20:00 close is valid (stop under the wick, 1.5R/2R).
- Orders: none. Book flat, 1 closed +1.88R, equity 10,187.68.

## 2026-10-28 09:21 UTC — price 81,390
- Flat, equity $10,187.68 (1 trade, +1.88R).
- 1h: above EMA50/200 (80.5k/81.05k), up CHoCH 80.8k, broke up from consolidation; 4h: above EMA50 (81.07k), just under EMA200 (81.67k); 1d: above EMA50/200. Price 81,497, inside value (POC 81.6k, VAH 82.5k).
- Positioning: funding 0.0098% (rising), OI -1.5% 24h (rally on short covering), near-term gamma +51M/1% (dampening), call wall 82k overhead, put wall 80k.
- News: Coinbase denies breach (vendor leak), BTC +0.9% in the following hour; FOMC today 18:00 UTC.
- Scan: no S10/S20 signal (10/20-day low 79,179, 2.4% below). DECISION: NO TRADE. Event rule: no new entries from 16:00 UTC (2h before FOMC). No tested long-breakout setup yet (backlog #6).
- Watch (not desk-tradable): HOOD -6.5% after earnings (perp 87.3), gap-down-while-stretched study n=11 favours a bounce; tracking the US open as an out-of-sample case.

## 2026-10-28 10:11 UTC — price 81,436
- 1h: 81.45k, back above EMA50/200 (80.6k/81.06k) after up CHoCH; broke out of consolidation with volume, but 12-bar delta -1.9k BTC and bear OB 81.58-82.04k overhead; POC 81.6k.
- 4h: above EMA50 81.07k, still under EMA200 81.67k; 20-bar range 79.3-81.8k; last closed 08:00 bar 81,050.
- 1d: above EMA50/200, in 79.2-84.9k range; 20d/10d low 79,179 is 2.4% away.
- Positioning: funding 0.0096%/8h, OI 24h -1.7%, basis -5bp; gamma flip ~80.4k, call wall 82k, put wall 80k (pinned 80-82k).
- News: FOMC 18:00 UTC (hold expected, presser 18:30); Core PCE+GDP Thu 12:30. Coinbase vendor data breach: no BTC reaction. Iran-deal headlines +0.3-0.5% m15 earlier.
- DECISION: NO TRADE. setup_scan: no S10/S20 signal in 3 days; analogs ~coin-flip (24h up 54%, n=102 episodes). No entries 16:00-18:00 UTC per event rule.
- Orders: none. Book flat, 1 closed +1.88R, equity 10,187.68.

## 2026-10-28 13:38 UTC — price 80,776
- 1h: 80.8k, back above EMA50 80.6k but under EMA200 81.1k; pulled back from 81.3k (12:00 4h close) into session VWAP -1σ; 12-bar delta +187 BTC.
- 4h: below EMA50 81.1k / EMA200 81.7k; 20-bar range 79.3k-81.8k, last CHoCH down; 12-bar delta -2.5k BTC.
- 1d: above EMA200 76.4k, at EMA50 80.8k; in 79.2k-84.9k range.
- Positioning: funding 0.0055%, OI -1.7% 24h, basis -4bp; 7d gamma flip 80.1k, put wall 80k, call wall 82k (pinned between).
- News: FOMC 18:00 UTC (hold 4.00% fcst), presser 18:30; core PCE + GDP Thu 12:30. BTC -0.7% over 2h on pre-Fed tape, no single headline move.
- DECISION: NO TRADE. setup_scan: no S10/S20 (10/20d low 79,179, 2.7% away). Outlook plans all EV ~0R. 16:00 close falls at the edge of the 2h pre-FOMC no-entry window, so no conditional orders either.
- Orders: none.

## 2026-10-28 14:19 UTC — price 80,595
- 14:19 UTC check: flat. BTC 80,572, slipped below 1h EMA50/200 (80.6k/81.05k) after rejecting 81.6k; 4h below EMA50/200; 1d at EMA50 (80.76k). 12-bar 4h delta -2.9k BTC. Funding 0.005%, OI -0.85% 24h, gamma +20M/1% (pin 80-82k, flip 80.1k).
- Scan: no S10/S20 signal (79,179 is 2.7% below). DECISION: NO TRADE; event rule blocks new entries from 16:00 UTC (FOMC 18:00).
- HOOD watch (out-of-sample case): bounced from 86.3 low / ~87 pre-open to 91.8 after the US open (+5%), in line with the stretched gap-down study (gap day closed above open 73%, n=11).
- Schedule changed to every 4h, 5 min after each 4h close.

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

## 2026-10-28 20:53 UTC — price 81,121
- 20:05 UTC run (done at 20:53; data back via the new Binance-archive + OKX fallback, fapi.binance.com is geo-blocked from the cloud box).
- 1h: 81.06k, above EMA50/200 (80.70k/81.04k), last CHoCH up; FOMC spike to 81.79k faded, 12-bar delta -219 BTC; session VWAP 81.0k.
- 4h: at EMA50 81.06k, under EMA200 81.65k; 20-bar range 79.3-81.8k. 1d: above EMA50 80.8k and EMA200 76.4k (bull regime).
- Positioning: funding 0.010%/8h (7d avg 0.0074%), OI -2.7% 24h (OKX), basis -3bp; gamma pin 80k put wall / 82k call wall, 7d flip 80.3k.
- News: Fed held (split vote, two dissents wanted a hike), Warsh: fewer meetings from next year, 'information-rich period' ahead; BTC +0.8% in the hour after, then gave it back (-0.8% from the 45m-ago headlines). Core PCE + GDP Thu 12:30.
- Scan: no signal. Daily regime BULL, so the new B20/R10 shorts are off; S10/S20 lows at 79,179 (3.0% away).
- DECISION: NO TRADE. Desk now trades both directions: B20/R10 shorts added (bear regime only), see research_log 2026-10-28.

## 2026-10-29 00:06 UTC — price 81,299
- 00:05 UTC check: flat. BTC 81,246; 1h above EMA50/200 (80.79k/81.06k), 12-bar delta +2.4k BTC; 4h reclaimed EMA50 81.08k, still under EMA200 81.65k; 1d above EMA50 80.8k / EMA200 76.45k (bull regime). Range 79.3-81.8k intact.
- Positioning: funding 0.010%/8h, OI -1.75% 24h (OKX), basis -4bp; gamma +61M/1% (7d), walls 81k/82k, flip 80.35k: pinned, low-vol tape.
- News: post-FOMC digestion (split hold, two hike dissents), Hormuz/Iran escort headlines with no BTC reaction. Core PCE + GDP today 12:30 UTC.
- Scan: no signal. Shorts off (bull regime); S10/S20 trigger zone 79,179 (2.7% below). DECISION: NO TRADE. Event rule: no new entries 10:30-12:30 UTC.
- Desk: snapshot.js no longer prints Node's proxy-agent warning.

## 2026-10-29 04:06 UTC — price 79,820
- 04:05 UTC check: flat. BTC fell 81.3k -> 79.8k (-1.8%) in the 00-04 4h candle; low 79,666, $356M of longs liquidated under 80k (CoinDesk). Drivers: 'hawkish hold' read of the Fed (two hike dissents), Iran/Hormuz risk, crypto equities in a stealth bear market (COIN/CRCL/HOOD -40-56% from highs).
- 1h below EMA50/200 (80.65k/81.0k); 4h below EMA50/200 (80.98k/81.61k), 12-bar delta -1.4k BTC; 1d lost EMA50 80.75k, still above EMA200 76.44k (bull regime, shorts off).
- Positioning: OI +2.1% 24h / +6.2% 7d into the drop (shorts adding), funding down to 0.004%; 7d gamma flipped NEGATIVE (-30M/1%) below the 80.2k flip: dealers now amplify moves.
- Scan: no signal yet. Price is 0.8% above the 20/10-day low 79,179: a 4h wick below it that closes back above = S10/S20 long; the 08:05 run will catch an 08:00 close. A 4h close BELOW 79,179 is a bull-regime breakdown (~0R): no short.
- DECISION: NO TRADE now. Event rule: no new entries 10:30-12:30 UTC (Core PCE + GDP 12:30), so a signal on the 12:00 close is skipped.

## 2026-10-29 07:05 UTC — price 79,909
- 07:05 UTC manual run: flat. BTC 79,905, 3h into the 04:00 4h candle (range 79,750-80,486): bounced to 80.49k and faded back under session VWAP 80.14k. 1h/4h below EMA50/200; 1d below EMA50 80.75k, above EMA200 76.44k (bull regime, shorts off).
- Flow/positioning: 12-bar 1h delta -2.2k BTC; OI +3.5% 24h / +9.4% 7d while funding sits at 0.004% (shorts adding, not longs); 7d gamma -29M/1% below the 80.26k flip; 80k is both call and put wall.
- News: no new BTC catalyst; Vance restarting Iran talks (oil lower), Russia/Ukraine drone strikes, PCE/GDP preview keeps hike bets alive. GDP (fcst 3.2%) + core PCE at 12:30.
- Scan: no signal (needs a CLOSED 4h candle). 79,179 sweep zone 0.9% below; the 08:00 close is the next chance, checked by the 08:05 run. DECISION: NO TRADE.

## 2026-10-29 08:10 UTC — price 79,982
- 08:05 UTC check: flat. 04-08 4h candle closed 79,820 (range 79,750-80,486): inside bar under the 4h EMA50/200 (80.94k/81.60k), no test of 79,179. 1h below EMA50/200; 1d below EMA50 80.75k, above EMA200 76.44k (bull regime, shorts off).
- Positioning: OI +4.4% 24h with funding sliding to 0.003%: shorts keep adding into the 80k magnet (call wall = put wall = 80k, 7d gamma -20M/1%, flip 80.28k).
- News: Treasury yields lower post-Fed, oil down on renewed US-Iran peace efforts; nothing BTC-specific. GDP + core PCE 12:30.
- Scan: no signal; 79,179 sweep zone 0.8% below. The 12:00 close falls inside the pre-data window (no entries 10:30-12:30), so the next actionable close is 16:00. DECISION: NO TRADE.

## 2026-10-29 11:34 UTC — price 80,111
- 11:34 UTC all-markets run (desk now covers BTC / ETH / HYPE perps + HOOD on Nasdaq). Inside the 10:30-12:30 pre-data window (GDP + core PCE 12:30): no new entries on any market.
- BTC 80,145: range 79.2-81.8k, bounced from 79,666 (yesterday's liquidation low); 1h/4h below EMA50/200, daily above EMA200 76.4k (bull). OI +4% 24h with funding ~0.003%: shorts adding. No S10/S20 sweep (79,179 is 1.2% below); B20 off (bull). NO TRADE: no signal + event window. If 12:00/16:00 4h wicks under 79,179 and closes back above -> S10/S20 long (16:00 is the first allowed close).
- ETH 2,324: sitting ON the daily EMA200 (2,319) after losing the daily EMA50 (2,445); 1h/4h below EMAs; OI +10.6% 7d, Deribit gamma negative below the 2,395-2,407 flip, put wall 2,300. NO TRADE: none of the desk setups work on ETH (S10 -0.06R, S20 -0.28R, B20 +0.21R t 1.0); a daily close under 2,319 would put ETH in a bear regime, but B20 isn't proven on ETH.
- HYPE 86.0: +8.6% in the 10:00 hour on 'NYSE owner (ICE) to bring Hyperliquid perpetual futures to the US'; above 1h/4h/1d EMAs, broke 82.5 (up BOS), OI +4.7% 24h, funding 0.01%. Strongest chart on the desk. NO TRADE: no tested HYPE setup (S10 -0.32R on HYPE, 17 months of data), and buying a +9% news candle at the high means a stop under 79 (8%+) for an unknown target. Watch: holding 82.5 on a retest would be a continuation; giving it back below 82.5 = failed breakout.
- HOOD 91.41 (Nasdaq closed; pre-market 12:00 UTC): post-earnings gap day closed +2.5% off its 89.23 open (the stretched gap-down study said the gap day closes above its open 73% of the time: case behaved). Still below 15m/1h/1d EMAs (daily -7.6% under EMA200), bear FVGs 92.3-95.4 overhead. NO TRADE: the paper desk trades BTCUSDT only, the gap study is n=11 (idea), and post-earnings drift argues against a long. Out-of-sample tracking: 10-day median after such gaps +23.9%; 10-day mark = Nov 11.
- Desk changes: HYPE + Nasdaq HOOD on the dashboard; market_setups_test.py (BTC setups fail on ETH/HYPE); R10 demoted to idea (fragile: +0.41R -> +0.27R with the regime checked at the breakdown); HYPE news rule (the ICE headline had scored impact 1).

## 2026-10-29 12:09 UTC — price 80,120
- 12:09 UTC: new scalp book live (0.5% risk, both directions, BTC/ETH/HYPE; rules in paper_desk.py). Desk runs go hourly.
- HYPE 87.6: X1 LONG limit 85.5 (from 12:30), stop 83.9, 2R (~88.7). Why: news repricing (ICE/NYSE to list Hyperliquid futures in the US) with OI +9.8% 24h, funding only 0.01% (not crowded), 5m taker delta +331k, 1h/4h/1d above EMAs. Buying the first pullback into the 5m imbalance, not the high. Invalid below 83.9: the gap fills and the momentum has failed.
- BTC 80,118: pinned at 80k (call wall = put wall), 15m range 79,790-80,350, short gamma below the 80.2k flip, OI +4.8% 24h with low funding. GDP + core PCE at 12:30. OCO BRK1 from the 12:30 candle on: X2 LONG on a 15m close > 80,350 (stop 79,990, 1.5R) / X3 SHORT on a 15m close < 79,790 (stop 80,150, 1.5R). Why: the release should break the pin; trade whichever side it breaks, out of the 15m range, with the stop back inside it.
- ETH 2,322: no order. It is a near-copy of BTC (sitting on its daily EMA200 2,319, 15m range 2,304-2,330); a second BTC-like bet doubles the same risk.
- HOOD: Nasdaq pre-market; no order (desk trades perps).

## 2026-10-29 12:25 UTC — price 80,064
- 12:24 UTC review (user: are these backtested?). No, they weren't; tested now (quant/scalp_tests.py). BTC release range break: -0.22R/trade, n=1,526, t -6.9 -> X2/X3 CANCELLED before 12:30. HYPE impulse pullback: BTC/ETH versions lose (-0.14/-0.13R, n=147/107), HYPE's own +0.83R on n=8 -> X1 kept at 0.5% risk, low confidence. HYPE 88.67 is now at X1's target (prior-high retest); if it fills at 85.5 the trade is a pullback-to-high play. Dashboard now draws paper orders/positions on the chart (server.py /api/paper).

## 2026-10-29 12:29 UTC — price 80,089
- 12:30 UTC (user: weigh the whole picture; a backtest is one input, not a veto). Agreed, with one condition: when the backtest is strongly negative, the confluence must give a specific reason this instance differs. Re-read BTC at the release: intraday trend down on 5m/15m/1h, 1h delta -1.3k, short gamma below 80.2k, shorts adding, supply 80.15-81.06k overhead, swing-long zone 79.18k below as a target. Breakdown side has confluence, breakout side doesn't. X4 SHORT on a 15m close < 79,790, stop 80,150, target 79,250 (1.5R), from 12:30 to 16:00, 0.5% risk. Breakout long not re-placed (against the intraday trend, into supply).
- Calibration: release-window breaks in the 1h-trend direction test -0.20R (n=648) vs -0.31R against (n=564). The trend filter helps but doesn't make it positive, so X4 is low confidence. Next test: breakdown + retest entry and wider ATR stops (the 0.45% stop sits inside release noise).

## 2026-10-29 12:51 UTC — price 80,057
- 12:52 UTC: prop rules now enforced in paper_desk.py: pass at +9% ($10,900); fail if equity drops 3% ($300) below its peak (trailing, the strict reading). Floor now $9,887.68, room $300. Swing risk 1% -> 0.5%, scalp 0.5% -> 0.35%, scalp day stop 1%, and open+pending risk capped at half the room ($150). X1/X4 resized to 0.35% (~$36 each, ~$43 with fees). Leverage on X4 ~0.8x notional, X1 ~0.2x: size comes from the stop distance, not leverage.

## 2026-10-29 12:56 UTC — price 80,013
- 12:56 UTC: rules corrected to Propr Turbo 1-Step (propr.xyz/rules via search; the site itself is outside this session's network allowlist): +9% target, 3% STATIC max drawdown (floor $9,700, never moves: profit adds room) and 3% daily loss from the 00:00 UTC balance (today $9,882.05, the binding one). No time limit, no minimum days. Leverage up to 1:10 on BTC/ETH per a listing; the 1x setting is margin, positions stay sized by the stop.

## 2026-10-29 13:05 UTC — price 80,104
- 13:05 post-release check: core PCE +0.5% m/m vs +0.3% expected (hot), GDP 3.4% vs 3.2%. Hawkish, yet BTC barely moved: 12:30 15m range 79,974-80,245, 12:45 close 80,024. Still inside 79,790-80,350, so X4 didn't trigger and stays pending to 16:00. HYPE 89.7, no pullback; X1 limit 85.5 unfilled. No changes: a muted reaction to hot data leaves the pin intact. Desk fix: news calendar showed released events as 'in -1d 23h', now 'released Xm ago'.

## 2026-10-29 13:18 UTC — price 80,170
- 13:16 hourly: flat, floor $9,882 (daily), room $305.
- BTC 80,140: hot PCE absorbed; 1h taker delta flipped to +1.0k (was -1.3k), price back on session VWAP 80.13k, still inside 79,790-80,350 under the 15m/1h EMAs and weekly VWAP 80.39k. Keep X4 (short on a 15m close < 79,790): the close itself would restore the downside case; the flow flip weakens it, so no new BTC entries. Upside break = against the 1h trend into supply 80.15-81.06k: no long.
- HYPE 91.1 (+15%, OI +13.6%, funding 0.01%, 15m delta +1.4M): X1 at 85.5 cancelled (6% away), X5 LONG limit 88.9 (retest of the 88.96 breakout), stop 87.2, 2R ~92.3, 0.35%. Not chasing 91: buying the first retest of the breakout level.
- ETH 2,328: 2,309-2,330 range, capped by weekly VWAP 2,331, 1h delta -29.6k vs 5m above EMAs: mixed, mid-range. No trade (range-edge fades tested negative; no edge either side).
- HOOD: Nasdaq opens 13:30; watch only.

## 2026-10-29 14:20 UTC — price 80,407
- 14:18 hourly: flat, room $305.
- BTC 80,422: broke UP out of 79,790-80,350 (15m close 80,431), above session/weekly VWAP, 7d gamma flipped positive (+5M/1%) above the 80,275 flip = dampening. X4 (short on a break below 79,790) CANCELLED: the range resolved the other way, and a later drop to 79,790 would be a different trade. No long: the break already happened (no chasing), the 1h is still under EMA50/200 (80,495/80,928) with supply 80.5-81.06k right above, and positive gamma favors chop, so a retest long has ~1R of room before resistance.
- HYPE 91.3: holding 88.5-92.1 at the highs; OI -2.7% in the last hour and 5m delta flat (profit-taking, no reversal). X5 LONG limit 88.9 kept: it sits just above the consolidation low 88.52, the breakout-retest level.
- ETH 2,330: pressing the range top 2,332.7 / weekly VWAP 2,331 with 1h delta -23k (selling into it). No trade: a short at the top is a range fade (tested negative) and a long into supply with sellers active isn't one either.
- HOOD: Nasdaq open; watch only.

## 2026-10-29 15:03 UTC — price 81,220
- 15:04 review (user's TradingView): the original BRK1 long side WORKED. 14:00-14:15 15m candle closed 80,409 > 80,350 -> X2 would have entered ~80,409 (stop 79,990, 1.5R target ~81,037); 14:30 candle ran to 81,525 -> target hit, about +1.5R (~+$53 at 0.35%). The short side never triggered (13:30 low 79,860, no close < 79,790).
- My errors: (1) at 12:24 I cancelled both sides on the -0.22R backtest; (2) at 12:30 I re-placed only the short, using confluence for one side and the backtest for the other (inconsistent); (3) at 14:18 I saw the 80,431 close and called it 'chasing' when price was 80,420, i.e. at the planned entry. The plan was right; my overrides weren't.
- Rules from this: a two-sided plan stays two-sided unless the chart invalidates one side (not a backtest alone); if a trigger fired since the last run and price is still within 0.25R of the planned entry, take it; every cancelled or skipped plan trade gets scored in the journal as a shadow trade so my overrides are measured too. Shadow #1: BRK1/X2 +1.5R (missed).

## 2026-10-29 15:08 UTC — price 81,339
- 15:10 UTC: added quant/paper/lessons.md (current rules, mistakes/misses log, shadow trades, review cadence) and paper_desk.py shadow trades: skipped/cancelled plan trades are resolved on 5m candles and reported as their own R record. S1 (missed BRK1 long) logged: +1.50R. Every run reads lessons.md first.

## 2026-10-29 15:13 UTC — price 81,462
- 15:20 UTC: (1) lessons.md now leads with WINS and what made them work (L1 +1.88R; S1 shadow +1.5R; D1F HYPE retro +2R) next to mistakes/misses; every closed trade gets a row either way. (2) User's tweet (@MuroCrypto, HYPE daily S/R flip + rising MA, entry ~77.3 on Oct 26, now ~91): coded as D1F and backtested: daily works (BTC +0.32R n=46, ETH +0.25R n=45, both halves positive), the same rule on 4h is ~0R. Added to setup_scan.py for BTC/ETH/HYPE; the scanner would have fired on HYPE at the Oct 24 close (76.65 -> 2R 91.57 hit today). No D1F signal now (nearest untested flipped levels are 19-39% below). (3) Swing reads now start from 1D/4H screenshots (rule 10).

## 2026-10-29 15:42 UTC — price 81,565
- 15:40 UTC plan (zoomed 5m-1D on all three). Risk-on in crypto while Nasdaq -1.5%: BTC +1.4% from the 80k pin, all intraday TFs above EMAs.
- BTC 81,525: 1h back above EMA200 (80,941), 4h testing EMA200 81,598, 7d gamma +70M (dampening) with the 82k call wall right above and bear OBs 81.37-81.88k (the 'weak high'). NO TRADE: long here buys into the call wall/supply under long gamma (pin 81-82k); short fades a strong trend. Swing scan: no S10/S20 (79,179 is 2.9% below), no D1F, shorts off (bull regime).
- ETH 2,365: X7 LONG limit 2,350 (pullback into bull FVG 2,342-2,356 after the range breakout), stop 2,326 (back inside the old range), target 2,398 under the 2,400 gamma wall (2R).
- HYPE 93.9: X5 (88.9) cancelled, 5% below. X6 LONG limit 92.2 (retest of the 92.1 breakout), stop 90.6 (under the 5m bull OB), target 95.0 under the 95.27 ATH (1.75R).
- Correlation: X6/X7 both crypto longs; together $86 max loss, inside the $153 cap. Only one BTC/ETH-type bet (ETH chosen: cleaner breakout-retest with a defined 2,400 target; BTC is pinned under 82k).

## 2026-10-29 16:23 UTC — price 81,401
- 16:21 hourly: flat, room $305; X7 ETH limit 2,350 still pending (low since placement ~2,353).
- BTC 81,377: the 16:00 4h closed 81,744 after tagging 81,944 into the 82k call wall; 5m delta -558 now. Pinned 81-82k under long gamma (+61M). NO TRADE: same as 15:40, a long buys the wall, a short fights the trend; watch a 4h close > 82k (breakout) or < 81k put wall (pin breaks down).
- ETH 2,358: holding the breakout, 15m delta +99k. X7 kept.
- HYPE 95.9: ran through X6's target zone and the 95.27 ATH to 96.9 without retesting 92.2 (X6 never filled, so no shadow). X6 cancelled; X8 LONG limit 95.3 (old ATH retest), stop 93.9, target 98.1 (2R). Not chasing 96: waiting for the retest.
- HOOD: watch only.

## 2026-10-29 17:17 UTC — price 80,973
- 17:16 hourly: X8 HYPE long FILLED 95.30 (16:40), X7 ETH long FILLED 2,350.0 (17:05). Open risk $77, room $305.
- HYPE 95.4 (X8 +0.24R): holding the old ATH 95.27 inside a 93.5-97.1 5m range; funding fell to 0.0018% while OI is +17% 24h (new shorts fading the ATH = squeeze fuel); 1h delta +1.9M; fresh catalyst (Druckenmiller backing Trade[XYZ]/Hyperliquid perps). HOLD, stop 93.9 / target 98.1 unchanged.
- ETH 2,350 (X7 0R): sitting in the 2,342-2,356 bull FVG it was bought in; 15m delta +21.8k, 5m -4.7k; call wall 2,360 just above, target 2,398 beyond it. HOLD, stop 2,326 (back inside the old range) unchanged. Risk: BTC.
- BTC 81,026: rejected 81,944 (82k call wall), now on 81,000 where the call and put walls sit (7d gamma +40M = pin). 1h EMA200 80,947 right below. NO TRADE: a BTC short would bet against the two open longs, and a long buys a pin. Watch: a 1h close < 80,947 weakens the ETH thesis (act on X7's stop, don't pre-empt).
- HOOD: watch only.

## 2026-10-29 18:13 UTC — price 80,774
- 18:12 hourly: X8 HYPE STOPPED 93.90 at 17:50 (-1.07R, -$38); equity $10,149.62, room $267.6. Wick to 93.05 then back to 94.3: the stop was inside 1h noise (lesson logged).
- X7 ETH 2,337.6 (-0.51R): 5m/15m delta -24k/-50k as BTC slipped under its 1h EMA200; still above the old range top 2,330 / weekly VWAP 2,333, so the breakout isn't failed. HOLD, stop 2,326 unchanged (never widen, no pre-emptive cut).
- HYPE 94.0: lost the ATH, now inside 93-97. X9 plan: LONG only on a 15m close > 95.4 (ATH reclaim), stop 92.9 under the sweep low, target 99.0. No blind re-entry.
- BTC 80,812: lost the 81k pin and the 1h EMA200 (80,944); 15m delta -2.1k; gamma flip 80,411 below. NO TRADE: a short would double down against X7 (same direction risk), a long has no trigger. Watch 80,411 (below it gamma turns amplifying).
- HOOD: watch only.

## 2026-10-29 18:35 UTC — price 80,631
- 18:35 UTC: X7 ETH STOPPED 2,326 (-1.10R, -$39.13). Equity $10,110.49 (+1.10%), room $228. Scalp book 0/2, -2.16R.
- What went wrong: (1) STALE LIMIT: placed 15:40 in a BTC-led rally; filled 17:05 after the picture had flipped: BTC rejected the 82k call wall (81,944) and lost the 81k pin, ETH was rejected at 2,378.8 with 15m delta -18k. The order filled on weakness, not on a healthy pullback. (2) LEADER IGNORED: I wrote 'risk: BTC' at 17:16 and held; BTC then lost its 1h EMA200 and ETH lost the old range top 2,330 = breakout failed (a real thesis loss, not a wick: 18:30 close 2,328). (3) CORRELATION: X7 and X8 were two crypto longs filled 25 min apart; one market turn took both (-$77). (4) TARGET behind supply: 2,398 sat beyond the 2,360 call wall and the 2,365-2,391 bear OBs that had already rejected ETH.
- What went right: stop honoured, loss exactly the planned 0.35% (+fees), daily floor never close.
- Fixes: lessons.md rules 12-15 (stale limits expire after 2h and are re-checked every run; leader check for alt longs; correlated longs count as one bet; targets must clear supply). paper_desk.py: scalp limits now default to a 2h expiry.

## 2026-10-29 18:41 UTC — price 80,572
- 18:42 UTC (user, LuxAlgo chart): X7 was badly LOCATED: entry 2,350 mid-range, stop 2,326 on top of the demand zone (5m bull OB 2,312-2,325, 15m bull OB 2,296-2,313, 2,300 put wall, strong low 2,292), the zone the bounce should come from. All of it was in my own snapshot; I didn't use it. Rule 16 added (enter at the zone, stop beyond it).
- Applied now: ETH 2,323.6 is in that zone. X10a LONG limit 2,322 + X10b LONG limit 2,312 (0.175% each = 0.35% total), stop 2,288 below the zone and the strong low, target 2,362 in front of the 2,360 call wall / 2,365 bear OB (1.2R from a, 2.1R from b; ~1.6R blended). Leader check: BTC 80,610 above its 80,388 gamma flip; cancel both if a BTC 15m closes below it. 2h expiry by default.

## 2026-10-29 18:42 UTC — price 80,632
- 18:50 reconciliation (user: 'why 2 scalp losers? only the ETH long filled'). Paper book: L1 swing BTC +1.88R; X8 scalp HYPE long filled 95.30 at 16:40 (5m low 95.30, then 95.25 at 16:45), stopped 93.90 at 17:50 (-1.07R); X7 scalp ETH long -1.10R. The user's HYPE order was the original X1 at 85.5, which never filled: I moved the HYPE long X1 -> X5 -> X6 -> X8 without flagging each move as an order to mirror, so the two books diverged. Fixes: rule 17 (every order change announced as an ORDER UPDATE); limits now fill only when price trades THROUGH the level (X8 would still have filled at 16:45, low 95.25). BTC release long = shadow S1 +1.5R (missed); BTC short X4 never triggered (correctly cancelled after the upside break).

## 2026-10-29 18:48 UTC — price 80,629
- 18:48 R check (user asked): X10a was 1.18R (2,322 -> 2,362 vs stop 2,288) and X9 at most 1.44R: both under my own 1.5R minimum. Replaced: X11a ETH limit 2,318 (1.53R) + X11b limit 2,312 (2.17R), stop 2,288, target 2,364 (0.175% each; ~1.85R blended); X12 HYPE long on a 15m close > 95.4, stop 92.9, target 2R from the fill. Every order now gets its R stated before placing.

## 2026-10-29 18:49 UTC — price 80,696
- 18:50 (user: 1.21R target makes no sense): agreed. That was X10a (2,322 -> 2,362), already replaced at 18:48 by X11a 2,318 -> 2,364 (1.53R). Now also: deep half X11b -> X11c, limit 2,312, stop 2,288, target 2,395 under the 2,398 weak high (3.46R). Blended if both fill and both hit: ~2.5R on 0.35%.

## 2026-10-29 19:13 UTC — price 80,800
- 19:11 hourly: no fills, no open positions; equity $10,110.49, room $228.
- Rule 12 re-check of pending orders: X11a/X11c ETH limits 2,318/2,312 KEPT: ETH 2,328.8 hovering above the demand zone (low 2,323.3); sellers still pressing (15m delta -67k) but the zone hasn't been tested yet, and the leader holds (BTC 80,810 above its 80,422 gamma flip, back above the 15m EMAs). X12 HYPE (15m close > 95.4) KEPT: HYPE 94.5 inside 93.05-95.7, buyers back (+142k 5m).
- BTC: between the 80,422 flip and the 81k pin, 1h EMA200 80,943 just above. NO TRADE: mid-range, no level to lean on (rule 16).
- News: Polymarket $2.65M exploit (third-party), no BTC reaction. HOOD: watch only.

## 2026-10-29 20:16 UTC — price 80,402
- 20:14 hourly: X11a (2,318) and X11c (2,312) ETH longs FILLED at 20:00. At 20:00 Trump announced a naval blockade of Iran after the Islamabad talks failed (impact 3); BTC -0.5%, 15m close 80,383 under its 80,389 gamma flip (7d gamma -5.6M, amplifying), under all intraday EMAs.
- Rule 13 (leader broke while an alt long is open: judge the thesis): the zone thesis now fights a risk-off war headline plus an amplifying gamma regime. CLOSED both at 2,314 for -$3.64 and -$0.25 (near flat) instead of waiting for 2,288. Logged as shadows S2/S3 to measure whether this exit was right. Cancelled X12 (HYPE reclaim long, rule 13).
- BTC: X13 SHORT limit 80,420 (retest of the broken flip inside the 15m bear FVG 80,148-80,450), stop 80,700 above the FVG and 1h EMA50, target 79,880 in front of the 79,860 bull OB (1.93R), 0.2% risk (keeps a loss near the 1% scalp day stop). News scalp; the daily regime is still bull so B20 stays off.
- Equity $10,106.60 (+1.07%), room $224.6, scalp losses today $81.

## 2026-10-29 20:49 UTC — price 78,941
- 20:50 UTC (user: 'Binance got hacked? BTC can go down'). X13 BTC short hit target 79,880 at 20:35: +$33.20 (+1.64R). ETH early exit at 20:14 confirmed right: shadows S2/S3 both stopped at 2,288 (-1R each) = ~$36 saved (user's mirrored ETH longs hit SL).
- Hack check: no report in the news feeds or a web search (latest: Binance said on Oct 27 it blocked DPRK-linked attacks, no losses). Market evidence of Binance-specific stress: BNB -5.3% in the 20:15-20:30 15m vs BTC -1.9%, ETH -2.65%, SOL -2.7%. BTC prices agree across venues (Binance.US 78,834, OKX 78,820, Coinbase 78,755), so no BTC dislocation.
- BTC 78,800 after 80.4k -> 78,233: lost the 80k put wall, the 80,389 gamma flip (amplifying) and the 20-day low 79,179. Shorts, at location: X14 SHORT limit 79,150 (retest of the broken 20-day low), stop 79,650, target 78,150 (2R), 0.35%. X15 SHORT on a 15m close < 78,200 (continuation), stop 78,950, target 76,700 (2R), 0.2%. Not selling at 78.8k after a 2.5% drop.
- Conflict noted: a tested S20 long fires if the 00:00 4h candle closes back above 79,179. If Binance stress is real, that sample doesn't cover an exchange-risk event; the 00:00 run decides with that in mind.

## 2026-10-29 20:52 UTC — price 78,980
- 20:52 (user: 'Twitter says Binance hacked for $2.7B'). Can't open x.com from here. No confirmation anywhere I can reach: news feeds, Google News (24h) and web search show only the Polymarket third-party exploit (19:28) and old Binance incidents (2019 $41M, 2022 BNB Chain $570M). Treating it as an unconfirmed rumor that the tape is partly pricing (BNB -5.3% in one 15m vs BTC -1.9%). Positioning unchanged: short-biased via X14 (retest 79,150; BTC touched 79,178 at 20:51) and X15 (continuation below 78,200). If confirmed: cascade risk, X15 matters. If denied: snap-back squeeze; X14's 79,650 stop caps it. Desk: added an exchange-risk Google News feed (Binance/Coinbase/OKX/Bybit/Hyperliquid + hack/exploit/withdrawals paused/insolvency, polled every 2 min).

## 2026-10-29 21:12 UTC — price 79,193
- 21:12 (user: 'short is going back, people are betting on this level'). Agreed. BTC built a base at 78.2-79.2k: lows 78,233 / 78,533 / 78,788 held, 5m selling faded (-239, +84, 0 in the last three bars), BNB bounced 692 -> 713 (+3%: the Binance panic is fading, no hack confirmed), OI +3.5% 24h added into the lows (shorts trapped), 78k is the new 7d/30d put wall. X14's stop 79,650 also sat INSIDE the 5m bear FVG 79,099-79,750 (rule 16 mirror: it should have been above 79,750). Closed X14 at 79,158 (-$6.22, -0.18R); shadow S4 tracks it.
- Two-sided plan for the base: X16 LONG limit 78,650 (retest of the base at the 78k put wall), stop 78,150 below the 78,233 low, target 79,650 under the FVG top (2R). X15 SHORT kept for a 15m close below 78,200 (the base breaks = cascade resumes), stop 78,950, target 76,700. Gamma is -67M/1%: whichever side breaks will move fast.

## 2026-10-29 21:14 UTC — price 79,204
- 21:13 hourly (BTC already covered at 21:12: X16 long 78,650 / X15 short < 78,200 pending, flat otherwise).
- ETH 2,265: broke below the 2,288-2,325 demand zone and the 2,292 strong low on heavy selling (15m delta -162k); the zone failed. NO TRADE: mid-move after -2.7%, the next demand is far below; a short here sells the bottom. ETH weaker than BTC (-2.9% vs -1.8% vs 15m EMA200).
- HYPE 93.3: held 92.7, still above 15m/1h EMAs while BTC/ETH broke: relative strength from its own catalyst. NO TRADE: rule 13 (leader broken) blocks alt longs; revisit if BTC reclaims 80k.

## 2026-10-29 21:28 UTC — price 79,287
- 21:28 UTC: HACK CONFIRMED in the news feed: CoinDesk 'Multi-billion Binance hack hitting crypto markets' (21:12) and 'Tether freezes 971M USDT amid suspected Binance hack' (21:11). The user's read from Twitter was right ~35 min before mainstream pickup; the new exchange-risk feed flagged it impact 3.
- Shadow S4 resolved: X14's stop 79,650 would have been hit (21:15 high 79,766): closing at -$6 saved ~$29.
- Reaction so far: muted. BTC 79,220 (+0.1-0.3% after the headlines), base 78.2-79.2k intact, BNB steady ~710, OI +5% 24h (shorts), 7d gamma -66M (any break moves fast). The Tether freeze limits how much the hacker can dump.
- Orders: X16 -> X17 (same base long 78,650/78,150/79,650, cut to 0.2%: event risk); X15 short < 78,200 kept; NEW X18 ETH SHORT limit 2,300 (bounce into the broken 2,288-2,325 zone), stop 2,332, target 2,235 (2R), 0.2%: ETH is the weak link (stolen funds usually route through ETH).
- HYPE 93.9: still above its EMAs, no trade (rule 13 for longs; no short case against its strength).

## 2026-10-29 22:13 UTC — price 78,902
- 22:12 hourly: X17 BTC long FILLED 78,650 (22:05), now 78,930 (+0.56R). Hack details escalating: Decrypt 'Binance drained of $5.5B', The Block 'outflows up to $5.8B', CZ 'may have been hacked', Binance 'user funds completely safe', Tether+Circle froze $1.79B. Yet BTC holds the 78.2-79.9k base; BNB ~707; OI +7.1% 24h (shorts keep adding), 7d gamma -75M.
- X17: stop tightened 78,150 -> 78,450 (under the 78,533 higher low): event tail risk is still growing (the numbers keep rising), so cut the open risk from $20 to ~$8 while keeping the trade. Target 79,650 unchanged.
- X15 (short < 78,200) and X18 (ETH short limit 2,300; ETH 2,270, 15m delta -157k, weakest major) kept.
- HYPE 93.0: momentum fading (15m delta -342k) but above the 15m EMA50; no trade.
- Macro: Nasdaq-100 futures falling on Amazon/Intel earnings, Google -$500bn (AI fears): risk-off backdrop.

## 2026-10-29 23:14 UTC — price 78,832
- 23:13 hourly: X17 BTC long 78,760 (+0.22R), stop 78,450 / target 79,650 unchanged: the 78.2-79.7k base still holds; Reuters: Tether+Circle froze $2.38B, Decrypt: hacker hunting exit ramps, DeFi venues pausing markets (limits the dump). OI +7% 24h, 7d gamma -78M, 78k put wall.
- X15 (BTC short < 78,200) and X18 (ETH short limit 2,300, ETH 2,266 in a 2,251-2,294 box) kept.
- HYPE 90.9: lost its 15m EMA50, heading for the 90.2-91.9 bull OB; no trade (no location yet; rule 13 for longs).
- 00:00 UTC: the 4h candle (low 78,233) closes; S20 long only if it closes back above 79,179 (BTC 78,760 now, unlikely). The daily-loss floor resets to 97% of the 00:00 balance.

## 2026-10-29 23:55 UTC — price 78,094
- 23:54: X17 BTC long STOPPED 78,450 at 23:45 (-0.56R, -$11.29). Investing.com 23:37: 'Binance halts withdrawals amid $5.3B hack'; Cointelegraph: BNB -7%. BTC broke the 78.2k base to 77,896, now ~78,000 on the 78k put wall; 7d gamma -99M/1% (moves amplified), OI +7.8% 24h. Equity $10,122.28 (+1.22%).
- X15 SHORT (15m close < 78,200, stop 78,950, target 76,700) is the plan's other side: if the 23:45 candle closes below 78,200 at 00:00 it fills; kept (two-sided plan; the base broke on new exchange-crisis news). X18 ETH short limit 2,300 (ETH 2,254) kept to its 00:30 expiry. HYPE 89.1 broke its 89.95 range low: no trade.
- Lessons: rule 19 (no counter-trend longs during a live exchange crisis); X17 row (tightened stop saved ~$9).

## 2026-10-30 00:15 UTC — price 77,899
- 00:13 UTC (new day; daily floor $9,818.61, room $303.7): X15 BTC SHORT FILLED 77,966.9 at the 00:00 close (base break), stop 78,950, target 76,700, 0.2%; now 77,932 (+0.04R). HOLD.
- Daily closes: BTC 77,967, below the daily EMA50 80,563 but above the EMA200 76,420 (bull regime: B20 still off; no S10/S20, the 4h closed below 79,179). ETH closed 2,252.5 BELOW its daily EMA200 2,317 = ETH in a bear regime (B20 on ETH tested +0.21R n=39 t 1.0: not tradable, noted). Options: BTC call wall = put wall = 78,000 with 7d gamma -102M: a pin magnet at 78k inside an amplifying regime: expect whipsaws around 78k.
- ETH 2,245: X18 (short 2,300) left to expire 00:30; ETH never bounced into it. No chase.
- HYPE 89.5: holding 88.9-92.5, above its 1h/4h EMAs, 5m buyers +136k; relative strength persists. No trade (rule 19: no counter-trend longs in the exchange crisis; HYPE long would be against BTC's trend).
- News: Guardian/Investing.com: Binance investigating a reported $5.3B hack; withdrawals halted (23:37). BNB 694.8, sliding again.

## 2026-10-30 01:12 UTC — price 77,230
- 01:11 hourly: X15 BTC short 77,130 (+0.85R); low 76,739 came within $39 of the 76,700 target. Stop tightened 78,950 -> 78,300 (above the broken 78,233 base low: a reclaim there kills the breakdown), max loss now ~-0.34R. Why now: BNB bouncing 683 -> 701 (+2.6%) and BTC sitting near the 77k strike while 7d gamma is -103M; a squeeze back to the 78k put wall is possible. Target 76,700 unchanged. X18 expired unfilled.
- News: BBC/Guardian: $2.5bn frozen; CoinDesk: the hack drained reserve wallets backing customer assets; Binance says customer money is safe. Withdrawals still halted.
- ETH 2,218: new low 2,196 at the 2,200 put wall, 1h delta -224k; no trade (mid-move, no level to sell into). HYPE 90.8: buyers active (+251k 15m), holding 88.5+; no trade (rule 19).

## 2026-10-30 02:12 UTC — price 76,944
- 02:11 hourly: X15 BTC short hit TARGET 76,700 at 01:35: +$24.50 (+1.21R). Equity $10,146.78 (+1.47%), room $328. Scalp book 8 trades -0.26R (2 wins); today +$24.50.
- BTC 76,965 (low 76,472): extended 4.7% under the 1h EMA200, OI +11% 24h (crowded shorts), BNB recovering 695 -> 706, Treasuries rallying (flight to safety). 7d call wall now 75k, put wall 78k, gamma -105M. WSJ: Binance suspended transactions, 'possibly the biggest-ever heist'. No chase: X19 SHORT limit 77,800 (retest of the 78k wall / base underside), stop 78,350, target 76,600 (2.2R), 0.2%.
- ETH 2,201: pinned at the 2,200 call=put wall, still heavy selling. X20 SHORT limit 2,252 (bounce), stop 2,296 above the 5m bear OB, target 2,175 (1.75R), 0.15%.
- HYPE 89.9: back to its 5m EMA200, sellers (-270k 5m); no trade.
- No longs (rule 19).

## 2026-10-30 03:13 UTC — price 77,448
- 03:11 hourly: flat; X19 (BTC short 77,800) and X20 (ETH short 2,252) pending to 04:12. BTC 77,474 bouncing off 76,472 toward the 78k pin (7d call wall = put wall = 78k, gamma -117M); OI +9.9% 24h (shorts crowded), BNB back to ~711. Binance itself now says $6.3B affected (BBC/NYT): official, yet BTC +0.07% on it: the news is priced, which raises squeeze risk. Kept X19 as placed: it sells the pin from below with the stop above it (78,350), not the low.
- ETH 2,216: bouncing inside 2,180-2,219 under the 2,200 pin's resistance band; X20 kept. HYPE 90.9 back above its 5m/15m EMAs, no trade (rule 19). BOJ held rates, raised its 2027 inflation outlook.

## 2026-10-30 04:13 UTC — price 78,038
- 04:13 UTC: TESTED SWING SIGNAL. The 04:00 4h closed 78,200 after wicking to 76,472 below the 10/20-day low 77,896 = S10 + S20. Rule 19 (exchange crisis) weighed against it: BNB recovered 692 -> 717 (+3.6%), Binance's official $6.3B confirmation moved BTC only +0.1% (priced), OI +7.6% 24h (crowded shorts), 78k pin reclaimed, 5m/15m delta positive. Decision: TAKE IT at reduced size (0.35% total vs 0.5%): SW1a LONG 78,050 (S10 half, target 80,907 = 1.73R) + SW1b LONG 78,050 (S20 half, target 81,809 = 2.27R), stop 76,395.5 under the wick. Managed on 1h candles, one-shot hold (tested exits).
- X19 BTC short (77,800) CLOSED at 78,050 (-$12.10, -0.60R): the sweep-reclaim and the 78k reclaim invalidate 'sell the pin from below'; can't hold a short against a tested long signal. Shadow S5 tracks it. X20 expired.
- ETH 2,234 / HYPE 92.2: no trades (ETH still under its daily EMA200; HYPE fine but SW1 already carries the crypto-long risk, rule 14).

## 2026-10-30 05:12 UTC — price 78,576
- 05:11 hourly: SW1a/SW1b BTC longs 78,613 (+0.34R each); one-shot hold to 80,907 / 81,809, stop 76,395.5 unchanged (tested exits; no breakeven). BTC back above its 5m EMA50, 15m delta +2.1k, BNB 720 (recovered), 7d gamma -99M with the 78k call=put pin now below price and the flip at 80.0k overhead. Shadow S5 resolved -1R: closing X19 at 04:13 saved ~$8.
- Risk to watch: CoinDesk: the hacker split $1.4B of BTC into 19 wallets that can't be frozen = potential spot supply. If it hits exchanges, SW1's stop does the work (no pre-emptive cut on a headline that is supply risk, not a sale).
- ETH 2,251 at its 2,250 call=put pin; HYPE 93.3 strong above all EMAs. No new trades: SW1 already carries the crypto-long risk (rule 14).

## 2026-10-30 06:17 UTC — price 78,571
- 06:15 hourly: SW1a/b BTC longs 78,526 (+0.29R), stop 76,395.5 / targets 80,907 & 81,809 unchanged (tested one-shot hold). Quiet Asia: BTC in a tight 78.2-78.6k box above the 78k call=put pin, 5m ATR 122; 7d gamma -109M, flip 80.0k overhead (above it gamma turns supportive). Saylor: Strategy has $30B credit capacity for more BTC buys (supportive).
- ETH 2,243 under its 2,250 pin, sellers on 5m/15m; HYPE 93.0 drifting with sellers (-617k 1h) but above all EMAs. No new trades: SW1 is the crypto-long risk (rule 14), no shorts against a tested BTC long.
- Watch: European open; stocks, yields and gold all falling pre-Europe (risk-off cross-asset).

## 2026-10-30 07:25 UTC — price 78,462
- 07:24 hourly: SW1a/b BTC longs 78,456 (+0.25R), stop/targets unchanged. Still boxed 78.2-78.6k on the 78k call=put pin (7d gamma -117M, flip 79.7k): a coil; whichever side breaks will run. OI cooling (+3.8% 24h from +11%: shorts covering). Treasury yields at multi-week lows (supportive). Bloomberg full coverage of the $6.3B hack: no new price impact.
- ETH 2,248 on its 2,250 pin, OI -2.4% 24h (deleveraging); HYPE 93.2 above all EMAs, mild selling. No new trades (rule 14; no shorts against the tested BTC long). European open next.

## 2026-10-30 08:14 UTC — price 78,089
- 08:13 hourly: SW1a/b BTC longs back to entry (78,068, +0.01R); the 08:00 4h closed 78,139 (low 77,883) and held above the 76,472 sweep wick. HOLD to 80,907 / 81,809, stop 76,395.5 (tested one-shot hold: no early exit at breakeven). Options re-struck: 7d gamma -34M (much less negative), put wall 77k, call wall 79k, flip 79.6k: a 77-79k range now. OI +1.7% 24h (froth gone).
- ETH 2,230 weak (15m delta -24k, OI -3.1%); HYPE 91.4 lost its 15m EMA50 (15m delta -373k). No new trades: SW1 carries the crypto risk (rule 14) and no shorts against the tested BTC long.

## 2026-10-30 09:13 UTC — price 77,800
- 09:12 hourly: SW1a/b BTC longs 77,777 (-0.17R): drifting toward the 77k put wall with Nasdaq futures tumbling (Investing.com) and 15m delta -1.6k. HOLD, stop 76,395.5 (under the 76,472 sweep wick) unchanged: the setup is invalid only below the wick, and 77k is the new put wall (support) between price and the stop. No early exit, no averaging down.
- ETH 2,225 weak under all EMAs; HYPE 91.7 at its 15m EMA50 with sellers. No trades (rule 14; no shorts against the tested BTC long). HOOD sliding pre-market (watch only).

## 2026-10-30 10:21 UTC — price 77,337
10:17 UTC hourly. BTC 77,340: SW1a/SW1b held (-0.43R), stop 76,395.5 below the 77k put wall and the 76,472 sweep low; tested one-shot hold, no change. No new 4h signal (08:00 close 78,138.6); daily still BULL (77,967 vs EMA200 76,420), so B20 off. 1h -2,271 BTC taker delta, below all EMAs: weak, but shorting into the 77k put wall with a live tested long is rule 14 (one bet) and bad location (rule 16). ETH 2,222: below EMAs, sitting on the 2,200 put wall; no short into support, no long without a reclaim of 2,240 (call wall). HYPE 91.7: range above 1h EMAs, -512k taker delta in 12h, no edge either way. D1F: no level within reach on any market. News: Bloomberg ties the stock/tech dip to the Binance hack; nothing new. No orders.

## 2026-10-30 11:20 UTC — price 77,644
11:16 UTC hourly. BTC 77,540: SW1a/SW1b held (-0.26R); 4h/1d: below 4h EMA50/200, above daily EMA200 76,432, inside the daily bull FVG 77,150-80,803; stop 76,395.5 stays under the sweep low and the 77k put wall. No new S10/S20/B20/D1F signal. New headline: Binance finds 'additional points of breach' (BI); BTC did not react (-0.02%). ETH 2,241 reclaimed 2,240 (the 10:17 long condition) but SKIPPED, shadow SH6: correlated with SW1 (rule 14), counter-trend long in an exchange crisis on a fresh breach headline (rule 19), 2,280 call wall caps it at 1.5R (rule 15). HYPE 93.1: strongest of the three through the hack (1h up BOS, above all EMAs and weekly VWAP 88.1), range 90.7-93.8 since 05:00. ORDER: X21 scalp long on a 15m close above 93.85, stop 92.55, 1.6R from the fill (~95.9 at a 93.85 fill), 0.25% risk (correlated with SW1), expires 13:19. No short: trend up, selling into a range top that has held is not location. (X20 first, cancelled: that id was used by an expired order earlier today.) Desk fix: every scalp order (close triggers too, not just limits) now expires after 2h by default (rule 12).

## 2026-10-30 12:13 UTC — price 77,525
12:11 UTC hourly. BTC 77,527: 12:00 4h closed 77,343.7 (low 77,188), no new S10/S20 (20-day low 76,472 still holds) and daily still BULL (EMA200 76,431), so no B20. SW1a/SW1b held at -0.32R: stop 76,395.5 under the sweep low; the put wall 77k has held all morning. US ECI q/q at 12:30 (medium, not top-impact): no rule block, but nothing new on BTC either way. ETH 2,240 sits on the 2,240 put wall, under 15m EMA50 2,244; shadow SH6 open, no trade (rules 14/19 unchanged). HYPE 92.1 slipped back from 93.5 with -833k 1h taker delta and OI -2% 24h: buyers fading at the range top. X21 (15m close > 93.85) kept: it only fires on a real break, expires 13:19. No HYPE short: trend up, 92 is mid-range. News: FBI/Secret Service on the Binance case, North Korea suspected; Trump says Iran war 'wrapped up soon'; tech sell-off. No new orders.

## 2026-10-30 13:23 UTC — price 77,351
13:21 UTC hourly. X21 EXPIRED unfilled at 13:19: HYPE never closed a 15m above 93.85 and fell back to 91.1. Waiting for the close instead of buying the 93.5 push kept the desk out of a failed break. BTC 77,374: SW1a/SW1b held (-0.41R), no new 4h bar since 12:00; stop 76,395.5 under the sweep low, 77k put wall still holding. Binance says it has $6.34B ready to cover the hack (The Block) and is working with the FBI: insolvency fear easing, which supports the tested long. ECI released 12:30, no reaction. ETH 2,232: below 5m/15m EMAs in the 2,200-2,240 box, no edge; SH6 open. HYPE 91.1 at the floor of the 90.7-93.8 range, 1h trend still up. ORDER: X22 scalp long, limit 90.85, stop 90.25 (beyond the 90.72 low), target 92.3 (2.4R, under the 92.6/93.8 supply), 0.25% risk (correlated with SW1), expires 15:22. Against it: 1h taker delta -369k and OI -4.8% 24h. No short: selling the floor of a range in a 1h uptrend is selling the bottom.

## 2026-10-30 13:45 UTC — price 76,930
13:43 UTC on-demand run (user check-in). X22 HYPE long FILLED 13:25 at 90.85; post-fill lows 90.70/90.72 held, now 91.5 (+1R). ORDER: X22 stop 90.25 -> 90.60 (under the post-fill double low; BTC just lost the 77k put wall, and HYPE is a correlated long), target 92.3 unchanged. BTC 76,976: US cash open sold crypto and crypto stocks; 15m taker -1,552 BTC, broke the 77k put wall in negative gamma (-45M). SW1a/SW1b held at -0.66R: stop 76,395.5 under the 76,472 sweep low is the tested invalidation, no new 4h bar yet, daily still BULL; no early exit and no short against it (rules 14/19). ETH 2,221 broke back under the 2,240 box with BTC: no trade; SH6 shadow is near -0.75R (the skip is saving money). HOOD (Nasdaq, watch only, not a Propr instrument): gapped from ~91 to an 82.34 open low (-9%) on the Binance hack hitting crypto stocks plus the tech sell-off; now 84.4 above session VWAP 83.4, inside the daily bull OB 83.7-89.5, under the bear gap FVG 84.6-91.3; daily below EMA50 103.5 and EMA200 98.7. Paper plan, both sides, tracked here only: SHORT a failed bounce at 86.5-87.5 (gap fill rejection), stop 88.7, target 82.3 (~2R); LONG only on a 15m close back above 88.95 (the broken swing low) with the open low holding, stop 86.4, target 92.4 (~1.4R: below the bar, so watch only unless the open low retest holds first). No HOOD entry in the first 30 min after the open.

## 2026-10-30 13:51 UTC — price 76,764
13:52 UTC (user: BTC 4h reaching support). BTC 76,811 is entering the 4h bull OB 74,909-77,324 (daily OB 74,909-78,223, daily bull FVG 73,400-76,510, daily EMA200 76,423). 4h below EMA50 80,369/EMA200 81,401, last 4h BOS down; 12-bar 4h taker -5,794 BTC; OI +4.2% 24h with funding flat 0.01%: shorts adding into support. Negative gamma all expiries (-46M 7d): moves overshoot; top strikes 77k/75k, 30d put wall 74k. Problem found: SW1's tested stop 76,395.5 sits inside this zone (lessons row added). Not widened. ORDER: X23 scalp long limit 75,700 (lower half of the zone), stop 74,750 (beyond the 74,909 swing low), target 77,250 (1.63R, under the 15m bear FVG 77,017-77,242), 0.35%, expires 22:00. It only fills after SW1 stops, so it re-enters with the stop beyond support instead of adding a second bet. Short side: none into support. If the daily closes under EMA200 76,423 at 00:00 the regime turns BEAR and B20 (4h close under the 20-day low) goes live; a 4h close under 74,909 voids the zone. Desk fix: the 3-open cap counts scalps only (the two SW1 halves were blocking every new scalp order).

## 2026-10-30 14:19 UTC — price 76,894
14:18 UTC hourly. X22 HYPE CLOSED at 90.60 (stop, -0.57R, -$14.39): my 13:43 tightening put the stop 0.1 under the 90.70/90.72 equal lows; HYPE swept them to 90.51 and is back at 90.9, original stop 90.25 untouched. Lessons row + rule 20 (no stops just under equal lows); shadow SH7 scores the untightened plan. No HYPE re-entry: SH7 already tracks that exact trade, BTC flow is heavy and a third correlated long would be the same bet (rule 14). BTC 76,672: SW1a/SW1b held at -0.83R (stop 76,395.5); 76,472 low still intact; OI +9.4% in 24h while price fell = big new positioning into the zone (squeeze fuel if 76.4k holds, acceleration if it breaks); 5m/15m/1h taker all negative (-2.3k/-2.8k/-2.4k BTC). X23 limit 75,700 / stop 74,750 / target 77,250 kept (expires 22:00). Next 4h close 16:00: a wick under 76,472 with a close back above = fresh S10/S20. News: analysts tell clients to buy crypto stocks; Binance pledges to cover losses (NBC); exploit was EIP-7702 related (Decrypt). ETH 2,215 broke 2,220, 15 above the 2,200 put wall: no short into it, no long against the trend. Account $10,120.29 (+1.20%), room $301.68.

## 2026-10-30 15:16 UTC — price 77,810
15:14 UTC hourly. BTC held the zone: low 76,567 (above the 76,472 sweep low and SW1's 76,395.5 stop), bounced to 77,708 as $1.3B of longs liquidated (Yahoo); 5m taker +2,434 BTC, back above 5m EMA50; OI +10.2% 24h. SW1a/SW1b -0.21R, held. X23 (75,700) now 2.6% away; kept to 22:00 in case of a second leg. Shadows resolved: SH7 (X22 untightened) hit target +2.42R, so my 13:43 tightening cost ~3R (~$75), lessons row updated (rule 20); SH6 (skipped ETH long) hit its stop -1R: that skip saved $25. ETH 2,251 broke up out of the 2,205-2,240 box (15m taker +21k ETH). ORDER: X24 scalp long limit 2,241 (box-top retest), stop 2,221 (beyond session VWAP 2,225), target 2,278 (under the 2,280 call wall) = 1.85R, 0.25% (correlated with SW1), expires 17:16. HYPE 93.0 back at the range top 93.5-93.8 with 5m taker +104k: no second correlated long; one alt long at a time (ETH has the better location: a limit at support, not a breakout at resistance). No shorts: everything bounced off support with buyers in control.

## 2026-10-30 16:17 UTC — price 77,590
16:15 UTC hourly. X24 ETH long FILLED 15:25 at 2,241 and STOPPED 15:50 at 2,221 (-1.11R, -$28.12): ETH wicked to 2,215.56 under the session VWAP and came back to 2,233. Stop was on the liquidity (0.37 ATR15m past VWAP); lessons row + rule 21 (scalp stops >= 1 ATR15m beyond the level). Scalp book 11 closed, -2.54R; today net scalp -$30. BTC 16:00 4h closed 77,570, low 76,567: held above the 76,472 sweep low, no fresh S10/S20 (no wick under the 20-day low). Daily BULL. SW1a/SW1b -0.30R, held. 7d gamma flip dropped to 78,182, call wall now 82k: above 78.2k dealers stop amplifying. X23 limit 75,700 kept to 22:00. ETH 2,233 mid-range after a failed breakout and a sweep: no trade, no revenge entry. HYPE 91.8 mid-range, OI -8.5% 24h (longs leaving): no trade. No shorts: BTC holding the 4h demand zone with the daily trend up. Room $273.55: size stays at 0.25% on correlated scalps.

## 2026-10-30 17:14 UTC — price 77,195
17:12 UTC hourly. BTC 77,160 drifting back toward the 77k put wall inside the 4h demand zone; 1h taker -2,952 BTC; OI +11.4% 24h. SW1a/SW1b -0.54R held (stop 76,395.5); X23 limit 75,700 kept to 22:00. News: Binance to publish full proof of reserves by Monday (CNBC) - supportive. ETH 2,241 retesting the box top again: SKIPPED under rule 21 - a stop 1 ATR15m beyond the swept 2,215.56 low (~2,212) against the 2,278 target (under the 2,280 call wall) is 1.28R, below 1.5. HYPE 91.2 mid-range. ORDER: X25 scalp long limit 90.75 (range floor), stop 89.62 (1 ATR15m beyond the swept 90.51 low, rule 21), target 92.6 (1.64R), 0.25%, expires 19:13. Against it: OI -5% and 1h taker -331k. No shorts: BTC still in the demand zone with the daily trend up.

## 2026-10-30 18:13 UTC — price 77,014
18:11 UTC hourly. X25 HYPE long FILLED 17:30 at 90.75; HYPE swept to 90.19 (under the 90.51 low again) and is 90.65 now: the rule-21 stop 89.62 kept it alive where the old habit would have been taken out. Held, -0.09R, target 92.6. 5m/15m taker turned positive (+70k/+48k HYPE). BTC 77,086 pinned on the 77k put wall; 15m/1h taker -2.2k/-2.7k BTC; OI +12.4% 24h. SW1a/SW1b -0.58R held; X23 limit 75,700 to 22:00. Open+pending risk $106.79 of a $136.78 cap: no room for another order until something resolves, and none is wanted. ETH 2,241 sits at the box top again: the 1.28R skip from 17:12 still stands. CNBC: why bitcoin held up better than feared after the hack. No new orders.

## 2026-10-30 19:15 UTC — price 76,437
19:11 UTC hourly. Bad hour: X25 HYPE long STOPPED 18:35 at 89.62 (-1.08R, -$27.24) and SW1a/SW1b BTC longs STOPPED 19:00 at 76,395.5 (-1.05R each, -$37.12): BTC flushed to 76,260, 135 under the swing stop that sat inside the 4h demand zone, and is back at 76,670; HYPE hit 89.07 and is back at 90.4. One correlated bet, one 25-min flush, -$64 (rule 14). Day -$94.5; equity $10,027.80 (+0.28%), room $209.18. TEST (new quant/intraday_level_test.py): every intraday 24h-level pattern loses after fees in both directions (-0.08 to -0.30R, t -1 to -9); my scalp book (12 closed, -0.30R/trade) matches it. Rule 22: scalp risk 0.35% -> 0.2% (code default and the hourly task's prompt updated), scalps need a catalyst or 4h/1d location. ORDERS: (1) SW2a/SW2b tested S10/S20 sweep-reclaim, CONDITIONAL on the 20:00 4h close above 76,472 (the 16:00 candle wicked to 76,260 under the 10/20-day low); stop 0.1% under the candle low; 1.5R / 2R; 0.175% each (0.35% total, size cut for the room); expire 20:05 if no signal. (2) X23 cancelled and re-placed as X26 at 0.2%: limit 75,700, stop 74,750, target 77,250 (1.63R), to 22:00. ETH 2,234 and HYPE 90.4: no trade (rule 22: no catalyst, no HTF location). BTC 1h taker -4.2k BTC, OI +13.9% 24h: crowded; a reclaim would squeeze it.

## 2026-10-30 20:14 UTC — price 76,905
20:12 UTC hourly. SIGNAL: the 16:00 4h closed 76,876.2 after wicking to 76,260 under the 10/20-day low 76,472 = tested S10+S20 sweep-reclaim (setup_scan 'SIGNAL NOW'). SW2a/SW2b had been EXPIRED by this run before the 20:00 candle was read (desk bug, fixed in process(): candles that closed before expiry count first). Re-instated at the 19:12 terms; price 76,883-76,927 was at the planned entry (rule: a fired plan trigger within 0.25R gets taken). ENTERED SW2a/SW2b BTC long 76,876.2, stop 76,183.7 (0.1% under the wick), targets 77,914.9 (1.5R) / 78,261.1 (2R), 0.175% each ($18 each). Context: daily still BULL (EMA200 76,420); 5m taker +841 BTC; 1h still -4.5k; OI +10.8% 24h with price back above the sweep = shorts trapped under 76.5k if it holds; 7d gamma flip 78,041 sits between the targets. X26 limit 75,700 sits under SW2's stop, so the two can't be open together; kept to 22:00. ETH 2,239 and HYPE 90.1: no catalyst, no HTF location (rule 22), no trade. MarketWatch: Fed officials see more hikes; bond yields fell sharply in October (flight to safety).

## 2026-10-30 21:13 UTC — price 76,647
21:12 UTC hourly. SW2a/SW2b BTC long 76,876 held at -0.34R (BTC 76,639); stop 76,183.7 under the 76,260 sweep wick, the tested invalidation; no change. 1h taker -3.6k BTC, OI +7% 24h (down from +13.9%: some of the crowd closed). Trump: US looking at whether North Korea did the Binance hack; calls for crypto rules (The Block/Bloomberg) - BTC -0.3% on it, no break. X26 limit 75,700 expires 22:00 (sits under SW2's stop). Daily close at 00:00 vs EMA200 76,420 decides the regime: a close below turns B20 shorts on. ETH 2,236 and HYPE 90.1: flat, no catalyst or HTF location (rule 22), no trade.

## 2026-10-30 22:12 UTC — price 76,858
22:11 UTC hourly. X26 (75,700) EXPIRED unfilled: BTC never revisited the lower half of the zone. SW2a/SW2b held at -0.05R (BTC 76,838), stop 76,183.7, targets 77,915/78,261; 5m/15m taker turned slightly positive. Daily close at 00:00 vs EMA200 76,420 still decides the regime. ETH 2,240 on the 2,240 put wall, flat: no trade. HYPE 89.3 sliding toward the 1h EMA50 88.74 and the 88.45 15m low with OI -5.2% (longs closing): no short (no catalyst, no HTF level under rule 22; selling into the 1h EMA50 is selling the bottom of a 1h uptrend), no long (falling knife, rule 22). No new orders.

## 2026-10-30 23:12 UTC — price 77,029
23:11 UTC hourly. SW2a/SW2b +0.26R (BTC 77,053, back above the 77k put wall; 5m/15m taker +858/+828 BTC); stop 76,183.7, targets 77,915/78,261; held. Daily close at 00:00 is set to stay above EMA200 76,420 (regime BULL, B20 off). HYPE catalyst checked: Bloomberg 22:53 'NYSE owner plans Hyperliquid perpetuals market in US'. Tape: no reaction (89.1-89.4 on thin 5m volume, OI -12.4% 24h). No trade: a catalyst the market ignores is not a repricing (rule 18 wants tape confirmation), and the confirmation long (15m back above 90.9, stop under the 88.45 low, target the 93.9 range top) is 1.2R. ETH 2,239 pinned at the 2,240 call/put wall: no trade. No calendar events listed for the next 7 days.

## 2026-10-31 00:13 UTC — price 77,277
00:12 UTC Sat 31 Oct hourly. Daily closed 77,286.8 above EMA200 76,428.5: regime stays BULL (B20 off). 20:00 4h closed 77,286.8, low 76,543: no new signal; 10/20-day low is now 76,260 (yesterday's sweep). New day: 00:00 balance $10,027.80, daily floor $9,726.96, room $300.83. SW2a/SW2b +0.58R (BTC 77,277), stop 76,183.7, targets 77,915/78,261; 15m taker +1,230 BTC; held. Yesterday (Fri 30 Oct): -$94.5 net. Wins X15 (+1.21R). Losses X19, X22, X24, X25, SW1a/b. Lessons: rules 20 (no stops under equal lows), 21 (1 ATR15m wick room), 22 (intraday levels test negative after fees: scalps 0.2% and need a catalyst or HTF location). ETH 2,245 and HYPE 89.6 (OI -10.8% 24h, deleveraged): no catalyst with tape confirmation and no HTF level in reach; no trade. D1F: no level within reach on any market.

## 2026-10-31 01:12 UTC — price 77,462
01:11 UTC hourly. SW2a/SW2b +0.84R (BTC 77,457, above 5m EMA200 for the first time since the flush; 15m taker +1,203 BTC); SW2a's 1.5R target 77,915 is 0.6% away, SW2b 78,261 sits just above the 7d gamma flip 78,161. Held, no change (tested one-shot exits). OI +1.1% 24h: the crowd that piled in on the way down has mostly closed. ETH 2,246 and HYPE 89.5 drifting with no catalyst and no HTF level in reach: no trade (rule 22). Quiet Asia session; no calendar events.

## 2026-10-31 02:12 UTC — price 77,350
02:11 UTC hourly. SW2a/SW2b +0.70R (BTC 77,359), quiet Asia drift between 77,240 and 77,460; stop 76,183.7, targets 77,915/78,261; held. OI flat 24h (-0.1%). ETH 2,243 pinned at the 2,240 strike, HYPE 89.8 in range, OI -9% 24h: no catalyst, no HTF level, no trade (rule 22). News quiet (Patriot sale to Ukraine; an 'AI hacking' warning piece on the Binance breach).

## 2026-10-31 03:11 UTC — price 77,276
03:10 UTC hourly. SW2a/SW2b +0.55R (BTC 77,257), tight Asia range (5m ATR 68), 1h taker -2.2k BTC; stop 76,183.7, targets 77,915/78,261; held. ETH 2,241 pinned at the 2,240 call/put strike; HYPE 89.3 in range with OI -9% 24h: no catalyst, no HTF level, no trade (rule 22). News quiet (BBC: North Korea prime suspect in the Binance hack, already priced).

## 2026-10-31 04:12 UTC — price 77,153
04:11 UTC hourly. 00:00 4h closed 77,107 (low 77,064): no new signal; daily BULL. SW2a/SW2b +0.49R (BTC 77,217), 1h taker -2.2k BTC, holding the 77k put wall; stop 76,183.7, targets 77,915/78,261; held. Geo: Iran says four tankers on fire after striking mines in Hormuz (Al Jazeera, 16m ago): oil risk into a weekend; BTC +0.1%, no reaction yet. Not a crypto catalyst with a tape reaction, so no trade; the swing stop is the risk control. ETH 2,239 pinned at 2,240; HYPE 89.2 sliding with 15m taker -63k toward the 1h EMA50 88.9 and the 88.45 low: no HTF level or catalyst, no trade (rule 22).

## 2026-10-31 05:12 UTC — price 77,231
05:11 UTC hourly. SW2a/SW2b +0.52R (BTC 77,235, quiet on the 77k put wall); stop 76,183.7, targets 77,915/78,261; held. HYPE 88.7 broke under its 1h EMA50 (88.87) and 15m EMA200 with volume (15m taker -157k, 1h -276k), 0.25 above the 88.45 swing low: no short (selling into a swing low after the break is selling the bottom; no catalyst or 4h/1d resistance to sell from, rule 22), no long (falling). ETH 2,240 pinned. CoinDesk: BTC stolen from Binance now exceeds Tesla's holdings (context, no reaction).

## 2026-10-31 06:12 UTC — price 77,229
06:11 UTC hourly. SW2a/SW2b +0.51R (BTC 77,228, 5m ATR 70: dead calm on the 77k put wall); stop 76,183.7, targets 77,915/78,261; held. HYPE 88.2 broke the 88.45 swing low (15m taker -108k, OI -10% 24h): no short at the low after the break, no 4h/1d resistance to sell from, no catalyst (rule 22); no long into a breakdown. ETH 2,241 pinned at 2,240. No news of note.

## 2026-10-31 07:12 UTC — price 77,349
07:11 UTC hourly. SW2a/SW2b +0.70R (BTC 77,363, back above 5m EMA200, 1h taker turned positive +149 BTC); stop 76,183.7, targets 77,915/78,261 (7d gamma flip now 78,230); held. HYPE 88.2 holding just under the broken 88.45 low, 5m taker positive +41k but 1h -211k; OI -10.5%: no trade (rule 22). ETH 2,242 pinned. No news, no calendar.

## 2026-10-31 08:12 UTC — price 77,351
08:11 UTC hourly. 04:00 4h closed 77,297 (low 77,050): no new signal; daily BULL. SW2a/SW2b +0.64R (BTC 77,322); stop 76,183.7, targets 77,915/78,261; held. Positioning shift: 7d gamma turned positive (+1.0M/1%) with the flip at 77,223 just under price: above it dealers dampen moves (expect chop/pin, slower path to the targets, but also cushioned dips). HYPE 87.9 grinding lower (1h taker -168k, OI -10.9% 24h), 4.5% above the D1F level 82.55 and the 1h EMA200 83.5: no trade yet (rule 22: no catalyst; HTF level not in reach). ETH 2,243 pinned. No news.

## 2026-10-31 08:25 UTC — price 77,340
08:23 UTC (user check-in). Record since start: 15 closed = 3 targets (L1, X13, X15: +$245.38), 8 stops (all longs: -$195.36), 4 manual exits (-$22.21); then SW2a/SW2b closed manually at 77,340 (+0.56R each, +$19.60). New: quant/confluence.py (9 tested indicator checks) and lessons rule 23 (one decision %, trade >= 60%, veto against |S| >= 7). Tests: trading against a strong score -0.17 to -0.22R (t -3.4); with it ~0R; S10/S20 rebuilt ~0R overall, no score bucket positive. SW2 closed because its setup is marginal and BTC scored -5 (78% short); shadows SH8/SH9 score the exit. DECISIONS (rule 23): BTC -5/9: long 22% (+5 S10/S20 context = 27%) NO; short 78% -15 (77k put wall + 4h/1d demand 74.9-77.3k under price: target into a zone) -15 (no catalyst, no HTF resistance to sell from) = 48% NO. ETH -5/9 (daily close now under EMA200): long 22% NO; short 78% -15 (pinned on the 2,240 strike, target into the 2,200 put wall) -15 (no catalyst/HTF level) = 48% NO. HYPE +3/9: long 67% -15 (no catalyst/HTF level, falling through the 1h EMA50) = 52% NO; short 33% NO. Flat. Equity $10,047.40 (+0.47%).

## 2026-10-31 09:12 UTC — price 77,366
09:11 UTC hourly. Flat. Equity $10,047.40 (+0.47%), room $320.43. Shadows SH8/SH9 (SW2 held to plan) open; BTC 77,372 vs targets 77,915/78,261. DECISIONS (rule 23): BTC -5/9: long 22% NO; short 78% -15 (target into the 77k put wall / 4h-1d demand 74.9-77.3k; 7d gamma positive above the 77,228 flip = pinned) -15 (no catalyst, no HTF resistance to sell from) = 48% NO. ETH -5/9: long 22% NO; short 78% -15 (on the 2,240 put wall) -15 (no catalyst/HTF level) = 48% NO. HYPE +1/9 (fell from +3; 15m broke down with -188k taker, OI -9.6%): long 56% -15 (falling, no catalyst/HTF level) = 41% NO; short 44% -15 (no catalyst/HTF resistance) = 29% NO. News: Iran war-risk pieces only, no crypto catalyst.

## 2026-10-31 10:12 UTC — price 77,402
10:10 UTC hourly. Flat; equity $10,047.40, room $320.43. Shadows SH8/SH9 open (BTC 77,411). DECISIONS (rule 23): BTC -5/9: long 22% NO; short 78% -15 (target into the 77k put wall/4h-1d demand; 7d gamma +3.8M above the 77,210 flip = pinned) -15 (no catalyst/HTF resistance) = 48% NO. ETH -5/9: long 22% NO; short 78% -15 (2,240 put wall under price) -15 = 48% NO. HYPE +1/9 (87.1, 15m taker -228k, sliding toward the 1h EMA200 83.5 and D1F level 82.55): long 56% -15 (falling, no catalyst/level yet) = 41% NO; short 44% -15 (no catalyst/HTF resistance) = 29% NO. Watch: HYPE near 82.5-83.5 (D1F flip level + 1h EMA200) is the first place a long could get HTF location. News: Binance-hack commentary only.

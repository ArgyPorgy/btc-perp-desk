// Live consistency test of the order book against Binance (read-only, ~40 s).
// Book A syncs at the start. Book B syncs later from a separate snapshot. Both then consume the same events.
// If the sync logic is exact, every price level inside B's snapshot range must match A exactly.
//   node tests/test_book_live.js
import { OrderBook } from '../js/book.js';

const REST = 'https://fapi.binance.com';
const ranges = {};
const snapFor = (name) => async () => {
  const s = await fetch(`${REST}/fapi/v1/depth?symbol=BTCUSDT&limit=1000`).then((r) => r.json());
  ranges[name] = { lo: +s.bids[s.bids.length - 1][0], hi: +s.asks[s.asks.length - 1][0] }; // what this snapshot covered
  return s;
};
const A = new OrderBook(snapFor('A'));
const B = new OrderBook(snapFor('B'));
let bOn = false, events = 0;

const ws = new WebSocket('wss://fstream.binance.com/public/stream?streams=btcusdt@depth@100ms');
ws.onmessage = (m) => {
  const e = JSON.parse(m.data).data;
  events++;
  A.onEvent(e);
  if (bOn) B.onEvent(e);
};
setTimeout(() => { bOn = true; }, 12000);

setTimeout(async () => {
  ws.close();
  // compare only prices that BOTH snapshots covered; outside that, each book legitimately knows different levels
  const minBid = Math.max(ranges.A.lo, ranges.B.lo), maxAsk = Math.min(ranges.A.hi, ranges.B.hi);
  console.log(`common snapshot range ${minBid} - ${maxAsk}`);
  let compared = 0, mismatches = 0;
  for (const side of ['bids', 'asks']) {
    const prices = new Set([...A[side].keys(), ...B[side].keys()]);
    for (const p of prices) {
      if (p < minBid || p > maxAsk) continue;
      compared++;
      if ((A[side].get(p) || 0) !== (B[side].get(p) || 0)) mismatches++;
    }
  }
  const a = A.best(), b = B.best();
  console.log(`events ${events} | A synced ${A.synced} resyncs ${A.resyncs} | B synced ${B.synced} resyncs ${B.resyncs}`);
  console.log(`best A ${a.bid}/${a.ask}  best B ${b.bid}/${b.ask}  crossed: ${a.bid >= a.ask}`);
  console.log(`levels compared ${compared}, mismatches ${mismatches}`);
  const ok = A.synced && B.synced && a.bid < a.ask && mismatches === 0 && compared > 500;
  console.log(ok ? 'PASS' : 'FAIL');
  process.exit(ok ? 0 : 1);
}, 40000);

// Indicator tests: synthetic cases + live cross-checks against Binance / Deribit (read-only).
//   node tests/test_indicators.js
import assert from 'node:assert/strict';
import { vwapBands, dayKey, deltaCvd, structure, fairValueGaps, volumeProfile, consolidation, atr, dailyAuction, scorecard } from '../js/indicators.js';
import { computeGex, parseInstrument } from '../js/gex.js';
import { backfillAggTrades, Footprint } from '../js/footprint.js';
import { execFileSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

// resolve from this file, so the test runs from the project root or from dashboard/
const GEX_PY = fileURLToPath(new URL('../../quant/gex.py', import.meta.url));

const REST = 'https://fapi.binance.com';
let passed = 0;
const ok = (name) => { passed++; console.log('ok ', name); };
const bar = (time, o, h, l, c, v = 10, tb = 5) => ({ time, open: o, high: h, low: l, close: c, volume: v, takerBuy: tb });

// --- VWAP: hand-computed
{
  const b = [bar(0, 1, 3, 1, 2, 1), bar(60, 2, 6, 3, 3, 3)]; // hlc3 = 2, 4
  const v = vwapBands(b, dayKey);
  assert.equal(v.vwap[1], (2 * 1 + 4 * 3) / 4);
  const sd = Math.sqrt((4 * 1 + 16 * 3) / 4 - 3.5 ** 2);
  assert.ok(Math.abs(v.up1[1] - (3.5 + sd)) < 1e-12);
  const reset = vwapBands([bar(86399, 1, 1, 1, 1), bar(86400, 9, 9, 9, 9)], dayKey);
  assert.equal(reset.vwap[1], 9); // new UTC day starts fresh
  ok('VWAP + bands + daily reset');
}
// --- delta / CVD
{
  const dc = deltaCvd([bar(0, 1, 1, 1, 1, 10, 7), bar(60, 1, 1, 1, 1, 4, 1), bar(86400, 1, 1, 1, 1, 2, 2)]);
  assert.deepEqual(dc.delta, [4, -2, 2]);
  assert.deepEqual(dc.cvd, [4, 2, 2]);
  ok('delta = taker buy - taker sell, CVD resets daily');
}
// --- structure: rise to a swing high, pull back, break it (BOS), then break the swing low (CHoCH)
{
  const closes = [10, 11, 12, 13, 14, 15, 14, 13, 12, 11, 10, 11, 12, 13, 14, 15, 16, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6];
  const b = closes.map((c, i) => bar(i * 60, c, c + 0.2, c - 0.2, c));
  const st = structure(b, 3);
  const kinds = st.events.map((e) => `${e.side > 0 ? 'up' : 'down'}-${e.kind}`);
  assert.ok(kinds.includes('up-BOS') || kinds.includes('up-CHoCH'), kinds.join());
  assert.equal(st.events[st.events.length - 1].side, -1, 'last break should be down');
  assert.equal(st.events[st.events.length - 1].kind, 'CHoCH');
  ok(`structure breaks: ${kinds.join(', ')}`);
}
// --- FVG: a gap up that later gets filled
{
  const b = [bar(0, 10, 10.5, 9.5, 10), bar(60, 10, 13, 10, 12.9), bar(120, 13, 14, 12, 13.5)];
  const a = atr(b);
  assert.equal(fairValueGaps(b, a, 0).length, 1);
  b.push(bar(180, 13, 13, 10, 10.2)); // trades through the whole gap
  assert.equal(fairValueGaps(b, atr(b), 0).length, 0);
  ok('fair value gap created then filled');
}
// --- volume profile: all volume at one level -> POC there
{
  const b = [bar(0, 100, 101, 99, 100, 1), bar(60, 100, 100.4, 100.2, 100.3, 1000), bar(120, 100, 105, 95, 100, 1)];
  const p = volumeProfile(b, 0, 2, 50, 0.7);
  assert.ok(Math.abs(p.poc - 100.3) < p.step, `poc ${p.poc}`);
  assert.ok(p.val <= p.poc && p.vah >= p.poc);
  ok('volume profile POC / value area');
}
// --- consolidation breakout with volume
{
  const b = [];
  for (let i = 0; i < 30; i++) b.push(bar(i * 60, 100, 103, 97, 100, 10));
  for (let i = 30; i < 40; i++) b.push(bar(i * 60, 100, 100.5, 99.5, 100, 10));
  b.push(bar(40 * 60, 100, 104, 100, 103.5, 50));
  const c = consolidation(b, atr(b));
  const last = c.ranges[c.ranges.length - 1];
  assert.equal(last.result, 1);
  ok('consolidation range + volume breakout');
}
// --- prior-day value area appears on the next day
{
  const b = [];
  for (let i = 0; i < 48; i++) b.push(bar(i * 3600, 100, 101, 99, 100));
  const a = dailyAuction(b, 3600, 60);
  assert.equal(a.prior[10], null);
  assert.ok(a.prior[30] && a.prior[30].poc > 98 && a.prior[30].poc < 102);
  assert.deepEqual(a.ib[24], { hi: 101, lo: 99 });
  ok('prior-day value area + initial balance');
}
// --- scorecard sanity
{
  const sc = scorecard({ close: 105, high: 106, low: 104, ema200: 100, vwap: 103, up1: 104, dn1: 102, lastBreak: 1, lastKind: 'BOS',
    profile: { vah: 104, val: 98 }, prior: { vah: 104, val: 99 }, cvdChange: 12, flowBars: 12, priceChange: 2,
    oiChangePct: 0.5, funding: 0.0001, bookImbalance: 0.3, gex: { flip: 100 }, consState: 1 });
  assert.equal(sc.rows.length, 11);
  assert.ok(sc.net >= 7, `net ${sc.net}`);
  ok(`scorecard (net ${sc.net})`);
}
// --- gex instrument parsing
{
  const p = parseInstrument('BTC-27NOV26-73000-P');
  assert.equal(new Date(p.expiryMs).toISOString(), '2026-11-27T08:00:00.000Z');
  assert.equal(p.strike, 73000); assert.equal(p.cp, 'P');
  ok('Deribit instrument parsing');
}

// ================= live cross-checks
// 1) Binance kline taker volume == delta rebuilt from every aggTrade in that minute
{
  const now = Date.now();
  const start = Math.floor(now / 60000) * 60000 - 3 * 60000; // a fully closed minute
  const k = await (await fetch(`${REST}/fapi/v1/klines?symbol=BTCUSDT&interval=1m&startTime=${start}&limit=1`)).json();
  const kb = { volume: +k[0][5], takerBuy: +k[0][9] };
  let buy = 0, sell = 0, url = `${REST}/fapi/v1/aggTrades?symbol=BTCUSDT&startTime=${start}&endTime=${start + 59999}&limit=1000`;
  let lastId = null;
  for (;;) {
    const batch = await (await fetch(url)).json();
    for (const t of batch) { if (t.T > start + 59999) break; if (t.m) sell += +t.q; else buy += +t.q; lastId = t.a; }
    if (batch.length < 1000 || batch[batch.length - 1].T > start + 59999) break;
    url = `${REST}/fapi/v1/aggTrades?symbol=BTCUSDT&fromId=${lastId + 1}&limit=1000`;
  }
  const dK = 2 * kb.takerBuy - kb.volume, dT = buy - sell;
  console.log(`   kline delta ${dK.toFixed(3)} BTC vs trades ${dT.toFixed(3)} BTC; volume ${kb.volume} vs ${(buy + sell).toFixed(3)}`);
  assert.ok(Math.abs(dK - dT) < 0.0015 && Math.abs(kb.volume - (buy + sell)) < 0.0015);
  ok('live: kline delta == sum of every aggressive trade in the minute');
}
// 2) footprint backfill is contiguous (no missing trade ids)
{
  const ids = [];
  const r = await backfillAggTrades(REST, 'BTCUSDT', Date.now() - 90e3, (t) => ids.push(t.a), { maxRequests: 20 });
  ids.sort((a, b) => a - b);
  let gaps = 0;
  for (let i = 1; i < ids.length; i++) if (ids[i] !== ids[i - 1] + 1) gaps++;
  assert.equal(gaps, 0);
  const fp = new Footprint(60);
  ok(`live: footprint backfill ${ids.length} trades, contiguous ids, complete=${r.complete}`);
}
// 3) JS gamma == Python gex.py on the same moment's data
{
  const [idx, book] = await Promise.all([
    fetch('https://www.deribit.com/api/v2/public/get_index_price?index_name=btc_usd').then((r) => r.json()),
    fetch('https://www.deribit.com/api/v2/public/get_book_summary_by_currency?currency=BTC&kind=option').then((r) => r.json()),
  ]);
  const js = computeGex(idx.result.index_price, book.result, Date.now(), 30);
  const py = execFileSync('python3', [GEX_PY, '30'], { encoding: 'utf8' });
  const m = py.match(/gamma flip: ([\d,]+|nan)\s+call wall: ([\d,]+)\s+put wall: ([\d,]+)/);
  const num = (s) => +s.replace(/,/g, '');
  console.log(`   JS  flip ${js.flip.toFixed(0)} call ${js.callWall} put ${js.putWall} | PY flip ${m[1]} call ${m[2]} put ${m[3]}`);
  assert.equal(js.callWall, num(m[2]));
  assert.equal(js.putWall, num(m[3]));
  if (m[1] !== 'nan') assert.ok(Math.abs(js.flip - num(m[1])) / num(m[1]) < 0.005);
  ok('live: JS gamma levels match Python gex.py');
}
console.log(`\n${passed} passed`);

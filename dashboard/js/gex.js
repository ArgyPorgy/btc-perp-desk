// BTC options gamma exposure from Deribit public data (same method as quant/gex.py).
// Naive dealer sign: calls +, puts -. The strike "walls" are the robust part; the sign is an assumption.

const MONTHS = { JAN: 0, FEB: 1, MAR: 2, APR: 3, MAY: 4, JUN: 5, JUL: 6, AUG: 7, SEP: 8, OCT: 9, NOV: 10, DEC: 11 };

export function gamma(S, K, T, iv) {
  if (T <= 0 || iv <= 0) return 0;
  const d1 = (Math.log(S / K) + 0.5 * iv * iv * T) / (iv * Math.sqrt(T));
  return Math.exp(-0.5 * d1 * d1) / Math.sqrt(2 * Math.PI) / (S * iv * Math.sqrt(T));
}

export function parseInstrument(name) { // BTC-27NOV26-73000-P
  const [, exp, strike, cp] = name.split('-');
  const m = exp.match(/^(\d{1,2})([A-Z]{3})(\d{2})$/);
  const expiryMs = Date.UTC(2000 + +m[3], MONTHS[m[2]], +m[1], 8, 0, 0);
  return { expiryMs, strike: +strike, cp };
}

export function computeGex(spot, summaries, nowMs, maxDays = Infinity) {
  const opts = [];
  for (const r of summaries) {
    const { expiryMs, strike, cp } = parseInstrument(r.instrument_name);
    const T = (expiryMs - nowMs) / (365.25 * 86400e3);
    if (T > 0 && T * 365.25 <= maxDays && r.open_interest > 0 && r.mark_iv > 0)
      opts.push({ K: strike, cp, T, iv: r.mark_iv / 100, oi: r.open_interest });
  }
  const net = (S) => opts.reduce((a, o) => a + (o.cp === 'C' ? 1 : -1) * gamma(S, o.K, o.T, o.iv) * o.oi * S * S * 0.01, 0);
  const byStrike = new Map();
  for (const o of opts) {
    const g = gamma(spot, o.K, o.T, o.iv) * o.oi * spot * spot * 0.01;
    const s = byStrike.get(o.K) || { calls: 0, puts: 0 };
    if (o.cp === 'C') s.calls += g; else s.puts += g;
    byStrike.set(o.K, s);
  }
  let callWall = null, putWall = null;
  for (const [K, s] of byStrike) {
    if (!callWall || s.calls > byStrike.get(callWall).calls) callWall = K;
    if (!putWall || s.puts > byStrike.get(putWall).puts) putWall = K;
  }
  const grid = Array.from({ length: 101 }, (_, i) => spot * (0.75 + 0.005 * i));
  const prof = grid.map(net);
  const flips = [];
  for (let i = 0; i < 100; i++)
    if (prof[i] * prof[i + 1] < 0) flips.push(grid[i] + (grid[i + 1] - grid[i]) * prof[i] / (prof[i] - prof[i + 1]));
  const flip = flips.length ? flips.reduce((a, b) => (Math.abs(b - spot) < Math.abs(a - spot) ? b : a)) : NaN;
  const top = [...byStrike].sort((a, b) => (b[1].calls + b[1].puts) - (a[1].calls + a[1].puts)).slice(0, 6)
    .map(([K, s]) => ({ strike: K, calls: s.calls, puts: s.puts }));
  return { spot, total: net(spot), flip, callWall, putWall, top, count: opts.length };
}

export async function fetchGex(deribit, maxDays = Infinity, timeoutMs = 15000) {
  const get = (u) => fetch(u, { signal: AbortSignal.timeout(timeoutMs) }).then((r) => {
    if (!r.ok) throw new Error(`Deribit HTTP ${r.status}`);
    return r.json();
  });
  const [idx, book] = await Promise.all([
    get(`${deribit}/get_index_price?index_name=btc_usd`),
    get(`${deribit}/get_book_summary_by_currency?currency=BTC&kind=option`),
  ]);
  return computeGex(idx.result.index_price, book.result, Date.now(), maxDays);
}

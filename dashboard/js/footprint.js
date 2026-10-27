// Footprint: aggressive buy / sell volume per price level per candle, built from Binance aggTrades.
// aggTrade.m === true means the buyer was the maker, i.e. the aggressor SOLD (hit the bid).

const r8 = (x) => Number(x.toFixed(8)); // keep price keys exact for fractional ticks (ETH, HOOD)

export class Footprint {
  constructor(tfSec, keepCandles = 40, baseTick = 1) {
    this.tf = tfSec;
    this.keep = keepCandles;
    this.base = baseTick; // stored resolution in USD; rendering re-buckets
    this.candles = new Map(); // candleTime -> { levels: Map(price -> {buy, sell}), buy, sell }
    this.since = null;        // earliest trade time we have (sec)
  }

  add(t) { // t: { p, q, T (ms), m }
    const ct = Math.floor(t.T / 1000 / this.tf) * this.tf;
    let c = this.candles.get(ct);
    if (!c) {
      c = { levels: new Map(), buy: 0, sell: 0 };
      this.candles.set(ct, c);
      if (this.candles.size > this.keep) this.candles.delete(Math.min(...this.candles.keys()));
    }
    const px = r8(Math.floor(+t.p / this.base + 1e-9) * this.base), q = +t.q;
    let lv = c.levels.get(px);
    if (!lv) { lv = { buy: 0, sell: 0 }; c.levels.set(px, lv); }
    if (t.m) { lv.sell += q; c.sell += q; } else { lv.buy += q; c.buy += q; }
    const ts = t.T / 1000;
    if (this.since === null || ts < this.since) this.since = ts;
  }

  // Candles newest-last, re-bucketed to `tick`: [{ time, rows: [{price, buy, sell}], buy, sell, poc }]
  view(n, tick) {
    const times = [...this.candles.keys()].sort((a, b) => a - b).slice(-n);
    return times.map((time) => {
      const c = this.candles.get(time);
      const agg = new Map();
      for (const [p, lv] of c.levels) {
        const k = r8(Math.floor(p / tick + 1e-9) * tick);
        const a = agg.get(k) || { buy: 0, sell: 0 };
        a.buy += lv.buy; a.sell += lv.sell;
        agg.set(k, a);
      }
      const rows = [...agg].map(([price, a]) => ({ price, buy: a.buy, sell: a.sell })).sort((a, b) => b.price - a.price);
      let poc = null;
      for (const r of rows) if (!poc || r.buy + r.sell > poc.buy + poc.sell) poc = r;
      return { time, rows, buy: c.buy, sell: c.sell, poc: poc ? poc.price : null };
    });
  }
}

// Fetch aggTrades newest-first back to startMs, so the history always joins the live stream with no hole.
// Returns { oldestMs, complete }: if the request budget runs out first, history starts at oldestMs.
export async function backfillAggTrades(rest, symbol, startMs, onTrade, { maxRequests = 60 } = {}) {
  const get = async (q) => { const r = await fetch(`${rest}/fapi/v1/aggTrades?symbol=${symbol}&limit=1000${q}`); if (!r.ok) throw new Error(`aggTrades ${r.status}`); return r.json(); };
  let batch = await get('');
  let oldestMs = Infinity;
  for (let n = 0; n < maxRequests && batch.length; n++) {
    for (const t of batch) if (t.T >= startMs) { onTrade(t); oldestMs = Math.min(oldestMs, t.T); }
    if (batch[0].T < startMs) return { oldestMs, complete: true };
    const firstId = batch[0].a;
    if (firstId <= 0) return { oldestMs, complete: true };
    batch = await get(`&fromId=${Math.max(0, firstId - 1000)}`);
    batch = batch.filter((t) => t.a < firstId);
  }
  return { oldestMs, complete: false };
}

// Local order book for Binance USDT-M futures, kept exact with Binance's documented sync procedure:
//  1. buffer diff events, 2. fetch a REST snapshot, 3. drop events with u < lastUpdateId,
//  4. the first applied event must satisfy U <= lastUpdateId <= u, 5. every next event's pu must equal the previous u.
// Any gap -> fresh snapshot. Also samples bucketed liquidity over time for the heatmap.

export class OrderBook {
  constructor(fetchSnapshot) {
    this.fetchSnapshot = fetchSnapshot; // async () => { lastUpdateId, bids: [[p,q]], asks: [[p,q]] }
    this.bids = new Map();
    this.asks = new Map();
    this.state = 'idle';   // idle -> fetching -> bridging -> synced
    this.buffer = [];
    this.snapId = null;
    this.lastU = null;
    this.resyncs = 0;
    this.lastEventMs = 0;
  }

  get synced() { return this.state === 'synced'; }

  onEvent(e) {
    this.lastEventMs = Date.now();
    if (this.state === 'synced') {
      if (e.pu !== this.lastU) return this.resync(e);
      return this.apply(e);
    }
    if (this.state === 'bridging') return this.bridge(e);
    this.buffer.push(e);
    if (this.state === 'idle') this.fetch();
  }

  async fetch() {
    this.state = 'fetching';
    let snap;
    try {
      snap = await this.fetchSnapshot();
    } catch (err) {
      console.warn('order book snapshot failed, retrying', err);
      setTimeout(() => this.fetch(), 2000);
      return;
    }
    this.bids = new Map(snap.bids.map(([p, q]) => [+p, +q]));
    this.asks = new Map(snap.asks.map(([p, q]) => [+p, +q]));
    this.snapId = snap.lastUpdateId;
    this.state = 'bridging';
    const buf = this.buffer;
    this.buffer = [];
    for (let i = 0; i < buf.length; i++) {
      if (this.state === 'fetching') { this.buffer.push(...buf.slice(i)); break; } // a resync started: keep the rest
      this.onEvent(buf[i]);
    }
  }

  bridge(e) {
    if (e.u < this.snapId) return;                      // older than the snapshot: drop
    if (e.U <= this.snapId && e.u >= this.snapId) {     // first event that spans the snapshot
      this.apply(e);
      this.state = 'synced';
      return;
    }
    this.resync(e);                                     // U > snapId: we missed events, start over
  }

  resync(e) {
    this.resyncs++;
    this.state = 'idle';
    this.lastU = null;
    this.buffer = e ? [e] : [];
    this.fetch();
  }

  apply(e) {
    for (const [p, q] of e.b) { const pr = +p, qt = +q; if (qt === 0) this.bids.delete(pr); else this.bids.set(pr, qt); }
    for (const [p, q] of e.a) { const pr = +p, qt = +q; if (qt === 0) this.asks.delete(pr); else this.asks.set(pr, qt); }
    this.lastU = e.u;
  }

  best() {
    let bid = -Infinity, ask = Infinity;
    for (const p of this.bids.keys()) if (p > bid) bid = p;
    for (const p of this.asks.keys()) if (p < ask) ask = p;
    return { bid, ask };
  }

  // (bid size - ask size) / total within ±pct of mid
  imbalance(pct = 0.005) {
    const { bid, ask } = this.best();
    if (!isFinite(bid) || !isFinite(ask)) return null;
    const mid = (bid + ask) / 2, lo = mid * (1 - pct), hi = mid * (1 + pct);
    let b = 0, a = 0;
    for (const [p, q] of this.bids) if (p >= lo) b += q;
    for (const [p, q] of this.asks) if (p <= hi) a += q;
    return b + a > 0 ? (b - a) / (b + a) : null;
  }

  // Resting size per price bucket within ±rangePct of mid.
  sample(bucket, rangePct = 0.015) {
    const { bid, ask } = this.best();
    if (!isFinite(bid) || !isFinite(ask)) return null;
    const mid = (bid + ask) / 2, lo = mid * (1 - rangePct), hi = mid * (1 + rangePct);
    const acc = new Map();
    const add = (p, q) => { if (p < lo || p > hi) return; const k = Math.floor(p / bucket) * bucket; acc.set(k, (acc.get(k) || 0) + q); };
    for (const [p, q] of this.bids) add(p, q);
    for (const [p, q] of this.asks) add(p, q);
    const prices = new Float64Array(acc.size), sizes = new Float32Array(acc.size);
    let i = 0;
    for (const [p, q] of acc) { prices[i] = p; sizes[i] = q; i++; }
    return { mid, bucket, prices, sizes };
  }
}

// Ring buffer of heatmap columns, one sample every `everySec`.
export class Heatmap {
  constructor(everySec = 3, maxColumns = 4800) {
    this.everySec = everySec;
    this.max = maxColumns;
    this.cols = [];
  }
  push(t, sample) {
    if (!sample) return;
    this.cols.push({ t, ...sample });
    if (this.cols.length > this.max) this.cols.splice(0, this.cols.length - this.max);
  }
}

// Binance split its USDⓈ-M futures WebSockets: trades/klines/mark/liquidations on /market, order book on /public.
// Markets on the desk: Binance USDⓈ-M perps for crypto; Robinhood on Nasdaq (kind 'stock': candles via server.py from
// Yahoo Finance, so no funding / OI / order book / footprint / liquidations, and no 4h timeframe).
export const MARKETS = {
  BTCUSDT: { label: 'BTC', name: 'Bitcoin', unit: 'BTC', dp: 1, fpBase: 1, fpTicks: [5, 10, 25, 50], tapeMin: 0.5, options: 'BTC', venue: 'Binance USDⓈ-M perp' },
  ETHUSDT: { label: 'ETH', name: 'Ethereum', unit: 'ETH', dp: 2, fpBase: 0.1, fpTicks: [0.5, 1, 2, 5], tapeMin: 10, options: 'ETH', venue: 'Binance USDⓈ-M perp' },
  HYPEUSDT: { label: 'HYPE', name: 'Hyperliquid', unit: 'HYPE', dp: 3, fpBase: 0.001, fpTicks: [0.005, 0.01, 0.025, 0.05], tapeMin: 100, options: null, venue: 'Binance USDⓈ-M perp' },
  HOOD: { label: 'HOOD', name: 'Robinhood', unit: 'shares', dp: 2, fpBase: 0.01, fpTicks: [0.01], tapeMin: 0, options: null, venue: 'Nasdaq, regular session (Yahoo Finance via server.py)', kind: 'stock' },
};
// ?s=ETHUSDT in the URL picks the market; otherwise the last one used in this browser; otherwise BTC.
const pick = (() => {
  if (typeof location === 'undefined') return '';
  const q = new URLSearchParams(location.search).get('s');
  let s;
  try { s = (q || localStorage.getItem('btc-perp-desk-symbol') || '').toUpperCase(); } catch { s = (q || '').toUpperCase(); }
  return s === 'HOODUSDT' ? 'HOOD' : s; // HOOD moved from Binance's TradFi perp to Nasdaq on 2026-10-29
})();
export const SYMBOL = MARKETS[pick] ? pick : 'BTCUSDT';
export const MARKET = MARKETS[SYMBOL];
// ?rest=http://127.0.0.1:8797 points the page at quant/fapi.py's fallback (machines where Binance is geo-blocked). Local URLs only.
const restParam = typeof location === 'undefined' ? null : new URLSearchParams(location.search).get('rest');
export const REST = restParam && /^http:\/\/(127\.0\.0\.1|localhost):\d+$/.test(restParam) ? restParam : 'https://fapi.binance.com';
export const WS_MARKET = 'wss://fstream.binance.com/market/stream?streams=';
export const WS_PUBLIC = 'wss://fstream.binance.com/public/stream?streams=';
export const DERIBIT = 'https://www.deribit.com/api/v2/public';
export const STOCK = MARKET.kind === 'stock';
export const TIMEFRAMES = STOCK ? { '1m': 60, '5m': 300, '15m': 900, '1h': 3600, '1d': 86400 }
  : { '1m': 60, '5m': 300, '15m': 900, '1h': 3600, '4h': 14400, '1d': 86400 };
export const OI_PERIOD = { '1m': '5m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '4h', '1d': '1d' };
export const HEATMAP_EVERY_SEC = 3;

// Binance split its USDⓈ-M futures WebSockets: trades/klines/mark/liquidations on /market, order book on /public.
// Markets on the desk. HOODUSDT is Binance's 24/7 TradFi perpetual on Robinhood stock (same API as the crypto perps).
export const MARKETS = {
  BTCUSDT: { label: 'BTC', name: 'Bitcoin', unit: 'BTC', dp: 1, fpBase: 1, fpTicks: [5, 10, 25, 50], tapeMin: 0.5, options: 'BTC', venue: 'Binance USDⓈ-M perp' },
  ETHUSDT: { label: 'ETH', name: 'Ethereum', unit: 'ETH', dp: 2, fpBase: 0.1, fpTicks: [0.5, 1, 2, 5], tapeMin: 10, options: 'ETH', venue: 'Binance USDⓈ-M perp' },
  HOODUSDT: { label: 'HOOD', name: 'Robinhood stock', unit: 'HOOD', dp: 2, fpBase: 0.01, fpTicks: [0.01, 0.02, 0.05, 0.1], tapeMin: 300, options: null, venue: 'Binance TradFi perp, 24/7' },
};
// ?s=ETHUSDT in the URL picks the market; otherwise the last one used in this browser; otherwise BTC.
const pick = (() => {
  if (typeof location === 'undefined') return '';
  const q = new URLSearchParams(location.search).get('s');
  try { return (q || localStorage.getItem('btc-perp-desk-symbol') || '').toUpperCase(); } catch { return (q || '').toUpperCase(); }
})();
export const SYMBOL = MARKETS[pick] ? pick : 'BTCUSDT';
export const MARKET = MARKETS[SYMBOL];
export const REST = 'https://fapi.binance.com';
export const WS_MARKET = 'wss://fstream.binance.com/market/stream?streams=';
export const WS_PUBLIC = 'wss://fstream.binance.com/public/stream?streams=';
export const DERIBIT = 'https://www.deribit.com/api/v2/public';
export const TIMEFRAMES = { '1m': 60, '5m': 300, '15m': 900, '1h': 3600, '4h': 14400, '1d': 86400 };
export const OI_PERIOD = { '1m': '5m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '4h', '1d': '1d' };
export const HEATMAP_EVERY_SEC = 3;

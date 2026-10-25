// Binance split its USDⓈ-M futures WebSockets: trades/klines/mark/liquidations on /market, order book on /public.
export const SYMBOL = 'BTCUSDT';
export const REST = 'https://fapi.binance.com';
export const WS_MARKET = 'wss://fstream.binance.com/market/stream?streams=';
export const WS_PUBLIC = 'wss://fstream.binance.com/public/stream?streams=';
export const DERIBIT = 'https://www.deribit.com/api/v2/public';
export const TIMEFRAMES = { '1m': 60, '5m': 300, '15m': 900, '1h': 3600, '4h': 14400, '1d': 86400 };
export const OI_PERIOD = { '1m': '5m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '4h', '1d': '1d' };
export const HEATMAP_EVERY_SEC = 3;

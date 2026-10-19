export const SYMBOLS: Record<string, string> = {
  SPY: 'S&P 500 ETF',
  DIA: 'Dow Jones ETF',
  NDAQ: 'Nasdaq, Inc.',
  TQQQ: '3× Nasdaq-100 ETF',
};
export type Price = { date: string; close: number };
export type Dataset = {
  ticker: string;
  name: string;
  source: string;
  mode: 'historical';
  start: string;
  end: string;
  prices: Price[];
};
export type Config = {
  ticker: string;
  start: string;
  end: string;
  fast: number;
  slow: number;
  capital: number;
  cost: number;
};
export type Trade = {
  date: string;
  side: 'Buy' | 'Sell';
  price: number;
  shares: number;
  fee: number;
  equity: number;
};
export type Point = {
  date: string;
  equity: number;
  benchmark: number;
  drawdown: number;
  benchmarkDrawdown: number;
  invested: boolean;
};
export type Result = {
  config: Config;
  source: string;
  coverage: string;
  points: Point[];
  trades: Trade[];
  totalReturn: number;
  benchmarkReturn: number;
  maxDrawdown: number;
  benchmarkDrawdown: number;
  exposure: number;
  fees: number;
  benchmarkFees: number;
  volatility: number;
  created: string;
};
export const DEFAULT: Config = {
  ticker: 'SPY',
  start: '2015-01-02',
  end: '2019-07-02',
  fast: 20,
  slow: 100,
  capital: 10000,
  cost: 10,
};
export const ASSUMPTIONS =
  'Long-only moving-average crossover, otherwise cash with no interest. Signals use the previous session; trades execute at the next session adjusted close. Fractional shares; no leverage, deposits or terminal liquidation. Costs are charged on traded notional, including benchmark entry. Adjusted closes incorporate the source’s split/distribution adjustments. Taxes and additional slippage are excluded.';
export function validateDataset(value: unknown, ticker: string): Dataset {
  const d = value as Dataset;
  if (
    !d ||
    d.ticker !== ticker ||
    !SYMBOLS[ticker] ||
    d.mode !== 'historical' ||
    typeof d.source !== 'string' ||
    !Array.isArray(d.prices) ||
    d.prices.length < 2
  )
    throw new Error('The historical dataset is unavailable or invalid. Please retry.');
  let previous = '';
  for (const p of d.prices) {
    if (!p || !validDate(p.date) || p.date <= previous || !Number.isFinite(p.close) || p.close <= 0)
      throw new Error('Invalid price history. Analysis was not changed.');
    previous = p.date;
  }
  if (d.start !== d.prices[0].date || d.end !== previous)
    throw new Error('Dataset coverage does not match its prices.');
  return d;
}
function validDate(value: string): boolean {
  return (
    typeof value === 'string' &&
    /^\d{4}-\d{2}-\d{2}$/.test(value) &&
    Number.isFinite(Date.parse(value)) &&
    new Date(value).toISOString().slice(0, 10) === value
  );
}
export function validateConfig(c: Config): string | null {
  if (!SYMBOLS[c.ticker]) return 'Choose an available ticker.';
  if (!validDate(c.start) || !validDate(c.end) || c.start >= c.end)
    return 'Choose a start date before the end date.';
  if (![c.fast, c.slow].every((v) => Number.isInteger(v) && v >= 2 && v <= 250) || c.fast >= c.slow)
    return 'Moving averages must be 2–250 sessions, with the fast window below the slow window.';
  if (!Number.isFinite(c.capital) || c.capital < 100 || c.capital > 100000000)
    return 'Starting capital must be between $100 and $100,000,000.';
  if (!Number.isFinite(c.cost) || c.cost < 0 || c.cost > 500)
    return 'Transaction cost must be between 0 and 500 basis points.';
  return null;
}
export function analyze(config: Config, data: Dataset): Result {
  const error = validateConfig(config);
  if (error) throw new Error(error);
  validateDataset(data, config.ticker);
  if (config.start < data.start || config.end > data.end)
    throw new Error(`Choose dates within the available history: ${data.start} to ${data.end}.`);
  const rows = data.prices.filter((p) => p.date >= config.start && p.date <= config.end);
  if (rows.length < 2) throw new Error('Choose a period with at least two trading sessions.');
  const first = data.prices.findIndex((p) => p.date === rows[0].date);
  if (first < config.slow)
    throw new Error(
      `Allow ${config.slow} sessions of price history before the start date to warm up the strategy.`,
    );
  const prefix = [0];
  data.prices.forEach((p) => prefix.push(prefix[prefix.length - 1] + p.close));
  let cash = config.capital,
    shares = 0,
    fees = 0,
    peak = config.capital,
    benchmarkPeak = config.capital,
    exposed = 0;
  const rate = config.cost / 10000;
  const benchmarkShares = config.capital / (rows[0].close * (1 + rate));
  const benchmarkFees = benchmarkShares * rows[0].close * rate;
  const trades: Trade[] = [];
  const points: Point[] = [
    {
      date: rows[0].date,
      equity: cash,
      benchmark: benchmarkShares * rows[0].close,
      drawdown: 0,
      benchmarkDrawdown: -benchmarkFees / config.capital,
      invested: false,
    },
  ];
  // Session zero establishes the common capital baseline. Orders start next session.
  for (let j = 1; j < rows.length; j++) {
    const row = rows[j],
      i = first + j;
    const fast = (prefix[i] - prefix[i - config.fast]) / config.fast;
    const slow = (prefix[i] - prefix[i - config.slow]) / config.slow;
    const wantInvested = fast > slow;
    if (shares > 0) exposed++;
    if (wantInvested && shares === 0) {
      shares = cash / (row.close * (1 + rate));
      const fee = shares * row.close * rate;
      cash = 0;
      fees += fee;
      trades.push({
        date: row.date,
        side: 'Buy',
        price: row.close,
        shares,
        fee,
        equity: shares * row.close,
      });
    } else if (!wantInvested && shares > 0) {
      const fee = shares * row.close * rate;
      cash = shares * row.close - fee;
      fees += fee;
      trades.push({ date: row.date, side: 'Sell', price: row.close, shares, fee, equity: cash });
      shares = 0;
    }
    const equity = cash + shares * row.close,
      benchmark = benchmarkShares * row.close;
    peak = Math.max(peak, equity);
    benchmarkPeak = Math.max(benchmarkPeak, benchmark);
    points.push({
      date: row.date,
      equity,
      benchmark,
      drawdown: equity / peak - 1,
      benchmarkDrawdown: benchmark / benchmarkPeak - 1,
      invested: shares > 0,
    });
  }
  const daily = points.slice(1).map((p, i) => p.equity / points[i].equity - 1);
  const mean = daily.reduce((a, b) => a + b, 0) / daily.length;
  const variance =
    daily.length > 1 ? daily.reduce((a, b) => a + (b - mean) ** 2, 0) / (daily.length - 1) : 0;
  return {
    config: { ...config },
    source: data.source,
    coverage: `${data.start} – ${data.end}`,
    points,
    trades,
    totalReturn: points.at(-1)!.equity / config.capital - 1,
    benchmarkReturn: points.at(-1)!.benchmark / config.capital - 1,
    maxDrawdown: Math.min(0, ...points.map((p) => p.drawdown)),
    benchmarkDrawdown: Math.min(0, ...points.map((p) => p.benchmarkDrawdown)),
    exposure: exposed / (rows.length - 1),
    fees,
    benchmarkFees,
    volatility: Math.sqrt(variance * 252),
    created: new Date().toISOString(),
  };
}
export const percent = (n: number, signed = false) =>
  `${signed && n > 0 ? '+' : ''}${(n * 100).toFixed(2)}%`;
export const money = (n: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    maximumFractionDigits: 0,
  }).format(n);

import { describe, expect, it } from 'vitest';
import { analyze, DEFAULT, validateConfig, validateDataset, type Dataset } from './engine';
function fixture(prices: number[]): Dataset {
  const rows = prices.map((close, i) => ({
    date: `2018-01-${String(i + 1).padStart(2, '0')}`,
    close,
  }));
  return {
    ticker: 'SPY',
    name: 'Fixture',
    source: 'Hand-calculated fixture',
    mode: 'historical',
    start: rows[0].date,
    end: rows.at(-1)!.date,
    prices: rows,
  };
}
const data = fixture([100, 100, 100, 100, 110, 121, 133.1, 80, 70, 60]);
const config = {
  ...DEFAULT,
  start: '2018-01-04',
  end: '2018-01-10',
  fast: 2,
  slow: 3,
  capital: 1000,
  cost: 0,
};
describe('historical crossover analysis', () => {
  it('compounds the benchmark and uses the same capital and dates', () => {
    const r = analyze(config, data);
    expect(r.benchmarkReturn).toBeCloseTo(-0.4);
    expect(r.points[0].date).toBe(config.start);
    expect(r.points.at(-1)!.date).toBe(config.end);
  });
  it('lags the signal: a new jump cannot trigger a same-day buy', () => {
    const r = analyze(config, data);
    expect(r.trades[0].date).toBe('2018-01-06');
    expect(r.trades[0].price).toBe(121);
    expect(r.points[1].equity).toBe(1000);
  });
  it('executes a sell after the crossover and reconciles terminal wealth', () => {
    const r = analyze(config, data);
    expect(r.trades.map((t) => [t.date, t.side])).toEqual([
      ['2018-01-06', 'Buy'],
      ['2018-01-09', 'Sell'],
    ]);
    expect(r.points.at(-1)!.equity).toBeCloseTo((1000 / 121) * 70);
    expect(r.exposure).toBeCloseTo(3 / 6);
  });
  it('charges buy and sell fees on actual notional, including benchmark entry', () => {
    const r = analyze({ ...config, cost: 100 }, data);
    const shares = 1000 / (121 * 1.01);
    const buyFee = shares * 121 * 0.01;
    const sellFee = shares * 70 * 0.01;
    expect(r.fees).toBeCloseTo(buyFee + sellFee);
    expect(r.points.at(-1)!.equity).toBeCloseTo(shares * 70 * 0.99);
    expect(r.benchmarkFees).toBeCloseTo(1000 - 1000 / 1.01);
    expect(r.benchmarkReturn).toBeCloseTo(600 / 1.01 / 1000 - 1);
    expect(r.totalReturn).toBeLessThan(analyze(config, data).totalReturn);
  });
  it('measures drawdown from initial capital and the running peak', () => {
    const r = analyze(config, data);
    expect(r.maxDrawdown).toBeCloseTo(70 / 133.1 - 1);
    expect(r.benchmarkDrawdown).toBeCloseTo(60 / 133.1 - 1);
  });
  it('stays in cash without inventing trades on a flat series', () => {
    const r = analyze({ ...config, end: '2018-01-06' }, fixture([100, 100, 100, 100, 100, 100]));
    expect(r.totalReturn).toBe(0);
    expect(r.volatility).toBe(0);
    expect(r.exposure).toBe(0);
    expect(r.trades).toEqual([]);
  });
  it('rejects insufficient warmup and dates outside dataset coverage', () => {
    expect(() => analyze({ ...config, start: '2018-01-02' }, data)).toThrow('warm up');
    expect(() => analyze({ ...config, end: '2020-01-01' }, data)).toThrow('available history');
  });
  it('validates settings and real calendar dates', () => {
    expect(validateConfig({ ...config, fast: 10, slow: 3 })).toContain('fast window');
    expect(validateConfig({ ...config, capital: NaN })).toContain('capital');
    expect(validateConfig({ ...config, start: '2018-02-31' })).toContain('start date');
  });
  it('rejects duplicate, malformed, nonpositive and unordered prices', () => {
    for (const prices of [
      [...data.prices, data.prices[0]],
      [{ date: '2018-02-31', close: 1 }, data.prices[1]],
      [{ date: '2018-01-01', close: 0 }, data.prices[1]],
    ])
      expect(() => validateDataset({ ...data, prices }, 'SPY')).toThrow();
  });
});

import { validateConfig, type Config, type Result } from './engine';
export type SavedRun = { id: string; name: string; result: Result };
export const STORAGE_KEY = 'strategy-lab:v1';
export type Stored = { draft: Config; saved: SavedRun[] };
function validResult(r: Result): boolean {
  if (
    !r ||
    validateConfig(r.config) ||
    typeof r.source !== 'string' ||
    typeof r.coverage !== 'string' ||
    typeof r.created !== 'string' ||
    !Array.isArray(r.points) ||
    r.points.length < 2 ||
    !Array.isArray(r.trades)
  )
    return false;
  if (
    ![
      r.totalReturn,
      r.benchmarkReturn,
      r.maxDrawdown,
      r.benchmarkDrawdown,
      r.exposure,
      r.fees,
      r.benchmarkFees,
      r.volatility,
    ].every(Number.isFinite)
  )
    return false;
  let previous = '';
  for (const p of r.points) {
    if (
      !p ||
      typeof p.date !== 'string' ||
      !/^\d{4}-\d{2}-\d{2}$/.test(p.date) ||
      p.date <= previous ||
      ![p.equity, p.benchmark, p.drawdown, p.benchmarkDrawdown].every(Number.isFinite) ||
      p.equity < 0 ||
      p.benchmark < 0 ||
      typeof p.invested !== 'boolean'
    )
      return false;
    previous = p.date;
  }
  return r.trades.every(
    (t) =>
      t &&
      typeof t.date === 'string' &&
      ['Buy', 'Sell'].includes(t.side) &&
      [t.price, t.shares, t.fee, t.equity].every(Number.isFinite),
  );
}
export function readStorage(): { state: Stored | null; warning: string } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return { state: null, warning: '' };
    const state = JSON.parse(raw) as Stored;
    if (
      !state ||
      validateConfig(state.draft) ||
      !Array.isArray(state.saved) ||
      state.saved.length > 12
    )
      throw new Error();
    const ids = new Set<string>();
    for (const run of state.saved) {
      if (
        !run ||
        typeof run.id !== 'string' ||
        ids.has(run.id) ||
        typeof run.name !== 'string' ||
        !run.name.trim() ||
        run.name.length > 80 ||
        !validResult(run.result)
      )
        throw new Error();
      ids.add(run.id);
    }
    return { state, warning: '' };
  } catch {
    return {
      state: null,
      warning:
        'Browser storage is unavailable or saved data could not be read. You can still analyze and export runs.',
    };
  }
}
export function writeStorage(state: Stored): boolean {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    return true;
  } catch {
    return false;
  }
}

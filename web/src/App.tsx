import { useEffect, useRef, useState } from 'react';
import {
  ArrowDownToLine,
  ArrowRight,
  ArrowUpRight,
  BarChart3,
  BookOpen,
  Check,
  ChevronDown,
  Clock3,
  FlaskConical,
  FolderOpen,
  GitCompareArrows,
  LoaderCircle,
  Play,
  Plus,
  RotateCcw,
  Search,
  ShieldCheck,
  Trash2,
  X,
} from 'lucide-react';
import {
  analyze,
  ASSUMPTIONS,
  DEFAULT,
  money,
  percent,
  SYMBOLS,
  validateConfig,
  validateDataset,
  type Config,
  type Result,
} from './engine';
import { readStorage, writeStorage, type SavedRun } from './storage';
import { Chart } from './Chart';

type View = 'Performance' | 'Risk' | 'Trades';
const initial = readStorage();
const same = (a: Config, b: Config) => JSON.stringify(a) === JSON.stringify(b);
const dollars = (n: number) =>
  new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n);
function Metric({
  title,
  value,
  detail,
  positive,
}: {
  title: string;
  value: string;
  detail: string;
  positive?: boolean;
}) {
  return (
    <div className="metric">
      <div className="metric-label">{title}</div>
      <strong className={positive === undefined ? '' : positive ? 'positive' : 'negative'}>
        {value}
      </strong>
      <span>{detail}</span>
    </div>
  );
}
export default function App() {
  const [draft, setDraft] = useState<Config>(initial.state?.draft ?? DEFAULT);
  const [saved, setSaved] = useState<SavedRun[]>(initial.state?.saved ?? []);
  const [result, setResult] = useState<Result | null>(null);
  const [view, setView] = useState<View>('Performance');
  const [page, setPage] = useState<'workspace' | 'saved'>('workspace');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [warning, setWarning] = useState(initial.warning);
  const [notice, setNotice] = useState('');
  const [query, setQuery] = useState('');
  const [selectedTrade, setSelectedTrade] = useState('');
  const [saveOpen, setSaveOpen] = useState(false);
  const [name, setName] = useState('');
  const [help, setHelp] = useState(false);
  const [controlsOpen, setControlsOpen] = useState(false);
  const [compare, setCompare] = useState<string[]>([]);
  const controller = useRef<AbortController | null>(null);
  const lastValidDraft = useRef<Config>(initial.state?.draft ?? DEFAULT);
  const booted = useRef(false);
  const dialogRef = useRef<HTMLDialogElement>(null);
  const helpRef = useRef<HTMLDialogElement>(null);
  const invalid = validateConfig(draft);
  const dirty = !!result && !same(draft, result.config);

  useEffect(() => {
    if (!validateConfig(draft)) lastValidDraft.current = draft;
    if (!writeStorage({ draft: lastValidDraft.current, saved }))
      setWarning(
        'Browser storage is unavailable or full. Changes are kept for this session; export runs to keep a copy.',
      );
  }, [draft, saved]);
  useEffect(() => {
    if (saveOpen) dialogRef.current?.showModal();
    else dialogRef.current?.close();
  }, [saveOpen]);
  useEffect(() => {
    if (help) helpRef.current?.showModal();
    else helpRef.current?.close();
  }, [help]);
  useEffect(() => {
    if (!booted.current) {
      booted.current = true;
      void run(initial.state?.draft ?? DEFAULT);
    }
    return () => {
      /* A subsequent run cancels prior fetches. */
    };
  }, []);
  async function run(config = draft) {
    const validation = validateConfig(config);
    if (validation) {
      setError(validation);
      return;
    }
    controller.current?.abort();
    const request = new AbortController();
    controller.current = request;
    const timeout = setTimeout(() => request.abort('timeout'), 15000);
    setLoading(true);
    setError('');
    setNotice('');
    try {
      const response = await fetch(`${import.meta.env.BASE_URL}data/${config.ticker}.json`, {
        signal: request.signal,
      });
      if (!response.ok)
        throw new Error(
          `Could not load ${config.ticker} history. Check your connection and retry.`,
        );
      let payload: unknown;
      try {
        payload = await response.json();
      } catch {
        if (request.signal.aborted) throw new Error('Request cancelled');
        throw new Error('The price history could not be read. Please retry.');
      }
      const data = validateDataset(payload, config.ticker);
      const next = analyze(config, data);
      if (request.signal.aborted) return;
      setResult(next);
      setSelectedTrade('');
      setQuery('');
    } catch (e) {
      if (request.signal.reason === 'timeout')
        setError('Price history took too long to load. Please retry.');
      else if (!request.signal.aborted)
        setError(
          e instanceof TypeError
            ? 'Could not load price history. Check your connection and retry.'
            : e instanceof Error
              ? e.message
              : 'Analysis failed. Please retry.',
        );
    } finally {
      clearTimeout(timeout);
      if (controller.current === request) setLoading(false);
    }
  }
  function update<K extends keyof Config>(key: K, value: Config[K]) {
    setDraft((c) => ({ ...c, [key]: value }));
    setError('');
  }
  function exportRun() {
    if (!result) return;
    const blob = new Blob(
      [
        JSON.stringify(
          {
            schemaVersion: 1,
            ...result,
            assumptions: ASSUMPTIONS,
            exportedAt: new Date().toISOString(),
          },
          null,
          2,
        ),
      ],
      { type: 'application/json' },
    );
    const url = URL.createObjectURL(blob),
      link = document.createElement('a');
    link.href = url;
    link.download = `${result.config.ticker}-analysis-${result.points[0].date}-${result.points.at(-1)!.date}.json`;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    setNotice('Exported results, trades, and assumptions.');
  }
  function save() {
    if (!result || !name.trim()) return;
    if (saved.length >= 12) {
      setNotice('You can keep up to 12 saved runs. Remove one to save another.');
      setSaveOpen(false);
      return;
    }
    setSaved((s) => [...s, { id: crypto.randomUUID(), name: name.trim().slice(0, 80), result }]);
    setSaveOpen(false);
    setNotice('Run saved on this browser.');
  }
  function restore(run: SavedRun) {
    controller.current?.abort();
    setLoading(false);
    setDraft(run.result.config);
    setResult(run.result);
    setPage('workspace');
    setError('');
    setNotice(`Restored “${run.name}”.`);
    setQuery('');
    setSelectedTrade('');
  }
  const filtered =
    result?.trades.filter((t) =>
      `${t.date} ${t.side} ${t.price.toFixed(2)}`.toLowerCase().includes(query.toLowerCase()),
    ) ?? [];
  const visibleComparisons = saved.filter((s) => compare.includes(s.id));
  const active = result?.config;
  const excess = result ? result.totalReturn - result.benchmarkReturn : 0;
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main-content">
        Skip to results
      </a>
      <header className="desktop-header">
        <div className="application-titlebar">
          <a
            className="brand"
            href="#"
            aria-label="Strategy Lab home"
            onClick={(e) => {
              e.preventDefault();
              setPage('workspace');
            }}
          >
            <span className="brand-icon" aria-hidden="true">
              <BarChart3 size={18} />
            </span>
            <span>
              python<span className="brand-light">stocks</span>
            </span>
          </a>
          <span className="titlebar-rule" aria-hidden="true" />
          <span className="application-label">A STOCK-MARKET WORKBENCH</span>
        </div>
        <nav className="menubar" aria-label="Main navigation">
          <button
            className={`nav-item ${page === 'workspace' ? 'active' : ''}`}
            onClick={() => setPage('workspace')}
            aria-current={page === 'workspace' ? 'page' : undefined}
          >
            <FlaskConical size={15} />
            Strategy Lab
          </button>
          <button
            className={`nav-item ${page === 'saved' ? 'active' : ''}`}
            onClick={() => setPage('saved')}
            aria-current={page === 'saved' ? 'page' : undefined}
          >
            <FolderOpen size={15} />
            Saved analyses <span className="count">{saved.length}</span>
          </button>
          <button className="nav-item" onClick={() => setHelp(true)} aria-label="Open help">
            <BookOpen size={15} />
            How it works
          </button>
          <span className="local-label">
            <span />
            Runs stay in this browser
          </span>
        </nav>
      </header>
      <div className="app-body">
        <main id="main-content" tabIndex={-1}>
          <div className="page-heading">
            <div>
              <div className="eyebrow">
                <span className="document-number">{page === 'workspace' ? '01' : '02'}</span>
                {page === 'workspace' ? 'THE WORKBENCH' : 'THE RUN ARCHIVE'}
                <span className="edition-label">HISTORICAL STUDIES</span>
              </div>
              <h1>
                {page === 'workspace' ? 'What if I’d invested differently?' : 'Your saved runs.'}
              </h1>
              <p>
                {page === 'workspace'
                  ? 'Pick a ticker, try a simple rule, and see how it played out. The trade log is there if you want to dig in.'
                  : 'Come back to a run, or put a few next to each other and compare the numbers.'}
              </p>
            </div>
            <div className="snapshot-stamp">
              <span>DATA CUT-OFF</span>
              <strong>02 JUL 2019</strong>
              <span>HISTORICAL, NOT LIVE</span>
            </div>
          </div>
          {warning && (
            <div className="banner warning" role="status">
              {warning}
            </div>
          )}
          {notice && (
            <div className="banner success" role="status">
              <Check size={16} />
              {notice}
              <button aria-label="Dismiss notification" onClick={() => setNotice('')}>
                <X size={15} />
              </button>
            </div>
          )}
          {page === 'workspace' ? (
            <div className="workspace-grid">
              <aside className="configuration card" aria-label="Analysis configuration">
                <div className="panel-heading">
                  <span className="window-index" aria-hidden="true">
                    A
                  </span>
                  <div>
                    <h2>Set up a run</h2>
                    <p>Change one thing. Run it again.</p>
                  </div>
                  <button
                    className="mobile-settings"
                    aria-expanded={controlsOpen}
                    aria-controls="configuration-form"
                    onClick={() => setControlsOpen((open) => !open)}
                  >
                    {controlsOpen ? 'Hide settings' : 'Edit settings'}
                    <ChevronDown size={13} />
                  </button>
                </div>
                <form
                  id="configuration-form"
                  className={controlsOpen ? 'mobile-open' : ''}
                  onSubmit={(e) => {
                    e.preventDefault();
                    void run();
                  }}
                >
                  <div className="form-section">
                    <div className="section-label">
                      <span>01</span>PRICE HISTORY
                    </div>
                    <label htmlFor="ticker">Ticker</label>
                    <div className="select-wrap">
                      <select
                        id="ticker"
                        value={draft.ticker}
                        onChange={(e) => update('ticker', e.target.value)}
                      >
                        {Object.entries(SYMBOLS).map(([symbol, label]) => (
                          <option key={symbol} value={symbol}>
                            {symbol} · {label}
                          </option>
                        ))}
                      </select>
                      <ChevronDown size={15} />
                    </div>
                    <p className="field-hint">
                      {draft.ticker === 'TQQQ'
                        ? 'Leveraged ETF · higher risk and daily leverage reset.'
                        : 'Adjusted prices · splits & distributions included'}
                    </p>
                    <label>Historical period</label>
                    <div className="date-fields">
                      <div>
                        <label className="sr-only" htmlFor="start">
                          Start date
                        </label>
                        <input
                          id="start"
                          type="date"
                          value={draft.start}
                          max="2019-07-02"
                          onChange={(e) => update('start', e.target.value)}
                        />
                        <small>Start date</small>
                      </div>
                      <span>–</span>
                      <div>
                        <label className="sr-only" htmlFor="end">
                          End date
                        </label>
                        <input
                          id="end"
                          type="date"
                          value={draft.end}
                          max="2019-07-02"
                          onChange={(e) => update('end', e.target.value)}
                        />
                        <small>End date</small>
                      </div>
                    </div>
                    <div className="period-shortcuts">
                      {[1, 3, 5].map((years) => (
                        <button
                          key={years}
                          type="button"
                          onClick={() =>
                            setDraft((c) => ({
                              ...c,
                              start: `${2019 - years}-07-02`,
                              end: '2019-07-02',
                            }))
                          }
                        >
                          {years}Y
                        </button>
                      ))}
                      <span>ending Jul 2019</span>
                    </div>
                  </div>
                  <div className="form-section">
                    <div className="section-label">
                      <span>02</span>MOVING AVERAGES
                    </div>
                    <div className="strategy-choice">
                      <span className="strategy-icon">
                        <GitCompareArrows size={18} />
                      </span>
                      <div>
                        <strong>Moving average crossover</strong>
                        <small>Buy on a crossover. Hold cash in between.</small>
                      </div>
                      <Check size={15} />
                    </div>
                    <div className="paired-fields">
                      <div>
                        <label htmlFor="fast">Fast window</label>
                        <div className="input-suffix">
                          <input
                            id="fast"
                            type="number"
                            min="2"
                            max="249"
                            value={Number.isNaN(draft.fast) ? '' : draft.fast}
                            onChange={(e) => update('fast', e.target.valueAsNumber)}
                          />
                          <span>days</span>
                        </div>
                      </div>
                      <div>
                        <label htmlFor="slow">Slow window</label>
                        <div className="input-suffix">
                          <input
                            id="slow"
                            type="number"
                            min="3"
                            max="250"
                            value={Number.isNaN(draft.slow) ? '' : draft.slow}
                            onChange={(e) => update('slow', e.target.valueAsNumber)}
                          />
                          <span>days</span>
                        </div>
                      </div>
                    </div>
                    <p className="field-hint">
                      Invest when the fast average is above the slow average; otherwise hold cash.
                    </p>
                  </div>
                  <div className="form-section">
                    <div className="section-label">
                      <span>03</span>CASH & COSTS
                    </div>
                    <label htmlFor="capital">Starting capital</label>
                    <div className="input-prefix">
                      <span>$</span>
                      <input
                        id="capital"
                        type="number"
                        min="100"
                        max="100000000"
                        value={Number.isNaN(draft.capital) ? '' : draft.capital}
                        onChange={(e) => update('capital', e.target.valueAsNumber)}
                      />
                      <small>USD</small>
                    </div>
                    <label htmlFor="cost">
                      Transaction cost{' '}
                      <span className="label-value">
                        {Number.isFinite(draft.cost) ? draft.cost : '—'} bps
                      </span>
                    </label>
                    <input
                      id="cost"
                      className="range"
                      type="range"
                      min="0"
                      max="100"
                      step="1"
                      value={draft.cost}
                      onChange={(e) => update('cost', Number(e.target.value))}
                    />
                    <div className="range-labels">
                      <span>0 bps</span>
                      <span>100 bps</span>
                    </div>
                    <p className="field-hint">
                      Charged on every buy and sell.
                      <br />
                      10 bps = 0.10% of the trade value.
                    </p>
                  </div>
                  {invalid && (
                    <p className="field-error" role="alert">
                      {invalid}
                    </p>
                  )}
                  <div className="run-actions">
                    <button
                      className="button primary run-button"
                      type="submit"
                      disabled={loading || !!invalid}
                    >
                      {loading ? (
                        <LoaderCircle size={17} className="spinning" />
                      ) : (
                        <Play size={15} fill="currentColor" />
                      )}
                      {loading ? 'Running analysis…' : 'Run analysis'}
                      <ArrowRight size={16} />
                    </button>
                    <button
                      type="button"
                      className="reset-button"
                      disabled={loading}
                      onClick={() => {
                        setDraft({ ...DEFAULT });
                        setError('');
                      }}
                    >
                      <RotateCcw size={12} />
                      Reset to example
                    </button>
                  </div>
                </form>
              </aside>
              <section className="results" aria-label="Analysis results" aria-busy={loading}>
                {error && (
                  <div className="banner error" role="alert">
                    <div>
                      <strong>We couldn’t run that analysis.</strong>
                      <p>
                        {error}
                        {result && ' Your previous result is still shown below.'}
                      </p>
                    </div>
                    <button
                      className="button small"
                      onClick={() => void run()}
                      disabled={loading || !!invalid}
                    >
                      Retry
                    </button>
                  </div>
                )}
                <div className="results-titlebar">
                  <span className="window-index" aria-hidden="true">
                    B
                  </span>
                  <span>RESULTS / {active?.ticker ?? draft.ticker}</span>
                  <span className="window-rule" aria-hidden="true" />
                  <span className="window-caption">MOVING AVERAGE STUDY</span>
                </div>
                <div className="results-toolbar">
                  <div className="result-context">
                    <span className="ticker-icon">{active?.ticker ?? draft.ticker}</span>
                    <div>
                      <h2>
                        {active?.ticker ?? draft.ticker}
                        <span>{SYMBOLS[active?.ticker ?? draft.ticker]}</span>
                      </h2>
                      <p>
                        {result
                          ? `${result.points[0].date} — ${result.points.at(-1)!.date} · ${result.points.length.toLocaleString()} sessions`
                          : 'Preparing your first analysis…'}
                      </p>
                    </div>
                  </div>
                  <div className="result-actions">
                    <button
                      className="button small"
                      disabled={!result || loading}
                      onClick={exportRun}
                    >
                      <ArrowDownToLine size={15} />
                      Export
                    </button>
                    <button
                      className="button small"
                      disabled={!result || loading}
                      onClick={() => {
                        setName(
                          `${result!.config.ticker} · ${result!.config.fast}/${result!.config.slow} crossover`,
                        );
                        setSaveOpen(true);
                      }}
                    >
                      <Plus size={15} />
                      Save run
                    </button>
                  </div>
                </div>
                <div className={`run-status ${dirty ? 'pending' : ''}`} role="status">
                  {loading ? (
                    <>
                      <LoaderCircle size={13} className="spinning" />
                      Running your analysis…
                    </>
                  ) : dirty ? (
                    <>
                      <Clock3 size={13} />
                      Inputs changed. Run analysis to update these results.
                    </>
                  ) : result ? (
                    <>
                      <Check size={13} />
                      Analysis complete
                      <span>
                        MA {active!.fast}/{active!.slow} · {active!.cost} bps ·{' '}
                        {money(active!.capital)} initial
                      </span>
                    </>
                  ) : (
                    'Loading historical prices…'
                  )}
                </div>
                {!result ? (
                  <div className="card empty-state">
                    <div className="empty-icon">
                      {loading ? <LoaderCircle className="spinning" /> : <BarChart3 />}
                    </div>
                    <h2>{loading ? 'Working through the prices…' : 'Ready when you are.'}</h2>
                    <p>
                      {loading
                        ? 'Loading historical prices and calculating each trade.'
                        : 'Choose a ticker and a date range, then run the numbers.'}
                    </p>
                  </div>
                ) : (
                  <>
                    <div className="metrics card" aria-label="Key performance metrics">
                      <Metric
                        title="Total return"
                        value={percent(result.totalReturn, true)}
                        positive={result.totalReturn >= 0}
                        detail={`${percent(result.benchmarkReturn, true)} buy & hold`}
                      />
                      <Metric
                        title="Maximum drawdown"
                        value={percent(result.maxDrawdown)}
                        detail={`${percent(result.benchmarkDrawdown)} buy & hold`}
                      />
                      <Metric
                        title="Market exposure"
                        value={`${(result.exposure * 100).toFixed(1)}%`}
                        detail="Time invested across sessions"
                      />
                      <Metric
                        title="Transaction costs"
                        value={dollars(result.fees)}
                        detail={`${result.trades.length} trades · ${active!.cost} bps per trade`}
                      />
                    </div>
                    <div className="card analysis-card">
                      <div className="analysis-titlebar">
                        <BarChart3 size={14} aria-hidden="true" />
                        <span>THE RECORD</span>
                        <span className="window-rule" aria-hidden="true" />
                        <span>03 VIEWS</span>
                      </div>
                      <div className="result-tabs" role="tablist" aria-label="Analysis views">
                        {(['Performance', 'Risk', 'Trades'] as View[]).map((tab, index) => (
                          <button
                            key={tab}
                            id={`tab-${tab}`}
                            role="tab"
                            aria-selected={view === tab}
                            aria-controls="analysis-panel"
                            tabIndex={view === tab ? 0 : -1}
                            className={view === tab ? 'selected' : ''}
                            onClick={() => {
                              setView(tab);
                              setQuery('');
                              setSelectedTrade('');
                            }}
                            onKeyDown={(e) => {
                              if (['ArrowRight', 'ArrowLeft', 'Home', 'End'].includes(e.key)) {
                                e.preventDefault();
                                const tabs: View[] = ['Performance', 'Risk', 'Trades'];
                                const next =
                                  e.key === 'Home'
                                    ? 0
                                    : e.key === 'End'
                                      ? 2
                                      : (index + (e.key === 'ArrowRight' ? 1 : 2)) % 3;
                                setView(tabs[next]);
                                document.getElementById(`tab-${tabs[next]}`)?.focus();
                              }
                            }}
                          >
                            {tab}
                            {tab === 'Trades' && <span>{result.trades.length}</span>}
                          </button>
                        ))}
                      </div>
                      <div
                        id="analysis-panel"
                        role="tabpanel"
                        aria-labelledby={`tab-${view}`}
                        tabIndex={0}
                      >
                        {view !== 'Trades' ? (
                          <>
                            <div className="chart-heading">
                              <div>
                                <h3>
                                  {view === 'Performance'
                                    ? 'How your capital would have grown'
                                    : 'Drawdowns over time'}
                                </h3>
                                <p>
                                  {view === 'Performance'
                                    ? `${money(active!.capital)} invested · returns after transaction costs`
                                    : 'Peak-to-trough declines · smaller losses are closer to zero'}
                                </p>
                              </div>
                              <div className="chart-legend">
                                <span>
                                  <i />
                                  Your strategy
                                </span>
                                <span>
                                  <i />
                                  Buy & hold
                                </span>
                              </div>
                            </div>
                            <Chart
                              key={`${result.created}-${view}`}
                              result={result}
                              risk={view === 'Risk'}
                              onTrade={(date) => {
                                setView('Trades');
                                setQuery(date);
                                setSelectedTrade(date);
                                setTimeout(
                                  () => document.getElementById('trade-search')?.focus(),
                                  0,
                                );
                              }}
                            />
                            {view === 'Risk' && (
                              <div className="risk-summary">
                                <span>
                                  Annualized strategy volatility
                                  <strong>{percent(result.volatility)}</strong>
                                </span>
                                <span>
                                  Largest decline<strong>{percent(result.maxDrawdown)}</strong>
                                </span>
                                <span>
                                  Sessions out of market
                                  <strong>{((1 - result.exposure) * 100).toFixed(1)}%</strong>
                                </span>
                              </div>
                            )}
                          </>
                        ) : (
                          <div className="trades-view">
                            <div className="chart-heading">
                              <div>
                                <h3>The trade log</h3>
                                <p>
                                  {result.trades.length} executions · adjusted-close prices ·
                                  fractional shares
                                </p>
                              </div>
                              <label className="search-field">
                                <Search size={15} />
                                <input
                                  id="trade-search"
                                  aria-label="Search trades"
                                  placeholder="Search date, buy or sell…"
                                  value={query}
                                  onChange={(e) => setQuery(e.target.value)}
                                />
                                {query && (
                                  <button
                                    aria-label="Clear search"
                                    onClick={() => {
                                      setQuery('');
                                      setSelectedTrade('');
                                    }}
                                  >
                                    <X size={13} />
                                  </button>
                                )}
                              </label>
                            </div>
                            <div className="table-scroll">
                              <table>
                                <thead>
                                  <tr>
                                    <th scope="col">Date</th>
                                    <th scope="col">Action</th>
                                    <th scope="col">Price</th>
                                    <th scope="col">Shares</th>
                                    <th scope="col">Cost</th>
                                    <th scope="col">Portfolio</th>
                                  </tr>
                                </thead>
                                <tbody>
                                  {filtered.map((t) => (
                                    <tr
                                      key={t.date}
                                      className={selectedTrade === t.date ? 'highlight-row' : ''}
                                    >
                                      <td>{t.date}</td>
                                      <td>
                                        <span className={`trade-pill ${t.side.toLowerCase()}`}>
                                          {t.side}
                                        </span>
                                      </td>
                                      <td>{dollars(t.price)}</td>
                                      <td>{t.shares.toFixed(3)}</td>
                                      <td>{dollars(t.fee)}</td>
                                      <td>{dollars(t.equity)}</td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                              {!filtered.length && (
                                <div className="no-trades">
                                  {query
                                    ? 'No trades match your search. Try another date or clear the search.'
                                    : 'No trades were triggered in this period. The strategy stayed in cash.'}
                                </div>
                              )}
                            </div>
                          </div>
                        )}
                      </div>
                      <div className="chart-footer">
                        <ShieldCheck size={13} />
                        Same period. Same starting capital. Costs included for both.
                      </div>
                    </div>
                    <div className="insight-card">
                      <span className="insight-icon" aria-hidden="true">
                        N.B.
                      </span>
                      <div>
                        <div className="section-label">WHAT HAPPENED</div>
                        <h3>
                          {excess > 0
                            ? 'The strategy finished ahead of buy & hold.'
                            : excess < 0
                              ? 'Staying invested would have returned more.'
                              : 'The strategy matched buy & hold.'}
                        </h3>
                        <p>
                          Your strategy returned <strong>{percent(result.totalReturn)}</strong>,{' '}
                          {Math.abs(excess * 100).toFixed(2)} percentage points{' '}
                          {excess >= 0 ? 'ahead of' : 'behind'} buy & hold. It was invested for{' '}
                          <strong>{(result.exposure * 100).toFixed(1)}%</strong> of sessions, with a
                          worst decline of <strong>{percent(result.maxDrawdown)}</strong>.{' '}
                          {Math.abs(result.maxDrawdown) < Math.abs(result.benchmarkDrawdown)
                            ? 'It reduced the deepest drawdown in this period.'
                            : 'It did not reduce the deepest drawdown in this period.'}
                        </p>
                        <button className="text-button" onClick={() => setHelp(true)}>
                          How this was calculated
                          <ArrowRight size={13} />
                        </button>
                      </div>
                    </div>
                    <div className="provenance">
                      <span>
                        <span className="data-dot" />
                        {result.source}
                      </span>
                      <span>Available history: {result.coverage}</span>
                      <span>
                        <Clock3 size={12} />
                        Snapshot ends July 2019 · not live data
                      </span>
                    </div>
                  </>
                )}
              </section>
            </div>
          ) : (
            <section className="saved-page">
              {saved.length === 0 ? (
                <div className="card empty-state">
                  <span className="empty-icon">
                    <FolderOpen size={28} />
                  </span>
                  <h2>Nothing saved yet.</h2>
                  <p>When a run looks interesting, save it. It’ll be waiting here next time.</p>
                  <button className="button primary" onClick={() => setPage('workspace')}>
                    Back to the workbench
                    <ArrowRight size={16} />
                  </button>
                </div>
              ) : (
                <>
                  <div className="saved-toolbar">
                    <h2>
                      Your analyses <span className="count">{saved.length}/12</span>
                    </h2>
                    <span>
                      <GitCompareArrows size={16} />
                      Select up to 3 to compare
                    </span>
                  </div>
                  <div className="saved-grid">
                    {saved.map((run, runIndex) => (
                      <article
                        key={run.id}
                        className={`card saved-card ${compare.includes(run.id) ? 'is-compared' : ''}`}
                      >
                        <div className="saved-card-top">
                          <span className="symbol-badge">{run.result.config.ticker}</span>
                          <span className="archive-index">
                            RUN / {String(runIndex + 1).padStart(2, '0')}
                          </span>
                          <button
                            className="icon-button"
                            aria-label={`Delete ${run.name}`}
                            onClick={() => {
                              setSaved((s) => s.filter((r) => r.id !== run.id));
                              setCompare((c) => c.filter((id) => id !== run.id));
                            }}
                          >
                            <Trash2 size={15} />
                          </button>
                        </div>
                        <h3>{run.name}</h3>
                        <p>
                          {run.result.config.start} → {run.result.config.end}
                        </p>
                        <strong className={run.result.totalReturn >= 0 ? 'positive' : 'negative'}>
                          {percent(run.result.totalReturn, true)}
                        </strong>
                        <p>
                          MA {run.result.config.fast}/{run.result.config.slow} ·{' '}
                          {run.result.config.cost} bps · {money(run.result.config.capital)}
                        </p>
                        <div className="saved-card-actions">
                          <label>
                            <input
                              type="checkbox"
                              checked={compare.includes(run.id)}
                              disabled={!compare.includes(run.id) && compare.length >= 3}
                              onChange={(e) =>
                                setCompare((c) =>
                                  e.target.checked
                                    ? [...c, run.id]
                                    : c.filter((id) => id !== run.id),
                                )
                              }
                            />
                            Compare
                          </label>
                          <button className="text-button" onClick={() => restore(run)}>
                            Open analysis
                            <ArrowUpRight size={14} />
                          </button>
                        </div>
                      </article>
                    ))}
                  </div>
                  {visibleComparisons.length > 0 && (
                    <div className="card comparison">
                      <h2>Compare saved runs</h2>
                      <p>
                        Different periods and tickers can produce different outcomes. Check
                        assumptions before comparing.
                      </p>
                      <div className="table-scroll">
                        <table>
                          <thead>
                            <tr>
                              <th scope="col">Measure</th>
                              {visibleComparisons.map((s) => (
                                <th scope="col" key={s.id}>
                                  {s.name}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {[
                              'Ticker',
                              'Period',
                              'MA windows',
                              'Initial capital',
                              'Cost per trade',
                              'Total return',
                              'Buy & hold return',
                              'Max drawdown',
                              'Market exposure',
                              'Transaction costs',
                            ].map((label, i) => (
                              <tr key={label}>
                                <th scope="row">{label}</th>
                                {visibleComparisons.map((s) => {
                                  const r = s.result,
                                    c = r.config;
                                  return (
                                    <td key={s.id}>
                                      {
                                        [
                                          c.ticker,
                                          `${c.start} – ${c.end}`,
                                          `${c.fast} / ${c.slow}`,
                                          money(c.capital),
                                          `${c.cost} bps`,
                                          percent(r.totalReturn),
                                          percent(r.benchmarkReturn),
                                          percent(r.maxDrawdown),
                                          percent(r.exposure),
                                          dollars(r.fees),
                                        ][i]
                                      }
                                    </td>
                                  );
                                })}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    </div>
                  )}
                </>
              )}
            </section>
          )}
          <footer className="page-footer">
            <span>
              <span className="status-square" aria-hidden="true" />
              LOCAL MODE
              <span className="footer-divider" aria-hidden="true">
                /
              </span>
              Happy tinkering.
            </span>
            <span>
              Historical results are not a forecast.{' '}
              <button onClick={() => setHelp(true)}>
                Read the methodology
                <ArrowUpRight size={12} />
              </button>
            </span>
          </footer>
        </main>
      </div>
      <dialog
        ref={dialogRef}
        onCancel={() => setSaveOpen(false)}
        onClose={() => setSaveOpen(false)}
        aria-labelledby="save-title"
      >
        <form
          onSubmit={(e) => {
            e.preventDefault();
            save();
          }}
        >
          <div className="dialog-heading">
            <span className="icon-tile">
              <FolderOpen size={20} />
            </span>
            <button
              type="button"
              className="icon-button"
              aria-label="Close save dialog"
              onClick={() => setSaveOpen(false)}
            >
              <X size={19} />
            </button>
          </div>
          <div className="dialog-kicker">SAVE TO LOCAL ARCHIVE</div>
          <h2 id="save-title">Save this run</h2>
          <p>
            Save the displayed result and its assumptions on this browser.
            {dirty && ' Your unrun input changes will not be included.'}
          </p>
          <label htmlFor="run-name">Analysis name</label>
          <input
            autoFocus
            id="run-name"
            maxLength={80}
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
          <div className="dialog-actions">
            <button type="button" className="button" onClick={() => setSaveOpen(false)}>
              Cancel
            </button>
            <button className="button primary" disabled={!name.trim()} type="submit">
              Save analysis
              <Check size={15} />
            </button>
          </div>
        </form>
      </dialog>
      <dialog
        ref={helpRef}
        onCancel={() => setHelp(false)}
        onClose={() => setHelp(false)}
        aria-labelledby="help-title"
      >
        <div className="dialog-heading">
          <span className="icon-tile">
            <BookOpen size={20} />
          </span>
          <button
            className="icon-button"
            aria-label="Close methodology"
            onClick={() => setHelp(false)}
          >
            <X size={19} />
          </button>
        </div>
        <div className="dialog-kicker">WORKBENCH MANUAL</div>
        <h2 id="help-title">How the numbers are worked out</h2>
        <p>
          Strategy Lab is a historical research tool. The bundled snapshots end on July 2, 2019;
          they are not current prices or forecasts.
        </p>
        <h3>How the strategy works</h3>
        <p>{ASSUMPTIONS}</p>
        <p>
          The first session establishes a cash baseline for the strategy and enters the benchmark.
          Strategy orders begin on the second session. A signal observed at the prior close is
          executed at the current adjusted close; the position held before that execution earns the
          session’s price change.
        </p>
        <h3>How to read the results</h3>
        <p>
          Total return is ending equity divided by starting capital, minus one. Drawdown includes
          initial capital as the first peak. Exposure is the fraction of close-to-close intervals
          held in the market. Volatility is the sample standard deviation of strategy daily returns
          × √252.
        </p>
        <p>
          Buy & hold purchases the same ticker on the first session with the same starting capital
          and entry cost. Open positions are valued at the last price without an assumed exit fee.
          Adjusted-close execution is a simplified model, not an executable price guarantee.
        </p>
        <h3>What to try next</h3>
        <p>
          Run an example, change one assumption, and save both results. Check different periods and
          costs rather than selecting a strategy from one favorable backtest.
        </p>
        <button className="button primary" onClick={() => setHelp(false)}>
          Back to the workbench
          <ArrowRight size={15} />
        </button>
      </dialog>
    </div>
  );
}

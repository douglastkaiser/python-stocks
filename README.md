# python-stocks

Analysis-first stock strategy workbench for decision support. Use it to validate signal quality, pressure-test scenarios, and check execution discipline before committing capital.

- All issues should have a priority tag and one other tag.
- All pull request should be reveiwed before merging.
- Preference is for Python but other options may be considered.

## Decision workflows and dashboard map

The app is organized around three explicit workflows. Each workflow maps to named UI locations so you can move from controls to evidence quickly.

1. **Signal confirmation**
   - **Workflow section:** `1. Signal confirmation`
   - **Primary controls:** `Ticker`, `Lookback window (days)`
   - **Key charts/cards:** `Market replay`, `Signals vs. benchmark`
   - **Related tab:** `Strategy Lab`
2. **Scenario stress-test**
   - **Workflow section:** `2. Scenario stress-test`
   - **Primary controls:** `Stress-test a scenario`, `Scenario controls`, `Timeline horizon`
   - **Key charts/cards:** `Comparison matrix`, `Timeline overlays`
   - **Related tab:** `Comparisons`
3. **Entry/exit discipline check**
   - **Workflow section:** `3. Entry/exit discipline check`
   - **Primary controls:** `Cost drag (bps)`
   - **Key charts/cards:** `Execution costs`
   - **Related tab:** `Cost/Impact Analysis`

The hero area supports all three workflows with quick controls (`Quick ticker`, `Preset windows`) and action CTAs (`Confirm signal`, `Run stress test`, `Run discipline check`).

### Provenance + timestamps in chart views

Every analysis/chart view includes shared metadata for:

- **Source**: the feed backing the chart.
- **Market date (as-of)**: the market session date represented by the data.
- **Last refresh timestamp**: when the app most recently refreshed the dataset.

`Market date` and `last refresh` are intentionally different:

- `Market date` tracks data recency in market terms (e.g., latest trading day included).
- `Last refresh` tracks operational recency (when data retrieval/generation ran).

If the refresh timestamp exceeds the stale threshold, the dashboard surfaces a non-blocking stale-data warning near the chart metadata.

## Start with the dashboard

Use this sequence so the first click matches the published preview flow:

1. **Interactive dashboard preview:** [docs/dashboard/](./docs/dashboard/)
2. **Decision workflow map:** [docs/dashboards.md](./docs/dashboards.md)

The [docs/](./docs) folder also includes deeper references:

- **Strategy catalog:** [docs/strategies.md](./docs/strategies.md) covers how each registered strategy behaves, what data it needs, and which parameters you can tweak.
- **Decision workflow map:** [docs/dashboards.md](./docs/dashboards.md) explains when to use each dashboard tab and what decision each view supports.
- **Methodology:** [docs/methodology.md](./docs/methodology.md) documents metric definitions, cost/slippage assumptions, and backtest limitations.
- **About + disclaimer:** [docs/about.md](./docs/about.md) is the primary location for legal/disclaimer text.
- **Hands-on tutorials:** [docs/tutorials.md](./docs/tutorials.md) mirrors interactive views with notebook-style steps.
- **Market data ingestion:** [docs/market_data.md](./docs/market_data.md) describes the daily provider, cache, quality checks, and demo fallback behavior.
- **Ad hoc release process:** [docs/release_process.md](./docs/release_process.md) provides a lightweight solo-maintainer checklist for safe shipping.

Time-in-market evidence remains available in the `Time in Market` tab as a supporting check, not the primary entry point.

## Dash app quickstart

Run the interactive Dash app locally or in the same artifact-preview mode used by CI:

1. Install the project (from the repo root):
   ```bash
   pip install -e .
   ```
2. Launch the app locally at http://127.0.0.1:8050:
   ```bash
   PYTHONPATH=. python -m python_stocks.dashboard.app
   ```
3. Generate the CI-style artifact preview (no server) with headless Plotly/Matplotlib outputs you can open in a browser:
   ```bash
   make artifacts
   # or directly:
   PYTHONPATH=. PYTHON_STOCKS_TEST_MODE=1 python scripts/generate_artifacts.py --output-dir artifacts
   ```
   This produces Plotly HTML/PNG snapshots under `artifacts/plotly/` and simulation summaries under `artifacts/simulation/` that mirror the GitHub Actions preview artifact.

### Daily real-market data ingestion

The project now supports an incremental daily OHLCV ingest pipeline for the curated symbols `SPY`, `DIA`, `NDAQ`, and `TQQQ`.

- **Provider:** Stooq public daily CSV endpoint (no auth required), wrapped behind a provider abstraction so sources can be swapped later.
- **Cadence:** Run once per market day (after close), e.g. via cron/Task Scheduler.
- **Local store/cache:** `${PYTHON_STOCKS_MARKET_DATA_DIR:-~/.cache/python-stocks/daily}` as per-symbol CSV files.
- **Fallback behavior:** If provider refresh fails, the app keeps using local cache when present; if no cache exists it falls back to bundled demo data under `python_stocks/raw_data`.
- **Data quality checks:** The ingest command reports warnings for missing business days, stale data, and malformed OHLCV rows.

Commands:

```bash
# default curated set
make ingest-daily

# equivalent explicit command
PYTHONPATH=. python -m python_stocks ingest-daily

# full refresh and custom stale threshold
PYTHONPATH=. python -m python_stocks ingest-daily --full-refresh --stale-after 2
```

## Development

Install `pre-commit` and enable the hooks to auto-run Ruff with `--fix` before each commit:

```
pip install pre-commit
pre-commit install
```

### Automation and CI

Local commands for development and CI parity:

- `make lint` runs local static checks (Black, Ruff, mypy, pyright).
- `make test` executes the regression suite with `PYTHON_STOCKS_TEST_MODE=1` (headless matplotlib) and is the primary CI gate.
- `make dash-smoke` runs the Dash layout smoke tests.
- `make artifacts` rebuilds the sample simulations and Plotly snapshots used as CI build artifacts.

The CI job uses `scripts/generate_artifacts.py` to produce PNG/HTML exports from the dashboard demo and CSV/JSON
outputs from a lightweight buy-and-hold simulation. Artifacts are published in the workflow run for download.

## Publish dashboards to GitHub Pages

GitHub Pages now serves content from the `gh-pages` branch so the public site stays in sync with CI assets while leaving the
repository clean:

- **Push to `main` (automatic):** `deploy-main.yml` runs automatically on every push to `main` and publishes the refreshed production site.
- **Manual workflow dispatch:** `deploy-main.yml` can also be run manually from the Actions tab using **Run workflow** (for example, to republish without a new commit).
- **PR previews (automatic publish + automatic cleanup):** `pr-preview.yml` publishes/updates previews at `pr/<number>/` for pull requests, and `pr-cleanup.yml` removes that preview path when the pull request is closed.

You can still regenerate static reports locally into `docs/` with the same command used by the workflows:

```bash
python -m python_stocks run --tickers SPY --start 2015-01-01 --end 2019-01-01 \
  --initial 50000 --report-dir docs --no-show
```

## Preset scenarios

Quick-start scripts live in `configs/` for common strategies:

- `./configs/buy_and_hold.sh`: SPY and DIA buy-and-hold snapshot for GitHub Pages publishing.
- `./configs/ma_crossover.sh`: Multi-parameter moving-average sweep on SPY.
- `./configs/momentum.sh`: Single-ticker TQQQ momentum preset.

Each script writes reports to `docs/` with `--no-show` enabled so the outputs are ready to publish to Pages.

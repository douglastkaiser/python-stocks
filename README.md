# python-stocks

Analysis-first stock strategy workbench for decision support. Use it to validate signal quality, pressure-test scenarios, and check execution discipline before committing capital.

- All issues should have a priority tag and one other tag.
- All pull requests should be reviewed before merging.
- Preference is for Python, but other options may be considered.

## Interactive Strategy Lab

The primary app is a modern, server-free React/TypeScript workspace published on
GitHub Pages. Configure a moving-average crossover, run a historical analysis,
inspect performance/risk/trades, and save or compare named results in your browser.
Every exported result includes its assumptions and evidence.

```sh
npm ci --prefix web
make web-dev
```

Use `make web-test` for calculation tests, `make web-build` to build the production
site, and `make web-browser` for desktop/mobile browser checks after installing
Chromium with `cd web && npx playwright install chromium`.

See [the workspace guide](docs/workspace.md) for architecture, calculations,
data semantics, testing, and publishing. Both the Pages root and `/dashboard/`
serve the complete interactive application. Bundled historical prices end on
**July 2, 2019**; the UI clearly distinguishes this snapshot from live market data.

The Python CLI and legacy Dash app remain available for local analysis below.

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

## Publish Strategy Lab to GitHub Pages

Pushes to `main` and manual runs of `deploy-main.yml` validate and publish the
interactive web application through GitHub Pages artifacts. Pull requests run
web calculation tests, browser checks, and the existing Python CI suite.

```sh
make web-build
python -m http.server 8080 --directory build/site
```

This produces the same self-contained application at the root and `/dashboard/`
with relative assets suitable for project Pages hosting. No Python server runs
in production. The legacy simulation reports can still be generated separately
with the CLI's `--report-dir` option.

## Preset scenarios

Quick-start scripts live in `configs/` for common strategies:

- `./configs/buy_and_hold.sh`: SPY and DIA buy-and-hold snapshot for GitHub Pages publishing.
- `./configs/ma_crossover.sh`: Multi-parameter moving-average sweep on SPY.
- `./configs/momentum.sh`: Single-ticker TQQQ momentum preset.

Each script writes reports to `docs/` with `--no-show` enabled so the outputs are ready to publish to Pages.

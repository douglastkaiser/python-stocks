# python-stocks

Stock market simulator to test out stock buy/sell strategies and to analyze risk profiles.

- All issues should have a priority tag and one other tag.
- All pull request should be reveiwed before merging.
- Preference is for Python but other options may be considered.

## Guided dashboards and strategy explainers

The [docs/](./docs) folder now includes guided walk-throughs for every available strategy, the comparison dashboards, and the core lesson we keep seeing in simulations: markets are tough to beat, so time **in** the market usually wins over attempts to time entries and exits.

- **Strategy catalog:** [docs/strategies.md](./docs/strategies.md) covers how each registered strategy behaves, what data it needs, and which parameters you can tweak.
- **Dashboard tour:** [docs/dashboards.md](./docs/dashboards.md) explains the Dash tabs (overview, strategy lab, cost/impact, comparisons, time-in-market, diagnostics) and how they illustrate market efficiency and holding-period discipline.
- **Hands-on tutorials:** [docs/tutorials.md](./docs/tutorials.md) mirrors the interactive views with notebook-style steps so you can reproduce the plots without launching the UI.

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

## Development

Install `pre-commit` and enable the hooks to auto-run Ruff with `--fix` before each commit:

```
pip install pre-commit
pre-commit install
```

### Automation and CI

Local commands mirror the GitHub Actions workflow:

- `make lint` runs Ruff checks.
- `make test` executes the regression suite with `PYTHON_STOCKS_TEST_MODE=1` (headless matplotlib).
- `make dash-smoke` runs the Dash layout smoke tests.
- `make artifacts` rebuilds the sample simulations and Plotly snapshots used as CI build artifacts.

The CI job uses `scripts/generate_artifacts.py` to produce PNG/HTML exports from the dashboard demo and CSV/JSON
outputs from a lightweight buy-and-hold simulation. Artifacts are published in the workflow run for download.

## Publish dashboards to GitHub Pages

Generate static plots and reports into the `docs/` folder and point GitHub Pages at that directory:

```bash
python -m python_stocks run --tickers SPY --start 2015-01-01 --end 2019-01-01 \
  --initial 50000 --report-dir docs --no-show
```

Then enable GitHub Pages in your repository settings (branch: `main` or `master`, folder: `/docs`). Assets will be served from
`https://douglastkaiser.github.io/python-stocks/`.

An automated workflow (`.github/workflows/publish-docs.yml`) rebuilds the `docs/` folder on every push to `main` and on pull
requests (for preview deployments). It runs a lightweight SPY+DIA sample backtest in headless mode, uploads the generated
CSV/JSON, PNG, and interactive HTML assets as a Pages artifact, posts a preview link on pull requests, and deploys without
committing the artifacts back to the repository.

## Preset scenarios

Quick-start scripts live in `configs/` for common strategies:

- `./configs/buy_and_hold.sh`: SPY and DIA buy-and-hold snapshot for GitHub Pages publishing.
- `./configs/ma_crossover.sh`: Multi-parameter moving-average sweep on SPY.
- `./configs/momentum.sh`: Single-ticker TQQQ momentum preset.

Each script writes reports to `docs/` with `--no-show` enabled so the outputs are ready to publish to Pages.

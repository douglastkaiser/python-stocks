# python-stocks dashboards

You can publish static dashboards for this project using GitHub Pages (via the `docs/` folder) without adding any new infrastructure.

## Quick start
1. Run a simulation and tell the CLI to write reports and plots to `docs/`:
   ```bash
   python -m python_stocks run --tickers SPY AAPL --start 2015-01-01 --end 2020-01-01 \
     --initial 50000 --monthly 500 --report-dir docs --no-show
   ```
   * `--report-dir docs` writes `strategy_summary.csv`, `strategy_summary.json`, and PNG charts under `docs/assets/`.
   * `--no-show` keeps the run non-interactive so it works in CI.

2. Commit the generated `docs/` contents and push to GitHub.

3. In your repository settings, enable **GitHub Pages** with the **Source** set to `Deploy from a branch` → `main` → `/docs`. The dashboards will be available at `https://douglastkaiser.github.io/python-stocks/`.

## What gets published?
- Static plots for the portfolio curve and each ticker (PNG files under `docs/assets/figure_*.png`).
- Strategy performance summaries in both CSV and JSON formats.

You can customize or add richer dashboards (e.g., embed Plotly or Vega-Lite visuals) by replacing `docs/index.md` with your own content and linking to the generated assets.

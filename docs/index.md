# python-stocks dashboards

Static dashboards under `/docs` are ready to publish directly to GitHub Pages. The `publish-docs` workflow rebuilds a small
sample backtest (SPY + DIA, 2017–2018) on every push to `main` and every pull request (for Draft Preview deployments). Each run
saves CSV/JSON summaries, PNG charts, and interactive HTML embeds so visitors always have something to browse without running the
simulator themselves.

## Starter dashboard (SPY + DIA)

The assets published to GitHub Pages come from `python -m python_stocks run --tickers SPY DIA --start 2017-01-01 --end
2018-01-01 --initial 50000 --monthly 500 --strategies buy_and_hold moving_average_filter --report-dir docs --no-show`. They are
generated in CI and uploaded as a Pages artifact (they are not committed to the repository to avoid giant HTML diffs).

- Strategy summaries: [strategy_summary.csv](./strategy_summary.csv) · [strategy_summary.json](./strategy_summary.json)
- Static plots: [figure_1.png](./assets/figure_1.png), [figure_2.png](./assets/figure_2.png), [figure_3.png](./assets/figure_3.png)
- Interactive price views: [SPY](./assets/spy_interactive.html) · [DIA](./assets/dia_interactive.html) (generated on the fly by
  the Pages workflow)

## Publish automatically

The GitHub Actions workflow at `.github/workflows/publish-docs.yml` installs the project, runs the sample simulation with
`--report-dir docs --no-show`, uploads the refreshed assets as a Pages artifact, posts a PR comment with the preview link, and
deploys the site to GitHub Pages (including Draft Preview deployments on pull requests). Point GitHub Pages at the `docs/`
folder (branch: `main`, folder: `/docs`) to serve the dashboards at your Pages URL.

## Run your own simulations

1. Use the CLI directly:
   ```bash
   python -m python_stocks run --tickers SPY DIA --start 2017-01-01 --end 2018-01-01 \
     --initial 50000 --monthly 500 --report-dir docs --no-show
   ```
   This writes the summary CSV/JSON and PNG/HTML assets under `docs/` for GitHub Pages.

2. Or run one of the presets from the repo root:
   ```bash
   ./configs/buy_and_hold.sh
   ./configs/ma_crossover.sh
   ./configs/momentum.sh
   ```

3. Push your branch and open a pull request to get an automatic Draft Preview, or push to `main` to refresh the published
   dashboard.

Feel free to customize the markdown content here, swap in your own visuals, or tweak the presets for different portfolios or
timeframes. For more guided context, see the new walkthroughs:

- [Strategy catalog](./strategies.md) for descriptions and parameter tips.
- [Dashboard tour](./dashboards.md) for a tab-by-tab explanation of the interactive views.
- [Tutorials](./tutorials.md) to recreate the Dash visuals in notebooks or scripts without running a server.

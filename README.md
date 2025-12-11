# python-stocks

Stock market simulator to test out stock buy/sell strategies and to analyze risk profiles.

- All issues should have a priority tag and one other tag.
- All pull request should be reveiwed before merging.
- Preference is for Python but other options may be considered.

## Development

Install `pre-commit` and enable the hooks to auto-run Ruff with `--fix` before each commit:

```
pip install pre-commit
pre-commit install
```

## Publish dashboards to GitHub Pages

Generate static plots and reports into the `docs/` folder and point GitHub Pages at that directory:

```bash
python -m python_stocks run --tickers SPY --start 2015-01-01 --end 2019-01-01 \
  --initial 50000 --report-dir docs --no-show
```

Then enable GitHub Pages in your repository settings (branch: `main`, folder: `/docs`). Assets will be served from
`https://douglastkaiser.github.io/python-stocks/`.

An automated workflow (`.github/workflows/publish-docs.yml`) rebuilds the `docs/` folder on every push to `main`, on pull
requests (for preview deployments), and on a weekly schedule. It runs a lightweight SPY+DIA sample backtest in headless mode,
uploads the generated CSV/JSON, PNG, and interactive HTML assets as a Pages artifact, and deploys without committing the
artifacts back to the repository.

## Preset scenarios

Quick-start scripts live in `configs/` for common strategies:

- `./configs/buy_and_hold.sh`: SPY and DIA buy-and-hold snapshot for GitHub Pages publishing.
- `./configs/ma_crossover.sh`: Multi-parameter moving-average sweep on SPY.
- `./configs/momentum.sh`: Single-ticker TQQQ momentum preset.

Each script writes reports to `docs/` with `--no-show` enabled so the outputs are ready to publish to Pages.

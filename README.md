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

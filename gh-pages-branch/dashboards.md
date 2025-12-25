# Dashboard tour

The Dash app ships with opinionated tabs that pair with the static assets published to GitHub Pages. Use this guide to understand how each view illustrates market efficiency and the value of staying invested.

## Overview
- **What it shows:** Price trend with overlays from the demo dataset (AAPL, MSFT, SPY).
- **Takeaway:** A simple price view establishes context for the strategy and cost experiments on other tabs.

## Strategy Lab
- **What it shows:** Moving-average crossover signals, trade markers, and cost drag controls.
- **Takeaway:** Timing can trim drawdowns but often misses upside—compare against `buy_and_hold` to see if churn is worthwhile.

## Cost / Impact Analysis
- **What it shows:** Adjustable basis-point cost slider with impact curves.
- **Takeaway:** Even tiny frictions can erase the theoretical edge of high-turnover strategies, reinforcing that patient holding often wins after costs.

## Comparisons
- **What it shows:** Matrix heatmap of strategy combinations and parameter windows, plus a timeline overlay.
- **Takeaway:** The best-performing cells usually belong to longer holding windows or less reactive configurations, underscoring the time-in-market theme.

## Time in Market
- **What it shows:** Focused view on holding-period discipline and missed-days scenarios.
- **Takeaway:** Demonstrates how skipping a handful of strong days can crater returns relative to simply staying invested.

## Data Diagnostics
- **What it shows:** Daily return distribution checks for sanity before drawing conclusions from simulations.
- **Takeaway:** Helps confirm whether outlier moves or bad data (e.g., missing opens) skew strategy comparisons.

## Preview without running a server
- Run `make artifacts` to create the Plotly HTML/PNG exports under `artifacts/plotly/`.
- Open `artifacts/plotly/price_trend.html` or `.../comparison_matrix.html` locally for a fast preview of the Dash visuals used in CI Draft Preview deployments.

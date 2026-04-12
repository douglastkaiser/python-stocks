---
layout: default
title: Methodology
---
# Methodology

This page documents the assumptions behind dashboard metrics and backtest-style visualizations.
For legal/disclaimer text, use the [About page](./about.md).

## Metric definitions

### Return and trend metrics
- **Trailing return (`Nd`)**: `(last close / close N sessions ago) - 1` using trading-session closes.
- **MA spread**: `(MA10 - MA50) / latest close` as a directional trend proxy.
- **Spread delta**: change in MA spread relative to the prior 10-session anchor.
- **Annualized volatility**: standard deviation of daily close-to-close returns scaled by `sqrt(252)`.

### Risk and participation context
- **Drawdown**: `(close / running peak) - 1`.
- **Rolling drawdown floor (20d)**: minimum drawdown over the last 20 sessions.
- **Turnover proxy**: 5-session rolling mean of absolute daily returns.
- **Volume ratio**: latest volume divided by trailing 20-session median volume.
- **Time in market**: share of sessions where the strategy state is invested.

### Comparison/stress-test views
- **Comparison matrix coordinates**:
  - x-axis: annualized volatility estimate.
  - y-axis: average daily return scaled to percent.
  - bubble size: estimated impact cost magnitude from the configured cost penalty.
- **Timeline overlays**: simulated strategy-equity paths over the selected horizon for side-by-side robustness checks.

## Slippage and cost assumptions

- **Cost drag input** uses **basis points (bps)** and represents an aggregate per-turnover execution friction assumption.
- **Narrative drag estimate** is an approximation: `annualized volatility * (cost_bps / 10,000)`.
- **Comparison matrix cost penalty** is a simplified scalar applied to volatility and turnover-sensitive views.
- **Liquidity context** in cost charts is derived from sample volume normalization and is not a live order-book impact model.

## Backtest caveats and limitations

- Dashboard strategy visuals are **illustrative backtest-style diagnostics**, not a live OMS/PMS execution log.
- Sample data and demo presets are deterministic for reproducible CI artifacts; they are not optimized forecasts.
- Models do not include full market microstructure effects (queue position, partial fills, spread dynamics, latency).
- Transaction costs, taxes, borrow fees, and venue-specific fees are simplified or omitted unless explicitly modeled.
- Results are sensitive to lookback windows, horizon selection, and input data quality.
- Historical performance in these charts does not guarantee future outcomes.

## How to use this page in workflow

1. Use dashboard chart-level **Assumptions used** toggles for quick context.
2. Use this Methodology page when validating numbers before sharing or acting on results.
3. Keep policy/disclaimer/legal review in [About](./about.md), so analysis screens stay focused.

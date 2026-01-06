# Strategy catalog

This guide summarizes the built-in strategies, their required data, and the levers you can adjust when running simulations via `python -m python_stocks run ...` or by supplying overrides to the Dash app.

## Core lesson: time in market beats timing

Across the preset runs, buy-and-hold routinely fares well versus timing attempts. The comparison and time-in-market dashboards reinforce that compounding during long holding windows usually outweighs minor timing edges—so use the experiments below to understand risk and drift, not to expect perfect market timing.

## Registered strategies

### `buy_and_hold`
- **Intent:** Deploy all available cash into a single ticker and hold through the simulation.
- **Data needs:** `Close`
- **Parameters:**
  - `ticker` — symbol to hold (expanded across all loaded tickers by default).
- **Notes:** The baseline for most comparisons; great for highlighting the drag of transaction costs and the benefit of staying invested.

### `moving_average_filter`
- **Intent:** Trade when a short-term moving average crosses a long-term one with slope checks.
- **Data needs:** `Close`
- **Parameters:**
  - `ticker` — symbol to trade.
  - `short_window` — short lookback (defaults to 10 or 20 days).
  - `long_window` — long lookback (defaults to 100 or 200 days).
- **Notes:** Useful for illustrating whipsaw risk: late entries can miss strong trends while exits can trim drawdowns.

### `open_close`
- **Intent:** Buy or sell at the open based on the previous close.
- **Data needs:** `Open`, `Close`
- **Parameters:**
  - `ticker` — symbol to trade.
- **Notes:** Designed to show how fragile open/close gaps can be versus simply holding; compare against the `buy_and_hold` benchmark to emphasize the cost of churn.

### `marcus_savings`
- **Intent:** Apply a fixed savings-account style interest accrual.
- **Data needs:** None beyond cash balance.
- **Parameters:**
  - `interest_rate` — annualized rate (defaults to 2.25%).
- **Notes:** Provides a low-volatility cash benchmark and a reminder that risk-free rates can rival poorly timed equity strategies in short windows.

### `no_investment`
- **Intent:** Hold 100% cash (no trades) for baseline comparisons.
- **Data needs:** None beyond cash balance.
- **Parameters:** None.
- **Notes:** Highlights the opportunity cost of sitting out of the market, especially in the time-in-market overlays.

## Parameter sweeps and overrides

Strategy parameters expand into grids automatically. Override defaults by passing `--param` flags such as:

```bash
python -m python_stocks run --tickers SPY DIA --strategies moving_average_filter \
  --param moving_average_filter.short_window=10,30 \
  --param moving_average_filter.long_window=120
```

The registry expands these into all combinations, making it easy to explore where timing helps—or where staying invested still wins.

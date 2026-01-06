# Tutorials: recreate the dashboard views without the UI

The snippets below mirror the Dash tabs so you can explore the same ideas in a notebook or Markdown setting. They rely on the lightweight `MarketSample` demo data that powers the CI artifacts.

## 1) Price overview and strategy signals

Generate the overview and strategy-signal plots for a chosen ticker:

```bash
python - <<'PY'
from pathlib import Path
from python_stocks.dashboard.components import MarketSample, price_trend_figure, strategy_signal_figure
from python_stocks.dashboard.theme import get_theme, DEFAULT_THEME_KEY

sample = MarketSample.demo(["AAPL", "MSFT", "SPY"], periods=180)
theme = get_theme(DEFAULT_THEME_KEY)
output = Path("tutorial_outputs")
output.mkdir(exist_ok=True)

price_trend_figure(sample, "AAPL", theme).write_html(output / "overview.html")
strategy_signal_figure(sample, "AAPL", theme).write_html(output / "strategy.html")
print("Wrote", list(output.iterdir()))
PY
```

Open `tutorial_outputs/overview.html` in a browser to see the same visualization used on the Overview tab.

## 2) Cost/impact and comparison matrix

Explore how transaction costs and lookback windows change the story:

```bash
python - <<'PY'
from pathlib import Path
from python_stocks.dashboard.components import (
    MarketSample,
    comparison_matrix_figure,
    cost_impact_figure,
)
from python_stocks.dashboard.theme import get_theme, DEFAULT_THEME_KEY

sample = MarketSample.demo(["AAPL", "MSFT", "SPY"], periods=180)
theme = get_theme(DEFAULT_THEME_KEY)
output = Path("tutorial_outputs")
output.mkdir(exist_ok=True)

cost_impact_figure(sample, "MSFT", theme).write_html(output / "cost_impact.html")
comparison_matrix_figure(sample, "MSFT", theme, window=120, cost_penalty=0.0025).write_html(output / "comparison.html")
print("Wrote", list(output.iterdir()))
PY
```

Compare `cost_impact.html` against `comparison.html` to see how rising frictions erode reactive strategies in the heatmap.

## 3) Time-in-market lesson

Reproduce the hold-vs-miss-days illustration:

```bash
python - <<'PY'
from pathlib import Path
from python_stocks.dashboard.components import MarketSample, time_in_market_figure, timeline_overlay_figure
from python_stocks.dashboard.theme import get_theme, DEFAULT_THEME_KEY

sample = MarketSample.demo(["AAPL", "MSFT", "SPY"], periods=252)
theme = get_theme(DEFAULT_THEME_KEY)
output = Path("tutorial_outputs")
output.mkdir(exist_ok=True)

time_in_market_figure(sample, "SPY", theme).write_html(output / "time_in_market.html")
timeline_overlay_figure(sample, "SPY", theme, horizon=252).write_html(output / "timeline_overlay.html")
print("Wrote", list(output.iterdir()))
PY
```

Opening `time_in_market.html` shows the key lesson: missing just a few strong days can outweigh months of well-timed exits, so long holding windows tend to dominate timing attempts.

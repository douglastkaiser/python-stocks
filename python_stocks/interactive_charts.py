"""Export lightweight interactive charts for GitHub Pages."""
import json
from pathlib import Path
from typing import Iterable, List

import numpy as np
import pandas as pd


VEGA_SCRIPTS = """
<script src="https://cdn.jsdelivr.net/npm/vega@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-lite@5"></script>
<script src="https://cdn.jsdelivr.net/npm/vega-embed@6"></script>
"""


def _moving_average(series: pd.Series, window: int) -> pd.Series:
    return series.rolling(window=window, min_periods=1).mean()


def _build_spec(ticker: str, table: pd.DataFrame) -> dict:
    return {
        "$schema": "https://vega.github.io/schema/vega-lite/v5.json",
        "description": f"Interactive price view for {ticker}",
        "data": {"values": table.to_dict(orient="records")},
        "layer": [
            {
                "mark": {"type": "line", "color": "#2563eb"},
                "encoding": {
                    "x": {"field": "date", "type": "temporal", "title": "Date"},
                    "y": {"field": "close", "type": "quantitative", "title": "Price"},
                    "tooltip": ["date", "close", "ma10", "ma100"],
                },
            },
            {
                "mark": {"type": "line", "color": "#16a34a"},
                "encoding": {"x": {"field": "date", "type": "temporal"}, "y": {"field": "ma10", "type": "quantitative"}},
            },
            {
                "mark": {"type": "line", "color": "#f97316"},
                "encoding": {"x": {"field": "date", "type": "temporal"}, "y": {"field": "ma100", "type": "quantitative"}},
            },
        ],
        "resolve": {"scale": {"y": "shared"}},
    }


def _build_html(ticker: str, spec: dict) -> str:
    spec_id = f"{ticker}-spec"
    container_id = f"{ticker}-chart"
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\" />\n"
        "<title>{title}</title>\n{scripts}\n</head>\n<body>\n"
        "<div id=\"{container}\" style=\"max-width:900px;margin:auto;\"></div>\n"
        "<script type=\"application/json\" id=\"{spec_id}\">{spec}</script>\n"
        "<script>const spec = JSON.parse(document.getElementById('{spec_id}').textContent);"
        "vegaEmbed('#{container}', spec, {{actions:false}});</script>\n"
        "</body>\n</html>\n"
    ).format(title=f"{ticker} interactive chart", scripts=VEGA_SCRIPTS, container=container_id, spec_id=spec_id, spec=json.dumps(spec))


def export_interactive_price_charts(
    tickers: Iterable[str], stock_history: pd.DataFrame, output_dir: Path
) -> List[Path]:
    """Persist interactive HTML line charts for each ticker.

    Args:
        tickers: The ordered collection of ticker symbols to render.
        stock_history: Multi-indexed DataFrame with ticker symbols as the top
            level and OHLC columns on the second level.
        output_dir: Destination directory for the generated HTML files.

    Returns:
        List of paths to the generated HTML assets.
    """

    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: List[Path] = []

    for ticker in tickers:
        close_series = stock_history[ticker]["Close"].replace([np.inf, -np.inf], np.nan).dropna()
        if close_series.empty:
            continue

        table = pd.DataFrame(
            {
                "date": close_series.index,
                "close": close_series,
            }
        )
        table["date"] = pd.to_datetime(table["date"]).dt.strftime("%Y-%m-%d")
        table["ma10"] = _moving_average(close_series, window=10)
        table["ma100"] = _moving_average(close_series, window=100)

        spec = _build_spec(ticker, table)
        output_path = output_dir / f"{ticker.lower()}_interactive.html"
        output_path.write_text(_build_html(ticker, spec))
        saved_paths.append(output_path)

    return saved_paths

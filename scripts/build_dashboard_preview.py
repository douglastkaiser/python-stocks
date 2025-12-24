"""Generate a static dashboard preview page for GitHub Pages previews."""

# ruff: noqa: E402

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import plotly.io as pio

from python_stocks.dashboard.components.figures import (
    cost_impact_figure,
    price_trend_figure,
    strategy_signal_figure,
    time_in_market_figure,
)  # noqa: E402
from python_stocks.dashboard.components.comparison import (
    comparison_matrix_figure,
    timeline_overlay_figure,
)  # noqa: E402
from python_stocks.dashboard.components.market import MarketSample  # noqa: E402
from python_stocks.dashboard.theme import DEFAULT_THEME_KEY, get_theme  # noqa: E402


def _render_figure_html(fig, theme) -> str:
    return pio.to_html(
        fig,
        include_plotlyjs="cdn",
        full_html=False,
        config={"displayModeBar": False},
        default_width="100%",
        default_height="320px",
    ).replace("plotly-graph-div", f"plotly-graph-div theme-{theme['mode']}")


def build_preview(output_root: Path) -> None:
    output_dir = output_root / "dashboard"
    output_dir.mkdir(parents=True, exist_ok=True)

    css_src = (
        Path(__file__).resolve().parent.parent
        / "python_stocks"
        / "dashboard"
        / "assets"
        / "dashboard.css"
    )
    css_text = css_src.read_text()

    sample = MarketSample.demo(["AAPL", "MSFT", "SPY", "QQQ"])
    theme = get_theme(DEFAULT_THEME_KEY)

    figures = {
        "price": price_trend_figure(sample, "AAPL", theme),
        "strategy": strategy_signal_figure(sample, "AAPL", theme),
        "cost": cost_impact_figure(sample, "AAPL", theme),
        "matrix": comparison_matrix_figure(
            sample, "AAPL", theme, window=90, cost_penalty=0.0025
        ),
        "timeline": timeline_overlay_figure(sample, "AAPL", theme, horizon=120),
        "time_mix": time_in_market_figure(sample, "AAPL", theme),
    }

    hero = """
    <section class="page-shell" style="padding: 24px 0;">
      <div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap;">
        <div style="display:flex;flex-direction:column;gap:4px;">
          <div style="font-size:14px;color:#64748b;font-weight:600;">Preview the Strategy Lab dashboard</div>
          <h1 style="margin:0;">Build resilient, cost-aware equity rules</h1>
          <p style="max-width:720px;font-size:16px;color:#475569;">
            This static preview mirrors the homepage layout so you can quickly evaluate graphs, hero copy, and spotlight sections.
            The live Dash app in production adds interactivity; this page keeps the visuals aligned with what will ship.
          </p>
          <div style="display:flex;gap:10px;flex-wrap:wrap;">
            <a href="../assets/spy_interactive.html" class="cta primary">View SPY interactive sample</a>
            <a href="../dashboards.md" class="cta secondary">Tour the full docs</a>
          </div>
        </div>
      </div>
    </section>
    """

    showcase = f"""
    <section class="page-shell" style="display:flex;flex-direction:column;gap:18px;">
      <div style="display:flex;flex-direction:column;gap:6px;">
        <div class="eyebrow">Guided dashboards and strategy explainers</div>
        <h2 style="margin:0;">Front-page spotlights for faster evaluation</h2>
        <p style="margin:0;color:{theme['muted_text']};max-width:880px;">
          Key visuals from the Dash app are pinned to the preview so reviewers can sanity-check tone, layout, and figure styling without
          spinning up the server. Inputs in production stay wired to the same components shown below.
        </p>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px;">
        <div class="surface-card">
          <h3>Market replay</h3>
          <p class="muted">Moving-average overlays make price context easier to read.</p>
          {_render_figure_html(figures["price"], theme)}
        </div>
        <div class="surface-card">
          <h3>Signals vs. benchmark</h3>
          <p class="muted">Equity curves update live as you tweak the lookback window.</p>
          {_render_figure_html(figures["strategy"], theme)}
        </div>
        <div class="surface-card">
          <h3>Execution costs</h3>
          <p class="muted">Costs and liquidity are front-and-center instead of buried in tooltips.</p>
          {_render_figure_html(figures["cost"], theme)}
        </div>
        <div class="surface-card">
          <h3>Comparison matrix</h3>
          <p class="muted">Return, volatility, and cost reactions in one view.</p>
          {_render_figure_html(figures["matrix"], theme)}
        </div>
        <div class="surface-card">
          <h3>Timeline overlays</h3>
          <p class="muted">Contextualize signals against events and market phases.</p>
          {_render_figure_html(figures["timeline"], theme)}
        </div>
        <div class="surface-card">
          <h3>Time in market</h3>
          <p class="muted">Estimate of time spent participating in positive trends.</p>
          {_render_figure_html(figures["time_mix"], theme)}
        </div>
      </div>
    </section>
    """

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Dashboard Preview</title>
  <style>
  :root {{ --page-max-width: 1200px; }}
  body {{
    margin: 0;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: radial-gradient(circle at 20% 20%, rgba(56, 189, 248, 0.08), transparent 35%),
      radial-gradient(circle at 80% 0%, rgba(99, 102, 241, 0.12), transparent 30%),
      #f8fafc;
  }}
  .page-shell {{
    max-width: var(--page-max-width);
    margin: 0 auto;
    padding: 0 16px;
  }}
  .cta {{
    display:inline-flex;
    align-items:center;
    justify-content:center;
    padding:10px 16px;
    border-radius:12px;
    font-weight:600;
    text-decoration:none;
    transition:transform 0.1s ease, box-shadow 0.1s ease;
    border:1px solid #cbd5e1;
  }}
  .cta.primary {{
    background:#2563eb;
    color:#0b1224;
    box-shadow:0 10px 30px rgba(37,99,235,0.25);
  }}
  .cta.secondary {{
    background:transparent;
    color:#0f172a;
  }}
  .eyebrow {{
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 12px;
    color: #64748b;
    font-weight: 700;
  }}
  .surface-card {{
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
  }}
  .surface-card h3 {{ margin: 0; }}
  .muted {{ color: #64748b; margin: 0; }}
  {css_text}
  </style>
</head>
<body>
  {hero}
  {showcase}
</body>
</html>
"""

    (output_dir / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("build/site")
    build_preview(target)

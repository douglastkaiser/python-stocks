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
from python_stocks.dashboard.theme import (  # noqa: E402
    DEFAULT_THEME_KEY,
    THEMES,
    get_theme,
)


def _render_figure_html(fig, theme) -> str:
    return pio.to_html(
        fig,
        include_plotlyjs="cdn",
        full_html=False,
        config={"displayModeBar": False},
        default_width="100%",
        default_height="320px",
    ).replace("plotly-graph-div", f"plotly-graph-div theme-{theme['mode']}")


def _render_themed_figure_html(light_fig, dark_fig) -> str:
    return "".join(
        [
            '<div class="theme-only theme-light">',
            _render_figure_html(light_fig, THEMES["light"]),
            "</div>",
            '<div class="theme-only theme-dark">',
            _render_figure_html(dark_fig, THEMES["dark"]),
            "</div>",
        ]
    )


def _theme_tokens(mode: str) -> str:
    theme = THEMES[mode]
    return "\n".join(
        [
            f"  --dashboard-mode: {theme['mode']};",
            f"  --dashboard-background: {theme['background']};",
            f"  --dashboard-panel: {theme['panel']};",
            f"  --dashboard-text: {theme['text']};",
            f"  --dashboard-muted-text: {theme['muted_text']};",
            f"  --dashboard-accent: {theme['accent']};",
            f"  --dashboard-accent-alt: {theme['accent_alt']};",
            f"  --dashboard-grid: {theme['grid']};",
            f"  --dashboard-plot-bg: {theme['plot_bg']};",
            f"  --dashboard-paper-bg: {theme['paper_bg']};",
        ]
    )


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
    light_theme = get_theme("light")
    dark_theme = get_theme("dark")

    figures = {
        "light": {
            "price": price_trend_figure(sample, "AAPL", light_theme),
            "strategy": strategy_signal_figure(sample, "AAPL", light_theme),
            "cost": cost_impact_figure(sample, "AAPL", light_theme),
            "matrix": comparison_matrix_figure(
                sample, "AAPL", light_theme, window=90, cost_penalty=0.0025
            ),
            "timeline": timeline_overlay_figure(
                sample, "AAPL", light_theme, horizon=120
            ),
            "time_mix": time_in_market_figure(sample, "AAPL", light_theme),
        },
        "dark": {
            "price": price_trend_figure(sample, "AAPL", dark_theme),
            "strategy": strategy_signal_figure(sample, "AAPL", dark_theme),
            "cost": cost_impact_figure(sample, "AAPL", dark_theme),
            "matrix": comparison_matrix_figure(
                sample, "AAPL", dark_theme, window=90, cost_penalty=0.0025
            ),
            "timeline": timeline_overlay_figure(
                sample, "AAPL", dark_theme, horizon=120
            ),
            "time_mix": time_in_market_figure(sample, "AAPL", dark_theme),
        },
    }

    hero = """
    <section class="page-shell hero-shell">
      <div class="hero-header-row">
        <div class="hero-stack">
          <div class="hero-kicker">Preview the Strategy Lab dashboard</div>
          <h1 class="hero-title">Build resilient, cost-aware equity rules</h1>
          <p class="hero-copy">
            This static preview mirrors the homepage layout so you can quickly evaluate graphs, hero copy, and spotlight sections.
            The live Dash app in production adds interactivity; this page keeps the visuals aligned with what will ship.
          </p>
          <div class="hero-actions">
            <a href="../assets/spy_interactive.html" class="cta primary">View SPY interactive sample</a>
            <a href="../dashboards.md" class="cta secondary">Tour the full docs</a>
          </div>
        </div>
        <div class="theme-switch" role="group" aria-label="Theme selector">
          <span class="theme-switch-label">Theme</span>
          <button type="button" class="theme-button" data-theme-choice="Light">Light</button>
          <button type="button" class="theme-button" data-theme-choice="Dark">Dark</button>
        </div>
      </div>
    </section>
    """

    showcase = f"""
    <section class="page-shell showcase-shell">
      <div class="showcase-header">
        <div class="eyebrow">Guided dashboards and strategy explainers</div>
        <h2 class="showcase-title">Front-page spotlights for faster evaluation</h2>
        <p class="showcase-copy">
          Key visuals from the Dash app are pinned to the preview so reviewers can sanity-check tone, layout, and figure styling without
          spinning up the server. Inputs in production stay wired to the same components shown below.
        </p>
      </div>
      <div class="showcase-grid">
        <div class="surface-card">
          <h3>Market replay</h3>
          <p class="muted">Moving-average overlays make price context easier to read.</p>
          {_render_themed_figure_html(figures["light"]["price"], figures["dark"]["price"])}
        </div>
        <div class="surface-card">
          <h3>Signals vs. benchmark</h3>
          <p class="muted">Equity curves update live as you tweak the lookback window.</p>
          {_render_themed_figure_html(figures["light"]["strategy"], figures["dark"]["strategy"])}
        </div>
        <div class="surface-card">
          <h3>Execution costs</h3>
          <p class="muted">Costs and liquidity are front-and-center instead of buried in tooltips.</p>
          {_render_themed_figure_html(figures["light"]["cost"], figures["dark"]["cost"])}
        </div>
        <div class="surface-card">
          <h3>Comparison matrix</h3>
          <p class="muted">Return, volatility, and cost reactions in one view.</p>
          {_render_themed_figure_html(figures["light"]["matrix"], figures["dark"]["matrix"])}
        </div>
        <div class="surface-card">
          <h3>Timeline overlays</h3>
          <p class="muted">Contextualize signals against events and market phases.</p>
          {_render_themed_figure_html(figures["light"]["timeline"], figures["dark"]["timeline"])}
        </div>
        <div class="surface-card">
          <h3>Time in market</h3>
          <p class="muted">Estimate of time spent participating in positive trends.</p>
          {_render_themed_figure_html(figures["light"]["time_mix"], figures["dark"]["time_mix"])}
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
  :root {{
    --page-max-width: 1200px;
    --theme-toggle-bg: rgba(148, 163, 184, 0.15);
    --theme-toggle-border: rgba(148, 163, 184, 0.35);
    --theme-button-bg: transparent;
    --theme-button-text: var(--dashboard-text);
    --theme-button-active-bg: var(--dashboard-accent);
    --theme-button-active-text: #ffffff;
    --hero-kicker: #64748b;
    --hero-gradient-a: rgba(56, 189, 248, 0.08);
    --hero-gradient-b: rgba(99, 102, 241, 0.12);
  }}
  [data-theme="light"] {{
{_theme_tokens("light")}
  }}
  [data-theme="dark"] {{
{_theme_tokens("dark")}
    --theme-toggle-bg: rgba(15, 23, 42, 0.7);
    --theme-toggle-border: rgba(148, 163, 184, 0.3);
    --theme-button-active-text: #0b1224;
    --hero-kicker: #cbd5e1;
    --hero-gradient-a: rgba(56, 189, 248, 0.14);
    --hero-gradient-b: rgba(99, 102, 241, 0.2);
  }}
  body {{
    margin: 0;
    font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    color: var(--dashboard-text);
    background: radial-gradient(circle at 20% 20%, var(--hero-gradient-a), transparent 35%),
      radial-gradient(circle at 80% 0%, var(--hero-gradient-b), transparent 30%),
      var(--dashboard-background);
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
    border:1px solid var(--dashboard-grid);
  }}
  .cta.primary {{
    background:var(--dashboard-accent);
    color:#ffffff;
    box-shadow:0 10px 30px color-mix(in srgb, var(--dashboard-accent) 35%, transparent);
  }}
  .cta.secondary {{
    background:var(--dashboard-panel);
    color:var(--dashboard-text);
  }}
  .eyebrow {{
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-size: 12px;
    color: var(--hero-kicker);
    font-weight: 700;
  }}
  .hero-shell {{ padding: 24px 0; }}
  .hero-header-row {{ display:flex;justify-content:space-between;align-items:flex-start;gap:16px;flex-wrap:wrap; }}
  .hero-stack {{ display:flex;flex-direction:column;gap:4px; }}
  .hero-kicker {{ font-size:14px;color:var(--hero-kicker);font-weight:600; }}
  .hero-title {{ margin:0; }}
  .hero-copy {{ max-width:720px;font-size:16px;color:var(--dashboard-muted-text); }}
  .hero-actions {{ display:flex;gap:10px;flex-wrap:wrap; }}
  .theme-switch {{
    display:inline-flex;
    align-items:center;
    gap:6px;
    padding:6px;
    border-radius:999px;
    border:1px solid var(--theme-toggle-border);
    background:var(--theme-toggle-bg);
  }}
  .theme-switch-label {{ font-size:12px; font-weight:600; color:var(--dashboard-muted-text); padding: 0 4px; }}
  .theme-button {{
    border:0;
    border-radius:999px;
    padding:6px 12px;
    cursor:pointer;
    font-weight:600;
    background:var(--theme-button-bg);
    color:var(--theme-button-text);
  }}
  .theme-button.is-active {{
    background:var(--theme-button-active-bg);
    color:var(--theme-button-active-text);
  }}
  .showcase-shell {{ display:flex;flex-direction:column;gap:18px; }}
  .showcase-header {{ display:flex;flex-direction:column;gap:6px; }}
  .showcase-title {{ margin:0; }}
  .showcase-copy {{ margin:0;color:var(--dashboard-muted-text);max-width:880px; }}
  .showcase-grid {{ display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:16px; }}
  .surface-card {{
    background: var(--dashboard-panel);
    border: 1px solid var(--dashboard-grid);
    border-radius: 12px;
    padding: 12px;
    display: flex;
    flex-direction: column;
    gap: 6px;
    box-shadow: 0 10px 30px rgba(15, 23, 42, 0.04);
  }}
  .surface-card h3 {{ margin: 0; }}
  .muted {{ color: var(--dashboard-muted-text); margin: 0; }}
  .theme-only {{ display: none; }}
  [data-theme="light"] .theme-light,
  [data-theme="dark"] .theme-dark {{ display: block; }}
  {css_text}
  </style>
</head>
<body data-theme="{DEFAULT_THEME_KEY}">
  {hero}
  {showcase}
  <script>
    (() => {{
      const storageKey = "dashboard-preview-theme";
      const root = document.body;
      const buttons = Array.from(document.querySelectorAll(".theme-button"));

      const applyTheme = (mode) => {{
        root.setAttribute("data-theme", mode);
        buttons.forEach((button) => {{
          button.classList.toggle("is-active", button.dataset.themeChoice.toLowerCase() === mode);
        }});
      }};

      const stored = window.localStorage.getItem(storageKey);
      const initial = stored === "light" || stored === "dark"
        ? stored
        : (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

      applyTheme(initial);

      buttons.forEach((button) => {{
        button.addEventListener("click", () => {{
          const selected = button.dataset.themeChoice.toLowerCase();
          window.localStorage.setItem(storageKey, selected);
          applyTheme(selected);
        }});
      }});
    }})();
  </script>
</body>
</html>
"""

    (output_dir / "index.html").write_text(html, encoding="utf-8")


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("build/site")
    build_preview(target)

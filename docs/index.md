---
layout: default
title: python-stocks
---
<link rel="stylesheet" href="./assets/landing.css">

<div class="landing" data-theme="light">
<section class="landing-hero">
  <div class="hero-text">
    <div class="eyebrow">Analysis-first workbench · Decision support</div>
    <h1>python-stocks dashboard</h1>
    <p class="lede">
      Confirm signals, stress-test scenarios, and check entry/exit discipline in one flow.
      Use the same controls and charts published in CI previews to make faster, evidence-backed decisions.
    </p>
    <div class="cta-row">
      <a class="cta primary" href="./dashboard/">Confirm signal in dashboard preview</a>
      <a class="cta secondary" href="./dashboards.md">Open the dashboard workflow map</a>
      <a class="cta secondary" href="./methodology.md">Review methodology assumptions</a>
    </div>
    <div class="landing-theme-row">
      <div class="landing-theme-switch" role="group" aria-label="Theme selector">
        <span class="label">Theme</span>
        <button type="button" data-theme-choice="Light">Light</button>
        <button type="button" data-theme-choice="Dark">Dark</button>
      </div>
    </div>
    <div class="stat-grid">
      <div class="stat"><div class="label">Workflow steps</div><div class="value">3 decision phases</div></div>
      <div class="stat"><div class="label">CI refreshed</div><div class="value">On every push</div></div>
      <div class="stat"><div class="label">Sample horizon</div><div class="value">2017–2018</div></div>
    </div>
  </div>
  <div class="landing-panel">
    <h2>Decision workflow entry points</h2>
    <div class="landing-card-grid" style="margin-top: 10px;">
      <div class="landing-card">
        <div class="chip">Workflow 1</div>
        <h3>1. Signal confirmation</h3>
        <p>Start with trend context and benchmark behavior before adjusting assumptions.</p>
        <p><a href="./dashboard/#strategy-tab">Confirm signal</a></p>
      </div>
      <div class="landing-card">
        <div class="chip">Workflow 2</div>
        <h3>2. Scenario stress-test</h3>
        <p>Use scenario presets and timeline horizon controls to pressure-test robustness.</p>
        <p class="landing-subtle"><a href="./dashboard/#comparison-tab">Run stress test</a></p>
      </div>
      <div class="landing-card">
        <div class="chip">Workflow 3</div>
        <h3>3. Entry/exit discipline check</h3>
        <p>Model cost drag and verify outcomes stay acceptable before scaling.</p>
        <p class="landing-subtle"><a href="./dashboard/#cost-tab">Run discipline check</a></p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="landing-section-header">
    <h2>Operational references</h2>
    <span>Map UI locations to decisions</span>
  </div>
  <div class="landing-columns">
    <div class="landing-panel">
      <p>Use the workflow map to match each decision to the right controls and charts:</p>
      <ul>
        <li>Hero controls: <code>Quick ticker</code>, <code>Preset windows</code></li>
        <li>Scenario panel: <code>Stress-test a scenario</code>, <code>Scenario controls</code></li>
        <li>Tabs: <code>Overview</code>, <code>Strategy Lab</code>, <code>Cost/Impact Analysis</code>, <code>Comparisons</code>, <code>Time in Market</code>, <code>Data Diagnostics</code></li>
      </ul>
      <p class="landing-subtle"><a href="./dashboards.md">Open dashboard workflow map</a></p>
    </div>
    <div class="landing-card-grid">
      <div class="landing-card">
        <h3>Strategy catalog</h3>
        <p>Reference strategy behavior, inputs, and parameter surfaces.</p>
        <p class="landing-subtle"><a href="./strategies.md">Strategy catalog</a></p>
      </div>
      <div class="landing-card">
        <h3>Tutorial reproductions</h3>
        <p>Notebook-style walkthroughs for reproducing visual outputs offline.</p>
        <p class="landing-subtle"><a href="./tutorials.md">Tutorials</a></p>
      </div>
      <div class="landing-card">
        <h3>Methodology</h3>
        <p>Metric definitions, slippage assumptions, and backtest limitations.</p>
        <p class="landing-subtle"><a href="./methodology.md">Methodology reference</a></p>
      </div>
      <div class="landing-card">
        <h3>About + disclaimer</h3>
        <p>Primary location for legal/disclaimer text and project intent.</p>
        <p class="landing-subtle"><a href="./about.md">About page</a></p>
      </div>
      <div class="landing-card">
        <h3>Quickstart commands</h3>
        <ul class="landing-inline-list">
          <li><code>pip install -e .</code></li>
          <li><code>PYTHONPATH=. python -m python_stocks.dashboard.app</code></li>
          <li><code>make artifacts</code></li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="landing-section-header">
    <h2>Publish automatically</h2>
    <span>GitHub Pages + PR previews</span>
  </div>
  <div class="landing-columns">
    <div class="landing-panel">
      <p>Every push triggers the Pages workflow to rebuild, upload, and deploy the SPY/DIA sample.</p>
      <ul>
        <li>Push to <code>main</code> to refresh the live site.</li>
        <li>Open a pull request to get a Draft Preview link and comment.</li>
        <li>Artifacts stay in lockstep with the dashboard for predictable decision reviews.</li>
      </ul>
      <div class="landing-badges">
        <span class="landing-badge">Artifacts: Plotly + PNG</span>
        <span class="landing-badge">CI: publish-docs</span>
        <span class="landing-badge">Pages folder: <code>/docs</code></span>
      </div>
    </div>
    <div class="landing-panel">
      <h3>Run locally</h3>
      <ol>
        <li>Install: <code>pip install -e .</code></li>
        <li>Launch app: <code>PYTHONPATH=. python -m python_stocks.dashboard.app</code></li>
        <li>Regenerate artifacts: <code>make artifacts</code></li>
      </ol>
      <p class="landing-subtle">Time-in-market output remains available as supporting evidence in the <code>Time in Market</code> tab.</p>
    </div>
  </div>
</section>
</div>

<script>
(() => {
  const landing = document.querySelector(".landing");
  if (!landing) {
    return;
  }

  const storageKey = "landing-theme";
  const buttons = Array.from(landing.querySelectorAll("[data-theme-choice]"));
  const applyTheme = (mode) => {
    landing.setAttribute("data-theme", mode);
    buttons.forEach((button) => {
      button.classList.toggle("is-active", button.dataset.themeChoice.toLowerCase() === mode);
    });
  };

  const stored = window.localStorage.getItem(storageKey);
  const initialTheme = stored === "light" || stored === "dark"
    ? stored
    : (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");

  applyTheme(initialTheme);

  buttons.forEach((button) => {
    button.addEventListener("click", () => {
      const selectedTheme = button.dataset.themeChoice.toLowerCase();
      window.localStorage.setItem(storageKey, selectedTheme);
      applyTheme(selectedTheme);
    });
  });
})();
</script>

<link rel="stylesheet" href="./assets/landing.css">

<div class="landing">
<section class="landing-hero">
  <div class="hero-text">
    <div class="eyebrow">Guided dashboards · Live simulations</div>
    <h1>python-stocks dashboards</h1>
    <p class="lede">
      Explore equity strategies with cost-aware charts, comparison matrices, and tutorial-style walkthroughs.
      Every preview is rebuilt automatically so visitors can explore without installing anything.
    </p>
    <div class="cta-row">
      <a class="cta primary" href="./assets/spy_interactive.html">View SPY preview</a>
      <a class="cta secondary" href="./dashboards.md">Tour the dashboard</a>
    </div>
    <div class="stat-grid">
      <div class="stat"><div class="label">CI refreshed</div><div class="value">On every push</div></div>
      <div class="stat"><div class="label">Sample horizon</div><div class="value">2017–2018</div></div>
      <div class="stat"><div class="label">Strategies</div><div class="value">Buy & hold + MA filter</div></div>
    </div>
  </div>
  <div class="landing-panel">
    <h2>Preview assets</h2>
    <div class="landing-card-grid" style="margin-top: 10px;">
      <div class="landing-card">
        <div class="chip">Snapshots</div>
        <h3>Static plots</h3>
        <p>PNG charts exported from the SPY/DIA simulation.</p>
        <p class="landing-subtle"><a href="./assets/figure_1.png">figure_1.png</a> · <a href="./assets/figure_2.png">figure_2.png</a> · <a href="./assets/figure_3.png">figure_3.png</a></p>
      </div>
      <div class="landing-card">
        <div class="chip">Interactive</div>
        <h3>Price + signals</h3>
        <p>Hoverable HTML views published alongside the static charts.</p>
        <p class="landing-subtle"><a href="./assets/spy_interactive.html">SPY</a> · <a href="./assets/dia_interactive.html">DIA</a></p>
      </div>
      <div class="landing-card">
        <div class="chip">Summaries</div>
        <h3>CSV + JSON</h3>
        <p>Strategy-level aggregates ready for notebooks or spreadsheets.</p>
        <p class="landing-subtle"><a href="./strategy_summary.csv">strategy_summary.csv</a> · <a href="./strategy_summary.json">strategy_summary.json</a></p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="landing-section-header">
    <h2>What ships with the site</h2>
    <span>Built from the SPY + DIA starter run</span>
  </div>
  <div class="landing-columns">
    <div class="landing-panel">
      <p>The pages are generated from:</p>
      <div class="landing-code-block">
        python -m python_stocks run --tickers SPY DIA --start 2017-01-01 --end 2018-01-01 \
        --initial 50000 --monthly 500 --strategies buy_and_hold moving_average_filter \
        --report-dir docs --no-show
      </div>
      <p class="landing-subtle">The CI workflow mirrors this exact command to keep previews current.</p>
    </div>
    <div class="landing-card-grid">
      <div class="landing-card">
        <h3>Strategy lab guidance</h3>
        <p>Walkthroughs explain how to read each tab and what inputs drive the visuals.</p>
        <p class="landing-subtle"><a href="./dashboards.md">Dashboard tour</a></p>
      </div>
      <div class="landing-card">
        <h3>Catalog + tutorials</h3>
        <p>Strategy definitions, parameter hints, and notebook-style recreations.</p>
        <ul class="landing-inline-list">
          <li><a href="./strategies.md">Strategy catalog</a></li>
          <li><a href="./tutorials.md">Tutorials</a></li>
        </ul>
      </div>
      <div class="landing-card">
        <h3>Preset scripts</h3>
        <p>Ready-to-run configs for momentum, moving-average sweeps, and buy-and-hold baselines.</p>
        <ul class="landing-inline-list">
          <li><code>./configs/buy_and_hold.sh</code></li>
          <li><code>./configs/ma_crossover.sh</code></li>
          <li><code>./configs/momentum.sh</code></li>
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
        <li>Artifacts stay in lockstep with the Dash app for predictable demos.</li>
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
      <p class="landing-subtle">Artifacts match the CI preview so you can verify changes before publishing.</p>
    </div>
  </div>
</section>
</div>

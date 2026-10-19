# Strategy Lab

Strategy Lab is the interactive website served at both the GitHub Pages root and
`/dashboard/`. It runs entirely in the browser; no Python server or account is
required. The existing Dash application remains available as a legacy local tool.

## Run and build

Requirements: Node.js 22+ and Python 3.11+. The web data exporter uses only Python's
standard library; the legacy Python tools require `pip install -e .`.

```sh
npm ci --prefix web
make web-dev
```

Open the local URL printed by Vite. For a production build:

```sh
make web-test
make web-build
cd web
npx playwright install chromium
npm run test:browser
```

`make web-build` exports validated historical data, type-checks and builds the
React app, and writes self-contained copies at `build/site/` and
`build/site/dashboard/`. Serve that directory with `python -m http.server 8080
--directory build/site` to test the GitHub Pages output. Relative asset paths also
support project Pages URLs such as `/python-stocks/dashboard/`.

## Research workflow

1. Start with the loaded SPY example, or choose SPY, DIA, NDAQ, or TQQQ.
2. Set a historical interval, fast/slow moving-average windows, initial capital,
   and transaction costs. Window lengths are trading sessions.
3. Choose **Run analysis**. Edited inputs are marked as pending until the run
   completes. Fetch or validation failures preserve the previous result.
4. Inspect Performance, Risk, and Trades. Selecting a chart trade marker opens
   the corresponding table entry. Arrow keys navigate the result tabs.
5. Save named runs in this browser. Saved analyses can be restored or compared
   side by side (up to three). Dates, capital, and costs remain visible when
   comparing unlike assumptions. Up to twelve runs can be kept.
6. Export the displayed result as JSON, including configuration, provenance,
   assumptions, full equity series, and individual trades.

Valid draft settings and runs use versioned local storage; incomplete number edits
do not overwrite the last valid configuration. Requests time out after 15 seconds
and offer a retry. On mobile, use **Edit settings** to reveal configuration. If storage is blocked,
corrupt, or full, the app warns and continues in memory. Export is the portable
backup. Clearing browser storage removes locally saved runs.

## Data and calculations

The dataset is a bundled historical snapshot ending **July 2, 2019**. There is
no browser fetch to a market-data provider and no claim of current pricing.
The source CSVs include adjusted closes, used to account for their split and
distribution adjustments. NDAQ is Nasdaq, Inc. stock; TQQQ is a leveraged ETF.

`python scripts/export_web_data.py` validates dates, ordering, positive finite
adjusted closes, and nonempty histories before writing static JSON. Generated
files are ignored by Git and regenerated for every production build.

The browser engine is a separate, explicitly defined moving-average crossover;
it does not claim parity with the legacy Python strategy named
`moving_average_filter`, which also uses slope checks. Fast and slow averages
use only prior sessions. The strategy enters/exits at the next adjusted close,
with fractional shares and costs on actual traded notional. The starting session
establishes the strategy's cash baseline and enters the buy-and-hold benchmark.
Strategy orders begin on session two. Full warmup history before the selected
period is required. Cash earns zero interest, and open positions are marked to
the final close without a forced liquidation fee.

Both portfolios start with identical capital. Benchmark entry costs are included.
Returns derive from compounded wealth. Drawdowns include initial capital as the
first peak. Exposure measures intervals held in market. Strategy volatility uses
sample daily return deviation times the square root of 252. Taxes, additional
slippage, and execution microstructure are excluded; adjusted-close executions
are a simplified model, not a tradable price guarantee.

## Verification and publishing

`web/src/engine.test.ts` contains hand-calculated financial fixtures. Playwright
covers desktop/mobile interactions, validation, linked trade markers, keyboard
navigation, saving/restoring/comparing, downloads, blocked storage, incomplete
input persistence, request timeouts, and failed fetch recovery. Automated WCAG
checks cover the workspace and save dialog. Production JS and fonts are bundled locally.

Pull requests run Python regression/artifact checks and the web calculation,
production build, and browser checks. Pushes to `main` build and verify the same
web app, then deploy it using the official GitHub Pages artifact workflow. There
is no separate static imitation, Jekyll build, or `gh-pages` branch requirement.

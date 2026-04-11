---
layout: default
title: Dashboard workflow map
---
# Dashboard workflow map

Use the dashboard as an analysis-first decision workbench: confirm signal quality, stress-test assumptions, then run execution discipline checks.

## Workflow 1 — Signal confirmation
- **When to use:** You want to decide whether a signal is strong enough to act on before changing costs or assumptions.
- **Decision it supports:** “Do I have enough trend and benchmark evidence to proceed?”
- **UI locations:**
  - Workflow section: `1. Signal confirmation`
  - Hero controls: `Quick ticker`, `Preset windows`
  - Section controls: `Ticker`, `Lookback window (days)`
  - Charts/cards: `Market replay`, `Signals vs. benchmark`
  - Related tabs/charts: `Overview` (`Price Overview`, `Strategy Lab`) and `Strategy Lab` tab (`Strategy Comparison`, `Execution Context`)

## Workflow 2 — Scenario stress-test
- **When to use:** You need to evaluate how robust a rule remains under different preset assumptions and horizons.
- **Decision it supports:** “Does this still hold up across scenarios and market regimes?”
- **UI locations:**
  - Workflow section: `2. Scenario stress-test`
  - Scenario panel: `Stress-test a scenario`, `Scenario controls`, `Load stress-test preset`, `Recompute stress test`
  - Section controls: `Timeline horizon`
  - Charts/cards: `Comparison matrix`, `Timeline overlays`
  - Related tab/charts: `Comparisons` tab (`Strategy matrix`, `Timeline overlay`)

## Workflow 3 — Entry/exit discipline check
- **When to use:** You are close to execution and need to test cost sensitivity before scaling or increasing turnover.
- **Decision it supports:** “Are expected outcomes still acceptable after realistic drag?”
- **UI locations:**
  - Workflow section: `3. Entry/exit discipline check`
  - Hero CTA: `Run discipline check`
  - Section controls: `Cost drag (bps)`
  - Charts/cards: `Execution costs`
  - Related tab/charts: `Cost/Impact Analysis` tab (`Cost Impact Curve`, `Slippage trend`)

## Supporting evidence: participation discipline
- **When to use:** You need a secondary check on participation risk after primary signal/stress/cost decisions are made.
- **Decision it supports:** “Am I sacrificing too much market participation?”
- **UI location:** `Time in Market` tab (`Time in Market Exposure`, `Participation diagnostics`)

## Data quality gate
- **When to use:** You suspect outliers or source irregularities may distort conclusions.
- **Decision it supports:** “Are these insights trustworthy enough to base decisions on?”
- **UI location:** `Data Diagnostics` tab (`Data Diagnostics` histogram)

## Preview without running a server
- Run `make artifacts` to create the Plotly HTML/PNG exports under `artifacts/plotly/`.
- Open `artifacts/plotly/price_trend.html` or `.../comparison_matrix.html` locally for a fast preview of the Dash visuals used in CI Draft Preview deployments.

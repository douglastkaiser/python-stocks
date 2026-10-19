# Ad Hoc Release Process (Solo Maintainer)

A lightweight checklist for shipping safely without a formal release train.

## Web workspace release checks

Run `npm ci --prefix web`, `make web-test`, and `make web-build`. Install Chromium
with `cd web && npx playwright install chromium`, then run `make web-browser`
from the repository root. Verify the built root and `/dashboard/` paths using a
static server, including a project subpath. Check saved comparisons, exports,
mobile layout, and failed-data retries. Pushes to main deploy this interactive
build after calculation and browser checks. See [workspace.md](./workspace.md).

The checklist below applies to the legacy local Dash app.

## 1) Pre-release manual UX checks

Before you ship, run the app locally and sanity-check the core user flow:

1. Start app:
   ```bash
   PYTHONPATH=. python -m python_stocks.dashboard.app
   ```
2. Verify the three workflow paths:
   - **Signal confirmation** (strategy tab and benchmark context)
   - **Scenario stress-test** (comparison tab and scenario controls)
   - **Entry/exit discipline check** (cost/impact tab)
3. Validate global controls and metadata:
   - Quick ticker + preset windows update charts
   - Source / market date / refresh timestamp render correctly
   - No obvious layout overlap, blank charts, or console errors

If any critical chart fails to render or key controls do not respond, stop and fix before release.

## 2) Data freshness verification

Use a fast freshness check right before shipping:

1. Refresh local daily data cache:
   ```bash
   make ingest-daily
   ```
2. Confirm latest market date is current for the last completed session (or expected for weekends/holidays).
3. In app metadata, confirm:
   - `Market date` is recent and plausible
   - `Last refresh` matches your latest ingest window
4. If provider data is delayed, note it in release notes and proceed only if fallback cache is healthy.

## 3) Basic smoke verification commands

Run the minimum command set from repo root:

```bash
make dash-smoke
make test
make artifacts
```

Optional but recommended if you changed packaging/tooling/checking behavior:

```bash
make lint
```

## 4) Post-release sanity check steps

Immediately after release/deploy:

1. Open the published site (or preview URL) in a clean browser session.
2. Confirm landing page loads and the dashboard route opens.
3. Spot-check one ticker path end-to-end (controls -> charts -> diagnostics).
4. Verify latest artifact outputs are present (Plotly + simulation files where expected).
5. Check CI/deploy workflow status and logs for warnings.
6. Add a short release note in your tracker (what changed, timestamp, known caveats).

## 5) Incident note template (solo maintenance)

Use this template when anything breaks during or after release:

```text
Incident title:
Date/time detected (UTC):
Detected by:

User impact:
Scope (who/what is affected):
Severity (low/medium/high):

Symptoms:
Probable trigger/change:

Immediate mitigation:
Status (monitoring/resolved):

Root cause (if known):
Follow-up fixes:
Owner:
Target date:

Validation after fix:
Communication/log note link:
```

Keep the note short. The goal is fast recovery and a searchable record for future you.

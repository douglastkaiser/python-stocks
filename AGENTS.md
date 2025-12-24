# Agent Helper

- Preserve tab indentation for Makefile recipes; commands must start with a literal tab, not spaces.
- After modifying automation scripts or CI-related files, run applicable Make targets locally when possible.
- Keep README and CI docs consistent with available Make targets.
- MarketSample demo data must use a DatetimeIndex (no mixed integer/timestamp indices) so Plotly snapshots and CI artifact builds remain stable; run `make artifacts` after touching dashboard sample data or figures.
- For dashboard previews, run `PYTHONPATH=. python scripts/build_dashboard_preview.py build/site` to verify the static page builds before pushing.
- Always run `make lint` locally after layout or automation changes to catch formatting and import-order issues early.

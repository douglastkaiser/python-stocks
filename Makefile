.PHONY: lint test dash-smoke artifacts ingest-daily

lint:
	black --check .
	ruff check .
	mypy .
	pyright

test:
	PYTHONPATH=. PYTHON_STOCKS_TEST_MODE=1 pytest tests

dash-smoke:
	PYTHONPATH=. PYTHON_STOCKS_TEST_MODE=1 pytest tests/test_dashboard_smoke.py

artifacts:
	PYTHONPATH=. PYTHON_STOCKS_TEST_MODE=1 python scripts/generate_artifacts.py --output-dir artifacts


ingest-daily:
	PYTHONPATH=. python -m python_stocks ingest-daily

.PHONY: web-dev web-test web-build web-browser

web-dev:
	python scripts/export_web_data.py
	npm run dev --prefix web

web-test:
	npm test --prefix web

web-build:
	PYTHONPATH=. python scripts/build_dashboard_preview.py build/site

web-browser:
	npm run test:browser --prefix web

.PHONY: lint test dash-smoke artifacts

lint:
	python -m ruff check .

test:
	PYTHONPATH=. PYTHON_STOCKS_TEST_MODE=1 pytest tests

dash-smoke:
	PYTHONPATH=. PYTHON_STOCKS_TEST_MODE=1 pytest tests/test_dashboard_smoke.py

artifacts:
	PYTHONPATH=. PYTHON_STOCKS_TEST_MODE=1 python scripts/generate_artifacts.py --output-dir artifacts

.PHONY: lint test dash-smoke artifacts

lint:
python -m ruff check .

test:
PYTHON_STOCKS_TEST_MODE=1 pytest tests

dash-smoke:
PYTHON_STOCKS_TEST_MODE=1 pytest tests/test_dashboard_smoke.py

artifacts:
PYTHON_STOCKS_TEST_MODE=1 python scripts/generate_artifacts.py --output-dir artifacts

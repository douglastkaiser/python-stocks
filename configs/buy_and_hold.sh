#!/usr/bin/env bash
set -euo pipefail

PYTHONWARNINGS=${PYTHONWARNINGS:-ignore} PYTHONPATH=${PYTHONPATH:-.} python -m python_stocks run \
  --tickers SPY DIA \
  --start 2017-01-01 --end 2018-01-01 \
  --initial 50000 --monthly 500 \
  --strategies buy_and_hold \
  --report-dir docs --no-show

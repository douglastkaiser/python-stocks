#!/usr/bin/env bash
set -euo pipefail

PYTHONWARNINGS=${PYTHONWARNINGS:-ignore} PYTHONPATH=${PYTHONPATH:-.} python -m python_stocks run \
  --tickers SPY \
  --start 2017-01-01 --end 2018-01-01 \
  --initial 40000 --monthly 400 \
  --strategies moving_average_filter \
  --param moving_average_filter.short_window=10,20 \
  --param moving_average_filter.long_window=100,200 \
  --report-dir docs --no-show

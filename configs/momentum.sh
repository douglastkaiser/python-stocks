#!/usr/bin/env bash
set -euo pipefail

PYTHONWARNINGS=${PYTHONWARNINGS:-ignore} PYTHONPATH=${PYTHONPATH:-.} python -m python_stocks run \
  --tickers TQQQ \
  --start 2017-01-01 --end 2018-01-01 \
  --initial 25000 --monthly 250 \
  --strategies moving_average_filter \
  --param moving_average_filter.short_window=20 \
  --param moving_average_filter.long_window=100 \
  --report-dir docs --no-show

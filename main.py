
import csv
from run_strategies import *
import matplotlib.pyplot as plt
from StockData import StockData
import time
from data_loading import *

## For plotting
# python -m pip install -U matplotlib
plt.close('all')

t0 = time.time()

initial_deposit = 10000
daily_deposit = 0  # 900/30
monthly_deposit = 100  # Adds at first of the month

# https://finance.yahoo.com/quote/TQQQ/history?p=TQQQ&.tsrc=fin-srch
tickers_to_run = []
tickers_to_run.append('SPY')
tickers_to_run.append('DIA')
# tickers_to_run.append('NDAQ')
# tickers_to_run.append('TQQQ')
stock_history_data = StockData(tickers_to_run)
# Cut down on timing.
stock_history_data.limit_timeframe('2010-01-01', '2016-01-11')
stock_history_data.add_external_investments(monthly_deposit, daily_deposit)

####### Run Strats #######
run_some_strategies(initial_deposit, stock_history_data)

stock_history_data.plot()

t1 = time.time()
Time = t1-t0
print("\nTime: " + "%.2f" % Time + " seconds")

plt.show()



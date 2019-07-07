
import csv
from run_strategies import *
import matplotlib.pyplot as plt
from StockData import StockData
import time
from data_loading import *
from math_helper import *

##### For plotting
# python -m pip install -U matplotlib
plt.close('all')

start_time = time.time()

initial_deposit = 10000
daily_deposit = 10
monthly_deposit = 100  # Adds at first of the month

##### https://finance.yahoo.com/quote/TQQQ/history?p=TQQQ&.tsrc=fin-srch
tickers_to_run = []
tickers_to_run.append('SPY')
tickers_to_run.append('DIA')
# tickers_to_run.append('NDAQ')
# tickers_to_run.append('TQQQ')
stock_history_data = StockData(tickers_to_run)
##### Cut down on timing.
# stock_history_data.limit_timeframe('2010-08-25', '2018-09-05')
stock_history_data.add_external_investments(monthly_deposit, daily_deposit)

####### Run Strats #######
run_some_strategies(initial_deposit, stock_history_data)

stock_history_data.plot()

##### Timing
end_time = time.time()
print_time(end_time - start_time)

##### Display all plots.
plt.show()


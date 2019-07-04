
import csv
from run_strategies import *
import matplotlib.pyplot as plt
from HistoricData import HistoricData
import sys
import time
from data_loading import *

## For plotting
# python -m pip install -U matplotlib
plt.close('all')

t0 = time.time()

initial_deposit = 10000
daily_investment = 0  # 900/30

# https://finance.yahoo.com/quote/TQQQ/history?p=TQQQ&.tsrc=fin-srch
historic_data = []
historic_data.append(load_into_historic_data_set('SPY', 'SPY'))
historic_data.append(load_into_historic_data_set('DIA', 'DIA'))
historic_data.append(load_into_historic_data_set('NDAQ', 'NDAQ'))
historic_data.append(load_into_historic_data_set('TQQQ', 'TQQQ'))


####### Run Strats #######
run_some_strategies(initial_deposit, daily_investment, historic_data)

historic_data.plot()

t1 = time.time()
Time = t1-t0
print("\nTime: " + "%.2f" % Time + " seconds")

plt.show()




import csv
from run_strategies import *
import matplotlib.pyplot as plt
from HistoricData import HistoricData
import sys
import time

## For plotting
# python -m pip install -U matplotlib
plt.close('all')

t0 = time.time()

initial_deposit = 10000
daily_investment = 0  # 900/30

# https://www.nasdaq.com/quotes/historical-quotes.aspx
if sys.platform == 'Windows':
    print('For King and Country, get a Mac Doug')
    data_location = 'raw_data\HistoricalQuotes_SPY.csv'  # https://www.nasdaq.com/symbol/spy/historical
else:
    data_location = 'raw_data/HistoricalQuotes_SPY.csv'

# Load up daily closing prices
with open(data_location) as csvfile:
    reader = csv.DictReader(csvfile)
    # Load in data to usable arrays.
    dates = []
    closing_prices = []
    opening_prices = []
    high_prices = []
    low_prices = []

    for row in reader:
        date_today = (row["date"])
        dates.append(date_today)
        close_price = float(row["close"])
        closing_prices.append(close_price)
        opening = float(row["open"])
        opening_prices.append(opening)
        high = float(row["high"])
        high_prices.append(high)
        low = float(row["low"])
        low_prices.append(low)
    # Reverse order of arrays to be chronological.
    dates = list(reversed(dates))
    closing_prices = list(reversed(closing_prices))
    opening_prices = list(reversed(opening_prices))
    high_prices = list(reversed(high_prices))
    low_prices = list(reversed(low_prices))

    # range_this_time = 250
    range_this_time = len(dates)

    dates = dates[0:range_this_time]
    closing_prices = closing_prices[0:range_this_time]
    opening_prices = opening_prices[0:range_this_time]
    high_prices = high_prices[0:range_this_time]
    low_prices = low_prices[0:range_this_time]

historic_data = HistoricData(dates, closing_prices, opening_prices, high_prices, low_prices)

####### Run Strats #######
run_some_strategies(initial_deposit, daily_investment, historic_data)

historic_data.plot()

t1 = time.time()
Time = t1-t0
print("\nTime: " + "%.2f" % Time + " seconds")

plt.show()


import csv
from run_strategies import *
import matplotlib.pyplot as plt

## For plotting
# python -m pip install -U matplotlib
plt.close('all')

initial_deposit = 10000
daily_investment = 10

# https://www.nasdaq.com/quotes/historical-quotes.aspx
data_location = 'raw_data\HistoricalQuotes_SPY.csv'  # https://www.nasdaq.com/symbol/spy/historical
# Load up daily closing prices
with open(data_location) as csvfile:
    reader = csv.DictReader(csvfile)
    # Load in data to usable arrays.
    close_prices = [];
    dates = [];
    for row in reader:
        close_price = float(row["close"])
        close_prices.append(close_price)
        #date = float(row["date"])
        #dates.append(date)
    # Reverse order of arrays to be chronological.
    close_prices = list(reversed(close_prices))



####### Run Strats #######
run_some_strategies(initial_deposit, daily_investment, close_prices)




plt.show()

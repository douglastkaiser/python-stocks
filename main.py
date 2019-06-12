
import csv
import numpy
from strategies import *
from TradingDay import TradingDay

init_deposit = 1000
daily_deposit = 1
# Before first purchase
bank_account = init_deposit
shares_owned = 0

# https://www.nasdaq.com/quotes/historical-quotes.aspx
data_location = 'raw_data\HistoricalQuotes_SPY.csv'  # https://www.nasdaq.com/symbol/spy/historical

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

    print("Initial Deposit: " + str(init_deposit))
    print("Daily Deposit: " + str(daily_deposit))

    print("\n -- Strat = Zero Investments --")
    protfolio_value = init_deposit + daily_deposit*len(close_prices)
    print("Shares Owned in end: " + str(0))
    print("Bank Account left over: " + str(protfolio_value))
    print("Total Value: " + str(protfolio_value))

    # Strat 1 - ASAP
    for close_price in close_prices:
        # Buy as much as possible.
        bank_account = bank_account + daily_deposit
        shares_to_buy = int(bank_account/close_price)
        bank_account = bank_account - shares_to_buy*close_price
        shares_owned = shares_owned + shares_to_buy

    print("\n -- Strat = Buy All Asap --")
    print("Shares Owned in end: " + str(shares_owned))
    print("Bank Account left over: " + str(bank_account))
    protfolio_value = shares_owned*close_prices[-1] + bank_account
    print("Total Value: " + str(protfolio_value))

    # Reset variables
    bank_account = init_deposit
    shares_owned = 0
    # Strat 2 - Sinusoid attempt
    prev_close_price_1 = close_prices[0]
    prev_close_price_2 = close_prices[0]
    prev_close_price_3 = close_prices[0]
    for close_price in close_prices:
        bank_account = bank_account + daily_deposit
        if (prev_close_price_1 < close_price) and (prev_close_price_1 < prev_close_price_2) and (prev_close_price_2 < prev_close_price_3):
            # Buy as much as possible.
            shares_to_buy = int(bank_account/close_price)
            bank_account = bank_account - shares_to_buy*close_price
            shares_owned = shares_owned + shares_to_buy
        elif (prev_close_price_1 > close_price) and (prev_close_price_1 > prev_close_price_2) and (prev_close_price_2 > prev_close_price_3):
            # Sell 1 share.
            if shares_owned > 0:
                bank_account = bank_account + 1*close_price
                shares_owned = shares_owned - 1
        prev_close_price_3 = prev_close_price_2
        prev_close_price_2 = prev_close_price_1
        prev_close_price_1 = close_price

    print("\n -- Strat = Sinusoid attempt --")
    print("Shares Owned in end: " + str(shares_owned))
    print("Bank Account left over: " + str(bank_account))
    protfolio_value = shares_owned*close_prices[-1] + bank_account
    print("Total Value: " + str(protfolio_value))

    # Reset variables
    bank_account = init_deposit
    shares_owned = 0
    # Strat 3 - MAF
    maf_n = 100
    maf = [close_prices[0]]*maf_n

    for close_price in close_prices:
        bank_account = bank_account + daily_deposit

        maf.append(close_price)
        maf.remove(maf[0])
        maf_average = sum(maf) / maf_n

        if (close_price < maf_average):
            # Buy as much as possible.
            shares_to_buy = int(bank_account/close_price)
            bank_account = bank_account - shares_to_buy*close_price
            shares_owned = shares_owned + shares_to_buy
        # elif (close_price > maf_average):
        #     # Sell 1 share.
        #     if shares_owned > 0:
        #         bank_account = bank_account + 1*close_price
        #         shares_owned = shares_owned - 1

    print("\n -- Strat = MAF --")
    print("Shares Owned in end: " + str(shares_owned))
    print("Bank Account left over: " + str(bank_account))
    protfolio_value = shares_owned*close_prices[-1] + bank_account
    print("Total Value: " + str(protfolio_value))
    

print(strategy_no_investment())
td = TradingDay(100, 10, [10, 20, 30])
print(td.price_history)
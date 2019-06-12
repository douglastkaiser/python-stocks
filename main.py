
import csv

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

    # Initial deposit - buy all you can
    for close_price in close_prices:
        bank_account = bank_account + daily_deposit
        shares_to_buy = int(bank_account/close_price)
        bank_account = bank_account - shares_to_buy*close_price
        shares_owned = shares_owned + shares_to_buy

    print("Initial Deposit: " + str(init_deposit))
    print("Daily Deposit: " + str(daily_deposit))

    print("\n -- Strat = Zero Investments --")
    protfolio_value = init_deposit + daily_deposit*len(close_prices)
    print("Shares Owned in end: " + str(0))
    print("Bank Account left over: " + str(protfolio_value))
    print("Total Value: " + str(protfolio_value))


    print("\n -- Strat = Buy All Asap --")
    print("Shares Owned in end: " + str(shares_owned))
    print("Bank Account left over: " + str(bank_account))
    protfolio_value = shares_owned*close_prices[-1] + bank_account
    print("Total Value: " + str(protfolio_value))
    

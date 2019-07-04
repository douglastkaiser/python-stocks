
import csv
from HistoricData import HistoricData
import pandas as pd

def load_into_historic_data_set(data_location, name):
    if sys.platform == 'Windows':
        data_location = "raw_data\\" + stock_data_name + ".csv"  # https://www.nasdaq.com/symbol/spy/historical
    else:
        data_location = "raw_data/" + stock_data_name + ".csv"

    df = pd.read_csv(data_location, parse_dates=["Dates"], index_col=["Dates"])

    return HistoricData(name, dates, closing_prices, opening_prices, high_prices, low_prices)

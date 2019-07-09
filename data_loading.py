
import csv
import sys
import pandas as pd

def load_into_stock_data_set(file_name):
    if sys.platform == 'Windows':
        data_location = "raw_data\\" + file_name + ".csv"
    else:
        data_location = "raw_data/" + file_name + ".csv"

    df = pd.read_csv(data_location, parse_dates=["Date"], index_col=["Date"])

    return df

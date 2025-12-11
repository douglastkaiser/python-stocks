
import csv
from pathlib import Path

import pandas as pd


def load_into_stock_data_set(file_name):
    data_dir = Path(__file__).resolve().parent / "raw_data"
    data_location = data_dir / f"{file_name}.csv"

    df = pd.read_csv(data_location, parse_dates=["Date"], index_col=["Date"], usecols=["Date", "Close", "Open"])

    return df

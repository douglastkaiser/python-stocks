
import matplotlib.pyplot as plt
import numpy as np
from math_helper import *
import pandas as pd
from data_loading import *

class StockData:

    def __init__(self, list_of_tickers, monthly_deposit=0, daily_deposit=0):
        data_frame_list=[]
        for ticker in list_of_tickers:
            data_frame_list.append(load_into_stock_data_set(ticker))
        df = pd.concat(data_frame_list, axis=1, keys=(list_of_tickers))
        # Reindex to fill missing days - non-trading days.
        inn = df.index
        idx = pd.date_range(inn[0], inn[-1])
        df = df.reindex(idx, fill_value=np.NaN)
        self.data_frame = df

        self.monthly_deposit = monthly_deposit
        self.daily_deposit = daily_deposit

    def get_stock_df_to_today_and_money_to_add(self, row_n):
        # Create stock history df up to this day.
        stock_df_to_today = self.data_frame.iloc[:row_n]
        # Calculate the investment schedule.
        money_to_add = self.daily_deposit
        if stock_df_to_today.index[-1].day == 1:
            money_to_add += self.monthly_deposit
        return stock_df_to_today, money_to_add

    def add_external_investments(self, monthly_deposit, daily_deposit):
        self.monthly_deposit = monthly_deposit
        self.daily_deposit = daily_deposit

    def total_days(self):
        return len(self.data_frame.index)

    def tickers(self):
        return list(self.data_frame.columns.levels[0])

    def limit_timeframe(self, start_date, end_date):
        self.data_frame = self.data_frame.loc[start_date:end_date]

    def plot(self):
        df = self.data_frame
        for ticker in self.tickers():
            fig = plt.figure()
            sub_df = df[ticker]['Close']  # [['Close', 'Open', 'High', 'Low']]
            sub_df = sub_df[~sub_df.isin([np.nan, np.inf, -np.inf])]
            sub_df.plot(kind='line', title=ticker+' Prices')

        # t = df['Date']
        # print(t)
        # plt.plot(t, self.closing_prices, label='Closing Prices')

        # mafshort = []
        # maflong = []
        # mafshort_slope = []
        # maflong_slope = []
        # mafshort_curv = []
        # for i in range(0, len(self.closing_prices)):
        #     data_for_use = self.closing_prices[0:i+1]
        #     mafshort.append(no_delay_moving_average_filter(data_for_use, 10))
        #     maflong.append(no_delay_moving_average_filter(data_for_use, 100))
            # mafshort_slope.append(no_delay_moving_average_filter(slope_vectorized(mafshort), 10))
            # mafshort_curv.append(no_delay_moving_average_filter(curvature_vectorized(mafshort), 10))
            # mafshort_slope.append(slope(mafshort, 2))
            # mafshort_curv.append(curvature(mafshort))

        # plt.plot(t, mafshort, label='Closing Prices - short day MAF')
        # plt.plot(t, maflong, label='Closing Prices - long day MAF')
        # plt.legend()
        # plt.title('SPY Prices')

        # fig = plt.figure()
        # plt.plot(t, mafshort_slope, label='Slope of Prices - short day MAF')
        # # plt.plot(t, maflong_slope, label='Slope of Prices - long day MAF')
        # plt.legend()
        # plt.title('SPY Prices - Slope')

        # fig = plt.figure()
        # plt.plot(t, mafshort_curv, label='Curv of Prices - short day MAF')
        # # plt.plot(t, maflong_curv, label='Curv of long day MAF')
        # plt.legend()
        # plt.title('SPY Prices - Curvature')


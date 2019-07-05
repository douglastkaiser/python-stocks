
import matplotlib.pyplot as plt
import numpy as np
from math_helper import *
import pandas as pd
from data_loading import *

class StockData:

    def __init__(self, list_of_tickers):
        data_frame_list=[]
        for ticker in list_of_tickers:
            data_frame_list.append(load_into_stock_data_set(ticker))
        self.data_frame = pd.concat(data_frame_list, axis=1, keys=(list_of_tickers))

    def total_days(self):
        return len(self.data_frame.index)

    def tickers(self):
        return self.data_frame.columns.levels[0]

    def plot(self):
        df = self.data_frame

        # sub_df = df['SPY'][['Close', 'High', 'Low', 'Open']]
        
        for ticker in self.tickers():
            fig = plt.figure()
            sub_df = df[ticker]['Close']
            sub_df.plot(kind='line', title=ticker)

        # 

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


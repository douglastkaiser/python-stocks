
import matplotlib.pyplot as plt
import numpy as np
from math_helper import *

class HistoricData:

    def __init__(self, dates, closing_prices, opening_prices, high_prices, low_prices):
        self.closing_prices = closing_prices
        self.dates = dates
        self.opening_prices = opening_prices
        self.high_prices = high_prices
        self.low_prices = low_prices

    # def maf_historic():

    def total_days(self):
        assert len(self.low_prices) == len(self.high_prices)
        assert len(self.low_prices) == len(self.opening_prices)
        assert len(self.low_prices) == len(self.dates)
        assert len(self.low_prices) == len(self.closing_prices)

        return len(self.low_prices)

    def plot(self):
        fig = plt.figure()
        t = np.linspace(1, len(self.closing_prices), len(self.closing_prices))
        plt.plot(t, self.closing_prices, label='Closing Prices')

        mafshort = no_delay_moving_average_filter_vectorized(self.closing_prices, 40)
        plt.plot(t, mafshort, label='Closing Prices - short day MAF')
        
        maflong = no_delay_moving_average_filter_vectorized(self.closing_prices, 200)
        plt.plot(t, maflong, label='Closing Prices - long day MAF')

        plt.legend()
        plt.title('SPY Prices')

        fig = plt.figure()
        mafshort_slope = slope_vectorized(mafshort, 2)
        maflong_slope = slope_vectorized(maflong, 2)
        plt.plot(t, mafshort_slope, label='Slope of Prices - short day MAF')
        plt.plot(t, maflong_slope, label='Slope of Prices - long day MAF')
        # mafshort_slope_mafshort = no_delay_moving_average_filter_vectorized(mafshort_slope, 10)
        # plt.plot(t, mafshort_slope_mafshort, label='10 MAF - Slope of 10 day MAF')
        plt.legend()
        plt.title('SPY Prices - derivative')

        # fig = plt.figure()
        # mafshort_curv = curvature_vectorized(mafshort, 2)
        # maflong_curv = curvature_vectorized(maflong, 2)
        # plt.plot(t, mafshort_curv, label='Curv of short day MAF')
        # plt.plot(t, maflong_curv, label='Curv of long day MAF')
        # # mafshort_curv_mafshort = no_delay_moving_average_filter_vectorized(mafshort_curv, 10)
        # # plt.plot(t, mafshort_curv_mafshort, label='10 MAF - Curv of 10 day MAF')
        # plt.legend()
        # plt.title('SPY Prices - double derivative')

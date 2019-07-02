
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

        mafshort = []
        maflong = []
        maflong_exp = []
        mafshort_slope = []
        # maflong_slope = []
        mafshort_curv = []
        for i in range(0, len(self.closing_prices)):
            data_for_use = self.closing_prices[0:i+1]
            mafshort.append(no_delay_moving_average_filter(data_for_use, 10))
            # maflong.append(no_delay_moving_average_filter(data_for_use, 100))
            maflong_exp.append(no_delay_moving_average_filter(data_for_use, 100))
            # mafshort_slope.append(no_delay_moving_average_filter(slope_vectorized(mafshort), 10))
            # mafshort_curv.append(no_delay_moving_average_filter(curvature_vectorized(mafshort), 10))
            mafshort_slope.append(slope(mafshort, 2))
            # mafshort_curv.append(curvature(mafshort))

        plt.plot(t, mafshort, label='Closing Prices - short day MAF')
        # plt.plot(t, maflong, label='Closing Prices - long day MAF')
        plt.plot(t, maflong_exp, label='Closing Prices - long day MAF')
        plt.legend()
        plt.title('SPY Prices')

        fig = plt.figure()
        plt.plot(t, mafshort_slope, label='Slope of Prices - short day MAF')
        # plt.plot(t, maflong_slope, label='Slope of Prices - long day MAF')
        plt.legend()
        plt.title('SPY Prices - Slope')

        # fig = plt.figure()
        # plt.plot(t, mafshort_curv, label='Curv of Prices - short day MAF')
        # # plt.plot(t, maflong_curv, label='Curv of long day MAF')
        # plt.legend()
        # plt.title('SPY Prices - Curvature')


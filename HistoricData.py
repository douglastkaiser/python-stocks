
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

        maf100_average = no_delay_moving_average_filter_vectorized(self.closing_prices, 20)
        plt.plot(t, maf100_average, label='Closing Prices - 20 day MAF')

        maf20_average = no_delay_moving_average_filter_vectorized(self.closing_prices, 100)
        plt.plot(t, maf20_average, label='Closing Prices - 100 day MAF')

        plt.legend()
        plt.title('SPY Prices')

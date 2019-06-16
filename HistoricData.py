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
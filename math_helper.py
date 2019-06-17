
def moving_average_filter(data, maf_n):
    latest_i = len(data)
    oldest_i = min([len(data)-maf_n, 0])
    data_in_window = data[oldest_i:latest_i]
    return sum(data_in_window)/len(data_in_window)

# def no_delay_maf(self, maf_n):

import numpy as np

def moving_average_filter_vectorized(data, maf_n):
    maf = []
    for i in range(0, len(data)):
        data_for_use = data[0:i+1]
        maf.append(moving_average_filter(data_for_use, maf_n))
    return maf

def moving_average_filter(data, maf_n):
    latest_i = len(data)
    oldest_i = max([latest_i-maf_n, 0])
    data_in_window = data[oldest_i:latest_i+1]
    if len(data_in_window) == 0:
        return 0
    return sum(data_in_window)/len(data_in_window)

def no_delay_moving_average_filter_vectorized(data, maf_n):
    maf_n_to_use = int(np.floor(maf_n/2))
    maf_once = moving_average_filter_vectorized(data, maf_n_to_use)
    maf_twice = list(reversed(moving_average_filter_vectorized(list(reversed(maf_once)), maf_n_to_use)))
    return maf_twice

def no_delay_moving_average_filter(data, maf_n):
    maf = no_delay_moving_average_filter_vectorized(data, maf_n)
    return maf[-1]

def percentage_difference(from_here, to_here):
    return 100*(to_here - from_here)/from_here

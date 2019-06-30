
import numpy as np


def moving_average_filter_vectorized(data, maf_n):
    assert type(maf_n) is int
    if not isinstance(data, list):
        data = [data]

    maf = []
    for i in range(0, len(data)):
        data_for_use = data[0:i+1]
        maf.append(moving_average_filter(data_for_use, maf_n))
    return maf


def moving_average_filter(data, maf_n):
    assert type(maf_n) is int
    if not isinstance(data, list):
        data = [data]

    maf_n = np.min([np.max([maf_n, 1]), len(data)])
    latest_i = len(data)
    oldest_i = max([latest_i-maf_n, 0])
    data_in_window = data[oldest_i:latest_i+1]
    if len(data_in_window) == 0:
        return 0
    return sum(data_in_window)/len(data_in_window)


def no_delay_moving_average_filter_vectorized(data, maf_n):
    assert type(maf_n) is int
    if not isinstance(data, list):
        data = [data]

    maf_n_to_use = int(np.floor(maf_n/2))
    maf_once = moving_average_filter_vectorized(data, maf_n_to_use)
    maf_twice = list(reversed(moving_average_filter_vectorized(list(reversed(maf_once)), maf_n_to_use)))
    return maf_twice


def no_delay_moving_average_filter(data, maf_n):
    assert type(maf_n) is int
    if not isinstance(data, list):
        data = [data]

    maf = no_delay_moving_average_filter_vectorized(data, maf_n)
    return maf[-1]


def percentage_difference(from_here, to_here):
    assert from_here != 0
    return 100*(to_here - from_here)/np.abs(from_here)


def slope(data):
    if not isinstance(data, list):
        data = [data]
    if (len(data) < 2):
        return 0

    return data[-1] - data[-2]


def curvature(data, n):
    assert type(n) is int
    if not isinstance(data, list):
        data = [data]
    if (len(data) < 3):
        return 0

    d_data = [slope([data[-3], data[-2]], n), slope([data[-2], data[-1]], n)]
    return slope(d_data, n)


def slope_vectorized(data, n):
    assert type(n) is int
    if not isinstance(data, list):
        data = [data]

    slope_vec = []
    for i in range(0, len(data)):
        data_for_use = data[0:i+1]
        slope_vec.append(slope(data_for_use, n))
    return slope_vec


def curvature_vectorized(data, n):
    assert type(n) is int
    if not isinstance(data, list):
        data = [data]

    curvature_vec = []
    for i in range(0, len(data)):
        data_for_use = data[0:i+1]
        curvature_vec.append(curvature(data_for_use, n))
    return curvature_vec

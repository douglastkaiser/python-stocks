
import numpy as np
from scipy.signal import butter, lfilter, freqz

def print_time(Time_sec):
    hours = int(Time_sec/3600)
    minutes = int(Time_sec/60)
    seconds = int(Time_sec)
    if hours >= 1:
        remaining_minutes = minutes-hours*60
        remaining_seconds = Time_sec-minutes*60
        hour_str = "%.0f" % hours + " hours, "
        min_str = "%.0f" % remaining_minutes + " minutes, and "
        sec_str = "%.2f" % remaining_seconds + " seconds"
        print("\nRuntime: " + hour_str + min_str + sec_str)
    elif minutes >= 1:
        remaining_seconds = Time_sec-minutes*60
        min_str = "%.0f" % minutes + " minutes and "
        sec_str = "%.2f" % remaining_seconds + " seconds"
        print("\nRuntime: " + min_str + sec_str)
    else:
        print("\nRuntime: " + "%.2f" % Time_sec + " seconds")


def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a


def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    if len(data) == 0:
        return 0
    if len(data) == 1:
        return data
    # data = [data[1], data[1], data[1], data[1], data[1], data]
    y = lfilter(b, a, data)
    # y = y[5:]
    return y


def no_delay_butter_low_pass_vectorized(data, cutoff, fs, order=5):
    bwf_once = butter_lowpass_filter(data, cutoff, fs)
    bwf_twice = list(reversed(butter_lowpass_filter(list(reversed(bwf_once)), cutoff, fs)))
    return bwf_twice


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

    data = data[-maf_n:]

    latest_i = len(data)
    oldest_i = max([latest_i-maf_n, 0])
    data_in_window = data[oldest_i:latest_i+1]
    maf = sum(data_in_window)/len(data_in_window)
    return maf


def no_delay_moving_average_filter_vectorized(data, maf_n):
    assert type(maf_n) is int
    if not isinstance(data, list):
        data = [data]
    maf_n_to_use = int(np.floor(maf_n/2))
    maf_once = moving_average_filter_vectorized(data, maf_n_to_use)
    maf_twice = list(reversed(moving_average_filter_vectorized(list(reversed(maf_once)), maf_n_to_use)))
    return maf_twice


def no_delay_moving_average_filter(data, maf_n):
    assert (type(maf_n) is int) or (type(maf_n) is np.int32)
    if not isinstance(data, list):
        data = [data]
    maf_n = int(np.min([np.max([maf_n, 1]), len(data)]))
    data = data[-maf_n:]
    maf = no_delay_moving_average_filter_vectorized(data, maf_n)
    return maf[-1]


def no_delay_moving_average_filter_on_that_day_vectorized(data, maf_n):
    maf = []
    for i in range(len(data)):
        data_for_use = data[0:i+1]
        maf.append(no_delay_moving_average_filter(data_for_use, maf_n))
    return maf


def percentage_difference(from_here, to_here):
    assert from_here != 0
    return 100*(to_here - from_here)/np.abs(from_here)


def slope(data, n):
    if not isinstance(data, list):
        data = [data]
    if (len(data) < 2) or (n < 2):
        return 0
    n = np.min([np.max([n, 1]), len(data)])
    return data[-1] - data[-n]


def curvature(data):
    if not isinstance(data, list):
        data = [data]
    if (len(data) < 3):
        return 0
    d_data = [slope([data[-3], data[-2]], 2), slope([data[-2], data[-1]], 2)]
    return slope(d_data, 2)


def slope_vectorized(data, n):
    if not isinstance(data, list):
        data = [data]
    slope_vec = []
    for i in range(0, len(data)):
        data_for_use = data[0:i+1]
        slope_vec.append(slope(data_for_use, n))
    return slope_vec


def curvature_vectorized(data):
    if not isinstance(data, list):
        data = [data]
    curvature_vec = []
    for i in range(0, len(data)):
        data_for_use = data[0:i+1]
        curvature_vec.append(curvature(data_for_use))
    return curvature_vec


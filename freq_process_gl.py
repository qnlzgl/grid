import numpy as np
import pandas as pd

# Parameters
N_f = 6  # Max number of NaN points to fill
T_c = 60  # Max length of allowed constant windows
df_c = 0.05  # Min height of isolated peaks

def true_intervals(bool_arr):
    """Get intervals where bool_arr is true."""
    mask = np.concatenate([[True], ~bool_arr, [True]])
    interval_bounds = np.flatnonzero(mask[1:] != mask[:-1]).reshape(-1, 2)
    interval_sizes = interval_bounds[:, 1] - interval_bounds[:, 0]
    return interval_bounds, interval_sizes

def extreme_points(data, limit=(49, 51)):
    """Identify points where values are outside acceptable limits."""
    f_too_low = np.argwhere((data < limit[0]).values)[:, 0]
    f_too_high = np.argwhere((data > limit[1]).values)[:, 0]
    print(f'Number of too high frequency values: {f_too_high.size}, '
          f'Number of too low frequency values: {f_too_low.size}')
    return f_too_low, f_too_high

def const_windows(increments, limit=60):
    """Identify constant value windows longer than the limit."""
    wind_bounds, wind_sizes = true_intervals(increments.abs() < 1e-9)
    long_window_bounds = wind_bounds[wind_sizes > limit]

    if long_window_bounds.size != 0:
        long_windows = np.hstack([np.r_[i:j] for i, j in long_window_bounds])
    else:
        long_windows = np.array([])

    print(f'Number of windows with constant frequency longer than {limit}s: {long_window_bounds.shape[0]}')
    return wind_bounds, wind_sizes, long_windows, long_window_bounds

def nan_windows(data):
    """Identify NaN windows."""
    wind_bounds, wind_sizes = true_intervals(data.isnull())
    print(f'Number of NaN intervals: {wind_sizes.shape[0]}')
    return wind_bounds, wind_sizes

def isolated_peaks(increments, limit=0.05):
    """Identify isolated peaks based on change magnitude."""
    high_incs = increments.where(increments.abs() > limit)
    peak_locations = np.argwhere((high_incs * high_incs.shift(-1) < 0).values)[:, 0]
    print(f'Number of isolated peaks: {peak_locations.size}')
    return peak_locations

def clean_data(series, N_f=6, T_c=60, df_c=0.05, limit=(49, 51)):
    """Main function to clean the series."""
    print('Find corrupted data ...')
    
    # Calculate differences
    increments = series.diff()
    
    # Identify extreme points
    f_too_low, f_too_high = extreme_points(series, limit)
    
    # Identify isolated peaks
    peak_loc = isolated_peaks(increments, df_c)
    
    # Identify constant windows
    window_bounds, window_sizes, long_windows_indices, long_window_bounds = const_windows(increments, T_c)
    
    # Identify NaN windows
    missing_data_bounds, missing_data_sizes = nan_windows(series)

    # Create a copy to mark corrupted data as NaN
    print('Mark corrupted data ...')
    data_m = series.copy()
    data_m.iloc[f_too_low] = np.nan
    data_m.iloc[f_too_high] = np.nan
    data_m.iloc[peak_loc] = np.nan
    data_m.iloc[long_windows_indices] = np.nan

    # Fill missing values up to N_f points
    print('Clean corrupted data ...')
    data_cl = data_m.fillna(method='ffill', limit=N_f)
    
    return data_cl

# Example usage with a pandas Series
# Assuming 'series' is your pandas Series with minute-level frequency data
cleaned_series = clean_data(series)
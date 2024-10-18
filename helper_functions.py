import glob
from calendar import monthrange
import numpy as np
import pandas as pd
import os
from parse import parse


def true_intervals(bool_arr):
    
    """ Get intervals where bool_arr is true"""

    mask = np.concatenate([[True], ~bool_arr, [True]])
    interval_bounds = np.flatnonzero(mask[1:] != mask[:-1]).reshape(-1, 2)
    interval_sizes = interval_bounds[:, 1] - interval_bounds[:, 0]

    return interval_bounds, interval_sizes


def extreme_points(data, limit=(49, 51)):
    f_too_low = np.argwhere((data < limit[0]).values)[:, 0]
    f_too_high = np.argwhere((data > limit[1]).values)[:, 0]

    print('Number of too high frequency values: ', f_too_high.size,
          'Number of too low frequency values: ', f_too_low.size)

    return f_too_low, f_too_high


def extreme_inc(increments, limit=0.05):
    inc_too_high = np.argwhere((increments.abs() > limit).values)[:, 0]

    print('Number of too large increments: ', inc_too_high.size)

    return inc_too_high


def const_windows(increments, limit=60):
    wind_bounds, wind_sizes = true_intervals(increments.abs() < 1e-9)

    long_windows = [[]]
    long_window_bounds = wind_bounds[wind_sizes > limit]

    if long_window_bounds.size != 0:
        long_windows = np.hstack([np.r_[i:j] for i, j in long_window_bounds])

    print('Number of windows with constant frequency for longer than {}s: '.format(limit),
          long_window_bounds.shape[0])

    return wind_bounds, wind_sizes, long_windows, long_window_bounds


def nan_windows(data):
    wind_bounds, wind_sizes= true_intervals(data.isnull())

    print('Number of Nan-intervals: ', wind_sizes.shape[0])

    return wind_bounds, wind_sizes


def isolated_peaks(increments, limit=0.05):
    high_incs = increments.where(increments.abs() > limit)
    peak_locations = np.argwhere((high_incs * high_incs.shift(-1) < 0).values)[:, 0]

    print('Number of isolated peaks: ', peak_locations.size)

    return peak_locations


def prepare_files(in_path, name_pattern):
    
    """Prepare a list of files in in_path that is sorted according to the date in the filename. Moreover,
     return the initial and the final timestamps of each month. Each file should represent one month."""

    # Load csv files in in_path
    files = np.array(glob.glob(in_path + '*.csv'))

    # Parse year and month from files according to name_pattern
    parsed = [parse(name_pattern, file) for file in files]
    file_dates = pd.to_datetime([file['year'] + '-' + file['month'] for file in parsed])

    # Sort files and file_dates by date
    file_sort_args = np.argsort(file_dates)
    files = files[file_sort_args]
    file_dates = file_dates[file_sort_args]

    # Get first and last timestamp for each month. file_dates includes first timestamp by default
    start_time = file_dates
    end_time = file_dates + pd.offsets.MonthEnd() + pd.offsets.DateOffset(hours=23, minutes=59, seconds=59)

    return files, start_time, end_time

def create_year_folders(root_folder, data, suffix, tso_name):
    
    for year in data.index.year.unique():
        folder = root_folder + '{}'.format(year) + suffix + '/{}/'.format(tso_name)
    
        if not os.path.exists(folder):
            os.makedirs(folder)   
    
def correct_indices_transnet(in_path, out_path, tso_name):
    
    """ Convert TransnetBW data to pandas Series with complete, tz-localized time index."""
    
    # Prepare files and initial/final timestamps of the months
    files_name_pattern = '{}/{year:.4}{month:.2}_Frequenz.csv'
    files, start_time, end_time = prepare_files(in_path, files_name_pattern)

    data = pd.Series()
    print('Processing the TransnetBW data...\n')
    
    for i, file in enumerate(files):
        print('File {} of {}'.format(i, len(files)))
        print(file)
        
        # Read external data
        new_data = pd.read_csv(file, header=None, names=['day', 'time', 'f'], usecols=[0, 1, 3])

        # Concatenate datetime columns from imported data
        dt_data = new_data.day + ' ' + new_data.time

        # Convert dt_data to datetime and coerce parsing-errors into setting values to NaN
        ind = pd.to_datetime(dt_data, errors='coerce')

        # If there are errors, try two other datetime formats that can occur in the data due to DST
        if ind.hasnans:
            try:
                mask = ind.isnull()
                ind_a = pd.to_datetime(dt_data[mask], format='%Y/%m/%d %HA:%M:%S', errors='coerce').dropna()
                ind_b = pd.to_datetime(dt_data[mask], format='%Y/%m/%d %HB:%M:%S', errors='coerce').dropna()
                ind[mask] = ind_a.append(ind_b).values
            except ValueError:
                print('There are unknown datetime formats in the data! Add them to dt_formats!')

        # Localize datetime index to obtain unique timestamps also during DST changes
        ind = ind.dt.tz_localize('CET', ambiguous='infer')
        new_data = new_data.set_index(ind).loc[:, 'f']

        # Remove duplicated recordings
        new_data = new_data[~new_data.index.duplicated()]

        # Align data to the full month index and fill missing data with NaN
        full_ind = pd.date_range(start=start_time[i], end=end_time[i], freq='1s', tz='CET')
        new_data = new_data.reindex(full_ind, fill_value=np.NaN)

        # Append to other data and make sure that all values have the same format 'float64'
        data = data.append(new_data.astype('float64'))
        
    # Convert timestamp to naive local time (removing tz-information)
    data.index = data.index.tz_localize(None)
    
    # Save reindexed data
    print('Saving processed data...')
    suffix = '_converted'
    create_year_folders(out_path, data, suffix, tso_name)
    data.groupby(by=data.index.year).apply(lambda x: x.to_csv(out_path + '{}'.format(x.name) + suffix + \
                                                              '/' + tso_name + '/{}.zip'.format(x.name),
                                                              float_format='%.6f',
                                                              na_rep='NaN',
                                                              compression={'method':'zip',
                                                                           'archive_name':'{}.csv'.format(x.name)},
                                                              header=False))

def correct_indices_nationalgrid(in_path, out_path, tso_name):
    
    """ Convert Nationalgrid data to pandas Series with complete, tz-localied time index."""
    
    # Prepare files and initial/final timestamps of the months
    files_name_pattern = '{}/f {year:.4} {month}.csv'
    files, start_time, end_time = prepare_files(in_path, files_name_pattern)

    data = pd.Series()
    print('Processing the Nationalgrid data...\n')
    
    for i, file in enumerate(files):
        print('File {} of {}'.format(i, len(files)))
        print(file)

        # Read external data
        new_data = pd.read_csv(file)

        # Align data to the full month index. 
        # The data indices have different formats, so that we need to create our own one.
        full_ind = pd.date_range(start=start_time[i], end=end_time[i], freq='1s',
                                 tz='UTC')
        new_data.index = full_ind.tz_convert('GB')

        # Append to other data
        data = data.append(new_data.f)

    # Convert timestamp to naive local time (removing tz-information)
    data.index = data.index.tz_localize(None)

    # Save reindexed data
    print('Saving processed data...')
    suffix = '_converted'
    create_year_folders(out_path, data, suffix, tso_name)
    data.groupby(by=data.index.year).apply(lambda x: x.to_csv(out_path + '{}'.format(x.name) + suffix + \
                                                              '/' + tso_name + '/{}.zip'.format(x.name),
                                                              float_format='%.3f',
                                                              na_rep='NaN',
                                                              compression={'method':'zip',
                                                                           'archive_name':'{}.csv'.format(x.name)},
                                                              header=False))

def correct_indices_fingrid(in_path, out_path, tso_name):
    
    """ Convert Fingrid data to pandas Series with complete, tz-localied time index and resample
    it to a resolution of 1s."""
    
    # Prepare files. 
    # Due to the file name format, the np.sort already produces the correct file order in time!
    files = glob.glob(in_path + '*.csv')
    files = np.sort(files)

    data = pd.Series()
    print('Processing the Fingrid data...\n')
    
    for i, file in enumerate(files):

        print('File {} of {}'.format(i, len(files)))
        print(file)

        try:
            # Read external data
            new_data = pd.read_csv(file, index_col='Time', parse_dates=True)

            # Localize the datetime index in its timezone 
            new_data.index = new_data.index.tz_localize('Europe/Helsinki',
                                                        ambiguous='infer')

            # Resampling
            new_data = new_data.resample('1S').mean()

            # Append to other data
            data = data.append(new_data.loc[:,'Value'])

        except Exception as e:
            # There are some empty data files which have to be filtered out by this exception
            print(e)
            continue

    # Reindex with full index and identify missing values with NaNs.
    full_ind = pd.date_range(start=data.index[0], end=data.index[-1], freq='1S',
                             tz='Europe/Helsinki')
    data = data.reindex(full_ind, fill_value=np.NaN)

    # Convert timestamp to naive local time (removing tz-information)
    data.index = data.index.tz_localize(None)
    
    # Save reindexed data 
    print('Saving processed data...')
    suffix = '_converted'
    create_year_folders(out_path, data, suffix, tso_name)
    data.groupby(by=data.index.year).apply(lambda x: x.to_csv(out_path + '{}'.format(x.name) + suffix + \
                                                              '/' + tso_name + '/{}.zip'.format(x.name),
                                                              float_format='%.4f',
                                                              na_rep='NaN',
                                                              compression={'method':'zip',
                                                                           'archive_name':'{}.csv'.format(x.name)},
                                                              header=False))


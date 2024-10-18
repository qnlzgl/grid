import glob
import numpy as np
import pandas as pd
import sys

sys.path.append('./')

from scripts.helper_functions import const_windows, nan_windows, create_year_folders
from scripts.helper_functions import isolated_peaks,  extreme_points

# Add path to processed data!
path_to_data = './'

# Additional parameters for output path creation
tso_names = ['TransnetBW', 'Nationalgrid', 'Fingrid']
suffix = '_cleansed'
precisions = ['%.6f','%.3f','%.4f']

# Set parameters for identifying corrupted data 

# Nan-points to fill 
N_f=6 
# Maximum length of allowed constant windows
T_c=60 
# Minimum height of isolated peaks
df_c=0.05 



# Mark and clean corrupted data points

for precision, tso_name in zip(precisions, tso_names):
    
    print('Marking and cleansing data from {}'.format(tso_name))
    
    ### Read the frequency data and calculate the increments ###
    
    print('Load data ...')
    files = glob.glob(path_to_data + '*_converted/' + '{}/'.format(tso_name) + '*.zip')
    files = np.sort(files)
    data = pd.Series(dtype=float)
    for i,file in enumerate(files):
        print('{} ({} of {})'.format(file, i+1, len(files)))
        chunk = pd.read_csv(file, index_col=0, header=None, squeeze=True)
        data = data.append(chunk)
    data.index = pd.to_datetime(data.index)
    
    df = data.diff()  

    ### Find positions and numbers of corrupted data ###
    
    print('Find corrupted data ...')
    # Indices where f(t) is too high/low
    f_too_low, f_too_high = extreme_points(data, (49, 51))
    # Location of isolated peaks
    peak_loc=isolated_peaks(df, df_c)
    # Right/Left bounds, sizes and indices of windows (>1 point) and long windows (> T_c points) 
    window_bounds, window_sizes, long_windows_indices, long_window_bounds=const_windows(df, T_c)
    # Right/Left indices and sizes of missing data 
    missing_data_bounds, missing_data_sizes = nan_windows(data)
 
    ### Mark corrupted data as NaN ###
    
    print('Mark corrupted data ...')
    data_m=data.copy()
    # Mark extreme values >51Hz and <49Hz 
    data_m.iloc[f_too_low]=np.nan
    data_m.iloc[f_too_high]=np.nan
    # Mark isolated peaks with abs. increments > df_c 
    data_m.iloc[peak_loc]=np.nan
    # Mark windows with const. freq. longer than T_c
    data_m.iloc[long_windows_indices]=np.nan

    ### Cleansing data by filling intervals of missing/ corrupted data ###
    
    # You can add your own cleansing procedure!
    # Here, we fill up to N_f values by propagating the last valid entry
    print('Clean corrupted data ...')
    data_cl=data_m.fillna(method='ffill', limit=N_f)
    
    ### Save cleansed data (including the remaining NaN-values) ###
    
    print('Saving the results ...')
    create_year_folders(path_to_data, data_cl, suffix, tso_name)
    data_cl.groupby(by=data_cl.index.year).apply(lambda x: x.to_csv(path_to_data + '{}'.format(x.name) + suffix + \
                                                                    '/' + tso_name + '/{}.zip'.format(x.name),
                                                                    float_format=precision,
                                                                    na_rep='NaN',
                                                                    compression={'method':'zip',
                                                                                 'archive_name':'{}.csv'.format(x.name)},
                                                                    header=False))

    ### Optional: Select longest interval with non-NaN data ### 
    
    # # Find non-NaN intervals and print maximum length 
    # valid_bounds, valid_sizes = true_intervals(~data_cl.isnull())
    # print('Length of longest interval without NaNs [in months]: ca. {:.0f}'.format(np.max(valid_sizes) / (3600.*24*30) ) )
    # # Select longest valid interval (without Nan values)
    # start,end= valid_bounds[ np.argmax(valid_sizes) ]
    # data_sel=data_cl.iloc[start:end]
    # data_sel.to_csv(out_path + 'selected_data.csv', float_format=precision)



# %%

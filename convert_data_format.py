# %%
import sys
sys.path.append('./')

from scripts.helper_functions import correct_indices_fingrid, correct_indices_nationalgrid, correct_indices_transnet

# Add path where processed data should be saved
path_to_data = './'
# Add path to external (downloaded) data
path_to_external_data = '../../External_data/'


# %% TransnetBW

in_path = path_to_external_data + 'Germany/transnetbw_frequency_data/'
tso_name = 'TransnetBW'

correct_indices_transnet(in_path, path_to_data, tso_name)

# %% Fingrid

in_path = path_to_external_data + 'Finland/fingrid_historic_frequency_data/'
tso_name = 'Fingrid'

correct_indices_fingrid(in_path, path_to_data, tso_name)

#%% Nationalgrid

in_path = path_to_external_data + 'GreatBritain/nationalgrideso_historic_frequency_data/'
tso_name = 'Nationalgrid'

correct_indices_nationalgrid(in_path, path_to_data, tso_name)




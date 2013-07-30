# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from scipy.interpolate import interp1d
import numpy as np
def interpolate_th(selfe_time_history_df, new_time_step, out_th_file):
    """Linearly interpolates time series at a given time_step to a new_time_step and writes a new out_th_file."""
    last_time_stamp = floor(selfe_time_history_df.time_step[-1] / new_time_step) * new_time_step
    new_dt_series = (new_time_step, last_time_stamp, new_time_step)
    inter_func = interp1d(selfe_time_history_df.time_step.values, selfe_time_history_df.values[:, 1:], bounds_error=False, axis=0)
    data_new_time_step = interp_func(new_dt_series)
    return np.column_stack((new_dt_series, data_new_time_step)
    
    

# <codecell>



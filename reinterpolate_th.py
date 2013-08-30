# -*- coding: utf-8 -*-
"""
Created on Fri Aug 30 08:15:40 2013

@author: snegusse

usage example: 

from an ipython shell
run ~/pyselfe/reinterpolate_th.py /home/snegusse/calibration_period/ flux.th 90 flux_test.th

where flux.th is the existing th file at any time step.
90 is the new time time step.
flux_test.th is the new th file with the new time step(90)
"""



import os
import sys

from scipy.interpolate import interp1d
import pandas as pd


def interpolate_th(selfe_time_history_df, new_time_step):
    """
    Linearly interpolates SELFE time history data at a given time step 
        to a new_time_step.
    Returns a numpy ndarray of the time history data at new time step.
    """
    last_time_stamp = pd.np.floor(selfe_time_history_df[0].values[-1] / \
                        new_time_step) * new_time_step
    new_dt_series = pd.np.arange(new_time_step, last_time_stamp, new_time_step)
    interp_func = interp1d(selfe_time_history_df[0].values, 
                           selfe_time_history_df.values[:, 1:], 
                            bounds_error=False, axis=0)
    data_new_time_step = interp_func(new_dt_series)
    return pd.np.column_stack((new_dt_series, data_new_time_step))


data_dir = sys.argv[1]
th_filename = sys.argv[2]
new_time_step = int(sys.argv[3])
output_th_filename = sys.argv[4]
output_th_file = os.path.join(data_dir, output_th_filename)

th_file = os.path.join(data_dir, th_filename)
th_data = pd.read_csv(th_file, sep='\s*', header=None)

th_at_new_timestep = interpolate_th(th_data, new_time_step) 
pd.np.savetxt(output_th_file, th_at_new_timestep, 
           fmt= '%i' + '%10.3f' * (th_data.columns.size - 1))






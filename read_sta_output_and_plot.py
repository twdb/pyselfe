# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:10:34 2013

@author: snegusse
"""
import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
base_dir = '/home/snegusse/modeling/brazos_river/calibration_20080824'
plot_dir = '/T/BaysEstuaries/USERS/SNegusse/Brazos/calibration_runs'
out_filename = 'staout_6'
mod_files = {'upwind':os.path.join(base_dir, 'base_case', 'outputs_const_san_bernard',
                                out_filename),
            'tvd': os.path.join(base_dir, 'advection_scheme', 'tvd',
                                'outputs', out_filename)}
obs_file = os.path.join(base_dir, 'all_sites_salinity.csv')
            
start_datetime = pd.datetime(2008,8,24)
sim_data_dict = {}

for sim in mod_files.keys():
    sal_data = np.genfromtxt(mod_files[sim], dtype=np.float)
    mod_datetimes = [pd.datetools.Second(t) + start_datetime for t in sal_data[:,0]]
    
    sal_df = pd.DataFrame(sal_data[:,[3,9,11,17,19,22,26,28]], 
                          columns=['bz1u', 'bz2u','bz2l','bz3u','bz3l','bz5u',
                                   'bz5l','bz6u'], index=mod_datetimes)
    sim_data_dict[sim] =  sal_df

selected_sites = {'bz2u': '23.8 river mile near Dow Chemical pump station (top)', 
                  'bz2l': '23.8 river mile near Dow Chemical pump station (bottom)', 
                  'bz3u': '15.5 river mile near FM 2004 bridge (top)', 
                  'bz3l': '15.5 river mile near FM 2004 bridge (bottom)',
                  'bz5u': '7.7 river mile near SH 36 bridge (top)', 
                  'bz5l': '7.7 river mile near SH 36 bridge (bottom)', 
                  'bz6u': '4.9 river mile near GIWW confluence (top)'}

obs_data = pd.read_csv(obs_file, sep=',', header=0, parse_dates=[0], 
                       index_col=0)

for site in selected_sites:  
    plt.figure()    
    obs_data = obs_data[obs_data > 0.]
    obs_data[site].plot(style='b.', label='observed')
    sim_data = sim_data_dict['upwind']
    sim_data[site].plot(style='r.', label='model predicted')
    plt.title(site.upper() + ' - ' + selected_sites[site])
    plt.ylabel('salinity, psu')
    plt.ylim(0,35)    
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(plot_dir, site + '_sal_ts.png'))
       
    scatter_df = pd.DataFrame({'obs': obs_data[site], 'mod': sim_data[site]})
    scatter_df = scatter_df.resample('H').dropna(how='any')
    scatter_df.index = scatter_df['obs']
    scatter_df = scatter_df.sort_index()
    scatter_df.plot(style={'obs':'k-', 'mod':'b.'})
    plt.title(site.upper() + ' - ' + selected_sites[site])
    plt.xlabel('observed')    
    plt.ylabel('model predicted')
    plt.xlim(0,35)
    plt.ylim(0,35)
    plt.grid(True)
#    plt.savefig(os.path.join(plot_dir, site + '_sal_scatter.png'))
    
plt.show()
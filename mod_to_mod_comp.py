# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 16:10:34 2013

@author: snegusse
"""
import os

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
base_dir = '/home/snegusse/modeling/brazos_river/historical_scenarios'
plot_dir = '/T/BaysEstuaries/USERS/SNegusse/Brazos/calibration_runs'
out_filename = 'staout_6'
mod_files = {'old_river_mouth': os.path.join(base_dir, 'pre_realignment_no_giww',
                                      out_filename),
            'diverted_river_no_giww': os.path.join(base_dir, 'post_realignment_no_giww',
                                      out_filename),
            'diverted_river_w_giww': os.path.join(base_dir, 'post_realignment_w_giww',
                                      out_filename),}
obs_file = os.path.join(base_dir, 'all_sites_salinity.csv')
            
start_datetime = pd.datetime(2008,8,24)
sim_data_dict = {}

for sim in mod_files.keys():
    sal_data = np.genfromtxt(mod_files[sim], dtype=np.float)
    mod_datetimes = [pd.datetools.Second(t) + start_datetime for t in 
                    sal_data[:,0]]
    if sim != 'old_river_mouth':
        sal_df = pd.DataFrame(sal_data[:,[3,9,12,16,20,22,27,28]], 
                              columns=['bz1u', 'bz2u','bz2l','bz3u','bz3l','bz5u',
                                       'bz5l','bz6u'], index=mod_datetimes)
    else:
        sal_df = pd.DataFrame(sal_data[:,[3,9,12,16,20]], 
                      columns=['bz1u', 'bz2u','bz2l','bz3u','bz3l'], index=mod_datetimes)
    sim_data_dict[sim] =  sal_df

selected_sites = {'bz2u': '23.8 river mile near Dow Chemical pump station (top)', 
                  'bz2l': '23.8 river mile near Dow Chemical pump station (bottom)', 
                  'bz3u': '15.5 river mile near FM 2004 bridge (top)', 
                  'bz3l': '15.5 river mile near FM 2004 bridge (bottom)',
                  'bz5u': '7.7 river mile near SH 36 bridge (top)', 
                  'bz5l': '7.7 river mile near SH 36 bridge (bottom)', 
                  'bz6u': '4.9 river mile near GIWW confluence (top)'}

#obs_data = pd.read_csv(obs_file, sep=',', header=0, parse_dates=[0], 
#                       index_col=0)
start_date = sim_data_dict['diverted_river_w_giww'].index[0]
end_date = sim_data_dict['diverted_river_w_giww'].index[-1]

for site in selected_sites: 
    plt.figure()
    site_dict = {}
    stat_dict = {}

    for sim in mod_files.keys():
        if site in sim_data_dict[sim]:
            site_dict[sim] = sim_data_dict[sim][site]
            stat_dict[sim] = site_dict[sim].ix[start_date:end_date].describe().ix['mean']
        
#    obs_data[site].dropna().plot(style='b-', label='observed')
    site_df = pd.DataFrame(site_dict)
    site_df.plot(style='.')
    plt.title(site.upper()[:3] + ' - ' + selected_sites[site])
    plt.ylabel('salinity, psu')
#    plt.xlim(start_date, end_date)
    plt.ylim(-0.1,45)
    if len(stat_dict.keys())==2:
        plt.annotate('mean salinity:\ndiverted_river_no_giww= ' 
                    + str(stat_dict['diverted_river_no_giww'])[:3] + ' psu' + '\n' + \
                 'diverted_river_w_giww= ' + str(stat_dict['diverted_river_w_giww'])[:3] + ' psu' + '\n', 
                    xy=(0.10, 0.80),xycoords='axes fraction') 
    else:
        plt.annotate('mean salinity:\n'+
                    'old_river_mouth= '  + str(stat_dict['old_river_mouth'])[:3] + ' psu' + '\n' +
                   'diverted_river_no_giww= ' 
            + str(stat_dict['diverted_river_no_giww'])[:3] + ' psu' + '\n' + \
         'diverted_river_w_giww= ' + str(stat_dict['diverted_river_w_giww'])[:3] + ' psu' + '\n', 
            xy=(0.10, 0.80),xycoords='axes fraction') 
#    plt.xlim(site_dict['stratified_ic'].index[0], site_dict['stratified_ic'].index[-1])
    plt.grid(True)
    plt.legend()
    plt.savefig(os.path.join(plot_dir, site + 'scenario.png'))

       
    
plt.show()
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
plot_dir = '/T/BaysEstuaries/USERS/SNegusse/Brazos/report_material/Figures/calibration/water_level'

parameter = 'salinity'

out_filename = {'water_level': 'staout_1', 'salinity':'staout_6'}
mod_files = {'scenone':os.path.join('/home/snegusse/modeling/brazos_river/historical_scenarios/pre_realignment_no_giww/calibration_period',
                                out_filename[parameter]),
            'scentwo':os.path.join('/home/snegusse/modeling/brazos_river/historical_scenarios/post_realignment_no_giww/calibration_period',
                                    out_filename[parameter]),
            'scenthree':os.path.join('/home/snegusse/modeling/brazos_river/historical_scenarios/post_realignment_w_giww/calibration_period',
                                    out_filename[parameter])}
                                
         
start_datetime = pd.datetime(2008,8,24)
sim_data_dict = {}
sim_percentiles = {}
for sim in mod_files.keys():
    param_data = np.genfromtxt(mod_files[sim], dtype=np.float)
    mod_datetimes = [pd.datetools.Second(t) + start_datetime for t in param_data[:,0]]

    if sim == 'scenone':
        param_df_one = pd.DataFrame(param_data[:,[3,9,11,17,19,22,25,28,31]],
                    columns=['bz1u', 'bz2u', 'bz2l', 'bz3u', 'bz3l', 
                    'concrete', 'near_dow','diversion_point', 'sbr'], 
                    index=mod_datetimes)
        sim_data_dict[sim] =  param_df_one
    else:
        param_df_two_three = pd.DataFrame(param_data[:,[3,9,11,17,19,22,25,28,31,35,38,43]], 
                     columns=['bz1u', 'bz2u','bz2l','bz3u','bz3l','concrete',
                              'near_dow', 'diversion_point', 'bz5u',
                               'bz5l','bz6u','sbr'], index=mod_datetimes)
        sim_data_dict[sim] = param_df_two_three
    sim_percentiles[sim] = sim_data_dict[sim].describe()

site_description = {'bz1u': '33.9 river mile near SH 35 bridge',
                  'bz2u': '23.8 river mile near Dow Chemical pump station (top)', 
                  'bz2l': '23.8 river mile near Dow Chemical pump station (bottom)', 
                  'bz3u': '15.5 river mile near FM 2004 bridge (top)', 
                  'bz3l': '15.5 river mile near FM 2004 bridge (bottom)',
                  'bz5u': '7.7 river mile near SH 36 bridge (top)', 
                  'bz5l': '7.7 river mile near SH 36 bridge (bottom)', 
                  'bz6u': '4.9 river mile near GIWW (top)',
                  'sbr': 'San Bernard River near GIWW'}
scen_1_sites = ['bz1u', 'bz2l', 'bz3l', 'concrete', 'near_dow','diversion_point']
scen_2_sites = ['bz1u', 'bz2l', 'bz3l', 'concrete', 'near_dow','diversion_point', 
            'bz5l', 'bz6u', 'sbr']
scen_3_sites = ['bz1u', 'bz2l', 'bz3l', 'concrete', 'near_dow','diversion_point', 
            'bz5l', 'bz6u', 'sbr']

sites_not_in_scen_one = [s for s in scen_2_sites if s not in scen_1_sites]
            
scen_1_medians = sim_percentiles['scenone'].T.ix[scen_1_sites]['75%']
scen_2_medians = sim_percentiles['scentwo'].T.ix[scen_2_sites]['75%']
scen_3_medians = sim_percentiles['scenthree'].T.ix[scen_3_sites]['75%']
for site in sites_not_in_scen_one:
    scen_1_medians.append(pd.Series({'50%':[np.nan]}, index=[site]))
    

N = len(scen_3_sites)
ind = np.arange(N*3,step=3)
width = 0.5
ax = plt.figure(figsize=(11,8.5)).add_subplot(111)
#plt.axvspan(3.5,11.5,facecolor='0.5', alpha=0.5)  
#plt.axvspan(15.5,19.5, facecolor='0.5', alpha=0.5)
rects1 = ax.bar(ind, scen_1_medians.ix[scen_3_sites], width, color='b')
rects2 = ax.bar(ind+width, scen_2_medians[scen_3_sites], width, color='r')
rects3 = ax.bar(ind+2*width, scen_3_medians[scen_3_sites], width, color='g')

ax.set_ylabel('salinity, psu')
ax.legend((rects1[0], rects2[0],rects3[0]), ('before brazos river diversion', 
                                   'after brazos river diversion no giww', 
                                   'after brazos river diversion with giww'), 
                                   prop={'size':8}, loc='best')
ax.set_xticks(ind+1.5 * width)
ax.set_xticklabels(scen_3_sites)

#percentiles = {}

for site in scen_1_sites:  
    plt.figure()    
    if parameter == 'water_level':
        mod_site = site + 'u'
#    obs_data = obs_data[obs_data > 0.]
    sim_one_data = sim_data_dict[mod_files.keys()[0]]
    sim_one_data[site].plot(style='-', label=mod_files.keys()[0])
    sim_two_data = sim_data_dict[mod_files.keys()[1]]
    sim_two_data[site].plot(style='-', label=mod_files.keys()[1])
    plt.title(site.upper() + ' - ' + site)
    plt.ylabel(parameter)
#    plt.ylim(0,35)    
    plt.grid(True)
    plt.legend()
#    plt.savefig(os.path.join(plot_dir, site + '_sal_ts.png'))
      
    """ 
    scatter_df = pd.DataFrame({'obs': obs_data[obs_site], 'mod': sim_data[mod_site]})
    scatter_df = scatter_df.resample('H').dropna(how='any')
    scatter_df.index = scatter_df['obs']
    scatter_df = scatter_df.sort_index()
    scatter_df.plot(style={'obs':'k-', 'mod':'b.'})
    plt.title(site.upper() + ' - ' + selected_sites[mod_site])
    plt.xlabel('observed')    
    plt.ylabel('model predicted')
    plt.legend().set_visible(False)
#    plt.xlim(0,35)
#    plt.ylim(0,35)
    plt.grid(True)
#    plt.savefig(os.path.join(plot_dir, site + '_sal_scatter.png'))
    """
plt.show()

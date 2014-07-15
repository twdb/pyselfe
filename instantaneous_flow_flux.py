# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 14:22:31 2013

@author: SNegusse
"""
import os
import sys
sys.path.append('/home/snegusse/pyselfe/')

import numpy as np 
import matplotlib.pyplot as plt
import pandas as pd

import pyselfe

"""
compute flow/flux at a given cross-section. 
assumptions: 
1. the channel width is uniformly divided by the model nodes
2. the channel width remains constant all depths,i.e. Area = width * depth
"""

sfile = 1
nfiles = 15
mod_start_datetime = pd.datetime(2008,8,24,0,0)


base_dir = '/home/snegusse/modeling/brazos_river/historical_scenarios'
mod_dir = os.path.join(base_dir, 'calibration_period/post_realignment_no_giww')
#'fine': os.path.join(base_dir, 'grid_convergence', 'fine_grid_tvd',
#                                'outputs')}
sal_init_filename = str(sfile) + '_salt.63'
vel_init_filename = str(sfile) + '_hvel.64'

sal_init_file = os.path.join(mod_dir,sal_init_filename)
vel_init_file = os.path.join(mod_dir, vel_init_filename)
"""
#based on joseph's grid'
profile_nodes = {'river_boundary': np.array([51,50,49,52]),
                 'bz2': np.array([4208,4207,4206,4205,4203,4204]),
                                'bz5': np.array([11099,11098,11097,11096,
                                                     11095,11094,11093]),
                                'giww-u': np.array([12512,12510,12509,12508,
                                                    12507,12506]),
                                'giww-d': np.array([12871,12888,12869,12867,
                                                    12866,12847,12850])}
"""    
#final grid                                                
profile_nodes = {'river_boundary': np.array([80,79,78,77]),
                 'bz2': np.array([7354,7353,7352,7351,7350,7349]),
                                'straight_ds_bz3': np.array([11908,11907,11906,
                                                             11905,11904,11903]),
                                'giww-u': np.array([16654,16653,16652,16651,
                                                    16650,16649,16648]),
                                'giww-d': np.array([17150,1749,17148,17147,17146,
                                                    17145,17144]),
                                'near_dow': np.array([14122,14121,1420,14119,
                                                      14118,14117])}                                                   
                              
channel_props = pd.DataFrame(data={'river_boundary': [113.,178.],
                                   'bz2': [36.5, 93],
                                    'straight_ds_bz3': [103., 104.],
                                    'giww-u': [85., 185.],
                                    'giww-d': [80., 192.],
                                    'near_dow': [45., 183.]}, 
                                   index=['orientation', 'width']).T

weights = {'river_boundary': np.array([.5,1,1,.5]),
           'bz2': np.array([.5, 1., 1., 1., 1., .5]),
           'straight_ds_bz3': np.array([.5,1,1,1,1,.5]),
            'giww-u': np.array([.5,1,1,1,1,1,.5]),
            'giww-d': np.array([.5,1,1,1,1,1,.5]),
            'near_dow': np.array([.5,1,1,1,1,.5])}

sites_sal_data = {}
sites_xvel_data = {}
sites_dp_data = {}
salt_flux = {}
flow_cfs = {}

mod_initial = (sal_init_file, vel_init_file)
[sal_t, tstep, eta, dp, sal_data] = \
mod_initial[0].read_time_series('salt.63', nfiles=nfiles, 
                             datadir=mod_dir, sfile=sfile)   
[vel_t, tstep, eta, dp, vel_data] = \
mod_initial[1].read_time_series('hvel.64',nfiles=nfiles, 
                                datadir=mod_dir, sfile=sfile)                               
                             
for profile in profile_nodes.keys():
    flow_file = os.path.join(base_dir, mod_dir, profile + '_flow.csv' )
    hdf5_file = os.path.join(base_dir, mod_dir, profile + '.h5')
    if os.path.exists(flow_file):
        flow_data = pd.read_csv(flow_file, sep=',',parse_dates=[0], 
                                index_col=0, header=0)
        hdf5_storage = pd.io.pytables.HDFStore(hdf5_file, mode='r')
        sites_sal_data[profile] = hdf5_storage['salinity']
        sites_xvel_data[profile] = hdf5_storage['x_vel']
        sites_dp_data[profile] = hdf5_storage['depth']
    else:
        nodes = (profile_nodes[profile] - 1)
        profile_sal_data = sal_data[:,nodes,1:,:]
        profile_vel_data = vel_data[:,nodes,1:,:]
        
        sal_mod_datetimes = [mod_start_datetime + pd.datetools.Second(dt)
                            for dt in sal_t]
        vel_mod_datetimes = [mod_start_datetime + pd.datetools.Second(dt)
                    for dt in vel_t]
        sites_sal_data[profile] = pd.Panel(profile_sal_data[:,:,:,0],
                                         major_axis=profile_nodes[profile], 
                                         items=sal_mod_datetimes)    
        profile_xvel_data =  profile_vel_data[:,:,:,0] * \
        np.cos(channel_props.ix[profile,'orientation'] * np.pi / 180.) - \
        profile_vel_data[:,:,:,1] * np.sin(channel_props.ix[profile,'orientation'] * \
                                    np.pi / 180.) 
        sites_xvel_data[profile] = pd.Panel(profile_xvel_data, 
                         major_axis=profile_nodes[profile], 
                         items=vel_mod_datetimes)
        
        dp_dynamic = dp + eta
        profile_dp_dynamic = dp_dynamic[:,nodes]
        sites_dp_data[profile] = pd.DataFrame(profile_dp_dynamic, 
                                                index=sal_mod_datetimes, 
                                       columns=profile_nodes[profile])
        #storing profile data in hdf5 file
        #hdf5_storage = pd.io.pytables.HDFStore(hdf5_file)
        #hdf5_storage['salinity'] = sites_sal_data[profile]
        #hdf5_storage['x_vel'] = sites_xvel_data[profile]
        #hdf5_storage['depth'] = sites_dp_data[profile]
        #hdf5_storage.close()

    depth_averaged_vel = sites_xvel_data[profile].mean(axis=2).T
    weighted_area_averaged_vel = (depth_averaged_vel * weights[profile]).sum(axis=1) / \
                                weights[profile].sum()
    weighted_area_averaged_dp = (sites_dp_data[profile] * weights[profile]).sum(axis=1) / \
                                weights[profile].sum()
    
    flow = weighted_area_averaged_vel * weighted_area_averaged_dp * \
                channel_props.ix[profile, 'width']
    flow_cfs[profile] = flow * 1 / 0.0283

flow_cfs = pd.DataFrame(flow_cfs)
flow_cfs.to_csv(flow_file, float_format='%10.2f', header=True, 
                index_label='datetime')
flow_cfs.plot()

plt.show()
        
        
                            
        
        
        
        
        
    
    

        
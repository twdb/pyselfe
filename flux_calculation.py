# -*- coding: utf-8 -*-
"""
Created on Thu Mar 28 14:22:31 2013

@author: SNegusse
"""
import os
import sys
sys.path.append('/home/snegusse/pyselfe/')

import numpy as np 
import pandas as pd

import pyselfe

sfile = 1
nfiles = 2
mod_start_datetime = pd.datetime(2008,8,24,0,0)
no_dow_start_datetime = pd.datetime(2008,9,23,0,0)
density = 1020.

tidal_period = '1490min'
flux_calc_start_date = pd.datetime(2008,9,20,19)
flux_calc_end_date = pd.datetime(2008,9,25)   

base_dir = '/home/snegusse/modeling/brazos_river/calibration_20080824'
mod_dirs = {'base_case': os.path.join(base_dir, 'base_case', 'outputs')}
#'fine': os.path.join(base_dir, 'grid_convergence', 'fine_grid_tvd',
#                                'outputs')}
sal_init_file = str(sfile) + '_salt.63'
vel_init_file = str(sfile) + '_hvel.64'

mod_initial={}
    

sites_xy = pd.DataFrame(np.array([[246469.00 , 3226774.00, np.nan],
                                  [  251473.33,  3216482.68, np.nan],
                                  [  258762.88,  3213500.45, 62.],
                                  [  268056.17, 3204466.99, 103.],                                  
                                  [  268006.08, 3204401.47, 103.],
                                  [  267495.05,  3198979.43, np.nan],
                                  [  276812.42, 3205896.17, np.nan] ,
                                  [  2730 , 3203521.88, np.nan]]), 
                            index=['bz1','bz2','bz3','bz4','bz5',
                                   'bz6u','icfr','frpt'], 
                                   columns=['x','y','orientation'])
brazos_sites = sites_xy.ix[['bz3','bz5'], ['x', 'y']]
sites_sal_data = {}
sites_uvel_data = {}
sites_vvel_data = {}
sites_dp_data = {}
mod_t = {}

for i in mod_dirs.keys():
    hdf5_file = os.path.join(base_dir, mod_dirs[i], i + '_' + \
                            'mod_data' + '.h5')
    if os.path.exists(hdf5_file):
        hdf5_storage = pd.io.pytables.HDFStore(hdf5_file, mode='r')
        sites_sal_data[i] = hdf5_storage['salinity']
        sites_uvel_data[i] = hdf5_storage['u_vel']
        sites_vvel_data[i] = hdf5_storage['v_vel']
        sites_dp_data[i] = hdf5_storage['depth']
    else:
        mod_initial[i] = (pyselfe.Dataset(os.path.join(mod_dirs[i],
                        sal_init_file)), pyselfe.Dataset(os.path.join(mod_dirs[i], 
                                                                vel_init_file)),)
        [sal_t, tstep, eta, dp, sal_data] = \
        mod_initial[i][0].read_time_series('salt.63', 
                                        xy=brazos_sites.values, 
                                        nfiles=nfiles, datadir=mod_dirs[i],
                                        sfile=sfile)
        [vel_t, tstep, eta, dp, vel_data] = \
        mod_initial[i][1].read_time_series('hvel.64', 
                                xy=brazos_sites.values, 
                                nfiles=nfiles, datadir=mod_dirs[i],
                                sfile=sfile)  
        sal_mod_datetimes = [mod_start_datetime + pd.datetools.Second(dt)
                            for dt in sal_t]
        vel_mod_datetimes = [mod_start_datetime + pd.datetools.Second(dt)
                    for dt in vel_t]
        sites_sal_data[i] = pd.Panel(sal_data[:,:,:,0], 
                                         major_axis=brazos_sites.index, 
                                         items=sal_mod_datetimes)
        sites_uvel_data[i] = pd.Panel(vel_data[:,:,:,0], 
                                 major_axis=brazos_sites.index, 
                                 items=vel_mod_datetimes)
        sites_vvel_data[i] = pd.Panel(vel_data[:,:,:,1], 
                         major_axis=brazos_sites.index, 
                         items=vel_mod_datetimes)
        
        
        dp_dynamic = dp + eta
        sites_dp_data[i] = pd.DataFrame(dp_dynamic, index=sal_mod_datetimes, 
                                       columns=brazos_sites.index.values)
        hdf5_storage = pd.io.pytables.HDFStore(hdf5_file)
        hdf5_storage['salinity'] = sites_sal_data[i]
        hdf5_storage['u_vel'] = sites_uvel_data[i]
        hdf5_storage['v_vel'] =  sites_vvel_data[i]
        hdf5_storage['depth'] = sites_dp_data[i]
        hdf5_storage.close()

for site in brazos_sites.index:
    site_sal_dict = {}
    site_uvel_dict = {}
    site_vvel_dict = {}
    site_uprime_dict = {}
    site_dp_dict = {}
    site_salt_flux = {}
    for sim in sites_sal_data.keys():
        site_sal_dict[sim] = sites_sal_data[sim].xs(site).T
        site_uvel_dict[sim] = sites_uvel_data[sim].xs(site).T
        site_vvel_dict[sim] = sites_vvel_data[sim].xs(site).T
        site_uprime_dict[sim] =  site_uvel_dict[sim] * \
        np.cos(sites_xy.ix[site, 'orientation'] * np.pi / 180.) - \
        site_vvel_dict[sim] * np.sin(sites_xy.ix[site, 'orientation'] * \
                                    np.pi / 180.) 
        site_dp_dict[sim] = sites_dp_data[sim][site]
        depth_avg_vel = site_uprime_dict[sim].mean(axis=1)
        depth_avg_sal = site_sal_dict[sim].mean(axis=1)
        site_flux_params = pd.DataFrame({'salinity': depth_avg_sal,
                                              'velocity': depth_avg_vel,
                                              'depth': site_dp_dict[sim]})
        site_flux_params = site_flux_params[flux_calc_start_date:\
                                                flux_calc_end_date]
        tidal_avg_flux_param = site_flux_params.resample(tidal_period)
        tidal_avg_flux_param = tidal_avg_flux_param[:-1]
        site_salt_flux[sim] = tidal_avg_flux_param.prod(axis=1) * density
        
        
        
                            
        
        
        
        
        
    
    

        
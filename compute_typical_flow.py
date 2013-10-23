# -*- coding: utf-8 -*-
"""
Created on Tue May 14 13:51:59 2013

@author: snegusse
"""

import os
import platform

import pandas as pd

import sonde.quantities as sq


def cfs_to_cms(flow):
    flow = flow * sq.cfs
    flow.units = sq.cms
    return flow.magnitude

if platform.system() == 'Linux':
    data_dir = '/T/BaysEstuaries/USERS/SNegusse/Brazos/Hydrology/gaged/'

usgs_flow_filename = '1967_2009_usgs_daily_streamflow.txt'
usgs_flow_file = os.path.join(data_dir, usgs_flow_filename)

names = ['agency', 'site_code', 'dates', 'flow', 'qa_status_fl', 'water_level',
         'qa_status_wl']
flow_data = pd.read_csv(usgs_flow_file, sep='\s*', parse_dates=[2], index_col=2, 
                         skiprows=pd.np.arange(31), names=names)
flow_data['flow'] = cfs_to_cms(flow_data['flow'].values) 
monthly_grouped = flow_data['flow'].groupby(lambda d: d.month)

aggregated_monthly_mean_flow = monthly_grouped.mean()
aggregated_monthly_mad_flow = monthly_grouped.mad()
aggregated_monthly_median_flow = monthly_grouped.quantile(0.5)
abs_devs = lambda group: pd.np.abs(group - group.quantile(.5))
abs_dev_flow = transformed_flow =  monthly_grouped.transform(abs_devs)
aggregated_monthly_medad_flow = abs_dev_flow.groupby(lambda d: d.month).quantile(0.5)


yearly_monthly_mean_flow = flow_data['flow'].resample('M', how='mean')
yearly_monthly_median_flow = flow_data['flow'].resample('M', how='median')


mean_normed_dev_dict = {}
median_normed_dev_dict = {}
years_of_record = pd.np.unique(flow_data.index.year)
for year in years_of_record[1:]:
    monthly_mean_of_year = yearly_monthly_mean_flow.ix[pd.datetime(year,1,1):\
                                                       pd.datetime(year,12,31)]
    monthly_median_of_year = yearly_monthly_median_flow.ix[pd.datetime(year,1,1):\
                                                       pd.datetime(year,12,31)]                                                       
    mean_monthly_normed_dev = pd.np.abs((monthly_mean_of_year.values - \
                                   aggregated_monthly_mean_flow.values) / \
                                   aggregated_monthly_mad_flow.values)
    median_monthly_normed_dev = pd.np.abs((monthly_median_of_year.values - \
                                   aggregated_monthly_median_flow.values) / \
                                   aggregated_monthly_medad_flow.values)                                   
    mean_normed_dev_dict[year] = mean_monthly_normed_dev.sum()
    median_normed_dev_dict[year] = median_monthly_normed_dev.sum()
    

mean_normed_dev_series = pd.Series(mean_normed_dev_dict) 
mean_normed_dev_series.sort()

median_normed_dev_series = pd.Series(median_normed_dev_dict) 
median_normed_dev_series.sort()

mean_year_ranks = pd.Series(pd.np.arange(1,mean_normed_dev_series.size+1), 
                              index=mean_normed_dev_series.index)
median_year_ranks = pd.Series(pd.np.arange(1,median_normed_dev_series.size+1), 
                              index=median_normed_dev_series.index)
                              
mean_rank_and_dev = pd.DataFrame({'rank': mean_year_ranks, 
                                  'normed_dev':mean_normed_dev_series})

median_rank_and_dev = pd.DataFrame({'rank': median_year_ranks, 
                                  'normed_dev':median_normed_dev_series})






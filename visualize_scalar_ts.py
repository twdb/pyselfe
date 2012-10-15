#imports
import os
import sys
import ctypes

flags = sys.getdlopenflags()
sys.setdlopenflags(flags|ctypes.RTLD_GLOBAL)

import numpy as np
from pyproj import Proj
from datetime import datetime, timedelta
from dateutil import tz
import pandas
import matplotlib
#matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pyselfe

sys.setdlopenflags(flags)



tcoon_zone = tz.gettz('UTC')
utc_6 = tz.gettz('UTC-6')
start_date = datetime(2000,1,1,0,0,0,0, utc_6)
end_date = datetime(2001,1,1,0,0,0,0, utc_6)
#start_date.replace(tzinfo=utc_6)

def mk_tcoon_date(text):
    utc = datetime.strptime(text.strip('"'), '%m-%d-%Y %H%M')
    utc = utc.replace(tzinfo=tcoon_zone)
    return utc.astimezone(utc_6)
def skill(xm,x0):
    """ calculate skill based on NOAA paper
        xm is model
        x0 is observation or a selected base model
    """
    return (1 - ((xm - x0)**2).sum() / ((np.abs(xm - x0.mean()) + np.abs(x0 - x0.mean()))**2).sum())
    
def rmse(xm,x0):
    """
    calculate rmse
    """
    return np.sqrt(((xm-x0)**2).mean())

def reindex(obs, mod):
    """ reindexes two pandas series by dates on which both observation and model data exists
    """
    r_mod = mod.reindex(obs.index).dropna()
    r_obs = obs.reindex(mod.index).dropna()
    return r_obs, r_mod

def calc_metrics(obs, mod):
    """
    calc all metrics
    """
    obs1, mod1 = reindex(obs, mod)
    xm = mod1.values
    x0 = obs1.values

    return [rmse(xm,x0), skill(xm,x0)]

mon_sites_file = '../field_data/corpus_station_list.csv'
selfe_data_dir = '/home/snegusse/modeling/corpus_christi_bay/laquinta_current_modeling/depth_sensitivty/47ft/windon/outputs/'

mon_sites = np.genfromtxt(mon_sites_file, dtype=None, names=True, delimiter=',', skip_header=1)

#convert from latlon to utm14
p = Proj(proj='utm',zone=14,ellps='WGS84')
xy = np.array(p(mon_sites['DDLon'], mon_sites['DDLat'])).transpose()

#initialize model data readers
selfe = pyselfe.Dataset(selfe_data_dir + '1_salt.63', nfiles=7)

for site, xy in zip(mon_sites, xy):
    print 'processing site: ', site['Name']
    pd = []
    if 'tc0' in site['Name']:
        data = np.genfromtxt('../field_data/' + site['Name']+'.csv', delimiter=',',
                             names='datetime,water_level,water_temperature',
                             dtype=[datetime, np.float, np.float],
                             missing_values='NA',
                             converters={'datetime':mk_tcoon_date})
        d = {'water_level': data['water_level'],
             'water_temperature': data['water_temperature']}
        pd = pandas.DataFrame(d, index=data['datetime'])
    elif 'tcSALT' in site['Name']:
        data = np.genfromtxt('../field_data/' + site['Name']+'.csv', delimiter=',',
                             names='datetime,water_temperature,salinity',
                             dtype=[datetime, np.float, np.float],
                             missing_values='NA',
                             converters={'datetime':mk_tcoon_date},
                             usecols=(0,2,3))
        d = {'water_temperature': data['water_temperature'],
             'salinity': data['salinity']}
        pd = pandas.DataFrame(d, index=data['datetime'])
    elif 'twdb' in site['Name']:
        data = np.genfromtxt('../field_data/' + site['Name'] + '.txt', delimiter='',
                             names='Y,m,d,hh,mm,water_temperature,salinity,water_level',
                             dtype=[np.float, np.float, np.float,
                                    np.float,np.float, np.float,
                                    np.float, np.float],
                             usecols=(0,1,2,3,4,5,8,10),
                             comments='#', missing_values=-9.99)
        field_dates_raw = np.array([datetime(int(Y), int(m), int(d), int(hh),
                                                  int(mm), 0, 0, utc_6) for Y,m,d,hh,mm in
                                zip(data['Y'],data['m'],data['d'],data['hh'],data['mm'])])
        field_dates, duplicate_index = np.unique(field_dates_raw, return_index=True)
        print (field_dates_raw.size - duplicate_index.size).__str__() + "records removed."
        d = {'water_level': data['water_level'][duplicate_index],
             'water_temperature': data['water_temperature'][duplicate_index],
             'salinity': data['salinity'][duplicate_index]}
        pd = pandas.DataFrame(d, index=field_dates)
    elif 'model' in site['Name']:
        pass
    else:
        continue


        
                                
                             
    params = site['Type'].split()
#    params = ['salinity', 'water_level']

    #salinity mid level
    #sal_series=[]

    if 'salinity' in params:
        print 'reading selfe salinity data'
        sal = selfe.read_time_series_xy('salt.63', xy[0], xy[1])
        dates = [start_date + timedelta(seconds=int(ts)) for ts in sal[:-1,0]]
        selfe_sal_ts = pandas.Series(sal[:-1,1], index=dates).dropna()

        if not 'model' in site['Name']:
            obs_sal_ts = pd['salinity'].dropna()
            idx = (obs_sal_ts.index > start_date) * (obs_sal_ts.index < end_date)
            obs_sal_ts = obs_sal_ts[idx]

        fig = plt.figure()
        ax = fig.add_subplot(111)
        plt.title('Salinity at' + ' ' + site['Name'])
        selfe_sal_plt = ax.plot_date(selfe_sal_ts.index, selfe_sal_ts.values, 'b-')
        if not 'model' in site['Name']:
            obs_sal_plt = ax.plot_date(obs_sal_ts.index, obs_sal_ts.values, 'r.', markersize=4)
        ax.set_xlim(start_date, end_date)
        ax.set_ylim(0, 50)
        ax.set_ylabel('Salinity, psu')
#       plt.legend(["selfe", "fvcom", "utbest", "observed"])
        ax.grid(True)
        fig.autofmt_xdate()
#        plt.savefig(site['Name'] + '_salinity.png')

    if 'water_level' in params:
        print 'reading selfe water level data'
        sal, eta = selfe.read_time_series_xy('salt.63', xy[0], xy[1], return_eta=True)
        dates = [start_date + timedelta(seconds=int(ts)) for ts in eta[:-1,0]]
        selfe_eta_ts = pandas.Series(eta[:-1,1], index=dates).dropna()

        etaplotstart = datetime(2000,12,6,0,0,0)
        etaplotend = datetime(2000,12,21,0,0,0)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        
        plt.title('Water Surface Elevation at' + ' ' + site['Name'])
        selfe_eta_plt = ax.plot_date(selfe_eta_ts.index, selfe_eta_ts.values, 'b-')
        if not 'model' in site['Name']:
            obs_eta_plt = ax.plot_date(obs_eta_ts.index, obs_eta_ts.values, 'r.', markersize=4)
        ax.set_ylim(-1, 1)
        ax.set_xlim(start_date, end_date)
        ax.set_ylabel('water surface elevation above MSL, m')
        ax.grid(True)
#        ax.legend(["selfe", "fvcom", "utbest", "observed"])
        fig.autofmt_xdate()
#        plt.savefig(site['Name'] + '_2000_eta.png')
plt.show()

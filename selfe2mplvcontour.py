import os
import datetime

import numpy as np
import scipy
import pandas
import matplotlib
import matplotlib.pylab as plt
import matplotlib.ticker as ticker

import shapefile
import pyselfe_hdf
import pyhat


start_date = datetime.datetime(2008,8,24,0,0)
output_dir = '/home/snegusse/modeling/brazos_river/ascar_runs/aug-dec08-Run75/outputs'
output_file = os.path.join(output_dir, '1_salt.63')
brazos_curtain_file = os.path.join(output_dir, 'brazos-centerline.shp')

def read_curtain_shapefile(curtain_shapefile):
    line = shapefile.Reader(curtain_shapefile)
    curtain_coords = np.array([s.points for s in line.shapes()])
    cx = curtain_coords[:,:,0].ravel()
    cy = curtain_coords[:,:,1].ravel()
    return cx, cy

def uniform_points_curtain(cx, cy, s_spacing):
    """ Function for extracting points uniformly spaced on curtain at s_spacing.
    Curtain is the spline defined by the points cx and cy
    """
    curtain = pyhat.Coord_SN(cx, cy)
    curt_s, cur_n = curtain.transform_xy_to_sn(cx, cy)
    curt_len = curt_s.max()
    unif_s_coord = np.arange(0, curt_len, s_spacing)
    unif_n_coord  = np.zeros(unif_s_coord.size)
    xcoord_curt_pts, ycoord_curt_pts = curtain.transform_sn_to_xy(unif_s_coord,
                                                               unif_n_coord)
    return xcoord_curt_pts, ycoord_curt_pts, unif_s_coord

def vertical_profile(model,param,curtain_pts=None, start_date=None, nf=1,
                     tofile=False, profile_file=None,**kwargs):
    """extracting selfe model outputs along a line/curtain.
    model_output: pyselfe Dataset class object or selfe output file to read and
    extract such as salt.63, hvel.64
    curtain_coor: 2d array of shape [x,y] of points defining the curtain.
    For matplotlib visualization, the points should be uniformly spaced along s.
    """
    if isinstance(model, pyselfe_hdf.Dataset):
        [time_steps, water_level, inital_depth,  vert_prof_data] = \
                     model.read_time_series(param, xy=curtain_pts,
                                                       nfiles=nf)
    elif type(model) == str:    
        model = pyselfe_hdf.Dataset(model)
        [time_steps, water_level, initial_depth, vert_prof_data] = \
                     model.read_time_series(param, xy=curtain_pts,
                                                       nfiles=nf)
    if start_date:
        model_datetimes = np.array([start_date + pandas.datetools.Second(dt) for
                                    dt in time_steps])
    water_depth = water_level + initial_depth

    if tofile == True:
        profile_storage = pandas.io.pytables.HDFStore(os.path.join(output_dir,
                                                                   profile_file))
        model_dt_series = pandas.Series(model_datetimes)
        if vert_prof_data.shape[3] == 1:
            vert_prof_data = pandas.Panel(vert_prof_data[:,:,:,0])
        water_depth = pandas.DataFrame(water_depth)
        curtain_pts = pandas.DataFrame(curtain_pts)
        profile_storage['model_datetimes'] = model_dt_series
        profile_storage['vert_profile_data'] = vert_prof_data
        profile_storage['water_depth'] = water_depth
        profile_storage['curtain_points'] = curtain_pts       
        profile_storage['sigma_levels'] = model.slevels
        profile_storage['uni_s_coords'] = curtain_pts[:,2]
        profile_storage.close()
        
    return model_datetimes, vert_prof_data, water_depth, model.slevels

def interp_vert_prof_s_to_z(vert_profile_data_s, water_depth=None,
                            sigma_levels=None, z_interval=1, s_coord=None):
    maximum_water_depth = water_depth.max()
    uniform_z_levels = np.arange(-maximum_water_depth, 0., z_interval)
    vert_prof_data_z = np.zeros((uniform_z_levels.size, s_coord.size))
    for node in vert_profile_data_s.shape[1]:
        node_z_levels = sigma_levels * water_depth[node]
        vert_prof = scipy.interp(uniform_z_levels, node_z_levels,
                                 vert_profile_data_s[node,:],
                                 left=np.nan, right=np.nan)
        vert_prof_data_z[:,node] = vert_prof
    return vert_prof_data_z, uniform_z_levels

brazos_cx, brazos_cy = read_curtain_shapefile(brazos_curtain_file)
[x_coor, y_coor, s_coor] = uniform_points_curtain(brazos_cx, brazos_cy, 1000)
xy_coors = np.column_stack((x_coor, y_coor))
xy_coors = xy_coors[::4,:]
[time_step, brazos_vprof_ts, dp, s_lev] = vertical_profile(output_file, 'salt.63',
                                                curtain_pts=xy_coors,
                                                start_date=start_date, nf=2,
                                                tofile=False)
i = 0
for dt in time_step:
    sal_vprofile_s = brazos_vprof_ts[i,:,:]
    brazos_sal_vprofile_z, z_levels = interp_vert_prof_s_to_z(sal_vprofile_s,
                                                       water_depth=dp[i,:],
                                                       sigma_levels=s_lev,
                                                       z_interval=1,
                                                       s_coord=s_coor)

    fig = plt.figure()
    plt.title('salinity vertical profile')
    origin='lower'
    cmap = plt.cm.jet
    cmap.set_over('red', 1.0)
    cmap.set_under('blue',1.0)
    ax = fig.add_subplot(111)
    locator=ticker.MaxNLocator(10)
    locator.create_dummy_axis()
    locator.set_bounds(0, 35)
    color_levels=locator()

    sal_vcontour = plt.contourf(s_coor, z_levels, brazos_sal_vprofile_z,
                                color_levels, cmap=cmap, extend='both',
                                origin=origin)
    plt.show()

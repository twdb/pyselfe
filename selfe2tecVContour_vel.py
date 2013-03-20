#!/usr/bin/python
#####################################################
## An python program to extract data along a profile
## line from the selfe binary and generate tecplot
## output files to plot a vertical profile contour map
## 
## selfe2tecVProfile.py <datadir> <tecfile> <param> <profilelinefile> <nfiles> 
##
## param = salt.63,temp.63 etc
#####################################################
## Author : Dharhas Pothina
## Last Modified : 20080611
## Requires : 
##     No Other Scripts Required
#####################################################

programname = "selfe2tecVContour.py";

import os
import sys
import platform

import numpy as np
import shapefile

sys.path.append('/home/snegusse/pyselfe')        
import pyselfe

def read_curtain_shapefile(curtain_shapefile):
    line = shapefile.Reader(curtain_shapefile)
    curtain_coords = np.array([s.points for s in line.shapes()])
    cx = curtain_coords[:,:,0].ravel()
    cy = curtain_coords[:,:,1].ravel()
    return cx, cy
    
def calc_channel_orientation(cx, cy):
    cx_delta = (cx[:-1] - cx[1:])
    cy_delta = (cy[:-1] - cy[1:])
    segment_length = np.hypot(cx_delta, cy_delta)
    cos_theta = cx_delta / segment_length
    theta_deg = np.arccos(cos_theta) * 180. / np.pi
    sin_theta = cy_delta / segment_length
    neg_sin_theta_ind = sin_theta < 0.
    theta_deg[neg_sin_theta_ind] *= -1
    theta_deg *= -1
    return theta_deg
    

#read in command line variables
if platform.system() == 'Linux':
    base_dir = '/home/snegusse/brazos_river/'

data_dir = os.path.join(base_dir, 'calibration_20080824','base_case',
                        'outputs')
tec_filename = 'cal_test.dat'
curtain_filename = 'brazos_centerline.shp'  

curtain_file = os.path.join(data_dir, curtain_filename)
tec_file = os.path.join(data_dir, tec_filename)
param = 'hvel.64'
sfile = 1
nfile = 1

model = pyselfe.Dataset(os.path.join(data_dir, str(sfile) + '_' + param))


# Read in xy/node locations of profile line
cx, cy = read_curtain_shapefile(curtain_file)
channel_orientation = calc_channel_orientation(cx, cy)

#take every third point and remove points upstream of bz2
cx = cx[::3][:30]
cy = cx[::3][:30]
xy = np.column_stack(cx, cy)
nxy = xy.shape[0]

# Read all time series data for set of xy
# level = nlevel - 1 because of zero indexing
[t,t_iter,eta,dp,data] = model.read_time_series(param,xy=xy, nfiles=nfile,
                                                datadir=data_dir, sfile=sfile)
# -----------------------------------------

#generate xz values for each timestep
sLevels = np.row_stack([-1.0,model.slevels])
Z = np.zeros((t.size,nxy,model.nlevels))/0.0
Z0 = np.zeros((nxy,model.nlevels))/0.0
for time in range(t.size):
    H = dp + eta[time,:]
    for node in range(nxy):
        Z[time,node,:] = H[node] * (1+sLevels) - dp[node]
        Z0[node,:] = dp[node]*sLevels 

#Make this actual xy distances later
D=[]
D.append(0)
dist = 0
for i in range(1, nxy):
    dist = dist + np.hypot((xy[i,0]-xy[i-1,0]),(xy[i,1]-xy[i-1,1]))
    D.append(dist)
    
X=[]
for lev in range(model.nlevels):
    X.append(D)

X = np.array(X).transpose()
#X = X.transpose().ravel()
#X = X.ravel()


header = []
header.append('TITLE = Selfe Vertical Profile : ' + (model.version).strip() + \
                ', ' + curtain_filename)

variables = {'salt.63': '\"Sal\"',
             'temp.63': '\"Temp\"',
             'vert.63': '\"W\"',
             'hvel.64': '\"Vel\"'}[(model.var_type).strip()]

header.append('Variables = \"X\", \"Z\", ' + variables + ', \"W\"')
zonetype = 'I=' + nxy.__str__() \
              + ', J=' + model.nlevels.__int__().__str__() \
              + ', DATAPACKING=POINT'
header.append('ZONE T=\"0.0\"' + zonetype + ', SOLUTIONTIME=0.0')

#Write ZONE 1
fid = open(tec_file,'w')
for txt in header:
    fid.write(txt + '\n')

for j in range(model.nlevels):
    for i in range(nxy):
        fid.write(X[i,j].__str__() + ' ' + Z0[i,j].__str__() + ' ' + (Z0[i,j]*0.0).__str__() +
                  ' ' + (Z0[i,j]*0.0).__str__() + '\n')
    
#Write Timesteps
for dt in range(t.size):
    zone = 'ZONE T=\"' + t[dt].__str__() + '\", ' + zonetype + ', SOLUTIONTIME= ' +t[dt].__str__() +'\n'
    fid.write(zone)
    Z0=Z[dt,:,:]
    for j in range(model.nlevels):
        for i in range(1,nxy):
            vx_en = data[dt,i,j,0]
            vy_en = data[dt,i,j,1]
            vx_xy = vx_en * np.cos(channel_orientation[i]) - vy_en * \
                    np.sin(channel_orientation[i]) 
            vy_xy = 0
            fid.write(X[i,j].__str__() + ' ' + Z0[i,j].__str__() + ' ' + (vx_xy).__str__() + ' '
                      + 0.0.__str__() + '\n')
fid.close()
#split into rows of 10
#rows = X.size/10
#remain = X.size-10*rows
#end = X.size

#savetxt(fid,X[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#X[10*rows:end].tofile(fid,sep=" ",format="%f")
#fid.write('\n')

#Z0=Z0.transpose().ravel()
#savetxt(fid,Z0[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#Z0[10*rows:end].tofile(fid,sep=" ",format="%f")
#fid.write('\n')

#dummy = Z0*0.0
#set all other vars =0 at t=0
#for i in range(model.flagSv):
#    savetxt(fid,dummy[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#    #fid.write('\n')
#    dummy[10*rows:end].tofile(fid,sep=" ",format="%f")
#    fid.write('\n')
    
#fid.write('\n')

#for i in range(t.size):
#    zone = 'ZONE T=\"' + t[i].__str__() + '\", ' + zonetype + ', SOLUTIONTIME= ' +t[i].__str__() +'\n'
#    fid.write(zone)
    
#    savetxt(fid,X[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#    X[10*rows:end].tofile(fid,sep=" ",format="%f")
#    fid.write('\n')
    
#    Z0=Z[i,:,:].transpose().ravel()
#    savetxt(fid,Z0[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#    Z0[10*rows:end].tofile(fid,sep=" ",format="%f")
#    fid.write('\n')
    
#    for j in range(model.flagSv):
#        tmpdata=data[i,:,:,j].transpose()
#        savetxt(fid,tmpdata[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#        tmpdata[10*rows:end].tofile(fid,sep=" ",format="%f")
#        fid.write('\n')



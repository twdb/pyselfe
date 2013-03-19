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

# load required modules
import struct
import sys
import subprocess
from numpy import *
from scipy import *
from pylab import *
from string import *
import datetime

#This function takes Bash commands and returns them
def runBash(cmd):
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    out = p.stdout.read().strip()
    return out  #This is the stdout from the shell command

if len(sys.argv)==1 or sys.argv[1]=='help' or sys.argv[1]=='-help' or sys.argv[1
]=='--help' :
    location=runBash("which " + programname)  
    message = runBash("awk \'/^##/ {print $0}\' < " + location);
    sys.exit(message)  

#sys.path.append('/home/snegusse/bin')        
import pyselfe

#read in command line variables
datadir=sys.argv[1]
tecfile=sys.argv[2]
param=sys.argv[3]
profilefile=sys.argv[4]
nfile=int(sys.argv[5])

model = pyselfe.Dataset(datadir + '/1_'+param)

# Read in xy/node locations of profile line

xy = loadtxt(profilefile,skiprows=7,usecols=(0,1),unpack=True)
nxy = xy.shape[1]
xy=xy.transpose()

# Read all time series data for set of xy
# level = nlevel - 1 because of zero indexing
[t,t_iter,eta,dp,data] = model.read_time_series(param,xy=xy,nfiles=nfile,datadir=datadir)
# -----------------------------------------

#generate xz values for each timestep
sLevels = hstack([-1.0,model.slevels])
Z = zeros((t.size,nxy,model.nlevels))/0.0
Z0 = zeros((nxy,model.nlevels))/0.0
for time in range(t.size):
    H = dp + eta[time,:]
    for node in range(nxy):
        Z[time,node,:] = H[node] * (1+sLevels) - dp[node]
        Z0[node,:] = dp[node]*sLevels 

#Make this actual xy distances later
D=[]
D.append(0)
dist = 0
for i in range(1,xy.shape[0]):
    dist = dist + sqrt((xy[i,0]-xy[i-1,0])**2 + (xy[i,1]-xy[i-1,1])**2)
    D.append(dist)
    
X=[]
for lev in range(model.nlevels):
    X.append(D)

X = array(X).transpose()
#X = X.transpose().ravel()
#X = X.ravel()


header = []
header.append('TITLE = Selfe Vertical Profile : ' + strip(model.version) + ', ' + profilefile)

variables = {'salt.63': '\"Sal\"',
             'temp.63': '\"Temp\"',
             'vert.63': '\"W\"',
             'hvel.64': '\"Vel\"'}[strip(model.var_type)]

header.append('Variables = \"X\", \"Z\", ' + variables + ', \"W\"')
zonetype = 'I=' + nxy.__str__() \
              + ', J=' + model.nlevels.__int__().__str__() \
              + ', DATAPACKING=POINT'
header.append('ZONE T=\"0.0\"' + zonetype + ', SOLUTIONTIME=0.0')

#Write ZONE 1
fid = open(tecfile,'w')
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
        for i in range(nxy):
            vx_en = data[dt,i,j,0]
            vy_en = data[dt,i,j,1]
            vx_xy = vy_en*cos(np.pi*12.5/180)+vx_en*sin(np.pi*12.5/180)
            vy_xy = vy_en*sin(np.pi*12.5/180)+vx_en*cos(np.pi*12.5/180)
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



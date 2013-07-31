#!/usr/bin/python
#####################################################
## An python program to extract a level from the selfe 
## binary and generate tecplot output files
## 
## selfe2tec2D.py <datadir> <tecfile> <param> <nlevel> <nfiles> 
##
## param = elev.61,hvel.63 etc
#####################################################
## Author : Dharhas Pothina
## Last Modified : 20080611
## Requires : 
##     No Other Scripts Required
#####################################################

programname = "selfe2tec2D.py";

# load required modules
import os
import struct
import sys
sys.path.append('/home/snegusse/test')
from string import strip

from numpy import *
from scipy import *
import pandas 

import pyselfe

if len(sys.argv)==1 or sys.argv[1]=='help' or sys.argv[1]=='-help' or sys.argv[1
]=='--help' :
    location=runBash("which " + programname)  
    message = runBash("awk \'/^##/ {print $0}\' < " + location);
    sys.exit(message)  
    


#read in command line variables
datadir=sys.argv[1]
tecfile=sys.argv[2]
param=sys.argv[3]
nlevel=sys.argv[4]
nfile=int(sys.argv[5])

model = pyselfe.Dataset(datadir + '/1_'+param)

# level = nlevel - 1 because of zero indexing
try:
    nlevel = int(nlevel)
    [t,t_iter,eta,dp,data] = model.read_time_series(param,levels=nlevel-1,
                                                        nfiles=nfile,
                                                        sfile=1,
                                                        datadir=datadir)
except ValueError:
    if nlevel == 'all':
        [t,t_iter,eta,dp,data] = model.read_time_series(param,
                                                        nfiles=nfile,
                                                        sfile=1,
                                                        datadir=datadir)
        data = data[:,:,1:,:].mean(axis=2)
                                                    

header = []
header.append('TITLE = Selfe : ' + strip(model.version))

variables = {'elev.61': '\"eta\"',
             'hvel.64': '\"U\", \"V\"',
             'salt.63': '\"Sal\"',
             'temp.63': '\"T\"',
             'vert.63': '\"W\"',
             'prcp.61': '\"Precip\"',
             'evap.61': '\"Evap\"',
             'wind.62': '\"WX\", \"WY\"'}[strip(model.var_type)]

header.append('Variables = \"X\", \"Y\", \"ETA\", \"DP\", ' + variables)
zonetype = 'NODES=' + model.np.__int__().__str__() \
              + ', ELEMENTS=' + model.ne.__int__().__str__() \
              + ', DATAPACKING=BLOCK, ZONETYPE=FETRIANGLE'
header.append('ZONE T=\"0.0\"' + zonetype + ', SOLUTIONTIME=0.0')

fid = open(tecfile,'w')
for txt in header:
    fid.write(txt + '\n')

#split into rows of 10
rows = model.np/10
remain = model.np-10*rows
end = model.np

savetxt(fid,model.x[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
model.x[10*rows:end].tofile(fid,sep=" ",format="%f")
fid.write('\n')

savetxt(fid,model.y[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#fid.write('\n')
model.y[10*rows:end].tofile(fid,sep=" ",format="%f")
fid.write('\n')

dummy=zeros(model.np)

# at t=0 eta=0
savetxt(fid,dummy[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#fid.write('\n')
dummy[10*rows:end].tofile(fid,sep=" ",format="%f")
fid.write('\n')

#change this to dp+eta later? Since dp is a constant
savetxt(fid,model.dp[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#fid.write('\n')
model.dp[10*rows:end].tofile(fid,sep=" ",format="%f")
fid.write('\n')

#set all other vars =0 at t=0
for i in range(model.flag_sv):
    savetxt(fid,dummy[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
    #fid.write('\n')
    dummy[10*rows:end].tofile(fid,sep=" ",format="%f")
    fid.write('\n')
    
fid.write('\n')

# Save elem connectivity list
savetxt(fid,model.elem.reshape(model.elem.size/3,3),delimiter=' ',fmt="%d")
fid.write('\n')

for i in range(t.size):
    tday = t[i]/86400.00
    zone = 'ZONE T=\"' + tday.__str__() + '\", ' + zonetype + ',VARSHARELIST=([1,2,4]=1), CONNECTIVITYSHAREZONE=1, SOLUTIONTIME= ' +tday.__str__() +'\n'
    fid.write(zone)
    savetxt(fid,eta[i,:][0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
    eta[i,:][10*rows:end].tofile(fid,sep=" ",format="%f")
    fid.write('\n')

#    dp = eta[i,:] + model.dp
#    savetxt(fid,dp[i,:][0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
#    dp[i,:][10*rows:end].tofile(fid,sep=" ",format="%f")
#    fid.write('\n')

    for j in range(model.flag_sv):
        if (data.ndim==4):
            data = data.reshape(data.shape[0],data.shape[1],data.shape[3])
        tmpdata=data[i,:,j]
#        print tmpdata.shape
#        print tmpdata[0:10*rows].shape
        savetxt(fid,tmpdata[0:10*rows].reshape(rows,10),delimiter=' ',fmt="%f")
        tmpdata[10*rows:end].tofile(fid,sep=" ",format="%f")
        fid.write('\n')

fid.close()

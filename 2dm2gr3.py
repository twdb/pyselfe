# -*- coding: utf-8 -*-
'''
Created on Tue Dec 14 08:20:33 2010

@author: snegusse
Script for converting SMS' 2dm format to SELFE gr3

Usage:
Input arguments: 
1. Directory where the *.2dm and *.bc files are located.
2. number_of_boundaries: This is the total number of the boundary nodestrings
in SMS which can also be found in the *.bc file , at the bottom - the index
of the last boundary
3. boundarytype dictionary: This maps the different nodestring indices 
in *.bc file (the keys) to the respective SELFE boundary types and the names are assigned
here which will be printed out in hgrid.gr3. 
The first value is used to group the different boundaries and control the order
they will be printed in hgrid.gr3. 
The second value will be printed as the header line in the boundary list in hgrid.gr3.
Note in SMS all external land and island boundaries are designated same index.
'''
import os
import platform 

import collections
import numpy as np
import glob

if platform.system() == 'Linux':
    grid_data_dir = '/T/BaysEstuaries/USERS/SNegusse/Grids/brazos_river/historical_geometry/post_realignment_no_giww'
else:
    grid_data_dir = 'T:\\BaysEstuaries\\USERS\\SNegusse\\Brazos\\input_for_joseph\\brazos_river_model_part2\\grid_no_giww'

number_of_boundaries = 4

grid_files = glob.glob(os.path.join(grid_data_dir, '*.2dm'))
#files = [os.path.join(dir, 'hgrid_1m_min.2dm')]

# historical scenarios with just Brazos and Ocean boundayr"
boundarytype = {1: ('river', 'brazos river'), 
                2: ('ocean', 'gom'),
                88: ('land', 'external land')}

"""
boundarytype = {1: ('river', 'brazos river'), 
                2: ('ocean', 'gom'),
                3: ('return', 'ups giww'),
                4: ('return', 'downs dow'),
                5: ('return', ' dow1'),
                6: ('return', 'dow23'),
                7: ('return', 'ups dow'),
                8: ('return', 'ups dow2'),
                99: ('land', 'external land')} 

boundarytype = {1: ('river', 'brazos river'), 
                2: ('river', 'san bernard'), 
                3: ('giww', 'giww-west'),
                4: ('ocean', 'gom'),
                5: ('giww', 'giww-east'),
                6: ('return', 'ups giww'),
                7: ('return', 'downs dow'),
                8: ('return', ' dow1'),
                9: ('return', 'dow23'),
                10: ('return', 'ups dow'),
                11: ('return', 'ups dow2'),
                88: ('land', 'external land'),                      
                99: ('land', 'island boundary'),}   
boundarytype = {1: ('river', 'brazos river'), 
                2: ('river', 'san bernard'), 
                3: ('discharge', 'dow outfall1'),
                4: ('discharge', 'dow outfall2n3'), 
                5: ('withdrawal', 'harris pump'),
                6: ('giww', 'giww-west'),
                7: ('giww', 'giww-east'),
                8: ('ocean', 'gom'),
                9: ('land', 'external land'),                      
                10: ('land', 'island boundary'),}   
               
boundarytype = {1: ('river', 'cedar'),
                2: ('river', 'bludwr'),
                3: ('river', 'cavasso'),
                4: ('river', 'copano'),
                5: ('river', 'mission'),
                6: ('river','aransas'),
                7: ('river', 'zero flow'),
                8: ('river', 'nueces'),
                9: ('powerplant', 'cpl powerplant outflow'),
               10: ('powerplant', 'cpl powerplant intake'),
               11: ('river', 'oso'),
               12: ('powerplant', 'bdavis powerplant outfall'),
               13: ('powerplant', 'bdavis powerplant intake'),
               14: ('river', 'cabal'),
               15: ('ocean', 'gom'),
               89: ('land', 'external land'),
               99: ('land', 'island boundary')}   

boundarytype = {1: ('river', 'sabine river'),
                2: ('river', 'neches river'),
                3: ('river', 'trinity river'),
                4: ('river', 'san jacinto river'),
                5: ('river', 'brazos river'),
                6: ('river','san bernard river'),
                7: ('river', 'colorado river'),
                8: ('river', 'tres palacios river'),
                9: ('river', 'lavaca river'),
                10: ('river','garcitas creek'),
                11: ('river', 'guadalupe river'),
                12: ('river', 'copano creek'),
                13: ('river', 'mission river'),
                14: ('river','aransas river'),
                15: ('river', 'nueces river'),
                16: ('river', 'oso creek'),
                17: ('river', 'los olmos'),
                18: ('river','rio grande river'),
                19: ('ocean', 'gulf of mexico'),                          
                888: ('land', 'external land'),
                999: ('land', 'island boundary')}
"""
for grid_file in grid_files:
    c = 0
    d = 0
    filename = grid_file.split(os.sep)[-1].split('.')[0] + '.gr3'
    fid = open(os.path.join(grid_data_dir,filename), 'w')
    
    f = open(grid_file,'r')
    two_dm = f.readlines()
    
    for line in two_dm:
        if line.split()[0] == 'ND':
            d = d+1
            depth = d.__str__() + ' ' +line.split()[2] + ' ' + line.split()[3] + ' ' + line.split()[4] + '\n'
            fid.write(depth)
            
    for line in two_dm:
        if line.split()[0] == 'E3T':
            c = c+1
            connectivity = line.split()[1] + ' ' + '3' + ' ' + line.split()[2] + ' ' + line.split()[3] + ' ' + line.split()[4] + '\n'
            fid.write(connectivity)

    if number_of_boundaries != 0:
        bc_filename = 'boundary.bc'
        f1 = open(os.path.join(grid_data_dir, bc_filename), 'r')
        bcfile = f1.readlines()
        
    
        stringlist = collections.defaultdict(list)
        i = 1
        stringlist[i] = [] 
    
        for line in bcfile:
            if line.split()[0] == 'GCL':
                stringlist[i] = np.append(stringlist[i],line.split()[1:])
                if np.int(stringlist[i][-1]) == -1:
                    stringlist[i] = stringlist[i][1:-1] 
                    i = i+1
                    stringlist[i] = []
        
        list = None    
        j = 1
        boundarylist = collections.defaultdict(list)
        boundarylist[j] = []
        
        for line in bcfile:
            if line.split()[0] == 'BHL':
                boundarytypeID = np.int(line.split()[2])
                boundarylist[j] = boundarytype[boundarytypeID]
                j = j+1
                
             
        river_nodes = 0
        ocean_nodes = 0
        land_nodes = 0
        river_boundaryID = []
        ocean_boundaryID = []
        land_boundaryID = []
        
    #this loop is for grouping the nodestrings into discharge boundaries, water level 
    #and land boundaries so they are printed in that order in hgrid.gr3     
        for k in np.arange(1,number_of_boundaries+1): 
            if boundarylist[k][0] != 'land' and boundarylist[k][0] != 'ocean':
                river_nodes = river_nodes + stringlist[k].size
                river_boundaryID = np.append(river_boundaryID,k)
    
            if boundarylist[k][0] == 'ocean':
                ocean_nodes = ocean_nodes + stringlist[k].size
                ocean_boundaryID = np.append(ocean_boundaryID,k)
                
            if boundarylist[k][0] == 'land':
                land_nodes = land_nodes + stringlist[k].size
                land_boundaryID = np.append(land_boundaryID,k)
    #this loop prints out the total number of open and land boundaries, and total 
    #number of nodes and list of nodes for each boundary to hgrid.gr3
                
        fid.write((river_boundaryID.__len__() + ocean_boundaryID.__len__()).__str__() + ' :Number of open boundaries\n' + (river_nodes + ocean_nodes).__str__() + '  !Number of open boundary nodes\n')  
        for z in river_boundaryID:
            fid.write(stringlist[z].size.__str__() + ' !Number of nodes in ' + boundarylist[z][1] + ' ' + '\n')
            boundary = np.array([np.int(bd) for bd in stringlist[z]])
            np.savetxt(fid,boundary,fmt='%10.0f')
        
        for z in ocean_boundaryID:
            fid.write(stringlist[z].size.__str__() + ' !Number of nodes in ' + boundarylist[z][1] + ' ' + '\n')
            boundary = np.array([np.int(bd) for bd in stringlist[z]])
            np.savetxt(fid,boundary,fmt='%10.0f')   
    
        fid.write(land_boundaryID.__len__().__str__() + ' :Number of land boundaries\n' + land_nodes.__str__() + ' !Number of land boundary nodes\n')
        for z in land_boundaryID:
            if boundarylist[z][1] == 'external land':
                landID = 0
            else:    
                landID = 1
            fid.write(stringlist[z].size.__str__() + ' ' + landID.__str__() + ' !Number of nodes in ' + boundarylist[z][1] + ' ' + z.__str__() + '\n')
            boundary = np.array([np.int(bd) for bd in stringlist[z]])
            np.savetxt(fid, boundary,fmt='%10.0f')
    fid.close()
                    
    with open(os.path.join(grid_data_dir,filename), 'r+') as f:
        old = f.read()
        f.seek(0)
        f.write(filename  + '\n' + c.__str__() + '   ' + d.__str__() + '\n' + old)
        f.close()
        
        
        

    
    
    
    
 

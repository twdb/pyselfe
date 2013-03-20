# -*- coding: utf-8 -*-
"""
Created on Tue Mar 19 15:47:47 2013

@author: snegusse
"""

import numpy as np

import shapefile 

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
    
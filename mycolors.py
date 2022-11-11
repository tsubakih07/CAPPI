import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import nclcmaps as ncl

def dz_cmap():
    data = [[255.0,255.0,255.0],
            [170.0,255.0,255.0],
            [85.0,160.0,255.0],
            # [29.0,0.0,255.0],
            [126.0,229.0,91.0],
            [78.0,204.0,67.0],
            [46.0,178.0,57.0],
            # [30.0,153.0,61.0],
            [255.0,255.0,102.0],
            [255.0,204.0,102.0],
            [255.0,136.0,76.0],
            # [255.0,25.0,25.0],
            [204.0,61.0,61.0],
            # [165.0,49.0,49.0],
            [237.0,0.0,237.0],
            [137.0,103.0,205.0],
            # [250.0,240.0,230.0]
            ]
    
    data = data / np.max(data)
    cmap = mpl.colors.ListedColormap(data)    
    cmap.set_over('gray')
    cmap.set_under('gray')
    return cmap

def zdr_cmap(c_index=None):
    cmap = ncl.cmap('precip3_16lev',c_index) 
    return cmap

def zdp_cmap(c_index=None):
    cmap = ncl.cmap('precip3_16lev',c_index) 
    return cmap
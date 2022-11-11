#%%
import pyart
import numpy as np
import pandas as pd
import os
from datetime import datetime as dt
import xarray as xr
import pandas as pd
import data_qc4qpe as qc
import get_emp_qpe
import gc
import subprocess
#%%
case = "Chanthu"
# date = '2018_0710'
date = '2021_0912'
D = '/mnt/d/Project/'
indir = D+'RAWdata/'+case+'/'+date+'/'
nc_out = D+'nc_data/'+case+'/'
cappi_out = D+'CAPPI_nc/'+case+'/'
os.makedirs(nc_out,exist_ok=True)
os.makedirs(cappi_out,exist_ok=True)

files = os.listdir(indir)
print('Radar data number: '+str(len(files)))
filename = files[170]

### read Zdr bias data
ifile = case+'_'+date+'_Zdr_bias.csv'
df_bias = pd.read_csv(ifile,header=0,sep=',', index_col=0,parse_dates=[0])
bias0 = 0.36
biasm = df_bias['mean'].mean()
bias = bias0 if abs(biasm) > abs(bias0) else biasm

#%%
# for hour in np.arange(4,5):   
for hour in np.arange(0,24):        
    filelist = [s for s in files if s[:8]+'_'+str(hour).zfill(2) in s]
    i = 0
    for filename in filelist:
        
        outname = filename[:-13]
        tdatetime = dt.strptime(outname, '%Y%m%d_%H%M')
        # tstr = tdatetime.strftime('%Y/%m/%d %H:%M UTC')
        tstr = tdatetime.strftime('%Y-%m-%d %H:%M:00')
        hh = tdatetime.hour
        
        
        print('Processing '+str(hh).zfill(2)+'UTC  :'+filename)
        ### read radar data
        radar = pyart.io.read_nexrad_archive(indir+filename) 
        

        ### correct Zdr bias
        # index = pd.to_datetime(tdatetime)
        # bias = df_bias['mean'].at_time(index).values
        # bias = df_bias['mean'].mean()

        # data QC for QPE
        radar,gatefilter = qc.qc_all(radar,bias)  

        ### retrive Kdp (takes about 6 min for 1 volume scan)
        print('>>> Caliculating Kdp... This will take several minutes <<<')
        radar = qc.get_kdp_maesaka(radar)
        
        ### add QPE fields
        print('>>> Doing QPE... <<<')
        radar = get_emp_qpe.get_all_QPE(radar)
 
        ### radar to grid
        ### resolution {dx,dy,dz} = (1.0, 1.0, 0.5) km
        print('>>> Convert radar object to grid... <<<')
        grid = pyart.map.grid_from_radars(radar, grid_shape=(25, 201, 201),
                                        grid_limits=((0.,12000,), (-100000., 100000.), (-100000, 100000.)))

        ### write NetCDF
        ### by xarray
        xarray = grid.to_xarray()

        ### combine hourly data
        if i == 0:
            out = xarray
        else:
            new = xarray            
            out = xr.concat([out, new], dim='time')
            
        
        ### free memory
        del radar, grid, xarray
        gc.collect()
        
        i = i+1
        
    ### write outputs    
    ### take hourly average
    mean = out.mean('time')
    outname1 ='Hourly_mean_'+date+str(hour).zfill(2)+'UTC.nc'
    mean.to_netcdf(nc_out+outname1)
    print('Output:'+nc_out+outname1)
    
    ### write out
    outname2 = 'CAPPI_Dataset_'+date+str(hour).zfill(2)+'UTC.nc'
    out.to_netcdf(cappi_out+outname2)
    print('Output:'+cappi_out+outname2)

    
    ### free memory
    del out
    gc.collect()
# %%

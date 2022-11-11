#%%
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr
import matplotlib.patches as patches
import mycolors
import nclcmaps
import os
#%%
# case = "Maria"
# date = '2018_0710'
case = "Chanthu"
date = '2021_0912'
hh = '03'
hei = 500
var = 'cross_correlation_ratio'
domain = 'small'

var_dict = {'reflectivity':'DZ',
            'cor_Zh': 'DZ',
            'differential_reflectivity':'ZD',
            'cor_Zdr':'ZD',
            'specific_differential_phase':'KDP',
            'differential_phase':'PD',
            'cross_correlation_ratio':'RH',
            'rr_zh':'RR',
            'rr_zh_zdr':'RR',
            'rr_kdp':'RR',
            'rr_kdp_zdr':'RR'
            }

vkey = var_dict.get(var)

### domain setting
# minlon = 121.25
# maxlon = 122.20
# minlat = 24.9
# maxlat = 25.8

### domain setting (x,y) in m
### origin: radar
east=    20  *1000
west=   -60  *1000
south = -20  *1000
north =  60  *1000


D = '/mnt/d/Project/'
nc_dir = D+'nc_data/'+case+'/'
infile = 'Hourly_mean_'+date+hh+'UTC.nc'
outdir = D+'img/'+case+'/'
os.makedirs(outdir,exist_ok=True)

# cappi_dir = D+'CAPPI_nc/'+case+'/'
# infile = 'CAPPI_Dataset_'+date+hh+'UTC.nc'

#%% read netcdf by xarray

ds = xr.open_dataset(nc_dir+infile)
if domain == 'small':
    # ds.sel(lon=slice(minlon,maxlon),lat=slice(minlat,maxlat),method='nearest')
    ds = ds.sel(x=slice(west,east),y=slice(south,north))
    step = 1
    markersize = 100
else:
    step =3
    markersize = 50
    
lon = ds['lon'].data
lat = ds['lat'].data
z = ds[var].sel(z=hei).data

    
### get topo data
### fine resolution
etopo = xr.open_dataset('~/.gmt/server/earth/earth_relief/earth_relief_15s_p/N20E120.earth_relief_15s_p.nc')
### set resolution 


### rough resolution
# etopo = xr.open_dataset('~/.gmt/server/earth/earth_relief/earth_relief_30s_g/N15E120.earth_relief_30s_g.nc')

tx=etopo.variables['lon'][:]
ty=etopo.variables['lat'][:]
Z=etopo.variables['z'][:]

X, Y = np.meshgrid(tx, ty)
X_rough = X[::step, ::step]
Y_rough = Y[::step, ::step]
Z_rough = Z[::step, ::step]


### plot region
minlon = lon.min()
maxlon = lon.max()
minlat = lat.min()
maxlat = lat.max()

# 描画範囲を決定
left_edge, right_edge = minlon, maxlon
bottom_edge, top_edge = minlat, maxlat

# 描画範囲に含まれるかを判定
X_isin_drawRange = (left_edge <= X_rough[0, :])\
                * (X_rough[0, :] <= right_edge)
Y_isin_drawRange = (bottom_edge <= Y_rough[:, 0])\
                * (Y_rough[:, 0] <= top_edge)
                

# 描画範囲のデータだけを抽出する
X_drawRange = X_rough[Y_isin_drawRange, :][:, X_isin_drawRange]
Y_drawRange = Y_rough[Y_isin_drawRange, :][:, X_isin_drawRange]
Z_drawRange = Z_rough[Y_isin_drawRange, :][:, X_isin_drawRange]

# levels = np.arange(np.floor(0), np.ceil(Z.max()), 200) # 値のリスト作成   
### topo contour interval
levels = [0,200,400,600,800,1000,2000,3000]  

#%%
fig = plt.figure(figsize=(12, 10),facecolor='white')
ax = fig.add_subplot(111)

# plot CAPPI reflectivity

# c_index = [2,3,4,5,6,7,9,10,11,12,13,15,16]
# cmap = nclcmaps.cmap('prcp_1',c_index)

if vkey == 'DZ': 
    cmap = mycolors.dz_cmap()   
    clv = [0.,5.,10.,15.,20.,25.,30.,35.,40.,45.,50.,55.,60.]
    clabel = 'dBZ'
    varname = '$Z_{HH}$'
elif vkey == 'ZD':
    cmap = mycolors.zdr_cmap()   
    clv = np.arange(-.5,3.25,.25)
    c_index = [1,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
    cmap = nclcmaps.cmap('precip3_16lev',c_index,'y')
    clabel = 'dB'
    varname = '$Z_{DR}$'
elif vkey == 'KDP':
    cmap = nclcmaps.cmap('MPL_Set3')  
    clv = np.arange(0,1.025,.025)
    clabel = 'deg/km'
    varname = '$K_{DP}$'
elif vkey == 'RR':
    cmap = nclcmaps.cmap('WhiteBlueGreenYellowRed')  
    clv = np.arange(0,62,2)
    clabel = 'mm/h'
    varname = 'Rain Rate'
elif vkey == 'RH':
    cmap = nclcmaps.cmap('cmp_haxby')  
    clv = np.arange(0.5,1.05,.05)
    clabel = ''
    varname = '\u03c1$_{HV}$'
    
### plot value with shading
x, y = np.meshgrid(lon, lat)
plt.contourf(x,y,z,cmap=cmap,levels=clv)#,vmin=0,vmax=60)
if vkey =='DZ' or vkey == 'RH':
    cbar = plt.colorbar(ticks = clv)
else:
    cbar = plt.colorbar()
cbar.set_label(clabel)
### fill nan with gray color
xmin, xmax, ymin, ymax = plt.axis()
xy = (xmin, ymin)
width = xmax - xmin
height = ymax - ymin
p = patches.Rectangle(xy, width, height, fill=True, color='lightgray', zorder=-10)
ax.add_patch(p)


### plot topo
ax.contour(X_drawRange, Y_drawRange, Z_drawRange, levels=levels,colors='k',linewidths=1)


plt.title(str(hei)+' m  CAPPI Hourly Averaged '+varname+' at '+hh+' UTC',fontsize=18)

### plot satations 

### radar site
wfs = [121.77305603027344,25.073055267333984]
ax.scatter(wfs[0],wfs[1], marker='^',c='k',s=markersize*2,label="Radar")
ax.text(wfs[0]+0.005,wfs[1], 'WFS', fontsize=markersize/4)

#add sounding locations
bc = [121.442017,24.997647]
ax.scatter(bc[0],bc[1], marker='s',c='k',s=markersize,label='Sounding')
ax.text(bc[0]+0.005,bc[1], 'BC', fontsize=markersize/5)

# surface stations
a = [121.529731,25.182586]
ax.scatter(a[0],a[1], marker='D',c='k',s=markersize,label='Parsivel')
ax.text(a[0]+0.005,a[1], 'Anbu', fontsize=markersize/5)

t = [121.514853,25.037658]
ax.scatter(t[0],t[1], marker='D',c='k',s=markersize)
ax.text(t[0]+0.005,t[1], 'Taipei', fontsize=markersize/5)

k = [121.740475,25.133314]
ax.scatter(k[0],k[1], marker='D',c='k',s=markersize)
ax.text(k[0]+0.005,k[1], 'Keeling', fontsize=markersize/5)

# ax.scatter(121.448906,25.164889, marker='o',c='k',s=markersize,label=),label_offset=[-0.05,0.015])

ax.legend()

plt.savefig(outdir+'/'+vkey+'_hourly_test_'+hh+'UTC_'+str(hei)+'-'+domain+'.png',dpi=300,bbox_inches='tight')
# %%
# index = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18]
# c_index = [2,3,4,5,6,7,9,10,11,12,13,15,16]

# cdict = dict({"prcp_1":[[255.0,255.0,255.0],
#                         [170.0,255.0,255.0],
#                         [85.0,160.0,255.0],
#                         [29.0,0.0,255.0],
#                         [126.0,229.0,91.0],
#                         [78.0,204.0,67.0],
#                         [46.0,178.0,57.0],
#                         [30.0,153.0,61.0],
#                         [255.0,255.0,102.0],
#                         [255.0,204.0,102.0],
#                         [255.0,136.0,76.0],
#                         [255.0,25.0,25.0],
#                         [204.0,61.0,61.0],
#                         [165.0,49.0,49.0],
#                         [237.0,0.0,237.0],
#                         [137.0,103.0,205.0],
#                         [250.0,240.0,230.0]]})


# %%

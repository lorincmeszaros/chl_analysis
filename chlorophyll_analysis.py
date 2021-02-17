# -*- coding: utf-8 -*-
"""
Created on 17-2-2021

@author: Lorinc Meszaros (Deltares)
"""
#==============================================================================
#Import packages
from netCDF4 import Dataset
import cftime as nc4
import os
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER
import cartopy.io.img_tiles as cimgt
import matplotlib 
import matplotlib.pyplot as plt
import numpy.ma as ma

#==============================================================================
#Dataset path
nc_path_chl1 = os.path.abspath(r'p:\11201274-odyssea\10-Workshops\Egypt_Training_2021\sv03-med-ogs-pft-rean-m_1613583524278.nc');  

#Dataset
dataset_chl1 = Dataset(nc_path_chl1) #chl

#==============================================================================  
#Interrogate netCDF file
print (dataset_chl1.file_format)
print (dataset_chl1.dimensions.keys()) #dimensions
print (dataset_chl1.dimensions['time'])
print (dataset_chl1.variables.keys()) #variables
print (dataset_chl1.variables['time'])
print (dataset_chl1.Conventions) # Get conventions attribute

attr=dataset_chl1.ncattrs() #find all NetCDF global attributes  
for attr in dataset_chl1.ncattrs():
    print (attr, '=', getattr(dataset_chl1, attr))
#==============================================================================  
#Access data
#Chl 1999-2018
fh_chl1 = Dataset(nc_path_chl1, mode='r')
time1=fh_chl1.variables['time'] #access time
jd1 = nc4.num2date(time1[:],time1.units, only_use_cftime_datetimes=False, only_use_python_datetimes=True)
lons1 = fh_chl1.variables['longitude'][:] #access longitude
lats1 = fh_chl1.variables['latitude'][:] #access latitude
chl = np.squeeze(fh_chl1.variables['chl'][:]) #access chlorophyll
fh_chl1.close()

#==============================================================================
#PLOT
timestep=1; #choose a time step (e.g. 0 - first image, 1 - second image, etc.)

#Plot map
chl_plot=np.squeeze(chl[timestep,:,:])
matplotlib.rcParams['figure.figsize'] = (10,10) #set figure size

proj=ccrs.Mercator() # Get some parameters for the Stereographic Projection
m = plt.axes(projection=proj)
# Put a background image on for nice sea rendering.
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')
m.add_image(stamen_terrain, 8)
#Add coastlines
m.coastlines(resolution='10m')
m.add_feature(cfeature.BORDERS.with_scale('10m'))
gl=m.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--') #add map gridlines
gl.xformatter = LONGITUDE_FORMATTER #format axis label
gl.yformatter = LATITUDE_FORMATTER #format axis label
gl.xlabels_top = False #disable axis label
gl.ylabels_right = False #disable axis label
#Plot data
plt.contourf(lons1, lats1, chl_plot, 60,
             transform=ccrs.PlateCarree(), vmin=0, vmax=0.7) #plot data

# Add Colorbar
cbar=plt.colorbar()             

# Add Title
plt.title('Chlorophyll-a concentration')

plt.show() #show plot

#==============================================================================
#Area average
    
#Chl area average
av_area_chl = np.full([int(chl.shape[0])], np.nan)
yearly_av_chl= np.full([round(chl.shape[0]/12)], np.nan)

av_area_chl = np.mean(np.mean(np.squeeze(chl[:,:,:]), axis = 1), axis=1)   
for i in np.arange(round(chl.shape[0]/12)):
    yearly_av_chl[i] = np.mean(av_area_chl[i:(i+12)])
start_year=int(str(jd1[0])[:4])
    
#Plot
fontsize=20
colors= ['lightcoral','plum','g','b',]

plt.figure(figsize=(15,5))
plt.bar(start_year+np.arange(len(yearly_av_chl[:])), yearly_av_chl[:], color=colors[0])
plt.xlabel("Years", fontsize=fontsize)
plt.ylabel("Yearly mean chlorophyll-a conc.", fontsize=fontsize)
plt.title("Yearly chlorophyll-a time series", fontsize=fontsize)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.ylim(0.06,0.09)
plt.show()

#Plot
plt.figure(figsize=(15,5))
plt.plot_date(jd1,av_area_chl, xdate=True, fmt='-', color=colors[1])
plt.grid()
plt.xlabel("Years", fontsize=fontsize)
plt.ylabel("Monthly mean chlorophyll-a conc.", fontsize=fontsize)
plt.title("Monthly chlorophyll-a time series", fontsize=fontsize)
plt.xticks(fontsize=fontsize)
plt.yticks(fontsize=fontsize)
plt.show()

#==============================================================================
#Trend lines

#Np.polyfit - Chlorophyll
slope_chl = np.full([int(chl.shape[1]), int(chl.shape[2])], np.nan)
for j in range(0,int(chl.shape[1])):
    for i in range(0,int(chl.shape[2])):
        y=chl[:,j,i]
        X=np.arange(len(y))
        
        reg = np.polyfit(X, y, 2)
        slope_chl[j,i]=reg[1]
    print(str(round(j/chl.shape[1]*100/10)*10) + ' %')
        
slope_chl=ma.masked_invalid(slope_chl)
slope_chl=ma.masked_less(slope_chl, -100.0)

#==============================================================================
#PLOT SLOPE

#Plot - Chl
matplotlib.rcParams['figure.figsize'] = (10,10) 
# Get some parameters for the Stereographic Projection
proj=ccrs.Mercator()
m = plt.axes(projection=proj)
# Put a background image on for nice sea rendering.
# Create a Stamen terrain background instance.
stamen_terrain = cimgt.Stamen('terrain-background')
m.add_image(stamen_terrain, 8)
#Add coastlines
m.coastlines(resolution='10m')
m.add_feature(cfeature.BORDERS.with_scale('10m'))
gl=m.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=2, color='gray', alpha=0.5, linestyle='--')
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabels_top = False
gl.ylabels_right = False
#Plot data
plt.contourf(lons1, lats1, slope_chl, 20, vmin=-0.0001, vmax=0.0007,transform=ccrs.PlateCarree())

# Add Colorbar
plt.colorbar()
#cbar = plt.colorbar(ticks=[-0.01, 0, 0.01])

# Add Title
plt.title('Slope of chlorophyll-a concentration change')

plt.show()

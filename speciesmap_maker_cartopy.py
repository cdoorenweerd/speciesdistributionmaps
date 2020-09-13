#!/usr/bin/env python
# coding: utf-8


import matplotlib
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy
import pandas as pd
import numpy as np
import psycopg2
import time
import linecache
from pathlib import Path


def simplemap(species):
       data_crs = ccrs.PlateCarree() # data to plot is in lat/lon coordinate system
       asiacentric = ccrs.PlateCarree(central_longitude=100) # change center of the map to ~ Thailand centric
       fig = plt.figure(figsize=(5, 5), dpi= 300, edgecolor='white')
       ax = fig.add_subplot(111, facecolor='white', frame_on=False, projection=asiacentric)
       # get bounding box coords here: http://boundingbox.klokantech.com, select 'dublincore'
       ax.set_extent([-120, 125, -40, 45], crs=asiacentric) # minx, maxx, miny, maxy. if not set, map extent will be adjusted to match plotted data
       ax.coastlines(resolution='50m', linewidth=0.2) # 50m or 110m, taken from naturalearthdata.com
       ax.add_feature(cartopy.feature.OCEAN)
       ax.add_feature(cartopy.feature.LAND, edgecolor='grey', linewidth=.2)
       ax.add_feature(cartopy.feature.LAKES)
       #ax.add_feature(cartopy.feature.RIVERS)
       ax.add_feature(cartopy.feature.BORDERS, edgecolor='grey', linewidth=0.2) # countries
       plt.title("University of Hawaii Insect Museum (c) " + time.strftime("%Y") + "\n" +
                  species + 
                 "\n Literature records (orange triangles) and UHIM collections (green circles: mscode sample, purple: bulk sample)", fontsize=3)
    
       # plot historical data
       dfhistsp = dfhist.query('taxon == @species')
       col_y_hist = list(dfhistsp['latitude'])
       col_x_hist = list(dfhistsp['longitude'])
       if col_y_hist: # returns true if the latitude list is not empty and runs the next line
              ax.plot(col_x_hist, col_y_hist, transform=data_crs, marker='^',color='#f1a340', markersize=2, zorder=27,
                      linestyle='None', markeredgewidth=.2, markeredgecolor='black', alpha=.8)

       # plot surplus data
       dfsurplussp = dfsurplus.query('taxon == @species')
       col_y_surplus = list(dfsurplussp['latitude'])
       col_x_surplus = list(dfsurplussp['longitude'])
       if col_y_surplus:
              ax.plot(col_x_surplus, col_y_surplus, transform=data_crs, marker='.',color='#998ec3', markersize=4, zorder=28,
                      linestyle='None', markeredgewidth=.2, markeredgecolor='black', alpha=.8)

       # plot ms sample data
       dfmscodessp = dfmscodes.query('final_id == @species')
       col_y_mscodes = list(dfmscodessp['latitude'])
       col_x_mscodes = list(dfmscodessp['longitude'])
       if col_y_mscodes:
              ax.plot(col_x_mscodes, col_y_mscodes, transform=data_crs, marker='.',color='#2ca25f', markersize=4, zorder=29,
                      linestyle='None', markeredgewidth=.2, markeredgecolor='black', alpha=.8)

       # save to plate
       speciesnospace = species.replace(" ", "_")
       datetoday = time.strftime("%Y%m%d")
       plt.savefig('output_maps/' + datetoday + '_' + speciesnospace + '_distribution.png',
                   dpi=600, bbox_inches="tight")
       plt.close('all')


connectstring = linecache.getline(filename='.connectstring', lineno=1)
conn = psycopg2.connect(connectstring)
sqlsurplus = "SELECT * FROM surplusview WHERE latitude IS NOT NULL;"
dfsurplus = pd.read_sql_query(sqlsurplus, conn)
sqlhist = "SELECT * FROM histrecords;"
dfhist = pd.read_sql_query(sqlhist, conn)
sqlmscodes = "SELECT * FROM ms_samplesview WHERE latitude IS NOT NULL;"
dfmscodes = pd.read_sql_query(sqlmscodes, conn)
conn = None

specieslist = dfmscodes['final_id'].unique().tolist()
Path("./output_maps").mkdir(parents=True, exist_ok=True)

print("Making maps for " + str(len(specieslist)) + " species")
for species in specieslist:
       try:
              simplemap(species)
       except Exception as e:
              print("Cannot make map for " + species + ". Exception error:")
              print(e)
              pass
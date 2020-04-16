#!/usr/bin/env python
# coding: utf-8


import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import psycopg2
import time
import linecache
from mpl_toolkits.basemap import Basemap
from pathlib import Path



# map drawing function
def simplemap(species):
       fig = plt.figure(figsize=(5, 5), dpi= 300, edgecolor='white')
       ax = fig.add_subplot(111, facecolor='white', frame_on=False)
       # get bounding box coords here: http://boundingbox.klokantech.com, select 'dublincore'
       westlimit=-19.9; southlimit=-39.6; eastlimit=174.9; northlimit=48.7
       m = Basemap(resolution='l', # c, l, i, h, f or None
                    projection='tmerc',
                    epsg=3395, # WGS84 world map projection, see http://epsg.io/3395
                    area_thresh=100, # to include/exclude small islands (km diameter)
                    llcrnrlon=westlimit, llcrnrlat=southlimit, urcrnrlon=eastlimit, urcrnrlat=northlimit)
       m.drawmapboundary(fill_color='#deebf7') # sea
       m.fillcontinents(color='white',lake_color='#deebf7') # land & lakes
       m.drawcoastlines(linewidth=0.2, color='grey', zorder=26)
       m.drawcountries(linewidth=0.2, color='grey', zorder=26)
       plt.title("University of Hawaii Insect Museum (c) 2020 \n" +
                  species + 
                 "\n Literature records (orange triangles) and UHIM collections (green circles: mscode sample, purple: bulk sample)", fontsize=3)
    
       # plot historical data
       dfhistsp = dfhist.query('taxon == @species')
       col_y_hist = list(dfhistsp['latitude'])
       col_x_hist = list(dfhistsp['longitude'])
       m.plot(col_x_hist, col_y_hist, marker='^',color='#f1a340', markersize=3, zorder=27, latlon=True,
              linestyle='None', markeredgewidth=.2, markeredgecolor='black', alpha=.8)
    
       # plot surplus data
       dfsurplussp = dfsurplus.query('taxon == @species')
       col_y_surplus = list(dfsurplussp['latitude'])
       col_x_surplus = list(dfsurplussp['longitude'])
       m.plot(col_x_surplus, col_y_surplus, marker='.',color='#998ec3', markersize=7, zorder=28, latlon=True,
           linestyle='None', markeredgewidth=.2, markeredgecolor='black', alpha=.8)

       # plot ms sample data
       dfmscodessp = dfmscodes.query('final_id == @species')
       col_y_mscodes = list(dfmscodessp['latitude'])
       col_x_mscodes = list(dfmscodessp['longitude'])
       m.plot(col_x_mscodes, col_y_mscodes, marker='.',color='#2ca25f', markersize=7, zorder=29, latlon=True,
           linestyle='None', markeredgewidth=.2, markeredgecolor='black', alpha=.8)

       # save to plate
       speciesnospace = species.replace(" ", "_")
       datetoday = time.strftime("%Y%m%d")
       plt.savefig('output_maps/' + datetoday + '_' + speciesnospace + '_distribution.png',
                   dpi=600, bbox_inches="tight")
       plt.close()

# Pull data from local postgresql
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

print("Making maps for " + len(specieslist) + "species")
for species in specieslist:
       try:
              simplemap(species)
       except Exception as e:
              print("Cannot make map for " + species + ". Exception error:")
              print(e)
              pass
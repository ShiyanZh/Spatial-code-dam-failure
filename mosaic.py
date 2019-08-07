# -*- coding: utf-8 -*-
"""
Created on Sat Sep 08 23:24:23 2018

@author: Shiyan
"""

import arcpy
import os

## Step 1: 
## create folder path and working environment
## Get the string list of .tif DEM
arcpy.env.overwriteOutput = True
folder_path = "D:/GWU/AdamJ/DEM/new_mosaic/resevoir_river_dem"
arcpy.env.workspace = folder_path
file_list = os.listdir(folder_path)
data_list = [x for x in file_list if x.endswith(".tif")]
tif_string = ";".join(data_list)

## Step 2:
## Define a function to calculate the min and max value of total original DEM files
## which will be used to compare them with the min and max value of mosaicked DEM to check if they are 
## the same as the values before mosaic DEM
def get_raster_min_max(tif_file_name):
    myRaster = arcpy.Raster(tif_file_name)
    org_min = myRaster.minimum 
    org_max = myRaster.maximum
    return [org_min, org_max]

## Step 3:
## Mosaic multiple raster DEM
## Set parameters
input_rasters = tif_string 
output_location = "D:/GWU/AdamJ/DEM/new_mosaic/resevoir_river_dem" 
output_rast = "mosaic_reri_add_all.tif"
sr = arcpy.SpatialReference(32618)
pixel_type = "32_BIT_FLOAT"
bands = 1
mosaic_method = "BLEND"
## Execute mosaic function
mosc_dem = arcpy.MosaicToNewRaster_management(input_rasters, output_location, 
                                   output_rast, sr,
                                   pixel_type, '', bands, mosaic_method)
## Get the max and min value of mosaicked raster
mosc_value = get_raster_min_max(mosc_dem)
mosc_min = min(mosc_value)
mosc_max = max(mosc_value)
print mosc_min, mosc_max

## Step 4:
## Compare the max and min value resuts of original and mosaicked DEM
## Put the min value and max value into two new lists, 
## and get the minimum min from min_list, and maximun max from max_list
all_og_min = []
all_og_max = []
for rast in data_list:
    ## Use calculate statistic method to re-statistic original DEM raster
    ## because the statistic data of original DEM might be out-dated
    n_rast = arcpy.CalculateStatistics_management(rast)
    ## Use defined function to collect all values
    og_value = get_raster_min_max(n_rast)
    all_og_min.append(og_value[0])
    all_og_max.append(og_value[1])
## Get the min and max value of original DEM files.    
tl_min = min(all_og_min)
tl_max = max(all_og_max)
print tl_min, tl_max

## Use 'if' statement to compare values
if tl_min == mosc_min and tl_max == mosc_max:
    print "Right answer"
else:
    print "Wrong"



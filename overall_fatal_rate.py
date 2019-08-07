# -*- coding: utf-8 -*-
"""
Created on Sun Feb 03 22:27:36 2019

@author: Shiyan
"""

import arcpy
import pandas as pd
import os 

# 1. Prepare raster and shapefiles
arcpy.env.overwriteOutput = True
# Set environment settings and path
in_path = "D:/GWU/AdamJ/task6/mission"
out_path = "D:/GWU/AdamJ/task6/mission/result/result.gdb"
#  Set local variables
arcpy.env.workspace = in_path
inFeatures = "building.shp"
outFeatures = inFeatures.replace('.shp','_pnt')
outFeatureClass = os.path.join(out_path, outFeatures)
# Use FeatureToPoint function to find a point inside each polygon(building)
# In order to extract values from DV raster
arcpy.FeatureToPoint_management(inFeatures, outFeatureClass, "INSIDE")
# Check out the ArcGIS Spatial Analyst extension license
arcpy.CheckOutExtension("Spatial")
# Execute ExtractValuesToPoints
# Assign the value from DV raster to building point layer
inPntFeatures = outFeatureClass 
inRaster = os.path.join(in_path, "flood_dv2.tif")
outPntBldg = os.path.join(out_path,inFeatures.replace('.shp', '_pnt_dv'))
arcpy.sa.ExtractValuesToPoints(inPntFeatures, inRaster, outPntBldg)
print "complete"

# 2.Define a function to get the arcTable in to DataFrame for the following calculation
def tbl_to_dataFrame(shp_path):
    # Get the arcTable's fields as list
    fld_list = arcpy.ListFields(shp_path)
    fld_names = [str(fld.name) for fld in fld_list]   
    # create an empty dictionary with arcTable's fields as keys
    data_dict = {}
    for fld in fld_names:
        data_dict[fld] = []   
    # Loop through each row, in each row loop through each field
    with arcpy.da.SearchCursor(shp_path, fld_names) as cursor:
        for row in cursor:
            for fld in fld_names:
                fld_index = fld_names.index(fld)
                cell_value = row[fld_index]
                # the raw cell_value are all read as unicode by SearchCursor, making it python string for now
                # if you need to convert some columns into numeric type, do it later
                try:                    
                    cell_value = str(cell_value)
                except UnicodeEncodeError:
                    cell_value = cell_value.encode('utf-8')
                # When it reads the first row, the dictionary does not have any value yet
                if data_dict[fld] == None:
                   data_dict[fld] = [cell_value]
                else:
                    # use a temp list to store value in each iteration
                    temp_list = data_dict[fld]
                    temp_list.append(cell_value)
                    data_dict[fld] = temp_list                
    # make a dataframe out of the dictionary
    data_df = pd.DataFrame(data_dict)
    return data_df
# Call funtion
dv_df = tbl_to_dataFrame(outPntBldg)

# 3.Calculate overall fatality rate and number of destroyed buildings from dataFRame
# Create new columns to assign each class(high, medium, low) corresponding raster value
dv_df['dv_class'] = ''
dv_df['bldg_num'] = 1
dv_df['RASTERVALU'] = dv_df['RASTERVALU'].astype(float)
# Define a function to assign DV range to corresponding raster value
def dv_class (row):
   if 0 < row['RASTERVALU'] <= 20 :
      row['dv_class'] = "Low"
   elif 20 < row['RASTERVALU'] <= 40 :
      row['dv_class'] = "Medium"
   elif 40 < row['RASTERVALU'] :
      row['dv_class'] = "High"
   elif row['RASTERVALU'] == -9999 :
      row['dv_class'] = "Safe"
   return row 
# Apply the function to dataFrame     
dv_df1 = dv_df.apply (lambda row: dv_class (row),axis=1) 
# Count the number of buildings of each category
dv_df2 = dv_df1.groupby(["dv_class"]).sum().reset_index(["dv_class"])
print dv_df2
# Create dictionaris of new columns of tatality rate and building damage rate
fatal_coe = {'High': 0.8, 'Medium': 0.1, 'Low': 0.01, 'Safe': 0}
bldg_dmg_rate = {'High': 1, 'Medium': 0.6, 'Low': 0.3, 'Safe': 0}
dv_df2['fatal_rate'] = dv_df2['dv_class'].map(fatal_coe)
dv_df2['bldg_dmg_rate'] = dv_df2['dv_class'].map(bldg_dmg_rate)
# Delete the needless column
dv_df2.drop("RASTERVALU", axis = 1, inplace = True)
# Calculate death toll and damaged buildings of each category
dv_df2['bldg_prcnt'] = dv_df2['bldg_num']/dv_df2['bldg_num'].sum()
dv_df2['death_num'] = 70000 * dv_df2['fatal_rate']*dv_df2['bldg_prcnt']
dv_df2['bldg_dmg_num'] = dv_df2['bldg_num'] * dv_df2['bldg_dmg_rate']
# Calculate overall fatality rate and overall damaged buildings
overall_fatal_rate = dv_df2['death_num'].sum()/70000
bldg_dstry_num = dv_df2['bldg_dmg_num'].sum()
# Save dataFrame to csv file
dv_df2.to_csv('report.csv', index=False)
# print results
print dv_df2
print overall_fatal_rate
print bldg_dstry_num
   
   
   
   
   
   
   
   
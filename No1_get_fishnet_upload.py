#coding:utf-8
"""
@File    : No1_get_fishnet.py
@Author  : roc
@Time    : 2023/2/10 21:36
"""
'Running in the arcpy environment of Python2.7'
import arcpy
import shapefile
from pyproj import Proj,transform
import numpy as np
# Arcpy generates a grid with the smallest circumscribed rectangle

gdb=r'E:\arcpy-\monggulia_fire'
arcpy.env.workspace=gdb
target_area='maybe_fire_area1'
#Input shp, output shp path
fc_path=r'E:\arcpy-\monggulia_fire\maybe_fire_area1.shp'#投影坐标WGS_1984_UTM_Zone_50N；地理坐标GCS_Beijing_1954
# out_feature_class2=r'E:\arcpy-\fishnet'
x = 0
out_feature_class2=r'E:\arcpy-\monggulia_fire\maybe_fire_area1_fishnet'#output name
# print(out_feature_class2)
fc=arcpy.ListFeatureClasses()
print(fc,fc[0])
#Generate a rectangle. The range is a rectangle specified by providing the coordinates of the lower left corner and upper right corner under the map unit.
# desc = arcpy.Describe("E:/arcpy-/内蒙古.shp")
desc = arcpy.Describe(fc_path)#"E:/arcpy-/monggulia_fire/maybe_fire_area1.shp")
print(desc.featureType, desc.extent)
# ext=desc.extent

# print(desc.extent.lowerLeft)
# GIS 米与度的转换公式
# double kilometter = 0.0089932202929999989 //1千米转为度
# degree = meter / (2 * Math.PI * 6371004) * 360;

m=0.0000089932202929999989 #1meter
#generate fishnet
fishnet = arcpy.CreateFishnet_management(out_feature_class = out_feature_class2,
    origin_coord=str(desc.extent.lowerLeft),
    y_axis_coord=str(desc.extent.XMin) + " " + str(desc.extent.YMax),
    cell_width = m*10000,#m*5000
    cell_height = m*10000,
    number_rows= None,
    number_columns = None,
    labels = "NO_LABELS",
    corner_coord=str(desc.extent.upperRight),
    template = fc_path,#'E:/arcpy-/monggulia_fire/maybe_fire_area1.shp',#Inner MongoliaUTM/Inner Mongolia uses Inner Mongolia shp as the template, based on the minimum circumscribed rectangle
    geometry_type = "POLYGON")
arcpy.MakeFeatureLayer_management(str(out_feature_class2)+'.shp', str(target_area)+'_fishnet_lyr')
arcpy.SelectLayerByLocation_management (str(target_area)+'_fishnet_lyr', 'intersect', fc_path)
shp_selected = arcpy.CopyFeatures_management(str(target_area)+'_fishnet_lyr', str(out_feature_class2)+'_sele.shp')
print('over')

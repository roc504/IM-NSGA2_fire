"""
@File    : No2_get_all_covered_stripe.py
@Author  : roc
@Time    : 2023/7/24 14:38
"""
'''
针对完全覆盖研究区的卫星条带生成
'''
import shapefile
# import No1_get_fishnet
import math as math
import numpy as np
import datetime
import time
import pandas as pd
import geopandas
from shapely import geometry

sat_name='TERRA'
sensor='MODIS'
data='10'
times='2'
cal_line_stime='2023-04-10 13:55:00'
cal_line_etime='2023-04-10 13:55:30'
start_time = time.time()
pass_time = '2023-04-10 13:55:00'
h , w = 705000 ,59.5657

orbit_orientation = 'left'#'right' # 卫星轨道偏向，left是指'\'轨道，向左倾斜，right是‘/’轨道，向右倾斜
open_time='2023,4,10,13,55,0'#选择开关机时间
close_time='2023,4,10,13,56,50'#选择开关机时间
sat_strp_wid=2850000#卫星条带幅宽
#卫星幅宽边界左右轻微移动微小距离，也就是一个格网的对角线长度
swing_orno=0#swing_orno为1说明有侧摆角，0为无侧摆角
grid_wid=120000#格网长度5000米
s=math.sqrt((grid_wid*0.0000089932202929999989)**2+(grid_wid*0.0000089932202929999989)**2)
#卫星幅宽信息

stripe_width=(sat_strp_wid/2)*0.0000089932202929999989#条带幅宽的一半
area_maxwidth=313520#受灾区最大跨度距离

df = pd.read_excel('E:/STK/monggulia_fire_satellite/'+sat_name+'_undersatellite_line.xlsx', usecols=["Time (UTC)","longitude (deg)","latitude (deg)","speed (km/sec)"])

def undersate_n(pass_time):
    pass_temp_index = df["Time (UTC)"] == pass_time  # df是一个DataFrame
    temp = np.flatnonzero(pass_temp_index)  # 返回的是array([126], dtype=int64)
    temp = [str(e) for e in temp]
    temp_index = int(''.join(temp))
    return (df.loc[ temp_index, "longitude (deg)"],df.loc[ temp_index, "latitude (deg)"])#temp_index是过境时间的index，是数字
def satspeed_n(pass_time):
    pass_temp_index = df["Time (UTC)"] == pass_time  # df是一个DataFrame
    temp = np.flatnonzero(pass_temp_index)  # 返回的是array([126], dtype=int64)
    temp = [str(z) for z in temp]
    temp_index = int(''.join(temp))
    return df.loc[temp_index, "speed (km/sec)"]

undersate1_n=undersate_n(cal_line_stime)
undersate2_n = undersate_n(cal_line_etime)
#卫星轨道速度
orbit_speed = satspeed_n(cal_line_stime)
v=orbit_speed*1000 #卫星速度
# print("星下点1坐标：",undersate1_n)
# print("星下点2坐标：",undersate2_n)
undersate1=undersate1_n
undersate2=undersate2_n

sf = shapefile.Reader('E:/arcpy-/monggulia_fire/maybe_fire_area1_fishnet_sele.shp')
shapes = sf.shapes()
lens = len(shapes)

grid_all = []#所有格网集合
for q in range(lens):
    grid_all.append(shapes[q].points)
# print "grid_all:", grid_all
print ("num(grid_all):", len(grid_all))

def get_undersate_line(x1,y1,x2,y2):
    #Ax+By+C=0
    sign = 1
    A = y2-y1
    if A < 0:
        sign = -1
        A = sign * A
    B = sign * (x1-x2)
    C = sign * (x2*y1-x1*y2)
    return [A,B,C]


def long_line_c(A,B,C1,d):#求星下点直线两边距离d的条带边线的C值
    C2rightC1=C1 - ( d  * math.sqrt(A * A + B * B))
    C2leftC1=(d  *  math.sqrt((A * A + B * B))) + C1
    return [C2leftC1,C2rightC1]


def get_wideline(A, B, x3, y3):  # x1,y1,x2,y2是星下点坐标，
    # x3,y3是开始成像星下点的坐标
    '''求开始成像时，垂直于星下点的直线ABC'''
    sign = 1
    if A < 0:
        sign = -1
        A = sign * A
    # 过单元格一角点，垂直于星下点直线
    # Bx - Ay +Ay3 - Bx3 = 0
    C3 = A * y3 - B * x3
    return [B, -A, C3]

open_time='2023,4,9,2,5,0'#选择开关机时间#gaofen2:2023,01,19,2,33,10
close_time='2023,4,9,2,10,0'#选择开关机时间
def select_times(start, end, frmt="%Y,%m,%d,%H,%M,%S"):
    '''求最长间隔时间'''
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    #     stime_temp = (stime+datetime.timedelta(seconds=+1))#.strftime("%Y-%m-%d %H:%M:%S")
    #     etime_temp = (etime+datetime.timedelta(seconds=-1))#.strftime("%Y-%m-%d %H:%M:%S")
    return stime,etime
T0,T1=select_times(open_time, close_time, frmt="%Y,%m,%d,%H,%M,%S")

#另一宽边直线方程

def get_satestripe_other_wideline(A, B, C, T0,T1, v, tit):  # ABC是顶边直线一般式系数，
    # T0开机时间；T1关机时间
    t =(T1-T0).seconds#开关机时间差
    # 两直线之间的距离d = \C1-C2\/√(A^2+B^2)
    # 所以新直线的C计算公式：C1=C2±d√(A^2+B^2)
    distance = (v*t)*0.0000089932202929999989#这里的distance是开关机时间内条带长度，v是卫星速度
    f = distance * math.sqrt(A * A + B * B)
    m1 = C + f
    m2 = C - f
    if tit == 0:  # tit==1为左斜，==0为右斜
        # result = 值1 if 条件 else 值2
        # C2 = m1 if C > m1 else m2
        C2 = m2
    else:
        C2 = m1

    return [A, B, C2]

def cross_point(A0,B0,C0,A1,B1,C1):
    #对 1 式乘 a2，对 2 式乘 a1 得：
    #a2*a1x + a2*b1y + a2*c1 = 0
    #a1*a2x + a1*b2y + a1*c2 = 0
    #对 1 式乘 a2，对 2 式乘 a1 得：
    #a2*a1x + a2*b1y + a2*c1 = 0
    #a1*a2x + a1*b2y + a1*c2 = 0
    y = (C0 * A1 - C1 * A0) / (A0 * B1 - A1 * B0)
    x = (C1 * B0 - C0 * B1) / (A0 * B1 - A1 * B0)
#     print("左上点:")
    return x,y

def GetCross(x1,y1,x2,y2,x,y):
    a=(x2-x1,y2-y1)
    b=(x-x1,y-y1)
    return a[0]*b[1]-a[1]*b[0]
# 判断(x,y)是否在矩形内部
def isInSide(x1,y1,x2,y2,x3,y3,x4,y4,x,y):
    return GetCross(x1,y1,x2,y2,x,y)*GetCross(x3,y3,x4,y4,x,y)>=0 and GetCross(x2,y2,x3,y3,x,y)*GetCross(x4,y4,x1,y1,x,y)>=0
#四点都在矩形内，返回True
def gridall_in_stripe(stripename,stripex,gridx):#stripex是由ut选出的矩形的索引，gridx是所有格网的索引
    leftdown = isInSide(stripename[stripex][0][0], stripename[stripex][0][1],
                        stripename[stripex][1][0], stripename[stripex][1][1],
                        stripename[stripex][2][0], stripename[stripex][2][1],
                        stripename[stripex][3][0], stripename[stripex][3][1],
                        grid_all[gridx][0][0], grid_all[gridx][0][1])
    leftup = isInSide(stripename[stripex][0][0], stripename[stripex][0][1],
                        stripename[stripex][1][0], stripename[stripex][1][1],
                        stripename[stripex][2][0], stripename[stripex][2][1],
                        stripename[stripex][3][0], stripename[stripex][3][1],
                        grid_all[gridx][1][0], grid_all[gridx][1][1])
    rightdown = isInSide(stripename[stripex][0][0], stripename[stripex][0][1],
                        stripename[stripex][1][0], stripename[stripex][1][1],
                        stripename[stripex][2][0], stripename[stripex][2][1],
                        stripename[stripex][3][0], stripename[stripex][3][1],
                        grid_all[gridx][2][0], grid_all[gridx][2][1])
    rightup = isInSide(stripename[stripex][0][0], stripename[stripex][0][1],
                        stripename[stripex][1][0], stripename[stripex][1][1],
                        stripename[stripex][2][0], stripename[stripex][2][1],
                        stripename[stripex][3][0], stripename[stripex][3][1],
                        grid_all[gridx][3][0], grid_all[gridx][3][1])
    if leftdown and leftup and rightdown and rightup:
        return True


#星下点ABC
underline_abc=get_undersate_line(undersate1[0],undersate1[1],undersate2[0],undersate2[1])
#平行与星下点的条带两边线的C
long_line_C=long_line_c(underline_abc[0],underline_abc[1],underline_abc[2],stripe_width)
#垂直与星下点的顶边直线ABC
wide_line_abc=get_wideline(underline_abc[0], underline_abc[1], undersate1[0],undersate1[1])
#经过最长时间获得的另一个垂直与星下点的顶边ABC
if orbit_orientation=='right':
    ohter_wide_line_abc=get_satestripe_other_wideline(wide_line_abc[0], wide_line_abc[1], wide_line_abc[2], T0,T1, v, 0)
else:
    ohter_wide_line_abc=get_satestripe_other_wideline(wide_line_abc[0], wide_line_abc[1], wide_line_abc[2], T0,T1, v, 1)
#四个直线的交点
#左下点坐标
stripe_leftdown = cross_point(underline_abc[0],
                              underline_abc[1],
                              long_line_C[0],
                              ohter_wide_line_abc[0],
                              ohter_wide_line_abc[1],
                              ohter_wide_line_abc[2])
# 左上点坐标
stripe_leftup = cross_point(underline_abc[0],
                            underline_abc[1],
                            long_line_C[0],
                            wide_line_abc[0],
                            wide_line_abc[1],
                            wide_line_abc[2])
# 右上点坐标
stripe_rightup = cross_point(underline_abc[0],
                             underline_abc[1],
                             long_line_C[1],
                             wide_line_abc[0],
                             wide_line_abc[1],
                             wide_line_abc[2])
# 左下点坐标
stripe_rightdown = cross_point(underline_abc[0],
                             underline_abc[1],
                             long_line_C[1],
                             ohter_wide_line_abc[0],
                             ohter_wide_line_abc[1],
                             ohter_wide_line_abc[2])
stripe4point_right = [[stripe_leftdown,stripe_leftup,stripe_rightup,stripe_rightdown]]

sf = shapefile.Reader('E:/arcpy-/monggulia_fire/maybe_fire_area1_fishnet_sele.shp')
shapes = sf.shapes()
lens = len(shapes)


listp=geometry.Polygon(stripe4point_right[0])
listi=[0]
cq = geopandas.GeoSeries(listp,
                             index=listi,  # 构建一个索引字段
                             crs='EPSG:4326',  # 坐标系是：WGS 1984
                             )
# cq.to_file('E:\\arcpy-\\monggulia_fire\\stripe\\CCtest_all.shp', driver='ESRI Shapefile',
#            encoding='utf-8')
with open('E:\\arcpy-\\monggulia_fire\\stripe\\'+str(sat_name) + '_'+str(sensor)+ '_'+ str(data)+ '_'+str(times) +'_stripe4point.txt', "w") as file:
    for s in stripe4point_right:
        file.write(str(s) + "\n")

cq.to_file('E:\\arcpy-\\monggulia_fire\\stripe\\' + str(sat_name) + '_'+str(sensor)+ '_'+str(data)+ '_'+str(times) + '_stripe_all.shp', driver='ESRI Shapefile',
               encoding='utf-8')
print('finish')

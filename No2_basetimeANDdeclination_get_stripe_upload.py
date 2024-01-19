"""
@File    : No2_basetimeANDdeclination_get_stripe.py
@Author  : roc
@Time    : 2023/3/14 19:30
"""
import random

'''
Considering the power on and off time and side swing angle, the satellite strip results are generated based on the grid.
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
from itertools import chain
#jl0105
sat_name='ZY1E'
sensor='VNIC'
data='10'
times='11'
cal_line_stime='2023-04-10 03:27:30'
#Calculate the starting time point of the subsatellite line. Fill in the time according to the xxx_undersatellet_line.xlsx file. It is best to have two adjacent times to ensure that the straight line formed by the starting point and the ending point is minimized by the curvature of the earth.
cal_line_etime='2023-04-10 03:28:00'
#Calculate the end time point of the nadir line
start_time = time.time()
pass_time = '2023-04-10 03:27:30'
#Previous moment time
'''=Orbital height, field of view='''
h , w = 778000 ,4.23#Orbital height, field of view 2w=arctan(Width/2h)*(180 / np.pi)
P = 26#/(180 / np.pi)  #Side swing angle, converted from degrees to radians
orbit_orientation = 'right'#'right' # Satellite orbit deviation, left refers to the '\' orbit, tilted to the left, right refers to the '/' orbit, tilted to the right
open_time='2023,4,10,3,27,3'#Select power on/off time
close_time='2023,4,10,3,28,23'#Select power on/off time



df = pd.read_excel('E:/STK/monggulia_fire_satellite/'+sat_name+'_undersatellite_line.xlsx', usecols=["Time (UTC)","longitude (deg)","latitude (deg)","speed (km/sec)"])
def undersate_n(pass_time):
    pass_temp_index = df["Time (UTC)"] == pass_time
    temp = np.flatnonzero(pass_temp_index)
    temp = [str(e) for e in temp]
    temp_index = int(''.join(temp))
    return (df.loc[ temp_index, "longitude (deg)"],df.loc[ temp_index, "latitude (deg)"])
def satspeed_n(pass_time):
    pass_temp_index = df["Time (UTC)"] == pass_time
    temp = np.flatnonzero(pass_temp_index)
    temp = [str(z) for z in temp]
    temp_index = int(''.join(temp))
    return df.loc[temp_index, "speed (km/sec)"]

undersate1_n=undersate_n(cal_line_stime)
undersate2_n = undersate_n(cal_line_etime)
#satellite orbital speed
orbit_speed = satspeed_n(cal_line_stime)

undersate1=undersate1_n
undersate2=undersate2_n
# sf = shapefile.Reader(No1_get_fishnet.shp_selected)
sf = shapefile.Reader('E:/arcpy-/monggulia_fire/maybe_fire_area1_fishnet_sele.shp')
shapes = sf.shapes()
lens = len(shapes)

grid_all = []#All grid sets
for q in range(lens):
    grid_all.append(shapes[q].points)
# print "grid_all:", grid_all
print ("num(grid_all):", len(grid_all))
# Linear equation of sub-satellite point trajectory
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

#Strip side straight line equation
def get_satestripe_lengline(x1, y1, x2, y2, x3, y3):  # x1, y1, x2, y2 are the coordinates of the subsatellite point, x3, y3 are the angular coordinates of the cell
    sign = 1
    A = y2 - y1
    if A < 0:
        sign = -1
        A = sign * A
    B = sign * (x1 - x2)
    C = sign * (x2 * y1 - x1 * y2)

    C3 = -(A * x3 + B * y3)
    return [A, B, C3]

#The distance between the side of the strip and the nadir point is d
def leng2undersate_distance(A,B,C1,C2):#A,B星下点轨迹or侧边的AB，C1是星下点，C2是侧边
    #两直线之间的距离d = \C1-C2\/√(A^2+B^2)
    d = abs(C1-C2)/math.sqrt(A * A + B * B)
    return d

#Side swing angle
def get_declination(d,h,w): #The unit of h here is m, and d needs to be converted.
    d_ = d/0.0000089932202929999989 #1米=0.0000089932202929999989
    declination = np.arctan(d_/h)*(180 / np.pi) - w/2 # arctan is calculated in radians, so it needs to be multiplied by (180/pi)
    return declination
#Swinging to the left is positive, and the side swing angle is negative, which means swinging to the right
def get_declination_Nagative(d,h,w):
    d_ = d/0.0000089932202929999989
    declination = np.arctan(d_/h)*(180 / np.pi) + w/2
    return declination
#strip width
def get_stripe_width(d,h,w):#d represents the distance between the side and the subsatellite point, h represents the satellite height, and w represents the field of view angle.
    if np.arctan(d/h)*(180 / np.pi) > w:
        stripe_width = d-h*np.tan((np.arctan(d/h)*(180 / np.pi)-w)*(np.pi / 180))
    else:
        stripe_width = d+h*np.tan((w-np.arctan(d/h)*(180 / np.pi))*(np.pi / 180))
    return stripe_width

#Bandwidth
def get_satestripe_wideline(x1, y1, x2, y2, x3, y3):  # x1, y1, x2, y2 are the coordinates of the sub-satellite point,
    # x3, y3 is a corner coordinate of the cell
    sign = 1
    A = y2 - y1
    if A < 0:
        sign = -1
        A = sign * A
    B = sign * (x1 - x2)
    C = sign * (x2 * y1 - x1 * y2)

    # 过单元格一角点，垂直于星下点直线
    # Bx - Ay +Ay3 - Bx3 = 0
    C3 = A * y3 - B * x3
    return [B, -A, C3]

#Equation of the other long side straight line
def get_satestripe_other_lengline(A,B,C,distance):#ABC is the general coefficient of the side straight line,，

    f = distance * math.sqrt(A * A + B * B)
    m1 = C + f
    m2 = C - f

    C2 = m1 if A < 0 else m2
    return [A, B, C2]


# Select the power on/off time period
def select_times(start, end, frmt="%Y,%m,%d,%H,%M,%S"):
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)

    time_pass = (etime - stime).seconds
    time_ssele = []
    time_esele = []
    for c in range(time_pass + 1):
        if c % 20 == 0:
            for d in range(c + 1, time_pass + 1):

                if d % 20 == 0:
                    stime_temp = (stime + datetime.timedelta(seconds=+c))
                    etime_temp = (stime + datetime.timedelta(seconds=+d))
                    time_ssele.append(stime_temp)
                    time_esele.append(etime_temp)


    return [time_ssele, time_esele]



#Another broadside equation of a straight line

def get_satestripe_other_wideline(A, B, C, T0,T1, v, tit):
    t =(T1-T0).seconds#开关机时间差

    distance = (v*t)*0.0000089932202929999989
    f = distance * math.sqrt(A * A + B * B)
    m1 = C + f
    m2 = C - f
    if tit == 1:
        C2 = m1 if C > m1 else m2
    else:
        C2 = m1 if C < m1 else m2

    return [A, B, C2]


#Intersection point of two straight line equations
def cross_point(A0,B0,C0,A1,B1,C1):

    y = (C0 * A1 - C1 * A0) / (A0 * B1 - A1 * B0)
    x = (C1 * B0 - C0 * B1) / (A0 * B1 - A1 * B0)

    return x,y

#Determine whether the four points of the grid are within the stripe rectangle

def GetCross(x1,y1,x2,y2,x,y):
    a=(x2-x1,y2-y1)
    b=(x-x1,y-y1)
    return a[0]*b[1]-a[1]*b[0]

# Determine whether (x,y) is inside the rectangle
def isInSide(x1,y1,x2,y2,x3,y3,x4,y4,x,y):
    return GetCross(x1,y1,x2,y2,x,y)*GetCross(x3,y3,x4,y4,x,y)>=0 and GetCross(x2,y2,x3,y3,x,y)*GetCross(x4,y4,x1,y1,x,y)>=0
#If all four points are within the rectangle, return True
def gridall_in_stripe(stripex,gridx):
    leftdown = isInSide(stripe4point[stripex][0][0], stripe4point[stripex][0][1],
                        stripe4point[stripex][1][0], stripe4point[stripex][1][1],
                        stripe4point[stripex][2][0], stripe4point[stripex][2][1],
                        stripe4point[stripex][3][0], stripe4point[stripex][3][1],
                        grid_all[gridx][0][0], grid_all[gridx][0][1])
    leftup = isInSide(stripe4point[stripex][0][0], stripe4point[stripex][0][1],
                        stripe4point[stripex][1][0], stripe4point[stripex][1][1],
                        stripe4point[stripex][2][0], stripe4point[stripex][2][1],
                        stripe4point[stripex][3][0], stripe4point[stripex][3][1],
                        grid_all[gridx][1][0], grid_all[gridx][1][1])
    rightdown = isInSide(stripe4point[stripex][0][0], stripe4point[stripex][0][1],
                        stripe4point[stripex][1][0], stripe4point[stripex][1][1],
                        stripe4point[stripex][2][0], stripe4point[stripex][2][1],
                        stripe4point[stripex][3][0], stripe4point[stripex][3][1],
                        grid_all[gridx][2][0], grid_all[gridx][2][1])
    rightup = isInSide(stripe4point[stripex][0][0], stripe4point[stripex][0][1],
                        stripe4point[stripex][1][0], stripe4point[stripex][1][1],
                        stripe4point[stripex][2][0], stripe4point[stripex][2][1],
                        stripe4point[stripex][3][0], stripe4point[stripex][3][1],
                        grid_all[gridx][3][0], grid_all[gridx][3][1])
    if leftdown and leftup and rightdown and rightup:
        return True


#Satellite point coordinates

v=orbit_speed*1000
time_list = select_times(open_time, close_time)

basetime_stripe4point=[]
for t in range(len(time_list[0])):
    T0 = time_list[0][t]
    T1 = time_list[1][t]

    if orbit_orientation == 'left':

        grid_U_left = []
        grid_U_left_num = []

        for i in range(len(grid_all)):
            grid_u = grid_all[i]
            # print 'grid_u:',grid_u
            undersateline = get_undersate_line(undersate1[0], undersate1[1],
                                               undersate2[0], undersate2[1])
            satestripelengline = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                         undersate2[0], undersate2[1],
                                                         grid_u[0][0],
                                                         grid_u[0][1])
            d_under_leng_lef = leng2undersate_distance(undersateline[0], undersateline[1],
                                        undersateline[2], satestripelengline[2])
            if undersateline[2]>satestripelengline[2]:
                declination = get_declination_Nagative(d_under_leng_lef, h, w)
            else:
                declination = get_declination(d_under_leng_lef, h, w)
            # print( 'declination:', declination)
            p = P
            # print(abs(declination) <= p)
            if abs(declination) <= p:
                if np.random.random()>0.5:
                    grid_U_left.append(grid_u)
                    grid_U_left_num.append(i)
        # print ('grid_U_left:', grid_U_left)

        print('num(grid_U_left)', len(grid_U_left))
        num_grid_U_left = len(grid_U_left)
        if num_grid_U_left == 0:
            # print('enough')
            break

        grid_T_left = []
        grid_T_left_num = []
        for _ in grid_U_left_num:
            #     grid_Ttemp = []
            grid_Ttemp_num = []
            grid_u = grid_all[_]
            for j in range(len(grid_all)):
                grid_t = grid_all[j]

                satestripelengline_u = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_u[0][0],
                                                               grid_u[0][1])
                satestripelengline_t = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_t[1][0],
                                                               grid_t[1][1])


                d_u_t_left = leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                            satestripelengline_u[2], satestripelengline_t[2])
                d_u_under=leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                            satestripelengline_u[2], undersateline[2])
                stripe_wide_left = get_stripe_width(d_u_under, h, w)
                stripe_wide_left = stripe_wide_left * 0.0000089932202929999989


                satestripewideline_t = get_satestripe_wideline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_t[1][0],
                                                               grid_t[1][1])
                satestripewideline_u = get_satestripe_wideline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_u[1][0],
                                                               grid_u[1][1])

                if d_u_t_left <= stripe_wide_left and abs(satestripewideline_u[2]) <= abs(satestripewideline_t[2]):
                    #             grid_Ttemp.append(grid_t)
                    grid_Ttemp_num.append(j)
            #     grid_T_left.append(grid_Ttemp)
            grid_T_left_num.append(grid_Ttemp_num)

            grid_T_left_num_1 = np.unique([b for a in grid_T_left_num for b in a])
        for gtlm in range(len(grid_T_left_num_1)):
            grid_T_left.append(grid_all[grid_T_left_num_1[gtlm]])

        print('num(grid_T_left):', len(grid_T_left))

        grid_ut_left = []
        for _ in grid_U_left_num:
            #     grid_U[_]
            #     grid_T[_]
            for __ in grid_T_left_num_1:
                #         grid_T[_][__]
                grid_u_t = (grid_all[_], grid_all[__])
                grid_ut_left.append(grid_u_t)

        print('num(grid_ut_left):', len(grid_ut_left))

        stripe4point_left = []
        for _ in range(len(grid_ut_left)):
            u_leftdown = grid_ut_left[_][0][0]
            t_leftup = grid_ut_left[_][1][1]
            satestripelengline_ = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                          undersate2[0], undersate2[1],
                                                          u_leftdown[0],
                                                          u_leftdown[1])
            undersateline_ = get_undersate_line(undersate1[0], undersate1[1],
                                                undersate2[0], undersate2[1])
            # d星下点与侧边距离
            d_under_leng_stripe_lef = leng2undersate_distance(undersateline_[0], undersateline_[1],
                                        undersateline_[2], satestripelengline_[2])
            stripe_wide_stripe = get_stripe_width(d_under_leng_stripe_lef, h, w)
            stripe_wide_stripe = stripe_wide_stripe * 0.0000089932202929999989
            other_satestripelengline_ = get_satestripe_other_lengline(satestripelengline_[0],
                                                                      satestripelengline_[1],
                                                                      satestripelengline_[2],
                                                                      stripe_wide_stripe)
            satestripewideline_ = get_satestripe_wideline(undersate1[0], undersate1[1],
                                                          undersate2[0], undersate2[1],
                                                          t_leftup[0],
                                                          t_leftup[1])
            other_satestripewideline_ = get_satestripe_other_wideline(satestripewideline_[0],
                                                                      satestripewideline_[1],
                                                                      satestripewideline_[2],
                                                                      T0, T1, v, 1)

            stripe_leftdown = cross_point(satestripelengline_[0],
                                          satestripelengline_[1],
                                          satestripelengline_[2],
                                          other_satestripewideline_[0],
                                          other_satestripewideline_[1],
                                          other_satestripewideline_[2])

            stripe_leftup = cross_point(satestripelengline_[0],
                                        satestripelengline_[1],
                                        satestripelengline_[2],
                                        satestripewideline_[0],
                                        satestripewideline_[1],
                                        satestripewideline_[2])

            stripe_rightup = cross_point(satestripewideline_[0],
                                         satestripewideline_[1],
                                         satestripewideline_[2],
                                         other_satestripelengline_[0],
                                         other_satestripelengline_[1],
                                         other_satestripelengline_[2])

            stripe_rightdown = cross_point(other_satestripelengline_[0],
                                           other_satestripelengline_[1],
                                           other_satestripelengline_[2],
                                           other_satestripewideline_[0],
                                           other_satestripewideline_[1],
                                           other_satestripewideline_[2])

            # print (stripe_leftdown, stripe_leftup, stripe_rightup, stripe_rightdown)
            stripe4point_left.append([stripe_leftdown, stripe_leftup, stripe_rightup, stripe_rightdown])
        # print stripe4point
        print('num(stripe4point_left):', len(stripe4point_left))
        stripe4point = stripe4point_left
    else :

        grid_U_right = []
        grid_U_right_num = []
        DECLINATION=[]
        for i in range(len(grid_all)):
            grid_u = grid_all[i]
            # print 'grid_u:',grid_u
            undersateline = get_undersate_line(undersate1[0], undersate1[1],
                                               undersate2[0], undersate2[1])
            satestripelengline = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                         undersate2[0], undersate2[1],
                                                         grid_u[3][0],
                                                         grid_u[3][1])
            d_under_leng_rig = leng2undersate_distance(undersateline[0], undersateline[1],
                                        undersateline[2], satestripelengline[2])
            if undersateline[2]>satestripelengline[2]:
                declination = get_declination_Nagative(d_under_leng_rig, h, w)
            else:
                declination = get_declination(d_under_leng_rig, h, w)
            DECLINATION.append(declination)

            p = P #/ (180 / np.pi)
            #     print(p)
            if abs(declination) <= p:
                if np.random.random()>0.5:
                    grid_U_right.append(grid_u)
                    grid_U_right_num.append(i)

        # print ('grid_U_right:', grid_U_right)
        # print(grid_U_right_num)
        print('num(grid_U_right)', len(grid_U_right))
        num_grid_U_right = len(grid_U_right)
        if num_grid_U_right == 0:
            # print('enough')
            break

        grid_T_right = []
        grid_T_right_num = []
        for _ in grid_U_right_num:
            grid_Ttemp_num = []
            grid_u = grid_all[_]
            for j in range(len(grid_all)):
                grid_t = grid_all[j]

                satestripelengline_u = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_u[3][0],
                                                               grid_u[3][1])
                satestripelengline_t = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_t[1][0],
                                                               grid_t[1][1])


                d_u_t_right = leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                            satestripelengline_u[2], satestripelengline_t[2])
                d_u_under = leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                                    satestripelengline_u[2], undersateline[2])
                stripe_wide_right = get_stripe_width(d_u_under, h, w)
                stripe_wide_right = stripe_wide_right * 0.0000089932202929999989

                satestripewideline_t = get_satestripe_wideline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_t[0][0],
                                                               grid_t[0][1])
                satestripewideline_u = get_satestripe_wideline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_u[0][0],
                                                               grid_u[0][1])

                if d_u_t_right <= stripe_wide_right and abs(satestripewideline_u[2]) >= abs(satestripewideline_t[2]):
                    #             grid_Ttemp.append(grid_t)
                    grid_Ttemp_num.append(j)
            #     grid_T_right.append(grid_Ttemp)
            grid_T_right_num.append(grid_Ttemp_num)

            grid_T_right_num_1 = np.unique([k for l in grid_T_right_num for k in l])
        for gtrm in range(len(grid_T_right_num_1)):
            grid_T_right.append(grid_all[grid_T_right_num_1[gtrm]])

        print('num(grid_T_right):', len(grid_T_right))

        grid_ut_right = []
        for _ in grid_U_right_num:
            #     grid_U[_]
            #     grid_T[_]
            for __ in grid_T_right_num_1:
                #         grid_T[_][__]
                grid_u_t = (grid_all[_], grid_all[__])
                grid_ut_right.append(grid_u_t)

        print('num(grid_ut_right):', len(grid_ut_right))

        stripe4point_right = []
        for _ in range(len(grid_ut_right)):
            u_leftup = grid_ut_right[_][0][1]
            t_rightup = grid_ut_right[_][1][2]
            satestripelengline_ = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                          undersate2[0], undersate2[1],
                                                          u_leftup[0],
                                                          u_leftup[1])
            undersateline_ = get_undersate_line(undersate1[0], undersate1[1],
                                                undersate2[0], undersate2[1])

            d_under_leng_stripe_rig = leng2undersate_distance(undersateline_[0], undersateline_[1],
                                        undersateline_[2], satestripelengline_[2])
            stripe_wide_stripe_ = get_stripe_width(d_under_leng_stripe_rig, h, w)
            stripe_wide_stripe_ = stripe_wide_stripe_ * 0.0000089932202929999989
            other_satestripelengline_ = get_satestripe_other_lengline(satestripelengline_[0],
                                                                      satestripelengline_[1],
                                                                      satestripelengline_[2],
                                                                      stripe_wide_stripe_)
            satestripewideline_ = get_satestripe_wideline(undersate1[0], undersate1[1],
                                                          undersate2[0], undersate2[1],
                                                          t_rightup[0],
                                                          t_rightup[1])
            other_satestripewideline_ = get_satestripe_other_wideline(satestripewideline_[0],
                                                                      satestripewideline_[1],
                                                                      satestripewideline_[2],
                                                                      T0, T1, v, 0)
            # print satestripelengline_, other_satestripelengline_, satestripewideline_, other_satestripewideline_


            stripe_leftdown = cross_point(satestripelengline_[0],
                                          satestripelengline_[1],
                                          satestripelengline_[2],
                                          other_satestripewideline_[0],
                                          other_satestripewideline_[1],
                                          other_satestripewideline_[2])

            stripe_leftup = cross_point(satestripelengline_[0],
                                        satestripelengline_[1],
                                        satestripelengline_[2],
                                        satestripewideline_[0],
                                        satestripewideline_[1],
                                        satestripewideline_[2])

            stripe_rightup = cross_point(satestripewideline_[0],
                                         satestripewideline_[1],
                                         satestripewideline_[2],
                                         other_satestripelengline_[0],
                                         other_satestripelengline_[1],
                                         other_satestripelengline_[2])

            stripe_rightdown = cross_point(other_satestripelengline_[0],
                                           other_satestripelengline_[1],
                                           other_satestripelengline_[2],
                                           other_satestripewideline_[0],
                                           other_satestripewideline_[1],
                                           other_satestripewideline_[2])

            # print (stripe_leftdown, stripe_leftup, stripe_rightup, stripe_rightdown)
            stripe4point_right.append([stripe_leftdown, stripe_leftup, stripe_rightup, stripe_rightdown])
        print('num(stripe4point_right):', len(stripe4point_right))
        stripe4point = stripe4point_right



    listp = []
    listi = []
    for i in range(len(stripe4point)):
        listp.append(geometry.Polygon(stripe4point[i]))
        listi.append(str(sat_name) + str(t) + '-' + str(i))
    cq = geopandas.GeoSeries(listp,
                             index=listi,  # 构建一个索引字段
                             crs='EPSG:4326',  # 坐标系是：WGS 1984
                             )

    cq.to_file('E:\\arcpy-\\monggulia_fire\\stripe\\'+str(sat_name)+ '_'+str(sensor)+ '_'+str(data)+ '_'+str(times) +'_stripe_' + str(t) + 's.shp', driver='ESRI Shapefile', encoding='utf-8')

    basetime_stripe4point.append(stripe4point)

print('num(basetime_stripe4point):', len(basetime_stripe4point))
basetime_stripe4point = [s for p in basetime_stripe4point for s in p]
end_time = time.time()

with open('E:\\arcpy-\\monggulia_fire\\stripe\\'+str(sat_name) + '_'+str(sensor)+ '_'+ str(data)+ '_'+str(times) +'_stripe4point.txt', "w") as file:
    for s in basetime_stripe4point:
        file.write(str(s) + "\n")

num_basetime_stripe4point=len(basetime_stripe4point)
if num_basetime_stripe4point !=0:

    listp = []
    listi = []
    for i in range(len(basetime_stripe4point)):
        listp.append(geometry.Polygon(basetime_stripe4point[i]))
        listi.append(str(sat_name) + str(t) + '-' + str(i))
    cq = geopandas.GeoSeries(listp,
                             index=listi,
                             crs='EPSG:4326',
                             )
    cq.to_file('E:\\arcpy-\\monggulia_fire\\stripe\\' + str(sat_name) + '_'+str(sensor)+ '_'+str(data)+ '_'+str(times) + '_stripe_all.shp', driver='ESRI Shapefile',
               encoding='utf-8')
    print('num(basetime_stripe4point_all):', len(basetime_stripe4point))
    print("time cost:", end_time - start_time, "s")
else:
    print('ok,this satellite dont pass target area')
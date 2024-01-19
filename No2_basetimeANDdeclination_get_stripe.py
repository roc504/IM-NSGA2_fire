"""
@File    : No2_basetimeANDdeclination_get_stripe.py
@Author  : roc
@Time    : 2023/3/14 19:30
"""
import random

'''
考虑开关机时间与侧摆角，基于格网生成卫星条带结果
'''
import shapefile
# import No1_get_fishnet#todo 连接No1
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
cal_line_stime='2023-04-10 03:27:30'#计算星下点直线的开始时间点,根据xxx_undersatellet_line.xlsx文件里的时间填，最好两个临近时间，保证开始点与结束点构成的直线受地球曲率影像最小#gf22023-01-19 02:30:00\sentinel2023-01-19 03:09:10\fy3a2023-01-19 06:41:00\jl2023-01-19 04:11:00\gj2b2023-01-18 22:39:00\gf12023-01-20 02:56:00
cal_line_etime='2023-04-10 03:28:00'#计算星下点直线的结束时间点#gf22023-01-19 02:35:00\sentinel2023-01-19 03:09:20\fy3a2023-01-19 06:42:00jl2023-01-19 04:12:00\gj2b2023-01-18 22:40:00\gf12023-01-20 02:57:00
start_time = time.time()
pass_time = '2023-04-10 03:27:30'#gaofen2023-01-19 02:30:00、sentinel2023-01-19 03:09:10、fy3a2023-01-19 06:41:00、jl2023-01-19 04:11:16#前一时刻时间
'''=轨道高度、视场角='''
h , w = 778000 ,4.23#卫星高度，视场角 2w=arctan(幅宽/2h)*(180 / np.pi)
P = 26#/(180 / np.pi)  # 高分2 的侧摆角,度换算成弧度'''
orbit_orientation = 'right'#'right' # 卫星轨道偏向，left是指'\'轨道，向左倾斜，right是‘/’轨道，向右倾斜
open_time='2023,4,10,3,27,3'#选择开关机时间#gaofen2:2023,01,19,2,33,10
close_time='2023,4,10,3,28,23'#选择开关机时间



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
orbit_speed = satspeed_n(cal_line_stime)# TODO 取前一个点的速度，或者取平均值
# print("星下点1坐标：",undersate1_n)
# print("星下点2坐标：",undersate2_n)
undersate1=undersate1_n
undersate2=undersate2_n


# sf = shapefile.Reader(No1_get_fishnet.shp_selected)
sf = shapefile.Reader('E:/arcpy-/monggulia_fire/maybe_fire_area1_fishnet_sele.shp')
shapes = sf.shapes()
lens = len(shapes)

grid_all = []#所有格网集合
for q in range(lens):
    grid_all.append(shapes[q].points)
# print "grid_all:", grid_all
print ("num(grid_all):", len(grid_all))
# 星下点轨迹直线方程
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

#条带侧边直线方程
def get_satestripe_lengline(x1, y1, x2, y2, x3, y3):  # x1,y1,x2,y2是星下点坐标，x3,y3是单元格的一个角坐标
    sign = 1
    A = y2 - y1
    if A < 0:
        sign = -1
        A = sign * A
    B = sign * (x1 - x2)
    C = sign * (x2 * y1 - x1 * y2)

    # 过单元格一角点，平行于星下点直线
    # 已知Ax+By+C=0,过(m,n)与之平行，平行的直线方程：A(x-m)+B(y-n) = 0
    C3 = -(A * x3 + B * y3)
    return [A, B, C3]

#条带侧边与星下点轨迹距离d
def leng2undersate_distance(A,B,C1,C2):#A,B星下点轨迹or侧边的AB，C1是星下点，C2是侧边
    #两直线之间的距离d = \C1-C2\/√(A^2+B^2)
    d = abs(C1-C2)/math.sqrt(A * A + B * B)
    return d

#侧摆角
def get_declination(d,h,w): #这里的h单位是m，d要换算
    d_ = d/0.0000089932202929999989 #1米=0.0000089932202929999989
    declination = np.arctan(d_/h)*(180 / np.pi) - w/2 # arctan计算出来的是弧度，所以要乘（180/pi）
    return declination
#向左侧摆为正，侧摆角为负，就说明向右侧摆
def get_declination_Nagative(d,h,w): #这里的h单位是m，d要换算
    d_ = d/0.0000089932202929999989 #1米=0.0000089932202929999989
#     declination = np.arctan(d_/h)*(180 / np.pi) - w/2 # arctan计算出来的是弧度，所以要乘（180/pi）
    declination = np.arctan(d_/h)*(180 / np.pi) + w/2
    return declination
#条带宽度
def get_stripe_width(d,h,w):#d代表侧边与星下点轨迹距离，h代表卫星高度，w代表视场角
    if np.arctan(d/h)*(180 / np.pi) > w:
        stripe_width = d-h*np.tan((np.arctan(d/h)*(180 / np.pi)-w)*(np.pi / 180))
    else:
        stripe_width = d+h*np.tan((w-np.arctan(d/h)*(180 / np.pi))*(np.pi / 180))
    return stripe_width

#条带宽边
def get_satestripe_wideline(x1, y1, x2, y2, x3, y3):  # x1,y1,x2,y2是星下点坐标，
    # x3,y3是单元格的一个角坐标
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

#另一长边直线方程
def get_satestripe_other_lengline(A,B,C,distance):#ABC是侧边直线一般式系数，
    #distance条带宽度
    #两直线之间的距离d = \C1-C2\/√(A^2+B^2)
    #所以新直线的C计算公式：C1=C2±d√(A^2+B^2)
    f = distance * math.sqrt(A * A + B * B)
    m1 = C + f
    m2 = C - f
    # result = 值1 if 条件 else 值2
    C2 = m1 if A < 0 else m2
    return [A, B, C2]


# 选择开关机时间段
def select_times(start, end, frmt="%Y,%m,%d,%H,%M,%S"):
    stime = datetime.datetime.strptime(start, frmt)
    etime = datetime.datetime.strptime(end, frmt)
    #     stime_temp = (stime+datetime.timedelta(seconds=+1))#.strftime("%Y-%m-%d %H:%M:%S")
    #     etime_temp = (etime+datetime.timedelta(seconds=-1))#.strftime("%Y-%m-%d %H:%M:%S")
    time_pass = (etime - stime).seconds  # 两个时间差了几秒
    time_ssele = []
    time_esele = []
    for c in range(time_pass + 1):  # 计算两个时间差内有多少时间组合
        if c % 20 == 0:#以20秒为基数生成一个开关组合
            for d in range(c + 1, time_pass + 1):  # time_pass+1包含结束的那一秒
                #             print(str(j),'-',str(i))
                if d % 20 == 0:
                    stime_temp = (stime + datetime.timedelta(seconds=+c))
                    etime_temp = (stime + datetime.timedelta(seconds=+d))
                    time_ssele.append(stime_temp)
                    time_esele.append(etime_temp)
        #             print(stime_temp,etime_temp)

    return [time_ssele, time_esele]

# T0 = time_list[0][4]
# T1 = time_list[1][4]

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
    if tit == 1:  # tit==1为左斜，==0为右斜
        # result = 值1 if 条件 else 值2
        C2 = m1 if C > m1 else m2
    else:
        C2 = m1 if C < m1 else m2

    return [A, B, C2]


#两直线方程交点
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

#判断格网四点是否在stripe矩形内
# 计算(x1,y1)(x,y)、(x2,y2)(x,y)向量的叉乘，a(x1,y1),b(x2,y2)的叉乘为x1y2-y1x2
def GetCross(x1,y1,x2,y2,x,y):
    a=(x2-x1,y2-y1)
    b=(x-x1,y-y1)
    return a[0]*b[1]-a[1]*b[0]

# 判断(x,y)是否在矩形内部
def isInSide(x1,y1,x2,y2,x3,y3,x4,y4,x,y):
    return GetCross(x1,y1,x2,y2,x,y)*GetCross(x3,y3,x4,y4,x,y)>=0 and GetCross(x2,y2,x3,y3,x,y)*GetCross(x4,y4,x1,y1,x,y)>=0
#四点都在矩形内，返回True
def gridall_in_stripe(stripex,gridx):#stripex是由ut选出的矩形的索引，gridx是所有格网的索引
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


#星下点坐标
# undersate1,undersate2 = shapes[0].points[1],shapes[4].points[1]#第46单元格的左上点，第2单元格的左上点
#gaofen2
'''v=orbit_speed*1000 #卫星速度
h , w = 613000 , 4.2#卫星高度，视场角 °2w=arctan(幅宽/2h)*(180 / np.pi)
P = 35#/(180 / np.pi)  # 高分2 的侧摆角,度换算成弧度'''

'''#sentinel2b
v=orbit_speed*1000 #卫星速度
h , w = 786000 , 20.6#卫星高度，视场角 °2w=arctan(幅宽/2h)*(180 / np.pi)
P = 10.3#/(180 / np.pi)  # 侧摆角,度换算成弧度'''

'''#fy3a
sat_name = 'fy3a'
v=orbit_speed*1000 #卫星速度
h , w = 836000 , 8.2#卫星高度，视场角 °2w=arctan(幅宽/2h)*(180 / np.pi)
P = 4.1#/(180 / np.pi)  # 侧摆角'''

v=orbit_speed*1000 #卫星速度
time_list = select_times(open_time, close_time)

basetime_stripe4point=[]
for t in range(len(time_list[0])):
    T0 = time_list[0][t]
    T1 = time_list[1][t]

    if orbit_orientation == 'left':

        # “\”左斜条带模式
        grid_U_left = []  # 所有可用的u单元格集合，星下点可以不在研究区，在很远的地方，侧偏角照射到研究区
        grid_U_left_num = []  # 获取出的U格网的编号

        for i in range(len(grid_all)):
            grid_u = grid_all[i]
            # print 'grid_u:',grid_u
            undersateline = get_undersate_line(undersate1[0], undersate1[1],
                                               undersate2[0], undersate2[1])
            satestripelengline = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                         undersate2[0], undersate2[1],
                                                         grid_u[0][0],
                                                         grid_u[0][1])  # grid_u[0][0]代表grid_u格网0号点（左下点）的x
            d_under_leng_lef = leng2undersate_distance(undersateline[0], undersateline[1],
                                        undersateline[2], satestripelengline[2])
            if undersateline[2]>satestripelengline[2]:
                declination = get_declination_Nagative(d_under_leng_lef, h, w)
            else:
                declination = get_declination(d_under_leng_lef, h, w)  # 偏移角
            # print( 'declination:', declination)
            p = P #/ (180 / np.pi) # 不需要转换弧度
            # print(abs(declination) <= p)
            if abs(declination) <= p:
                if np.random.random()>0.5:  # 随机在结果里选择格网
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
                # 作过t格网右上点直线平行于星下点的直线
                satestripelengline_u = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_u[0][0],
                                                               grid_u[0][1])
                satestripelengline_t = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_t[1][0],
                                                               grid_t[1][1])

                # 两平行线的距离
                d_u_t_left = leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                            satestripelengline_u[2], satestripelengline_t[2])#过u点和t点的两条平行线间的距离
                d_u_under=leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                            satestripelengline_u[2], undersateline[2])
                stripe_wide_left = get_stripe_width(d_u_under, h, w)#根据最左侧点到星下点距离求得条带宽度
                stripe_wide_left = stripe_wide_left * 0.0000089932202929999989

                # 求互相平行的两个垂线
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
            # 去除重复的点
            grid_T_left_num_1 = np.unique([b for a in grid_T_left_num for b in a])
        for gtlm in range(len(grid_T_left_num_1)):
            grid_T_left.append(grid_all[grid_T_left_num_1[gtlm]])
        # grid_T是包含所有u单元格对应的t单元格,每个[[]]里对应一个u单元格
        # print ('grid_T_left:',grid_T_left)
        print('num(grid_T_left):', len(grid_T_left))
        # print(grid_T_left_num_1)
        # print(len(grid_T_left_num_1))

        grid_ut_left = []
        for _ in grid_U_left_num:
            #     grid_U[_]
            #     grid_T[_]
            for __ in grid_T_left_num_1:
                #         grid_T[_][__]
                grid_u_t = (grid_all[_], grid_all[__])
                grid_ut_left.append(grid_u_t)
        # print (grid_ut_left[0])
        # 这个grid_ut是合适的u单元格和相对应的t单元格的集合
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
            # print satestripelengline_, other_satestripelengline_, satestripewideline_, other_satestripewideline_

            # 左下点坐标
            stripe_leftdown = cross_point(satestripelengline_[0],
                                          satestripelengline_[1],
                                          satestripelengline_[2],
                                          other_satestripewideline_[0],
                                          other_satestripewideline_[1],
                                          other_satestripewideline_[2])
            # 左上点坐标
            stripe_leftup = cross_point(satestripelengline_[0],
                                        satestripelengline_[1],
                                        satestripelengline_[2],
                                        satestripewideline_[0],
                                        satestripewideline_[1],
                                        satestripewideline_[2])
            # 右上点坐标
            stripe_rightup = cross_point(satestripewideline_[0],
                                         satestripewideline_[1],
                                         satestripewideline_[2],
                                         other_satestripelengline_[0],
                                         other_satestripelengline_[1],
                                         other_satestripelengline_[2])
            # 左下点坐标
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
        # “/”右斜条带模式
        grid_U_right = []  # 所有可用的u单元格集合，星下点可以不在研究区，在很远的地方，侧偏角照射到研究区
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
                                                         grid_u[3][1])  # grid_u[0][0]代表grid_u格网0号点（左下点）的x
            d_under_leng_rig = leng2undersate_distance(undersateline[0], undersateline[1],
                                        undersateline[2], satestripelengline[2])
            if undersateline[2]>satestripelengline[2]:
                declination = get_declination_Nagative(d_under_leng_rig, h, w)
            else:
                declination = get_declination(d_under_leng_rig, h, w)  # 偏移角
            DECLINATION.append(declination)
            #     print ('declination:', declination)
            p = P #/ (180 / np.pi)
            #     print(p)
            if abs(declination) <= p:
                if np.random.random()>0.5:#随机在结果里选择格网
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
                # 作过t格网右上点直线平行于星下点的直线
                satestripelengline_u = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_u[3][0],
                                                               grid_u[3][1])
                satestripelengline_t = get_satestripe_lengline(undersate1[0], undersate1[1],
                                                               undersate2[0], undersate2[1],
                                                               grid_t[1][0],
                                                               grid_t[1][1])

                # 两平行线的距离
                d_u_t_right = leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                            satestripelengline_u[2], satestripelengline_t[2])
                d_u_under = leng2undersate_distance(satestripelengline_u[0], satestripelengline_u[1],
                                                    satestripelengline_u[2], undersateline[2])
                stripe_wide_right = get_stripe_width(d_u_under, h, w)
                stripe_wide_right = stripe_wide_right * 0.0000089932202929999989
                # 求互相平行的两个垂线
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
            # 去除重复的点
            grid_T_right_num_1 = np.unique([k for l in grid_T_right_num for k in l])
        for gtrm in range(len(grid_T_right_num_1)):
            grid_T_right.append(grid_all[grid_T_right_num_1[gtrm]])
        # grid_T是包含所有u单元格对应的t单元格,每个[[]]里对应一个u单元格
        # print ('grid_T_right:',grid_T_right)
        print('num(grid_T_right):', len(grid_T_right))

        grid_ut_right = []
        for _ in grid_U_right_num:
            #     grid_U[_]
            #     grid_T[_]
            for __ in grid_T_right_num_1:
                #         grid_T[_][__]
                grid_u_t = (grid_all[_], grid_all[__])
                grid_ut_right.append(grid_u_t)
        # 这个grid_ut是合适的u单元格和相对应的t单元格的集合
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
            # d星下点与侧边距离
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

            # 左下点坐标
            stripe_leftdown = cross_point(satestripelengline_[0],
                                          satestripelengline_[1],
                                          satestripelengline_[2],
                                          other_satestripewideline_[0],
                                          other_satestripewideline_[1],
                                          other_satestripewideline_[2])
            # 左上点坐标
            stripe_leftup = cross_point(satestripelengline_[0],
                                        satestripelengline_[1],
                                        satestripelengline_[2],
                                        satestripewideline_[0],
                                        satestripewideline_[1],
                                        satestripewideline_[2])
            # 右上点坐标
            stripe_rightup = cross_point(satestripewideline_[0],
                                         satestripewideline_[1],
                                         satestripewideline_[2],
                                         other_satestripelengline_[0],
                                         other_satestripelengline_[1],
                                         other_satestripelengline_[2])
            # 左下点坐标
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


    # if orbit_orientation == 'right': #判断选左斜还是右斜轨道，以最后确定stripe的四点集合
    #     stripe4point = stripe4point_right
    # else:
    #     stripe4point = stripe4point_left
    # # stripe4point = list(chain(stripe4point_left, stripe4point_right))#将左斜右斜所有stripe加在一起
    # print('num(stripe4point):', len(stripe4point))

    # stripe4point转成shp
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
    # 所有条带合一个shp
    listp = []
    listi = []
    for i in range(len(basetime_stripe4point)):
        listp.append(geometry.Polygon(basetime_stripe4point[i]))
        listi.append(str(sat_name) + str(t) + '-' + str(i))
    cq = geopandas.GeoSeries(listp,
                             index=listi,  # 构建一个索引字段
                             crs='EPSG:4326',  # 坐标系是：WGS 1984
                             )
    cq.to_file('E:\\arcpy-\\monggulia_fire\\stripe\\' + str(sat_name) + '_'+str(sensor)+ '_'+str(data)+ '_'+str(times) + '_stripe_all.shp', driver='ESRI Shapefile',
               encoding='utf-8')
    print('num(basetime_stripe4point_all):', len(basetime_stripe4point))
    print("time cost:", end_time - start_time, "s")
else:
    print('ok,this satellite dont pass target area')
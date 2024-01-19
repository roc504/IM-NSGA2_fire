#coding:utf-8
"""
@File    : sar_get_utgrid_set.py
@Author  : roc
@Time    : 2023/2/13 20:18
"""

import shapefile
from pyproj import Proj,transform
import numpy as np

#判断格网四点是否在stripe圆内
import math
#判断(x,y)点是否在雷达圆内
def isInCircle(x0,y0,r,x,y):
    ds = math.sqrt((x-x0)**2+(y-y0)**2)
    if ds <= r:
        return True

#todo 雷达圆心已知，圆心经过路线已知。可求两边平行的长边，平行距离r

#'''三点求圆，返回圆心和半径'''
def get_circle(p1, p2, p3):
    x, y, z = p1[0] + p1[1] * 1j, p2[0] + p2[1] * 1j, p3[0] + p3[1] * 1j
    w = z - x
    w /= y - x
    c = (x - y) * (w - abs(w) ** 2) / 2j / w.imag - x
    return (-c.real, -c.imag), abs(c + x)

def get_circle(x0,y0,a,b,r):
    if (x0-a)**2+(y0-b)**2-r**2==0:
        return True


'''
c, r = get_circle((0, 1), (0, -1), (-1, 0))
print('({:.2f},{:.2f}),r= {:.2f}'.format(c[0], c[1], r))
# 格网四顶点都在圆内，返回True
def gridall_in_circle():
    leftdown = isInCircle(x0, y0, r, x, y)
    leftup = isInCircle(x0, y0, r, x, y)
    rightdown =isInCircle(x0, y0, r, x, y)
    rightup =isInCircle(x0, y0, r, x, y)
    if leftdown and leftup and rightdown and rightup:
        return True
'''
n=2
A = [[0 for i in range(n)] for i in range(n)]
a = [0]*n
print(A)

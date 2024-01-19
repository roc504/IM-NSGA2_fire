"""
@File    : mult_test.py
@Author  : roc
@Time    : 2023/4/26 16:09
"""

# import time

import shapefile
import numpy as np
# import math
import geatpy as ea

from pylab import *
import matplotlib; matplotlib.use('TKAgg')
import matplotlib.pyplot as plt
# from collections import Counter
# from mpl_toolkits.mplot3d import Axes3D # 空间三维画图
mpl.rcParams['font.sans-serif'] = ['SimHei']
mpl.rcParams['axes.unicode_minus'] = False

sf = shapefile.Reader('E:/arcpy-/monggulia_fire/maybe_fire_area1_fishnet_sele.shp')
shapes = sf.shapes()
lens = len(shapes)
grid_all = []#所有格网集合
for q in range(lens):
    grid_all.append(shapes[q].points)
print("num(grid_all):", len(grid_all))

def read_stripe_masage(sat_name):
    # sat_name='CB04_9_1_sele'#gf1_test
    # stripe4point_sat=[]
    with open('D:\\stripe_txt\\st\\' + str(sat_name) + '_sele_stripe4point.txt', "r",
              encoding='utf-8') as f:  # 打开文本
    # with open('E:\\arcpy-\\monggulia_fire\\stripe\\'+str(sat_name)+'_stripe4point.txt', "r", encoding='utf-8') as f:  #打开文本
        stripe4point = f.readlines()  # 读取文本
        stripe4point_ = [eval(s) for s in stripe4point]
        # for i in range(len(stripe4point_)):
        #     if i%1==0:
        #         stripe4point_sat.append(stripe4point_[i])
    stripe=len(stripe4point_)
    return stripe4point_,stripe
    # print('num(stripe4point_'+sat_name+')',stripe)

'''需要的卫星'''
sat_list=['ZY1F_VNIC_9_11','GF1C_PMS_9_1','GF7_DLC_9_1','HJ2B_CCD_9_11','HJ2B_CCD_10_1',
          'HJ2A_CCD_10_1','ZY1E_VNIC_10_11','GF5B_AHSI_10_1','CB04_IRS_10_1','ZY1F_IRS_11_1',
          'CB04A_WFI_10_1','CB04A_MUX_11_1','CB04_WFI_11_1','HJ2A_CCD_11_1','GF3C_SAR_11_1',
          'Sentinel2B_MSI_9_1','WORLDVIEW3_PMS_10_1','TERRA_MODIS_9_1','TERRA_MODIS_10_1','TERRA_MODIS_11_1',
          'GF1D_PMI_9_1','Landsat8_OLI_10_1','GF2_PMI_10_1','HJ2A_HSI_9_1','Gf7_DLC_11_1']
#生成各卫星的条带坐标条带
Stripepoints_all=[]
for i in sat_list:
    Stripepoints_all.append(read_stripe_masage(i)[0])

for k in range(len(sat_list)):
    m=sat_list[k]
    # print(m)
    exec(f'stripe_{m} = Stripepoints_all[k]')  # 这样运行出来，直接stripe_ZY1F_VNIC_9_1就直接是条带的坐标列表

'''
stripe_ZY1F_VNIC_9_1=Stripepoints_all[0]#stripe_gf1,[0]是具体条带的四点坐标，[1]是有多少条带
stripe_GF1B_PMS_9_1=Stripepoints_all[1]
stripe_HJ2B_CCD_9_1=Stripepoints_all[2]
stripe_HJ2B_HSI_9_1=Stripepoints_all[3]
stripe_HJ2A_CCD_11_1=Stripepoints_all[4]
stripe_Sentinel2B_MSI_9_1=Stripepoints_all[5]
stripe_ZY1E_VNIC_10_1=Stripepoints_all[6]
stripe_ZY1E_AHSI_10_1=Stripepoints_all[7]
stripe_CB04_IRS_10_1=Stripepoints_all[8]
stripe_ZY1F_VNIC_11_1=Stripepoints_all[9]
stripe_CB04A_WFI_10_1=Stripepoints_all[10]
stripe_WORLDVIEW3_10_2=Stripepoints_all[11]
stripe_ZY1F_AHSI_9_2=Stripepoints_all[12]
stripe_GF3C_11_1=Stripepoints_all[13]
stripe_GF6_PMI_10_1=Stripepoints_all[14]
stripe_GF1D_PMI_9_1=Stripepoints_all[15]
stripe_Landsat8_OLI_10_1=Stripepoints_all[16]
stripe_GF2_PMI_10_1=Stripepoints_all[17]
stripe_HJ2A_HSI_9_1=Stripepoints_all[18]
stripe_Gf7_DLC_11_1=Stripepoints_all[19]
'''
#生成各卫星的条带数
No_all=[]
for i in sat_list:
    No_all.append(read_stripe_masage(i)[1])

for k in range(len(sat_list)):
    exec(f"no{k+1} = No_all[k]")
'''
no1=No_all[0]
no2=No_all[1]
no3=No_all[2]
no4=No_all[3]
no5=No_all[4]
no6=No_all[5]
no7=No_all[6]
no8=No_all[7]
no9=No_all[8]
no10=No_all[9]
no11=No_all[10]
no12=No_all[11]
no13=No_all[12]
no14=No_all[13]
no15=No_all[14]

no16=No_all[15]
no17=No_all[16]
no18=No_all[17]
no19=No_all[18]
no20=No_all[19]
'''

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


# todo 每个covered单独计算，[0,no1],[0,no2]..,
def covered_num(stripename,num):
    covered=[]
    for _ in range(0,num):#(0,28)
        a = []
        for __ in range(len(grid_all)):
            if gridall_in_stripe(stripename,_,__):
                a.append(__)
        # print a
        covered.append(a)
    if covered == []:
        covered = [[] for i in range(1)]
    return covered
    # print('covered',covered[:20])
    # print('num-covered',len(covered))

#这里covered_num的第一个参数直接写stripe_卫星名称（前面列出来的卫星）
covered1=covered_num(stripe_ZY1F_VNIC_9_11,no1)
print('num-covered1',len(covered1))
covered2=covered_num(stripe_GF1C_PMS_9_1,no2)
print('num-covered2',len(covered2))
covered3=covered_num(stripe_GF7_DLC_9_1,no3)
print('num-covered3',len(covered3))
covered4=covered_num(stripe_HJ2B_CCD_9_11,no4)
print('num-covered4',len(covered4))
covered5=covered_num(stripe_HJ2B_CCD_10_1,no5)
print('num-covered5',len(covered5))
covered6=covered_num(stripe_HJ2A_CCD_10_1,no6)
print('num-covered6',len(covered6))
covered7=covered_num(stripe_ZY1E_VNIC_10_11,no7)
print('num-covered7',len(covered7))
covered8=covered_num(stripe_GF5B_AHSI_10_1,no8)
print('num-covered8',len(covered8))
covered9=covered_num(stripe_CB04_IRS_10_1,no9)
print('num-covered9',len(covered9))
covered10=covered_num(stripe_ZY1F_IRS_11_1,no10)
print('num-covered10',len(covered10))
covered11=covered_num(stripe_CB04A_WFI_10_1,no11)
print('num-covered11',len(covered11))
covered12=covered_num(stripe_CB04A_MUX_11_1,no12)
print('num-covered12',len(covered12))
covered13=covered_num(stripe_CB04_WFI_11_1,no13)
print('num-covered13',len(covered13))
covered14=covered_num(stripe_HJ2A_CCD_11_1,no14)
print('num-covered14',len(covered14))
covered15=covered_num(stripe_GF3C_SAR_11_1,no15)
print('num-covered15',len(covered15))
covered16=covered_num(stripe_Sentinel2B_MSI_9_1,no16)
print('num-covered16',len(covered16))
covered17=covered_num(stripe_WORLDVIEW3_10_2,no17)
print('num-covered17',len(covered17))
covered18=covered_num(stripe_TERRA_MODIS_9_1,no18)
print('num-covered18',len(covered18))
covered19=covered_num(stripe_TERRA_MODIS_10_1,no19)
print('num-covered19',len(covered19))
covered20=covered_num(stripe_TERRA_MODIS_11_1,no20)
print('num-covered20',len(covered20))
covered21=covered_num(stripe_GF1D_PMI_9_1,no21)
print('num-covered21',len(covered21))
covered22=covered_num(stripe_Landsat8_OLI_10_1,no22)
print('num-covered22',len(covered22))
covered23=covered_num(stripe_GF2_PMI_10_1,no23)
print('num-covered23',len(covered23))
covered24=covered_num(stripe_HJ2A_HSI_9_1,no24)
print('num-covered24',len(covered24))
covered25=covered_num(stripe_Gf7_DLC_11_1,no25)
print('num-covered25',len(covered25))

#把所有covered放在一个列表里，方便后面循环
covered_all=[covered1,covered2,covered3,covered4,covered5,
             covered6,covered7,covered8,covered9,covered10,
             covered11,covered12,covered13,covered14,covered15,
             covered16,covered17,covered18,covered19,covered20,
             covered21,covered22,covered23,covered24,covered25]

# TODO 这个函数改为，将每次变化后的条带覆盖多少1求出来
def get_covered_grid_num(x,covered_all):
    '''
    这个函数将输入的x（形式为NIND×D的种群），转换成对应条带覆盖的格网数
    输出也是NIND×D
    '''
    NN=[]
    for temp in range(x.shape[1]):
        n = []
        for i in x[:, temp]:
            c=covered_all[temp][int(i)]
            n.append(len(c))
        N=np.array(n)
        NN.append(N)
    data=np.stack(NN,1)
    return data

def stripe_covered_grid(Phen,covered_all):
    '''
    存下了在这个种群中每个个体的每个基因的条带所覆盖的格网对应的卫星数和条带数，形式为{‘格网编号’：[(卫星编号x，条带编号s),()..]}
    输出形式为NIND×1
    为function1提供输入
    '''
    all_set=[]#100个字典，每个字典里存的是这个个体20个卫星条带覆盖的格网编号（下标）
    # one_set={}#创建在这里可以获得整个种群对应覆盖的格网覆盖情况（每个格网由哪些条带覆盖）
    for i in range(Phen.shape[0]):
        one_set={}#这个字典里存的是20个基因的条带覆盖的格网编号（下标）。在这里获得每个个体对应覆盖的格网覆盖情况
        for j in range(Phen.shape[1]):
            Phen_num=Phen[i,j]
            # print(Phen_num)
            covered_grid=covered_all[j][Phen_num]
            # print(covered_grid)
            for k in covered_grid:
                if one_set.__contains__(str(k)):
                    one_set[str(k)].append((j,Phen_num))
                else:
                    one_set[str(k)]=[(j,Phen_num)]

        all_set.append(one_set)#如果one_set字典创建在整个循环外，注释掉这句，如果创建在第一层循环，保留
    return all_set
# TODO 运行上面函数得到格网覆盖情况
# all_set=stripe_covered_grid(Phen,covered_all)
# a=get_covered_grid_num(Phen, covered1, covered2, covered3, covered4, covered5, covered6)
# print(a)

"""============================目标函数定义============================"""
"""
avaliable：可获得性
unitcost：单位价格/k
untiltime：距离灾害发生时间/h


"""
#第一层权重，可获得性
# import numpy as np
'''可获得性'''
avaliable = np.array([6, 5, 6, 2, 2,
                      2, 6, 6, 2, 6,
                      2, 2, 2, 2, 7,
                      1, 9, 3, 3, 3,
                      100, 100, 100, 100, 100])  # 实验用20颗卫星可获得性
aval = []
for a in avaliable:
    a = float(a - np.max(avaliable)) / (np.min(avaliable) - np.max(avaliable))
    aval.append(a)
print('aval',aval)
# a1, a2, a3 ,a4, a5, a6, a7, a8, a9, a10, a11=aval[0], aval[1], aval[2], aval[3], aval[4], aval[5], aval[6], aval[7], aval[8], aval[9], aval[10]
aval_=[-5.0 if i ==-0.0 else i for i in aval]#-50.0
# a1_, a2_, a3_ ,a4_, a5_, a6_, a7_, a8_, a9_, a10_, a11_=aval_[0], aval_[1], aval_[2], aval_[3], aval_[4], aval_[5], aval_[6], aval_[7], aval_[8], aval_[9], aval_[10]
aval_arr=np.array(aval_)
print('aval_arr',aval_arr)
'''def function1(X1,para):#X1.shape->(1xD),para是可获得性的约束（数组）para.shape->(Dx1)

    # a1, a2, a3 ,a4, a5, a6=aval[0], aval[1], aval[2], aval[3], aval[4], aval[5]
    a1_, a2_, a3_ ,a4_, a5_, a6_, a7_, a8_, a9_, a10_, a11_=aval_[0], aval_[1], aval_[2], aval_[3], aval_[4], aval_[5], aval_[6], aval_[7], aval_[8], aval_[9], aval_[10]
    #0.98989898989899, 0.98989898989899, 1.0, 0.9696969696969697, -1.0, -1.0
    n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11=X1[0],X1[1],X1[2],X1[3],X1[4],X1[5],X1[6],X1[7],X1[8],X1[9], X1[10]#表现型里的随机初始值，代表条带编号
    # value = -(a1 * n1 + a2 * n2 + a3 * n3 + a4 * n4 + a5 * n5 + a6 * n6)
    # value = -(a1_*n1 + a2_*n2 + a3_*n3 + a4_*n4 + a5_*n5 + a6_*n6+ a7_*n7+ a8_*n8+ a9_*n9+ a10_*n10+ a11_*n11)
    paraT=para.T
    
    value=-(np.dot(X1,paraT))
    return value'''

def function1(Phen,para):
    '''求每个个体覆盖格网的可获得性'''
    all_set=stripe_covered_grid(Phen,covered_all)
    all_grid_aval_cul=[]#种群中各个个体的可获得性（100x1）
    for i in range(Phen.shape[0]):
        grid_aval_cul=[]#种群中个体的可获得性（这个个体覆盖的格网的可获得性累加）
        for key in all_set[i]:#遍历phen生成的覆盖格网
            # print (key, 'corresponds to', all_set[i][key])
            grid_aval=[]#每个格网的可获得性
            for value in range(len(all_set[i][key])):#遍历每一个个体覆盖的格网的value，形式为[(卫星编号x，条带编号s),(卫星编号x，条带编号s)..]
                # print (value, 'is', all_set[0][key][value])
                # print(all_set[0][key][value][0])
                # print(aval_[all_set[0][key][value][0]])
                grid_aval.append(para[all_set[i][key][value][0]])#[(卫星编号x，条带编号s)]中只要卫星编号x，以此检索对应可获得性

            #公式x=1-累积(1-aval_x)
            aval_result=1
            for aval in grid_aval:
                aval_result=aval_result*(1-aval)
            aval_result=1-aval_result
            grid_aval_cul.append(aval_result)
        grid_cul=np.sum(grid_aval_cul)*(-1)
        # print('第i个体的可获得性之和',grid_cul)
        all_grid_aval_cul.append(grid_cul)
    return all_grid_aval_cul

'''价格'''
unitcost = np.array([0.38, 6.9, 250, 2.4, 2.4,
                     2.4, 3.78, 13.9, 0, 0.38,
                     0, 0, 0, 2.4, 25,
                     0, 3750, 0, 0, 0,
                     6.94, 0.23, 54.3, 2.4, 250])  # 实验用6颗卫星单位价格/yuan,单元格10km2
cost = []
for c in unitcost:
    c = float(c - np.max(unitcost)) / (np.min(unitcost) - np.max(unitcost))
    cost.append(c)
cost_arr=np.array(cost)
#aaaaa
def function2(X2,para):#para是单位价格约束(数组

    # a1, a2, a3, a4, a5, a6 = aval[0], aval[1], aval[2], aval[3], aval[4], aval[5]
    a1_, a2_, a3_ ,a4_, a5_, a6_, a7_, a8_, a9_, a10_, a11_=aval_[0], aval_[1], aval_[2], aval_[3], aval_[4], aval_[5], aval_[6], aval_[7], aval_[8], aval_[9], aval_[10]

    # b1, b2, b3, b4, b5, b6, b7, b8, b9, b10 = cost[0], cost[1], cost[2], cost[3], cost[4], cost[5], cost[6], cost[7], cost[8], cost[9]
    b1, b2, b3 ,b4, b5, b6, b7, b8, b9, b10, b11=a1_*cost[0], a2_*cost[1], a3_*cost[2], a4_*cost[3], a5_*cost[4], a6_*cost[5], a7_*cost[6], a8_*cost[7], a9_*cost[8], a10_*cost[9], a11_*cost[10]
    #0.494949494949495, 0.395959595959596, 1.0 ,0.6787878787878787, 0.6787878787878787, 0.0, -0.1
    n1, n2, n3, n4, n5, n6, n7, n8, n9, n10, n11=X2[0],X2[1],X2[2],X2[3],X2[4],X2[5],X2[6],X2[7],X2[8],X2[9],X2[10]#表现型里的随机初始值，代表条带编号8
    # value = b1 * n1 + b2 * n2 + b3 * n3 + b4 * n4 + b5 * n5 + b6 * n6+ b7 * n7+ b8 * n8+ b9 * n9+ b10 * n10+ b10 * n11
    paraT = para.T
    value = np.dot(X2, paraT)#100x20·20x1->100x1，是这100个个体的结果
    return value


untiltime = np.array([11969, 50045, 11600, 13800, 101630,
                      98617, 98903, 98922, 135930, 186692,
                      97500, 185013, 224478, 186435, 206808,
                      11124, 137485, 7705, 96560, 185396,
                      14120, 135356, 97466, 12206,  226171])# 实验用6颗卫星距离灾害发生时间/min
def function3(X3,para_time):

    # a1, a2, a3, a4, a5, a6 = aval[0], aval[1], aval[2], aval[3], aval[4], aval[5]
    # a1_, a2_, a3_, a4_, a5_, a6_ = aval_[0], aval_[1], aval_[2], aval_[3], aval_[4], aval_[5]

    # untiltime = np.array([20.5, 22, 25.5, 30.5, 35.7, 45])
    untiltime = para_time
    # time = []
    # for t in untiltime:
    #     t = float(t - np.max(untiltime)) / (np.min(untiltime) - np.max(untiltime))
    #     time.append(t)
    # c1, c2, c3, c4, c5, c6 = a1 * time[0], a2 * time[1], a3 * time[2], a4 * time[3], a5 * time[4], a6 * time[5]
    # c1, c2, c3 ,c4, c5, c6=a1_*time[0], a2_*time[1], a3_*time[2], a4_*time[3], a5_*time[4], a6_*time[5]
    # c1, c2, c3, c4, c5, c6 = time[0], time[1], time[2], time[3], time[4], time[5]
    # n1, n2, n3, n4, n5, n6=X3[0],X3[1],X3[2],X3[3],X3[4],X3[5]#表现型里的随机初始值，代表条带编号
    # value = c1 * n1 + c2 * n2 + c3 * n3 + c4 * n4 + c5 * n5 + c6 * n6
    value = 0
    for i in range(D):
        if X3[i]!=0:#有覆盖单元格才计算
            if value <= untiltime[i]:
                value = untiltime[i]
            else:
                value = value
    # valuet = value
    return value


# Function to carry out NSGA-II's fast non dominated sort，非支配排序
def fast_non_dominated_sort(values1, values2, values3):
    S = [[] for i in range(0, len(values1))]  # len(values1)个空列表
    front = [[]]
    n = [0 for i in range(0, len(values1))]
    rank = [0 for i in range(0, len(values1))]
    # 将front0全部整理出来了，并未对front1-n等进行整理
    for p in range(0, len(values1)):
        S[p] = []
        n[p] = 0
        for q in range(0, len(values1)):
            if (values1[p] <= values1[q] and values2[p] <= values2[q] and values3[p] <= values3[q]):
                if (values1[p] == values1[q] and values2[p] == values2[q] and values3[p] == values3[q]):
                    pass
                else:
                    #                 elif q not in S[p]:
                    S[p].append(q)
            elif (values1[q] <= values1[p] and values2[q] <= values2[p] and values3[q] <= values3[p]):
                if (values1[p] == values1[q] and values2[p] == values2[q] and values3[p] == values3[q]):
                    pass
                else:
                    n[p] = n[p] + 1
            '''if (values1[p] > values1[q] and values2[p] > values2[q] and values3[p] > values3[q])\
            or (values1[p] >= values1[q] and values2[p] > values2[q] and values3[p] > values3[q])\
            or (values1[p] > values1[q] and values2[p] >= values2[q] and values3[p] > values3[q])\
            or (values1[p] > values1[q] and values2[p] > values2[q] and values3[p] >= values3[q]):
                if q not in S[p]:
                    S[p].append(q)
            elif (values1[q] > values1[p] and values2[q] > values2[p] and values3[q] > values3[p])\
            or (values1[q] >= values1[p] and values2[q] > values2[p] and values3[q] > values3[p])\
            or (values1[q] > values1[p] and values2[q] >= values2[p] and values3[q] > values3[p])\
            or (values1[q] > values1[p] and values2[q] > values2[p] and values3[q] >= values3[p]):
                n[p] = n[p] + 1'''
        #         print('S'+str([p])+':',S[p])
        #         print('n'+str([p])+':',n[p])
        if n[p] == 0:
            rank[p] = 0
            if p not in front[0]:
                front[0].append(p)
    i = 0
    # 该循环能将所有的个体全部进行分类，显然最后一层的个体中，没有可以支配的个体了
    while (front[i] != []):
        Q = []
        for p in front[i]:
            for q in S[p]:
                n[q] = n[q] - 1
                if (n[q] == 0):
                    rank[q] = i + 1
                    if q not in Q:
                        Q.append(q)
        i = i + 1
        front.append(Q)

    del front[len(front) - 1]  # 删除了最后一层无支配个体的front层,最后一层是空集
    return front

#Function to find index of list,且是找到的第一个索引
def index_of(a,list):
    for i in range(0,len(list)):
        if list[i] == a:
            return i
    return -1

#Function to sort by values 找出front中对应值的索引序列
def sort_by_values(list1, values):
    sorted_list = []
    while(len(sorted_list)!=len(list1)):
        if index_of(min(values),values) in list1:
            sorted_list.append(index_of(min(values),values))
        values[index_of(min(values),values)] = math.inf
    return sorted_list

#拥挤度
def crowding_distance(values1, values2, values3, front):
    # distance = [0 for i in range(len(front))]
    lenth= len(front)
    for i in range(lenth):
        distance = [0 for i in range(lenth)]
        sorted1 = sort_by_values(front, values1[:])  #找到front中的个体索引序列
        sorted2 = sort_by_values(front, values2[:])  #找到front中的个体索引序列
        sorted3 = sort_by_values(front, values3[:])
        distance[0] = 4444
        distance[lenth-1] = 4444
        if max(values1) != min(values1) and max(values2) != min(values2) and max(values3) != min(values3):
            for k in range(1, lenth - 1):  # for all other points
                distance[k] = distance[k] + abs(values1[sorted1[k + 1]] - values1[sorted1[k - 1]]) / (
                            max(values1) - min(values1))
                distance[k] = distance[k] + abs(values2[sorted2[k + 1]] - values2[sorted2[k - 1]]) / (
                            max(values2) - min(values2))
                distance[k] = distance[k] + abs(values3[sorted3[k + 1]] - values3[sorted3[k - 1]]) / (
                            max(values3) - min(values3))
        else:
            for k in range(1, lenth - 1):  # for all other points
                distance[k] = distance[k] + abs(values1[sorted1[k + 1]] - values1[sorted1[k - 1]]) / (
                            max(values1) - min(values1))
                distance[k] = distance[k] + abs(values2[sorted2[k + 1]] - values2[sorted2[k - 1]]) / (
                            max(values2) - min(values2))
                # distance[k] = distance[k] + abs(values3[sorted3[k + 1]] - values3[sorted3[k - 1]]) / max(values3) - min(values3)

    return distance

def get_rank(x,front):
    for i in range(len(front)):
        for j in front[i]:
#             print(j)
            if x in front[i]:
                return i

def get_distance(x,front,distance):
    for i in range(len(front)):
        for j in distance[i]:
#             print(j)
            if x in front[i]:
                return i

def binary_tournament(ind1, ind2, front, distance):
    """
    二元锦标赛
    :param ind1:个体1号
    :param ind2: 个体2号
    :return:返回较优的个体
    """
    ind1_rank=get_rank(ind1,front)
    ind2_rank=get_rank(ind2,front)
    ind1_distance=get_distance(ind1,front,distance)
    ind2_distance=get_distance(ind2,front,distance)
    if ind1_rank != ind2_rank:  # 如果两个个体有支配关系，即在两个不同的rank中，选择rank小的
        return ind1 if ind1_rank < ind2_rank else ind2
    elif ind1_distance != ind2_distance:  # 如果两个个体rank相同，比较拥挤度距离，选择拥挤读距离大的
        return ind1 if ind1_distance > ind2_distance else ind2
    else:  # 如果rank和拥挤度都相同，返回任意一个都可以
        return ind1
def choose_select(Phen, front, distance):
    next_population1 = Phen.copy()
    """
    use select,crossover and mutation to create a new population Q
    :param Phen: 父代种群
    :return Q : 子代种群
    """
    popnum = len(Phen)
    Q = []
    # binary tournament selection
    # count = 0
    a = 0
    #     for a in range(int(popnum / 2)):
    while (a < popnum):
        # 从种群中随机选择两个个体，进行二元锦标赛，选择出一个 parent1
        i = np.random.randint(0, popnum - 1)
        j = np.random.randint(0, popnum - 1)
        parent1_index = binary_tournament(i, j, front, distance)
        parent1 = Phen[parent1_index]

        # 从种群中随机选择两个个体，进行二元锦标赛，选择出一个 parent2
        i = np.random.randint(0, popnum - 1)
        j = np.random.randint(0, popnum - 1)
        parent2_index = binary_tournament(i, j, front, distance)
        parent2 = Phen[parent2_index]

        while (parent1 == parent2).all():  # 如果选择到的两个父代完全一样，则重选另一个
            i = np.random.randint(0, popnum - 1)
            j = np.random.randint(0, popnum - 1)
            parent2 = binary_tournament(i, j, front,distance)
            parent2_index = binary_tournament(i, j, front,distance)
            parent2 = Phen[parent2_index]

        # 随机产生交叉点
        position = np.random.randint(0, popnum - 1)
        # 将两个个体从交叉点断开
        tmp11 = parent1[:position]
        tmp12 = parent1[position:]
        tmp21 = parent2[:position]
        tmp22 = parent2[position:]
        # 重新组合成新的个体
        # print(next_population1[i])
        next_population1[a] = np.append(tmp11, tmp22)
        # print(next_population1[i])
        next_population1[a + 1] = np.append(tmp21, tmp12)

        # 产生的子代进入子代种群
        Q.append(next_population1[a])
        Q.append(next_population1[a + 1])
        a += 2
        # count += 1
    return Q

#限制边界，当随机出每个卫星条带数量的边界时，随机回边界内
def Limit_bound(x,j,i):
    if x[j, i] > No_all[i] - 1 or x[j, i] < 0:
        if No_all[i] == 0:
            x[j, i] = np.random.randint(0, No_all[i] + 1, 1)
        else:
            x[j, i] = np.random.randint(0, No_all[i], 1)

def variation(solution,front,distance):
    copy_solution = solution.copy()  # (100, 20)
    #交叉算子
    cross_solution = choose_select(copy_solution, front, distance)
    offspring_solution = np.stack(cross_solution, 0)
    #克隆
    for ii in range(solution.shape[0]):  # 遍历所有个体
        '''这里a是offspring_solution，不是solution。保留solution以防出问题'''
        # a = solution[ii]  # 当前个体 .shape(D,),这里取出来是[1,1,1..D]列表
        a = offspring_solution[ii]  # 当前个体 .shape(D,),这里取出来是[1,1,1..D]列表
        a = a.reshape(-1, solution.shape[1])  # （-1，维度D），转换成一行D列数组，矩阵
        Na = np.tile(a, (Ncl, 1))  # 对当前个体进行克隆 Na.shape=(Ncl, D)
        deta = deta0 / (gen_no + 1)  # 刚开始迭代时,deta较大,初始值可以是上下限的中间值，随着迭代次数变多,deta减少
        #变异
        for j in range(Ncl):  # 遍历每一个样本
            for i in range(D):  # 遍历每一个维度
                if np.random.random() < pm:  # 以一定概率进行变异
                    Na[j, i] = Na[j, i] + (
                            ((np.random.random() - 0.5) * 2) * deta)  # 元素=元素+加一个随机数，在原数周围随机的跳动
                #用边界限制函数约束随机的条带数
                Limit_bound(Na, j, i)

        Na[0, :] = offspring_solution[ii]
        Na_num = get_covered_grid_num(Na,covered_all)#get_covered_grid_num(Na, covered1, covered2, covered3, covered4, covered5, covered6, covered7, covered8, covered9, covered10, covered11)
        # TODO function1_values=function1(all_set,aval_)
        # function1_values = [function1(Na_num[i],aval_arr) for i in range(0, Na_num.shape[0])]
        function1_values = function1(Na, aval_)
        function2_values = [function2(Na_num[i],cost_arr) for i in range(0, Na_num.shape[0])]
        function3_values = [function3(Na_num[i],untiltime) for i in range(0, Na_num.shape[0])]
        non_dominated_sorted_solution = fast_non_dominated_sort(function1_values[:], function2_values[:],
                                                                function3_values[:])
        crowding_distance_values = []
        for i in range(0, len(non_dominated_sorted_solution)):
            crowding_distance_values.append(
                crowding_distance(function1_values[:], function2_values[:], function3_values[:],
                                  non_dominated_sorted_solution[i][:]))

        #拥挤度选择：先选i rank小的个体，如果同i rank再选拥挤度大的个体作为最优
        for i in range(len(non_dominated_sorted_solution)):
            if len(non_dominated_sorted_solution[i]) <= 2:
                front1 = non_dominated_sorted_solution[i]
                front1_np = np.array(front1)
                Index = np.argsort(crowding_distance_values[i], axis=0)
                front1_sort = front1_np[Index]
                front1_max_crowd = front1_sort[-1]
                offspring_solution[ii] = Na[front1_max_crowd]
            elif len(non_dominated_sorted_solution[i]) > 2:  # 如果第一个front小于等于二，就找第二个front的最大拥挤度
                front1 = non_dominated_sorted_solution[i]
                front1_np = np.array(front1)
                Index = np.argsort(crowding_distance_values[i], axis=0)
                front1_sort = front1_np[Index]
                #如果不管两边最大的拥挤度，选择最大的拥挤度如下
                num_4444 = 2#一个front里两个最大值
                #如果考虑两个最大的拥挤度4444，如下
                # num_4444 = 0
                front1_max_crowd = front1_sort[-(num_4444 + 1)]#选出rank低的拥挤度高的个体索引
                offspring_solution[ii] = Na[front1_max_crowd]
                break

    return offspring_solution

#定义随机新种群
def refresh():
    """
    创建一般新生种群并返回
    """
    bf = np.random.randint(0, no6, (NIND, D))  #创建0-1000000很大的随机数，然后约束边界生成随机新种群
    for j in range(bf.shape[0]):
        for i in range(bf.shape[1]):
            #限制边界
            Limit_bound(bf, j, i)

    return bf

"""============================变量设置============================"""


#每个卫星条带都是从零计数
x1 = [0, no1-1] # 第一个决策变量范围
x2 = [0, no2-1] # 第二个决策变量范围
x3 = [0, no3-1] # 第三个决策变量范围
x4 = [0, no4-1] # 第四个决策变量范围
x5 = [0, no5-1]
x6 = [0, no6-1]
x7 = [0, no7-1]
x8 = [0, no8-1]
x9 = [0, no9-1]
x10 = [0, no10-1]
x11 = [0, no11-1]
x12 = [0, no12-1]
x13 = [0, no13-1]
x14 = [0, no14-1]
x15 = [0, no15-1]
x16 = [0, no16-1]
x17 = [0, no17-1]
x18 = [0, no18-1]
x19 = [0, no19-1]
x20 = [0, no20-1]
x21 = [0, no21]
x22 = [0, no22]
x23 = [0, no23]
x24 = [0, no24]
x25 = [0, no25]
ranges=np.vstack([x1, x2, x3, x4, x5, x6, x7, x8, x9, x10,
                  x11, x12, x13, x14, x15, x16, x17, x18, x19,x20,
                  x21, x22, x23, x24, x25]).T # 生成自变量的范围矩阵，使得第一行为所有决策变量的下界，第二行为上界
# borders=np.vstack([b1, b2, b3, b4]).T # 生成自变量的边界矩阵
varTypes = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                     1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                     1, 1, 1, 1, 1]) # 决策变量的类型，0表示连续，1表示离散
"""==========================染色体编码设置========================="""
Encoding = 'RI'
FieldDR = ea.crtfld(Encoding,varTypes,ranges)
"""=========================初始个体参数设置========================"""
NIND      = 100 # 种群个体数目
D=len(sat_list)#维度，几个卫星
# MAXGEN    = 50 # 最大遗传代数
# np.random.seed(3)
Chrom = ea.crtpc(Encoding, NIND, FieldDR) # 生成种群染色体矩阵
Phen = Chrom#表现型矩阵
# print(Phen)
covered_num = get_covered_grid_num(Phen, covered_all)#get_covered_grid_num(Phen, covered1, covered2, covered3, covered4, covered5, covered6, covered7, covered8, covered9, covered10, covered11)

"""=========================免疫算法参数设置========================"""
deta0=150#5# 刚开始迭代时,deta较大,初始值可以是上下限的中间值，随着迭代次数变多,deta减少
pm=0.7#变异率
gen_no=0#初始代数
D=25#维度，几个卫星
max_gen=300#最大代数
Ncl=10
# pop_size=10
"""=========================计算pareto前沿========================"""
while (gen_no < max_gen):
    print('\n')
    print('gen_no:迭代次数', gen_no)
    # function1_values = [function1(covered_num[i],aval_arr) for i in range(0, NIND)]
    function1_values = function1(Phen, aval_)
    function2_values = [function2(covered_num[i],cost_arr) for i in range(0, NIND)]
    function3_values = [function3(covered_num[i],untiltime) for i in range(0, NIND)]
    print('function1_values', function1_values)  # 求得的是目标函数的结果
    print('function2_values', function2_values)
    print('function3_values', function3_values)
    non_dominated_sorted_solution = fast_non_dominated_sort(function1_values[:], function2_values[:],
                                                            function3_values[:])
    print('non_dominated_sorted_solution', non_dominated_sorted_solution)
    crowding_distance_values = []
    for i in range(0, len(non_dominated_sorted_solution)):
        crowding_distance_values.append(crowding_distance(function1_values[:], function2_values[:], function3_values[:],
                                                          non_dominated_sorted_solution[i][:]))
    print("crowding_distance_values", crowding_distance_values)

    #父代变异＋随机子代作为新一代，精英保留策略
    muta_phen = variation(Phen,non_dominated_sorted_solution,crowding_distance_values)#父代变异后的种群
    muta_covered_num = get_covered_grid_num(muta_phen, covered_all)
    fresh_phen = refresh()#随机新种群
    fresh_covered_num = get_covered_grid_num(fresh_phen, covered_all)
    # phen2 = np.concatenate((Phen, muta_phen), axis=0)
    # covered_num2 = np.concatenate((covered_num, muta_covered_num), axis=0)
    phen2 = np.concatenate((muta_phen, fresh_phen), axis=0)#变异父代＋随机子代
    covered_num2 = np.concatenate((muta_covered_num, fresh_covered_num), axis=0)#格网数

    # function1_values2 = [function1(covered_num2[i],aval_arr) for i in range(0, 2 * NIND)]
    function1_values2 = function1(phen2, aval_)
    function2_values2 = [function2(covered_num2[i],cost_arr) for i in range(0, 2 * NIND)]
    function3_values2 = [function3(covered_num2[i],untiltime) for i in range(0, 2 * NIND)]
    print('function1_values2', function1_values2)  # 求得的是目标函数的结果
    print('function2_values2', function2_values2)
    print('function3_values2', function3_values2)
    non_dominated_sorted_solution2 = fast_non_dominated_sort(function1_values2[:], function2_values2[:],
                                                             function3_values2[:])
    print('non_dominated_sorted_solution2', non_dominated_sorted_solution2)
    crowding_distance_values2 = []
    for i in range(0, len(non_dominated_sorted_solution2)):
        crowding_distance_values2.append(
            crowding_distance(function1_values2[:], function2_values2[:], function3_values2[:],
                              non_dominated_sorted_solution2[i][:]))
    print('crowding_distance_values2', crowding_distance_values2)

    new_solution = []
    for i in range(0, len(non_dominated_sorted_solution2)):
        non_dominated_sorted_solution2_1 = [
            index_of(non_dominated_sorted_solution2[i][j], non_dominated_sorted_solution2[i]) for j in
            range(0, len(non_dominated_sorted_solution2[i]))]
        print('non_dominated_sorted_solution2_1:', non_dominated_sorted_solution2_1)
        front22 = sort_by_values(non_dominated_sorted_solution2_1[:], crowding_distance_values2[i][:])
        print("front22", front22)
        front = [non_dominated_sorted_solution2[i][front22[j]] for j in
                 range(0, len(non_dominated_sorted_solution2[i]))]
        print('front', front)
        # front.reverse()# todo 前面的排序是从大到小，这里反转，选的是小的
        #精英保留
        for value in front:
            new_solution.append(value)
            if (len(new_solution) == NIND):
                break
        if (len(new_solution) == NIND):
            break

    # phenx = [covered_num2[i] for i in new_solution]
    # covered_num = np.stack(phenx, axis=0)
    phenx = [phen2[i] for i in new_solution]
    phenx = np.stack(phenx, axis=0)
    print('phenx',phenx)
    covered_num = get_covered_grid_num(phenx, covered_all)
    print('covered_num',covered_num)

    #计算选出的子代的pareto front，将最后的covered_num的Pareto 前沿计算出来，方便后面画图
    # function1_values = [function1(covered_num[i],aval_arr) for i in range(0, NIND)]
    function1_values = function1(phenx, aval_)
    function2_values = [function2(covered_num[i],cost_arr) for i in range(0, NIND)]
    function3_values = [function3(covered_num[i],untiltime) for i in range(0, NIND)]
    print('function1_values', function1_values)  # 求得的是目标函数的结果
    print('function2_values', function2_values)
    print('function3_values', function3_values)
    non_dominated_sorted_solution = fast_non_dominated_sort(function1_values[:], function2_values[:],
                                                            function3_values[:])
    print('non_dominated_sorted_solution', non_dominated_sorted_solution)
    # crowding_distance_values = []
    # for i in range(0, len(non_dominated_sorted_solution)):
    #     crowding_distance_values.append(crowding_distance(function1_values[:], function2_values[:], function3_values[:],
    #                                                       non_dominated_sorted_solution[i][:]))
    # print("crowding_distance_values", crowding_distance_values)


    gen_no = gen_no + 1

'''=====================生成结果==================='''
#把function123存在txt中
with open('E:\\arcpy-\\monggulia_fire\\stripe\\result\\function1.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in function1_values:
        file.write(str(s) + "\n")

with open('E:\\arcpy-\\monggulia_fire\\stripe\\result\\function2.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in function2_values:
        file.write(str(s) + "\n")

with open('E:\\arcpy-\\monggulia_fire\\stripe\\result\\function3.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in function3_values:
        file.write(str(s) + "\n")

#把front存在txt中
with open('E:\\arcpy-\\monggulia_fire\\stripe\\result\\non_dominated_sorted_solution.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in non_dominated_sorted_solution:
        file.write(str(s) + "\n")
#把最终的phenx存在txt中
np.savetxt("E:\\arcpy-\\monggulia_fire\\stripe\\result\\phenx.txt", Phen,fmt='%d',delimiter=',')

'''====================生成结果==================='''

function1 = [i * 1 for i in function1_values]
function2 = [j * 1 for j in function2_values]
function3 = [j * 1 for j in function3_values]
#这里的function123是所有NIND个体的结果，下面转成数组找出Pareto front，只画front图
print('function1_values',function1_values)
print('function2_values',function2_values)
print('function3_values',function3_values)
front1 = non_dominated_sorted_solution[0]#Pareto front
front1_np = np.array(front1)
function1_values_np = np.array(function1_values)
function2_values_np = np.array(function2_values)
function3_values_np = np.array(function3_values)
function1_values1 = function1_values_np[front1_np].tolist()
function2_values1 = function2_values_np[front1_np].tolist()
function3_values1 = function3_values_np[front1_np].tolist()
print('function1_values',function1_values1)
print('function2_values',function2_values1)
print('function3_values',function3_values1)
function1 = [i * 1 for i in function1_values1]
function2 = [j * 1 for j in function2_values1]
function3 = [j * 1 for j in function3_values1]
#这里的function123是只显示Pareto front的结果

#其他pareto解
# front2 = non_dominated_sorted_solution[1]#Pareto rank2
# front2_np = np.array(front2)
# function1_values_np = np.array(function1_values)
# function2_values_np = np.array(function2_values)
# function3_values_np = np.array(function3_values)
# function1_values2 = function1_values_np[front2_np].tolist()
# function2_values2 = function2_values_np[front2_np].tolist()
# function3_values2 = function3_values_np[front2_np].tolist()
# function11 = [i * 1 for i in function1_values2]
# function21 = [j * 1 for j in function2_values2]
# function31 = [j * 1 for j in function3_values2]


plt.subplot(1, 3, 1)
plt.xlabel("覆盖")
plt.ylabel("成本")
plt.scatter(function1,function2)

# plt.scatter(function11,function21)
# plt.scatter(function12,function22)
# plt.scatter(function13,function23)
# z = np.polyfit(function1, function2, 1)
# p = np.poly1d(z)
# plt.plot(function1,p(function1),"r",linewidth=0.5)

plt.subplot(1, 3, 2)
plt.xlabel("覆盖")
plt.ylabel("时效")
plt.scatter(function1,function3)

# plt.scatter(function11,function31)
# plt.scatter(function12,function32)
# plt.scatter(function13,function33)
# z = np.polyfit(function1, function3, 1)
# p = np.poly1d(z)
# plt.plot(function1,p(function1),"r",linewidth=0.5)

plt.subplot(1, 3, 3)
plt.xlabel("成本")
plt.ylabel("时效")
function2r=[j * -1 for j in function2_values]

# function2r1=[j * -1 for j in function2_values2]
# function2r2=[j * -1 for j in function2_values3]
# function2r3=[j * -1 for j in function2_values4]

function3r=[j * 1 for j in function3_values]

# function3r1=[j * 1 for j in function3_values2]
# function3r2=[j * 1 for j in function3_values3]
# function3r3=[j * 1 for j in function3_values4]
# function21 = [7.808163265306122,22.693877551020407]
# function2r1=[j * -1 for j in function21]

plt.scatter(function2r,function3r)

# plt.scatter(function2r1,function3r1)
# plt.scatter(function2r2,function3r2)
# plt.scatter(function2r3,function3r3)

# plt.scatter(function2r1,function31)
# z = np.polyfit(function2r, function3r, 1)
# p = np.poly1d(z)
# plt.plot(function2r,p(function2r),"r",linewidth=0.5)

plt.tight_layout()

# fig = plt.figure()
# ax = Axes3D(fig)
# ax.scatter(function1, function2, function3)
# ax.scatter(function11, function21, function31)
#
# ax.set_xlabel('覆盖', fontsize=15)
# ax.set_ylabel('成本', fontsize=15)
# ax.set_zlabel('时效', fontsize=15)
#
# ax.plot_trisurf(function1, function2, function3,cmap="Greens")
# ax.plot_trisurf(function11, function21, function31,cmap="Blues")

plt.show()

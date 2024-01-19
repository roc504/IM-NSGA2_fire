"""
@File    : Geatpy_test.py
@Author  : roc
@Time    : 2023/3/25 19:41
"""

import shapefile
from pyproj import Proj,transform
import numpy as np
import numpy as np
import geatpy as ea # 导入geatpy库
# from aimfunc import aimfunc # 导入自定义的目标函数,就是上面的CV、f
import time
sf = shapefile.Reader('E:/arcpy-/monggulia_fire/maybe_fire_area1_fishnet_sele.shp')
shapes = sf.shapes()
lens = len(shapes)
grid_all = []#所有格网集合
for q in range(lens):
    grid_all.append(shapes[q].points)
print("num(grid_all):", len(grid_all))

def read_stripe_masage(sat_name):
    # sat_name='CB04_9_1_sele'#gf1_test
    stripe4point_gf1_sele=[]
    with open('D:\\stripe_txt\\st\\'+str(sat_name)+'_sele_stripe4point.txt', "r", encoding='utf-8') as f:  #打开文本
        stripe4point = f.readlines()   #读取文本
        stripe4point_gf1 = [eval(s) for s in stripe4point]
        for i in range(len(stripe4point_gf1)):
            if i%1==0:
                stripe4point_gf1_sele.append(stripe4point_gf1[i])
    stripe=len(stripe4point_gf1_sele)
    return stripe4point_gf1_sele,stripe
    # print('num(stripe4point_'+sat_name+')',stripe)

# sat_list=['ZY1F_VNIC_9_1','GF1C_PMS_9_1','GF7_DLC_9_1','HJ2B_CCD_9_1','HJ2B_CCD_10_1',
#           'HJ2A_CCD_10_1','ZY1E_VNIC_10_1','GF5B_AHSI_10_1','CB04_IRS_10_1','ZY1F_IRS_11_1',
#           'CB04A_WFI_10_1','CB04A_MUX_11_1','CB04_WFI_11_1','HJ2A_CCD_11_1','GF3C_SAR_11_1',
#           'Sentinel2B_MSI_9_1','WORLDVIEW3_10_2','TERRA_MODIS_9_1','TERRA_MODIS_10_1','TERRA_MODIS_11_1',
#           'GF1D_PMI_9_1','Landsat8_OLI_10_1','GF2_PMI_10_1','HJ2A_HSI_9_1','Gf7_DLC_11_1']

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
    exec(f'stripe_{m} = Stripepoints_all[k]')

No_all=[]
for i in sat_list:
    No_all.append(read_stripe_masage(i)[1])

for k in range(len(sat_list)):
    exec(f"no{k+1} = No_all[k]")



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


def covered_num(stripename,num):
    covered=[]
    for _ in range(0,num):#(0,28)
        a = []
        for __ in range(len(grid_all)):
            if gridall_in_stripe(stripename,_,__):
                a.append(__)
        # print a
        covered.append(a)
        del a
    if covered == []:
        covered = [[] for i in range(1)]
    return covered
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
def get_covered_grid_num(x,covered_all):
    NN=[]
    for temp in range(D):
        n = []
        for i in x[:, temp]:
            c=covered_all[temp][int(i)]
            n.append(len(c))
        N=np.array(n)
        NN.append(N)
    data=np.stack(NN,1)
    return data

#function1
avaliable = np.array([6, 5, 6, 2, 2,
                      2, 6, 6, 2, 6,
                      2, 2, 2, 2, 7,
                      1, 9, 3, 3, 3,
                      100, 100, 100, 100, 100])
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
#function2
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
print('cost_arr',cost_arr)
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
#function3
untiltime = np.array([11969, 50045, 11600, 13800, 101630,
                      98617, 98903, 98922, 135930, 186692,
                      97500, 185013, 224478, 186435, 206808,
                      11124, 137485, 7705, 96560, 185396,
                      14120, 135356, 97466, 12206,  226171])# 实验用6颗卫星距离灾害发生时间/min
print('untiltime_arr',untiltime)
def function3(X3,para_time):
    untiltime = para_time
    value = 0
    for i in range(D):
        if X3[i]!=0:#有覆盖单元格才计算
            if value <= untiltime[i]:
                value = untiltime[i]
            else:
                value = value
    # valuet = value
    return value


def aim(function1,function2,function3,weight):#function123是数组
    f=weight[0]*function1 +weight[1]*function2 +weight[2]*function3

    # CV = np.dot(covered_num,para_bT).reshape(NIND,1) - max_cost_vstack  # 生成种群个体违反约束程度矩阵CV，以处理等式约束：b1*x1+b2*x2+b3*x3+b4*x4<=500
    # CV=CV.reshape(NIND,1)
    # CV矩阵中元素小于或等于0表示对应个体满足对应的约束条件，否则是违反对应的约束条件，大于0的值越大，表示违反约束的程度越高。
    # 生成CV标记之后，在后面调用适应度函数计算适应度时，只要把CV矩阵作为函数传入参数传进函数体，
    # 就会自动根据CV矩阵所描述的种群个体违反约束程度来计算出合适的种群个体适应度。

    f=f.reshape(NIND,1)
    return f#, CV  # 返回目标函数值矩阵

'''def aim(covered_num):
    a1, a2, a3 ,a4, a5=1, 1, 1, 1, 1
    a6, a7, a8, a9 ,a10=1, 1, 1, 1, 1
    a11, a12, a13, a14, a15=-1, 1, -1, -1, -1
    a16, a17, a18, a19, a20 = -10, -10, -10, -10, -10
    para_a=[a1, a2, a3 ,a4, a5, a6, a7, a8, a9 ,a10, a11, a12, a13, a14, a15, a16, a17, a18, a19, a20]
    para_aT=(np.array(para_a)).T
    #价格约束
    b1, b2, b3, b4, b5 = 0.038, 0.36, 0.08, 0.08, 0.08
    b6, b7, b8, b9, b10=0, 0.038, 0.038, 0, 0.038
    b11, b12, b13, b14, b15=33, 0, 0.038, 2.5, 0.037
    b16, b17, b18, b19, b20=0.069, 0.023, 0.543, 0.08, 2.5
    para_b=[b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12, b13, b14, b15, b16, b17, b18, b19, b20]
    para_bT=(np.array(para_b)).T
    # x1 = Phen[:, 0]  # 取出种群表现型矩阵的第一列，得到所有个体的决策变量x
    # x2 = Phen[:, 1]  # 取出种群表现型矩阵的第二列，得到所有个体的决策变量y
    # x3 = Phen[:, 2]  # 取出种群表现型矩阵的第san列，得到所有个体的决策变量x
    # x4 = Phen[:, 3]  # 取出种群表现型矩阵的第si列，得到所有个体的决策变量y
    # x5 = Phen[:, 4]  # 取出种群表现型矩阵的第5列，得到所有个体的决策变量y
    # x6 = Phen[:, 5]  # 取出种群表现型矩阵的第6列，得到所有个体的决策变量y

    # n1 = covered_num[0]
    # n2 = covered_num[1]
    # n3 = covered_num[2]
    # n4 = covered_num[3]
    # n5 = covered_num[4]
    # n6 = covered_num[5]
    # n7 = covered_num[6]
    # n8 = covered_num[7]
    # n9 = covered_num[8]
    # n10 = covered_num[9]
    # n11 = covered_num[10]
    # n12 = covered_num[11]
    # n13 = covered_num[12]
    # n14 = covered_num[13]
    # n15 = covered_num[14]
    # n16 = covered_num[15]
    # n17 = covered_num[16]
    # n18 = covered_num[17]
    # n19 = covered_num[18]
    # n20 = covered_num[19]
    max_cost=np.array(2.5*1692)
    max_cost_vstack=np.tile(max_cost, (NIND, 1))

    # CV = np.dot(covered_num,para_bT).reshape(NIND,1) - max_cost_vstack  # 生成种群个体违反约束程度矩阵CV，以处理等式约束：b1*x1+b2*x2+b3*x3+b4*x4<=500
    # CV=CV.reshape(NIND,1)
    # CV矩阵中元素小于或等于0表示对应个体满足对应的约束条件，否则是违反对应的约束条件，大于0的值越大，表示违反约束的程度越高。
    # 生成CV标记之后，在后面调用适应度函数计算适应度时，只要把CV矩阵作为函数传入参数传进函数体，
    # 就会自动根据CV矩阵所描述的种群个体违反约束程度来计算出合适的种群个体适应度。
    f = np.dot(covered_num,para_aT)# 计算目标函数值，覆盖格网最大
    f=f.reshape(NIND,1)
    return f#, CV  # 返回目标函数值矩阵'''

"""============================================================"""
times=time.time()
covered_all=np.load(r'D:\\stripe_txt\\st_covered_all\\covered_all1.npy',allow_pickle=True)
timee=time.time()
print('covered_all赋值完成，耗时',timee-times)

'''
max G = a1*gx1+a2*gx2+a3*gx3+a4*gx4+a5*gx5+a6*gx6
可获得性：a1=1、a2=1、a3=1、a4=1、a5=1、a6=0
每格网价格：b1=4、b2=5、b3=1、b4=10、b5=3、b6=4
分辨率敏感度：c1=2、c2=2、c3=10、c4=40、c5=30、c6=0.5
观测敏感度:d1=1、d2=1、d3=1、d4=0.6、d5=1、d6=1

st
#价格约束
b1*g(x1)+b2*g(x2)+b3*g(x3)+b4*g(x4)+b5*g(x5)+b6*g(x6)<=4500
#可获得性约束
a1=1、a2=1、a3=1、a4=1、a5=1、a6=0
#分辨率约束
c1=2、c2=2、c3=10、c4=40、c5=30、c6=0.5
#分辨率越高的归一到0,1间越大
resolution = np.array([2,2,10,40,30,0.5])#实验用6颗卫星分辨率
for x in resolution:
    x = float(x - np.max(resolution))/(np.min(resolution)- np.max(resolution))
x1*g(x1)+x2*g(x2)+x3*g(x3)+x4*g(x4)+x5*g(x5)+x6*g(x6)<=470
#观测敏感度约束
gf1多光谱、gf2多光谱、sentinel2b多光谱、gf5高光谱、pleiades1b多光谱、gj103多光谱
d1=1、d2=1、d3=1、d4=0.6、d5=1、d6=1

'''
"""============================变量设置============================"""
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
# b1 = [1, 1] # 第一个决策变量边界，1表示包含范围的边界，0表示不包含
# b2 = [1, 1] # 第二个决策变量边界，1表示包含范围的边界，0表示不包含
# b3 = [1, 1] # 第三个决策变量边界，1表示包含范围的边界，0表示不包含
# b4 = [1, 1] # 第四个决策变量边界，1表示包含范围的边界，0表示不包含

ranges=np.vstack([x1, x2, x3, x4, x5, x6, x7, x8, x9, x10,
                  x11, x12, x13, x14, x15, x16, x17, x18, x19,x20,
                  x21, x22, x23, x24, x25]).T # 生成自变量的范围矩阵，使得第一行为所有决策变量的下界，第二行为上界
# borders=np.vstack([b1, b2, b3, b4]).T # 生成自变量的边界矩阵
varTypes = np.array([1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                     1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                     1, 1, 1, 1, 1]) # 决策变量的类型，0表示连续，1表示离散 # 决策变量的类型，0表示连续，1表示离散

"""==========================染色体编码设置========================="""
Encoding = 'RI' # 'BG'表示采用二进制/格雷编码
# 二进制编码
# codes = [0, 0] # 决策变量的编码方式，设置两个0表示两个决策变量均使用二进制编码
# precisions =[4, 4] # 决策变量的编码精度，表示二进制编码串解码后能表示的决策变量的精度可达到小数点后6位
# scales = [0, 0] # 0表示采用算术刻度，1表示采用对数刻度
# FieldD = ea.crtfld(Encoding,varTypes,ranges,borders,precisions,codes,scales) # 调用函数创建译码矩阵
FieldDR = ea.crtfld(Encoding,varTypes,ranges)#实数编码

"""=========================遗传算法参数设置========================"""
NIND      = 100 # 种群个体数目
D=len(sat_list)#维度，几个卫星
MAXGEN    = 150 # 最大遗传代数
maxormins = [-1] # 列表元素为1则表示对应的目标函数是最小化，元素为-1则表示对应的目标函数是最大化
selectStyle = 'rws' # 采用轮盘赌选择
recStyle  = 'xovdp' # 采用两点交叉
mutStyle  = 'mutuni' # 采用实数染色体的变异算子
pc        = 0.7 # 交叉概率
pm        = 0.3 # 整条染色体的变异概率（每一位的变异概率=pm/染色体长度）
Lind = int(len(FieldDR[0, :])) # 计算染色体长度
obj_trace = np.zeros((MAXGEN, D)) # 定义目标函数值记录器
var_trace = np.zeros((MAXGEN, Lind)) # 染色体记录器，记录历代最优个体的染色体
"""=========================开始遗传算法进化========================"""
start_time = time.time() # 开始计时
Chrom = ea.crtpc(Encoding, NIND, FieldDR) # 生成种群染色体矩阵
Phen = Chrom#表现型矩阵
covered_num=get_covered_grid_num(Phen,covered_all)
function1_values = function1(Phen, aval_)
function2_values = [function2(covered_num[i],cost_arr) for i in range(0, NIND)]
function3_values = [function3(covered_num[i],untiltime) for i in range(0, NIND)]
function1_values_arr=np.array(function1_values)
function2_values_arr=np.array(function2_values)
function3_values_arr=np.array(function3_values)
#三个目标的权重
weight=[4,1,8]
wei = []
for a in weight:
    a = float(a - np.min(weight)) / (np.max(weight) - np.min(weight))
    wei.append(a)
# variable = ea.bs2ri(Chrom, FieldDR) # 对初始种群进行解码
CV = np.zeros((NIND, 1)) # 初始化一个CV矩阵（此时因为未确定个体是否满足约束条件，因此初始化元素为0，暂认为所有个体是可行解个体）
# ObjV, CV = aim(covered_num) # 计算初始种群个体的目标函数值
ObjV= aim(function1_values_arr,function2_values_arr,function3_values_arr,weight)
FitnV = ea.ranking(maxormins * ObjV, CV) # 根据目标函数大小分配适应度值
best_ind = np.argmax(FitnV) # 计算当代最优个体的序号
"""========================================================="""

# print('N1,N2,N3,N4,N5,N6',get_covered_grid_num(covered1, covered2, covered3, covered4, covered5, covered6))
# 开始进化
for gen in range(MAXGEN):
    SelCh = Chrom[ea.selecting(selectStyle,FitnV,NIND-1),:] # 选择
    SelCh = ea.recombin(recStyle, SelCh, pc) # 重组，交叉
    SelCh = ea.mutate(mutStyle, Encoding, SelCh, FieldDR, pm) # 变异
    # 把父代精英个体与子代的染色体进行合并，得到新一代种群
    Chrom = np.vstack([Chrom[best_ind, :].astype(int), SelCh])
    Phen = Chrom
    covered_num = get_covered_grid_num(Phen, covered_all)
    # Phen = ea.bs2ri(Chrom, FieldDR) # 对种群进行解码(二进制转十进制)
    # ObjV, CV = aim(Phen) # 求种群个体的目标函数值
    ObjV = aim(function1_values_arr,function2_values_arr,function3_values_arr,weight)
    FitnV = ea.ranking(maxormins * ObjV, CV) # 根据目标函数大小分配适应度值
    # 记录
    best_ind = np.argmax(FitnV) # 计算当代最优个体的序号
    obj_trace[gen,0]=np.sum(ObjV)/ObjV.shape[0] #记录当代种群的目标函数均值
    obj_trace[gen,1]=ObjV[best_ind] #记录当代种群最优个体目标函数值
    var_trace[gen,:]=Chrom[best_ind,:] #记录当代种群最优个体的染色体
    print('var_trace',var_trace)
    print('function2_values',function2_values_arr)
    print('function3_values',function3_values_arr)
# 进化完成
end_time = time.time() # 结束计时
ea.trcplot(obj_trace, [['种群个体平均目标函数值', '种群最优个体目标函数值']]) # 绘制图像


"""============================输出结果============================"""
best_gen = np.argmax(obj_trace[:, [1]])
print('最优解的目标函数值：', obj_trace[best_gen, 1])
variable = var_trace[[best_gen], :] # 解码得到表现型（即对应的决策变量值）
print('最优解的决策变量值为：')
result=[]
for i in range(variable.shape[1]):
    result.append(variable[0, i])
    print('x'+str(i)+'=',variable[0, i])
print('用时：', end_time - start_time, '秒')


'''=====================生成结果==================='''
'''#把function123存在txt中
with open('D:\\stripe_txt\\st\\GA_result\\目标函数值.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in obj_trace:
        file.write(str(s) + "\n")

with open('D:\\stripe_txt\\st\\GA_result\\决策变量值.txt', "w") as file:
    # file.write('front:'+"\n")
    for i in range(variable.shape[1]):
        file.write('x' + str(i) + '=', variable[0, i])

#把最终的phenx存在txt中
np.savetxt("D:\\stripe_txt\\st\\GA_result\\phenx.txt", ObjV,fmt='%d',delimiter=',')
'''
'''====================生成结果==================='''

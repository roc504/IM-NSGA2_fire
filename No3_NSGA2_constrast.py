"""
@File    : No3_NSGA2_constrast.py
@Author  : roc
@Time    : 2023/9/22 16:39
"""

#Importing required modules
import math
import random
import time
import geatpy as ea
import numpy as np
import matplotlib.pyplot as plt


def each_covered(sat_num):
    num=sat_num+1
    real_path = (r'D:\stripe_txt\covered_all\covered' + str(num) + '.npy')
    real_data = np.load(real_path, allow_pickle=True)
    return real_data

# def get_covered_grid_num(x):
#     '''
#     这个函数将输入的x（形式为NIND×D的种群），转换成对应条带覆盖的格网数
#     输出也是NIND×D
#     '''
#     NN=[]
#     for temp in range(x.shape[1]):
#         n = []
#         for i in x[:, temp]:
#             c=each_covered(temp)[int(i)]
#             # c=covered_all[temp][int(i)]
#             n.append(len(c))
#             del c
#         N=np.array(n)
#         del n
#         NN.append(N)
#     data=np.stack(NN,1)
#     return data

def get_covered_grid_num(x,covered_all):
    '''
    这个函数将输入的x（形式为NIND×D的种群），转换成对应条带覆盖的格网数
    输出也是NIND×D
    '''
    NN=[]
    for temp in range(x.shape[1]):
        n = []
        for i in x[:, temp]:
            # 对大数据量，单独读取
            # c=each_covered(temp)[int(i)]
            # 对小数据量，整体读取
            c=covered_all[temp][int(i)]
            n.append(len(c))
            del c
        N=np.array(n)
        del n
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
            #对大数据量，单独读取
            # covered_grid = each_covered(j)[Phen_num]
            # 对小数据量，整体读取
            covered_grid=covered_all[j][Phen_num]
            # print(covered_grid)
            for k in covered_grid:
                if one_set.__contains__(str(k)):
                    one_set[str(k)].append((j,Phen_num))
                else:
                    one_set[str(k)]=[(j,Phen_num)]

        all_set.append(one_set)#如果one_set字典创建在整个循环外，注释掉这句，如果创建在第一层循环，保留
    return all_set

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
aval_=[-5.0 if i ==-0.0 else i for i in aval]#-50.0
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
    paraT = para.T
    value = np.dot(X2, paraT)#100x20·20x1->100x1，是这100个个体的结果
    return value


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

#Function to find index of list
#函数查找列表的索引
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

#Function to carry out NSGA-II's fast non dominated sort
#函数执行NSGA-II的快速非支配排序
"""基于序列和拥挤距离"""
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

#Function to calculate crowding distance
#计算拥挤距离的函数
def crowding_distance(values1, values2, values3, front):
    distance = [0 for i in range(0,len(front))]
    sorted1 = sort_by_values(front, values1[:])
    sorted2 = sort_by_values(front, values2[:])
    sorted3 = sort_by_values(front, values3[:])
    distance[0] = 4444444444444444
    distance[len(front) - 1] = 4444444444444444
    for k in range(1,len(front)-1):
        distance[k] = distance[k]+ (values1[sorted1[k+1]] - values2[sorted1[k-1]])/(max(values1)-min(values1))
    for k in range(1,len(front)-1):
        distance[k] = distance[k]+ (values1[sorted2[k+1]] - values2[sorted2[k-1]])/(max(values2)-min(values2))
    for k in range(1, len(front) - 1):
        distance[k] = distance[k]+ (values1[sorted3[k+1]] - values2[sorted3[k-1]])/(max(values3)-min(values3))
    return distance

'''def crowding_distance(values1, values2, values3, front):
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

    return distance'''

#Function to carry out the crossover
#函数进行交叉
def crossover(solution,a,b):
    solution1 = solution
    crosee_r = random.random()
    if crosee_r < 0.9:
        parent1 = solution[a]
        parent2 = solution[b]
        position = np.random.randint(0, D - 1)
        tmp11 = parent1[:position]
        tmp12 = parent1[position:]
        tmp21 = parent2[:position]
        tmp22 = parent2[position:]
        solution1[a] = np.append(tmp11, tmp22)
        solution1[b] = np.append(tmp21, tmp12)
        mutation(solution1, a, b)
        return solution1[a], solution1[b]
    else:
        return solution1[a], solution1[b]


def Limit_bound(x,j,i):
    if x[j, i] > No_all[i] - 1 or x[j, i] < 0:
        if No_all[i] == 0:
            x[j, i] = np.random.randint(0, No_all[i] + 1, 1)
        else:
            x[j, i] = np.random.randint(0, No_all[i], 1)
#Function to carry out the mutation operator
#函数进行变异操作
def mutation(solution,a,b):
    solution1=np.array(solution)
    mutation_prob = random.random()

    for i in range(D-8):  # 针对前面有数的条带
        pr=np.random.random()
        if pr < 0.7:  # 以一定概率进行变异
            solution1[a, i] = np.random.randint(0, No_all[i])
            solution1[b, i] = np.random.randint(0, No_all[i])
            return solution1[a], solution1[b]
        else:
            return solution1[a], solution1[b]





def read_stripe_masage(sat_name):
    with open('D:\\stripe_txt\\st\\'+str(sat_name)+'_sele_stripe4point.txt', "r", encoding='utf-8') as f:  #打开文本
        stripe4point = f.readlines()  # 读取文本
        stripe4point_ = [eval(s) for s in stripe4point]
    stripe=len(stripe4point_)
    print('read'+str(sat_name)+'_sele_stripe4point.txt')
    return stripe4point_,stripe


#Main program starts here
"""============================变量设置============================"""
'''covered_all赋值'''
times=time.time()
covered_all=np.load(r'D:\\stripe_txt\\st_covered_all\\covered_all1.npy',allow_pickle=True)
timee=time.time()
print('covered_all赋值完成，耗时',timee-times)
'''需要的卫星'''
timestart=time.time()
sat_list = ['ZY1F_VNIC_9_11', 'GF1C_PMS_9_1', 'GF7_DLC_9_1', 'HJ2B_CCD_9_11', 'HJ2B_CCD_10_1',
                'HJ2A_CCD_10_1', 'ZY1E_VNIC_10_11', 'GF5B_AHSI_10_1', 'CB04_IRS_10_1', 'ZY1F_IRS_11_1',
                'CB04A_WFI_10_1', 'CB04A_MUX_11_1', 'CB04_WFI_11_1', 'HJ2A_CCD_11_1', 'GF3C_SAR_11_1',
                'Sentinel2B_MSI_9_1', 'WORLDVIEW3_PMS_10_1', 'TERRA_MODIS_9_1', 'TERRA_MODIS_10_1', 'TERRA_MODIS_11_1',
                'GF1D_PMI_9_1', 'Landsat8_OLI_10_1', 'GF2_PMI_10_1', 'HJ2A_HSI_9_1', 'Gf7_DLC_11_1']


# # 生成各卫星的条带数
# No_all = []
# for i in sat_list:
#     No_all.append(read_stripe_masage(i)[1])
# for k in range(len(sat_list)):
#     exec(f"no{k + 1} = No_all[k]")

"==================="
# 生成各卫星的条带数
# No_all = []
# for i in sat_list:
#     No_all.append(read_stripe_masage(i)[1])
# for k in range(len(sat_list)):
#     exec(f"no{k + 1} = No_all[k]")
no1=1569088
no2=886654
no3=120474
no4=732467
no5=393494
no6=975608
no7=2529720
no8=1000944
no9=2928774
no10=31110
no11=7830
no12=836042
no13=1144013
no14=260324
no15=2038049
no16=313632
no17=393204
no18=1
no19=1
no20=1
no21=0
no22=0
no23=0
no24=0
no25=0
No_all=[no1,no2,no3,no4,no5,no6,no7,no8,no9,no10,
        no11,no12,no13,no14,no15,no16,no17,no18,no19,no20,
        no21,no22,no23,no24,no25]
"==================="

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
solution=Chrom
print('first_solution:',solution)
covered_num = get_covered_grid_num(Phen,covered_all)#get_covered_grid_num(Phen, covered1, covered2, covered3, covered4, covered5, covered6, covered7, covered8, covered9, covered10, covered11)
print('first_covered_num:',covered_num)
timeend=time.time()
print('生成一个种群时间:',timeend-timestart)
"""=============================================================="""

NIND = 100
max_gen = 150
# D=25#维度，几个卫星
#Initialization
gen_no=0
while(gen_no<max_gen):
    function1_values = function1(Phen, aval_)
    function2_values = [function2(covered_num[i], cost_arr) for i in range(0, NIND)]
    function3_values = [function3(covered_num[i], untiltime) for i in range(0, NIND)]
    non_dominated_sorted_solution = fast_non_dominated_sort(function1_values[:], function2_values[:],
                                                            function3_values[:])
    print("The best front for Generation number ",gen_no, " is")
    for valuez in non_dominated_sorted_solution[0]:
        print(solution[valuez],end=" ")
        print("\n")
    print("\n")
    crowding_distance_values=[]
    for i in range(0, len(non_dominated_sorted_solution)):
        crowding_distance_values.append(crowding_distance(function1_values[:], function2_values[:], function3_values[:],
                                                          non_dominated_sorted_solution[i][:]))
    solution2 = solution[:]

    #Generating offsprings
    while(len(solution2)!=2*NIND):
        a1 = random.randint(0,NIND-1)
        b1 = random.randint(0,NIND-1)
        # cros_muta=crossover(solution,a1,b1)
        # solution2[-1,:]=crossover(solution,a1,b1)[0]
        # solution2[-1,:]=crossover(solution,a1,b1)[1]
        childa=crossover(solution,a1,b1)[0]
        childb=crossover(solution,a1,b1)[1]
        solution2=np.concatenate((solution2, [childa]), axis=0)
        solution2=np.concatenate((solution2, [childb]), axis=0)
    solution2_num = get_covered_grid_num(solution2, covered_all)
    function1_values2 = function1(solution2, aval_)
    function2_values2 = [function2(solution2_num[i], cost_arr) for i in range(0,2*NIND)]
    function3_values2 = [function3(solution2_num[i], untiltime) for i in range(0,2*NIND)]
    # function1_values2 = [function1(solution2[i])for i in range(0,2*NIND)]
    # function2_values2 = [function2(solution2[i])for i in range(0,2*NIND)]
    non_dominated_sorted_solution2 = fast_non_dominated_sort(function1_values2[:], function2_values2[:],
                                                            function3_values2[:])
    crowding_distance_values2=[]
    for i in range(0,len(non_dominated_sorted_solution2)):
        crowding_distance_values2.append(crowding_distance(function1_values2[:], function2_values2[:], function3_values2[:],
                                                          non_dominated_sorted_solution2[i][:]))
    new_solution= []
    for i in range(0,len(non_dominated_sorted_solution2)):
        non_dominated_sorted_solution2_1 = [index_of(non_dominated_sorted_solution2[i][j],non_dominated_sorted_solution2[i] ) for j in range(0,len(non_dominated_sorted_solution2[i]))]
        front22 = sort_by_values(non_dominated_sorted_solution2_1[:], crowding_distance_values2[i][:])
        front = [non_dominated_sorted_solution2[i][front22[j]] for j in range(0,len(non_dominated_sorted_solution2[i]))]
        front.reverse()
        for value in front:
            new_solution.append(value)
            if(len(new_solution)==NIND):
                break
        if (len(new_solution) == NIND):
            break
    solution = [solution2[i] for i in new_solution]
    gen_no = gen_no + 1

'''=====================生成结果==================='''
#把function123存在txt中
with open('D:\\stripe_txt\\st\\result\\constract\\function1.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in function1_values:
        file.write(str(s) + "\n")

with open('D:\\stripe_txt\\st\\result\\constract\\function2.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in function2_values:
        file.write(str(s) + "\n")

with open('D:\\stripe_txt\\st\\result\\constract\\function3.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in function3_values:
        file.write(str(s) + "\n")

#把front存在txt中
with open('D:\\stripe_txt\\st\\result\\constract\\non_dominated_sorted_solution.txt', "w") as file:
    # file.write('front:'+"\n")
    for s in non_dominated_sorted_solution:
        file.write(str(s) + "\n")
#把最终的phenx存在txt中
np.savetxt("D:\\stripe_txt\\st\\result\\constract\\phenx.txt", Phen,fmt='%d',delimiter=',')

'''====================生成结果==================='''

#Lets plot the final front now
function1 = [i * -1 for i in function1_values]
function2 = [j * -1 for j in function2_values]
plt.xlabel('Function 1', fontsize=15)
plt.ylabel('Function 2', fontsize=15)
plt.scatter(function1, function2)
plt.show()




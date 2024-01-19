#coding:utf-8

# import get_fishnet_test
import time
import shapefile
# import No2_basetimeANDdeclination_get_stripe#todo 连接No2


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
    with open('E:\\arcpy-\\monggulia_fire\\stripe\\'+str(sat_name)+'_sele_stripe4point.txt', "r", encoding='utf-8') as f:  #打开文本
        stripe4point = f.readlines()   #读取文本
        stripe4point_gf1 = [eval(s) for s in stripe4point]
        for i in range(len(stripe4point_gf1)):
            if i%1==0:
                stripe4point_gf1_sele.append(stripe4point_gf1[i])
    stripe=len(stripe4point_gf1_sele)
    return stripe4point_gf1_sele,stripe
    # print('num(stripe4point_'+sat_name+')',stripe)

'''需要的卫星'''
sat_list=['ZY1F_VNIC_9_1','GF1B_PMS_9_1','HJ2B_CCD_9_1','HJ2B_HSI_9_1','HJ2A_CCD_11_1',
          'Sentinel2B_MSI_9_1','ZY1E_VNIC_10_1','ZY1E_AHSI_10_1','CB04_IRS_10_1','ZY1F_VNIC_11_1',
          'CB04A_WFI_10_1','WORLDVIEW3_10_2','ZY1F_AHSI_9_2','GF3C_11_1','GF6_PMI_10_1',
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
'''# todo 可以连接No2
sat_name='gf5b'
with open('E:\\arcpy-\\wuhan\\stripe\\'+str(sat_name)+'_stripe4point.txt', "r", encoding='utf-8') as f:  #打开文本
    stripe4point = f.read()   #读取文本
    stripe4point = eval(stripe4point)#这里用eval将字符串转换为代码来执行
# print(stripe4point)
print(len(stripe4point))
'''

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
    if covered == []:
        covered = [[] for i in range(1)]
    return covered
#有很多很多个矩形，每个矩形覆盖一些格网
covered1=covered_num(stripe_ZY1F_VNIC_9_1,no1)
covered2=covered_num(stripe_GF1B_PMS_9_1,no2)
covered3=covered_num(stripe_HJ2B_CCD_9_1,no3)
covered4=covered_num(stripe_HJ2B_HSI_9_1,no4)
covered5=covered_num(stripe_HJ2A_CCD_11_1,no5)
covered6=covered_num(stripe_Sentinel2B_MSI_9_1,no6)
covered7=covered_num(stripe_ZY1E_VNIC_10_1,no7)
covered8=covered_num(stripe_ZY1E_AHSI_10_1,no8)
covered9=covered_num(stripe_CB04_IRS_10_1,no9)
covered10=covered_num(stripe_ZY1F_VNIC_11_1,no10)
covered11=covered_num(stripe_CB04A_WFI_10_1,no11)
covered12=covered_num(stripe_WORLDVIEW3_10_2,no12)
covered13=covered_num(stripe_ZY1F_AHSI_9_2,no13)
covered14=covered_num(stripe_GF3C_11_1,no14)
covered15=covered_num(stripe_GF6_PMI_10_1,no15)
covered16=covered_num(stripe_GF1D_PMI_9_1,no16)
covered17=covered_num(stripe_Landsat8_OLI_10_1,no17)
covered18=covered_num(stripe_GF2_PMI_10_1,no18)
covered19=covered_num(stripe_HJ2A_HSI_9_1,no19)
covered20=covered_num(stripe_Gf7_DLC_11_1,no20)
covered_all=[covered1,covered2,covered3,covered4,covered5,
             covered6,covered7,covered8,covered9,covered10,
             covered11,covered12,covered13,covered14,covered15,
             covered16,covered17,covered18,covered19,covered20]



#给各个stripe编号
def code_num(covered_all):
    covered_num = []
    for k in range(len(covered_all)):
        for i in range(len(covered_all[k])):
            covered_num.append(str(sat_list[k]) + '_stripe' + str(i))
    # for j in sat_list:
    #     for k in range(len(covered_all)):
    #         for i in range(len(covered_all[k])):
    #             covered_num.append(str(j)+'_stripe'+str(i))
    return covered_num
covered_num=code_num(covered_all)
'''covered_num = []
for i in range(len(covered)):
    covered_num.append('satone_stripe'+str(i))
# print 'covered_num:',covered_num
print('num(covered_num)',len(covered_num))'''

#将sat1的所有stripe覆盖的grid编号，字典
# stipe_grid_covered = dict(zip(covered_num,covered))
# print stipe_grid_covered

'''stripe_grid_covered = {}
for i in range(len(covered_num)):
    a = set()
    for j in range(len(covered[i])):
        a.add(covered[i][j])
    stripe_grid_covered[covered_num[i]] = a'''

'''for q in range(len(covered_all)):
        a = set()
        for z in range(len(covered_all[q])):
            for j in range(len(covered_all[q][z])):
                a.add(covered_all[q][z][j])
        stripe_grid_covered[covered_num[j]] = a'''
stripe_grid_covered = {}
k=0
while k < len(covered_num):
    for q in range(len(covered_all)):
        for z in range(len(covered_all[q])):
            a = set()
            for s in range(len(covered_all[q][z])):
                a.add(covered_all[q][z][s])
            stripe_grid_covered[covered_num[k]] = a
            k+=1
# print 'stripe_grid_covered:',stripe_grid_covered
#这一步为了去除不覆盖格网的条带，例如[[], [], [], [], [], [28], [18]]中的[]
#在字典中删除，确保[]的编号也一起删除
for k in list ( stripe_grid_covered.keys ( ) ):
     if not stripe_grid_covered [ k ] :
         del stripe_grid_covered [ k ]
print(stripe_grid_covered)

grid_x = []#格网的编号
for i in range(len(grid_all)):
    grid_x.append(i)
grid_x = set(grid_x)

'''
Sat_set = stripe_grid_covered# TODO Sat_set应该改成stripe_set条带集合
final_satellite = set()
i = 0
while grid_x:
    i += 1
    best_sate = None
    sat_covered = set()
    for sate, grid in Sat_set.items():#sate是Sat_set集合中的卫星sat，grid是Sate_set集合中的格网
        covered = grid_x & grid#两者交集，表示覆盖的格网有哪些
        if len(covered) > len(sat_covered):
            best_sate = sate
            sat_covered = covered
    grid_x -= sat_covered
    final_satellite.add(best_sate)
    if i == 5000:
        break

print("final_satellite:\n", final_satellite)'''

def greedy_cover(stripe_grid_covered,grid_x):#stripe_grid_covered为上面生成的条带覆盖格网的集合，grid_x为所有格网的编号
    start_time = time.time()
    Sat_set = stripe_grid_covered# TODO Sat_set应该改成stripe_set条带集合
    final_satellite = set()
    i = 0
    while grid_x:
        i += 1
        best_sate = None
        sat_covered = set()
        for sate, grid in Sat_set.items():#sate是Sat_set集合中的卫星sat，grid是Sate_set集合中的格网
            covered = grid_x & grid#两者交集，表示覆盖的格网有哪些
            if len(covered) > len(sat_covered):
                best_sate = sate
                sat_covered = covered
        grid_x -= sat_covered
        final_satellite.add(best_sate)
        if i == 500000:
            break
    end_time = time.time()
    print("time cost:", end_time - start_time, "s")
    return  final_satellite


if __name__ == '__main__':
    print(greedy_cover(stripe_grid_covered,grid_x))




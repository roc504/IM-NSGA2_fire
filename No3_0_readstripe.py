"""
@File    : mult_test.py
@Author  : roc
@Time    : 2023/4/26 16:09
"""

import time
import shapefile
import numpy as np

sf = shapefile.Reader('E:/arcpy-/monggulia_fire/maybe_fire_area1_fishnet_sele.shp')
shapes = sf.shapes()
lens = len(shapes)
grid_all = []#所有格网集合
for q in range(lens):
    grid_all.append(shapes[q].points)
# print("num(grid_all):", len(grid_all))

def read_stripe_masage(sat_name):
    # sat_name='CB04_9_1_sele'#gf1_test
    # stripe4point_sat=[]
    with open('D:\\stripe_txt\\st\\'+str(sat_name)+'_sele_stripe4point.txt', "r", encoding='utf-8') as f:  #打开文本
        stripe4point = f.readlines()  # 读取文本
        stripe4point_ = [eval(s) for s in stripe4point]
        # for i in range(len(stripe4point_)):
        #     if i%1==0:
        #         stripe4point_sat.append(stripe4point_[i])
    stripe=len(stripe4point_)
    print('read'+str(sat_name)+'_sele_stripe4point.txt')
    return stripe4point_,stripe
    # print('num(stripe4point_'+sat_name+')',stripe)


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
        del a
    if covered == []:
        covered = [[] for i in range(1)]
    return covered
    # print('covered',covered[:20])
    # print('num-covered',len(covered))
'''===换种判断矩形是否在矩形的方法=='''
def is_rectangle_inside(stripename, stripex, gridx):
    '''rect1是格网矩形，rect2是条带矩形，判断rect1是否在rect2里'''
    rect1=stripename[stripex]
    rect2=grid_all[gridx]
    # 计算 rect1 的四个顶点坐标
    x1_rect1, y1_rect1 = zip(*rect1)
    x2_rect1, y2_rect1 = zip(*rect1)

    # 计算 rect2 的四个顶点坐标
    x_rect2 = [point[0] for point in rect2]
    y_rect2 = [point[1] for point in rect2]

    # 判断 rect1 的四个顶点是否都在 rect2 内部
    rect1_inside_rect2 = all(
        min(x_rect2) <= x <= max(x_rect2) and \
        min(y_rect2) <= y <= max(y_rect2)
        for x, y in zip(x1_rect1, y1_rect1))
    return rect1_inside_rect2
def covered_num_gai(stripename,num):
    covered=[]
    for _ in range(0,num):#(0,28)
        a = []
        for __ in range(len(grid_all)):
            if is_rectangle_inside(stripename,_,__):
                a.append(__)
        # print a
        covered.append(a)
        del a
    if covered == []:
        covered = [[] for i in range(1)]
    return covered

if __name__=='__main__':
    # '''需要的卫星'''
    sat_list = ['ZY1F_VNIC_9_11', 'GF1C_PMS_9_1', 'GF7_DLC_9_1', 'HJ2B_CCD_9_11', 'HJ2B_CCD_10_1',
                'HJ2A_CCD_10_1', 'ZY1E_VNIC_10_11', 'GF5B_AHSI_10_1', 'CB04_IRS_10_1', 'ZY1F_IRS_11_1',
                'CB04A_WFI_10_1', 'CB04A_MUX_11_1', 'CB04_WFI_11_1', 'HJ2A_CCD_11_1', 'GF3C_SAR_11_1',
                'Sentinel2B_MSI_9_1', 'WORLDVIEW3_PMS_10_1', 'TERRA_MODIS_9_1', 'TERRA_MODIS_10_1', 'TERRA_MODIS_11_1',
                'GF1D_PMI_9_1', 'Landsat8_OLI_10_1', 'GF2_PMI_10_1', 'HJ2A_HSI_9_1', 'Gf7_DLC_11_1']


    # # 生成各卫星的条带坐标条带
    # Stripepoints_all = []
    # for i in sat_list:
    #     Stripepoints_all.append(read_stripe_masage(i)[0])
    #
    # for k in range(len(sat_list)):
    #     m = sat_list[k]
    #     # print(m)
    #     exec(f'stripe_{m} = Stripepoints_all[k]')  # 这样运行出来，直接stripe_ZY1F_VNIC_9_1就直接是条带的坐标列表
    #
    # # 生成各卫星的条带数
    # No_all = []
    # for i in sat_list:
    #     No_all.append(read_stripe_masage(i)[1])
    #
    # for k in range(len(sat_list)):
    #     exec(f"no{k + 1} = No_all[k]")

    #这里covered_num的第一个参数直接写stripe_卫星名称（前面列出来的卫星）
    # covered1 = covered_num(stripe_ZY1F_VNIC_9_11, no1)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered1.npy', covered1)
    # print('num-covered1', len(covered1))
    # covered2 = covered_num(stripe_GF1C_PMS_9_1, no2)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered2.npy', covered2)
    # print('num-covered2', len(covered2))
    # covered3 = covered_num(stripe_GF7_DLC_9_1, no3)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered3.npy', covered3)
    # print('num-covered3', len(covered3))
    # covered4 = covered_num(stripe_HJ2B_CCD_9_11, no4)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered4.npy', covered4)
    # print('num-covered4', len(covered4))
    # covered5 = covered_num(stripe_HJ2B_CCD_10_1, no5)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered5.npy', covered5)
    # print('num-covered5', len(covered5))
    # covered6 = covered_num(stripe_HJ2A_CCD_10_1, no6)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered6.npy', covered6)
    # print('num-covered6', len(covered6))
    # covered7 = covered_num(stripe_ZY1E_VNIC_10_11, no7)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered7.npy', covered7)
    # print('num-covered7', len(covered7))
    # covered8 = covered_num(stripe_GF5B_AHSI_10_1, no8)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered8.npy', covered8)
    # print('num-covered8', len(covered8))
    # covered9 = covered_num(stripe_CB04_IRS_10_1, no9)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered9.npy', covered9)
    # print('num-covered9', len(covered9))
    # covered10 = covered_num(stripe_ZY1F_IRS_11_1, no10)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered10.npy', covered10)
    # print('num-covered10', len(covered10))
    # covered11 = covered_num(stripe_CB04A_WFI_10_1, no11)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered11.npy', covered11)
    # print('num-covered11', len(covered11))
    # covered12 = covered_num(stripe_CB04A_MUX_11_1, no12)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered12.npy', covered12)
    # print('num-covered12', len(covered12))
    # covered13 = covered_num(stripe_CB04_WFI_11_1, no13)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered13.npy', covered13)
    # print('num-covered13', len(covered13))
    # covered14 = covered_num(stripe_HJ2A_CCD_11_1, no14)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered14.npy', covered14)
    # print('num-covered14', len(covered14))
    # covered15 = covered_num(stripe_GF3C_SAR_11_1, no15)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered15.npy', covered15)
    # print('num-covered15', len(covered15))
    # covered16 = covered_num(stripe_Sentinel2B_MSI_9_1, no16)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered16.npy', covered16)
    # print('num-covered16', len(covered16))
    # covered17 = covered_num(stripe_WORLDVIEW3_PMS_10_1, no17)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered17.npy', covered17)
    # print('num-covered17', len(covered17))
    # covered18 = covered_num(stripe_TERRA_MODIS_9_1, no18)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered18.npy', covered18)
    # print('num-covered18', len(covered18))
    # covered19 = covered_num(stripe_TERRA_MODIS_10_1, no19)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered19.npy', covered19)
    # print('num-covered19', len(covered19))
    # covered20 = covered_num(stripe_TERRA_MODIS_11_1, no20)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered20.npy', covered20)
    # print('num-covered20', len(covered20))
    # covered21 = covered_num(stripe_GF1D_PMI_9_1, no21)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered21.npy', covered21)
    # print('num-covered21', len(covered21))
    # covered22 = covered_num(stripe_Landsat8_OLI_10_1, no22)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered22.npy', covered22)
    # print('num-covered22', len(covered22))
    # covered23 = covered_num(stripe_GF2_PMI_10_1, no23)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered23.npy', covered23)
    # print('num-covered23', len(covered23))
    # covered24 = covered_num(stripe_HJ2A_HSI_9_1, no24)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered24.npy', covered24)
    # print('num-covered24', len(covered24))
    # covered25 = covered_num(stripe_Gf7_DLC_11_1, no25)
    # np.save('D:\\stripe_txt\\st_covered_all\\covered25.npy', covered25)
    # print('num-covered25', len(covered25))
    # covered_all = [covered1, covered2, covered3, covered4, covered5,
    #                covered6, covered7, covered8, covered9, covered10,
    #                covered11, covered12, covered13, covered14, covered15,
    #                covered16, covered17, covered18, covered19, covered20,
    #                covered21, covered22, covered23, covered24, covered25]



    time_start_1 = time.time()
    covered_all = []
    for each in range(1, 26):
        real_path = (r'D:\\stripe_txt\\st_covered_all\\covered' + str(each) + '.npy')
        real_data = np.load(real_path, allow_pickle=True)  # 类型是numpy array
        covered_all.append(real_data)
        del real_data
        print('已添加covered'+str(each))
    np.save(r'D:\\stripe_txt\\st_covered_all\\covered_all1.npy', covered_all)
    time_end_1 = time.time()
    print("运行时间1：" + str(time_end_1 - time_start_1) + "秒")
    print('finish')


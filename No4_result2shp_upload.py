"""
@File    : No4_result2shp.py
@Author  : roc
@Time    : 2023/7/20 22:33
"""
from shapely import geometry
import geopandas
import numpy as np

sat_list=['ZY1F_VNIC_9_11','GF1C_PMS_9_1','GF7_DLC_9_1','HJ2B_CCD_9_11','HJ2B_CCD_10_1',
          'HJ2A_CCD_10_1','ZY1E_VNIC_10_11','GF5B_AHSI_10_1','CB04_IRS_10_1','ZY1F_IRS_11_1',
          'CB04A_WFI_10_1','CB04A_MUX_11_1','CB04_WFI_11_1','HJ2A_CCD_11_1','GF3C_SAR_11_1',
          'Sentinel2B_MSI_9_1','WORLDVIEW3_PMS_10_1','TERRA_MODIS_9_1','TERRA_MODIS_10_1','TERRA_MODIS_11_1',
          'GF1D_PMI_9_1','Landsat8_OLI_10_1','GF2_PMI_10_1','HJ2A_HSI_9_1','Gf7_DLC_11_1']
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

Stripepoints_all=[]
for i in sat_list:
    Stripepoints_all.append(read_stripe_masage(i)[0])

for k in range(len(sat_list)):
    m=sat_list[k]
    # print(m)
    exec(f'stripe_{m} = Stripepoints_all[k]')  # 这样运行出来，直接stripe_ZY1F_VNIC_9_1就直接是条带的坐标列表



#读front
def txt2list(file_route):
    non_dominated_sorted_solution=[]
    f=open(file_route, "r", encoding='utf-8')
    stripe4point = f.readline()
    while stripe4point:
        stripe4point_tu = eval(stripe4point) # 转为元组形式
        non_dominated_sorted_solution.append(stripe4point_tu)
        stripe4point = f.readline()
    return non_dominated_sorted_solution


def result2shp(non_dominated_sorted_solution,Phen,Stripepoints_all):
    alist=non_dominated_sorted_solution[0]
    for i in range(len(alist)):
        n=alist[i]
        individuals=Phen[n]
        individuals_list=individuals.tolist()
        listp=[]
        listi=[]
        for j in range(len(individuals_list)):#几个为0的卫星条带直接不算
            s=individuals_list[j]
            if s == 0:
                # temp=[[]]
                continue
            else:
                temp = Stripepoints_all[j][s]
            listp.append(geometry.Polygon(temp))
            listi.append(str(sat_list[j])+ '_' + str(s))

        cq = geopandas.GeoSeries(listp,
                             index=listi,  # 构建一个索引字段
                             crs='EPSG:4326',  # 坐标系是：WGS 1984
                             )
        cq.to_file('D:\\stripe_txt\\st\\GA_result_time\\individual_'+str(n)+'result_stripe.shp', driver='ESRI Shapefile',
               encoding='utf-8')
        print('finish')
if __name__=='__main__':

    # non_dominated_sorted_solution=txt2list('D:\\stripe_txt\\st\\result\\non_dominated_sorted_solution.txt')
    # pheny= np.loadtxt("D:\\stripe_txt\\st\\result\\phenx.txt",dtype = int,delimiter=',')
    # pheny = np.loadtxt("D:\\stripe_txt\\st\\result\\constract\\phenx.txt", dtype=int, delimiter=',')

    # # phenx=[phenx]#对于GA，只有一个给结果，需要增加一个维度
    #
    # result2shp(non_dominated_sorted_solution,phenx,Stripepoints_all)

    # non_dominated_sorted_solution = txt2list('D:\\stripe_txt\\st\\GA_result\\non_dominated_sorted_solution.txt')
    # phenx = np.loadtxt("D:\\stripe_txt\\st\\GA_result\\phenx.txt", dtype=int, delimiter=',')

    non_dominated_sorted_solution = txt2list('D:\\stripe_txt\\st\\GA_result_time\\non_dominated_sorted_solution.txt')
    phenx = np.loadtxt("D:\\stripe_txt\\st\\GA_result_time\\phenx.txt", dtype=int, delimiter=',')

    # phenx=[phenx]#对于GA，只有一个给结果，需要增加一个维度

    result2shp(non_dominated_sorted_solution, phenx, Stripepoints_all)
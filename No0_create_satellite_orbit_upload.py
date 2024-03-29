"""
@File    : No0_create_satellite_orbit.py
@Author  : roc
@Time    : 2022/9/29 17:34
"""

import datetime
import os
import time

import pandas as pd
import win32com.client

startTime = time.time()

# 创建高分2卫星轨道
def createSatellite(path_tle, starttime, stoptime, SATname, NORAD_Num):
    # Create data storage path
    target_excel_dir = r'E:/STK/monggulia_fire_satellite'
    if not os.path.exists(target_excel_dir):
        os.makedirs(target_excel_dir)

    # Get reference to running STK instance
    app = win32com.client.Dispatch('STK11.Application')
    app.Visible = True
    # Get our IAgStkObjectRoot interface
    root = app.Personality2
    # creat a new scenario
    # IAgStkObjectRoot root: STK Object Model Root
    root.NewScenario('satellite_test')  # The scene name cannot contain spaces or other illegal characters.
    scenario = root.CurrentScenario
    root.UnitPreferences.SetCurrentUnit('DateFormat', 'UTCG')
    # 设置场景时间
    root.CurrentScenario.StartTime = starttime  # '21 Feb 2023 16:00:00.00'
    root.CurrentScenario.StopTime = stoptime  # '22 Feb 2023 04:00:00.00'

    satellite = root.CurrentScenario.Children.New(18, SATname)
    satellite.SetPropagatorType(4)
    propagator = satellite.Propagator
    propagator.UseScenarioAnalysisTime
    propagator.CommonTasks.AddSegsFromFile(NORAD_Num, path_tle)  # 40118
    propagator.AutoUpdateEnabled = True
    propagator.Propagate()
    satOrbitDP = satellite.DataProviders.GetDataPrvTimeVarFromPath('Classical Elements/J2000')
    results_orbit = satOrbitDP.Exec(starttime, stoptime, 30)
    satLLADP = satellite.DataProviders.GetDataPrvTimeVarFromPath('Cartesian Velocity/Fixed')
    results_LLA = satLLADP.Exec(starttime, stoptime, 30)
    # Cartesian Velocity/Fixed里的参数
    sat_time = results_orbit.DataSets[0].GetValues()
    # sat_time = results_LLA.DataSets[0].GetValues()
    sat_vx = results_LLA.DataSets[1].GetValues()
    sat_vy = results_LLA.DataSets[2].GetValues()
    sat_vz = results_LLA.DataSets[3].GetValues()
    sat_speed = results_LLA.DataSets[4].GetValues()
    sat_vr = results_LLA.DataSets[5].GetValues()
    sat_vi = results_LLA.DataSets[6].GetValues()
    satLLADP2 = satellite.DataProviders.GetDataPrvTimeVarFromPath('LLA State/Fixed')
    results_LLA2 = satLLADP2.Exec(starttime, stoptime, 30)
    sat_lat = results_LLA2.DataSets[1].GetValues()
    sat_lon = results_LLA2.DataSets[2].GetValues()
    Data = pd.DataFrame(
        columns=('Time (UTC)',
                 'latitude (deg)', 'longitude (deg)', 'speed (km/sec)'))
    for j in range(0, len(sat_time)):
        t = sat_time[j].split('.', 1)[0]
        # Convert output time to timestamp to facilitate filtering of core calculation data
        # Time format style output by STK:1 Jan 2020 04:00:00
        t_stamp = time.strptime(t, '%d %b %Y %H:%M:%S')
        t_stamp = time.mktime(t_stamp) / 3600
        # 转换输出时间为格式时间便于显示以及读取
        t = datetime.datetime.strptime(t, '%d %b %Y %H:%M:%S')
        t = datetime.datetime.strftime(t, '%Y-%m-%d %H:%M:%S')

        lat = sat_lat[j]
        lon = sat_lon[j]
        speed = sat_speed[j]

        Data = Data.append(pd.DataFrame(
            {'Time (UTC)': [t],
             'latitude (deg)': [lat], 'longitude (deg)': [lon], 'speed (km/sec)': [speed]}),
            ignore_index=True)
    Data.to_excel(target_excel_dir + '/' + str(SATname) + '_undersatellite_line.xlsx',
                      'sheet1', float_format='%.6f', index=False)


t1 = '09 Apr 2023 00:00:00.00'
t2 = '12 Apr 2023 00:00:00.00'

# path_tle = r'E:/STK/monggulia_fire_satellite/ZY302.txt'
# SATname='ZY302'
# NORAD_Num='41556'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/CB04.txt'
# SATname='CB04'
# NORAD_Num='40336'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/GF1D.txt'
# SATname='GF1D'
# NORAD_Num='43262'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/GF1C.txt'
# SATname='GF1C'
# NORAD_Num='43260'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/GF3.txt'
# SATname='GF3'
# NORAD_Num='41727'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/GF3C.txt'
# SATname='GF3C'
# NORAD_Num='52200'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/GF5B.txt'
# SATname='GF5B'
# NORAD_Num='49122'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/ZY1F.txt'
# SATname='ZY1F'
# NORAD_Num='44528'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/CB04A.txt'
# SATname='CB04A'
# NORAD_Num='44883'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/HJ2A.txt'
# SATname='HJ2A'
# NORAD_Num='46478'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
# path_tle = r'E:/STK/monggulia_fire_satellite/GF6.txt'
# SATname='GF6'
# NORAD_Num='43484'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/GF7.txt'
# SATname='GF7'
# NORAD_Num='44703'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/HJ2B.txt'
# SATname='HJ2B'
# NORAD_Num='46479'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/SENTINEL1A.txt'
# SATname='SENTINEL1A'
# NORAD_Num='39634'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/SENTINEL1B.txt'
# SATname='SENTINEL1B'
# NORAD_Num='41456'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/SENTINEL2A.txt'
# SATname='SENTINEL2A'
# NORAD_Num='40697'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/SENTINEL2B.txt'
# SATname='SENTINEL2B'
# NORAD_Num='42063'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/WORLDVIEW3.txt'
# SATname='WORLDVIEW3'
# NORAD_Num='40115'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/ZY1F.txt'
# SATname='ZY1F'
# NORAD_Num='44528'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
# totalTime = time.time() - startTime
#
# path_tle = r'E:/STK/monggulia_fire_satellite/ZY302.txt'
# SATname='ZY302'
# NORAD_Num='41556'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
# totalTime = time.time() - startTime
#
# path_tle = r'E:/STK/monggulia_fire_satellite/ZY302.txt'
# SATname='ZY302'
# NORAD_Num='41556'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
# totalTime = time.time() - startTime

# path_tle = r'E:/STK/monggulia_fire_satellite/GF1.txt'
# SATname='GF1'
# NORAD_Num='39150'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/GF1B.txt'
# SATname='GF1B'
# NORAD_Num='43259'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
#
# path_tle = r'E:/STK/monggulia_fire_satellite/GF3B.txt'
# SATname='GF3B'
# NORAD_Num='49495'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)

# path_tle = r'E:/STK/monggulia_fire_satellite/ZY1F.txt'
# SATname='ZY1F'
# NORAD_Num='50465'
# createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
# totalTime = time.time() - startTime

path_tle = r'E:/STK/monggulia_fire_satellite/GF4.txt'
SATname='GF4'
NORAD_Num='41194'
createSatellite(path_tle,t1,t2, SATname, NORAD_Num)
totalTime = time.time() - startTime

print("--- computer speed+point: {a:4.3f} sec ---".format(a=totalTime))

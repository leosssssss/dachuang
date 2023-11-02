import xarray as xr
import pandas as pd
import numpy as np


def PotentialVorticity(vo, t, P=500):
    """
    :param vo: 输入等压面的位涡
    :param t: 输入等压面的温度
    :param P: 等压面层
    :return: 返回位涡
    """
    R = 8.3144626   #气体常数R
    _rho = R*t/P #500hPa密度的倒数
    theta = t*(1000/P)**0.286    #500hPa上的位温
    C = np.identity(np.shape(t)[0]) - 1/np.shape(t)[0]*np.ones(np.shape(t))    #中心阵
    D_theta = np.dot(np.dot(theta, C), theta.T) #位温的散度
    potentialVorticity = np.dot(np.dot(_rho, vo), D_theta)
    return potentialVorticity


adressF = 'D:/datas/dachuang/台风预测数据/typhoon(CHINA)/typhoon forecast data.csv'
adressERAH = "E:/data/"
adressERAT = ".grib"
Frange = 4.5
forcastData = pd.read_csv(adressF, index_col=0, low_memory=False)
for i in range(forcastData.shape[0]):
    month = forcastData.loc[i, 'time+0'][0:4]+forcastData.loc[i, 'time+0'][5:7]
    time = forcastData.loc[i, 'time+0']
    lon = forcastData.loc[i, 'lon+0']
    lat = forcastData.loc[i, 'lat+0']
    ERA = xr.open_dataset(adressERAH+month+adressERAT, engine='cfgrib', mask_and_scale=False)
    d500 = ERA.d.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #500hPa的散度
    u500 = ERA.u.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #500hPa的水平风速
    """
    计算位势涡度（使用ertel位涡计算）"""
    vo500 = ERA.vo.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values   #500hPa的绝对涡度
    t500 = ERA.vo.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values    #500hPa的温度
    pv = PotentialVorticity(vo500, t500)    #500hPa的位涡
    print(pv)
    xr.Dataset.close(ERA)
    break

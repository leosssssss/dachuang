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


def OneWave(data):
    """
    :param data: 传入的数据
    :return: 返回取得一波非对称信息后的数据
    """
    fr = np.fft.fft(data)
    fr1 = fr[1]
    A = np.sqrt(fr1.imag ** 2 + fr1.real ** 2)
    maxI = fr1[A == max(A)]
    maxA = max(A)
    angle = np.angle(maxI)
    returnList = [maxA, angle]
    return returnList

adressF = 'D:/datas/dachuang/台风预测数据/typhoon(CHINA)/typhoon forecast data.csv'
adressLSM = "D:/datas/dachuang/masks/IMERG_land_sea_mask.nc"
adressERAH = "E:/data/"
adressERAT = ".grib"
adressGeopotential = "D:/datas/dachuang/masks/Geopotential.grib"
Frange = 4.5
forcastData = pd.read_csv(adressF, index_col=0, low_memory=False)
LSMask = xr.open_dataset(adressLSM)
geopotential = xr.open_dataset(adressGeopotential, engine='cfgrib')
for i in range(forcastData.shape[0]):
    month = forcastData.loc[i, 'time+0'][0:4]+forcastData.loc[i, 'time+0'][5:7]
    time = forcastData.loc[i, 'time+0']
    lon = forcastData.loc[i, 'lon+0']
    lat = forcastData.loc[i, 'lat+0']
    ERA = xr.open_dataset(adressERAH+month+adressERAT, engine='cfgrib', mask_and_scale=False)
    d500 = ERA.d.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #500hPa的散度
    u500 = ERA.u.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #500hPa的水平风速
    vo500 = ERA.vo.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values   #500hPa的绝对涡度
    t500 = ERA.vo.loc[time, lat+Frange:lat-Frange, lon-Frange:lon+Frange].values    #500hPa的温度
    pv = PotentialVorticity(vo500, t500)    #500hPa的位涡
    LSM = LSMask.landseamask.loc[lat-Frange:lat+Frange, lon-Frange:lon+Frange].values   #海陆遮罩
    G = geopotential.z.loc[lat+Frange:lat-Frange, lon-Frange:lon+Frange].values #地势
    LSMOW = OneWave(LSM)    #海陆遮罩的一波处理
    GOW = OneWave(G) #地势的一波处理
    xr.Dataset.close(ERA)
    break

import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

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
def Operate(adressForcast, adressLSMData, adressERAHData, adressERATData, adressGeopotentialData):
	Frange = 4.5
	forecastData = pd.read_csv(adressForcast, index_col=0, low_memory=False)
	LSMask = xr.open_dataset(adressLSMData)
	geopotential = xr.open_dataset(adressGeopotentialData, engine='cfgrib')
	for i in range(forecastData.shape[0]):
		month = forecastData.loc[i, 'time+0'][0:4]+forecastData.loc[i, 'time+0'][5:7]
		time = forecastData.loc[i, 'time+0']
		lon = forecastData.loc[i, 'lon+0']
		lat = forecastData.loc[i, 'lat+0']
		ERA = xr.open_dataset(adressERAHData + month + adressERATData, engine='cfgrib', mask_and_scale=False)
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


def Autocorrelation(adressForcast, delay=10):
	"""已经完成了求时间序列，后续还剩求自相关系数"""
	forcastData = pd.read_csv(adressForcast, index_col=0, low_memory=False)
	l = 300
	ac = np.zeros((l, 2))   #返回的序列
	temp = np.zeros((l, 2)) #暂时存储
	num = 200901
	t = 0
	cnt = 0 #记录次数
	for i in range(forcastData.shape[0]):
		if num != forcastData.loc[i, 'nums']:
			num = forcastData.loc[i+1, 'nums']
			ac += temp
			temp = np.zeros((l, 2))
			t = 0
			cnt += 1
		else:
			temp[t, 0] = forcastData.loc[i, 'speed+0']
			temp[t, 1] = forcastData.loc[i, 'pressure+0']
			t += 1
	ac /= cnt
	ac = ac[0:30, ...]
	coefSpeed = autocorrelation(ac[...,0], delay)
	coefPressure = autocorrelation(ac[...,1], delay)
	return [coefSpeed, coefPressure]


def autocorrelation(x,lags, n=None):#计算lags阶以内的自相关系数，返回lags个值，将序列均值、标准差视为不变
	n = len(x)
	x =np.array(x)
	variance = x.var()
	x = x-x.mean()
	result = np.correlate(x, x, mode = 'full')[-n+1:-n+lags+1]/\
		(variance*(np.arange(n-1,n-1-lags,-1)))
	return result


def ShowFig():
	plt.plot(Autocorrelation(adressF, 15)[1], c='b', label='original value')
	plt.plot(abs(Autocorrelation(adressF, 15)[1]), c='r', label='absolute value')
	plt.axhline(0, color='k', linestyle='--')
	plt.xlabel("tome interval (per 6 hours)")
	plt.ylabel("autocorrection coefficient")
	plt.title("autocorrection of pressure")
	plt.legend()
	plt.show()



